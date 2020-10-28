"""
channels feature implementation as specified by the specification

Feature implementation was written by Richard Quisumbing.

2020 T3 COMP1531 Major Project
"""

from src.feature.validate import validate_token
from src.feature.action import convert_token_to_u_id
from src.feature.error import InputError, AccessError
from src.feature.data import data
from src.classes.Channel import Channel

def channels_list(token):
    """Provide a list of all channels (and their associated details) that the
    authorised user is part of

    Args:
        token (string): unique identifer of user

    Returns:
        (dict): { channels }
    """

    # Authorised user check.
    if not validate_token(token):
        raise AccessError("User cannot list channels, log in first.")

    # Get user ID from token.
    u_id = convert_token_to_u_id(token)
    
    # Add channels the user is a part of into joined_channels.
    user_details = data.get_user_details(u_id)
    channels = user_details['channels']
    joined_channels = []
    for channel in channels:
        joined_channels.append({
            'channel_id': channel['channel_id'],
            'name': channel['name']
        })

    return {
        "channels": joined_channels
    }

def channels_listall(token):
    """Provide a list of all channels (and their associated details)

    Args:
        token (string): unique identifer of user

    Returns:
        (dict): { channels }
    """

    # Authorised user check
    if not validate_token(token):
        raise AccessError("User cannot list channels, log in first.")

    # Add all available channels into all_channels (both public and private).
    all_channels = []
    for curr_channel in data.get_channels():
        channel_id_name = {
            'channel_id': curr_channel.get_channel_id(),
            'name': curr_channel.get_name()
        }
        all_channels.append(channel_id_name)

    return {
        "channels": all_channels
    }

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
    if not validate_token(token):
        raise AccessError("Token is invalid. User must log back in.")

    # Raise InputError if the channel name is invalid.
    if len(name) > 20 or len(name) < 1:
        raise InputError("Channel name is invalid, please enter a name between 1-20 characters.")

    # Generate channel_id.
    channel_id = 1
    if len(data.get_channels()) != 0:
        # Channel list is not empty.
        channel_list = data.get_channels()
        channel_id = channel_list[-1].get_channel_id() + 1

    # Create new channel and store it into data structure.
    channel_details = Channel(name, is_public, channel_id)
    data.add_channels(channel_details)

    u_id = convert_token_to_u_id(token)
    data.add_channel_to_user_list(u_id, channel_id)

    # Add user to created channel as well as making them owner.
    data.add_member_to_channel(u_id, channel_id)
    data.add_owner_to_channel(u_id, channel_id)

    return {
        'channel_id': channel_id,
    }
