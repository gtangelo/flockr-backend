"""
standup feature implementation as specified by the specification

Feature implementation was written by Prathamesh Jagtap.

2020 T3 COMP1531 Major Project
"""
import pickle
from threading import Thread
from datetime import timezone, datetime

from src.feature.action import (
    token_to_handle_name,
    set_standup_inactive
)
from src.feature.validate import ( 
    validate_token_as_channel_member,
)
from src.feature.confirm import confirm_channel_id, confirm_token
from src.classes.error import InputError, AccessError
from src.globals import DATA_FILE

def standup_start(token, channel_id, length):
    """For a given channel, start the standup period whereby for the next 
    "length" seconds if someone calls "standup_send" with a message, it is 
    buffered during the X second window then at the end of the X second window 
    a message will be added to the message queue in the channel from the user 
    who started the standup. X is an integer that denotes the number of seconds 
    that the standup occurs for

    Args:
        token (string)
        channel_id (int)
        length (int)

    Returns:
        (dict): { time_finish }
    """
    data = pickle.load(open(DATA_FILE, "rb"))
    
    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_channel_id(data, channel_id)

    # Error check: An active standup is currently running in this channel
    if data.specify_standup_status(channel_id)['is_active']:
        raise InputError(description="Standup is already running in the channel")

    # Error check (Assumption): User must be in the channel to start a standup
    if not validate_token_as_channel_member(data, token, channel_id):
        raise AccessError(description="User must be in the channel to start a standup")

    # Error check (Assumption): Length specified is less than or equal to 0
    if length <= 0:
        raise InputError(description="Length of standup must be greater than 0 seconds")

    # set standup as active and calculate time_finish
    completion_time = int(datetime.now(tz=timezone.utc).timestamp()) + length
    data.set_standup_active_in_channel(channel_id, completion_time)

    # when completion time is met, set standup as inactive and send messages
    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)
    Thread(target=set_standup_inactive, args=(token, channel_id, length), daemon=True).start()

    return { 'time_finish': completion_time }

def standup_active(token, channel_id):
    """For a given channel, return whether a standup is active in it, and what
    time the standup finishes. If no standup is active, then time_finish
    returns None

    Args:
        token (string)
        channel_id (int)

    Returns:
        (dict): { is_active, time_finish }
    """
    data = pickle.load(open(DATA_FILE, "rb"))

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_channel_id(data, channel_id)

    # Error check (Assumption): User must be in the channel to start a standup
    if not validate_token_as_channel_member(data, token, channel_id):
        raise AccessError(description="User must be in the channel to start a standup")

    return data.specify_standup_status(channel_id)

def standup_send(token, channel_id, message):
    """Sending a message to get buffered in the standup queue, assuming a
    standup is currently active

    Args:
        token (string)
        channel_id (int)
        message (string)

    Returns:
        (dict): {}
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

    # if an active standup is not currently running in this channel
    standup_information = data.specify_standup_status(channel_id)
    if not standup_information['is_active']:
        raise InputError(description="Standup is not currently running in this channel")

    # Error check (Assumption): User must be in the channel to start a standup
    if not validate_token_as_channel_member(data, token, channel_id):
        raise AccessError(description="User must be in the channel to start a standup")

    # append message to 'standup_messages' string
    handle_name = token_to_handle_name(data, token)
    if data.show_standup_messages(channel_id) == "":
        new_message = f'{handle_name}: {message}'
    else:
        new_message = f'\n{handle_name}: {message}'
    data.append_standup_message(channel_id, new_message)

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)
    
    return {} 
