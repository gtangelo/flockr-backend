import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
from error import InputError, AccessError

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

#------------------------------------------------------------------------------#
#                                 message/send                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_message_send_more_than_1000_char(url):
    """
    Testing when the message sent is over 1000 characters
    """
    requests.delete(url + '/clear')

    user_profile = {
        'email'     : 'johnsmith@gmail.com',
        'password'  : 'password',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    user_1 = requests.post(url + 'auth/register', json=user_profile).json()

    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': True,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_message = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : ("Hello" * 250),
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    res_err.status_code == InputError.code

    arg_message = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : ("HI " * 500),
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    res_err.status_code == InputError.code

    arg_message = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : ("My name is blah" * 100),
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    res_err.status_code == InputError.code

    requests.delete(url + '/clear')

def test_message_send_auth_user_not_in_channel(url):
    """
    Testing when the authorised user has not joined the channel they
    are trying to post to
    """
    requests.delete(url + '/clear')

    user_profile = {
        'email'     : 'johnsmith@gmail.com',
        'password'  : 'password',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    user_1 = requests.post(url + 'auth/register', json=user_profile).json()

    user_profile = {
        'email'     : 'janesmith@gmail.com',
        'password'  : 'password',
        'name_first': 'Jane',
        'name_last' : 'Smith',
    }
    user_2 = requests.post(url + 'auth/register', json=user_profile).json()

    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': True,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_message = {
        'token'     : user_2['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : "Hello",
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    res_err.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_message_send_expired_token(url):
    """
    Testing invalid token for users which have logged out
    """
    requests.delete(url + '/clear')

    user_profile = {
        'email'     : 'johnsmith@gmail.com',
        'password'  : 'password',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    user_1 = requests.post(url + 'auth/register', json=user_profile).json()

    user_profile = {
        'email'     : 'janesmith@gmail.com',
        'password'  : 'password',
        'name_first': 'Jane',
        'name_last' : 'Smith',
    }
    user_2 = requests.post(url + 'auth/register', json=user_profile).json()

    user_profile = {
        'email'     : 'jonesmith@gmail.com',
        'password'  : 'password',
        'name_first': 'Jone',
        'name_last' : 'Smith',
    }
    user_3 = requests.post(url + 'auth/register', json=user_profile).json()

    user_profile = {
        'email'     : 'jamesmith@gmail.com',
        'password'  : 'password',
        'name_first': 'Jame',
        'name_last' : 'Smith',
    }
    user_4 = requests.post(url + 'auth/register', json=user_profile).json()

    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': True,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    log_out = requests.post(f'{url}/auth/logout', json={'token': user_1['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_2['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_3['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_4['token']}).json()
    assert log_out['is_success']

    arg_message = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : "Hello",
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    res_err.status_code == AccessError.code

    arg_message = {
        'token'     : user_2['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : "Hello",
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    res_err.status_code == AccessError.code

    arg_message = {
        'token'     : user_3['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : "Hello",
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    res_err.status_code == AccessError.code

    arg_message = {
        'token'     : user_4['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : "Hello",
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    res_err.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_message_send_incorrect_token_type(url):
    """
    Testing invalid token data type handling
    """
    requests.delete(url + '/clear')

    user_profile = {
        'email'     : 'johnsmith@gmail.com',
        'password'  : 'password',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    user_1 = requests.post(url + 'auth/register', json=user_profile).json()

    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': True,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_message = {
        'token'     : 12,
        'channel_id': new_channel_1['channel_id'],
        'message'   : "Hello",
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    res_err.status_code == AccessError.code

    arg_message = {
        'token'     : -12,
        'channel_id': new_channel_1['channel_id'],
        'message'   : "Hello",
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    res_err.status_code == AccessError.code

    arg_message = {
        'token'     : 121.11,
        'channel_id': new_channel_1['channel_id'],
        'message'   : "Hello",
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    res_err.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_message_send_channel_id(url):
    """
    Testing when an invalid channel_id is used as a parameter
    """
    requests.delete(url + '/clear')

    user_profile = {
        'email'     : 'johnsmith@gmail.com',
        'password'  : 'password',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    user_1 = requests.post(url + 'auth/register', json=user_profile).json()

    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': True,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_message = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'] + 7,
        'message'   : "Hello",
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    res_err.status_code == InputError.code

    requests.delete(url + '/clear')

def test_message_send_valid_token(url):
    """
    Testing if token is valid
    """
    requests.delete(url + '/clear')

    user_profile = {
        'email'     : 'johnsmith@gmail.com',
        'password'  : 'password',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    user_1 = requests.post(url + 'auth/register', json=user_profile).json()

    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': True,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_message = {
        'token'     : -1,
        'channel_id': new_channel_1['channel_id'],
        'message'   : "Hello",
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    res_err.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_message_send_output_empty_str(url):
    """
    Testing an empty string message (Authorised user sends a message in a channel)
    """
    requests.delete(url + '/clear')

    user_profile = {
        'email'     : 'johnsmith@gmail.com',
        'password'  : 'password',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    user_1 = requests.post(url + 'auth/register', json=user_profile).json()

    user_profile = {
        'email'     : 'janesmith@gmail.com',
        'password'  : 'password',
        'name_first': 'Jane',
        'name_last' : 'Smith',
    }
    user_2 = requests.post(url + 'auth/register', json=user_profile).json()

    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': True,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_join = {
        'token'     : user_2['token'],
        'channel_id': new_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    arg_message = {
        'token'     : user_2['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : "",
    }
    res_err = requests.post(url + 'message/send', json=arg_message)
    res_err.status_code == InputError.code

    requests.delete(url + '/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_message_send_output_one(url):
    """
    Testing a normal case (Authorised user sends a message in a channel)
    """
    requests.delete(url + '/clear')

    user_profile = {
        'email'     : 'johnsmith@gmail.com',
        'password'  : 'password',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    user_1 = requests.post(url + 'auth/register', json=user_profile).json()

    user_profile = {
        'email'     : 'janesmith@gmail.com',
        'password'  : 'password',
        'name_first': 'Jane',
        'name_last' : 'Smith',
    }
    user_2 = requests.post(url + 'auth/register', json=user_profile).json()

    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': True,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_join = {
        'token'     : user_2['token'],
        'channel_id': new_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    message_str_one = "Welcome guys!"
    message_str_two = "Hello, I'm Jane!"

    arg_message = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : message_str_one,
    }
    new_message_1 = requests.post(url + 'message/send', json=arg_message).json()

    arg_message = {
        'token'     : user_2['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : message_str_two,
    }
    new_message_2 = requests.post(url + 'message/send', json=arg_message).json()

    arg_message_list = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
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

def test_message_send_output_two(url):
    """
    Testing a longer case (multiple authorised users sending messages in a channel)
    """
    requests.delete(url + '/clear')

    user_profile = {
        'email'     : 'johnsmith@gmail.com',
        'password'  : 'password',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    user_1 = requests.post(url + 'auth/register', json=user_profile).json()

    user_profile = {
        'email'     : 'janesmith@gmail.com',
        'password'  : 'password',
        'name_first': 'Jane',
        'name_last' : 'Smith',
    }
    user_2 = requests.post(url + 'auth/register', json=user_profile).json()

    user_profile = {
        'email'     : 'jonesmith@gmail.com',
        'password'  : 'password',
        'name_first': 'Jone',
        'name_last' : 'Smith',
    }
    user_3 = requests.post(url + 'auth/register', json=user_profile).json()

    user_profile = {
        'email'     : 'jamesmith@gmail.com',
        'password'  : 'password',
        'name_first': 'Jame',
        'name_last' : 'Smith',
    }
    user_4 = requests.post(url + 'auth/register', json=user_profile).json()

    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': True,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_join = {
        'token'     : user_2['token'],
        'channel_id': new_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    arg_join = {
        'token'     : user_3['token'],
        'channel_id': new_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    arg_join = {
        'token'     : user_4['token'],
        'channel_id': new_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    msg_str_1 = "Welcome guys!"
    msg_str_2 = "Hello, I'm Jane!"
    msg_str_3 = "sup"
    msg_str_4 = "Ok, let's start the project"
    msg_str_5 = "Join the call when you're ready guys"
    msg_str_6 = "sure, lemme get something to eat first"
    msg_str_7 = "Yeah aight, I'm joining."

    arg_message = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : msg_str_1,
    }
    requests.post(url + 'message/send', json=arg_message)

    arg_message = {
        'token'     : user_2['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : msg_str_2,
    }
    requests.post(url + 'message/send', json=arg_message)

    arg_message = {
        'token'     : user_3['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : msg_str_3,
    }
    requests.post(url + 'message/send', json=arg_message)

    arg_message = {
        'token'     : user_4['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : msg_str_4,
    }
    requests.post(url + 'message/send', json=arg_message)

    arg_message = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : msg_str_5,
    }
    requests.post(url + 'message/send', json=arg_message)

    arg_message = {
        'token'     : user_2['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : msg_str_6,
    }
    requests.post(url + 'message/send', json=arg_message)

    arg_message = {
        'token'     : user_3['token'],
        'channel_id': new_channel_1['channel_id'],
        'message'   : msg_str_7,
    }
    requests.post(url + 'message/send', json=arg_message)

    arg_message_list = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
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
#                                message/remove                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#


#------------------------------------------------------------------------------#
#                                 message/edit                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#
