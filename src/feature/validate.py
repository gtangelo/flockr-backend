"""
File containing helper functions that ease proccess in some feature functions.
These functions often need to validate information from the database.

Implementation was done by entire group.

2020 T3 COMP1531 Major Project
"""

import re

from src.feature.action import convert_token_to_u_id
from src.feature.data import data
from src.feature.globals import NON_EXIST, OWNER

# General functions to verify user

def validate_token(token):
    """Determines whether or not the user token has been authorised.

    Args:
        token (string): unique identifier for authorised user

    Returns:
        (bool): whether the token is valid
    """
    token_list = data.get_active_tokens()
    if token in token_list:
        return True
    return False

def validate_token_by_u_id(u_id):
    """Determines whether or not the user has been authorised based on u_id.

    Args:
        u_id (int): u_id for user

    Returns:
        (bool): whether the u_id has an active token
    """
    is_valid = False
    for user in data.get_active_users():
        if user['u_id'] == u_id:
            is_valid = True
    return is_valid

def validate_u_id(u_id):
    """Returns whether the `u_id` is valid.

    Args:
        u_id (int): u_id of the user

    Returns:
        (bool): True if u_id is found. False is otherwise.
    """
    users_list = data.get_user_ids()
    if u_id in users_list:
        return True
    return False

def validate_u_id_as_flockr_owner(u_id):
    """Determines the given u_id is a flockr owner or not

    Args:
        u_id (int): u_id of user

    Returns:
        (bool): True if u_id is a flockr owner. False otherwise.
    """
    for member in data.get_users():
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
    valid_email_syntax = r"^[a-z0-9]+[\._-]?[a-z0-9]+[@]\w+[.]\w+$"
    if len(email) <= 320 and len(email) >= 3 and re.search(valid_email_syntax, email):
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
    """Returns whether the name contains only letters and '-'

    Args:
        name (string): should be >= 1 && <= 50

    Returns:
        (bool): if valid, true, otherwise false.
    """
    valid_chars_name = '^[A-Za-z-]+$'
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
    for user in data.get_users():
        if user['password'] == password:
            return True
    return False

def validate_handle_str(handle_str):
    ''' Confirms if the inputted handle string is valid.
    Args:
        handle_str (string): new handle string

    Returns:
        (bool): if valid, true, otherwise false.
    ''' 
    valid_chars_handle = '^[A-Za-z!-~0-9.]+$'
    if re.search(valid_chars_handle, handle_str):
        if len(handle_str) <= 20 and len(handle_str) >= 3:
            return True
    return False

def validate_handle_unique(handle_str):
    ''' Confirms that the inputted handle_str is unique
    Args:
        handle_str (string): new handle string
    
    Returns:
        (bool): if valid, true, otherwise false.
    '''
    for user in data.get_users():
        if user['handle_str'] == handle_str:
            return False
    return True

# Helper functions relating to channels
def validate_channel_id(channel_id):
    """Returns whether or not channel_id is a valid channel id.

    Args:
        channel_id (int)

    Returns:
        (bool): True if the channel_id is valid. False otherwise.
    """
    channel_list = data.get_channel_ids()
    if channel_id in channel_list:
        return True
    return False

def validate_token_as_channel_member(token, channel_id):
    """Returns whether or not the user is a member of a channel based on the token.

    Args:
        token (string)
        channel_id (int)

    Returns:
        (bool): True if member is in channel. False otherwise.
    """
    if validate_token(token):
        channel_details = data.get_channel_details(channel_id)
        member_list = list(map(lambda member: member['u_id'], channel_details['all_members']))
        u_id = convert_token_to_u_id(token)
        if u_id in member_list:
            return True
    return False

def validate_token_as_channel_owner(token, channel_id):
    """Returns whether or not the user is an owner of a channel based on the token.

    Args:
        token (string)
        channel_id (int)

    Returns:
        (bool): True if member is an owner in the channel. False otherwise.
    """
    if validate_token(token):
        channel_details = data.get_channel_details(channel_id)
        owner_list = list(map(lambda owner: owner['u_id'], channel_details['owner_members']))
        u_id = convert_token_to_u_id(token)
        if u_id in owner_list:
            return True
    return False

def validate_u_id_as_channel_member(u_id, channel_id):
    """Return whether if user is a member of the given channel

    Args:
        u_id (int)
        channel_id (int)

    Returns:
        (bool): True if u_id is a channel member. False otherwise.
    """
    channel_details = data.get_channel_details(channel_id)
    members_list = list(map(lambda member: member['u_id'], channel_details['all_members']))
    if u_id in members_list:
        return True
    return False

def validate_u_id_as_channel_owner(u_id, channel_id):
    """Return whether u_id given is an owner in the channel

    Args:
        u_id (int)
        channel_id (int)

    Returns:
        (bool): True if u_id is a channel owner. False otherwise.
    """
    channel_details = data.get_channel_details(channel_id)
    owners_list = list(map(lambda owner: owner['u_id'], channel_details['owner_members']))
    if u_id in owners_list:
        return True
    return False


def validate_flockr_owner(u_id):
    """Return whether user with u_id is a flockr owner

    Args:
        u_id (int): u_id for user

    Returns:
        (bool): True if user is flockr owner. False otherwise.
    """
    for user in data.get_users():
        if user['u_id'] == u_id and user['permission_id'] == OWNER:
            return True
    return False

def validate_message_present(message_id):
    """Returns whether message with message_id is available
       and the channel it is located in

    Args:
        message_id (int): unqiue id for message

    Returns:
        (bool): True if message is present. False otherwise.
        (bool, int): Returns true if message_id exist. False otherwise. Returns
        the channel_id where the message_id was found
    """
    on_list = False
    channel_id = NON_EXIST
    for channel in data.get_channels():
        for message in channel['messages']:
            if message['message_id'] == message_id:
                on_list = True
                channel_id = channel['channel_id']
    return on_list, channel_id

def validate_universal_permission(token, channel_id):
    """Validates whether user is a flockr owner or channel owner

    Args:
        token (string): unique identifier for authorised user
        channel_data (dictionary): channel information

    Returns:
        (bool): True if either criteria is met. False otherwise.
    """
    authorized = False
    u_id = convert_token_to_u_id(token)
    condition_1 = validate_u_id_as_flockr_owner(u_id)
    condition_2 = validate_u_id_as_channel_owner(u_id, channel_id)
    if condition_1 or condition_2:
        authorized = True
    return authorized

# Helper functions relating to messages.

def validate_react_id(react_id, message_id):
    """Validates whether the react_id exists or not in the message.

    Args:
        react_id (int): unique identifier for a specific message react.
        message_id (int): unique id for message.

    Returns:
        (bool): True if either criteria is met. False otherwise.
    """

    valid_react = False
    for channel in data.get_channels():
        for message in channel['messages']:
            if message['message_id'] == message_id:
                for react in message['reacts']:
                    if react['react_id'] == react_id:
                        valid_react = True
    return valid_react
    