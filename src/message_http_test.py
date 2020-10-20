from json import dumps
import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
import message

from other import clear
from error import InputError, AccessError
from data import data

# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
@pytest.fixture
def url():
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")

# Example testing from echo_http_test.py
# def test_echo(url):
#     '''
#     A simple test to check echo
#     '''
#     resp = requests.get(url + 'echo', params={'data': 'hello'})
#     assert json.loads(resp.text) == {'data': 'hello'}

def register_default_user(url, name_first, name_last):
    email = f'{name_first.lower()}{name_last.lower()}@gmail.com'
    data = {
        'email': email,
        'password': 'password',
        'name_first': name_first,
        'name_last': name_last
    }
    payload = requests.post(f'{url}auth/register', json=data)
    return payload.json()

@pytest.fixture
def user_1(url):
    requests.delete(f'{url}/clear')
    return register_default_user(url, 'John', 'Smith')

@pytest.fixture
def user_2(url):
    return register_default_user(url, 'Jane', 'Smith')
    
@pytest.fixture
def user_3(url):
    return register_default_user(url, 'Jace', 'Smith')
    
@pytest.fixture
def user_4(url):
    return register_default_user(url, 'Janice', 'Smith')

@pytest.fixture
def default_channel(url, user_1):
    return requests.post(f'{url}/channels/create', json={
        'token': user_1['token'],
        'name': 'Group 1',
        'is_public': True,
    }).json()

@pytest.fixture
def default_message(url, user_1, default_channel):
    return requests.post(f'{url}/message/send', json={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'message': "Hey channel!",
    }).json()

#------------------------------------------------------------------------------#
#                                 message/send                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#



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
    error.status_code = AccessError.code

    remove_details = {
        'token'     : user_2['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = AccessError.code

    remove_details = {
        'token'     : user_3['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = AccessError.code

    remove_details = {
        'token'     : user_4['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = AccessError.code
    requests.delete(f'{url}/clear')

def test_message_remove_incorrect_token_type(url, user_1, default_message):
    """Testing invalid token data type handling
    """
    remove_details = {
        'token'     : 12,
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = AccessError.code

    remove_details = {
        'token'     : -12,
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = AccessError.code

    remove_details = {
        'token'     : 121.11,
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = AccessError.code
    requests.delete(f'{url}/clear')

def test_message_remove_wrong_data_type(url, user_1, default_message):
    """Testing when wrong data types are used as input
    """
    remove_details = {
        'token'     : user_1['token'],
        'message_id': '@#$!',
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = InputError.code

    remove_details = {
        'token'     : user_1['token'],
        'message_id': 67.666,
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = InputError.code

    remove_details = {
        'token'     : user_1['token'],
        'message_id': default_message['message_id'] - 1,
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = InputError.code

    remove_details = {
        'token'     : user_1['token'],
        'message_id': default_message['message_id'] + 1,
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = InputError.code
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
    error.status_code = InputError.code

    remove_details = {
        'token'     : user_1['token'],
        'message_id': default_message['message_id'] - 1,
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = InputError.code

    remove_details = {
        'token'     : user_1['token'],
        'message_id': default_message['message_id'] + 100,
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = InputError.code

    remove_details = {
        'token'     : user_1['token'],
        'message_id': default_message['message_id'] - 100,
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = InputError.code
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
    error.status_code = InputError.code
    requests.delete(f'{url}/clear')

def test_message_remove_not_authorized_channel_owner(url, user_1, user_2, user_3, user_4, default_channel, default_message):
    """Testing when message based on message_id is called for deletion
       but the requester is not a channel_owner
    """
    invite_details = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_2['u_id'],
    }
    channel_return = requests.post(f'{url}/channel/invite', json=invite_details).json()
    assert channel_return == {}

    invite_details = {
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_3['u_id'],
    }
    channel_return = requests.post(f'{url}/channel/invite', json=invite_details).json()
    assert channel_return == {}

    remove_details = {
        'token'     : user_2['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = AccessError.code

    remove_details = {
        'token'     : user_3['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = AccessError.code

    remove_details = {
        'token'     : user_4['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = AccessError.code

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
    error.status_code = AccessError.code

    remove_details = {
        'token'     : user_3['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = AccessError.code

    remove_details = {
        'token'     : user_4['token'],
        'message_id': default_message['message_id'],
    }
    error = requests.delete(f'{url}/message/remove', json=remove_details)
    error.status_code = AccessError.code
    requests.delete(f'{url}/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_message_remove_authorized_owner_channel(url, user_1, default_channel):
    """Testing when message based on message_id is deleted by channel owner / flockr owner
    """
    message_details = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'message'   : 'I',
    }
    message_1 = requests.post(f'{url}/message/send', json=message_details).json()

    message_details = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'message'   : 'am',
    }
    message_2 = requests.post(f'{url}/message/send', json=message_details).json()

    message_details = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'message'   : 'really',
    }
    message_3 = requests.post(f'{url}/message/send', json=message_details).json()

    message_details = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'message'   : 'hungry :(',
    }
    message_4 = requests.post(f'{url}/message/send', json=message_details).json()

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
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
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
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
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
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
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
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            on_list = True
    assert not on_list
    requests.delete(f'{url}/clear')

def test_message_remove_authorized_flockr_owner(url):
    """(Assumption Testing) Testing when message based on message_id is deleted by
       flockr owner who is not part of any channel
       (Assumption) First user to register is flockr owner
    """
    requests.delete(f'{url}/clear')
    clear()
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
        'message'   : 'I',
    }
    message_1 = requests.post(f'{url}/message/send', json=message_details).json()

    message_details = {
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
        'message'   : 'am',
    }
    message_2 = requests.post(f'{url}/message/send', json=message_details).json()

    message_details = {
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
        'message'   : 'really',
    }
    message_3 = requests.post(f'{url}/message/send', json=message_details).json()

    message_details = {
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
        'message'   : 'hungry :(',
    }
    message_4 = requests.post(f'{url}/message/send', json=message_details).json()

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
        'channel_id': default_channel['channel_id'],
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
        'channel_id': default_channel['channel_id'],
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
        'channel_id': default_channel['channel_id'],
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
        'channel_id': default_channel['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            on_list = True
    assert not on_list
    requests.delete(f'{url}/clear')

#------------------------------------------------------------------------------#
#                                message_edit                                  #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_message_edit_expired_token(url, user_1, user_2, user_3, user_4, default_channel, default_message):
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
    error.status_code == AccessError.code

    message_info = {
        'token': user_2['token'],
        'message_id': default_message['message_id'],
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == AccessError.code

    message_info = {
        'token': user_3['token'],
        'message_id': default_message['message_id'],
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == AccessError.code

    message_info = {
        'token': user_4['token'],
        'message_id': default_message['message_id'],
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == AccessError.code
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
    error.status_code == AccessError.code

    message_info = {
        'token': -12,
        'message_id': default_message['message_id'],
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == AccessError.code

    message_info = {
        'token': 121.11,
        'message_id': default_message['message_id'],
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_message_edit_wrong_data_type(url, user_1, default_message):
    """Testing when wrong data types are used as input
    """
    message_info = {
        'token': user_1['token'],
        'message_id': '@#$!',
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == InputError.code

    message_info = {
        'token': user_1['token'],
        'message_id': 67.666,
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == InputError.code

    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'] - 1,
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == InputError.code

    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'] + 1,
        'message': 'hello',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == InputError.code
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
    error.status_code == InputError.code

    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'message': message_str_2,
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == InputError.code

    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'message': message_str_3,
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == InputError.code
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
    error.status_code == InputError.code

    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'message': -1,
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == InputError.code

    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'message': 100,
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == InputError.code

    message_info = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'message': 127.66,
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == InputError.code
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
    error.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_message_edit_not_authorized_channel_owner(url, user_1, user_2, user_3, user_4, default_channel, default_message):
    """Testing when message based on message_id is called for editing
       but the requester is not a channel_owner
    """
    invite_details = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_2['u_id'],
    }
    channel_return = requests.post(f'{url}/channel/invite', json=invite_details).json()
    assert channel_return == {}

    invite_details = {
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
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
    error.status_code == AccessError.code

    message_info = {
        'token': user_3['token'],
        'message_id': default_message['message_id'],
        'message': 'lets edit!',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == AccessError.code

    message_info = {
        'token': user_4['token'],
        'message_id': default_message['message_id'],
        'message': 'lets edit!',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_message_edit_not_authorized_flockr_owner(url, user_1, user_2, user_3, user_4, default_channel, default_message):
    """Testing when message based on message_id is called for editing
       but the requester is not a flockr owner
    """
    requests.delete(f'{url}/clear')
    clear()

    message_info = {
        'token': user_2['token'],
        'message_id': default_message['message_id'],
        'message': 'lets edit!',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == AccessError.code

    message_info = {
        'token': user_3['token'],
        'message_id': default_message['message_id'],
        'message': 'lets edit!',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == AccessError.code

    message_info = {
        'token': user_4['token'],
        'message_id': default_message['message_id'],
        'message': 'lets edit!',
    }
    error = requests.put(f'{url}/message/edit', json=message_info)
    error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_message_edit_authorized_owner_channel(url, user_1, default_channel, default_message):
    """Testing when message based on message_id is edited by channel owner / flockr owner
    """
    on_list = False
    message_profile = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
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
        'channel_id': default_channel['channel_id'],
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
    clear()
    
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

def test_message_edit_empty_string(url, user_1, default_channel):
    """Testing when message based on message_id is edited by
       an empty string; in which case the message is deleted
    """
    message_details = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'message'   : 'I',
    }
    message_1 = requests.post(f'{url}/message/send', json=message_details).json()

    message_details = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'message'   : 'am',
    }
    message_2 = requests.post(f'{url}/message/send', json=message_details).json()

    message_details = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'message'   : 'really',
    }
    message_3 = requests.post(f'{url}/message/send', json=message_details).json()

    message_details = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
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
        'channel_id': default_channel['channel_id'],
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
        'channel_id': default_channel['channel_id'],
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
        'channel_id': default_channel['channel_id'],
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
        'channel_id': default_channel['channel_id'],
        'start'     : 0,
    }
    message_data = requests.get(f'{url}/channel/messages', params=message_profile).json()
    for messages in message_data['messages']:
        if messages['message_id'] == message_4['message_id']:
            on_list = True
    assert not on_list
    requests.delete(f'{url}/clear')


