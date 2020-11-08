"""
channel feature implementation as specified by the specification

Feature implementation was written by Gabriel Ting, Tam Do, Prathamesh Jagtap.

2020 T3 COMP1531 Major Project
"""
import pickle

from src.feature.confirm import confirm_channel_id, confirm_token, confirm_u_id
from src.feature.validate import (
    validate_token_as_channel_member,
    validate_u_id_as_channel_owner,
    validate_u_id_as_channel_member,
)
from src.feature.action import (
    convert_token_to_u_id,
    get_messages_list,
)
from src.classes.error import InputError, AccessError
from src.globals import DATA_FILE, OWNER, MEMBER


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
    data = pickle.load(open(DATA_FILE, "rb"))

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_channel_id(data, channel_id)
    confirm_u_id(data, u_id)

    # Error check: the authorised user is not already a member of the channel 
    # (i.e. not in channel when calling this function)
    if not validate_token_as_channel_member(data, token, channel_id):
        raise AccessError(description="AccessError: User not authorized to invite, please join channel")

    # Error check (Assumption): User with u_id is already in the channel but is 
    # invited again
    if validate_u_id_as_channel_member(data, u_id, channel_id):
        raise InputError(description="InputError: User is already part of the channel")
    
    user = data.get_user_details(u_id)
    data.add_member_to_channel(u_id, channel_id)
    data.add_channel_to_user_list(u_id, channel_id)

    # if user is flockr owner: make him the group owner too
    if user['permission_id'] == OWNER:
        data.add_owner_to_channel(u_id, channel_id)
    
    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)

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
    data = pickle.load(open(DATA_FILE, "rb"))

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_channel_id(data, channel_id)

    # Error check: Authorised user is not a member of channel with channel_id
    if not validate_token_as_channel_member(data, token, channel_id):
        raise AccessError(description="AccessError: Authorised user is not a member of the channel")

    channel_details = data.get_channel_details(channel_id)

    return {
        'name': channel_details['name'],
        'owner_members': channel_details['owner_members'],
        'all_members': channel_details['all_members'],
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

    data = pickle.load(open(DATA_FILE, "rb"))

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_channel_id(data, channel_id)

    # Error check: start is greater than the total number of messages in the channel
    channel_details = data.get_channel_details(channel_id)
    if start >= len(channel_details['messages']) and start != 0:
        raise InputError(description=f"InputError: start value ({start}) is greater than the \
        total number of messages in the channel ({len(channel_details['messages'])} messages)")
    if start < 0:
        raise InputError(description=f"InputError: start value ({start}) must be greater than or equal to 0")

    # Error check: Authorised user is not a member of channel with channel_id
    if not validate_token_as_channel_member(data, token, channel_id):
        raise AccessError(description="AccessError: Authorised user is not a member of the channel")

    # (Assumption) Case where there are no messages in the channel
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

    # Create the messages list.
    messages_list = get_messages_list(data, token, channel_id)

    if end == -1:
        messages = messages_list[start:]
    else:
        messages = messages_list[start:end]

    return {
        'messages': messages,
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
    data = pickle.load(open(DATA_FILE, "rb"))

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_channel_id(data, channel_id)

    # Error check: Authorised user is not a member of channel with channel_id
    if not validate_token_as_channel_member(data, token, channel_id):
        raise AccessError(description="AccessError: Authorised user is not a member of the channel")

    u_id = convert_token_to_u_id(data, token)
    data.remove_member_from_channel(u_id, channel_id)
    data.remove_owner_from_channel(u_id, channel_id)
    data.delete_channel_from_user_list(u_id, channel_id)
    channel_details = data.get_channel_details(channel_id)

    # Case where all owners have left, assign the oldest member as the new 
    # channel owner.
    if len(channel_details['owner_members']) == 0 and len(channel_details['all_members']) != 0:
        data.add_owner_to_channel(channel_details['all_members'][0]['u_id'], channel_id)
    
    # Case where all members have left, delete channel from database
    if len(channel_details['all_members']) == 0:
        data.delete_channel(channel_id)

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)

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
    data = pickle.load(open(DATA_FILE, "rb"))

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_channel_id(data, channel_id)

    # Error check (Assumption): Check whether user is a channel member already
    if validate_token_as_channel_member(data, token, channel_id):
        return {}

    # Error check: User cannot join a channel if they are a flockr member and
    # the channel is private
    u_id = convert_token_to_u_id(data, token)
    user = data.get_user_details(u_id)
    channel_details = data.get_channel_details(channel_id)
    if user['permission_id'] == MEMBER and not channel_details['is_public']:
        raise AccessError(description="AccessError: Private channel cannot be joined unless user is a flockr owner")

    
    data.add_member_to_channel(user['u_id'], channel_id)
    data.add_channel_to_user_list(user['u_id'], channel_id)

    # If the user is the flockr owner, make their permissions as a channel owner.
    if user['permission_id'] == OWNER:
        data.add_owner_to_channel(user['u_id'], channel_id)
    
    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)
    
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
    data = pickle.load(open(DATA_FILE, "rb"))

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_channel_id(data, channel_id)
    confirm_u_id(data, u_id)

    # Error check: User id u_id is already an owner of the channel
    if validate_u_id_as_channel_owner(data, u_id, channel_id):
        raise InputError(description=f"InputError: User with u_id {u_id} is not an owner of channel")

    # Error check: User is not an owner of the flockr, or an owner of this channel
    if not validate_token_as_channel_member(data, token, channel_id):
        raise AccessError(description="AccessError: Authorised user is not an owner of the flockr, or an owner of the channel")

    # Add user as member if not already.
    if not validate_u_id_as_channel_member(data, u_id, channel_id):
        data.add_member_to_channel(u_id, channel_id)
        data.add_channel_to_user_list(u_id, channel_id)
    data.add_owner_to_channel(u_id, channel_id)

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)
    
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
    data = pickle.load(open(DATA_FILE, "rb"))

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_channel_id(data, channel_id)
    confirm_u_id(data, u_id)

    # Error check: When user with user id u_id is not an owner of the channel
    if not validate_u_id_as_channel_owner(data, u_id, channel_id):
        raise InputError(description=f"InputError: User with u_id {u_id} is not an owner of channel")

    # Error check: User is not an owner of the flockr, or an owner of this channel
    if not validate_token_as_channel_member(data, token, channel_id):
        raise AccessError(description="AccessError: Authorised user is not an owner of the flockr, or an owner of the channel")
    
    # Error check (Assumption): There must be at least one owner in the channel
    channel_data = data.get_channel_details(channel_id)
    if len(channel_data['owner_members']) == 1:
        raise InputError(description="InputError: There must be at least one owner in the channel")
    
    data.remove_owner_from_channel(u_id, channel_id)

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)

    return {}
