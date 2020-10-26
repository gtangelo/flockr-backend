"""
Helper functions to test http_tests.

2020 T3 COMP1531 Major Project
"""

import requests
from datetime import datetime, timezone

def register_default_user(url, name_first, name_last):
    """Sends a auth/register request based on the parameters received to create
    a user 

    Args:
        url (string)
        name_first (string)
        name_last (string)

    Returns:
        (response): payload of request
    """
    email = f'{name_first.lower()}{name_last.lower()}@gmail.com'
    data = {
        'email': email,
        'password': 'password',
        'name_first': name_first,
        'name_last': name_last
    }
    payload = requests.post(f'{url}auth/register', json=data)
    return payload.json()

def create_messages(url, user, channel_id, i, j):
    """Sends n messages using the /message/send request to the channel with 
    channel_id in channel_data

    Args:
        url (string)
        user (dict): { u_id, token }
        channel_id (int)
        i (int): start value
        j (int): end value

    Returns:
        (list of messages)
    """
    result = []
    for index in range(i, j):
        time = int(datetime.now().replace(tzinfo=timezone.utc).timestamp())
        message_info = requests.post(url + '/message/send', json={
            'token': user['token'],
            'channel_id': channel_id,
            'message': f'{index}'
        }).json()
        result.insert(0, {
            'message_id': message_info['message_id'],
            'u_id': user['u_id'],
            'message': f"{index}",
            'time_created': time,
        })
    return result


def send_message(url, user, channel, message):
    """Sends a request to /message/send to send a message to a channel

    Args:
        url (string)
        user (dict): { u_id, token }
        channel (dict)
        message (string)

    Returns:
        (response): payload of request
    """
    return requests.post(url + 'message/send', json={
        'token'     : user['token'],
        'channel_id': channel['channel_id'],
        'message'   : message,
    })