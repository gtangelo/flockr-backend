import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json


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
#                                message/remove                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#


#------------------------------------------------------------------------------#
#                                 message/edit                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#


