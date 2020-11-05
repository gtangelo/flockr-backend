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

def helper_channel_invite(url, user_1, user_2, channel):
    """Invites user_2 to channel which user_1 is in

    Args:
        url (string)
        user_1 (dict): { u_id, token }
        user_2 (dict): { u_id, token }
        channel (dict)
    """
    return requests.post(f'{url}channel/invite', json={
        'token'     : user_1['token'],
        'channel_id': channel['channel_id'],
        'u_id'      : user_2['u_id'],
    })

def helper_channel_messages(url, user, channel, index):
    """Returns messages from specified order of index

    Args:
        url (string)
        user (dict): { u_id, token }
        channel (dict)
        index (int)
    """
    return requests.get(f'{url}channel/messages', params={
        'token'     : user['token'],
        'channel_id': channel['channel_id'],
        'start'     : index,
    })

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

def send_message_later(url, user, channel, message, time_sent):
    """Sends a request to /message/send to send a message to a channel

    Args:
        url (string)
        user (dict): { u_id, token }
        channel (dict)
        message (string)
        time_sent (int)

    Returns:
        (response): payload of request
    """
    return requests.post(url + 'message/sendlater', json={
        'token'     : user['token'],
        'channel_id': channel['channel_id'],
        'message'   : message,
        'time_sent' : time_sent,
    })

def helper_standup_start(url, user, channel, length):
    """Sends a request to /standup/start to start standup

    Args:
        url (string)
        user (dict): { u_id, token }
        channel (dict)
        message (str)

    Returns:
        (dict): { time_finish }
    """
    return requests.post(f'{url}standup/start', json={
        'token'     : user['token'],
        'channel_id': channel['channel_id'],
        'length'    : length,
    })

def helper_standup_active(url, user, channel):
    """Checks if standup is active or not

    Args:
        url (string)
        user (dict): { u_id, token }
        channel (dict)

    Returns:
        (dict): { 'is_active', 'time_finish' }
    """
    return requests.get(f'{url}standup/active', params={
        'token'     : user['token'],
        'channel_id': channel['channel_id'],
    })

def helper_standup_send(url, user, channel, message):
    """Send standup to channel where standup is running

    Args:
        url (string)
        user (dict): { u_id, token }
        channel (dict)
        message (string)

    Returns:
        (dict): {}
    """
    return requests.post(f'{url}standup/send', json={
        'token'     : user['token'],
        'channel_id': channel['channel_id'],
        'message'   : message,
    })

def helper_message_pin(url, user, message_id):
    """Given a message within a channel, mark it as "pinned" to be given 
    special display treatment by the frontend

    Args:
        token (string)
        message_id (int)

    Returns:
        (dict)
    """
    return requests.post(f"{url}/message/pin", json={
        'token': user['token'],
        'message_id': message_id,
    })

def helper_message_unpin(url, user, message_id):
    """Given a message within a channel, remove it's mark as unpinned

    Args:
        token (string)
        message_id (int)

    Returns:
        (dict)
    """
    return requests.post(f"{url}/message/unpin", json={
        'token': user['token'],
        'message_id': message_id,
    })
