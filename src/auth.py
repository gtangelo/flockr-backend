"""
This feature covers the basic process of creating and managing users.
"""

from data import data
from validate import validate_create_email, validate_names, validate_names_characters, validate_create_password, validate_user_exists, validate_logged_in, validate_user_exists, validate_password, convert_email_to_uid, convert_token_to_user, convert_user_to_token
from error import InputError, AccessError
def auth_login(email, password):
    if type(email) != str:
        raise InputError("Email is not of type string.")
    if type(password) != str:
        raise InputError("Password is not of type string.")

    u_id = convert_email_to_uid(email)
    token = convert_user_to_token(u_id)
    if (validate_logged_in(token)):
        raise InputError("Already logged in.")
    if (validate_password(password)):
        raise InputError("Incorrect password.")
    if not (validate_user_exists(email)):
        raise InputError("This email is not registered.")
    if not (validate_create_email(email)):
        raise InputError("Invalid Email.")

    login = {}
    for user in data['users']:
        if user['email'] == email:
            login = user
            break
    
    del login['channels']
    del login['password']
    login['token'] = token
    data['active_users'].append(login)

    return {
        'u_id': login['u_id'],
        'token': login['token'],
    }


    

def auth_logout(token):
    if not (validate_logged_in(token)):
        raise InputError("This user is not logged in")
    logout_user = convert_token_to_user(token)
    for user in data['active_users']:
        if user == logout_user:
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
    # error handling email
    # elif not (validate_create_email(email)):
        # raise InputError("Invalid email.")
    elif (validate_user_exists(email)):
        raise InputError("A user with that email already exists.")
    # error handling password
    elif not (validate_create_password(password)):
        raise InputError("Invalid password, password should be between 6 - 128 characters (inclusive).")
    # error handling names
    elif not (validate_names(name_first)):
        raise InputError("First name should be between 1 - 50 characters (inclusive).")
    elif not (validate_names(name_last)):
        raise InputError("Last name should be between 1 - 50 characters (inclusive).")
    elif not (validate_names_characters(name_first)):
        raise InputError("Please include only alphabets, hyphens and whitespaces.")

    # Generating handle strings (concatinating first and last name)
    first_name_concat = name_first[0:1].lower()
    if (len(name_last) > 19):
        last_name_concat = name_last[0:19].lower()
    else:
        last_name_concat = name_last.lower()
    hstring = first_name_concat + last_name_concat
    # registering user in data
    newUser = {
        'u_id': len(data['users']) + 1,
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last,
        'handle_str': hstring,
        'channels': [

        ],
    }
    is_owner = False
    if newUser['u_id'] == 1:
        is_owner == True
    newUser["is_flockr_owner"] = is_owner
    data['users'].append(newUser)
    # when registering, automatically log user in.
    del newUser['channels']
    del newUser['password']
    # need to change token generating in later iterations.
    newUser["token"] = email
    # moving new user into active users.
    data['active_users'].append(newUser)

    return {
        'u_id': newUser['u_id'],
        'token': newUser['token'],
    }
