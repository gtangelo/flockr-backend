"""
message feature implementation as specified by the specification

Feature implementation was written by Tam Do and Prathamesh Jagtap.

2020 T3 COMP1531 Major Project
"""

from datetime import datetime
from data import data, OWNER, MEMBER
from error import InputError, AccessError
from validate import (
    validate_token,
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

def message_send(token, channel_id, message):
    """Send a message from authorised_user to the channel specified by channel_id

    Args:
        token (string)
        channel_id (int)
        message (string)

    Returns:
        (dict): { message_id }
    """

    # Error handling (Input/Access)
    # Message has more than 1000 characters
    if len(message) > 1000:
        raise InputError("Message has more than 1000 characters")
    # Authorised user has not joined the channel that they are trying to post to
    channel_data = validate_channel_id(channel_id)
    if not validate_user_in_channel(token, channel_data):
        raise AccessError("Authorised user is not a member of channel with channel_id")
    # Check if the channel_id is a valid channel
    is_valid_id = validate_channel_id(channel_id)
    if not is_valid_id:
        raise InputError("Channel ID is not a valid channel")
    # Check if token is valid
    if not validate_token(token):
        raise AccessError("Token is invalid, please register/login")

    # Add message to the channel
    channel_index = data['channels'].index(channel_data)
    # Generate the message_id
    message_id = data['total_messages']
    # Get the u_id of the user
    u_id = convert_token_to_user(token)
    # Get the time of when the message is sent
    current_time = datetime.now()
    dt_string = current_time.strftime("%d/%m/%Y %H:%M:%S")
    channel_data['messages'].append({
        'message_id': message_id,
        'u_id': u_id,
        'message': message,
        'time_created': dt_string,
    })
    data['channels'][channel_index] = channel_data

    return {
        'message_id': message_id,
    }

def message_remove(token, message_id):
    """Given a message_id for a message, this message is removed from the channel

    Args:
        token (string)
        message_id (int)

    Returns:
        (dict): {}
    """
    return {
    }

def message_edit(token, message_id, message):
    """Given a message, update it's text with new text. If the new message is an
    empty string, the message is deleted.

    Args:
        token (string)
        message_id (int)
        message (string)

    Returns:
        (dict): {}
    """
    return {
    }
