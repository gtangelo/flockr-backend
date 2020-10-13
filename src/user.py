"""
user feature implementation as specified by the specification

Feature implementation was written by Christian Ilagan and Richard Quisumbing.

2020 T3 COMP1531 Major Project
"""
from data import data
from validate import (
    validate_token,
    validate_names,
    validate_names_characters,
    validate_change_name,
    validate_handle_str,
    validate_handle_unique,
) 
from action import (
    convert_token_to_user
)    
from error import AccessError, InputError
def user_profile(token, u_id):
    """For a valid user, returns information about their user_id, email, first
    name, last name, and handle

    Args:
        token (string)
        u_id (int)

    Returns:
        (dict): { user }
    """
    return {
        'user': {
        	'u_id': 1,
        	'email': 'cs1531@cse.unsw.edu.au',
        	'name_first': 'Hayden',
        	'name_last': 'Jacobs',
        	'handle_str': 'hjacobs',
        },
    }

def user_profile_setname(token, name_first, name_last):
    """Update the authorised user's first and last name

    Args:
        token (string)
        name_first (string)
        name_last (string)

    Returns:
        (dict): {}
    """
    if not validate_token(token):
        raise InputError("Invalid token")
    if not validate_change_name(name_first):
        raise InputError("Name should be between 1-50 chars")
    if not validate_change_name(name_last):
        raise InputError("Name should be between 1-50 chars")
    if len(name_first) > 0:
        if not validate_names_characters(name_first):
            raise InputError("Invalid chars inputted")
    if len(name_last) > 0:
        if not validate_names_characters(name_last):
            raise InputError("Invalid chars inputted")
    # changing the name in the active users field 
    for active_user in data['active_users']:
        if active_user['token'] == token:
            if len(name_first) > 0:
                active_user['name_first'] = name_first
            if len(name_last) > 0:
                active_user['name_last'] = name_last
            break

    # changing name in the users field
    user_details = convert_token_to_user(token)
    for user in data['users']:
        if user['u_id'] == user_details['u_id']:
            if len(name_first) > 0:
                user['name_first'] = name_first
            if len(name_last) > 0:
                user['name_last'] = name_last
            break
    return {
    }
    
     

def user_profile_setemail(token, email):
    return {
    }

def user_profile_sethandle(token, handle_str):
    '''Update authorised users handle

    Args: 
    token (string)
    handle_str (string)

    Returns:
        (dict): {}
    '''
    if not validate_handle_unique(handle_str):
        raise InputError("This handle already exists")
    if not validate_handle_str(handle_str):
        raise InputError("Invalid characters, must be between 3-20 chars")

    # updating in active users list.
    for active_user in data['active_users']:
        if active_user['token'] == token:
            active_user['handle_str'] = handle_str
            break

    # updating in users list.
    user_details = convert_token_to_user(token)
    for user in data['users']:
        if user['u_id'] == user_details['u_id']:
            user['handle_str'] = handle_str
            break
    
    return {
    }