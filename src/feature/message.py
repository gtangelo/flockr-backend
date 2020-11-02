"""
message feature implementation as specified by the specification

Feature implementation was written by Tam Do and Prathamesh Jagtap.

2020 T3 COMP1531 Major Project
"""

from datetime import timezone, datetime
import time
from threading import Timer, Thread
from src.feature.validate import (
    validate_token,
    validate_channel_id, 
    validate_token_as_channel_member,
    validate_message_present,
    validate_universal_permission,
)
from src.feature.action import convert_token_to_u_id
from src.feature.error import InputError, AccessError
from src.feature.data import data

def message_sendlater_helper(token, channel_id, message, time_delay):
    time.sleep(time_delay)
    message_send(token, channel_id, message)

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
    if not validate_token(token):
        raise AccessError("Token is invalid, please register/login")
    if len(message) > 1000:
        raise InputError("Message has more than 1000 characters")
    if len(message) == 0:
        raise InputError("Message is empty")
    if not validate_channel_id(channel_id):
        raise InputError("Channel ID is not a valid channel")
    if not validate_token_as_channel_member(token, channel_id):
        raise AccessError("Authorised user is not a member of channel with channel_id")

    # Add message to the channel
    message_id = data.generate_message_id()
    u_id = convert_token_to_u_id(token)
    data.create_message(u_id, channel_id, message_id, message)
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
    userAuthorized = False 
    # Error checks
    if not validate_token(token):
        raise AccessError("Token is invalid, please register/login")

    # check valid message_id (InputError) (each message has a unique id)
    on_list, channel_id = validate_message_present(message_id)
    if not on_list:
        raise InputError("Message does not exist")

    # check if user is authorized
    u_id = convert_token_to_u_id(token)
    valid_permission = validate_universal_permission(token, channel_id)

    # remove the message if user is flockr owner or channel owner or sent by authorized user
    # (Assumption) flockr owner does not need to be a part of the channel to remove message
    for channel in data.get_channels():
        for message in channel['messages']:
            if message['message_id'] == message_id:
                if message['u_id'] == u_id or valid_permission:
                    userAuthorized = True
                    data.remove_message(channel_id, message_id)
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
    on_list, channel_id = validate_message_present(message_id)
    if not on_list:
        raise InputError("Message does not exist")

    # check valid message data type
    if not isinstance(message, str):
        raise InputError("Message is not type string")
    
    if len(message) > 1000:
        raise InputError("Message has more than 1000 characters")

    # check if user is authorized
    u_id = convert_token_to_u_id(token)
    valid_permission = validate_universal_permission(token, channel_id)

    # edit the message if user is flockr owner or channel owner or sent by authorized user
    # (Assumption) flockr owner does not need to be a part of the channel to edit message
    for channel in data.get_channels():
        for curr_message in channel['messages']:
            if curr_message['message_id'] == message_id:
                if curr_message['u_id'] == u_id or valid_permission:
                    userAuthorized = True
                    data.edit_message(channel_id, message_id, message)
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
    # Error handling (Input/Access)
    if not validate_token(token):
        raise AccessError("Token is invalid, please register/login")
    if len(message) > 1000:
        raise InputError("Message has more than 1000 characters")
    if len(message) == 0:
        raise InputError("Message is empty")
    if not validate_channel_id(channel_id):
        raise InputError("Channel ID is not a valid channel")
    if not validate_token_as_channel_member(token, channel_id):
        raise AccessError("Authorised user is not a member of channel with channel_id")
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    if curr_time > time_sent:
        raise InputError("Time sent is a time in the past")

    # Send the message at the time_sent
    if curr_time == time_sent:
        send_message = message_send(token, channel_id, message)
        message_id = send_message['message_id']
    else:
        time_delay = int(time_sent - curr_time)
        #Timer(time_delay, lambda: message_send(token, channel_id, message)).start()
        message_id = data.generate_message_id()
        Thread(target=message_sendlater_helper, args=(token, channel_id, message, time_delay), daemon=True).start()
    return {
        'message_id': message_id
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
