"""
message feature test implementation to test functions in message.py

Feature implementation was written by Tam Do and Prathamesh Jagtap.

2020 T3 COMP1531 Major Project
"""
from datetime import timezone, datetime
import time
import requests

from src.feature.error import InputError, AccessError
from src.helpers.helpers_http_test import (
    send_message, 
    send_message_later, 
    helper_message_pin, 
    helper_message_unpin,
    helper_message_react,
    helper_message_unreact,
)

THUMBS_UP = 1
THUMBS_DOWN = 2

# Delay for messages (To avoid failed tests)
DELAY = 5

#------------------------------------------------------------------------------#
#                                 message/send                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_message_send_more_than_1000_char(url, user_1, public_channel_1):
    """
    Testing when the message sent is over 1000 characters
    """
    resp = send_message(url, user_1, public_channel_1, ("Hello" * 250))
    assert resp.status_code == InputError.code
    resp = send_message(url, user_1, public_channel_1, ("HI " * 500))
    assert resp.status_code == InputError.code
    resp = send_message(url, user_1, public_channel_1, ("My name is blah" * 100))
    assert resp.status_code == InputError.code
    requests.delete(url + '/clear')

def test_message_send_auth_user_not_in_channel(url, user_1, user_2, public_channel_1):
    """
    Testing when the authorised user has not joined the channel they
    are trying to post to
    """
    resp = send_message(url, user_2, public_channel_1, "Hello")
    assert resp.status_code == AccessError.code
    requests.delete(url + '/clear')

def test_message_send_expired_token(url, user_1, user_2, user_3, user_4, public_channel_1):
    """
    Testing invalid token for users which have logged out
    """
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_1['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_2['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_3['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_4['token']}).json()
    assert log_out['is_success']

    res_err = send_message(url, user_1, public_channel_1, "Hello")
    assert res_err.status_code == AccessError.code

    res_err = send_message(url, user_2, public_channel_1, "Hello")
    assert res_err.status_code == AccessError.code

    res_err = send_message(url, user_3, public_channel_1, "Hello")
    assert res_err.status_code == AccessError.code

    res_err = send_message(url, user_4, public_channel_1, "Hello")
    assert res_err.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_message_send_incorrect_token_type(url, user_1, public_channel_1):
    """
    Testing invalid token data type handling
    """
    arg_message = {
        'token'     : 12,
        'channel_id': public_channel_1['channel_id'],
        'message'   : "Hello",
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    assert res_err.status_code == AccessError.code

    arg_message = {
        'token'     : -12,
        'channel_id': public_channel_1['channel_id'],
        'message'   : "Hello",
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    assert res_err.status_code == AccessError.code

    arg_message = {
        'token'     : 121.11,
        'channel_id': public_channel_1['channel_id'],
        'message'   : "Hello",
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    assert res_err.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_message_send_channel_id(url, user_1, public_channel_1):
    """
    Testing when an invalid channel_id is used as a parameter
    """
    arg_message = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'] + 7,
        'message'   : "Hello",
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    assert res_err.status_code == InputError.code

    requests.delete(url + '/clear')

def test_message_send_valid_token(url, user_1, public_channel_1):
    """
    Testing if token is valid
    """
    arg_message = {
        'token'     : -1,
        'channel_id': public_channel_1['channel_id'],
        'message'   : "Hello",
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    assert res_err.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_message_send_output_empty_str(url, user_1, user_2, public_channel_1):
    """
    Testing an empty string message (Authorised user sends a message in a channel)
    """
    arg_join = {
        'token'     : user_2['token'],
        'channel_id': public_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    res_err = send_message(url, user_2, public_channel_1, "")
    assert res_err.status_code == InputError.code

    requests.delete(url + '/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_message_send_output_one(url, user_1, user_2, public_channel_1):
    """
    Testing a normal case (Authorised user sends a message in a channel)
    """
    arg_join = {
        'token'     : user_2['token'],
        'channel_id': public_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    message_str_one = "Welcome guys!"
    message_str_two = "Hello, I'm Jane!"

    new_message_1 = send_message(url, user_1, public_channel_1, message_str_one).json()
    new_message_2 = send_message(url, user_1, public_channel_1, message_str_two).json()

    arg_message_list = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }
    message_list = requests.get(url + 'channel/messages', params=arg_message_list).json()

    message_count = 0
    for msg in message_list['messages']:
        message_count += 1
        assert msg['message'] in (message_str_one, message_str_two)
    assert message_count == 2
    assert new_message_1['message_id'] != new_message_2['message_id']

    requests.delete(url + '/clear')

def test_message_send_output_two(url, user_1, user_2, user_3, user_4, public_channel_1):
    """
    Testing a longer case (multiple authorised users sending messages in a channel)
    """
    arg_join = {
        'token'     : user_2['token'],
        'channel_id': public_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    arg_join = {
        'token'     : user_3['token'],
        'channel_id': public_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    arg_join = {
        'token'     : user_4['token'],
        'channel_id': public_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    msg_str_1 = "Welcome guys!"
    msg_str_2 = "Hello, I'm Jane!"
    msg_str_3 = "sup"
    msg_str_4 = "Ok, let's start the project"
    msg_str_5 = "Join the call when you're ready guys"
    msg_str_6 = "sure, lemme get something to eat first"
    msg_str_7 = "Yeah aight, I'm joining."

    send_message(url, user_1, public_channel_1, msg_str_1)
    send_message(url, user_2, public_channel_1, msg_str_2)
    send_message(url, user_3, public_channel_1, msg_str_3)
    send_message(url, user_4, public_channel_1, msg_str_4)
    send_message(url, user_1, public_channel_1, msg_str_5)
    send_message(url, user_2, public_channel_1, msg_str_6)
    send_message(url, user_3, public_channel_1, msg_str_7)

    arg_message_list = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }
    message_list = requests.get(url + 'channel/messages', params=arg_message_list).json()

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
    requests.delete(url + '/clear')

#------------------------------------------------------------------------------#
#                                message_remove                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_message_remove_expired_token(url, user_1, user_2, user_3, user_4, default_message):
    """Testing invalid token for users which have logged out
    """
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_1['token']}).json()
    assert log_out['is_success'] == True
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_2['token']}).json()
    assert log_out['is_success'] == True
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_3['token']}).json()
    assert log_out['is_success'] == True
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_4['token']}).json()
    assert log_out['is_success'] == True

    remove_details = {
        'token'     : user_1['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == AccessError.code

    remove_details = {
        'token'     : user_2['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == AccessError.code

    remove_details = {
        'token'     : user_3['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == AccessError.code

    remove_details = {
        'token'     : user_4['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_message_remove_incorrect_token_type(url, user_1, default_message):
    """Testing invalid token data type handling
    """
    remove_details = {
        'token'     : 12,
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == AccessError.code

    remove_details = {
        'token'     : -12,
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == AccessError.code

    remove_details = {
        'token'     : 121.11,
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_message_remove_wrong_data_type(url, user_1, default_message):
    """Testing when wrong data types are used as input
    """
    remove_details = {
        'token'     : user_1['token'],
        'message_id': default_message['message_id'] - 1,
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == InputError.code

    remove_details = {
        'token'     : user_1['token'],
        'message_id': default_message['message_id'] + 1,
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_message_remove_message_not_existent(url, user_1, default_message):
    """Testing when message based on message_id does not exist
       and is subjected for deletion
    """
    remove_details = {
        'token'     : user_1['token'],
        'message_id': default_message['message_id'] + 1,
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == InputError.code

    remove_details = {
        'token'     : user_1['token'],
        'message_id': default_message['message_id'] - 1,
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == InputError.code

    remove_details = {
        'token'     : user_1['token'],
        'message_id': default_message['message_id'] + 100,
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == InputError.code

    remove_details = {
        'token'     : user_1['token'],
        'message_id': default_message['message_id'] - 100,
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_message_remove_message_deleted_already(url, user_1, default_message):
    """Testing when message based on message_id has been deleted already
       and is subjected for deletion again
    """
    remove_details = {
        'token'     : user_1['token'],
        'message_id': default_message['message_id'],
    }
    empty_dict = requests.delete(f'{url}/message/remove', json=remove_details).json()
    assert empty_dict == {}

    remove_details = {
        'token'     : user_1['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_message_remove_not_authorized_channel_owner(url, user_1, user_2, user_3, user_4, public_channel_1, default_message):
    """Testing when message based on message_id is called for deletion
       but the requester is not a channel_owner
    """
    invite_details = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'u_id'      : user_2['u_id'],
    }
    channel_return = requests.post(f'{url}/channel/invite', json=invite_details).json()
    assert channel_return == {}

    invite_details = {
        'token'     : user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'u_id'      : user_3['u_id'],
    }
    channel_return = requests.post(f'{url}/channel/invite', json=invite_details).json()
    assert channel_return == {}

    remove_details = {
        'token'     : user_2['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == AccessError.code

    remove_details = {
        'token'     : user_3['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == AccessError.code

    remove_details = {
        'token'     : user_4['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == AccessError.code

    remove_details = {
        'token'     : user_1['token'],
        'message_id': default_message['message_id'],
    }
    empty_dict = requests.delete(f'{url}/message/remove', json=remove_details).json()
    assert empty_dict == {}
    requests.delete(f'{url}/clear')

def test_message_remove_not_authorized_flockr_owner(url, user_1, user_2, user_3, user_4, default_message):
    """Testing when message based on message_id is called for deletion
       but the requester is not a flockr owner
    """
    remove_details = {
        'token'     : user_2['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == AccessError.code

    remove_details = {
        'token'     : user_3['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == AccessError.code

    remove_details = {
        'token'     : user_4['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_message_remove_authorized_owner_channel(url, user_1, public_channel_1):
    """Testing when message based on message_id is deleted by channel owner / flockr owner
    """
    message_1 = send_message(url, user_1, public_channel_1, 'I').json()
    message_2 = send_message(url, user_1, public_channel_1, 'am').json()
    message_3 = send_message(url, user_1, public_channel_1, 'really').json()
    message_4 = send_message(url, user_1, public_channel_1, 'hungry :(').json()

    """deleting message 1
    """
    on_list = False
    empty_dict = requests.delete(f'{url}/message/remove', json={
        'token'     : user_1['token'],
        'message_id': message_1['message_id'],
    }).json()
    assert empty_dict == {}

    message_data = requests.get(f'{url}/channel/messages', params={
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            on_list = True
    assert not on_list

    """deleting message 3
    """
    empty_dict = requests.delete(f'{url}/message/remove', json={
        'token'     : user_1['token'],
        'message_id': message_3['message_id'],
    }).json()
    assert empty_dict == {}
    message_data = requests.get(f'{url}/channel/messages', params={
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            on_list = True
    assert not on_list

    """deleting message 2
    """
    empty_dict = requests.delete(f'{url}/message/remove', json={
        'token'     : user_1['token'],
        'message_id': message_2['message_id'],
    }).json()
    assert empty_dict == {}
    message_data = requests.get(f'{url}/channel/messages', params={
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            on_list = True
    assert not on_list

    """deleting message 4
    """
    empty_dict = requests.delete(f'{url}/message/remove', json={
        'token'     : user_1['token'],
        'message_id': message_4['message_id'],
    }).json()
    assert empty_dict == {}
    message_profile = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            on_list = True
    assert not on_list
    requests.delete(f'{url}/clear')

def test_message_remove_authorized_flockr_owner(url, user_1, user_2, public_channel_2):
    """(Assumption Testing) Testing when message based on message_id is deleted by
       flockr owner who is not part of any channel
       (Assumption) First user to register is flockr owner
    """

    message_1 = send_message(url, user_2, public_channel_2, 'I').json()
    message_2 = send_message(url, user_2, public_channel_2, 'am').json()
    message_3 = send_message(url, user_2, public_channel_2, 'really').json()
    message_4 = send_message(url, user_2, public_channel_2, 'hungry :(').json()

    """deleting message 1
    """
    on_list = False
    remove_details = {
        'token'     : user_1['token'],
        'message_id': message_1['message_id'],
    }
    empty_dict = requests.delete(f'{url}/message/remove', json=remove_details).json()
    assert empty_dict == {}
    message_profile = {
        'token'     : user_2['token'],
        'channel_id': public_channel_2['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            on_list = True
    assert not on_list

    """deleting message 3
    """
    remove_details = {
        'token'     : user_1['token'],
        'message_id': message_3['message_id'],
    }
    empty_dict = requests.delete(f'{url}/message/remove', json=remove_details).json()
    assert empty_dict == {}
    message_profile = {
        'token'     : user_2['token'],
        'channel_id': public_channel_2['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            on_list = True
    assert not on_list

    """deleting message 2
    """
    remove_details = {
        'token'     : user_1['token'],
        'message_id': message_2['message_id'],
    }
    empty_dict = requests.delete(f'{url}/message/remove', json=remove_details).json()
    assert empty_dict == {}
    message_profile = {
        'token'     : user_2['token'],
        'channel_id': public_channel_2['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            on_list = True
    assert not on_list

    """deleting message 4
    """
    remove_details = {
        'token'     : user_1['token'],
        'message_id': message_4['message_id'],
    }
    empty_dict = requests.delete(f'{url}/message/remove', json=remove_details).json()
    assert empty_dict == {}
    message_profile = {
        'token'     : user_2['token'],
        'channel_id': public_channel_2['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            on_list = True
    assert not on_list
    requests.delete(f'{url}/clear')

def test_message_remove_authorized_user(url, user_1, user_2, public_channel_1):
    """Testing when user is not flockr owner or channel owner, and wants to delete
       his/her message which he/she sent earlier

       Also testing if this user is unable to delete any another messages
    """
    invite_details = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'u_id'      : user_2['u_id'],
    }
    channel_return = requests.post(f'{url}/channel/invite', json=invite_details).json()
    assert channel_return == {}

    message_1 = send_message(url, user_1, public_channel_1, 'Im user 1!').json()
    message_2 = send_message(url, user_2, public_channel_1, 'Im user 2!').json()
    message_3 = send_message(url, user_2, public_channel_1, 'Okay bye!!').json()

    """deleting message 2
    """
    on_list = False
    empty_dict = requests.delete(f'{url}/message/remove', json={
        'token'     : user_2['token'],
        'message_id': message_2['message_id'],
    }).json()
    assert empty_dict == {}
    message_data = requests.get(f'{url}/channel/messages', params={
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_2['message_id']:
            on_list = True
    assert not on_list

    """deleting message 3
    """
    empty_dict = requests.delete(f'{url}/message/remove', json={
        'token'     : user_1['token'],
        'message_id': message_3['message_id'],
    }).json()
    assert empty_dict == {}
    message_data = requests.get(f'{url}/channel/messages', params={
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_3['message_id']:
            on_list = True
    assert not on_list

    error = requests.delete(f'{url}/message/remove', json={
        'token'     : user_2['token'],
        'message_id': message_1['message_id'],
    })
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

#------------------------------------------------------------------------------#
#                                message_edit                                  #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_message_edit_expired_token(url, user_1, user_2, user_3, user_4, public_channel_1, default_message):
    """Testing invalid token for users which have logged out
    """
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_1['token']}).json()
    assert log_out['is_success'] == True
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_2['token']}).json()
    assert log_out['is_success'] == True
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_3['token']}).json()
    assert log_out['is_success'] == True
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_4['token']}).json()
    assert log_out['is_success'] == True

    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == AccessError.code

    message_info = {
        'token': user_2['token'],
        'message_id': default_message['message_id'],
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == AccessError.code

    message_info = {
        'token': user_3['token'],
        'message_id': default_message['message_id'],
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == AccessError.code

    message_info = {
        'token': user_4['token'],
        'message_id': default_message['message_id'],
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_message_edit_incorrect_token_type(url, user_1, default_message):
    """Testing invalid token data type handling
    """
    message_info = {
        'token': 12,
        'message_id': default_message['message_id'],
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == AccessError.code

    message_info = {
        'token': -12,
        'message_id': default_message['message_id'],
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == AccessError.code

    message_info = {
        'token': 121.11,
        'message_id': default_message['message_id'],
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_message_edit_wrong_data_type(url, user_1, default_message):
    """Testing when wrong data types are used as input
    """
    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'] - 1,
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == InputError.code

    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'] + 1,
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_message_edit_more_than_1000_char(url, user_1, default_message):
    """
    Testing when the message to edit is replaced with 1000 characters new message
    """
    message_str_1 = ("Hello" * 250)
    message_str_2 = ("HI " * 500)
    message_str_3 = ("My name is blah" * 100)

    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'message': message_str_1,
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == InputError.code

    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'message': message_str_2,
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == InputError.code

    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'message': message_str_3,
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_message_edit_integer_message(url, user_1, default_message):
    """Testing when message data type is an integer
    """
    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'message': 0,
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == InputError.code

    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'message': -1,
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == InputError.code

    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'message': 100,
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == InputError.code

    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'message': 127.66,
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_message_edit_deleted_message(url, user_1, default_message):
    """Testing when message based on message_id does not exist
       and is subjected for editing
    """
    remove_details = {
        'token'     : user_1['token'],
        'message_id': default_message['message_id'],
    }
    empty_dict = requests.delete(f'{url}/message/remove', json=remove_details).json()
    assert empty_dict == {}

    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'message': 'hey',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_message_edit_not_authorized_channel_owner(url, user_1, user_2, user_3, user_4, public_channel_1, default_message):
    """Testing when message based on message_id is called for editing
       but the requester is not a channel_owner
    """
    invite_details = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'u_id'      : user_2['u_id'],
    }
    channel_return = requests.post(f'{url}/channel/invite', json=invite_details).json()
    assert channel_return == {}

    invite_details = {
        'token'     : user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'u_id'      : user_3['u_id'],
    }
    channel_return = requests.post(f'{url}/channel/invite', json=invite_details).json()
    assert channel_return == {}

    message_info = {
        'token': user_2['token'],
        'message_id': default_message['message_id'],
        'message': 'lets edit!',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == AccessError.code

    message_info = {
        'token': user_3['token'],
        'message_id': default_message['message_id'],
        'message': 'lets edit!',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == AccessError.code

    message_info = {
        'token': user_4['token'],
        'message_id': default_message['message_id'],
        'message': 'lets edit!',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_message_edit_not_authorized_flockr_owner(url, user_1, user_2, user_3, user_4, public_channel_1, default_message):
    """Testing when message based on message_id is called for editing
       but the requester is not a flockr owner
    """
    requests.delete(f'{url}/clear')

    message_info = {
        'token': user_2['token'],
        'message_id': default_message['message_id'],
        'message': 'lets edit!',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == AccessError.code

    message_info = {
        'token': user_3['token'],
        'message_id': default_message['message_id'],
        'message': 'lets edit!',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == AccessError.code

    message_info = {
        'token': user_4['token'],
        'message_id': default_message['message_id'],
        'message': 'lets edit!',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_message_edit_authorized_owner_channel(url, user_1, public_channel_1, default_message):
    """Testing when message based on message_id is edited by channel owner / flockr owner
    """
    on_list = False
    message_profile = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == default_message['message_id']:
            if messages['message'] == "Hey channel!":
                on_list = True
    assert on_list

    edited = False
    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'message': 'not hungry :)',
    }
    empty_dict = requests.put(f'{url}/message/edit', json=message_info).json()
    assert empty_dict == {}
    message_profile = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == default_message['message_id']:
            if messages['message'] == 'not hungry :)':
                edited = True
    assert edited
    requests.delete(f'{url}/clear')

def test_message_edit_authorized_flockr_owner(url):
    """(Assumption Testing) Testing when message based on message_id is edited by
       flockr owner who is not part of any channel
       (Assumption) First user to register is flockr owner
    """
    requests.delete(f'{url}/clear')
    
    user_information = {
        'email': 'jacobcreek@gmail.com',
        'password': 'password',
        'name_first': 'Jacob',
        'name_last': 'Creek',
    }
    user_1 = requests.post(f'{url}/auth/register', json=user_information).json()

    user_information = {
        'email': 'jinperry@gmail.com',
        'password': 'password',
        'name_first': 'Jin',
        'name_last': 'Perry',
    }
    user_2 = requests.post(f'{url}/auth/register', json=user_information).json()

    channel_profile = {
        'token'    : user_2['token'],
        'name'     : 'Group 1',
        'is_public': True,
    }
    default_channel = requests.post(f'{url}/channels/create', json=channel_profile).json()
    
    message_details = {
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
        'message'   : 'hungry :(',
    }
    message_1 = requests.post(f'{url}/message/send', json=message_details).json()

    on_list = False
    message_profile = {
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            if messages['message'] == 'hungry :(':
                on_list = True
    assert on_list

    edited = False
    message_info = {
        'token': user_1['token'],
        'message_id': message_1['message_id'],
        'message': 'not hungry :)',
    }
    empty_dict = requests.put(f'{url}/message/edit', json=message_info).json()
    assert empty_dict == {}
    message_profile = {
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            if messages['message'] == 'not hungry :)':
                edited = True
    assert edited
    requests.delete(f'{url}/clear')

def test_message_edit_empty_string(url, user_1, user_2, public_channel_1):
    """Testing when user is not flockr owner or channel owner, and wants to edit
       his/her message which he/she sent earlier

       Also testing if this user is unable to edit any another messages
    """
    message_details = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'message'   : 'I',
    }
    message_1 = requests.post(f'{url}/message/send', json=message_details).json()

    message_details = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'message'   : 'am',
    }
    message_2 = requests.post(f'{url}/message/send', json=message_details).json()

    message_details = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'message'   : 'really',
    }
    message_3 = requests.post(f'{url}/message/send', json=message_details).json()

    message_details = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'message'   : 'hungry :(',
    }
    message_4 = requests.post(f'{url}/message/send', json=message_details).json()

    on_list = False
    """deleting message 1
    """
    message_info = {
        'token': user_1['token'],
        'message_id': message_1['message_id'],
        'message': '',
    }
    empty_dict = requests.put(f'{url}/message/edit', json=message_info).json()
    assert empty_dict == {}
    message_profile = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            on_list = True
    assert not on_list

    """deleting message 3
    """
    message_info = {
        'token': user_1['token'],
        'message_id': message_3['message_id'],
        'message': '',
    }
    empty_dict = requests.put(f'{url}/message/edit', json=message_info).json()
    assert empty_dict == {}
    message_profile = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_3['message_id']:
            on_list = True
    assert not on_list

    """deleting message 2
    """
    message_info = {
        'token': user_1['token'],
        'message_id': message_2['message_id'],
        'message': '',
    }
    empty_dict = requests.put(f'{url}/message/edit', json=message_info).json()
    assert empty_dict == {}
    message_profile = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_2['message_id']:
            on_list = True
    assert not on_list

    """deleting message 4
    """
    message_info = {
        'token': user_1['token'],
        'message_id': message_4['message_id'],
        'message': '',
    }
    empty_dict = requests.put(f'{url}/message/edit', json=message_info).json()
    assert empty_dict == {}
    message_profile = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_4['message_id']:
            on_list = True
    assert not on_list

    message_info = {
        'token': user_2['token'],
        'message_id': message_1['message_id'],
        'message': 'I can edit admin!',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)   
    error.status_code == AccessError.code 
    requests.delete(f'{url}/clear')

def test_message_edit_authorized_user(url, user_1, user_2, public_channel_1):
    """Testing when user is not flockr owner or channel owner, and wants to edit
       his/her message which he/she sent earlier

       Also testing if this user is unable to edit any another messages
    """
    invite_details = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'u_id'      : user_2['u_id'],
    }
    channel_return = requests.post(f'{url}/channel/invite', json=invite_details).json()
    assert channel_return == {}

    message_1 = send_message(url, user_1, public_channel_1, 'Im user 1!').json()
    message_2 = send_message(url, user_2, public_channel_1, 'Im user 2!').json()
    message_3 = send_message(url, user_2, public_channel_1, 'Okay bye!!').json()

    """editing message 2
    """
    on_list = False
    message_info = {
        'token': user_2['token'],
        'message_id': message_2['message_id'],
        'message': "Nice to meet you!",
    }
    empty_dict = requests.put(f'{url}/message/edit', json=message_info).json()
    assert empty_dict == {}
    message_profile = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_2['message_id']:
            if messages['message'] == 'Nice to meet you!':
                on_list = True
    assert on_list

    on_list = False
    message_info = {
        'token': user_1['token'],
        'message_id': message_3['message_id'],
        'message': "I can edit!!!",
    }
    empty_dict = requests.put(f'{url}/message/edit', json=message_info).json()
    assert empty_dict == {}
    message_profile = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_3['message_id']:
            if messages['message'] == 'I can edit!!!':
                on_list = True
    assert on_list

    on_list = False
    message_info = {
        'token': user_2['token'],
        'message_id': message_3['message_id'],
        'message': "",
    }
    empty_dict = requests.put(f'{url}/message/edit', json=message_info).json()
    assert empty_dict == {}
    message_profile = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_3['message_id']:
            on_list = True
    assert not on_list

    message_info = {
        'token': user_2['token'],
        'message_id': message_1['message_id'],
        'message': "I can edit admin!",
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

#------------------------------------------------------------------------------#
#                               message/sendlater                              #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_message_send_later_more_than_1000_char(url, user_1, public_channel_1):
    """
    Testing when the message sent is over 1000 characters
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    resp = send_message_later(url, user_1, public_channel_1, ("Hello" * 250), curr_time + 7)
    assert resp.status_code == InputError.code
    resp = send_message_later(url, user_1, public_channel_1, ("HI " * 500), curr_time + 7)
    assert resp.status_code == InputError.code
    resp = send_message_later(url, user_1, public_channel_1, ("My name is blah" * 100), curr_time + 7)
    assert resp.status_code == InputError.code
    requests.delete(url + '/clear')

def test_message_send_later_auth_user_not_in_channel(url, user_1, user_2, public_channel_1):
    """
    Testing when the authorised user has not joined the channel they
    are trying to post to
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    resp = send_message_later(url, user_2, public_channel_1, "Hello", curr_time + 7)
    assert resp.status_code == AccessError.code
    requests.delete(url + '/clear')

def test_message_send_later_expired_token(url, user_1, user_2, user_3, user_4, public_channel_1, default_message):
    """
    Testing invalid token for users which have logged out
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_1['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_2['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_3['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_4['token']}).json()
    assert log_out['is_success']

    res_err = send_message_later(url, user_1, public_channel_1, "Hello", curr_time + 7)
    assert res_err.status_code == AccessError.code

    res_err = send_message_later(url, user_2, public_channel_1, "Hello", curr_time + 7)
    assert res_err.status_code == AccessError.code

    res_err = send_message_later(url, user_3, public_channel_1, "Hello", curr_time + 7)
    assert res_err.status_code == AccessError.code

    res_err = send_message_later(url, user_4, public_channel_1, "Hello", curr_time + 7)
    assert res_err.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_message_send_later_incorrect_token_type(url, user_1, public_channel_1, default_message):
    """
    Testing invalid token data type handling
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    arg_message = {
        'token'     : 12,
        'channel_id': public_channel_1['channel_id'],
        'message'   : "Hello",
        'time_sent' : curr_time + 7,
    }
    res_err = requests.post(url + 'message/sendlater', json=arg_message)
    assert res_err.status_code == AccessError.code

    arg_message = {
        'token'     : -12,
        'channel_id': public_channel_1['channel_id'],
        'message'   : "Hello",
        'time_sent' : curr_time + 7,
    }
    res_err = requests.post(url + 'message/sendlater', json=arg_message)
    assert res_err.status_code == AccessError.code

    arg_message = {
        'token'     : 121.11,
        'channel_id': public_channel_1['channel_id'],
        'message'   : "Hello",
        'time_sent' : curr_time + 7,
    }
    res_err = requests.post(url + 'message/sendlater', json=arg_message)
    assert res_err.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_message_send_later_channel_id(url, user_1, public_channel_1):
    """
    Testing when an invalid channel_id is used as a parameter
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    arg_message = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'] + 7,
        'message'   : "Hello",
        'time_sent' : curr_time + 7,
    }
    res_err = requests.post(url + 'message/sendlater', json=arg_message)
    assert res_err.status_code == InputError.code
    requests.delete(url + '/clear')

def test_message_send_later_valid_token(url, user_1, public_channel_1):
    """
    Testing if token is valid
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    arg_message = {
        'token'     : -1,
        'channel_id': public_channel_1['channel_id'],
        'message'   : "Hello",
        'time_sent' : curr_time + 7,
    }
    res_err = requests.post(url + 'message/sendlater', json=arg_message)
    assert res_err.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_message_send_later_output_empty_str(url, user_1, user_2, public_channel_1):
    """
    Testing an empty string message (Authorised user sends a message in a channel)
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    arg_join = {
        'token'     : user_2['token'],
        'channel_id': public_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    res_err = send_message_later(url, user_2, public_channel_1, "", curr_time + 7)
    assert res_err.status_code == InputError.code

    requests.delete(url + '/clear')

def test_message_send_later_time_is_in_past(url, user_1, public_channel_1):
    """
    Testing when time sent is a time in the past
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    res_err = send_message_later(url, user_1, public_channel_1, "Bye", curr_time - 7)
    assert res_err.status_code == InputError.code
    requests.delete(url + '/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_message_send_later_time_sent_is_curr_time(url, user_1, user_2, public_channel_1):
    """
    Testing a case where time sent is the current time
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    arg_join = {
        'token'     : user_2['token'],
        'channel_id': public_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    send_message_later(url, user_1, public_channel_1, "Hi", curr_time).json()

    arg_message_list = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }
    message_list = requests.get(url + 'channel/messages', params=arg_message_list).json()

    message_count = 0
    for msg in message_list['messages']:
        message_count += 1
        assert msg['time_created'] == curr_time
    assert message_count == 1
    requests.delete(url + '/clear')

def test_message_send_later_output_one(url, user_1, user_2, public_channel_1):
    """
    Testing a normal case (Authorised user sends a delayed message in a channel)
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    arg_join = {
        'token'     : user_2['token'],
        'channel_id': public_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    message_str_one = "Welcome guys!"
    message_str_two = "Hello, I'm Jane!"

    new_message_1 = send_message_later(url, user_1, public_channel_1, message_str_one, curr_time + 7).json()
    new_message_2 = send_message_later(url, user_1, public_channel_1, message_str_two, curr_time + 17).json()
    time.sleep(18)

    arg_message_list = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }
    message_list = requests.get(url + 'channel/messages', params=arg_message_list).json()

    message_count = 0
    msg_time_list = []
    for msg in message_list['messages']:
        message_count += 1
        msg_time_list.append(msg['time_created'])
        assert msg['message'] in (message_str_one, message_str_two)
    assert message_count == 2
    assert msg_time_list[1] in range(curr_time + 7 - DELAY, curr_time + 7 + DELAY)
    assert msg_time_list[0] in range(curr_time + 17 - DELAY, curr_time + 17 + DELAY)
    assert new_message_1['message_id'] != new_message_2['message_id']
    requests.delete(url + '/clear')

def test_message_send_later_output_two(url, user_1, user_2, user_3, user_4, public_channel_1):
    """
    Testing a longer case (multiple authorised users sending messages in a channel)
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    arg_join = {
        'token'     : user_2['token'],
        'channel_id': public_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    arg_join = {
        'token'     : user_3['token'],
        'channel_id': public_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    arg_join = {
        'token'     : user_4['token'],
        'channel_id': public_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    msg_str_1 = "Welcome guys!"
    msg_str_2 = "Hello, I'm Jane!"
    msg_str_3 = "sup"
    msg_str_4 = "Ok, let's start the project"
    msg_str_5 = "Join the call when you're ready guys"
    msg_str_6 = "sure, lemme get something to eat first"
    msg_str_7 = "Yeah aight, I'm joining."

    send_message_later(url, user_1, public_channel_1, msg_str_1, curr_time + 1)
    send_message_later(url, user_2, public_channel_1, msg_str_2, curr_time + 2)
    send_message_later(url, user_3, public_channel_1, msg_str_3, curr_time + 3)
    send_message_later(url, user_4, public_channel_1, msg_str_4, curr_time + 4)
    send_message_later(url, user_1, public_channel_1, msg_str_5, curr_time + 5)
    send_message_later(url, user_2, public_channel_1, msg_str_6, curr_time + 6)
    send_message_later(url, user_3, public_channel_1, msg_str_7, curr_time + 7)
    time.sleep(8)

    arg_message_list = {
        'token'     : user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start'     : 0,
    }
    message_list = requests.get(url + 'channel/messages', params=arg_message_list).json()

    message_count = 0
    message_confirmed = False
    check_unique_msg_id = []
    msg_time_list = []
    for msg in message_list['messages']:
        if msg['message'] in {msg_str_1, msg_str_2, msg_str_3,
                              msg_str_4, msg_str_5, msg_str_6, msg_str_7}:
            message_confirmed = True
        message_count += 1
        check_unique_msg_id.append(msg['message_id'])
        msg_time_list.append(msg['time_created'])
    assert message_count == 7
    assert message_confirmed
    assert len(set(check_unique_msg_id)) == 7
    assert msg_time_list[6] in range(curr_time + 1 - DELAY, curr_time + 1 + DELAY)
    assert msg_time_list[5] in range(curr_time + 2 - DELAY, curr_time + 2 + DELAY)
    assert msg_time_list[4] in range(curr_time + 3 - DELAY, curr_time + 3 + DELAY)
    assert msg_time_list[3] in range(curr_time + 4 - DELAY, curr_time + 4 + DELAY)
    assert msg_time_list[2] in range(curr_time + 5 - DELAY, curr_time + 5 + DELAY)
    assert msg_time_list[1] in range(curr_time + 6 - DELAY, curr_time + 6 + DELAY)
    assert msg_time_list[0] in range(curr_time + 7 - DELAY, curr_time + 7 + DELAY)
    requests.delete(url + '/clear')

#------------------------------------------------------------------------------#
#                                 message/react                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_react_input_message_id_1(url, user_1, public_channel_1):
    """Testing invalid message_id when a channel has no messages
    """
    data_1 = {
        'token': user_1['token'],
        'message_id': 1,
        'react_id': THUMBS_UP,
    }
    data_2 = {
        'token': user_1['token'],
        'message_id': 2,
        'react_id': THUMBS_UP,
    }
    data_3 = {
        'token': user_1['token'],
        'message_id': 0,
        'react_id': THUMBS_UP,
    }
    result_1 = requests.post(f"{url}/message/react", json = data_1).json()
    result_2 = requests.post(f"{url}/message/react", json = data_2).json()
    result_3 = requests.post(f"{url}/message/react", json = data_3).json()
    assert result_1.status_code == InputError.code
    assert result_2.status_code == InputError.code
    assert result_3.status_code == InputError.code


def test_react_input_message_id_2(url, user_1, public_channel_1, default_message):
    """Testing invalid message_id when a channel has a message
    """
    data_1 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'] + 1,
        'react_id': THUMBS_UP,
    }
    data_2 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'] - 1,
        'react_id': THUMBS_UP,
    }
    result_1 = requests.post(f"{url}/message/react", json = data_1).json()
    result_2 = requests.post(f"{url}/message/react", json = data_2).json()
    assert result_1.status_code == InputError.code
    assert result_2.status_code == InputError.code

def test_react_input_react_id(url, user_1, public_channel_1, default_message):
    """Test when the react_id is invalid
    """
    data_1 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'react_id': 0,
    }
    data_2 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'react_id': -1,
    }
    data_3 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'react_id': -1,
    }
    data_4 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'react_id': 1000,
    }
    result_1 = requests.post(f"{url}/message/react", json = data_1).json()
    result_2 = requests.post(f"{url}/message/react", json = data_2).json()
    result_3 = requests.post(f"{url}/message/react", json = data_3).json()
    result_4 = requests.post(f"{url}/message/react", json = data_4).json()
    assert result_1.status_code == InputError.code
    assert result_2.status_code == InputError.code
    assert result_3.status_code == InputError.code
    assert result_4.status_code == InputError.code

def test_react_input_reacted_message(url, user_1, public_channel_1, thumbs_up_defualt_message):
    """Test if the message with message_id already contains an active React with
    react_id from the authorised user (thumbs up)
    """
    data_1 = {
        'token': user_1['token'],
        'message_id': thumbs_up_default_message['id'],
        'react_id': THUMBS_UP,
    }
    result_1 = requests.post(f"{url}/message/react", json = data_1).json()
    assert result_1.status_code == InputError.code

def test_react_input_reacted_message(url, user_1, public_channel_1, thumbs_down_default_message):
    """Test if the message with message_id already contains an active React with
    react_id from the authorised user (thumbs down)
    """
    data_1 = {
        'token': user_1['token'],
        'message_id': thumbs_up_default_message['id'],
        'react_id': THUMBS_DOWN,
    }
    result_1 = requests.post(f"{url}/message/react", json = data_1).json()
    assert result_1.status_code == InputError.code

def test_react_access_invalid_token(url, user_1, public_channel_1, default_message, logout_user_1):
    """Test if token is invalid
    """
    data_1 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'react_id': THUMBS_UP,
    }
    data_2 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'react_id': THUMBS_DOWN,
    }
    result_1 = requests.post(f"{url}/message/react", json = data_1).json()
    result_2 = requests.post(f"{url}/message/react", json = data_2).json()
    assert result_1.status_code == InputError.code
    assert result_2.status_code == InputError.code

def test_react_access_user_not_in_channel(url, user_1, user_2, public_channel_1, default_message):
    """(Assumption testing): testing when a flockr member not in the channel 
    calling message_react will raise an AccessError.
    """
    data_1 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'react_id': THUMBS_UP,
    }
    data_2 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'react_id': THUMBS_DOWN,
    }
    result_1 = requests.post(f"{url}/message/react", json = data_1).json()
    result_2 = requests.post(f"{url}/message/react", json = data_2).json()
    assert result_1.status_code == AccessError.code
    assert result_2.status_code == AccessError.code
    
#?------------------------------ Output Testing ------------------------------?#

def test_react_output_basic_react_thumbs_up(url, user_1, public_channel_1, thumbs_up_default_message):
    """Basic test whether a message has indeed been reacted by the user who created
    the message (thumbs up).
    """
    data_1 = {
        'token': user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }
    message_details = requests.get(f"{url}/channel/messages", params = data_1).json()
    assert len(message_details['reacts']) == 1
    assert message_details['reacts'][0]['react_id'] == THUMBS_UP
    assert len(message_details['reacts'][0]['u_ids']) == 1
    assert message_details['reacts'][0]['u_ids'] == [user_1['u_id']]
    assert message_details['reacts'][0]['is_this_user_reacted'] == True
    

def test_react_output_basic_react_thumbs_down(url, user_1, public_channel_1, thumbs_down_default_message):
    """Basic test whether a message has indeed been reacted by the user who created
    the message (thumbs up).
    """
    data_1 = {
        'token': user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }
    message_details = requests.get(f"{url}/channel/messages", params = data_1).json()
    assert len(message_details['reacts']) == 1
    assert message_details['reacts'][0]['react_id'] == THUMBS_DOWN
    assert len(message_details['reacts'][0]['u_ids']) == 1
    assert message_details['reacts'][0]['u_ids'] == [user_1['u_id']]
    assert message_details['reacts'][0]['is_this_user_reacted'] == True
    

def test_react_output_another_user_thumbs_up(url, user_1, user_2, public_channel_1, default_message):
    """Test if another user can react a message created by another user (thumbs up).
    """
    data_inv = {
        'token': user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'id': user_2['u_id'],
    }
    data_1 = {
        'token': user_2['token'],
        'message_id': default_message['message_id'],
        'react_id': THUMBS_UP,
    }
    data_react
    requests.post(f"{url}/channel/invite", json = data_inv)
    requests.post(f"{url}/message/react", json = data_react)
    data_1 = {
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }
    message_details = requests.get(f"{url}/channel/messages", params = data_1).json()
    message_details = message_details['messages']
    assert len(message_details['reacts']) == 1
    assert message_details['reacts'][0]['react_id'] == THUMBS_UP
    assert len(message_details['reacts'][0]['u_ids']) == 1
    assert message_details['reacts'][0]['u_ids'] == [user_2['u_id']]
    assert message_details['reacts'][0]['is_this_user_reacted'] == True

def test_react_output_another_user_thumbs_down(url, user_1, user_2, public_channel_1, default_message):
    """Test if another user can react a message created by another user (thumbs down).
    """
    data_inv = {
        'token': user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'id': user_2['u_id'],
    }
    data_1 = {
        'token': user_2['token'],
        'message_id': default_message['message_id'],
        'react_id': THUMBS_DOWN,
    }
    data_react
    requests.post(f"{url}/channel/invite", json = data_inv)
    requests.post(f"{url}/message/react", json = data_react)
    data_1 = {
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }
    message_details = requests.get(f"{url}/channel/messages", params = data_1).json()
    message_details = message_details['messages']
    assert len(message_details['reacts']) == 1
    assert message_details['reacts'][0]['react_id'] == THUMBS_DOWN
    assert len(message_details['reacts'][0]['u_ids']) == 1
    assert message_details['reacts'][0]['u_ids'] == [user_2['u_id']]
    assert message_details['reacts'][0]['is_this_user_reacted'] == True
    

#------------------------------------------------------------------------------#
#                                message/unreact                               #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_authorised_to_unreact(url, user_1, public_channel_1):
    """
    Test for logged out user trying to unreact to a message.
    """
    msg_1 = send_message(url, user_1, public_channel_1, "Hello").json()
    helper_message_react(url, user_1, msg_1['message_id'], THUMBS_UP)

    requests.post(f"{url}/auth/logout", json={
        'token': user_1['token']
    })

    ret_unreact = helper_message_unreact(url, user_1, msg_1['message_id'], THUMBS_UP)
    assert ret_unreact.status_code == AccessError.code
    
    requests.delete(url + '/clear')

def test_nonmember_unreact(url, user_2, user_3, public_channel_2):
    """
    Test for users outside of the channel that the message is in trying to unreact that message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_3['token'],
        'channel_id': public_channel_2['channel_id']
    })

    msg_1 = send_message(url, user_2, public_channel_2, "Hello").json()
    helper_message_react(url, user_3, msg_1['message_id'], THUMBS_UP)

    requests.post(f"{url}/channel/leave", json={
        'token': user_3['token'],
        'channel_id': public_channel_2['channel_id']
    })

    ret_unreact = helper_message_unreact(url, user_3, msg_1['message_id'], THUMBS_UP)
    assert ret_unreact.status_code == AccessError.code
    
    requests.delete(url + '/clear')

def test_valid_message_id_unreact(url, user_1, public_channel_1):
    """
    Test if the message exists or not.
    """
    msg_1 = send_message(url, user_1, public_channel_1, "Hello").json()
    helper_message_react(url, user_1, msg_1['message_id'], THUMBS_UP)

    ret_unreact_1 = helper_message_unreact(url, user_1, msg_1['message_id'] + 1, THUMBS_UP)
    assert ret_unreact_1.status_code == InputError.code
    ret_unreact_2 = helper_message_unreact(url, user_1, msg_1['message_id'] - 1, THUMBS_UP)
    assert ret_unreact_2.status_code == InputError.code
    ret_unreact_3 = helper_message_unreact(url, user_1, msg_1['message_id'] + 500, THUMBS_UP)
    assert ret_unreact_3.status_code == InputError.code

    requests.delete(url + '/clear')
    

def test_valid_react_id_unreact(url, user_1, public_channel_1):
    """
    Test if the specific react exists.
    """
    msg_1 = send_message(url, user_1, public_channel_1, "Hello").json()
    helper_message_react(url, user_1, msg_1['message_id'], THUMBS_UP)

    ret_unreact_1 = helper_message_unreact(url, user_1, msg_1['message_id'], 3)
    assert ret_unreact_1.status_code == InputError.code
    ret_unreact_2 = helper_message_unreact(url, user_1, msg_1['message_id'], -1)
    assert ret_unreact_2.status_code == InputError.code
    ret_unreact_3 = helper_message_unreact(url, user_1, msg_1['message_id'], -13)
    assert ret_unreact_3.status_code == InputError.code
    ret_unreact_4 = helper_message_unreact(url, user_1, msg_1['message_id'], 21)
    assert ret_unreact_4.status_code == InputError.code

    requests.delete(url + '/clear')

def test_message_already_unreacted(url, user_1, user_2, public_channel_1):
    """
    Test for unreacting to a message that is already unreacted to.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = send_message(url, user_1, public_channel_1, "Hello").json()
    msg_2 = send_message(url, user_2, public_channel_1, "Hola").json()
    helper_message_react(url, user_2, msg_2['message_id'], THUMBS_UP)

    ret_unreact_1 = helper_message_unreact(url, user_2, msg_1['message_id'], THUMBS_UP)
    assert ret_unreact_1.status_code == InputError.code
    ret_unreact_2 = helper_message_unreact(url, user_2, msg_2['message_id'], THUMBS_DOWN)
    assert ret_unreact_2.status_code == InputError.code

    requests.delete(url + '/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_unreact_correct_message_thumbsup(url, user_1, user_2, public_channel_1):
    """
    Basic test for unreacting a react_id in a message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    send_message(url, user_1, public_channel_1, "Hello").json()
    msg_2 = send_message(url, user_1, public_channel_1, "Hola").json()
    msg_3 = send_message(url, user_2, public_channel_1, "Mate").json()
    send_message(url, user_2, public_channel_1, "What?!").json()

    helper_message_react(url, user_1, msg_2['message_id'], THUMBS_UP)
    helper_message_react(url, user_1, msg_3['message_id'], THUMBS_UP)
    helper_message_react(url, user_2, msg_3['message_id'], THUMBS_UP)

    helper_message_unreact(url, user_1, msg_3['message_id'], THUMBS_UP)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    count_msg_unreacted_1 = 0
    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] == THUMBS_UP:
                if user_1['u_id'] not in react['u_ids'] and (curr_message['message'] in [
                    'Hello', 'Mate', 'What?!'
                ]):
                    count_msg_unreacted_1 += 1
    assert count_msg_unreacted_1 == 3
    
    requests.delete(url + '/clear')

def test_unreact_correct_message_thumbsdown(url, user_1, user_2, public_channel_1):
    """
    Basic test for unreacting a react_id in a message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = send_message(url, user_1, public_channel_1, "Hola").json()
    msg_2 = send_message(url, user_1, public_channel_1, "Mate").json()

    helper_message_react(url, user_2, msg_1['message_id'], THUMBS_DOWN)
    helper_message_react(url, user_2, msg_2['message_id'], THUMBS_DOWN)

    helper_message_unreact(url, user_2, msg_2['message_id'], THUMBS_DOWN)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    count_msg_unreacted_1 = 0
    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] == THUMBS_DOWN:
                if user_2['u_id'] not in react['u_ids'] and (curr_message['message'] == 'Mate'):
                    count_msg_unreacted_1 += 1
    assert count_msg_unreacted_1 == 1

    requests.delete(url + '/clear')

def test_unreact_owned_messages(url, user_1, user_2, public_channel_1):
    """
    Test for unreacting owned messages.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = send_message(url, user_1, public_channel_1, "Hola").json()
    msg_2 = send_message(url, user_2, public_channel_1, "Mate").json()
    msg_3 = send_message(url, user_2, public_channel_1, "Hi").json()
    msg_4 = send_message(url, user_2, public_channel_1, "What?").json()

    helper_message_react(url, user_2, msg_2['message_id'], THUMBS_UP)
    helper_message_react(url, user_2, msg_3['message_id'], THUMBS_UP)
    helper_message_react(url, user_2, msg_4['message_id'], THUMBS_UP)
    helper_message_react(url, user_1, msg_1['message_id'], THUMBS_UP)

    helper_message_unreact(url, user_2, msg_2['message_id'], THUMBS_UP)
    helper_message_unreact(url, user_2, msg_3['message_id'], THUMBS_UP)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    count_msg_unreacted_1 = 0
    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] == THUMBS_UP:
                if user_2['u_id'] not in react['u_ids'] and (curr_message['message'] in [
                    'Hola', 'Hi', 'Mate'
                    ]):
                    count_msg_unreacted_1 += 1
    assert count_msg_unreacted_1 == 3

    requests.delete(url + '/clear')

def test_unreact_other_messages(url, user_1, user_2, user_3, public_channel_3):
    """
    Test for unreacting other user's messages.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_1['token'],
        'channel_id': public_channel_3['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_3['channel_id']
    })

    msg_1 = send_message(url, user_1, public_channel_3, "Hola").json()
    msg_2 = send_message(url, user_1, public_channel_3, "Mate").json()
    msg_3 = send_message(url, user_2, public_channel_3, "Hi").json()
    msg_4 = send_message(url, user_2, public_channel_3, "What?").json()
    msg_5 = send_message(url, user_2, public_channel_3, "OKAY").json()

    helper_message_react(url, user_3, msg_1['message_id'], THUMBS_UP)
    helper_message_react(url, user_3, msg_2['message_id'], THUMBS_UP)
    helper_message_react(url, user_3, msg_3['message_id'], THUMBS_UP)
    helper_message_react(url, user_3, msg_5['message_id'], THUMBS_UP)

    helper_message_unreact(url, user_3, msg_2['message_id'], THUMBS_UP)
    helper_message_unreact(url, user_3, msg_3['message_id'], THUMBS_UP)
    helper_message_unreact(url, user_3, msg_5['message_id'], THUMBS_UP)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_3['channel_id'],
        'start': 0,
    }).json()

    count_msg_unreacted_1 = 0
    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] == THUMBS_UP:
                if user_3['u_id'] not in react['u_ids'] and (curr_message['message'] in [
                    'Hi', 'Mate', 'What?', 'OKAY'
                    ]):
                    count_msg_unreacted_1 += 1
    assert count_msg_unreacted_1 == 4

    requests.delete(url + '/clear')

def test_unreact_multiple_messages(url, user_1, user_2, user_3, public_channel_2):
    """
    Test for unreacting multiple messages.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_1['token'],
        'channel_id': public_channel_2['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_3['token'],
        'channel_id': public_channel_2['channel_id']
    })

    msg_1 = send_message(url, user_1, public_channel_2, "Hola").json()
    msg_2 = send_message(url, user_1, public_channel_2, "Mate").json()
    msg_3 = send_message(url, user_1, public_channel_2, "Hi").json()
    msg_4 = send_message(url, user_1, public_channel_2, "What?").json()
    msg_5 = send_message(url, user_2, public_channel_2, "OKAY").json()
    msg_6 = send_message(url, user_2, public_channel_2, "I").json()
    msg_7 = send_message(url, user_2, public_channel_2, "Am").json()
    msg_8 = send_message(url, user_2, public_channel_2, "Good").json()

    helper_message_react(url, user_3, msg_1['message_id'], THUMBS_UP)
    helper_message_react(url, user_3, msg_2['message_id'], THUMBS_UP)
    helper_message_react(url, user_3, msg_4['message_id'], THUMBS_UP)
    helper_message_react(url, user_3, msg_5['message_id'], THUMBS_UP)
    helper_message_react(url, user_3, msg_6['message_id'], THUMBS_UP)
    helper_message_react(url, user_3, msg_7['message_id'], THUMBS_DOWN)
    helper_message_react(url, user_3, msg_8['message_id'], THUMBS_DOWN)

    helper_message_unreact(url, user_3, msg_1['message_id'], THUMBS_UP)
    helper_message_unreact(url, user_3, msg_4['message_id'], THUMBS_UP)
    helper_message_unreact(url, user_3, msg_5['message_id'], THUMBS_UP)
    helper_message_unreact(url, user_3, msg_6['message_id'], THUMBS_UP)
    helper_message_unreact(url, user_3, msg_8['message_id'], THUMBS_DOWN)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_2['channel_id'],
        'start': 0,
    }).json()

    count_msg_unreacted_1 = 0
    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] in (THUMBS_UP, THUMBS_DOWN):
                if user_3['u_id'] not in react['u_ids']:
                    count_msg_unreacted_1 += 1
    # Each message has 2 react options, and there should be a total of 13 non-active reacts for user_3.
    assert count_msg_unreacted_1 == 14
    
    requests.delete(url + '/clear')

def test_unreact_same_react_from_different_users(url, user_1, user_2, user_3, public_channel_1):
    """
    Test for unreacting the same react from a message from multiple users (thumbs down).
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_3['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = send_message(url, user_1, public_channel_1, "Hola").json()

    helper_message_react(url, user_1, msg_1['message_id'], THUMBS_DOWN)
    helper_message_react(url, user_2, msg_1['message_id'], THUMBS_DOWN)
    helper_message_react(url, user_3, msg_1['message_id'], THUMBS_DOWN)

    helper_message_unreact(url, user_1, msg_1['message_id'], THUMBS_DOWN)
    helper_message_unreact(url, user_2, msg_1['message_id'], THUMBS_DOWN)
    helper_message_unreact(url, user_3, msg_1['message_id'], THUMBS_DOWN)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] == THUMBS_DOWN:
                assert user_1['u_id'] not in react['u_ids']
                assert user_2['u_id'] not in react['u_ids']
                assert user_3['u_id'] not in react['u_ids']

    requests.delete(url + '/clear')

def test_unreact_latest_reacts_from_message(url, user_1, user_2, user_3, public_channel_1):
    """
    Test for unreacting latest react from the same message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_3['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = send_message(url, user_1, public_channel_1, "Hola").json()

    helper_message_react(url, user_1, msg_1['message_id'], THUMBS_UP)
    helper_message_react(url, user_1, msg_1['message_id'], THUMBS_DOWN)
    helper_message_react(url, user_2, msg_1['message_id'], THUMBS_UP)
    helper_message_react(url, user_2, msg_1['message_id'], THUMBS_DOWN)
    helper_message_react(url, user_3, msg_1['message_id'], THUMBS_DOWN)
    helper_message_react(url, user_3, msg_1['message_id'], THUMBS_UP)

    helper_message_unreact(url, user_2, msg_1['message_id'], THUMBS_DOWN)
    helper_message_unreact(url, user_3, msg_1['message_id'], THUMBS_UP)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] == THUMBS_UP:
                assert user_1['u_id'] not in react['u_ids']
                assert user_2['u_id'] not in react['u_ids']
                assert user_3['u_id'] not in react['u_ids']
            elif react['react_id'] == THUMBS_DOWN:
                assert user_1['u_id'] in react['u_ids']
                assert user_2['u_id'] not in react['u_ids']
                assert user_3['u_id'] not in react['u_ids']

    requests.delete(url + '/clear')

def test_flockr_owner_unreact_messages(url, user_1, user_2, public_channel_2):
    """
    (Assumption Test) Test for a flockr owner unreacting a react_id in a message from 
    outside the channel.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_1['token'],
        'channel_id': public_channel_2['channel_id']
    })

    msg_1 = send_message(url, user_1, public_channel_2, "Hola").json()

    helper_message_react(url, user_1, msg_1['message_id'], THUMBS_DOWN)

    requests.post(f"{url}/channel/leave", json={
        'token': user_1['token'],
        'channel_id': public_channel_2['channel_id']
    })

    helper_message_unreact(url, user_1, msg_1['message_id'], THUMBS_DOWN)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_2['channel_id'],
        'start': 0,
    }).json()

    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] == THUMBS_UP:
                assert user_1['u_id'] not in react['u_ids']
            elif react['react_id'] == THUMBS_DOWN:
                assert user_1['u_id'] not in react['u_ids']

    requests.delete(url + '/clear')

def test_unreact_in_private_channel(url, user_1, user_2, user_3, private_channel_2):
    """
    Test for unreacting in a private channel.
    """
    requests.post(f"{url}/channel/invite", json={
        'token': user_2['token'],
        'channel_id': private_channel_2['channel_id'],
        'u_id': user_3['u_id'],
    })

    msg_1 = send_message(url, user_2, private_channel_2, "Be right back").json()

    helper_message_react(url, user_3, msg_1['message_id'], THUMBS_UP)
    helper_message_react(url, user_3, msg_1['message_id'], THUMBS_DOWN)

    helper_message_unreact(url, user_3, msg_1['message_id'], THUMBS_DOWN)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': private_channel_2['channel_id'],
        'start': 0,
    }).json()

    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] == THUMBS_UP:
                assert user_3['u_id'] not in react['u_ids']
            elif react['react_id'] == THUMBS_DOWN:
                assert user_3['u_id'] not in react['u_ids']

    requests.delete(url + '/clear')


#------------------------------------------------------------------------------#
#                                  message/pin                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_valid_message_id(url, user_1, default_message, public_channel_1):
    """
    Test whether the message_id is a valid id.
    """
    ret_pinned = helper_message_pin(url, user_1, default_message['message_id'] + 1)
    assert ret_pinned.status_code == InputError.code

    msg_1 = send_message(url, user_1, public_channel_1, "Hello World!").json()

    ret_pinned_1 = helper_message_pin(url, user_1, msg_1['message_id'] - 2)
    assert ret_pinned_1.status_code == InputError.code

    msg_2 = send_message(url, user_1, public_channel_1, "Now Way!?").json()

    ret_pinned_2 = helper_message_pin(url, user_1, msg_2['message_id'] + 100)
    assert ret_pinned_2.status_code == InputError.code

    requests.delete(url + '/clear')

def test_already_pinned(url, user_1, user_2, public_channel_1):
    """
    Test for pinning an already pinned message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_1['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = send_message(url, user_1, public_channel_1, "Hello World!").json()
    send_message(url, user_1, public_channel_1, "Now Way!?").json()

    helper_message_pin(url, user_1, msg_1['message_id'])
    ret_pinned = helper_message_pin(url, user_1, msg_1['message_id'])
    assert ret_pinned.status_code == InputError.code

    requests.delete(url + '/clear')
    
def test_user_is_member_of_channel_with_message(url, user_1, user_2, user_3, user_4, public_channel_2):
    """
    Test for user pinning a message in a channel that they are not a member of.
    """
    msg_1 = send_message(url, user_2, public_channel_2, "I am amazing!").json()

    ret_pinned_1 = helper_message_pin(url, user_3, msg_1['message_id'])
    ret_pinned_2 = helper_message_pin(url, user_4, msg_1['message_id'])

    assert ret_pinned_1.status_code == AccessError.code
    assert ret_pinned_2.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_authorised_to_pin(url, user_1, default_message, logout_user_1):
    """
    Test for a logged out user trying to pin a message.
    """
    ret_pinned = helper_message_pin(url, user_1, default_message['message_id'])
    assert ret_pinned.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_non_owner_pin(url, user_1, user_2, public_channel_1):
    """
    Test for a user who is not an owner of the channel, pinning a message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = send_message(url, user_1, public_channel_1, "Hello World!").json()
    send_message(url, user_2, public_channel_1, "Now Way!?").json()

    ret_pinned = helper_message_pin(url, user_2, msg_1['message_id'])
    assert ret_pinned.status_code == AccessError.code

    requests.delete(url + '/clear')


#?------------------------------ Output Testing ------------------------------?#

def test_pin_correct_message(url, user_1, user_2, public_channel_1):
    """
    Test for pinning the correct message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    send_message(url, user_1, public_channel_1, "Hello World!").json()
    msg_2 = send_message(url, user_1, public_channel_1, "Hi").json()
    msg_3 = send_message(url, user_2, public_channel_1, "What?!").json()
    send_message(url, user_2, public_channel_1, "1521 Comp!").json()

    helper_message_pin(url, user_1, msg_2['message_id'])
    helper_message_pin(url, user_1, msg_3['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    count_msg_pinned = 0
    for curr_message in message_list['messages']:
        if curr_message['is_pinned'] and (curr_message['message'] in ['Hi', 'What?!']):
            count_msg_pinned += 1
        
    assert count_msg_pinned == 2

    requests.delete(url + '/clear')

def test_added_owner_can_pin(url, user_1, user_2, public_channel_1):
    """
    Test for pinning messages from a recently added owner.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    send_message(url, user_1, public_channel_1, "Hello World!").json()
    msg_2 = send_message(url, user_2, public_channel_1, "Hi").json()

    requests.post(f"{url}/channel/addowner", json={
        'token': user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'u_id': user_2['u_id'],
    }).json()

    helper_message_pin(url, user_2, msg_2['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    for curr_message in message_list['messages']:
        if curr_message['message_id'] == msg_2['message_id']:
            assert curr_message['is_pinned']
    
    requests.delete(url + '/clear')

def test_pin_owned_message(url, user_1, public_channel_1):
    """
    Test for pinning the user's own messages.
    """
    msg_1 = send_message(url, user_1, public_channel_1, "Hello World!").json()
    helper_message_pin(url, user_1, msg_1['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    for curr_message in message_list['messages']:
        if curr_message['message_id'] == msg_1['message_id']:
            assert curr_message['is_pinned']

    requests.delete(url + '/clear')

def test_pin_other_messages(url, user_1, user_2, user_3, public_channel_2):
    """
    Test for pinning other user's messages.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_1['token'],
        'channel_id': public_channel_2['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_3['token'],
        'channel_id': public_channel_2['channel_id']
    })

    msg_1 = send_message(url, user_1, public_channel_2, "Hello World!").json()
    msg_2 = send_message(url, user_1, public_channel_2, "Hi").json()
    msg_3 = send_message(url, user_3, public_channel_2, "What?!").json()
    msg_4 = send_message(url, user_3, public_channel_2, "1521 Comp!").json()

    helper_message_pin(url, user_2, msg_1['message_id'])
    helper_message_pin(url, user_2, msg_2['message_id'])
    helper_message_pin(url, user_2, msg_3['message_id'])
    helper_message_pin(url, user_2, msg_4['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_1['token'],
        'channel_id': public_channel_2['channel_id'],
        'start': 0,
    }).json()

    count_msg_pinned = 0
    for curr_message in message_list['messages']:
        if curr_message['is_pinned'] and (curr_message['message'] in [
            'Hi', 'What?!', "Hello World!", "1521 Comp!"
            ]):
            count_msg_pinned += 1
        
    assert count_msg_pinned == 4

    requests.delete(url + '/clear')

def test_pin_multiple_messages(url, user_1, user_2, user_3, user_4, public_channel_3):
    """
    Test for pinning multiple different messages.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_1['token'],
        'channel_id': public_channel_3['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_3['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_4['token'],
        'channel_id': public_channel_3['channel_id']
    })

    requests.post(f"{url}/channel/addowner", json={
        'token': user_3['token'],
        'channel_id': public_channel_3['channel_id'],
        'u_id': user_4['u_id'],
    }).json()
    
    msg_1 = send_message(url, user_1, public_channel_3, "Intelligence").json()
    msg_2 = send_message(url, user_2, public_channel_3, "Is").json()
    msg_3 = send_message(url, user_2, public_channel_3, "The").json()
    send_message(url, user_3, public_channel_3, "Ability").json()
    msg_5 = send_message(url, user_3, public_channel_3, "To Adapt").json()
    msg_6 = send_message(url, user_3, public_channel_3, "To").json()
    msg_7 = send_message(url, user_4, public_channel_3, "Change").json()

    helper_message_pin(url, user_3, msg_1['message_id'])
    helper_message_pin(url, user_3, msg_2['message_id'])
    helper_message_pin(url, user_4, msg_3['message_id'])
    helper_message_pin(url, user_4, msg_5['message_id'])
    helper_message_pin(url, user_4, msg_6['message_id'])
    helper_message_pin(url, user_4, msg_7['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_1['token'],
        'channel_id': public_channel_3['channel_id'],
        'start': 0,
    }).json()

    count_msg_pinned = 0
    for curr_message in message_list['messages']:
        if curr_message['is_pinned'] and (curr_message['message'] in [
            'Intelligence', 'Is', "The", "Ability", "To Adapt", "To", "Change"
            ]):
            count_msg_pinned += 1
        
    assert count_msg_pinned == 6

    requests.delete(url + '/clear')

def test_pin_in_private_channel(url, user_1, user_2, private_channel_1):
    """
    Test for pinning messages in private channels.
    """
    requests.post(f"{url}/channel/invite", json={
        'token': user_1['token'],
        'channel_id': private_channel_1['channel_id'],
        'u_id': user_2['u_id'],
    }).json()

    msg_1 = send_message(url, user_1, private_channel_1, "Become").json()
    msg_2 = send_message(url, user_2, private_channel_1, "A").json()
    msg_3 = send_message(url, user_2, private_channel_1, "Hero").json()

    helper_message_pin(url, user_1, msg_1['message_id'])
    helper_message_pin(url, user_1, msg_2['message_id'])
    helper_message_pin(url, user_1, msg_3['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_1['token'],
        'channel_id': private_channel_1['channel_id'],
        'start': 0,
    }).json()

    count_msg_pinned = 0
    for curr_message in message_list['messages']:
        if curr_message['is_pinned'] and (curr_message['message'] in [
            'Become', 'A', "Hero"
            ]):
            count_msg_pinned += 1
        
    assert count_msg_pinned == 3

    requests.delete(url + '/clear')

def test_flockr_owner_pin_msg_in_nonmember_channels(url, user_1, user_2, private_channel_2):
    """
    (Assumption Testing) Test for the ability of flockr owner to pin messages in channels that
    they are not a part of.
    (Assumption) First user to register is flockr owner.
    """
    msg_1 = send_message(url, user_2, private_channel_2, "I").json()
    msg_2 = send_message(url, user_2, private_channel_2, "Am").json()
    msg_3 = send_message(url, user_2, private_channel_2, "Insane").json()

    helper_message_pin(url, user_1, msg_1['message_id'])
    helper_message_pin(url, user_1, msg_2['message_id'])
    helper_message_pin(url, user_1, msg_3['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': private_channel_2['channel_id'],
        'start': 0,
    }).json()

    count_msg_pinned = 0
    for curr_message in message_list['messages']:
        if curr_message['is_pinned'] and (curr_message['message'] in [
            'I', 'Am', "Insane"
            ]):
            count_msg_pinned += 1
        
    assert count_msg_pinned == 3

    requests.delete(url + '/clear')


#------------------------------------------------------------------------------#
#                                 message/unpin                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_valid_message_id_unpin(url, user_1, default_message, public_channel_1):
    """
    Test whether the message_id is a valid id.
    """
    helper_message_pin(url, user_1, default_message['message_id'])
    ret_unpinned = helper_message_unpin(url, user_1, default_message['message_id'] + 1)

    assert ret_unpinned.status_code == InputError.code

    msg_1 = send_message(url, user_1, public_channel_1, "Hello World!").json()
    helper_message_pin(url, user_1, msg_1['message_id'])
    ret_unpinned_1 = helper_message_unpin(url, user_1, msg_1['message_id'] - 2)
    assert ret_unpinned_1.status_code == InputError.code

    msg_2 = send_message(url, user_1, public_channel_1, "Now Way!?").json()
    helper_message_pin(url, user_1, msg_2['message_id'])
    ret_unpinned_2 = helper_message_pin(url, user_1, msg_2['message_id'] + 100)
    assert ret_unpinned_2.status_code == InputError.code

    requests.delete(url + '/clear')

def test_already_unpinned(url, user_1, user_2, public_channel_1):
    """
    Test for pinning an already unpinned message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = send_message(url, user_2, public_channel_1, "Hello World!").json()

    ret_unpinned = helper_message_unpin(url, user_1, msg_1['message_id'])
    assert ret_unpinned.status_code == InputError.code

    requests.delete(url + '/clear')

def test_user_is_member_of_channel_with_message_unpin(url, user_1, user_2, user_3, user_4, public_channel_2):
    """
    Test for user unpinning a message in a channel that they are not a member of.
    """
    msg_1 = send_message(url, user_2, public_channel_2, "I am amazing!").json()
    msg_2 = send_message(url, user_2, public_channel_2, "No you're not!").json()

    helper_message_pin(url, user_2, msg_1['message_id'])
    helper_message_pin(url, user_2, msg_2['message_id'])

    ret_unpinned_1 = helper_message_unpin(url, user_3, msg_1['message_id'])
    ret_unpinned_2 = helper_message_unpin(url, user_4, msg_2['message_id'])

    assert ret_unpinned_1.status_code == AccessError.code
    assert ret_unpinned_2.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_authorised_to_unpin(url, user_1, public_channel_1):
    """
    Test for a logged out user trying to unpin a message.
    """
    msg_1 = send_message(url, user_1, public_channel_1, "I am amazing!").json()
    helper_message_pin(url, user_1, msg_1['message_id'])

    requests.post(f"{url}/auth/logout", json={
        'token': user_1['token'],
    }).json()

    ret_unpinned = helper_message_unpin(url, user_1, msg_1['message_id'])
    assert ret_unpinned.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_non_owner_unpin(url, user_1, user_2, public_channel_1):
    """
    Test for a user who is not an owner of the channel, unpinning a message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = send_message(url, user_1, public_channel_1, "Hello World!").json()
    helper_message_pin(url, user_1, msg_1['message_id'])

    ret_unpinned = helper_message_unpin(url, user_2, msg_1['message_id'])
    assert ret_unpinned.status_code == AccessError.code

    requests.delete(url + '/clear')


#?------------------------------ Output Testing ------------------------------?#

def test_unpin_correct_message(url, user_1, user_2, public_channel_1):
    """
    Test for unpinning the correct message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = send_message(url, user_1, public_channel_1, "Hello World!").json()
    msg_2 = send_message(url, user_1, public_channel_1, "Hi").json()
    msg_3 = send_message(url, user_2, public_channel_1, "What?!").json()
    msg_4 = send_message(url, user_2, public_channel_1, "1521 Comp!").json()

    helper_message_pin(url, user_1, msg_1['message_id'])
    helper_message_pin(url, user_1, msg_2['message_id'])
    helper_message_pin(url, user_1, msg_3['message_id'])
    helper_message_pin(url, user_1, msg_4['message_id'])

    helper_message_unpin(url, user_1, msg_1['message_id'])
    helper_message_unpin(url, user_1, msg_4['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    count_msg_unpinned = 0
    for curr_message in message_list['messages']:
        if not curr_message['is_pinned'] and (curr_message['message'] in ['Hello World!', '1521 Comp!']):
            count_msg_unpinned += 1
        
    assert count_msg_unpinned == 2

    requests.delete(url + '/clear')

def test_added_owner_can_unpin(url, user_1, user_2, public_channel_1):
    """
    Test for unpinning messages from a recently added owner.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = send_message(url, user_1, public_channel_1, "Hello World!").json()
    msg_2 = send_message(url, user_2, public_channel_1, "Hi").json()
    helper_message_pin(url, user_1, msg_1['message_id'])
    helper_message_pin(url, user_1, msg_2['message_id'])

    requests.post(f"{url}/channel/addowner", json={
        'token': user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'u_id': user_2['u_id'],
    }).json()

    helper_message_unpin(url, user_2, msg_2['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    for curr_message in message_list['messages']:
        if curr_message['message_id'] == msg_2['message_id']:
            assert not curr_message['is_pinned']
    
    requests.delete(url + '/clear')

def test_unpin_owned_message(url, user_1, public_channel_1):
    """
    Test for unpinning the user's own messages.
    """
    msg_1 = send_message(url, user_1, public_channel_1, "Hello World!").json()
    helper_message_pin(url, user_1, msg_1['message_id'])
    helper_message_unpin(url, user_1, msg_1['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    for curr_message in message_list['messages']:
        if curr_message['message_id'] == msg_1['message_id']:
            assert not curr_message['is_pinned']

    requests.delete(url + '/clear')

def test_unpin_other_messages(url, user_1, user_2, user_3, public_channel_2):
    """
    Test for unpinning other user's messages.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_1['token'],
        'channel_id': public_channel_2['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_3['token'],
        'channel_id': public_channel_2['channel_id']
    })

    msg_1 = send_message(url, user_1, public_channel_2, "Hello World!").json()
    msg_2 = send_message(url, user_1, public_channel_2, "Hi").json()
    msg_3 = send_message(url, user_3, public_channel_2, "What?!").json()
    msg_4 = send_message(url, user_3, public_channel_2, "1521 Comp!").json()

    helper_message_pin(url, user_2, msg_1['message_id'])
    helper_message_pin(url, user_2, msg_2['message_id'])
    helper_message_pin(url, user_2, msg_3['message_id'])
    helper_message_pin(url, user_2, msg_4['message_id'])

    helper_message_unpin(url, user_2, msg_1['message_id'])
    helper_message_unpin(url, user_2, msg_3['message_id'])
    helper_message_unpin(url, user_2, msg_4['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_1['token'],
        'channel_id': public_channel_2['channel_id'],
        'start': 0,
    }).json()

    count_msg_unpinned = 0
    for curr_message in message_list['messages']:
        if not curr_message['is_pinned'] and (curr_message['message'] in [
            'Hello World!', 'What?!', "1521 Comp!"
            ]):
            count_msg_unpinned += 1
        
    assert count_msg_unpinned == 3

    requests.delete(url + '/clear')

def test_unpin_multiple_messages(url, user_1, user_2, user_3, user_4, public_channel_3):
    """
    Test for unpinning multiple different messages.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_1['token'],
        'channel_id': public_channel_3['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_3['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_4['token'],
        'channel_id': public_channel_3['channel_id']
    })

    requests.post(f"{url}/channel/addowner", json={
        'token': user_3['token'],
        'channel_id': public_channel_3['channel_id'],
        'u_id': user_4['u_id'],
    }).json()
    
    msg_1 = send_message(url, user_1, public_channel_3, "Intelligence").json()
    msg_2 = send_message(url, user_2, public_channel_3, "Is").json()
    msg_3 = send_message(url, user_2, public_channel_3, "The").json()
    send_message(url, user_3, public_channel_3, "Ability").json()
    msg_5 = send_message(url, user_3, public_channel_3, "To Adapt").json()
    msg_6 = send_message(url, user_3, public_channel_3, "To").json()
    msg_7 = send_message(url, user_4, public_channel_3, "Change").json()

    helper_message_pin(url, user_3, msg_1['message_id'])
    helper_message_pin(url, user_3, msg_2['message_id'])
    helper_message_pin(url, user_4, msg_3['message_id'])
    helper_message_pin(url, user_4, msg_5['message_id'])
    helper_message_pin(url, user_4, msg_6['message_id'])
    helper_message_pin(url, user_4, msg_7['message_id'])

    helper_message_unpin(url, user_4, msg_1['message_id'])
    helper_message_unpin(url, user_4, msg_2['message_id'])
    helper_message_unpin(url, user_3, msg_3['message_id'])
    helper_message_unpin(url, user_4, msg_5['message_id'])
    helper_message_unpin(url, user_4, msg_7['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_1['token'],
        'channel_id': public_channel_3['channel_id'],
        'start': 0,
    }).json()

    count_msg_unpinned = 0
    for curr_message in message_list['messages']:
        if not curr_message['is_pinned'] and (curr_message['message'] in [
            'Intelligence', 'Is', "The", "Ability", "To Adapt", "Change"
            ]):
            count_msg_unpinned += 1
        
    assert count_msg_unpinned == 6

    requests.delete(url + '/clear')

def test_unpin_in_private_channel(url, user_1, user_2, private_channel_1):
    """
    Test for unpinning messages in private channels.
    """
    requests.post(f"{url}/channel/invite", json={
        'token': user_1['token'],
        'channel_id': private_channel_1['channel_id'],
        'u_id': user_2['u_id'],
    }).json()

    msg_1 = send_message(url, user_1, private_channel_1, "Become").json()
    msg_2 = send_message(url, user_2, private_channel_1, "A").json()
    msg_3 = send_message(url, user_2, private_channel_1, "Hero").json()

    helper_message_pin(url, user_1, msg_1['message_id'])
    helper_message_pin(url, user_1, msg_2['message_id'])
    helper_message_pin(url, user_1, msg_3['message_id'])

    helper_message_unpin(url, user_1, msg_2['message_id'])
    helper_message_unpin(url, user_1, msg_3['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_1['token'],
        'channel_id': private_channel_1['channel_id'],
        'start': 0,
    }).json()

    count_msg_unpinned = 0
    for curr_message in message_list['messages']:
        if not curr_message['is_pinned'] and (curr_message['message'] in [
            'A', "Hero"
            ]):
            count_msg_unpinned += 1
        
    assert count_msg_unpinned == 2

    requests.delete(url + '/clear')

def test_flockr_owner_unpin_msg_in_nonmember_channels(url, user_1, user_2, private_channel_2):
    """
    (Assumption Testing) Test for the ability of flockr owner to unpin messages in channels that
    they are not a part of.
    (Assumption) First user to register is flockr owner.
    """
    send_message(url, user_2, private_channel_2, "I").json()
    msg_2 = send_message(url, user_2, private_channel_2, "Am").json()
    msg_3 = send_message(url, user_2, private_channel_2, "Insane").json()

    helper_message_pin(url, user_1, msg_2['message_id'])
    helper_message_pin(url, user_1, msg_3['message_id'])

    helper_message_unpin(url, user_1, msg_3['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': private_channel_2['channel_id'],
        'start': 0,
    }).json()

    count_msg_pinned = 0
    for curr_message in message_list['messages']:
        if not curr_message['is_pinned'] and (curr_message['message'] in [
            'I', "Insane"
            ]):
            count_msg_pinned += 1
        
    assert count_msg_pinned == 2

    requests.delete(url + '/clear')
