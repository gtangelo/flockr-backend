"""
user feature implementation as specified by the specification

Feature implementation was written by Christian Ilagan and Richard Quisumbing.

2020 T3 COMP1531 Major Project
"""

from src.helpers.validate import (
    validate_token,
    validate_names,
    validate_names_characters,
    validate_handle_str,
    validate_handle_unique,
    validate_create_email,
)
from src.helpers.action import (
    convert_token_to_user
)
from src.feature.error import AccessError, InputError
from src.feature.data import data

def user_profile(token, u_id):
    """For a valid user, returns information about their user_id, email, first
    name, last name, and handle

    Args:
        token (string)
        u_id (int)

    Returns:
        (dict): { user }
    """

    # Authorised user check.
    authorised_to_display_profile = validate_token(token)
    if not authorised_to_display_profile:
        raise AccessError("User cannot display another user's profile, must log in first.")

    # InputError is raised for when a u_id does not match any user in user list inside data.py.
    count = 0
    for curr_user in data['users']:
        if curr_user['u_id'] == u_id:
            count += 1

    if count == 0:
        raise InputError("User with u_id is not a valid user.")

    # Search data.py for the valid user with matching u_id.
    profile_details = {}
    profile_details['user'] = {}

    for curr_user in data['users']:
        if curr_user['u_id'] == u_id:
            profile_details['user']['u_id'] = u_id
            profile_details['user']['email'] = curr_user['email']
            profile_details['user']['name_first'] = curr_user['name_first']
            profile_details['user']['name_last'] = curr_user['name_last']
            profile_details['user']['handle_str'] = curr_user['handle_str']

    return profile_details

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
    if not validate_names(name_first) or not validate_names(name_last):
        raise InputError("Name should be between 1-50 chars")
    if not validate_names_characters(name_first) or not validate_names_characters(name_last):
        raise InputError("Invalid chars inputted")

    # changing the name in the active users field
    for active_user in data['active_users']:
        if active_user['token'] == token:
            active_user['name_first'] = name_first
            active_user['name_last'] = name_last

    # changing name in the users field
    user_details = convert_token_to_user(token)
    for user in data['users']:
        if user['u_id'] == user_details['u_id']:
            user['name_first'] = name_first
            user['name_last'] = name_last

    # changing name in channels field - all_members
    for channel in data['channels']:
        for user in channel['all_members']:
            if user['u_id'] == user_details['u_id']:
                user['name_first'] = name_first
                user['name_last'] = name_last
        for owner in channel['owner_members']:
            if owner['u_id'] == user_details['u_id']:
                owner['name_first'] = name_first
                owner['name_last'] = name_last

    return {}

def user_profile_setemail(token, email):
    """Update the authorised user's email.

    Args:
        token (string): unique identifier of user.
        email (string): what the email will be set to.

    Returns:
        (dict): Contains no key types.
    """

    # Authorised user check.
    authorised_to_display_profile = validate_token(token)
    if not authorised_to_display_profile:
        raise AccessError("User cannot display another user's profile, must log in first.")

    # Check for email name validity.
    is_email_valid = validate_create_email(email)
    if not is_email_valid:
        raise InputError("Email contains invalid syntax. Try again.")

    # Check for whether email is already in use.
    for curr_user in data['users']:
        if curr_user['email'] == email:
            raise InputError("Email is already taken. Try again.")

    # Obtain u_id from token.
    user_details = convert_token_to_user(token)

    # Loop through users list in data.py and update the email of the user supplying the token.
    for curr_user in data['users']:
        if user_details['u_id'] == curr_user['u_id']:
            curr_user['email'] = email

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
    if not validate_token(token):
        raise InputError("Invalid Token.")
    if not validate_handle_unique(handle_str):
        raise InputError("This handle already exists")
    if not validate_handle_str(handle_str):
        raise InputError("Invalid characters, must be between 3-20 chars")

    # updating in active users list.
    for active_user in data['active_users']:
        if active_user['token'] == token:
            active_user['handle_str'] = handle_str

    # updating in users list.
    user_details = convert_token_to_user(token)
    for user in data['users']:
        if user['u_id'] == user_details['u_id']:
            user['handle_str'] = handle_str

    return {}


def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    """Given a URL of an image on the internet, crops the image within bounds (x_start, y_start) and (x_end, y_end). Position (0,0) is the top left.

    Args:
        token (string)
        img_url (string)
        x_start (int)
        y_start (int)
        x_end (int)
        y_end (int)

    Returns:
        (dict): {}
    """
    return {}
