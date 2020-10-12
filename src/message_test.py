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
#                                 message_send                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_message_send_more_than_1000_char():
    """
    Testing when the message sent is over 1000 characters
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    message_str = ("Hello" * 250)
    with pytest.raises(InputError):
        message.message_send(user_1['token'], new_channel['channel_id'], message_str)
    clear()

def test_message_send_auth_user_not_in_channel():
    """
    Testing when the authorised user has not joined the channel they
    are trying to post to
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    message_str = "Hello"
    with pytest.raises(AccessError):
        message.message_send(user_2['token'], new_channel['channel_id'], message_str)
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_message_send_output_one():
    """
    Testing a normal case (Authorised user sends a message in a channel)
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    channel.channel_join(user_2['token'], new_channel['channel_id'])
    message_str_one = "Welcome guys!"
    message_str_two = "Hello, I'm Jane!"
    message.message_send(user_1['token'], new_channel['channel_id'], message_str_one)
    message.message_send(user_2['token'], new_channel['channel_id'], message_str_two)
    message_list = channel.channel_messages(user_1['token'], new_channel['channel_id'], 0)
    message_count = 0
    for msg in message_list['messages']:
        message_count += 1
        assert msg is message_str_one or msg is message_str_two
    assert message_count == 2
    clear()

#------------------------------------------------------------------------------#
#                               message_remove                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

#?------------------------------ Output Testing ------------------------------?#

#------------------------------------------------------------------------------#
#                                 message_edit                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

#?------------------------------ Output Testing ------------------------------?#
