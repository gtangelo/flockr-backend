"""
other feature implementation as specified by the specification

Feature implementation was written by Tam Do and Gabriel Ting.

2020 T3 COMP1531 Major Project
"""
from src.action import convert_token_to_user, get_details_from_u_id
from src.validate import (
    validate_flockr_owner,
    validate_token, 
    validate_token_as_channel_member, 
    validate_u_id,
)
from src.error import AccessError, InputError
from src.data import data, MEMBER, OWNER

def clear():
    """Resets the internal data of the application to it's initial state

    Returns:
        (dict): {}
    """
    data['active_users'] = []
    data['users'] = []
    data['channels'] = []
    data['first_owner_u_id'] = None
    data['total_messages'] = None
    return {}

def users_all(token):
    """Returns a list of all users and their associated details

    Args:
        token (string)

    Returns:
        (dict): { users }
    """

    # Error handling (Access)
    if not validate_token(token):
        raise AccessError("Token is not valid")

    all_users = []

    for user_id in data['users']:
        user_details = get_details_from_u_id(user_id['u_id'])
        all_users.append({
            'u_id': user_details['u_id'],
            'email': user_details['email'],
            'name_first': user_details['name_first'],
            'name_last': user_details['name_last'],
            'handle_str': user_details['handle_str'],
        })

    return {
        'users': all_users
    }

def admin_userpermission_change(token, u_id, permission_id):
    """Given a User by their user ID, set their permissions to new permissions
    described by permission_id

    Args:
        token (string)
        u_id (int)
        permission_id (int)
    """
    if not validate_token(token):
        raise AccessError("invalid token")
    if not validate_u_id(u_id):
        raise InputError("u_id does not refer to a valid user")
    user_id = convert_token_to_user(token)
    if not validate_flockr_owner(user_id['u_id']):
        raise AccessError("The authorised user is not an owner")
    if permission_id not in (MEMBER, OWNER):
        raise InputError("permission_id does not refer to a value permission")
    if u_id == data['first_owner_u_id'] and permission_id == MEMBER:
        raise InputError("First flockr owner cannot be a member")
    
    for user in data['users']:
        if user['u_id'] == u_id:
            user['permission_id'] = permission_id
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
    # Error handling
    if not validate_token(token):
        raise AccessError("Token is not valid")
    if len(query_str) == 0:
        raise InputError("query_str must be atleast 1 character long (inclusive)")

    msg_dict = {}
    for channel in data['channels']:
        if validate_token_as_channel_member(token, channel):
            for msg in channel['messages']:
                msg_dict[msg['message']] = {
                    'message_id': msg['message_id'],
                    'time_created': msg['time_created'],
                    }

    # Get the u_id
    u_id = convert_token_to_user(token)
    matched_msg = []
    for key, val in msg_dict.items():
        if key.find(query_str) != -1:
            matched_msg.append({
                'message_id': val['message_id'],
                'u_id': u_id['u_id'],
                'message': key,
                'time_created': val['time_created'],
            })

    return {
        'messages': matched_msg
    }
