"""
other feature implementation as specified by the specification

Feature implementation was written by Tam Do and Gabriel Ting.

2020 T3 COMP1531 Major Project
"""
import pickle

from src.feature.confirm import confirm_token, confirm_u_id
from src.feature.validate import (
    validate_flockr_owner,
    validate_token_as_channel_member, 
)
from src.feature.action import convert_token_to_u_id, get_messages_list
from src.classes.error import AccessError, InputError
from src.globals import DATA_FILE, INVALID_QUERY, MEMBER, OWNER

def clear():
    """Resets the internal data of the application to it's initial state

    Returns:
        (dict): {}
    """

    data = pickle.load(open(DATA_FILE, "rb"))

    data.clear_active_users()
    data.clear_users()
    data.clear_channels()
    data.clear_first_owner_u_id()
    data.clear_total_messages()
    data.clear_reset_users()

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)
    
    return {}

def users_all(token):
    """Returns a list of all users and their associated details

    Args:
        token (string)

    Returns:
        (dict): { users }
    """
    data = pickle.load(open(DATA_FILE, "rb"))

    # Error checks: Basic validation
    confirm_token(data, token)

    all_users = []
    for u_id in data.get_user_ids():
        user_details = data.get_user_details(u_id)
        all_users.append({
            'u_id': user_details['u_id'],
            'email': user_details['email'],
            'name_first': user_details['name_first'],
            'name_last': user_details['name_last'],
            'handle_str': user_details['handle_str'],
            'profile_img_url': user_details['profile_img_url']
        })

    return { 'users': all_users }

def admin_userpermission_change(token, u_id, permission_id):
    """Given a User by their user ID, set their permissions to new permissions
    described by permission_id

    Args:
        token (string)
        u_id (int)
        permission_id (int)
    """

    data = pickle.load(open(DATA_FILE, "rb"))

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_u_id(data, u_id)


    if permission_id not in (MEMBER, OWNER):
        raise InputError(description="InputError: permission_id does not refer to a value permission")
    
    # Error check: The authorised user is not an owner
    user_id = convert_token_to_u_id(data, token)
    if not validate_flockr_owner(data, user_id):
        raise AccessError(description="AccessError: User is not a flockr owner")

    # Error check (Assumption): First flockr owner cannot have member permissions
    if u_id == data.get_first_owner_u_id() and permission_id == MEMBER:
        raise InputError(description="InputError: First flockr owner cannot be a member")

    data.set_user_permission_id(u_id, permission_id)

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)

    return {}

def search(token, query_str):
    """Given a query string, return a collection of messages in all of the
    channels that the user has joined that match the query

    Args:
        token (string)
        query_str (string)

    Returns:
        (dict): { messages }
    """

    data = pickle.load(open(DATA_FILE, "rb"))

    # Error checks: Basic validation
    confirm_token(data, token)

    # Error check (Assumption): query_str must be atleast 1 character
    if len(query_str) == 0:
        raise InputError(description="InputError: query_str must be atleast 1 character long")

    all_messages = []
    for channel in data.get_channels():
        if validate_token_as_channel_member(data, token, channel['channel_id']):
            messages = get_messages_list(data, token, channel['channel_id'])
            for msg in messages:
                all_messages.append(msg)

    # Get the u_id
    matched_msg = []
    for message in all_messages:
        if message['message'].find(query_str) != INVALID_QUERY:
            matched_msg.insert(0, message)

    return { 'messages': matched_msg }
