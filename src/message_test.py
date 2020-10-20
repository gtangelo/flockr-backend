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
from error import InputError, AccessError
from other import clear

#------------------------------------------------------------------------------#
#                                message_send                                  #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_message_send_more_than_1000_char():
    """
    Testing when the message sent is over 1000 characters
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    message_str_1 = ("Hello" * 250)
    message_str_2 = ("HI " * 500)
    message_str_3 = ("My name is blah" * 100)
    with pytest.raises(InputError):
        message.message_send(user_1['token'], new_channel['channel_id'], message_str_1)
    with pytest.raises(InputError):
        message.message_send(user_1['token'], new_channel['channel_id'], message_str_2)
    with pytest.raises(InputError):
        message.message_send(user_1['token'], new_channel['channel_id'], message_str_3)
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

def test_message_send_expired_token():
    """
    Testing invalid token for users which have logged out
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    user_4 = auth.auth_register('prathsjag@gmail.com', 'password', 'Praths', 'Jag')

    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    new_message = message.message_send(user_1['token'], new_channel['channel_id'], "Hey channel!")
    auth.auth_logout(user_1['token'])
    auth.auth_logout(user_2['token'])
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])

    with pytest.raises(AccessError):
        message.message_send(user_1['token'], new_message['message_id'], "Hi")
    with pytest.raises(AccessError):
        message.message_send(user_1['token'], new_message['message_id'], "Hi")
    with pytest.raises(AccessError):
        message.message_send(user_1['token'], new_message['message_id'], "Hi")
    with pytest.raises(AccessError):
        message.message_send(user_1['token'], new_message['message_id'], "Hi")
    clear()

def test_message_send_incorrect_token_type():
    """
    Testing invalid token data type handling
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    new_message = message.message_send(user['token'], new_channel['channel_id'], "Bye channel!")

    with pytest.raises(AccessError):
        message.message_send(12, new_message['message_id'], "Hi")
    with pytest.raises(AccessError):
        message.message_send(-12, new_message['message_id'], "Hi")
    with pytest.raises(AccessError):
        message.message_send(121.11, new_message['message_id'], "Hi")
    clear()

def test_message_send_channel_id():
    """
    Testing when an invalid channel_id is used as a parameter
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    with pytest.raises(InputError):
        message.message_send(user['token'], new_channel['channel_id'] + 7, "Bye channel!")
    clear()

def test_message_send_valid_token():
    """
    Testing if token is valid
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    with pytest.raises(AccessError):
        message.message_send(-1, new_channel['channel_id'], "Bye channel!")
    clear()

def test_message_send_output_empty_str():
    """
    Testing an empty string message (Authorised user sends a message in a channel)
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    channel.channel_join(user_2['token'], new_channel['channel_id'])
    message_str = ""
    with pytest.raises(InputError):
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
    check_unique_msg_id = []
    for msg in message_list['messages']:
        message_count += 1
        check_unique_msg_id.append(msg['message_id'])
        assert msg['message'] in (message_str_one, message_str_two)
    assert message_count == 2
    assert check_unique_msg_id[0] != check_unique_msg_id[1]
    clear()

def test_message_send_output_two():
    """
    Testing a longer case (multiple authorised users sending messages in a channel)
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    user_3 = auth.auth_register('jonesmith@gmail.com', 'password', 'Jone', 'Smith')
    user_4 = auth.auth_register('jamesmith@gmail.com', 'password', 'Jame', 'Smith')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    channel.channel_join(user_2['token'], new_channel['channel_id'])
    channel.channel_join(user_3['token'], new_channel['channel_id'])
    channel.channel_join(user_4['token'], new_channel['channel_id'])
    msg_str_1 = "Welcome guys!"
    msg_str_2 = "Hello, I'm Jane!"
    msg_str_3 = "sup"
    msg_str_4 = "Ok, let's start the project"
    msg_str_5 = "Join the call when you're ready guys"
    msg_str_6 = "sure, lemme get something to eat first"
    msg_str_7 = "Yeah aight, I'm joining."
    message.message_send(user_1['token'], new_channel['channel_id'], msg_str_1)
    message.message_send(user_2['token'], new_channel['channel_id'], msg_str_2)
    message.message_send(user_3['token'], new_channel['channel_id'], msg_str_3)
    message.message_send(user_4['token'], new_channel['channel_id'], msg_str_4)
    message.message_send(user_1['token'], new_channel['channel_id'], msg_str_5)
    message.message_send(user_2['token'], new_channel['channel_id'], msg_str_6)
    message.message_send(user_3['token'], new_channel['channel_id'], msg_str_7)
    message_list = channel.channel_messages(user_1['token'], new_channel['channel_id'], 0)
    message_count = 0
    message_confirmed = False
    check_unique_msg_id = []
    for msg in message_list['messages']:
        if msg['message'] in {msg_str_1, msg_str_2, msg_str_3, 
                            msg_str_4, msg_str_5, msg_str_6, msg_str_7}:
            message_confirmed = True
        message_count += 1
        check_unique_msg_id.append(msg['message_id'])
    assert message_count == 7
    assert message_confirmed
    assert len(set(check_unique_msg_id)) == 7
    clear()

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
    new_message = message.message_send(user_1['token'], new_channel['channel_id'], "Hey channel!")
    auth.auth_logout(user_1['token'])
    auth.auth_logout(user_2['token'])
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])

    with pytest.raises(AccessError):
        message.message_remove(user_1['token'], new_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_2['token'], new_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_3['token'], new_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_4['token'], new_message['message_id'])
    clear()

def test_message_remove_incorrect_token_type():
    """Testing invalid token data type handling
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    new_message = message.message_send(user['token'], new_channel['channel_id'], "Bye channel!")

    with pytest.raises(AccessError):
        message.message_remove(12, new_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(-12, new_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(121.11, new_message['message_id'])
    clear()

def test_message_remove_wrong_data_type():
    """Testing when wrong data types are used as input
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    new_message = message.message_send(user['token'], new_channel['channel_id'], "Bye channel!")

    with pytest.raises(InputError):
        message.message_remove(user['token'], '@#$!')
    with pytest.raises(InputError):
        message.message_remove(user['token'], 67.666)
    with pytest.raises(InputError):
        message.message_remove(user['token'], new_message['message_id'] - 1)
    with pytest.raises(InputError):
        message.message_remove(user['token'], new_message['message_id'] + 1)
    clear()

def test_message_remove_message_not_existent():
    """Testing when message based on message_id does not exist
       and is subjected for deletion
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    new_message = message.message_send(user['token'], new_channel['channel_id'], "Bye channel!")

    with pytest.raises(InputError):
        message.message_remove(user['token'], new_message['message_id'] + 1)
    with pytest.raises(InputError):
        message.message_remove(user['token'], new_message['message_id'] - 1)
    with pytest.raises(InputError):
        message.message_remove(user['token'], new_message['message_id'] + 100)
    with pytest.raises(InputError):
        message.message_remove(user['token'], new_message['message_id'] - 100)
    clear()

def test_message_remove_message_deleted_already():
    """Testing when message based on message_id has been deleted already
       and is subjected for deletion again
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    new_message = message.message_send(user['token'], new_channel['channel_id'], "Hey channel!")
    assert message.message_remove(user['token'], new_message['message_id']) == {}

    with pytest.raises(InputError):
        message.message_remove(user['token'], new_message['message_id'])
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
    new_message = message.message_send(user_1['token'], new_channel['channel_id'], "Hey channel!")

    with pytest.raises(AccessError):
        message.message_remove(user_2['token'], new_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_3['token'], new_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_4['token'], new_message['message_id'])
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
    new_message = message.message_send(user_1['token'], new_channel['channel_id'], "Hey channel!")

    with pytest.raises(AccessError):
        message.message_remove(user_2['token'], new_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_3['token'], new_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_4['token'], new_message['message_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_message_remove_authorized_owner_channel():
    """Testing when message based on message_id is deleted by channel owner / flockr owner
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message_1 = message.message_send(user['token'], new_channel['channel_id'], 'I')
    message_2 = message.message_send(user['token'], new_channel['channel_id'], 'am')
    message_3 = message.message_send(user['token'], new_channel['channel_id'], 'really')
    message_4 = message.message_send(user['token'], new_channel['channel_id'], 'hungry :(')
    on_list = False
    assert message.message_remove(user['token'], message_1['message_id']) == {}
    message_data = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            on_list = True
    assert not on_list

    assert message.message_remove(user['token'], message_3['message_id']) == {}
    message_data = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_3['message_id']:
            on_list = True
    assert not on_list

    assert message.message_remove(user['token'], message_2['message_id']) == {}
    message_data = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_2['message_id']:
            on_list = True
    assert not on_list

    assert message.message_remove(user['token'], message_4['message_id']) == {}
    message_data = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_4['message_id']:
            on_list = True
    assert not on_list
    clear()

def test_message_remove_authorized_flockr_owner():
    """(Assumption Testing) Testing when message based on message_id is deleted by
       flockr owner who is not part of any channel
       (Assumption) First user to register is flockr owner
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    new_channel = channels.channels_create(user_2['token'], 'Group 1', True)
    message_1 = message.message_send(user_2['token'], new_channel['channel_id'], 'I')
    message_2 = message.message_send(user_2['token'], new_channel['channel_id'], 'am')
    message_3 = message.message_send(user_2['token'], new_channel['channel_id'], 'really')
    message_4 = message.message_send(user_2['token'], new_channel['channel_id'], 'hungry :(')

    on_list = False
    assert message.message_remove(user_1['token'], message_1['message_id']) == {}
    message_data = channel.channel_messages(user_2['token'], new_channel['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            on_list = True
    assert not on_list

    assert message.message_remove(user_1['token'], message_3['message_id']) == {}
    message_data = channel.channel_messages(user_2['token'], new_channel['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_3['message_id']:
            on_list = True
    assert not on_list

    assert message.message_remove(user_1['token'], message_2['message_id']) == {}
    message_data = channel.channel_messages(user_2['token'], new_channel['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_2['message_id']:
            on_list = True
    assert not on_list

    assert message.message_remove(user_1['token'], message_4['message_id']) == {}
    message_data = channel.channel_messages(user_2['token'], new_channel['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_4['message_id']:
            on_list = True
    assert not on_list
    clear()

#------------------------------------------------------------------------------#
#                                message_edit                                  #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_message_edit_expired_token():
    """Testing invalid token for users which have logged out
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    user_4 = auth.auth_register('prathsjag@gmail.com', 'password', 'Praths', 'Jag')

    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    new_message = message.message_send(user_1['token'], new_channel['channel_id'], "Hey channel!")
    auth.auth_logout(user_1['token'])
    auth.auth_logout(user_2['token'])
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])

    with pytest.raises(AccessError):
        message.message_edit(user_1['token'], new_message['message_id'], 'hello')
    with pytest.raises(AccessError):
        message.message_edit(user_2['token'], new_message['message_id'], 'hello')
    with pytest.raises(AccessError):
        message.message_edit(user_3['token'], new_message['message_id'], 'hello')
    with pytest.raises(AccessError):
        message.message_edit(user_4['token'], new_message['message_id'], 'hello')
    clear()

def test_message_edit_incorrect_token_type():
    """Testing invalid token data type handling
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    new_message = message.message_send(user['token'], new_channel['channel_id'], "Bye channel!")

    with pytest.raises(AccessError):
        message.message_edit(12, new_message['message_id'], 'hello')
    with pytest.raises(AccessError):
        message.message_edit(-12, new_message['message_id'], 'hello')
    with pytest.raises(AccessError):
        message.message_edit(121.11, new_message['message_id'], 'hello')
    clear()

def test_message_edit_wrong_data_type():
    """Testing when wrong data types are used as input
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    new_message = message.message_send(user['token'], new_channel['channel_id'], "Bye channel!")

    with pytest.raises(InputError):
        message.message_edit(user['token'], '@#$!', 'hello')
    with pytest.raises(InputError):
        message.message_edit(user['token'], 67.666, 'hello')
    with pytest.raises(InputError):
        message.message_edit(user['token'], new_message['message_id'] - 1, 'hello')
    with pytest.raises(InputError):
        message.message_edit(user['token'], new_message['message_id'] + 1, 'hello')
    clear()

def test_message_edit_integer_message():
    """Testing when message data type is an integer
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    new_message = message.message_send(user['token'], new_channel['channel_id'], "Bye channel!")

    with pytest.raises(InputError):
        message.message_edit(user['token'], new_message['message_id'], 0)
    with pytest.raises(InputError):
        message.message_edit(user['token'], new_message['message_id'], -1)
    with pytest.raises(InputError):
        message.message_edit(user['token'], new_message['message_id'], 100)
    with pytest.raises(InputError):
        message.message_edit(user['token'], new_message['message_id'], 127.66)
    clear()

def test_message_edit_more_than_1000_char():
    """
    Testing when the message to edit is over 1000 characters
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    new_message = message.message_send(user_1['token'], new_channel['channel_id'], "Bye channel!")
    message_str_1 = ("Hello" * 250)
    message_str_2 = ("HI " * 500)
    message_str_3 = ("My name is blah" * 100)
    with pytest.raises(InputError):
        message.message_edit(user_1['token'], new_message['message_id'], message_str_1)
    with pytest.raises(InputError):
        message.message_edit(user_1['token'], new_message['message_id'], message_str_2)
    with pytest.raises(InputError):
        message.message_edit(user_1['token'], new_message['message_id'], message_str_3)
    clear()

def test_message_edit_deleted_message():
    """Testing when message based on message_id does not exist
       and is subjected for editing
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    new_message = message.message_send(user['token'], new_channel['channel_id'], "Bye channel!")

    assert message.message_remove(user['token'], new_message['message_id']) == {}

    with pytest.raises(InputError):
        message.message_edit(user['token'], new_message['message_id'], 'hey')
    clear()

def test_message_edit_not_authorized_channel_owner():
    """Testing when message based on message_id is called for editing
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
    new_message = message.message_send(user_1['token'], new_channel['channel_id'], "Hey channel!")

    with pytest.raises(AccessError):
        message.message_edit(user_2['token'], new_message['message_id'], 'lets edit!')
    with pytest.raises(AccessError):
        message.message_edit(user_3['token'], new_message['message_id'], 'lets edit!')
    with pytest.raises(AccessError):
        message.message_edit(user_4['token'], new_message['message_id'], 'lets edit!')
    clear()

def test_message_edit_not_authorized_flockr_owner():
    """Testing when message based on message_id is called for editing
       but the requester is not a flockr owner
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    user_4 = auth.auth_register('prathsjag@gmail.com', 'password', 'Praths', 'Jag')

    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    new_message = message.message_send(user_1['token'], new_channel['channel_id'], "Hey channel!")

    with pytest.raises(AccessError):
        message.message_edit(user_2['token'], new_message['message_id'], 'lets edit!')
    with pytest.raises(AccessError):
        message.message_edit(user_3['token'], new_message['message_id'], 'lets edit!')
    with pytest.raises(AccessError):
        message.message_edit(user_4['token'], new_message['message_id'], 'lets edit!')
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_message_edit_authorized_owner_channel():
    """Testing when message based on message_id is edited by channel owner / flockr owner
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    new_message = message.message_send(user['token'], new_channel['channel_id'], 'hungry :(')

    on_list = False
    message_data = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == new_message['message_id']:
            if messages['message'] == 'hungry :(':
                on_list = True
    assert on_list

    edited = False
    assert message.message_edit(user['token'], new_message['message_id'], 'not hungry :)') == {}
    message_data = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == new_message['message_id']:
            if messages['message'] == 'not hungry :)':
                edited = True
    assert edited
    clear()

def test_message_edit_authorized_flockr_owner():
    """(Assumption Testing) Testing when message based on message_id is edited by
       flockr owner who is not part of any channel
       (Assumption) First user to register is flockr owner
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    new_channel = channels.channels_create(user_2['token'], 'Group 1', True)
    new_message = message.message_send(user_2['token'], new_channel['channel_id'], 'hungry :(')

    on_list = False
    message_data = channel.channel_messages(user_2['token'], new_channel['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == new_message['message_id']:
            if messages['message'] == 'hungry :(':
                on_list = True
    assert on_list

    edited = False
    assert message.message_edit(user_1['token'], new_message['message_id'], 'not hungry :)') == {}
    message_data = channel.channel_messages(user_2['token'], new_channel['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == new_message['message_id']:
            if messages['message'] == 'not hungry :)':
                edited = True
    assert edited
    clear()

def test_message_edit_empty_string():
    """Testing when message based on message_id is edited by
       an empty string; in which case the message is deleted
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message_1 = message.message_send(user['token'], new_channel['channel_id'], 'I')
    message_2 = message.message_send(user['token'], new_channel['channel_id'], 'am')
    message_3 = message.message_send(user['token'], new_channel['channel_id'], 'really')
    message_4 = message.message_send(user['token'], new_channel['channel_id'], 'hungry :(')

    on_list = False
    assert message.message_edit(user['token'], message_1['message_id'], '') == {}
    message_data = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            on_list = True
    assert not on_list

    assert message.message_edit(user['token'], message_3['message_id'], '') == {}
    message_data = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_3['message_id']:
            on_list = True
    assert not on_list

    assert message.message_edit(user['token'], message_2['message_id'], "") == {}
    message_data = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_2['message_id']:
            on_list = True
    assert not on_list

    assert message.message_edit(user['token'], message_4['message_id'], "") == {}
    message_data = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_4['message_id']:
            on_list = True
    assert not on_list
    clear()
