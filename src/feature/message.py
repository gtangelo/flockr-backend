"""
message feature implementation as specified by the specification

Feature implementation was written by Tam Do and Prathamesh Jagtap.

2020 T3 COMP1531 Major Project
"""

from datetime import timezone, datetime
from src.helpers.validate import (
    validate_token,
    validate_channel_id, 
    validate_token_as_channel_member,
    validate_message_present,
    validate_universal_permission,
)
from src.helpers.action import convert_token_to_user
from src.feature.error import InputError, AccessError
from src.feature.data import data

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
    # Check if token is valid
    if not validate_token(token):
        raise AccessError("Token is invalid, please register/login")
    if len(message) > 1000:
        raise InputError("Message has more than 1000 characters")
    # Message is empty
    if len(message) == 0:
        raise InputError("Message is empty")
    # Authorised user has not joined the channel that they are trying to post to
    is_valid_id, channel_data = validate_channel_id(channel_id)
    # Check if the channel_id is a valid channel
    if not is_valid_id:
        raise InputError("Channel ID is not a valid channel")
    if not validate_token_as_channel_member(token, channel_data):
        raise AccessError("Authorised user is not a member of channel with channel_id")
    # Add message to the channel
    channel_index = data['channels'].index(channel_data)
    # Generate the message_id
    data['total_messages'] += 1
    message_id = data['total_messages']
    # Get the u_id of the user`
    u_id = convert_token_to_user(token)
    # Get the time of when the message is sent
    time_created = int(datetime.now().replace(tzinfo=timezone.utc).timestamp())
    channel_data['messages'].insert(0, {
        'message_id': message_id,
        'u_id': u_id['u_id'],
        'message': message,
        'time_created': time_created,
    })
    data['channels'][channel_index] = channel_data

    return {
        'message_id': message_id
    }

def message_remove(token, message_id):
    """Given a message_id for a message, this message is removed from the channel

    Args:
        token (string)
        message_id (int)

    Returns:
        (dict): {}
    """
    userAuthorized = False 
    # check valid token (AccessError)
    if not validate_token(token):
        raise AccessError("Token is invalid, please register/login")

    # check valid message_id (InputError) (each message has a unique id)
    on_list, channel_details = validate_message_present(message_id)
    if not on_list:
        raise InputError("Message does not exist")

    # check if user is authorized
    user_info = convert_token_to_user(token)
    valid_permission = validate_universal_permission(token, channel_details)

    # remove the message if user is flockr owner or channel owner or sent by authorized user
    # (Assumption) flockr owner does not need to be a part of the channel to remove message
    for channels in data['channels']:
        for messages in channels['messages']:
            if messages['message_id'] == message_id:
                if messages['u_id'] == user_info['u_id'] or valid_permission:
                    userAuthorized = True
                    channels['messages'].remove(messages)
    if not userAuthorized:
        raise AccessError("User not authorized to remove message")
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
    # remove message if new message is an empty string
    if message == '':
        return message_remove(token, message_id)

    userAuthorized = False 
    # check valid token (AccessError)
    if not validate_token(token):
        raise AccessError("Token is invalid, please register/login")

    # check valid message_id (InputError) (each message has a unique id)
    on_list, channel_details = validate_message_present(message_id)
    if not on_list:
        raise InputError("Message does not exist")

    # check valid message data type
    if not isinstance(message, str):
        raise InputError("Message is not type string")
    
    if len(message) > 1000:
        raise InputError("Message has more than 1000 characters")

    # check if user is authorized
    user_info = convert_token_to_user(token)
    valid_permission = validate_universal_permission(token, channel_details)

    # edit the message if user is flockr owner or channel owner or sent by authorized user
    # (Assumption) flockr owner does not need to be a part of the channel to edit message
    for channels in data['channels']:
        for messages in channels['messages']:
            if messages['message_id'] == message_id:
                if messages['u_id'] == user_info['u_id'] or valid_permission:
                    userAuthorized = True
                    messages['message'] = message
    if not userAuthorized:
        raise AccessError("User not authorized to edit message")
    return {}

def message_sendlater(token, channel_id, message, time_sent):
    """Send a message from authorised_user to the channel specified by 
    channel_id automatically at a specified time in the future

    Args:
        token (string)
        channel_id (int)
        message (string)
        time_sent (int)

    Returns:
        (dict): { message_id }
    """
    return {
        "message_id": 0,
    }

def message_react(token, message_id, react_id):
    """Given a message within a channel the authorised user is part of, add 
    a "react" to that particular message

    Args:
        token (string)
        message_id (int)
        react_id (int)

    Returns:
        (dict): {}
    """
    return {}

def message_unreact(token, message_id, react_id):
    """Given a message within a channel the authorised user is part of, 
    remove a "react" to that particular message

    Args:
        token (string)
        message_id (int)
        react_id (int)

    Returns:
        (dict): {}
    """
    return {}

def message_pin(token, message_id):
    """Given a message within a channel, mark it as "pinned" to be given 
    special display treatment by the frontend

    Args:
        token (string)
        message_id (int)

    Returns:
        (dict)
    """
    return {}

def message_unpin(token, message_id):
    """Given a message within a channel, remove it's mark as unpinned

    Args:
        token (string)
        message_id (int)

    Returns:
        (dict)
    """
    return {}
