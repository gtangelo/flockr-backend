"""
standup feature test implementation to test functions in message.py

Feature implementation was written by Prathamesh Jagtap.

2020 T3 COMP1531 Major Project
"""
from datetime import timezone, datetime
import time
import requests

from src.feature.error import InputError, AccessError
from src.helpers.helpers_http_test import *

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

    error = helper_standup_start(url, user_1, public_channel_1, 10)
    assert error.status_code == AccessError.code
    error = helper_standup_start(url, user_2, public_channel_1, 10)
    assert error.status_code == AccessError.code
    error = helper_standup_start(url, user_3, public_channel_1, 10)
    assert error.status_code == AccessError.code
    error = helper_standup_start(url, user_4, public_channel_1, 10)
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_standup_start_invalid_token(url, user_2, user_3, user_4, public_channel_1):
    """Testing invalid token for users
    """
    error = helper_standup_start(url, user_2, public_channel_1, 10)
    assert error.status_code == AccessError.code
    error = helper_standup_start(url, user_3, public_channel_1, 10)
    assert error.status_code == AccessError.code
    error = helper_standup_start(url, user_4, public_channel_1, 10)
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_standup_start_invalid_channel(url, user_2, public_channel_1):
    """Testing invalid channel_ids
    """
    error = helper_standup_start(url, user_2, {'channel_id': 0}, 10)
    assert error.status_code == InputError.code
    error = helper_standup_start(url, user_2, {'channel_id': -12}, 10)
    assert error.status_code == InputError.code
    error = helper_standup_start(url, user_2, {'channel_id': 444}, 10)
    assert error.status_code == InputError.code
    error = helper_standup_start(url, user_2, {'channel_id': -11.22}, 10)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_standup_start_invalid_length(url, user_1, user_2, public_channel_1):
    """Testing invalid time length
    """
    error = helper_standup_start(url, user_1, public_channel_1, -10)
    assert error.status_code == InputError.code
    error = helper_standup_start(url, user_1, public_channel_1, 0)
    assert error.status_code == InputError.code
    error = helper_standup_start(url, user_2, public_channel_1, -40)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_standup_start_already_started(url, user_1, public_channel_1):
    """Testing when a standup is already running in channel 
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = helper_standup_start(url, user_1, public_channel_1, 120).json()
    assert information['time_finish'] == curr_time + 120

    error = helper_standup_start(url, user_1, public_channel_1, 5)
    assert error.status_code == InputError.code
    error = helper_standup_start(url, user_1, public_channel_1, 50)
    assert error.status_code == InputError.code
    error = helper_standup_start(url, user_1, public_channel_1, 120)
    assert error.status_code == InputError.code
    error = helper_standup_start(url, user_1, public_channel_1, 240)
    assert error.status_code == InputError.code
    error = helper_standup_start(url, user_1, public_channel_1, 360)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_standup_start_unauthorized_user(url, user_1, user_2, user_3, public_channel_1):
    """(Assumption testing) Testing when a user who is not part of the channel
       tries to start a standup
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = helper_standup_start(url, user_1, public_channel_1, 2).json()
    assert information['time_finish'] == curr_time + 2

    information = helper_standup_active(url, user_1, public_channel_1).json()
    assert information['is_active']
    assert information['time_finish'] == curr_time + 2

    error = helper_standup_start(url, user_2, public_channel_1, 2)
    assert error.status_code == AccessError.code
    error = helper_standup_start(url, user_3, public_channel_1, 2)
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')


#?------------------------------ Output Testing ------------------------------?#

def test_standup_start_working_example(url, user_1, user_2, user_3, public_channel_1):
    """Testing when standup is working, via message collation
    """
    assert helper_channel_invite(url, user_1, user_2, public_channel_1).json() == {}
    assert helper_channel_invite(url, user_2, user_3, public_channel_1).json() == {}

    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = helper_standup_start(url, user_1, public_channel_1, 2).json()
    assert information['time_finish'] == curr_time + 2

    payload = helper_standup_active(url, user_1, public_channel_1).json()
    assert payload['is_active'] == True

    on_list = False
    assert helper_standup_send(url, user_1, public_channel_1, 'Hey guys!').json() == {}
    message_data = helper_channel_messages(url, user_1, public_channel_1, 0).json()
    for messages in message_data['messages']:
        if messages['message'] == 'Hey guys!':
            on_list = True
    assert not on_list

    on_list = False
    assert helper_standup_send(url, user_2, public_channel_1, 'Its working!').json() == {}
    message_data = helper_channel_messages(url, user_1, public_channel_1, 0).json()
    for messages in message_data['messages']:
        if messages['message'] == 'Its working!':
            on_list = True
    assert not on_list

    assert helper_standup_send(url, user_3, public_channel_1, 'Wohoo!').json() == {}
    payload = helper_standup_active(url, user_1, public_channel_1).json()
    assert payload['is_active'] == True

    time.sleep(4)
    payload = helper_standup_active(url, user_1, public_channel_1).json()
    assert payload['is_active'] == False

    on_list = False
    message_data = helper_channel_messages(url, user_1, public_channel_1, 0).json()
    for messages in message_data['messages']:
        if messages['message'] == 'Hey guys!':
            on_list = True
    assert on_list

    on_list = False
    for messages in message_data['messages']:
        if messages['message'] == 'Its working!':
            on_list = True
    assert on_list

    on_list = False
    for messages in message_data['messages']:
        if messages['message'] == 'Wohoo!':
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

    error = helper_standup_active(url, user_1, public_channel_1)
    assert error.status_code == AccessError.code
    error = helper_standup_active(url, user_2, public_channel_1)
    assert error.status_code == AccessError.code
    error = helper_standup_active(url, user_3, public_channel_1)
    assert error.status_code == AccessError.code
    error = helper_standup_active(url, user_4, public_channel_1)
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_standup_active_invalid_token(url, user_2, public_channel_1):
    """Testing invalid token for users
    """
    error = helper_standup_active(url, user_2, public_channel_1)
    assert error.status_code == AccessError.code
    error = helper_standup_active(url, user_2, public_channel_1)
    assert error.status_code == AccessError.code
    error = helper_standup_active(url, user_2, public_channel_1)
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_standup_active_invalid_channel(url, user_2, public_channel_1):
    """Testing invalid channel_ids
    """
    error = helper_standup_active(url, user_2, public_channel_1)
    assert error.status_code == InputError.code
    error = helper_standup_active(url, user_2, public_channel_1)
    assert error.status_code == InputError.code
    error = helper_standup_active(url, user_2, public_channel_1)
    assert error.status_code == InputError.code
    error = helper_standup_active(url, user_2, public_channel_1)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_standup_active_unauthorized_user(url, user_1, user_2, user_3, public_channel_1):
    """(Assumption testing) Testing when a user who is not part of the channel
       tries to see if a standup is active in that channel
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = helper_standup_start(url, user_1, public_channel_1, 2).json()
    assert information['time_finish'] == curr_time + 2

    information = helper_standup_active(url, user_1, public_channel_1).json()
    assert information['is_active']
    assert information['time_finish'] == curr_time + 2

    error = helper_standup_active(url, user_2, public_channel_1)
    assert error.status_code == AccessError.code
    error = helper_standup_active(url, user_3, public_channel_1)
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_standup_active_is_active(url, user_1, user_2, user_3, public_channel_1):
    """Testing when standup is active
    """
    assert helper_channel_invite(url, user_1, user_2, public_channel_1).json() == {}
    assert helper_channel_invite(url, user_2, user_3, public_channel_1).json() == {}

    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = helper_standup_start(url, user_1, public_channel_1, 2).json()
    assert information['time_finish'] == curr_time + 2

    information = helper_standup_active(url, user_1, public_channel_1).json()
    assert information['is_active']
    assert information['time_finish'] == curr_time + 2

    information = helper_standup_active(url, user_2, public_channel_1).json()
    assert information['is_active']
    assert information['time_finish'] == curr_time + 2 

    information = helper_standup_active(url, user_3, public_channel_1).json()
    assert information['is_active']
    assert information['time_finish'] == curr_time + 2 
    requests.delete(f'{url}/clear')

def test_standup_active_not_active(url, user_1, user_2, user_3, public_channel_1):
    """Testing when standup is not active
    """
    assert helper_channel_invite(url, user_1, user_2, public_channel_1).json() == {}
    assert helper_channel_invite(url, user_2, user_3, public_channel_1).json() == {}

    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = helper_standup_start(url, user_1, public_channel_1, 2).json()
    assert information['time_finish'] == curr_time + 2
    time.sleep(4)

    information = helper_standup_active(url, user_1, public_channel_1).json()
    assert not information['is_active']
    assert information['time_finish'] == None

    information = helper_standup_active(url, user_2, public_channel_1).json()
    assert not information['is_active']
    assert information['time_finish'] == None 

    information = helper_standup_active(url, user_3, public_channel_1).json()
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

    error = helper_standup_send(url, user_1, public_channel_1, 'Hey')
    assert error.status_code == AccessError.code
    error = helper_standup_send(url, user_2, public_channel_1, 'Hey')
    assert error.status_code == AccessError.code
    error = helper_standup_send(url, user_3, public_channel_1, 'Hey')
    assert error.status_code == AccessError.code
    error = helper_standup_send(url, user_4, public_channel_1, 'Hey')
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_standup_send_invalid_token(url, user_2, user_3, user_4, public_channel_1):
    """Testing invalid token for users
    """
    error = helper_standup_send(url, user_2, public_channel_1, 'Hey')
    assert error.status_code == AccessError.code
    error = helper_standup_send(url, user_3, public_channel_1, 'Hey')
    assert error.status_code == AccessError.code
    error = helper_standup_send(url, user_4, public_channel_1, 'Hey')
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_standup_send_invalid_channel(url, user_1, user_2):
    """Testing invalid channel_ids
    """
    error = helper_standup_send(url, user_1, {'channel_id': -122}, 'Hey')
    assert error.status_code == InputError.code
    error = helper_standup_send(url, user_1, {'channel_id': -642}, 'Hey')
    assert error.status_code == InputError.code
    error = helper_standup_send(url, user_2, {'channel_id': 6264}, 'Hey')
    assert error.status_code == InputError.code
    error = helper_standup_send(url, user_2, {'channel_id': 21.11}, 'Hey')
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_standup_send_invalid_message(url, user_1, user_2, user_3, public_channel_1):
    """Testing when message is invalid type
    """
    error = helper_standup_send(url, user_1, public_channel_1, 0)
    assert error.status_code == InputError.code
    error = helper_standup_send(url, user_2, public_channel_1, -10)
    assert error.status_code == InputError.code
    error = helper_standup_send(url, user_3, public_channel_1, 43.333)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_standup_send_more_than_1000_char(url, user_1, public_channel_1):
    """Testing when the message to send via standup send is over 1000 characters
    """
    message_str_1 = ("Hello" * 250)
    message_str_2 = ("HI " * 500)
    message_str_3 = ("My name is blah" * 100)

    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = helper_standup_start(url, user_1, public_channel_1, 2).json()
    assert information['time_finish'] == curr_time + 2

    error = helper_standup_send(url, user_1, public_channel_1, message_str_1)
    assert error.status_code == InputError.code
    error = helper_standup_send(url, user_1, public_channel_1, message_str_2)
    assert error.status_code == InputError.code
    error = helper_standup_send(url, user_1, public_channel_1, message_str_3)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_standup_send_no_standup(url, user_1, user_2, user_3, public_channel_1):
    """Testing when no standup is currently running in channel specified
    """
    assert helper_channel_invite(url, user_1, user_2, public_channel_1).json() == {}
    assert helper_channel_invite(url, user_2, user_3, public_channel_1).json() == {}

    error = helper_standup_send(url, user_1, public_channel_1, 'Hey')
    assert error.status_code == InputError.code
    error = helper_standup_send(url, user_2, public_channel_1, 'Hey')
    assert error.status_code == InputError.code
    error = helper_standup_send(url, user_3, public_channel_1, 'Hey')
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_standup_send_unauthorized_user(url, user_1, user_2, user_3, public_channel_1):
    """Testing when a user who is not part of the channel tries to send a standup to
       that channel
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = helper_standup_start(url, user_1, public_channel_1, 2).json()
    assert information['time_finish'] == curr_time + 2

    information = helper_standup_active(url, user_1, public_channel_1).json()
    assert information['is_active']
    assert information['time_finish'] == curr_time + 2

    error = helper_standup_send(url, user_2, public_channel_1, 'Hey')
    assert error.status_code == AccessError.code
    error = helper_standup_send(url, user_3, public_channel_1, 'Hey')
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_standup_send_working_example(url, user_1, user_2, user_3, public_channel_1):
    """Testing when standup send is working, via message collation
    """
    assert helper_channel_invite(url, user_1, user_2, public_channel_1).json() == {}
    assert helper_channel_invite(url, user_2, user_3, public_channel_1).json() == {}

    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = helper_standup_start(url, user_1, public_channel_1, 2).json()
    assert information['time_finish'] == curr_time + 2

    on_list = False
    assert helper_standup_send(url, user_1, public_channel_1, 'Pizza!').json() == {}
    message_data = helper_channel_messages(url, user_1, public_channel_1, 0).json()
    for messages in message_data['messages']:
        if messages['message'] == 'Pizza!':
            on_list = True
    assert not on_list
    
    assert helper_standup_send(url, user_2, public_channel_1, 'Water!').json() == {}
    assert helper_standup_send(url, user_3, public_channel_1, 'Melon!').json() == {}
    time.sleep(4)

    on_list = False
    message_data = helper_channel_messages(url, user_1, public_channel_1, 0).json()
    for messages in message_data['messages']:
        if messages['message'] == 'Pizza!':
            on_list = True
    assert on_list

    on_list = False
    for messages in message_data['messages']:
        if messages['message'] == 'Water!':
            on_list = True
    assert on_list

    on_list = False
    for messages in message_data['messages']:
        if messages['message'] == 'Melon!':
            on_list = True
    assert on_list
    requests.delete(f'{url}/clear')
