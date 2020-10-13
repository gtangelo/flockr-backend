"""
message feature implementation as specified by the specification

Feature implementation was written by Tam Do and Prathamesh Jagtap.

2020 T3 COMP1531 Major Project
"""

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
    validate_u_id_as_flockr_owner,
)
from action import (
    get_details_from_u_id,
    add_channel_to_user_list,
    get_lowest_u_id_user_in_channel,
    remove_channel_in_user_list,

def message_send(token, channel_id, message):
    """Send a message from authorised_user to the channel specified by channel_id

    Args:
        token (string)
        channel_id (int)
        message (string)

    Returns:
        (dict): { message_id }
    """
    return {
        'message_id': 1,
    }

def message_remove(token, message_id):
    """Given a message_id for a message, this message is removed from the channel

    Args:
        token (string)
        message_id (int)

    Returns:
        (dict): {}
    """
    # check valid token (AccessError)
    if not validate_token(token):
        raise AccessError("Token is invalid, please register/login")

    # check valid message_id (InputError) (each message has a unique id)
    on_list = False
    channel_details = {}
    for channels in data['channels']:
        for messages in channels['messages']:
            if messages['message_id'] == message_id:
                on_list = True
                channel_details = channels
    if not on_list:
        raise InputError("Message does not exist")
    
    # check if user is authorized
    authorized = False
    user_details = convert_token_to_user(token)
    condition_1 = validate_u_id_as_flockr_owner(user_details['u_id'])
    condition_2 = validate_u_id_as_channel_owner(user_details['u_id'], channel_details)
    if condition_1 or condition_2:
        authorized = True
    if not authorized:
        raise AccessError("User not authorized to remove message")

    # remove the message if user is flockr owner or channel owner
    # (Assumption) flockr owner does not need to be a part of the channel to remove message
    for channels in data['channels']:
        for messages in channels['messages']:
            if messages['message_id'] == message_id:
                channels['messages'].remove(messages)
    return {}

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