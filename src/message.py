"""
message feature implementation as specified by the specification

Feature implementation was written by Tam Do and Prathamesh Jagtap.

2020 T3 COMP1531 Major Project
"""

from datetime import timezone, datetime
from data import data
from error import InputError, AccessError
from validate import (
    validate_token,
    validate_channel_id,
    validate_user_in_channel,
    convert_token_to_user,
    validate_message_present,
    validate_universal_permission,
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
    is_valid_id, channel_data = validate_channel_id(channel_id)
    # Check if the channel_id is a valid channel
    if not is_valid_id:
        raise InputError("Channel ID is not a valid channel")
     # Check if token is valid
    if not validate_token(token):
        raise AccessError("Token is invalid, please register/login")
    if not validate_user_in_channel(token, channel_data):
        raise AccessError("Authorised user is not a member of channel with channel_id")

    # Add message to the channel
    channel_index = data['channels'].index(channel_data)
    # Generate the message_id
    data['total_messages'] += 1
    message_id = data['total_messages']
    # Get the u_id of the user`
    u_id = convert_token_to_user(token)
    # Get the time of when the message is sent
    time = datetime.now()
    time_created = time.replace(tzinfo=timezone.utc).timestamp()
    channel_data['messages'].append({
        'message_id': message_id,
        'u_id': u_id['u_id'],
        'message': message,
        'time_created': int(time_created),
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
    # check valid token (AccessError)
    if not validate_token(token):
        raise AccessError("Token is invalid, please register/login")

    # check valid message_id (InputError) (each message has a unique id)
    on_list, channel_details = validate_message_present(message_id)
    if not on_list:
        raise InputError("Message does not exist")

    # check if user is authorized
    authorized = validate_universal_permission(token, channel_details)
    if not authorized:
        raise AccessError("User not authorized to remove message")

    # remove the message if user is flockr owner or channel owner
    # (Assumption) flockr owner does not need to be a part of the channel to remove message
    for channels in data['channels']:
        for messages in channels['messages']:
            if messages['message_id'] == message_id:
                channels['messages'].remove(messages)
    return {}

# TOD0: new line and null terminator test as message
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

    # check if user is authorized
    authorized = validate_universal_permission(token, channel_details)
    if not authorized:
        raise AccessError("User not authorized to remove message")

    # remove message if new message is an empty string
    # edit the message if user is flockr owner or channel owner
    # (Assumption) flockr owner does not need to be a part of the channel to edit message
    if message == '':
        message_remove(token, message_id)

    for channels in data['channels']:
        for messages in channels['messages']:
            if messages['message_id'] == message_id:
                messages['message'] = message
    return {}
