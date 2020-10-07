"""
channel feature implementation as specified by the specification

Feature implementation was written by Gabriel Ting, Tam Do, Prathamesh Jagtap.

2020 T3 COMP1531 Major Project
"""

from data import data
from error import InputError, AccessError
from validate import (
    user_is_authorise,
    validate_channel_id,
    validate_user_in_channel,
    convert_token_to_user,
    validate_u_id,
    validate_u_id_as_channel_owner,
    validate_user_as_member,
)
from action import (
    get_details_from_u_id,
    add_channel_to_user_list,
    get_lowest_u_id_user_in_channel,
    remove_channel_in_user_list,
)

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
    # raise InputError if channel_id is invalid
    channel_valid, channel_info = validate_channel_id(channel_id)
    if not channel_valid:
        raise InputError("Channel ID is not a valid channel")
        # raises AccessError if token is invalid
    if not validate_u_id(u_id):
        raise InputError("Invited user not found")
    if not user_is_authorise(token):
        raise AccessError("Token is invalid, please register/login")
    if validate_user_as_member(u_id, channel_info):
        raise AccessError("User is already part of the channel")

    user_details = convert_token_to_user(token)

    # if user is flockr owner: make him the group owner too (add tests)
    # check if inviter is authorized to invite by being a member of channel
    for channels in data['channels']:
        if channels['channel_id'] == channel_id:
            for members in channels['all_members']:
                if members['u_id'] == user_details['u_id']:
                    for users in data['users']:
                        if users['u_id'] == u_id:
                            # add user info to channel database
                            invited_user = {
                                'u_id'      : u_id,
                                'name_first': users['name_first'],
                                'name_last' : users['name_last'],
                            }
                            channels['all_members'].append(invited_user)

                            if users['is_flockr_owner']:
                                channels['owner_members'].append(invited_user)

                            # add channel info to user database
                            channel_info = {
                                'channel_id': channel_id,
                                'name'      : channels['name'],
                                'is_public' : channels['is_public']
                            }
                            users['channels'].append(channel_info)
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
    # raises AccessError if token is invalid
    user_authorized = user_is_authorise(token)
    if not user_authorized:
        raise AccessError("Token is invalid, please register/login")

    # raise InputError if channel_id is invalid
    channel_valid, channel_info = validate_channel_id(channel_id)
    if not channel_valid:
        raise InputError("Channel ID is not a valid channel")
    u_id = convert_token_to_user(token)['u_id']
    # raise AccessError if not authorized to see details
    if not validate_user_as_member(u_id, channel_info):
        raise AccessError("User is not authorized to see channel details")
    # check whether user is authorized to see channel details
    user_details = convert_token_to_user(token)
    for channels in data['channels']:
        if channels['channel_id'] == channel_id:
            for members in channels['all_members']:
                if members['u_id'] == user_details['u_id']:
                    channel_info = {
                        'name'         : channels['name'],
                        'owner_members': channels['owner_members'],
                        'all_members'  : channels['all_members'],
                    }
    return channel_info

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
    is_valid_id, channel_data = validate_channel_id(channel_id)

    if not is_valid_id:
        raise InputError("Channel ID is not a valid channel")
    if start > len(channel_data['messages']):
        raise InputError("start is greater than the total number of messages in the channel")
    if not user_is_authorise(token):
        raise AccessError("Token is not valid")
    if not validate_user_in_channel(token, channel_data):
        raise AccessError("Authorised user is not a member of channel with channel_id")

    # Case where there are no messages in the channel
    if len(channel_data['messages']) == 0:
        return {
            'messages': [],
            'start': -1,
            'end': -1,
        }

    # Case where there are messages in the channel
    end = start + 50
    if end > len(channel_data['messages']):
        end = -1

    message_list = []
    for message in channel_data['messages']:
        message_list.append(message)

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
    is_valid_id, channel_data = validate_channel_id(channel_id)
    if not is_valid_id:
        raise InputError("Channel ID is not a valid channel")
    if not user_is_authorise(token):
        raise AccessError("Token is not valid")
    if not validate_user_in_channel(token, channel_data):
        raise AccessError("Authorised user is not a member of channel with channel_id")

    user_details = convert_token_to_user(token)
    channel_index = data['channels'].index(channel_data)

    # Remove user as member
    for user in channel_data['all_members']:
        if user['u_id'] == user_details['u_id']:
            channel_data['all_members'].remove(user)
            break
    # Remove user as owner
    for user in channel_data['owner_members']:
        if user['u_id'] == user_details['u_id']:
            channel_data['owner_members'].remove(user)
            break

    data['channels'][channel_index] = channel_data
    remove_channel_in_user_list(user_details['u_id'], channel_id)

    # Case where all owners have left, assign a user with the lowest u_id as
    # new owner
    if len(channel_data['owner_members']) == 0 and len(channel_data['all_members']) != 0:
        lowest_u_id_user = get_lowest_u_id_user_in_channel(channel_data)
        channel_data['owner_members'].append(lowest_u_id_user)

    # Case where all members have left, delete channel from database
    if len(channel_data['all_members']) == 0:
        data['channels'].pop(channel_index)

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
    is_valid_id, channel_data = validate_channel_id(channel_id)
    if not is_valid_id:
        raise InputError("Channel ID is not a valid channel")
    if not user_is_authorise(token):
        raise AccessError("Token is not valid")
    if validate_user_in_channel(token, channel_data):
        return {}

    user_details = convert_token_to_user(token)
    if not user_details['is_flockr_owner'] and not channel_data['is_public']:
        raise AccessError("Authorised user is not a member of channel with channel_id")

    channel_index = data['channels'].index(channel_data)

    # Add user as member if not already
    if not validate_user_as_member(user_details['u_id'], channel_data):
        channel_data['all_members'].append({
            'u_id': user_details['u_id'],
            'name_first': user_details['name_first'],
            'name_last': user_details['name_last'],
        })

    # If user is flockr owner (if not already owner, add them)
    if user_details['is_flockr_owner']:
        if not validate_u_id_as_channel_owner(user_details['u_id'], channel_data):
            channel_data['owner_members'].append({
                'u_id': user_details['u_id'],
                'name_first': user_details['name_first'],
                'name_last': user_details['name_last'],
            })

    data['channels'][channel_index] = channel_data

    add_channel_to_user_list(user_details['u_id'], channel_data)
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
    is_valid_id, channel_data = validate_channel_id(channel_id)
    if not is_valid_id:
        raise InputError("Channel ID is not a valid channel")
    if not user_is_authorise(token):
        raise AccessError("Token is not valid")
    if not validate_user_in_channel(token, channel_data):
        raise AccessError("Authorised user is not a member of channel with channel_id")
    if not validate_u_id(u_id):
        raise InputError("u_id is not a valid u_id")
    if validate_u_id_as_channel_owner(u_id, channel_data):
        raise InputError("u_id is already owner of channel")

    channel_index = data['channels'].index(channel_data)

    # Get the user that matches with the u_id
    user_details = get_details_from_u_id(u_id)

    # Add user as member if not already
    if not validate_user_as_member(u_id, channel_data):
        channel_data['all_members'].append({
            'u_id': user_details['u_id'],
            'name_first': user_details['name_first'],
            'name_last': user_details['name_last'],
        })

    # Add user as owner if not already
    if not validate_u_id_as_channel_owner(u_id, channel_data):
        channel_data['owner_members'].append({
            'u_id': user_details['u_id'],
            'name_first': user_details['name_first'],
            'name_last': user_details['name_last'],
        })

    data['channels'][channel_index] = channel_data

    # Add channel to user list if channel is not already in list
    add_channel_to_user_list(u_id, channel_data)
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
    is_valid_id, channel_data = validate_channel_id(channel_id)
    if not is_valid_id:
        raise InputError("Channel ID is not a valid channel")
    if not user_is_authorise(token):
        raise AccessError("Token is not valid")
    if not validate_user_in_channel(token, channel_data):
        raise AccessError("Authorised user is not a member of channel with channel_id")
    if not validate_u_id(u_id):
        raise InputError("u_id is not a valid u_id")
    if not validate_u_id_as_channel_owner(u_id, channel_data):
        raise InputError("u_id is not owner of channel")

    channel_index = data['channels'].index(channel_data)
    # Get the user that matches with the u_id
    user_details = get_details_from_u_id(u_id)

    # Remove user as owner
    for user in channel_data['owner_members']:
        if user['u_id'] == u_id:
            channel_data['owner_members'].remove({
                'u_id': user_details['u_id'],
                'name_first': user_details['name_first'],
                'name_last': user_details['name_last'],
            })
            break

    data['channels'][channel_index] = channel_data
    return {}
