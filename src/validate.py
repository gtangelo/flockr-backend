from data import data
import re

#used for validating an email

'''
Returns whether or not channel_id is a valid channel id.

    Parameters:
        channel_id (int): channel id

    Returns:
        (bool, dict): whether channel_id is a valid channel id in the data. 
            - If valid, returns True and 'channel_data' which stores all relevant
            information in a dictionary belonging to the channel with the 
            'channel_id'
            - Otherwise, returns False
'''
def validate_channel_id(channel_id):
    for channel in data['channels']:
        if channel_id == channel['id']:
            channel_data = channel
            return True, channel_data
    return False

'''
Determines whether or not the user has been authorised.

    Parameters:
        token (int): unique identifier for authorised user

    Returns:
        (bool): whether the token is valid
'''

def user_is_authorise(token):
    for user in data['active_users']:
        if user['token'] == token:
            return True
    return False
    
def user_is_authorise_u_id(u_id):
    for user in data['active_users']:
        if user['u_id'] == u_id:
            return True
        return False

'''
Returns the user details based on the given token

    Parameters:
        token (int): unique identifier for authorised user

    Returns:
        (dict): dictionary containing user details
'''
def convert_token_to_user(token):
    user_details = {}
    for user in data['active_users']:
        if user['token'] == token:
            user_details = user
            break
    return user_details

'''
Returns the token of a user, given the u_id
    Parameters:
        u_id (int)
    
    Returns:
        token
'''
def convert_user_to_token(u_id):
    user_details = {}
    user_details['token'] = ''
    for user in data['active_users']:
        if user['u_id'] == u_id:
            user_details['token'] = user['token']
            break
    return user_details['token']

'''
Returns the token of a user, given the u_id, also checks if the user is registered
    Parameters:
        u_id (int)
    
    Returns:
        token
'''

def convert_email_to_uid(email):
    user_details = {}
    user_details['u_id'] = -1
    for user in data['users']:
        if user['email'] == email:
            user_details['u_id'] = user['u_id']
            break
    return user_details['u_id']


'''
Returns whether or not the user is a member of a channel.

    Parameters:
        token (int): unique identifier for authorised user
        channel_data (dict): channel information

    Returns:
        (bool): whether the token is found within 'channel_data'
'''

def validate_user_in_channel(token, channel_data):
    if user_is_authorise(token):
        user_details = convert_token_to_user(token)
        for user in channel_data['members']:
            if user['id'] == user_details['id']:
                return True
    
    return False



'''
Returns wheter the email is valid or not, does
    Parameters:
        email (string): should follow regex syntax, have characters <= 320 && >= 3
    Returns:
        (bool): if valid, true, otherwise false.
'''

def validate_create_email(email):
    if (len(email) <= 320 and len(email) >= 3):
        if (re.search(r'[\w.-]+@[\w.-]+.\w+',email)):
            return True
    return False

'''
Returns wheter the password is valid or not
    Parameters:
        password (string): should be be atleast 6 chars but not greater than 128 chars

    Returns:
        (bool): if valid, true, otherwise false.
'''

def validate_password_length(password):
    if (len(password) < 6 or len(password) > 128):
        return False
    return True

'''
Returns wheter the password is valid or not
    Parameters:
        password (string): 
        checks if characters inputted are valid 

    Returns:
        (bool): if valid, true, otherwise false.
'''
def validate_password_chars(password):
    valid_chars_password = '^[!-~]+$'
    if (re.search(valid_chars_password, password)):
        return True
    
'''
Returns wheter either the first or last name is valid or not
    Parameters:
        name_first or name_last (string): should be >= 1 && <= 50
    
    Returns:
        (bool): if valid, true, otherwise false.
'''

def validate_names(name):
    
    if (len(name) < 1 or len(name) > 50):
        return False
    return True

'''
Returns wheter the name contains only letters and '-' and ' ' 
    Parameters:
        name_first or name_last
    Returns:
        (bool): if valid, true, otherwise false.
'''

def validate_names_characters(name):
    valid_chars_name = '^[A-Za-z- ]+$'
    if (re.search(valid_chars_name, name)):
        return True
    return False

'''
Returns wheter the user is already logged in or not
    Parameters:
        token: verifies if the user is logged in
    Returns:
        (bool): if valid, true, otherwise false.
'''
def validate_logged_in(token):
    for user in data['active_users']:
        if user['token'] == token:
            return True 
    return False

'''
Confirms if the password inputted is correct for a given user.
    Parameters:
        password (str)
    Returns:
        (bool): if valid, true, otherwise false.
'''
def validate_password(password):
    for user in data['users']:
        if user['password'] == password:
            return True
    return False

def generate_token(email):
    no_tok = 'invalid_tok'
    for user in data['users']:
        if user['email'] == email:
            return email
    return no_tok




