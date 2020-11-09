"""
channels feature implementation as specified by the specification

Feature implementation was written by Richard Quisumbing.

2020 T3 COMP1531 Major Project
"""
import pickle

from src.feature.confirm import confirm_token
from src.feature.action import convert_token_to_u_id
from src.classes.error import InputError
from src.globals import DATA_FILE

def channels_list(token):
    """Provide a list of all channels (and their associated details) that the
    authorised user is part of

    Args:
        token (string): unique identifer of user

    Returns:
        (dict): { channels }
    """

    data = pickle.load(open(DATA_FILE, "rb"))
    
    confirm_token(data, token)

    u_id = convert_token_to_u_id(data, token)
    user_details = data.get_user_details(u_id)

    # Add channels the user is a part of into joined_channels.
    joined_channels = []
    for channel in user_details['channels']:
        joined_channels.append({
            'channel_id': channel['channel_id'],
            'name': channel['name']
        })

    return { 'channels': joined_channels }

def channels_listall(token):
    """Provide a list of all channels (and their associated details)

    Args:
        token (string): unique identifer of user

    Returns:
        (dict): { channels }
    """

    data = pickle.load(open(DATA_FILE, "rb"))

    confirm_token(data, token)

    # Add all available channels into all_channels (both public and private).
    all_channels = []
    for curr_channel in data.get_channels():
        all_channels.append({
            'channel_id': curr_channel['channel_id'],
            'name': curr_channel['name']
        })

    return { 'channels': all_channels }


def channels_create(token, name, is_public):
    """Creates a new channel with that name that is either a public or private channel

    Args:
        token (string)
        name (string)
        is_public (bool)

    Returns:
        (dict): { channel_id }
    """

    data = pickle.load(open(DATA_FILE, "rb"))

    confirm_token(data, token)

    # Error check: Channel name validation
    if len(name) > 20 or len(name) < 1:
        raise InputError(description="Channel name must be between 1 to 20 characters")

    # Generate channel_id.
    channel_id = 1
    if len(data.get_channels()) != 0:
        channel_list = data.get_channels()
        channel_id = channel_list[-1]['channel_id'] + 1

    # Create new channel and store it into data structure.
    data.create_channel(name, is_public, channel_id)
    u_id = convert_token_to_u_id(data, token)
    data.add_channel_to_user_list(u_id, channel_id)

    # Add user to created channel as well as making them owner.
    data.add_member_to_channel(u_id, channel_id)
    data.add_owner_to_channel(u_id, channel_id)

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)

    return { 'channel_id': channel_id }
