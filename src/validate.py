"""
File containing helper functions that ease proccess in some feature functions.
These functions often need to validate information from the database.

Implementation was done by entire group.

2020 T3 COMP1531 Major Project
"""

import re
from action import convert_token_to_user
from data import data, OWNER

# General functions to verify user

def validate_token(token):
    """Determines whether or not the user token has been authorised.

    Args:
        token (string): unique identifier for authorised user

    Returns:
        (bool): whether the token is valid
    """
    for user in data['active_users']:
        if user['token'] == token:
            return True
    return False

def validate_token_by_u_id(u_id):
    """Determines whether or not the user has been authorised based on u_id.

    Args:
        u_id (int): u_id for user

    Returns:
        (bool): whether the u_id has an active token
    """
    for user in data['active_users']:
        if user['u_id'] == u_id:
            return True
        return False

def validate_u_id(u_id):
    """Returns whether the `u_id` is valid.

    Args:
        u_id (int): u_id of the user

    Returns:
        (bool): True if u_id is found. False is otherwise.
    """
    for member in data['users']:
        if member['u_id'] == u_id:
            return True
    return False

def validate_u_id_as_flockr_owner(u_id):
    """Determines the given u_id is a flockr owner or not

    Args:
        u_id (int): u_id of user

    Returns:
        (bool): True if u_id is a flockr owner. False otherwise.
    """
    for member in data['users']:
        if member['u_id'] == u_id and member['permission_id'] == OWNER:
            return True
    return False

# Helper functions for authorisation

def validate_create_email(email):
    """Returns whether the email address is valid.

    Args:
        email (string): should follow regex syntax, have characters <= 320 && >= 3

    Returns:
        (bool): if valid, true, otherwise false.
    """
    if len(email) <= 320 and len(email) >= 3 and re.search(r'[\w.-]+@[\w.-]+.\w+', email):
        return True
    return False

def validate_password_length(password):
    """Returns whether the password length is valid

    Args:
        password (string): should be be atleast 6 chars but not greater than 128 chars

    Returns:
        (bool): if valid, true, otherwise false.
    """
    if (len(password) < 6 or len(password) > 128):
        return False
    return True

def validate_password_chars(password):
    """Returns whether the password characters are valid

    Args:
        password (string): checks if characters inputted are valid

    Returns:
        (bool): if valid, true, otherwise false.
    """
    valid_chars_password = '^[!-~]+$'
    if re.search(valid_chars_password, password):
        return True
    return False

def validate_names(name):
    """Returns whether either the name is valid

    Args:
        name (string): should be >= 1 && <= 50

    Returns:
        (bool): if valid, true, otherwise false.
    """
    if len(name) < 1 or len(name) > 50:
        return False
    return True

def validate_names_characters(name):
    """Returns whether the name contains only letters and '-' and ' '

    Args:
        name (string): should be >= 1 && <= 50

    Returns:
        (bool): if valid, true, otherwise false.
    """
    valid_chars_name = '^[A-Za-z- ]+$'
    if re.search(valid_chars_name, name):
        return True
    return False

def validate_password(password):
    """Confirms if the password inputted is correct for a given user.

    Args:
        password (string): password to check

    Returns:
        (bool): if valid, true, otherwise false.
    """
    for user in data['users']:
        if user['password'] == password:
            return True
    return False

# Helper functions relating to channels
def validate_channel_id(channel_id):
    """Returns whether or not channel_id is a valid channel id.

    Args:
        channel_id (int): channel_id of channel

    Returns:
        (bool, dict): {channel_id, name, messages, all_members,
                        owner_members, is_public}
                    If channel_id is valid, returns True and 'channel_data'
                    which stores all relevant information in a dictionary
                    belonging to the channel with the 'channel_id'.
                    Otherwise, returns False and an empty dict {}.
    """
    for curr_channel in data['channels']:
        if channel_id == curr_channel['channel_id']:
            return True, curr_channel
    return False, {}

def validate_user_in_channel(token, channel_data):
    """Returns whether or not the user is a member of a channel.

    Args:
        token (string): unique identifier for authorised user
        channel_data (dict): channel information

    Returns:
        (bool): whether the token is found within 'channel_data'
    """
    if validate_token(token):
        user_details = convert_token_to_user(token)
        for user in channel_data['all_members']:
            if user['u_id'] == user_details['u_id']:
                return True

    return False

def validate_u_id_as_channel_owner(u_id, channel):
    """Return whether u_id given is an owner in the channel

    Args:
        u_id (int): u_id of the user
        channel (dict): contain info of the channel
            {channel_id, name, messages, all_members, owner_members, is_public}

    Returns:
        (bool): True if u_id is a channel owner. False otherwise.
    """
    for owner in channel['owner_members']:
        if owner['u_id'] == u_id:
            return True
    return False

def validate_user_as_member(u_id, channel):
    """Return whether if user is a member of the given channel

    Args:
        u_id (int): u_id of user
        channel (dict): details containing about the channel
            {channel_id, name, messages, all_members, owner_members, is_public}

    Returns:
        (bool): True if user is a member of that channel. False otherwise.
    """
    for user in channel['all_members']:
        if user['u_id'] == u_id:
            return True
    return False

def validate_flockr_owner(u_id):
    """Return whether user with u_id is a flockr owner

    Args:
        u_id (int): u_id for user

    Returns:
        (bool): True if user is flockr owner. False otherwise.
    """
    for user in data['users']:
        if user['u_id'] == u_id and user['permission_id'] == OWNER:
            return True
    return False
    