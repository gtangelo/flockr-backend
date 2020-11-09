"""
File containing helper functions that ease proccess in some feature functions.
These functions often perform certain action to extract/store information from
the database.

2020 T3 COMP1531 Major Project
"""
import time
import jwt
import pickle

from src.globals import DATA_FILE, NON_EXIST, SECRET

def generate_token(data, email):
    """Generates a unique token identifier

    Args:
        email (string): email address of user

    Returns:
        (string): token identifier
    """
    for user in data.get_users():
        if user['email'] == email:
            encoded_jwt = jwt.encode({'email': user['email']}, SECRET, algorithm='HS256')
            return str(encoded_jwt)
    return 'invalid_token'

def convert_token_to_u_id(data, token):
    """Returns the corressponding u_id for the given token

    Args:
        token (string)

    Returns:
        (int): user u_id for the token
    """
    tokens_list = data.get_active_tokens()
    if token in tokens_list:
        user = data.get_active_user_details(token)
        return user['u_id']
    return NON_EXIST

def convert_email_to_u_id(data, email):
    """Returns the u_id of a user, given the token.

    Args:
        email (str): email address of user

    Returns:
        u_id (int): corressponding u_id of email address
    """
    u_id = NON_EXIST
    for user in data.get_users():
        if user['email'] == email:
            u_id = user['u_id']
    return u_id

def generate_handle_str(data, name_first, name_last):
    ''' Generates a basic handle string given a users first and last name

    Args:
        name_first (str): first name of user
        name_last (str): last name of user

    Returns:
        handle_str (str): concat version of first and last name
    '''
    first_name_concat = name_first[0:1].lower()
    if len(name_last) >= 17:
        last_name_concat = name_last[0:17].lower()
    else:
        last_name_concat = name_last.lower()
    hstring = first_name_concat + last_name_concat
    count = 0
    for user in data.get_users():
        if user['handle_str'].startswith(hstring):
            count += 1
    hstring += str(count)
    return hstring

def token_to_handle_name(data, token):
    """For the given token, return the user's handle string

    Args:
        token (string)
    """
    u_id = convert_token_to_u_id(data, token)
    for user in data.get_users():
        if user['u_id'] == u_id:
            return user['handle_str']

def set_standup_inactive(token, channel_id, length):
    """Set standup in a channel as inactive after specified length of time
       then sends the 'standup_messages' to channel

    Args:
        channel_id (int): channel with channel_id specified
        length (int): number of seconds till inactivation
    """
    time.sleep(length)
    
    data = pickle.load(open(DATA_FILE, "rb"))
    standup_messages_all = data.show_standup_messages(channel_id)
    if standup_messages_all != "":
        message_id = data.generate_message_id()
        u_id = convert_token_to_u_id(data, token)
        data.create_message(u_id, channel_id, message_id, standup_messages_all)
    data.set_standup_inactive_in_channel(channel_id)
    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)


def get_messages_list(data, token, channel_id):
    """Retrieves the information of the messages within the channel with
    channel_id

    Args:
        token (string)
        channel_id (int)
    
    Returns:
        messages_list (dict): { message_id, u_id, message, time_created, reacts, is_pinned  }
    """
    channel_details = data.get_channel_details(channel_id)
    u_id = convert_token_to_u_id(data, token)
    messages_list = []
    for message in channel_details['messages']:
        user_reacted_thumbs_up = u_id in message['reacts'][0]['u_ids']
        user_reacted_thumbs_down = u_id in message['reacts'][1]['u_ids']
        user_reacted_love_react = u_id in message['reacts'][2]['u_ids']
        messages_list.append({
            'message_id'    : message['message_id'], 
            'u_id'          : message['u_id'], 
            'message'       : message['message'], 
            'time_created'  : message['time_created'], 
            'is_pinned'     : message['is_pinned'],
            'reacts': [
                {
                    # Thumbs up react - react_id = 1
                    'react_id': message['reacts'][0]['react_id'],
                    'u_ids': message['reacts'][0]['u_ids'],
                    'is_this_user_reacted': user_reacted_thumbs_up,
                },
                {
                    # Thumbs down react - react_id = 2
                    'react_id': message['reacts'][1]['react_id'],
                    'u_ids': message['reacts'][1]['u_ids'],
                    'is_this_user_reacted': user_reacted_thumbs_down,
                },
                {
                    # Love react - react_id = 3
                    'react_id': message['reacts'][2]['react_id'],
                    'u_ids': message['reacts'][2]['u_ids'],
                    'is_this_user_reacted': user_reacted_love_react,
                }
            ],
        })
    return messages_list

def find_message_id_in_channel(data, message_id):
    """Returns the channel_id where the message_id is found 

    Args:
        message_id (int)

    Returns:
        (int): channel_id where message_id was found
    """
    for channel in data.get_channels():
        for message in channel['messages']:
            if message['message_id'] == message_id:
                return channel['channel_id']
    return NON_EXIST