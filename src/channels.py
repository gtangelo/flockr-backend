"""
channels feature implementation as specified by the specification

Feature implementation was written by Richard Quisumbing.

2020 T3 COMP1531 Major Project
"""

from src.validate import validate_token
from src.action import convert_token_to_user
from src.error import InputError, AccessError
from src.data import data

def channels_list(token):
    """Provide a list of all channels (and their associated details) that the
    authorised user is part of

    Args:
        token (string): unique identifer of user

    Returns:
        (dict): { channels }
    """

    # Authorised user check.
    authorised_to_list = validate_token(token)
    if not authorised_to_list:
        raise AccessError("User cannot list channels, log in first.")

    # Get user ID from token.
    user_details = convert_token_to_user(token)
    u_id = user_details['u_id']

    # Add channels the user is a part of into joined_channels.
    joined_channels = {}
    joined_channels['channels'] = []

    for curr_channel in data['channels']:
        for member in curr_channel['all_members']:
            if member['u_id'] == u_id:
                channel_id_name = {
                    'channel_id': curr_channel['channel_id'],
                    'name': curr_channel['name']
                }
                joined_channels['channels'].append(channel_id_name)

    return joined_channels

def channels_listall(token):
    """Provide a list of all channels (and their associated details)

    Args:
        token (string): unique identifer of user

    Returns:
        (dict): { channels }
    """

    # Authorised user check
    authorised_to_list = validate_token(token)
    if not authorised_to_list:
        raise AccessError("User cannot list channels, log in first.")

    # Add all available channels into all_channels (both public and private).
    all_channels = {}
    all_channels['channels'] = []

    for curr_channel in data['channels']:
        channel_id_name = {
            'channel_id': curr_channel['channel_id'],
            'name': curr_channel['name']
        }
        all_channels['channels'].append(channel_id_name)

    return all_channels

def channels_create(token, name, is_public):
    """Creates a new channel with that name that is either a public or private channel

    Args:
        token (string)
        name (string)
        is_public (bool)

    Returns:
        (dict): { channel_id }
    """

    # Authorised user can create channels.
    authorised_to_list = validate_token(token)
    if not authorised_to_list:
        raise AccessError("Token is invalid. User must log back in.")

    # Raise InputError if the channel name is invalid.
    if len(name) > 20 or len(name) < 1:
        raise InputError("Channel name is invalid, please enter a name between 1-20 characters.")

    # Generate channel_id.
    channel_id = 1
    if len(data['channels']) != 0:
        # Channel list is not empty.
        channel_id = data['channels'][-1]['channel_id'] + 1

    # Create new channel and populate its keys.
    channel_details = {}

    channel_details['channel_id'] = channel_id
    channel_details['name'] = name
    channel_details['is_public'] = is_public
    channel_details['all_members'] = []
    channel_details['owner_members'] = []
    channel_details['messages'] = []

    # Obtain u_id from token and then add the user into the channel member lists.
    creator = convert_token_to_user(token)
    user_details = {}
    user_details['u_id'] = creator['u_id']
    user_details['name_first'] = creator['name_first']
    user_details['name_last'] = creator['name_last']

    # Add user to created channel as well as making them owner.
    channel_details['all_members'].append(user_details)
    channel_details['owner_members'].append(user_details)

    # Store channel_details into the channels list inside data.py.
    data['channels'].append(channel_details)

    # Store channel name and id into user channel lists.
    channel_id_name_only = {}
    channel_id_name_only['channel_id'] = channel_id
    channel_id_name_only['name'] = name
    channel_id_name_only['is_public'] = is_public
    for user_index, user in enumerate(data['users']):
        if user['u_id'] == creator['u_id']:
            data['users'][user_index]['channels'].append(channel_id_name_only)

    return {
        'channel_id': channel_id,
    }
