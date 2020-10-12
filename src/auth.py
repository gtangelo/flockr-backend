"""
auth feature implementation which covers the basic process of creating and
managing users as outlined in the specification.

Feature implementation was written by Christian Ilagan.

2020 T3 COMP1531 Major Project
"""

from data import data, OWNER, MEMBER
from validate import (
    validate_create_email,
    validate_names,
    validate_names_characters,
    validate_password_length,
    validate_password,
    validate_token_by_u_id,
    validate_password_chars,
)
from action import (
    convert_email_to_uid,
    generate_token,
    generate_handle_str,
)
from error import InputError


def auth_login(email, password):
    """Given a registered users' email and password and generates a valid token
    for the user to remain authenticated

    Args:
        email (string): [description]
        password (string): [description]

    Returns:
        (dict): { u_id, token }
    """
    # input handling
    # converting email to be all lowercase
    email = email.lower()

    u_id = convert_email_to_uid(email)
    token = generate_token(email)
    if not validate_create_email(email):
        raise InputError("Invalid Email.")
    if u_id == -1:
        raise InputError("Email is not registered")
    if validate_token_by_u_id(u_id):
        raise InputError("User is already logged in.")
    if not validate_password_length(password):
        raise InputError("Invalid password input.")
    if not validate_password_chars(password):
        raise InputError("Invalid characters entered.")
    if not validate_password(password):
        raise InputError("Incorrect password.")

    # adding to database
    new_login = {}
    new_login['u_id'] = u_id
    new_login['token'] = token
    data['active_users'].append(new_login)

    return {
        'u_id': new_login['u_id'],
        'token': new_login['token'],
    }

def auth_logout(token):
    """Given an active token, invalidates the token to log the user out. If a
    valid token is given, and the user is successfully logged out, it returns
    true, otherwise false.

    Args:
        token (string): unique identifier for user

    Returns:
        (dict): { is_success }
    """
    for user in data['active_users']:
        if user['token'] == token:
            data['active_users'].remove(user)
            return {
                'is_success': True,
            }
    return {
        'is_success': False,
    }

def auth_register(email, password, name_first, name_last):
    """Given a user's first and last name, email address, and password, create
    a new account for them and return a new token for authentication in their
    session. A handle is generated that is the concatentation of a lowercase-only
    first name and last name. If the concatenation is longer than 20 characters,
    it is cutoff at 20 characters. If the handle is already taken, you may modify
    the handle in any way you see fit to make it unique.

    Args:
        email (string)
        password (string)
        name_first (string)
        name_last (string)

    Returns:
        (dict): { u_id, token }
    """
    # error handling
    # converting email to be all lowercase
    email = email.lower()
    if not validate_create_email(email):
        raise InputError("Invalid email.")
    u_id = convert_email_to_uid(email)
    if not u_id == -1:
        raise InputError("A user with that email already exists.")
    # error handling password
    if not validate_password_length(password) or not validate_password_chars(password):
        raise InputError("Invalid characters. Between 6 - 128 characters (inclusive).")
    # error handling names
    if not validate_names(name_first) or not validate_names(name_last):
        raise InputError("First/Last name should be between 1 - 50 characters (inclusive).")
    if not validate_names_characters(name_first) or not validate_names_characters(name_last):
        raise InputError("Please include only alphabets, hyphens and whitespaces.")

    # Generating handle strings (concatinating first and last name)
    hstring = generate_handle_str(name_first, name_last)
    assert len(hstring) <= 20
    # registering user in data
    new_user = {
        'u_id': len(data['users']) + 1,
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last,
        'handle_str': hstring,
        'channels': [],
    }
    # assigning flockr owner
    is_owner = MEMBER
    if new_user['u_id'] == 1:
        is_owner = OWNER
        data["total_messages"] = 0
    new_user["permission_id"] = is_owner
    data["first_owner_u_id"] = 1
    data['users'].append(new_user)
    # in the first iteration, the token is just the email
    token = generate_token(email)
    # when registering, automatically log user in.
    new_login = {}
    new_login['u_id'] = new_user['u_id']
    new_login['token'] = token

    data['active_users'].append(new_login)

    return {
        'u_id': new_login['u_id'],
        'token': new_login['token'],
    }
