"""
other feature implementation as specified by the specification

2020 T3 COMP1531 Major Project
"""
from action import convert_token_to_user
from error import AccessError, InputError
from validate import validate_flockr_owner, validate_token, validate_u_id
from data import MEMBER, OWNER, data

def clear():
    """Resets the internal data of the application to it's initial state
    """
    data['active_users'] = []
    data['users'] = []
    data['channels'] = []
    data['first_owner_u_id'] = None
    data['total_messages'] = None

def users_all(token):
    """Returns a list of all users and their associated details

    Args:
        token (string)

    Returns:
        (dict): { messages }
    """
    return {
        'users': [
            {
                'u_id': 1,
                'email': 'cs1531@cse.unsw.edu.au',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'hjacobs',
            },
        ],
    }

def admin_userpermission_change(token, u_id, permission_id):
    """Given a User by their user ID, set their permissions to new permissions 
    described by permission_id

    Args:
        token (string)
        u_id (int)
        permission_id (int)
    """
    if not validate_u_id(u_id):
        raise InputError("u_id does not refer to a valid user")
    if permission_id != OWNER and permission_id != MEMBER:
        raise InputError("permission_id does not refer to a value permission")
    if u_id == data['first_owner_u_id'] and permission_id == MEMBER:
        raise InputError("First flockr owner cannot be a member")
    if not validate_token(token):
        raise AccessError("invalid token")
    user_id = convert_token_to_user(token)
    if not validate_flockr_owner(user_id['u_id']):
        raise AccessError("The authorised user is not an owner")
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
    return {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
    }