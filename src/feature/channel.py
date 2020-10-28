"""
channel feature implementation as specified by the specification

Feature implementation was written by Gabriel Ting, Tam Do, Prathamesh Jagtap.

2020 T3 COMP1531 Major Project
"""

from src.feature.validate import (
    validate_token,
    validate_channel_id,
    validate_token_as_channel_member,
    validate_u_id,
    validate_u_id_as_channel_owner,
    validate_u_id_as_channel_member,
)
from src.feature.action import (
    convert_token_to_u_id,
    get_lowest_u_id_in_channel,
)
from src.feature.error import InputError, AccessError
from src.feature.data import data
from src.feature.globals import OWNER, MEMBER

def channel_invite(token, channel_id, u_id):
    """Invites a user (with user id u_id) to join a channel with ID channel_id.
    Once invited the user is added to the channel immediately

    Args:
        token (string)
        channel_id (int)
        u_id (int):

    Returns:
        (dict): {}
    """
    # Error Checks
    if not validate_u_id(u_id):
        raise InputError("Invited user not found")
    if not validate_channel_id(channel_id):
        raise InputError("Channel ID is not a valid channel")
    if not validate_token(token):
        raise AccessError("Token is invalid, please register/login")

    # raises AccessError if user is not authorized to invite
    member_u_id = convert_token_to_u_id(token)
    if not validate_u_id_as_channel_member(member_u_id, channel_id):
        raise AccessError("User not authorized to invite, please join channel")
    # raises InputError when user is invited multiple times or invites him/herself
    if validate_u_id_as_channel_member(u_id, channel_id):
        raise InputError("User is already part of the channel")
    
    user = data.get_user_object(u_id)
    data.add_member_to_channel(u_id, channel_id)
    # if user is flockr owner: make him the group owner too
    if user.get_permission_id() == OWNER:
        data.add_owner_to_channel(u_id, channel_id)
    
    data.add_channel_to_user_list(u_id, channel_id)
    
    return {}

def channel_details(token, channel_id):
    """Given a Channel with ID channel_id that the authorised user is part of,
    provide basic details about the channel

    Args:
        token (string)
        channel_id (int)

    Returns:
        (dict): { name, owner_members, all_members }
    """
    # Error Checks
    if not validate_token(token):
        raise AccessError("Token is invalid, please register/login")
    if not validate_channel_id(channel_id):
        raise InputError("Channel ID is not a valid channel")

    # raise AccessError if not authorized to see details
    u_id = convert_token_to_u_id(token)
    if not validate_u_id_as_channel_member(u_id, channel_id):
        raise AccessError("User is not authorized to see channel details")

    # check whether user is authorized to see channel details
    channel_details = data.get_channel_object(channel_id)
    return {
        'name'         : channel_details.get_name(),
        'owner_members': channel_details.get_owner_members(),
        'all_members'  : channel_details.get_all_members(),
    }

def channel_messages(token, channel_id, start):
    """Given a Channel with ID channel_id that the authorised user is part of,
    return up to 50 messages between index "start" and "start + 50". Message
    with index 0 is the most recent message in the channel. This function returns
    a new index "end" which is the value of "start + 50", or, if this function
    has returned the least recent messages in the channel, returns -1 in "end"
    to indicate there are no more messages to load after this return.

    Args:
        token (string)
        channel_id (int)
        start (int)

    Returns:
        (dict): { messages, start, end }
    """
    # Error Checks
    if not validate_channel_id(channel_id):
        raise InputError("Channel ID is not a valid channel")
    channel_details = data.get_channel_details(channel_id)
    if start >= len(channel_details['messages']) and start != 0:
        raise InputError("start is greater than the total number of messages in the channel")
    if start < 0:
        raise InputError("start can only be positive")
    if not validate_token(token):
        raise AccessError("Token is not valid")
    if not validate_token_as_channel_member(token, channel_id):
        raise AccessError("Authorised user is not a member of channel with channel_id")
    # Case where there are no messages in the channel
    if len(channel_details['messages']) == 0:
        return {
            'messages': [],
            'start': -1,
            'end': -1,
        }

    # Case where there are messages in the channel
    end = start + 50
    if end >= len(channel_details['messages']):
        end = -1
    message_list = channel_details['messages']
    if end == -1:
        return {
            'messages': message_list[start:],
            'start': start,
            'end': end
        }
    return {
        'messages': message_list[start:end],
        'start': start,
        'end': end
    }

def channel_leave(token, channel_id):
    """Given a channel ID, the user removed as a member of this channel

    Args:
        token (string)
        channel_id (int)

    Returns:
        (dict): {}
    """
    # Error Checks
    if not validate_channel_id(channel_id):
        raise InputError("Channel ID is not a valid channel")
    if not validate_token(token):
        raise AccessError("Token is not valid")
    if not validate_token_as_channel_member(token, channel_id):
        raise AccessError("Authorised user is not a member of channel with channel_id")

    u_id = convert_token_to_u_id(token)
    channel_details = data.get_channel_details(channel_id)
    data.remove_member_from_channel(u_id, channel_id)
    data.remove_owner_from_channel(u_id, channel_id)
    data.remove_channel_from_user_list(u_id, channel_id)

    # Case where all owners have left, assign a user with the lowest u_id as
    # new owner
    if len(channel_details['owner_members']) == 0 and len(channel_details['all_members']) != 0:
        lowest_u_id_user = get_lowest_u_id_in_channel(channel_id)
        data.add_owner_to_channel(lowest_u_id_user, channel_id)
    
    # Case where all members have left, delete channel from database
    if len(channel_details['all_members']) == 0:
        data.delete_channel(channel_id)

    return {}

def channel_join(token, channel_id):
    """Given a channel_id of a channel that the authorised user can join, adds
    them to that channel

    Args:
        token (string)
        channel_id (int)

    Returns:
        (dict): {}
    """
    # Error Checks
    if not validate_channel_id(channel_id):
        raise InputError("Channel ID is not a valid channel")
    if not validate_token(token):
        raise AccessError("Token is not valid")
    # Check whether user is a channel member already
    if validate_token_as_channel_member(token, channel_id):
        return {}

    u_id = convert_token_to_u_id(token)
    user = data.get_user_details(u_id)
    channel_details = data.get_channel_details(channel_id)
    # User cannot join a channel if they are a flockr member and the channel is private
    if user['permission_id'] == MEMBER and not channel_details['is_public']:
        raise AccessError("Authorised user is not a member of channel with channel_id")

    data.add_member_to_channel(user['u_id'], channel_id)
    data.add_channel_to_user_list(user['u_id'], channel_id)

    # If the user is the flockr owner, make their permissions as a channel owner.
    if user['permission_id'] == OWNER:
        data.add_owner_to_channel(user['u_id'], channel_id)
    return {}

def channel_addowner(token, channel_id, u_id):
    """Make user with user id u_id an owner of this channel

    Args:
        token (string)
        channel_id (int)
        u_id (int)

    Returns:
        (dict): {}
    """
    # Error Checks
    if not validate_channel_id(channel_id):
        raise InputError("Channel ID is not a valid channel")
    if not validate_token(token):
        raise AccessError("Token is not valid")
    if not validate_token_as_channel_member(token, channel_id):
        raise AccessError("Authorised user is not a member of channel with channel_id")
    if not validate_u_id(u_id):
        raise InputError("u_id is not a valid u_id")
    if validate_u_id_as_channel_owner(u_id, channel_id):
        raise InputError("u_id is already owner of channel")

    # Add user as member if not already.
    if not validate_u_id_as_channel_member(u_id, channel_id):
        data.add_member_to_channel(u_id, channel_id)
        data.add_channel_to_user_list(u_id, channel_id)
    data.add_owner_to_channel(u_id, channel_id)
    return {}

def channel_removeowner(token, channel_id, u_id):
    """Remove user with user id u_id an owner of this channel

    Args:
        token (string)
        channel_id (int)
        u_id (int)

    Returns:
        (dict): {}
    """
    # Error Checks
    if not validate_channel_id(channel_id):
        raise InputError("Channel ID is not a valid channel")
    if not validate_token(token):
        raise AccessError("Token is not valid")
    if not validate_token_as_channel_member(token, channel_id):
        raise AccessError("Authorised user is not a member of channel with channel_id")
    if not validate_u_id(u_id):
        raise InputError("u_id is not a valid u_id")
    if not validate_u_id_as_channel_owner(u_id, channel_id):
        raise InputError("u_id is not owner of channel")
    data.remove_owner_from_channel(u_id, channel_id)
    return {}
