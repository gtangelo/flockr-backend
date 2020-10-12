"""
message feature test implementation to test functions in message.py

Feature implementation was written by Tam Do and Prathamesh Jagtap.

2020 T3 COMP1531 Major Project
"""

import pytest
import auth
import channel
import channels
import message
from datetime import datetime, timezone
from error import InputError, AccessError
from other import clear

#------------------------------------------------------------------------------#
#                                message_send                                  #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

#?------------------------------ Output Testing ------------------------------?#

#------------------------------------------------------------------------------#
#                                message_remove                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_message_remove_expired_token():
    """Testing invalid token for users which have logged out
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    user_4 = auth.auth_register('prathsjag@gmail.com', 'password', 'Praths', 'Jag')

    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    message = message.message_send(user_1['token'], new_channel['channel_id'], "Hey channel!")
    auth.auth_logout(user_1['token'])
    auth.auth_logout(user_2['token'])
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])

    with pytest.raises(AccessError):
        message.message_remove(user_1['token'], message['message_id'])  
    with pytest.raises(AccessError):
        message.message_remove(user_2['token'], message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_3['token'], message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_4['token'], message['message_id'])
    clear()

def test_message_remove_incorrect_token_type():
    """Testing invalid token data type handling
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message = message.message_send(user['token'], new_channel['channel_id'], "Bye channel!")

    with pytest.raises(AccessError):
        message.message_remove(12, message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(-12, message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(121.11, message['message_id'])
    clear()

def test_message_remove_wrong_data_type():
    """Testing when wrong data types are used as input
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message = message.message_send(user['token'], new_channel['channel_id'], "Bye channel!") 

    with pytest.raises(InputError):
        message.message_remove(user['token'], '@#$!')
    with pytest.raises(InputError):
        message.message_remove(user['token'], 67.666)
    with pytest.raises(InputError):
        message.message_remove(user['token'], message['message_id'] - 1)
    with pytest.raises(InputError):
        message.message_remove(user['token'], message['message_id'] + 1)
    clear()

def test_message_remove_message_not_existent():
    """Testing when message based on message_id does not exist
       and is subjected for deletion
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message = message.message_send(user['token'], new_channel['channel_id'], "Bye channel!") 

    with pytest.raises(InputError):
        message.message_remove(user['token'], message['message_id'] + 1)
    with pytest.raises(InputError):
        message.message_remove(user['token'], message['message_id'] - 1)
    with pytest.raises(InputError):
        message.message_remove(user['token'], message['message_id'] + 100)
    with pytest.raises(InputError):
        message.message_remove(user['token'], message['message_id'] - 100)
    clear()

def test_message_remove_message_deleted_already():
    """Testing when message based on message_id has been deleted already
       and is subjected for deletion again
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message = message.message_send(user['token'], new_channel['channel_id'], "Hey channel!")
    
    assert message.message_remove(user['token'], message['message_id']) == {}

    with pytest.raises(InputError):
        message.message_remove(user['token'], message['message_id'])
    clear()

def test_message_remove_not_authorized_channel_owner():
    """Testing when message based on message_id is called for deletion
       but the requester is not a channel_owner
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    user_4 = auth.auth_register('prathsjag@gmail.com', 'password', 'Praths', 'Jag')

    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    channel.channel_invite(user_1['token'], new_channel['channel_id'], user_2['u_id'])
    channel.channel_invite(user_2['token'], new_channel['channel_id'], user_3['u_id'])
    message = message.message_send(user_1['token'], new_channel['channel_id'], "Hey channel!")

    with pytest.raises(AccessError):
        message.message_remove(user_2['token'], message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_3['token'], message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_4['token'], message['message_id'])
    clear()

def test_message_remove_not_authorized_flockr_owner():
    """Testing when message based on message_id is called for deletion
       but the requester is not a flockr owner
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    user_4 = auth.auth_register('prathsjag@gmail.com', 'password', 'Praths', 'Jag')

    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    message = message.message_send(user_1['token'], new_channel['channel_id'], "Hey channel!")

    with pytest.raises(AccessError):
        message.message_remove(user_2['token'], message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_3['token'], message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_4['token'], message['message_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

#------------------------------------------------------------------------------#
#                                message_edit                                  #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

#?------------------------------ Output Testing ------------------------------?#
