"""
standup feature test implementation to test functions in message.py

2020 T3 COMP1531 Major Project
"""
from datetime import timezone, datetime
import time
import requests

from src.feature.error import InputError, AccessError
from src.helpers.helpers_http_test import (
    request_standup_start, 
    request_standup_active, 
    request_standup_send, 
    request_channel_invite,
    request_channel_messages,
)
from src.globals import STANDUP_DELAY

#------------------------------------------------------------------------------#
#                               standup_start                                  #
#------------------------------------------------------------------------------#

#?------------------------ Input/Access Error Testing ------------------------?#

def test_standup_start_expired_token(url, user_1, user_2, user_3, user_4, public_channel_1):
    """Testing expired token for users which have logged out
    """
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_1['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_2['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_3['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_4['token']}).json()
    assert log_out['is_success']

    error = request_standup_start(url, user_1['token'], public_channel_1['channel_id'], 10)
    assert error.status_code == AccessError.code
    error = request_standup_start(url, user_2['token'], public_channel_1['channel_id'], 10)
    assert error.status_code == AccessError.code
    error = request_standup_start(url, user_3['token'], public_channel_1['channel_id'], 10)
    assert error.status_code == AccessError.code
    error = request_standup_start(url, user_4['token'], public_channel_1['channel_id'], 10)
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_standup_start_invalid_token(url, user_2, user_3, user_4, public_channel_1):
    """Testing invalid token for users
    """
    error = request_standup_start(url, user_2['token'], public_channel_1['channel_id'], 10)
    assert error.status_code == AccessError.code
    error = request_standup_start(url, user_3['token'], public_channel_1['channel_id'], 10)
    assert error.status_code == AccessError.code
    error = request_standup_start(url, user_4['token'], public_channel_1['channel_id'], 10)
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_standup_start_invalid_channel(url, user_2, public_channel_1):
    """Testing invalid channel_ids
    """
    error = request_standup_start(url, user_2['token'], 0, 10)
    assert error.status_code == InputError.code
    error = request_standup_start(url, user_2['token'], -1, 10)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_standup_start_invalid_length(url, user_1, user_2, public_channel_1):
    """Testing invalid time length
    """
    error = request_standup_start(url, user_1['token'], public_channel_1['channel_id'], -10)
    assert error.status_code == InputError.code
    error = request_standup_start(url, user_1['token'], public_channel_1['channel_id'], 0)
    assert error.status_code == InputError.code
    error = request_standup_start(url, user_2['token'], public_channel_1['channel_id'], -40)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_standup_start_already_started(url, user_1, public_channel_1):
    """Testing when a standup is already running in channel 
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = request_standup_start(url, user_1['token'], public_channel_1['channel_id'], 120).json()
    assert information['time_finish'] == curr_time + 120

    error = request_standup_start(url, user_1['token'], public_channel_1['channel_id'], 5)
    assert error.status_code == InputError.code
    error = request_standup_start(url, user_1['token'], public_channel_1['channel_id'], 50)
    assert error.status_code == InputError.code
    error = request_standup_start(url, user_1['token'], public_channel_1['channel_id'], 120)
    assert error.status_code == InputError.code
    error = request_standup_start(url, user_1['token'], public_channel_1['channel_id'], 240)
    assert error.status_code == InputError.code
    error = request_standup_start(url, user_1['token'], public_channel_1['channel_id'], 360)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_standup_start_unauthorized_user(url, user_1, user_2, user_3, public_channel_1):
    """(Assumption testing) Testing when a user who is not part of the channel
       tries to start a standup
    """
    standup_duration = 2
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = request_standup_start(url, user_1['token'], public_channel_1['channel_id'], standup_duration).json()
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    information = request_standup_active(url, user_1['token'], public_channel_1['channel_id']).json()
    assert information['is_active']
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    error = request_standup_start(url, user_2['token'], public_channel_1['channel_id'], 2)
    assert error.status_code == AccessError.code
    error = request_standup_start(url, user_3['token'], public_channel_1['channel_id'], 2)
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')


#?------------------------------ Output Testing ------------------------------?#

def test_standup_start_working_example(url, user_1, user_2, user_3, public_channel_1):
    """Testing when standup is working, via message collation
    """
    assert request_channel_invite(url, user_1['token'], public_channel_1['channel_id'], user_2['u_id']).json() == {}
    assert request_channel_invite(url, user_2['token'], public_channel_1['channel_id'], user_3['u_id']).json() == {}

    standup_duration = 2
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = request_standup_start(url, user_1['token'], public_channel_1['channel_id'], standup_duration).json()
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish']
    assert information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    payload = request_standup_active(url, user_1['token'], public_channel_1['channel_id']).json()
    assert payload['is_active'] == True

    on_list = False
    assert request_standup_send(url, user_1['token'], public_channel_1['channel_id'], 'Hey guys!').json() == {}
    message_data = request_channel_messages(url, user_1['token'], public_channel_1['channel_id'], 0).json()
    for messages in message_data['messages']:
        if messages['message'] == 'John: Hey guys!':
            on_list = True
    assert not on_list

    on_list = False
    assert request_standup_send(url, user_2['token'], public_channel_1['channel_id'], 'Its working!').json() == {}
    message_data = request_channel_messages(url, user_1['token'], public_channel_1['channel_id'], 0).json()
    for messages in message_data['messages']:
        if messages['message'] == 'John: Hey guys!\n Jane: Its working!':
            on_list = True
    assert not on_list

    assert request_standup_send(url, user_3['token'], public_channel_1['channel_id'], 'Wohoo!').json() == {}
    payload = request_standup_active(url, user_1['token'], public_channel_1['channel_id']).json()
    assert payload['is_active'] == True

    time.sleep(4)
    payload = request_standup_active(url, user_1['token'], public_channel_1['channel_id']).json()
    assert payload['is_active'] == False

    on_list = False
    message_data = request_channel_messages(url, user_1['token'], public_channel_1['channel_id'], 0).json()
    for messages in message_data['messages']:
        print(messages['message'])
        if messages['message'] == 'John: Hey guys!\nJane: Its working!\nJace: Wohoo!':
            on_list = True
    assert on_list
    requests.delete(f'{url}/clear')

#------------------------------------------------------------------------------#
#                               standup_active                                 #
#------------------------------------------------------------------------------#

#?------------------------ Input/Access Error Testing ------------------------?#

def test_standup_active_expired_token(url, user_1, user_2, user_3, user_4, public_channel_1):
    """Testing invalid token for users which have logged out
    """
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_1['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_2['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_3['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_4['token']}).json()
    assert log_out['is_success']

    error = request_standup_active(url, user_1['token'], public_channel_1['channel_id'])
    assert error.status_code == AccessError.code
    error = request_standup_active(url, user_2['token'], public_channel_1['channel_id'])
    assert error.status_code == AccessError.code
    error = request_standup_active(url, user_3['token'], public_channel_1['channel_id'])
    assert error.status_code == AccessError.code
    error = request_standup_active(url, user_4['token'], public_channel_1['channel_id'])
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_standup_active_invalid_token(url, user_2, public_channel_1):
    """Testing invalid token for users
    """
    error = request_standup_active(url, user_2['token'], public_channel_1['channel_id'])
    assert error.status_code == AccessError.code
    error = request_standup_active(url, user_2['token'], public_channel_1['channel_id'])
    assert error.status_code == AccessError.code
    error = request_standup_active(url, user_2['token'], public_channel_1['channel_id'])
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_standup_active_invalid_channel(url, user_2, public_channel_1):
    """Testing invalid channel_ids
    """
    error = request_standup_active(url, user_2['token'], public_channel_1['channel_id'])
    assert error.status_code == InputError.code
    error = request_standup_active(url, user_2['token'], public_channel_1['channel_id'])
    assert error.status_code == InputError.code
    error = request_standup_active(url, user_2['token'], public_channel_1['channel_id'])
    assert error.status_code == InputError.code
    error = request_standup_active(url, user_2['token'], public_channel_1['channel_id'])
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_standup_active_unauthorized_user(url, user_1, user_2, user_3, public_channel_1):
    """(Assumption testing) Testing when a user who is not part of the channel
       tries to see if a standup is active in that channel
    """
    standup_duration = 2
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = request_standup_start(url, user_1['token'], public_channel_1['channel_id'], standup_duration).json()
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    information = request_standup_active(url, user_1['token'], public_channel_1['channel_id']).json()
    assert information['is_active']
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    error = request_standup_active(url, user_2['token'], public_channel_1['channel_id'])
    assert error.status_code == AccessError.code
    error = request_standup_active(url, user_3['token'], public_channel_1['channel_id'])
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_standup_active_is_active(url, user_1, user_2, user_3, public_channel_1):
    """Testing when standup is active
    """
    assert request_channel_invite(url, user_1['token'], public_channel_1['channel_id'], user_2['u_id']).json() == {}
    assert request_channel_invite(url, user_2['token'], public_channel_1['channel_id'], user_3['u_id']).json() == {}

    standup_duration = 2
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = request_standup_start(url, user_1['token'], public_channel_1['channel_id'], standup_duration).json()
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    information = request_standup_active(url, user_1['token'], public_channel_1['channel_id']).json()
    assert information['is_active']
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    information = request_standup_active(url, user_2['token'], public_channel_1['channel_id']).json()
    assert information['is_active']
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY) 

    information = request_standup_active(url, user_3['token'], public_channel_1['channel_id']).json()
    assert information['is_active']
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY) 
    requests.delete(f'{url}/clear')

def test_standup_active_not_active(url, user_1, user_2, user_3, public_channel_1):
    """Testing when standup is not active
    """
    assert request_channel_invite(url, user_1['token'], public_channel_1['channel_id'], user_2['u_id']).json() == {}
    assert request_channel_invite(url, user_2['token'], public_channel_1['channel_id'], user_3['u_id']).json() == {}

    standup_duration = 2
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = request_standup_start(url, user_1['token'], public_channel_1['channel_id'], standup_duration).json()
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)
    time.sleep(4)

    information = request_standup_active(url, user_1['token'], public_channel_1['channel_id']).json()
    assert not information['is_active']
    assert information['time_finish'] == None

    information = request_standup_active(url, user_2['token'], public_channel_1['channel_id']).json()
    assert not information['is_active']
    assert information['time_finish'] == None 

    information = request_standup_active(url, user_3['token'], public_channel_1['channel_id']).json()
    assert not information['is_active']
    assert information['time_finish'] == None
    requests.delete(f'{url}/clear')

#------------------------------------------------------------------------------#
#                                standup_send                                  #
#------------------------------------------------------------------------------#

#?------------------------ Input/Access Error Testing ------------------------?#

def test_standup_send_expired_token(url, user_1, user_2, user_3, user_4, public_channel_1):
    """Testing expired token for users which have logged out
    """
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_1['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_2['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_3['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_4['token']}).json()
    assert log_out['is_success']

    error = request_standup_send(url, user_1['token'], public_channel_1['channel_id'], 'Hey')
    assert error.status_code == AccessError.code
    error = request_standup_send(url, user_2['token'], public_channel_1['channel_id'], 'Hey')
    assert error.status_code == AccessError.code
    error = request_standup_send(url, user_3['token'], public_channel_1['channel_id'], 'Hey')
    assert error.status_code == AccessError.code
    error = request_standup_send(url, user_4['token'], public_channel_1['channel_id'], 'Hey')
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_standup_send_invalid_token(url, user_2, user_3, user_4, public_channel_1):
    """Testing invalid token for users
    """
    error = request_standup_send(url, user_2['token'], public_channel_1['channel_id'], 'Hey')
    assert error.status_code == AccessError.code
    error = request_standup_send(url, user_3['token'], public_channel_1['channel_id'], 'Hey')
    assert error.status_code == AccessError.code
    error = request_standup_send(url, user_4['token'], public_channel_1['channel_id'], 'Hey')
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_standup_send_invalid_channel(url, user_1, user_2):
    """Testing invalid channel_ids
    """
    error = request_standup_send(url, user_1['token'], -1, 'Hey')
    assert error.status_code == InputError.code
    error = request_standup_send(url, user_1['token'], 0, 'Hey')
    assert error.status_code == InputError.code
    error = request_standup_send(url, user_2['token'], -10, 'Hey')
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_standup_send_invalid_message(url, user_1, user_2, user_3, public_channel_1):
    """Testing when message is invalid type
    """
    error = request_standup_send(url, user_1['token'], public_channel_1['channel_id'], 0)
    assert error.status_code == InputError.code
    error = request_standup_send(url, user_2['token'], public_channel_1['channel_id'], -10)
    assert error.status_code == InputError.code
    error = request_standup_send(url, user_3['token'], public_channel_1['channel_id'], 43.333)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_standup_send_more_than_1000_char(url, user_1, public_channel_1):
    """Testing when the message to send via standup send is over 1000 characters
    """
    message_str_1 = ("Hello" * 250)
    message_str_2 = ("HI " * 500)
    message_str_3 = ("My name is blah" * 100)

    standup_duration = 2
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = request_standup_start(url, user_1['token'], public_channel_1['channel_id'], standup_duration).json()
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    error = request_standup_send(url, user_1['token'], public_channel_1['channel_id'], message_str_1)
    assert error.status_code == InputError.code
    error = request_standup_send(url, user_1['token'], public_channel_1['channel_id'], message_str_2)
    assert error.status_code == InputError.code
    error = request_standup_send(url, user_1['token'], public_channel_1['channel_id'], message_str_3)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_standup_send_no_standup(url, user_1, user_2, user_3, public_channel_1):
    """Testing when no standup is currently running in channel specified
    """
    assert request_channel_invite(url, user_1['token'], public_channel_1['channel_id'], user_2['u_id']).json() == {}
    assert request_channel_invite(url, user_2['token'], public_channel_1['channel_id'], user_3['u_id']).json() == {}

    error = request_standup_send(url, user_1['token'], public_channel_1['channel_id'], 'Hey')
    assert error.status_code == InputError.code
    error = request_standup_send(url, user_2['token'], public_channel_1['channel_id'], 'Hey')
    assert error.status_code == InputError.code
    error = request_standup_send(url, user_3['token'], public_channel_1['channel_id'], 'Hey')
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_standup_send_unauthorized_user(url, user_1, user_2, user_3, public_channel_1):
    """Testing when a user who is not part of the channel tries to send a standup to
       that channel
    """
    standup_duration = 2
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = request_standup_start(url, user_1['token'], public_channel_1['channel_id'], standup_duration).json()
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    information = request_standup_active(url, user_1['token'], public_channel_1['channel_id']).json()
    assert information['is_active']
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    error = request_standup_send(url, user_2['token'], public_channel_1['channel_id'], 'Hey')
    assert error.status_code == AccessError.code
    error = request_standup_send(url, user_3['token'], public_channel_1['channel_id'], 'Hey')
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_standup_send_working_example(url, user_1, user_2, user_3, public_channel_1):
    """Testing when standup send is working, via message collation
    """
    assert request_channel_invite(url, user_1['token'], public_channel_1['channel_id'], user_2['u_id']).json() == {}
    assert request_channel_invite(url, user_2['token'], public_channel_1['channel_id'], user_3['u_id']).json() == {}

    standup_duration = 2
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = request_standup_start(url, user_1['token'], public_channel_1['channel_id'], standup_duration).json()
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    on_list = False
    assert request_standup_send(url, user_1['token'], public_channel_1['channel_id'], 'Pizza!').json() == {}
    message_data = request_channel_messages(url, user_1['token'], public_channel_1['channel_id'], 0).json()
    for messages in message_data['messages']:
        if messages['message'] == 'John: Pizza!':
            on_list = True
    assert not on_list
    
    assert request_standup_send(url, user_2['token'], public_channel_1['channel_id'], 'Water!').json() == {}
    assert request_standup_send(url, user_3['token'], public_channel_1['channel_id'], 'Melon!').json() == {}
    time.sleep(4)

    on_list = False
    message_data = request_channel_messages(url, user_1['token'], public_channel_1['channel_id'], 0).json()
    for messages in message_data['messages']:
        if messages['message'] == 'John: Pizza!\nJane: Water!\nJace: Melon!':
            on_list = True
    assert on_list
    requests.delete(f'{url}/clear')
