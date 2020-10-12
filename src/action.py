"""
File containing helper functions that ease proccess in some feature functions.
These functions often perform certain action to extract/store information from
the database.

Implementation was done by entire group.

2020 T3 COMP1531 Major Project
"""

from data import data

def generate_token(email):
    """Generates a unique token identifier

    Args:
        email (string): email address of user

    Returns:
        (string): token identifier
    """
    no_tok = 'invalid_tok'
    for user in data['users']:
        if user['email'] == email:
            return email
    return no_tok

def convert_token_to_user(token):
    """Returns the user details based on the given token

    Args:
        token (int): unique identifier for authorised user

    Returns:
        (dict): {u_id, email, name_first, name_last, handle_str}
                dictionary containing user details
    """
    user_details = {}
    for user in data['active_users']:
        if user['token'] == token:
            user_details = user
            break
    for user in data['users']:
        if user['u_id'] == user_details['u_id']:
            user_details = user
            break
    return user_details

def convert_user_to_token(u_id):
    """Returns the token of a user, given the u_id

    Args:
        u_id (int): u_id of user

    Returns:
        token (string): unique token identifier
    """
    user_details = {}
    user_details['token'] = ''
    for user in data['active_users']:
        if user['u_id'] == u_id:
            user_details['token'] = user['token']
            break
    return user_details['token']

def get_details_from_u_id(u_id):
    """Return user details for corressponding u_id

    Args:
        u_id (int): u_id of user

    Returns:
        (dict): {u_id, email, password, name_first, name_last, handle_str,
                    channels, is_flockr_owner}
                details containing user information
    """
    for user in data['users']:
        if user['u_id'] == u_id:
            return user
    return {}

def add_channel_to_user_list(u_id, channel):
    """Add channel information on the user list in the data structure

    Args:
        u_id (int): u_id of user
        (dict): {u_id, email, password, name_first, name_last, handle_str,
                    channels, is_flockr_owner}
                details containing user information
    """
    in_channel = False
    for user_index, user in enumerate(data['users']):
        if user['u_id'] == u_id:
            add_channel = {}
            add_channel['channel_id'] = channel['channel_id']
            add_channel['name'] = channel['name']
            add_channel['is_public'] = channel['is_public']
            for curr_channel in user['channels']:
                if curr_channel['channel_id'] == channel['channel_id']:
                    in_channel = True
                    break
            if in_channel:
                data['users'][user_index]['channels'].append(add_channel)
            return

def get_lowest_u_id_user_in_channel(channel):
    """Return information of user in the channel with the lowest u_id

    Args:
        channel (dict): details containing about the channel
            {channel_id, name, messages, all_members, owner_members, is_public}

    Returns:
        (dict): {u_id, email, password, name_first, name_last, handle_str,
                    channels, is_flockr_owner}
                details containing user information. Return `None` if there
                are no members
    """
    if len(channel['all_members']) > 0:
        lowest_u_id_user = channel['all_members'][0]
        for user in channel['all_members']:
            if lowest_u_id_user['u_id'] > user['u_id']:
                lowest_u_id_user = user
        return lowest_u_id_user
    return None

def remove_channel_in_user_list(u_id, channel_id):
    """Remove user with u_id in the channel within the database

    Args:
        u_id (int): u_id of user
        channel_id (int): channel_id of channel

    Output:
        Deletes user info with u_id in the channel data with channel_id.
    """
    for user_index, user in enumerate(data['users']):
        if user['u_id'] == u_id:
            for curr_channel in user['channels']:
                if curr_channel['channel_id'] == channel_id:
                    data['users'][user_index]['channels'].remove(curr_channel)

def convert_email_to_uid(email):
    """Returns the token of a user, given the u_id, also checks if the user is
    registered

    Args:
        email (int): email address of user

    Returns:
        u_id (int): corressponding u_id of email address
    """
    user_details = {}
    user_details['u_id'] = -1
    for user in data['users']:
        if user['email'] == email:
            user_details['u_id'] = user['u_id']
            break
    return user_details['u_id']

def generate_handle_str(name_first, name_last):
    ''' Generates a basic handle string given a users first and last name

    Args:
        name_first (str): first name of user
        name_last (str): last name of user

    Returns:
        handle_str (str): concat version of first and last name
    '''
    first_name_concat = name_first[0:1].lower()
    if len(name_last) > 17:
        last_name_concat = name_last[0:17].lower()
    else:
        last_name_concat = name_last.lower()
    hstring = first_name_concat + last_name_concat
    count = 0
    for user in data['users']:
        if user['handle_str'].startswith(hstring):
            count += 1
    hstring += str(count)
    return hstring
