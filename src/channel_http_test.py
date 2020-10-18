from json import dumps
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
#                               channel/invite                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#



#------------------------------------------------------------------------------#
#                               channel/details                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#


#------------------------------------------------------------------------------#
#                               channel/messages                               #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#



#------------------------------------------------------------------------------#
#                               channel/leave                                  #
#------------------------------------------------------------------------------#

def register_default_user(url, name_first, name_last):
    email = f'{name_first.lower()}{name_last.lower()}@gmail.com'
    data = {
        'email': email,
        'password': 'password',
        'name_first': name_first,
        'name_last': name_last
    }
    payload = requests.post(f'{url}/auth/register', json=dumps(data))
    return payload.json()

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_input_leave_channel_id(url):
    """Testing when an invalid channel_id is used as a parameter
    """
    requests.delete(f'{url}/clear')
    user = register_default_user(url, 'John', 'Smith')

    data = {
        'token': user['token']
        'name': 'Group 1',
        'is_public': True,
    }

    # channel_data = requests.post(f'{url}/channels/create', json=dumps(data))

    data = {'token': user['token'], 'channel_id': -1}
    payload = requests.post(f'{url}/channel/leave', json=dumps(data))
    assert payload.status_code == InputError.code

    data = {'token': user['token'], 'channel_id': 0}
    payload = requests.post(f'{url}/channel/leave', json=dumps(data))
    assert payload.status_code == InputError.code

    data = {'token': user['token'], 'channel_id': 1}
    payload = requests.post(f'{url}/channel/leave', json=dumps(data))
    assert payload.status_code == InputError.code

    requests.delete(f'{url}/clear')

def test_access_leave_user_is_member():
    """Testing if a user was not in the channel initially
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    new_channel_1 = channels.channels_create(user_1['token'], 'Group 1', True)
    new_channel_2 = channels.channels_create(user_2['token'], 'Group 2', True)

    with pytest.raises(AccessError):
        channel.channel_leave(user_1['token'], new_channel_2['channel_id'])
    with pytest.raises(AccessError):
        channel.channel_leave(user_2['token'], new_channel_1['channel_id'])
    clear()

def test_access_leave_valid_token():
    """Testing if token is valid
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    auth.auth_logout(user['token'])

    with pytest.raises(AccessError):
        channel.channel_leave(user['token'], new_channel['channel_id'])
    clear()


#?------------------------------ Output Testing ------------------------------?#



#------------------------------------------------------------------------------#
#                               channel/join                                   #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#


#------------------------------------------------------------------------------#
#                               channel/addowner                               #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#



#------------------------------------------------------------------------------#
#                             channel/removeowner                              #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#



#------------------------------------------------------------------------------#
#                               channel/invite                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#


