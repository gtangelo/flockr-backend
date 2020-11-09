"""
message feature implementation as specified by the specification

Feature implementation was written by Tam Do, Prathamesh Jagtap, Gabriel Ting
and Richard Quisumbing.

2020 T3 COMP1531 Major Project
"""
import time
import pickle
from datetime import timezone, datetime
from threading import Thread

from src.feature.confirm import (
    confirm_channel_id, 
    confirm_message_id, 
    confirm_react_id, 
    confirm_token
)
from src.feature.validate import (
    validate_token_as_channel_member,
    validate_token_as_channel_owner, 
    validate_u_id_as_channel_member,
    validate_u_id_as_flockr_owner,
    validate_active_react_id, 
    validate_universal_permission,
)
from src.feature.action import convert_token_to_u_id
from src.classes.error import InputError, AccessError
from src.globals import DATA_FILE


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

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_channel_id(data, channel_id)

    # Error check: Message is more than 1000 characters or 0 characters
    if len(message) > 1000:
        raise InputError(description="InputError: Message has more than 1000 characters")
    if len(message) == 0:
        raise InputError(description="InputError: Message is empty")

    # Error check: the authorised user has not joined the channel they are trying to post to
    if not validate_token_as_channel_member(data, token, channel_id):
        raise AccessError(description="AccessError: Authorised user is not a member of the channel")

    # Add message to the channel
    message_id = data.generate_message_id()
    u_id = convert_token_to_u_id(data, token)
    data.create_message(u_id, channel_id, message_id, message)

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)

    return { 'message_id': message_id }


def message_remove(token, message_id):
    """Given a message_id for a message, this message is removed from the channel

    Args:
        token (string)
        message_id (int)

    Returns:
        (dict): {}
    """
    data = pickle.load(open(DATA_FILE, "rb"))

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_message_id(data, message_id)

    # remove the message if user is flockr owner or channel owner or sent by authorized user
    # (Assumption) flockr owner does not need to be a part of the channel to remove message
    channel_id = data.get_channel_id_with_message_id(message_id)
    u_id = convert_token_to_u_id(data, token)
    valid_permission = validate_universal_permission(data, token, channel_id)
    userAuthorized = False
    for channel in data.get_channels():
        for message in channel['messages']:
            if message['message_id'] == message_id:
                if message['u_id'] == u_id or valid_permission:
                    userAuthorized = True
                    data.remove_message(channel_id, message_id)
    
    # Error check: User was not authorised to remove the message
    if not userAuthorized:
        raise AccessError(description="AccessError: User not authorized to remove message")
    
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

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_message_id(data, message_id)

    # Error check: Message is more than 1000 characters or 0 characters
    if len(message) > 1000:
        raise InputError(description="InputError: Message has more than 1000 characters")

    # edit the message if user is flockr owner or channel owner or sent by authorized user
    # (Assumption) flockr owner does not need to be a part of the channel to edit message
    u_id = convert_token_to_u_id(data, token)
    channel_id = data.get_channel_id_with_message_id(message_id)
    valid_permission = validate_universal_permission(data, token, channel_id)
    userAuthorized = False
    for channel in data.get_channels():
        for curr_message in channel['messages']:
            if curr_message['message_id'] == message_id:
                if curr_message['u_id'] == u_id or valid_permission:
                    userAuthorized = True
                    data.edit_message(channel_id, message_id, message)
    
    # Error check: User was not authorised to edit the message
    if not userAuthorized:
        raise AccessError("AccessError: User not authorized to edit message")

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

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_channel_id(data, channel_id)

    # Error check: Message is more than 1000 characters or 0 characters
    if len(message) > 1000:
        raise InputError(description="InputError: Message has more than 1000 characters")
    if len(message) == 0:
        raise InputError(description="InputError: Message is empty")

    # Error check: Time sent is a time in the past
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    if curr_time > time_sent:
        raise InputError(description="InputError: Time sent is a time in the past")

    # Error check: the authorised user has not joined the channel they are trying to post to
    if not validate_token_as_channel_member(data, token, channel_id):
        raise AccessError(description="AccessError: Authorised user is not a member of the channel")
    
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
    
    return { 'message_id': message_id }

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

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_message_id(data, message_id)
    confirm_react_id(data, message_id, react_id)
    
    # Error check: Message with ID message_id already contains an active React 
    # with ID react_id from the authorised user
    u_id = convert_token_to_u_id(data, token)
    if validate_active_react_id(data, u_id, message_id, react_id):
        raise InputError(description=f"InputError: Message already contains an active react")
    
    # Error check (Assumption): Flockr member not in channel with message_id 
    channel_id = data.get_channel_id_with_message_id(message_id)
    is_member = validate_u_id_as_channel_member(data, u_id, channel_id)
    is_flock_owner = validate_u_id_as_flockr_owner(data, u_id)
    if not is_member and not is_flock_owner:
        raise AccessError(description=f"AccessError: User is not in the channel that has the message_id {message_id}")
    
    # unreact all active reacts (based on assumption)
    active_react_ids = data.get_active_react_ids(u_id, message_id)
    if active_react_ids != []:
        for active_react_id in active_react_ids:
            message_unreact(token, message_id, active_react_id)
    
    # reload to get updated data from message_unreact
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

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_message_id(data, message_id)
    confirm_react_id(data, message_id, react_id)

    # Error check: Message with ID message_id does not contain an active React with ID react_id
    u_id = convert_token_to_u_id(data, token)
    if not validate_active_react_id(data, u_id, message_id, react_id):
        raise InputError(description=f"InputError: Message already contains a non-active react")


    # Error check (Assumption): Flockr member not in channel with message_id 
    channel_id = data.get_channel_id_with_message_id(message_id)
    is_member = validate_u_id_as_channel_member(data, u_id, channel_id)
    is_flock_owner = validate_u_id_as_flockr_owner(data, u_id)
    if not is_member and not is_flock_owner:
        raise AccessError(description=f"AccessError: User is not in the channel that has the message_id {message_id}")

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

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_message_id(data, message_id)

    # Error check: Message with ID message_id is already pinned
    channel_id = data.get_channel_id_with_message_id(message_id)
    channel_messages = data.get_channel_details(channel_id)['messages']
    for curr_message in channel_messages:
        if curr_message['message_id'] == message_id:
            if curr_message['is_pinned']:
                raise InputError(description="InputError: Message is already pinned")

    # Check if user is a flockr owner.
    u_id = convert_token_to_u_id(data, token)
    flockr_owner = validate_u_id_as_flockr_owner(data, u_id)
    channel_member = validate_token_as_channel_member(data, token, channel_id)
    channel_owner = validate_token_as_channel_owner(data, token, channel_id)

    # Error check: The authorised user is not a member of the channel that the message is within
    if not flockr_owner and not channel_member:
        raise AccessError(description="AccessError: Authorised user is not a member of the channel \
        that contains the message")
    
    # Error check: The authorised user is not an owner
    if not flockr_owner and not channel_owner:
        raise AccessError(description="AccessError: The authorised user is not an owner of the channel")
    
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

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_message_id(data, message_id)

    # Check if message is already unpinned.
    channel_id = data.get_channel_id_with_message_id(message_id)
    channel_messages = data.get_channel_details(channel_id)['messages']
    for curr_message in channel_messages:
        if curr_message['message_id'] == message_id:
            if not curr_message['is_pinned']:
                raise InputError(description="InputError: Message is already unpinned")

    # Check if user is a flockr owner.
    u_id = convert_token_to_u_id(data, token)
    flockr_owner = validate_u_id_as_flockr_owner(data, u_id)
    channel_member = validate_token_as_channel_member(data, token, channel_id)
    channel_owner = validate_token_as_channel_owner(data, token, channel_id)

    # Error check: The authorised user is not a member of the channel that the message is within
    if not flockr_owner and not channel_member:
        raise AccessError(description="AccessError: Authorised user is not a member of the channel \
        that contains the message")
    
    # Error check: The authorised user is not an owner
    if not flockr_owner and not channel_owner:
        raise AccessError(description="AccessError: The authorised user is not an owner of the channel")
    
    # Pin message (If user is a flockr owner or channel owner).
    for curr_channel in data.get_channels():
        for curr_message in curr_channel['messages']:
            if curr_message['message_id'] == message_id:
                curr_message['is_pinned'] = False

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)

    return {}
