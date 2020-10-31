"""
standup feature test implementation to test functions in message.py


2020 T3 COMP1531 Major Project
"""
import time
import pytest
from datetime import timezone, datetime

import src.feature.auth as auth
import src.feature.channel as channel
import src.feature.channels as channels
import src.feature.message as message
import src.feature.standup as standup

from src.feature.data import data
from src.feature.other import clear
from src.feature.error import InputError, AccessError


#------------------------------------------------------------------------------#
#                               standup_start                                  #
#------------------------------------------------------------------------------#

#?------------------------ Input/Access Error Testing ------------------------?#

def test_standup_start_expired_token(user_1, user_2, user_3, user_4, public_channel_1):
    """Testing expired token for users which have logged out
    """
    auth.auth_logout(user_1['token'])
    auth.auth_logout(user_2['token'])
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])

    with pytest.raises(AccessError):
        standup.standup_start(user_1['token'], public_channel_1['channel_id'], 10)
    with pytest.raises(AccessError):
        standup.standup_start(user_2['token'], public_channel_1['channel_id'], 10)
    with pytest.raises(AccessError):
        standup.standup_start(user_3['token'], public_channel_1['channel_id'], 10)
    with pytest.raises(AccessError):
        standup.standup_start(user_4['token'], public_channel_1['channel_id'], 10)
    clear()

def test_standup_start_invalid_token(public_channel_1):
    """Testing invalid token for users
    """
    with pytest.raises(AccessError):
        standup.standup_start(-1, public_channel_1['channel_id'], 10)
    with pytest.raises(AccessError):
        standup.standup_start('@#&!', public_channel_1['channel_id'], 10)
    with pytest.raises(AccessError):
        standup.standup_start(43.333, public_channel_1['channel_id'], 10)
    clear()

def test_standup_start_invalid_channel(user_1, user_2):
    """Testing invalid channel_ids
    """
    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], -122, 10)
    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], -642, 10)
    with pytest.raises(InputError):
        standup.standup_start(user_2['token'], '@#@!', 10)
    with pytest.raises(InputError):
        standup.standup_start(user_2['token'], 212.11, 10)
    clear()

def test_standup_start_invalid_length(user_1, user_2, public_channel_1):
    """Testing invalid time length
    """
    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], public_channel_1['channel_id'], -10)
    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], public_channel_1['channel_id'], 0)
    with pytest.raises(InputError):
        standup.standup_start(user_2['token'], public_channel_1['channel_id'], '@#!')
    clear()

def test_standup_start_already_started(user_1, public_channel_1):
    """Testing when a standup is already running in channel 
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = standup.standup_start(user_1['token'], public_channel_1['channel_id'], 120)
    assert information['time_finish'] == curr_time + 120

    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], public_channel_1['channel_id'], 5)
    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], public_channel_1['channel_id'], 50)
    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], public_channel_1['channel_id'], 120)
    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], public_channel_1['channel_id'], 240)
    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], public_channel_1['channel_id'], 360)
    clear()

def test_standup_start_unauthorized_user(user_1, user_2, user_3, public_channel_1):
    """(Assumption testing) Testing when a user who is not part of the channel
       tries to start a standup
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = standup.standup_start(user_1['token'], public_channel_1['channel_id'], 2)
    assert information['time_finish'] == curr_time + 2

    information = standup.standup_active(user_1['token'], public_channel_1['channel_id'])
    assert information['is_active']
    assert information['time_finish'] == curr_time + 2

    with pytest.raises(AccessError):
        standup.standup_start(user_2['token'], public_channel_1['channel_id'], 2)
    with pytest.raises(AccessError):
        standup.standup_start(user_3['token'], public_channel_1['channel_id'], 2)
    clear()


#?------------------------------ Output Testing ------------------------------?#

def test_standup_start_working_example(user_1, user_2, user_3, public_channel_1):
    """Testing when standup is working, via message collation
    """
    assert channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id']) == {}
    assert channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_3['u_id']) == {}

    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = standup.standup_start(user_1['token'], public_channel_1['channel_id'], 2)
    assert information['time_finish'] == curr_time + 2

    assert data.specify_standup_status(public_channel_1['channel_id'])['is_active'] == True
    assert standup.standup_send(user_1['token'], public_channel_1['channel_id'], 'Hey guys!') == {}
    assert standup.standup_send(user_2['token'], public_channel_1['channel_id'], 'Its working!') == {}
    assert standup.standup_send(user_3['token'], public_channel_1['channel_id'], 'Wohoo!') == {}
    assert data.specify_standup_status(public_channel_1['channel_id'])['is_active'] == True
    time.sleep(4)
    assert data.specify_standup_status(public_channel_1['channel_id'])['is_active'] == False

    on_list = False
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
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
    clear()

#------------------------------------------------------------------------------#
#                               standup_active                                 #
#------------------------------------------------------------------------------#

#?------------------------ Input/Access Error Testing ------------------------?#

def test_standup_active_expired_token(user_1, user_2, user_3, user_4, public_channel_1):
    """Testing invalid token for users which have logged out
    """
    auth.auth_logout(user_1['token'])
    auth.auth_logout(user_2['token'])
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])

    with pytest.raises(AccessError):
        standup.standup_active(user_1['token'], public_channel_1['channel_id'])
    with pytest.raises(AccessError):
        standup.standup_active(user_2['token'], public_channel_1['channel_id'])
    with pytest.raises(AccessError):
        standup.standup_active(user_3['token'], public_channel_1['channel_id'])
    with pytest.raises(AccessError):
        standup.standup_active(user_4['token'], public_channel_1['channel_id'])
    clear()

def test_standup_active_invalid_token(public_channel_1):
    """Testing invalid token for users
    """
    with pytest.raises(AccessError):
        standup.standup_active(-1, public_channel_1['channel_id'])
    with pytest.raises(AccessError):
        standup.standup_active('@#&!', public_channel_1['channel_id'])
    with pytest.raises(AccessError):
        standup.standup_active(43.333, public_channel_1['channel_id'])
    clear()

def test_standup_active_invalid_channel(user_1, user_2):
    """Testing invalid channel_ids
    """
    with pytest.raises(InputError):
        standup.standup_active(user_1['token'], -122)
    with pytest.raises(InputError):
        standup.standup_active(user_1['token'], -642)
    with pytest.raises(InputError):
        standup.standup_active(user_2['token'], '@#@!')
    with pytest.raises(InputError):
        standup.standup_active(user_2['token'], 212.11)
    clear()

def test_standup_active_unauthorized_user(user_1, user_2, user_3, public_channel_1):
    """(Assumption testing) Testing when a user who is not part of the channel
       tries to see if a standup is active in that channel
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = standup.standup_start(user_1['token'], public_channel_1['channel_id'], 2)
    assert information['time_finish'] == curr_time + 2

    information = standup.standup_active(user_1['token'], public_channel_1['channel_id'])
    assert information['is_active']
    assert information['time_finish'] == curr_time + 2

    with pytest.raises(AccessError):
        standup.standup_active(user_2['token'], public_channel_1['channel_id'])
    with pytest.raises(AccessError):
        standup.standup_active(user_3['token'], public_channel_1['channel_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_standup_active_is_active(user_1, user_2, user_3, public_channel_1):
    """Testing when standup is active
    """
    assert channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id']) == {}
    assert channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_3['u_id']) == {}

    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = standup.standup_start(user_1['token'], public_channel_1['channel_id'], 2)
    assert information['time_finish'] == curr_time + 2

    information = standup.standup_active(user_1['token'], public_channel_1['channel_id'])
    assert information['is_active']
    assert information['time_finish'] == curr_time + 2

    information = standup.standup_active(user_2['token'], public_channel_1['channel_id'])
    assert information['is_active']
    assert information['time_finish'] == curr_time + 2 

    information = standup.standup_active(user_3['token'], public_channel_1['channel_id'])
    assert information['is_active']
    assert information['time_finish'] == curr_time + 2 
    clear()

def test_standup_active_not_active(user_1, user_2, user_3, public_channel_1):
    """Testing when standup is not active
    """
    assert channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id']) == {}
    assert channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_3['u_id']) == {}

    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = standup.standup_start(user_1['token'], public_channel_1['channel_id'], 2)
    assert information['time_finish'] == curr_time + 2
    time.sleep(2)

    information = standup.standup_active(user_1['token'], public_channel_1['channel_id'])
    assert not information['is_active']
    assert information['time_finish'] == None

    information = standup.standup_active(user_2['token'], public_channel_1['channel_id'])
    assert not information['is_active']
    assert information['time_finish'] == None

    information = standup.standup_active(user_3['token'], public_channel_1['channel_id'])
    assert not information['is_active']
    assert information['time_finish'] == None
    clear()

#------------------------------------------------------------------------------#
#                                standup_send                                  #
#------------------------------------------------------------------------------#

#?------------------------ Input/Access Error Testing ------------------------?#

def test_standup_send_expired_token(user_1, user_2, user_3, user_4, public_channel_1):
    """Testing expired token for users which have logged out
    """
    auth.auth_logout(user_1['token'])
    auth.auth_logout(user_2['token'])
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])

    with pytest.raises(AccessError):
        standup.standup_send(user_1['token'], public_channel_1['channel_id'], 'Hey')
    with pytest.raises(AccessError):
        standup.standup_send(user_2['token'], public_channel_1['channel_id'], 'Hey')
    with pytest.raises(AccessError):
        standup.standup_send(user_3['token'], public_channel_1['channel_id'], 'Hey')
    with pytest.raises(AccessError):
        standup.standup_send(user_4['token'], public_channel_1['channel_id'], 'Hey')
    clear()

def test_standup_send_invalid_token(public_channel_1):
    """Testing invalid token for users
    """
    with pytest.raises(AccessError):
        standup.standup_send(-1, public_channel_1['channel_id'], 'Hey')
    with pytest.raises(AccessError):
        standup.standup_send('@#&!', public_channel_1['channel_id'], 'Hey')
    with pytest.raises(AccessError):
        standup.standup_send(43.333, public_channel_1['channel_id'], 'Hey')
    clear()

def test_standup_send_invalid_channel(user_1, user_2):
    """Testing invalid channel_ids
    """
    with pytest.raises(InputError):
        standup.standup_send(user_1['token'], -122, 'Hey')
    with pytest.raises(InputError):
        standup.standup_send(user_1['token'], -642, 'Hey')
    with pytest.raises(InputError):
        standup.standup_send(user_2['token'], '@#@!', 'Hey')
    with pytest.raises(InputError):
        standup.standup_send(user_2['token'], 212.11, 'Hey')
    clear()

def test_standup_send_invalid_message(user_1, user_2, user_3, public_channel_1):
    """Testing when message is invalid type
    """
    with pytest.raises(InputError):
        standup.standup_send(user_1['token'], public_channel_1['channel_id'], 0)
    with pytest.raises(InputError):
        standup.standup_send(user_2['token'], public_channel_1['channel_id'], -10)
    with pytest.raises(InputError):
        standup.standup_send(user_3['token'], public_channel_1['channel_id'], 43.333)
    clear()

def test_standup_send_more_than_1000_char(user_1, public_channel_1):
    """Testing when the message to send via standup send is over 1000 characters
    """
    message_str_1 = ("Hello" * 250)
    message_str_2 = ("HI " * 500)
    message_str_3 = ("My name is blah" * 100)

    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = standup.standup_start(user_1['token'], public_channel_1['channel_id'], 2)
    assert information['time_finish'] == curr_time + 2

    with pytest.raises(InputError):
        standup.standup_send(user_1['token'], public_channel_1['channel_id'], message_str_1)
    with pytest.raises(InputError):
        standup.standup_send(user_1['token'], public_channel_1['channel_id'], message_str_2)
    with pytest.raises(InputError):
        standup.standup_send(user_1['token'], public_channel_1['channel_id'], message_str_3)
    clear()

def test_standup_send_no_standup(user_1, user_2, user_3, public_channel_1):
    """Testing when no standup is currently running in channel specified
    """
    assert channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id']) == {}
    assert channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_3['u_id']) == {}

    with pytest.raises(InputError):
        standup.standup_send(user_1['token'], public_channel_1['channel_id'], 'Hey')
    with pytest.raises(InputError):
        standup.standup_send(user_2['token'], public_channel_1['channel_id'], 'Hey')
    with pytest.raises(InputError):
        standup.standup_send(user_3['token'], public_channel_1['channel_id'], 'Hey')
    clear()

def test_standup_send_unauthorized_user(user_1, user_2, user_3, public_channel_1):
    """Testing when a user who is not part of the channel tries to send a standup to
       that channel
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = standup.standup_start(user_1['token'], public_channel_1['channel_id'], 2)
    assert information['time_finish'] == curr_time + 2

    information = standup.standup_active(user_1['token'], public_channel_1['channel_id'])
    assert information['is_active']
    assert information['time_finish'] == curr_time + 2

    with pytest.raises(AccessError):
        standup.standup_send(user_2['token'], public_channel_1['channel_id'], 'Hey')
    with pytest.raises(AccessError):
        standup.standup_send(user_3['token'], public_channel_1['channel_id'], 'Hey')
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_standup_send_working_example(user_1, user_2, user_3, public_channel_1):
    """Testing when standup send is working, via message collation
    """
    assert channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id']) == {}
    assert channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_3['u_id']) == {}

    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = standup.standup_start(user_1['token'], public_channel_1['channel_id'], 2)
    assert information['time_finish'] == curr_time + 2

    assert standup.standup_send(user_1['token'], public_channel_1['channel_id'], 'Pizza!') == {}
    assert standup.standup_send(user_2['token'], public_channel_1['channel_id'], 'Water!') == {}
    assert standup.standup_send(user_3['token'], public_channel_1['channel_id'], 'Melon!') == {}
    time.sleep(4)

    on_list = False
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
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
    clear()
