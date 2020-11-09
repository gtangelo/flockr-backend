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
        time = int(datetime.now(tz=timezone.utc).timestamp())
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

def request_channels_create(url, token, name, is_public):
    return requests.post(f'{url}channel/invite', json={
        'token'     : token,
        'name'      : name,
        'is_public' : is_public,
    })

def request_channel_invite(url, token, channel_id, u_id):
    return requests.post(f'{url}channel/invite', json={
        'token'     : token,
        'channel_id': channel_id,
        'u_id'      : u_id,
    })

def request_channel_messages(url, token, channel_id, start):
    return requests.get(f'{url}channel/messages', params={
        'token'     : token,
        'channel_id': channel_id,
        'start'     : start,
    })

def request_channel_leave(url, token, channel_id):
    return requests.post(f'{url}channel/leave', params={
        'token'     : token,
        'channel_id': channel_id,
    })

def request_standup_start(url, token, channel_id, length):
    return requests.post(f'{url}standup/start', json={
        'token'     : token,
        'channel_id': channel_id,
        'length'    : length,
    })

def request_standup_active(url, token, channel_id):
    return requests.get(f'{url}standup/active', params={
        'token'     : token,
        'channel_id': channel_id,
    })

def request_standup_send(url, token, channel_id, message):
    return requests.post(f'{url}standup/send', json={
        'token'     : token,
        'channel_id': channel_id,
        'message'   : message,
    })

def request_message_send(url, token, channel_id, message):
    return requests.post(url + 'message/send', json={
        'token'     : token,
        'channel_id': channel_id,
        'message'   : message,
    })

def request_message_sendlater(url, token, channel_id, message, time_sent):
    return requests.post(url + 'message/sendlater', json={
        'token'     : token,
        'channel_id': channel_id,
        'message'   : message,
        'time_sent' : time_sent,
    })

def request_message_react(url, token, message_id, react_id):
    return requests.post(f"{url}/message/react", json={
        'token': token,
        'message_id': message_id,
        'react_id': react_id,
    })

def request_message_unreact(url, token, message_id, react_id):
    return requests.post(f"{url}/message/unreact", json={
        'token': token,
        'message_id': message_id,
        'react_id': react_id,
    })

def request_message_pin(url, token, message_id):
    return requests.post(f"{url}/message/pin", json={
        'token': token,
        'message_id': message_id,
    })

def request_message_unpin(url, token, message_id):
    return requests.post(f"{url}/message/unpin", json={
        'token': token,
        'message_id': message_id,
    })

def request_user_details(url, token, u_id):
    return requests.get(f"{url}/user/profile", params={
        'token': token,
        'u_id': u_id,
    })
