"""
message feature implementation as specified by the specification

Feature implementation was written by Tam Do, Prathamesh Jagtap, Gabriel Ting
and Richard Quisumbing.

2020 T3 COMP1531 Major Project
"""

from datetime import timezone, datetime
from src.globals import DATA_FILE
from threading import Thread
import time
import pickle

from src.feature.validate import (
    validate_token,
    validate_channel_id,
    validate_token_as_channel_member,
    validate_token_as_channel_owner, 
    validate_u_id_as_channel_member,
    validate_u_id_as_flockr_owner,
    validate_message_id,
    validate_react_id, 
    validate_active_react_id, 
    validate_universal_permission,
)
from src.feature.action import convert_token_to_u_id
from src.feature.error import InputError, AccessError

def delay_message_send(token, channel_id, message, time_delay):
    """Executes message_send after the given delay

    Args:
        token (string)
        channel_id (int)
        message (string)
        time_delay (int)
    """
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
    data = pickle.load(open(DATA_FILE, "rb"))
    # Error handling (Input/Access)
    if not validate_token(data, token):
        raise AccessError("Token is invalid, please register/login")
    if len(message) > 1000:
        raise InputError("Message has more than 1000 characters")
    if len(message) == 0:
        raise InputError("Message is empty")
    if not validate_channel_id(data, channel_id):
        raise InputError("Channel ID is not a valid channel")
    if not validate_token_as_channel_member(data, token, channel_id):
        raise AccessError("Authorised user is not a member of channel with channel_id")

    # Add message to the channel
    message_id = data.generate_message_id()
    u_id = convert_token_to_u_id(data, token)
    data.create_message(u_id, channel_id, message_id, message)

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)

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
    data = pickle.load(open(DATA_FILE, "rb"))

    userAuthorized = False
    # Error checks
    if not validate_token(data, token):
        raise AccessError("Token is invalid, please register/login")

    # check valid message_id (InputError) (each message has a unique id)
    if not validate_message_id(data, message_id):
        raise InputError("Message does not exist")

    # check if user is authorized
    channel_id = data.get_channel_id_with_message_id(message_id)
    u_id = convert_token_to_u_id(data, token)
    valid_permission = validate_universal_permission(data, token, channel_id)

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
    
    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)
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
    data = pickle.load(open(DATA_FILE, "rb"))

    # remove message if new message is an empty string
    if message == '':
        return message_remove(token, message_id)

    userAuthorized = False
    # check valid token (AccessError)
    if not validate_token(data, token):
        raise AccessError("Token is invalid, please register/login")

    # check valid message_id (InputError) (each message has a unique id)
    if not validate_message_id(data, message_id):
        raise InputError("Message does not exist")

    # check valid message data type
    if not isinstance(message, str):
        raise InputError("Message is not type string")

    if len(message) > 1000:
        raise InputError("Message has more than 1000 characters")

    # check if user is authorized
    u_id = convert_token_to_u_id(data, token)
    channel_id = data.get_channel_id_with_message_id(message_id)
    valid_permission = validate_universal_permission(data, token, channel_id)

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

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)

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
    data = pickle.load(open(DATA_FILE, "rb"))

    # Error handling (Input/Access)
    if not validate_token(data, token):
        raise AccessError("Token is invalid, please register/login")
    if len(message) > 1000:
        raise InputError("Message has more than 1000 characters")
    if len(message) == 0:
        raise InputError("Message is empty")
    if not validate_channel_id(data, channel_id):
        raise InputError("Channel ID is not a valid channel")
    if not validate_token_as_channel_member(data, token, channel_id):
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
        message_id = data.generate_message_id()
        with open(DATA_FILE, 'wb') as FILE:
            pickle.dump(data, FILE)
        Thread(target=delay_message_send, args=(token, channel_id, message, time_delay), daemon=True).start()
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
    data = pickle.load(open(DATA_FILE, "rb"))

    if not validate_token(data, token):
        raise AccessError("Invalid token")
    
    if not validate_message_id(data, message_id):
        raise InputError("message_id is not a valid message")
    if not validate_react_id(data, react_id, message_id):
        raise InputError("react_id is not a valid React ID")
    u_id = convert_token_to_u_id(data, token)
    if validate_active_react_id(data, u_id, message_id, react_id):
        raise InputError("Message with ID message_id already contains an active React with ID react_id")

    channel_id = data.get_channel_id_with_message_id(message_id)
    is_member = validate_u_id_as_channel_member(data, u_id, channel_id)
    is_flock_owner = validate_u_id_as_flockr_owner(data, u_id)

    if not is_member and not is_flock_owner:
        raise AccessError("Flockr member not in channel with message_id")
    active_react_ids = data.get_active_react_ids(u_id, message_id)
    if active_react_ids != []:
        for active_react_id in active_react_ids:
            with open(DATA_FILE, 'wb') as FILE:
                pickle.dump(data, FILE)
            message_unreact(token, message_id, active_react_id)
    data = pickle.load(open(DATA_FILE, "rb"))
    message = data.get_message_details(channel_id, message_id)
    message['reacts'][react_id - 1]['u_ids'].append(u_id)

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)

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
    data = pickle.load(open(DATA_FILE, "rb"))

    ## Error handling (Input/Access).
    if not validate_token(data, token):
        raise AccessError("Token is invalid, please register/login")

    u_id = convert_token_to_u_id(data, token)
    if not validate_message_id(data, message_id):
        raise InputError("message_id is not a valid message")
    if not validate_react_id(data, react_id, message_id):
        raise InputError("react_id is not a valid React ID")
    if not validate_active_react_id(data, u_id, message_id, react_id):
        raise InputError("Message with ID message_id already contains a non-active React with ID react_id")

    # Check if user is flockr owner.
    channel_id = data.get_channel_id_with_message_id(message_id)
    is_member = validate_u_id_as_channel_member(data, u_id, channel_id)
    is_flock_owner = validate_u_id_as_flockr_owner(data, u_id)
    if not is_member and not is_flock_owner:
        # Check if the user is in the channel that the message is in.
        raise AccessError("Flockr member not in channel with message_id")

    # Otherwise unreact the message with react_id.
    message = data.get_message_details(channel_id, message_id)
    message['reacts'][react_id - 1]['u_ids'].remove(u_id)

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)

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
    data = pickle.load(open(DATA_FILE, "rb"))

    ## Error handling (Input/Access)

    # Check if the message_id is valid (Exists or not).
    if not validate_message_id(data, message_id):
        raise InputError("Message does not exist")

    # Check if message is already pinned.
    channel_id = data.get_channel_id_with_message_id(message_id)
    channel_messages = data.get_channel_details(channel_id)['messages']
    for curr_message in channel_messages:
        if curr_message['message_id'] == message_id:
            if curr_message['is_pinned']:
                raise InputError("Message is already pinned.")

    # Authorised user check.
    if not validate_token(data, token):
        raise AccessError("Token is invalid, please register/login")

    # Check if user is a flockr owner.
    u_id = convert_token_to_u_id(data, token)
    if not validate_u_id_as_flockr_owner(data, u_id):
        # Check if the user is in the channel that the message is in.
        if not validate_token_as_channel_member(data, token, channel_id):
            raise AccessError("Authorised user is not a member of channel with channel_id")
        # Check if the user is an owner of the channel or is a flockr owner.
        if not validate_token_as_channel_owner(data, token, channel_id):
            raise AccessError("Authorised user is not an owner of the channel")

    # Pin message (If user is a flockr owner or channel owner).
    for curr_channel in data.get_channels():
        for curr_message in curr_channel['messages']:
            if curr_message['message_id'] == message_id:
                curr_message['is_pinned'] = True
    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)
    return {}

def message_unpin(token, message_id):
    """Given a message within a channel, remove it's mark as unpinned

    Args:
        token (string)
        message_id (int)

    Returns:
        (dict)
    """
    data = pickle.load(open(DATA_FILE, "rb"))

    ## Error handling (Input/Access)

    # Check if the message_id is valid (Exists or not).
    if not validate_message_id(data, message_id):
        raise InputError("Message does not exist")

    # Check if message is already unpinned.
    channel_id = data.get_channel_id_with_message_id(message_id)
    channel_messages = data.get_channel_details(channel_id)['messages']
    for curr_message in channel_messages:
        if curr_message['message_id'] == message_id:
            if not curr_message['is_pinned']:
                raise InputError("Message is already unpinned.")

    # Authorised user check.
    if not validate_token(data, token):
        raise AccessError("Token is invalid, please register/login")

    # Check if user is a flockr owner.
    u_id = convert_token_to_u_id(data, token)
    if not validate_u_id_as_flockr_owner(data, u_id):
        # Check if the user is in the channel that the message is in.
        if not validate_token_as_channel_member(data, token, channel_id):
            raise AccessError("Authorised user is not a member of channel with channel_id")
        # Check if the user is an owner of the channel or is a flockr owner.
        if not validate_token_as_channel_owner(data, token, channel_id):
            raise AccessError("Authorised user is not an owner of the channel")

    # Pin message (If user is a flockr owner or channel owner).
    for curr_channel in data.get_channels():
        for curr_message in curr_channel['messages']:
            if curr_message['message_id'] == message_id:
                curr_message['is_pinned'] = False

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)

    return {}
