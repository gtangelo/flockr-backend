"""
This feature covers the basic process of creating and managing users.
"""

from data import data
from validate import validate_create_email, validate_names, validate_names_characters, validate_create_password, validate_logged_in, validate_password, convert_email_to_uid, convert_token_to_user, convert_user_to_token, user_is_authorise_u_id, generate_token
from error import InputError, AccessError
def auth_login(email, password):
    if type(email) != str:
        raise InputError("Email is not of type string.")
    if type(password) != str:
        raise InputError("Password is not of type string.")

    # input handling
    # converting email to be all lowercase
    email = email.lower()

    u_id = convert_email_to_uid(email)
    token = generate_token(email)
    if not (validate_create_email(email)):
        raise InputError("Invalid Email.")
    if (u_id == -1):
        raise InputError("Email is not registered")
    if (user_is_authorise_u_id(u_id)):
        raise InputError("User is already logged in.")
    if not (validate_create_password(password)):
        raise InputError("Invalid password input.")
    if not (validate_password(password)):
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

    if not (validate_logged_in(token)):
        raise AccessError("This user is not logged in")

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
    # error handling inputs
    if type(email) != str:
        return InputError("Email is not of type string.")
    elif type(password) != str:
        return InputError("Password is not of type string.")
    elif type(name_first) != str:
        return InputError("First name is not of type string.")
    elif type(name_last) != str:
        return InputError("Last name is not of type string.")
    # error handling 
    # converting email to be all lowercase
    email = email.lower()
    if not (validate_create_email(email)):
        raise InputError("Invalid email.")
    u_id = convert_email_to_uid(email) 
    if not (u_id == -1):
        raise InputError("A user with that email already exists.")
    # error handling password
    if not (validate_create_password(password)):
        raise InputError("Invalid password, password should be between 6 - 128 characters (inclusive).")
    # error handling names
    if not (validate_names(name_first)):
        raise InputError("First name should be between 1 - 50 characters (inclusive).")
    if not (validate_names(name_last)):
        raise InputError("Last name should be between 1 - 50 characters (inclusive).")
    if not (validate_names_characters(name_first)):
        raise InputError("Please include only alphabets, hyphens and whitespaces.")

    # Generating handle strings (concatinating first and last name)
    first_name_concat = name_first[0:1].lower()
    if (len(name_last) > 19):
        last_name_concat = name_last[0:19].lower()
    else:
        last_name_concat = name_last.lower()
    hstring = first_name_concat + last_name_concat
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
    is_owner = False
    if new_user['u_id'] == 1:
        is_owner = True
    new_user["is_flockr_owner"] = is_owner
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
