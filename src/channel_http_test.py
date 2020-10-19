from json import dumps
import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json

from other import clear
from error import InputError, AccessError
from data import data

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
    requests.delete(f'{url}clear')
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


# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
@pytest.fixture(scope="session")
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

# #?-------------------------- Input/Access Error Testing ----------------------?#

# def test_channel_invite_login_user_HTTP(url):
#     """Testing invalid token for users which have logged out
#     """
#     requests.delete(url + '/clear')
#     clear()
#     user_profile = {
#         'email'     : 'johnsmith@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Smith',
#     }
#     user_1 = requests.post(url + 'auth/register', json=user_profile).json()

#     user_profile = {
#         'email'     : 'jennielin@gmail.com',
#         'password'  : 'password',
#         'name_first': 'Jennie',
#         'name_last' : 'Lin',
#     }
#     user_2 = requests.post(url + 'auth/register', json=user_profile).json()

#     user_profile = {
#         'email'     : 'johnperry@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Perry',
#     }
#     user_3 = requests.post(url + 'auth/register', json=user_profile).json()

#     user_profile = {
#         'email'     : 'prathsjag@gmail.com',
#         'password'  : 'password',
#         'name_first': 'Praths',
#         'name_last' : 'Jag',
#     }
#     user_4 = requests.post(url + 'auth/register', json=user_profile).json()

#     channel_profile = {
#         'token'    : user_1['token'],
#         'name'     : 'Group 1',
#         'is_public': True,
#     }
#     new_channel = requests.post(url + '/channels/create', json=channel_profile).json()

#     log_out = requests.post(url + '/auth/logout', json={'token': user_1['token']}).json()
#     assert log_out['is_success'] == True
#     log_out = requests.post(url + '/auth/logout', json={'token': user_2['token']}).json()
#     assert log_out['is_success'] == True
#     log_out = requests.post(url + '/auth/logout', json={'token': user_3['token']}).json()
#     assert log_out['is_success'] == True
#     log_out = requests.post(url + '/auth/logout', json={'token': user_4['token']}).json()
#     assert log_out['is_success'] == True

#     # with pytest.raises(AccessError):
#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_1['u_id'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == AccessError.code

#     channel_profile = {
#         'token'     : user_2['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_3['u_id'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == AccessError.code

#     channel_profile = {
#         'token'     : user_3['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_3['u_id'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == AccessError.code

#     channel_profile = {
#         'token'     : user_4['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_3['u_id'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == AccessError.code
#     requests.delete(url + '/clear')
#     clear()

# def test_channel_invite_wrong_data_type_HTTP(url):
#     """Testing when wrong data types are used as input
#     """
#     requests.delete(url + '/clear')
#     clear()
#     user_profile = {
#         'email'     : 'johnsmith@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Smith',
#     }
#     user = requests.post(url + 'auth/register', json=user_profile).json()

#     channel_profile = {
#         'token'    : user['token'],
#         'name'     : 'Group 1',
#         'is_public': True,
#     }
#     new_channel = requests.post(url + 'channels/create', json=channel_profile).json()

#     channel_profile = {
#         'token'     : user['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : -1,
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == InputError.code

#     channel_profile = {
#         'token'     : user['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : '@#$!',
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == InputError.code

#     channel_profile = {
#         'token'     : user['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : 67.666,
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == InputError.code
#     requests.delete(url + '/clear')
#     clear()

# def test_channel_invite_invalid_user_HTTP(url):
#     """Testing when invalid user is invited to channel
#     """
#     requests.delete(url + '/clear')
#     clear()
#     user_profile = {
#         'email'     : 'johnsmith@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Smith',
#     }
#     user = requests.post(url + 'auth/register', json=user_profile).json()

#     channel_profile = {
#         'token'    : user['token'],
#         'name'     : 'Group 1',
#         'is_public': True,
#     }
#     new_channel = requests.post(url + 'channels/create', json=channel_profile).json()

#     channel_profile = {
#         'token'     : user['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user['u_id'] + 1,
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == InputError.code

#     channel_profile = {
#         'token'     : user['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user['u_id'] - 1,
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == InputError.code
#     requests.delete(url + '/clear')
#     clear()

# def test_channel_invite_invalid_channel_HTTP(url):
#     """Testing when valid user is invited to invalid channel
#     """
#     requests.delete(url + '/clear')
#     clear()
#     user_profile = {
#         'email'     : 'johnsmith@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Smith',
#     }
#     user_1 = requests.post(url + 'auth/register', json=user_profile).json()

#     user_profile = {
#         'email'     : 'jennielin@gmail.com',
#         'password'  : 'password',
#         'name_first': 'Jennie',
#         'name_last' : 'Lin',
#     }
#     user_2 = requests.post(url + 'auth/register', json=user_profile).json()

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': -122,
#         'u_id'      : user_2['u_id'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == InputError.code

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': -642,
#         'u_id'      : user_2['u_id'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == InputError.code

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': '@#@!',
#         'u_id'      : user_2['u_id'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == InputError.code

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': 212.11,
#         'u_id'      : user_2['u_id'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == InputError.code
#     requests.delete(url + '/clear')
#     clear()

# def test_channel_invite_not_authorized_HTTP(url):
#     """Testing when user is not authorized to invite other users to channel
#     (Assumption) This includes an invalid user inviting users to channel
#     """
#     requests.delete(url + '/clear')
#     clear()
#     user_profile = {
#         'email'     : 'johnsmith@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Smith',
#     }
#     user_1 = requests.post(url + 'auth/register', json=user_profile).json()

#     user_profile = {
#         'email'     : 'jennielin@gmail.com',
#         'password'  : 'password',
#         'name_first': 'Jennie',
#         'name_last' : 'Lin',
#     }
#     user_2 = requests.post(url + 'auth/register', json=user_profile).json()

#     user_profile = {
#         'email'     : 'johnperry@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Perry',
#     }
#     user_3 = requests.post(url + 'auth/register', json=user_profile).json()

#     channel_profile = {
#         'token'    : user_3['token'],
#         'name'     : 'Group 1',
#         'is_public': True,
#     }
#     new_channel = requests.post(url + 'channels/create', json=channel_profile).json()
#     log_out = requests.post(url + 'auth/logout', json={'token': user_1['token']}).json()
#     assert log_out['is_success'] == True

#     channel_profile = {
#         'token'     : 12,
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_3['u_id'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == AccessError.code

#     channel_profile = {
#         'token'     : -12,
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_3['u_id'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == AccessError.code

#     channel_profile = {
#         'token'     : 121.11,
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_3['u_id'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == AccessError.code

#     channel_profile = {
#         'token'     : user_2['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_1['token'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == AccessError.code

#     channel_profile = {
#         'token'     : user_2['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_3['token'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == AccessError.code

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_3['token'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == AccessError.code
#     requests.delete(url + '/clear')
#     clear()

# def test_channel_invite_invalid_self_invite_HTTP(url):
#     """Testing when user is not allowed to invite him/herself to channel
#     (Assumption testing) this error will be treated as AccessError
#     """
#     requests.delete(url + '/clear')
#     clear()
#     user_profile = {
#         'email'     : 'johnsmith@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Smith',
#     }
#     user = requests.post(url + 'auth/register', json=user_profile).json()

#     channel_profile = {
#         'token'    : user['token'],
#         'name'     : 'Group 1',
#         'is_public': True,
#     }
#     new_channel = requests.post(url + 'channels/create', json=channel_profile).json()

#     channel_profile = {
#         'token'     : user['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user['u_id'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == InputError.code
#     requests.delete(url + '/clear')
#     clear()

# def test_channel_multiple_invite_HTTP(url):
#     """Testing when user invites a user multiple times
#     (Assumption testing) this error will be treated as AccessError
#     """
#     requests.delete(url + '/clear')
#     clear()
#     user_profile = {
#         'email'     : 'johnsmith@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Smith',
#     }
#     user_1 = requests.post(url + 'auth/register', json=user_profile).json()

#     user_profile = {
#         'email'     : 'jennielin@gmail.com',
#         'password'  : 'password',
#         'name_first': 'Jennie',
#         'name_last' : 'Lin',
#     }
#     user_2 = requests.post(url + 'auth/register', json=user_profile).json()
#     channel_profile = {
#         'token'    : user_1['token'],
#         'name'     : 'Group 1',
#         'is_public': True,
#     }
#     new_channel = requests.post(url + 'channels/create', json=channel_profile).json()

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_2['u_id'],
#     }
#     channel_return = requests.post(url + 'channel/invite', json=channel_profile).json()
#     assert channel_return == {}

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_2['u_id'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == InputError.code

#     channel_profile = {
#         'token'     : user_2['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_2['u_id'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == InputError.code

#     channel_profile = {
#         'token'     : user_2['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_1['u_id'],
#     }
#     error = requests.post(url + 'channel/invite', json=channel_profile)
#     error.status_code == InputError.code
#     requests.delete(url + '/clear')
#     clear()

# #?------------------------------ Output Testing ------------------------------?#

# def test_channel_invite_successful_HTTP(url):
#     """Testing if user has successfully been invited to the channel
#     """
#     requests.delete(url + '/clear')
#     clear()
#     user_profile = {
#         'email'     : 'johnsmith@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Smith',
#     }
#     user_1 = requests.post(url + 'auth/register', json=user_profile).json()

#     user_profile = {
#         'email'     : 'jennielin@gmail.com',
#         'password'  : 'password',
#         'name_first': 'Jennie',
#         'name_last' : 'Lin',
#     }
#     user_2 = requests.post(url + 'auth/register', json=user_profile).json()

#     user_profile = {
#         'email'     : 'johnperry@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Perry',
#     }
#     user_3 = requests.post(url + 'auth/register', json=user_profile).json()

#     user_profile = {
#         'email'     : 'prathsjag@gmail.com',
#         'password'  : 'password',
#         'name_first': 'Praths',
#         'name_last' : 'Jag',
#     }
#     user_4 = requests.post(url + 'auth/register', json=user_profile).json()

#     channel_profile = {
#         'token'    : user_1['token'],
#         'name'     : 'Group 1',
#         'is_public': True,
#     }
#     new_channel = requests.post(url + 'channels/create', json=channel_profile).json()

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_2['u_id'],
#     }
#     channel_return = requests.post(url + 'channel/invite', json=channel_profile).json()
#     assert channel_return == {}

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': new_channel['channel_id'],
#     }
#     channel_information = requests.get(url + 'channel/details', json=channel_profile).json()
#     assert channel_information == {
#         'name': 'Group 1',
#         'owner_members': [
#             {
#                 'u_id': user_1['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Smith',
#             },
#         ],
#         'all_members': [
#             {
#                 'u_id': user_1['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Smith',
#             },
#             {
#                 'u_id': user_2['u_id'],
#                 'name_first': 'Jennie',
#                 'name_last': 'Lin',
#             },
#         ],
#     }

#     channel_profile = {
#         'token'     : user_2['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_3['u_id'],
#     }
#     channel_return = requests.post(url + 'channel/invite', json=channel_profile).json()
#     assert channel_return == {}

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': new_channel['channel_id'],
#     }
#     channel_information = requests.get(url + 'channel/details', json=channel_profile).json()
#     assert channel_information == {
#         'name': 'Group 1',
#         'owner_members': [
#             {
#                 'u_id': user_1['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Smith',
#             },
#         ],
#         'all_members': [
#             {
#                 'u_id': user_1['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Smith',
#             },
#             {
#                 'u_id': user_2['u_id'],
#                 'name_first': 'Jennie',
#                 'name_last': 'Lin',
#             },
#             {
#                 'u_id': user_3['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Perry',
#             },
#         ],
#     }

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_4['u_id'],
#     }
#     channel_return = requests.post(url + 'channel/invite', json=channel_profile).json()
#     assert channel_return == {}

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': new_channel['channel_id'],
#     }
#     channel_information = requests.get(url + 'channel/details', json=channel_profile).json()    
#     assert channel_information == {
#         'name': 'Group 1',
#         'owner_members': [
#             {
#                 'u_id': user_1['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Smith',
#             },
#         ],
#         'all_members': [
#             {
#                 'u_id': user_1['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Smith',
#             },
#             {
#                 'u_id': user_2['u_id'],
#                 'name_first': 'Jennie',
#                 'name_last': 'Lin',
#             },
#             {
#                 'u_id': user_3['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Perry',
#             },
#             {
#                 'u_id': user_4['u_id'],
#                 'name_first': 'Praths',
#                 'name_last': 'Jag',
#             },
#         ],
#     }
#     requests.delete(url + '/clear')
#     clear()

# def test_channel_invite_flockr_user_HTTP(url):
#     """(Assumption testing) first person to register is flockr owner
#     Testing if flockr owner has been successfully invited to channel and given ownership
#     """
#     requests.delete(url + '/clear')
#     clear()
#     user_profile = {
#         'email'     : 'johnsmith@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Smith',
#     }
#     user_1 = requests.post(url + 'auth/register', json=user_profile).json()

#     user_profile = {
#         'email'     : 'jennielin@gmail.com',
#         'password'  : 'password',
#         'name_first': 'Jennie',
#         'name_last' : 'Lin',
#     }
#     user_2 = requests.post(url + 'auth/register', json=user_profile).json()

#     user_profile = {
#         'email'     : 'johnperry@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Perry',
#     }
#     user_3 = requests.post(url + 'auth/register', json=user_profile).json()

#     channel_profile = {
#         'token'    : user_2['token'],
#         'name'     : 'Group 1',
#         'is_public': False,
#     }
#     new_channel = requests.post(url + 'channels/create', json=channel_profile).json()

#     channel_profile = {
#         'token'     : user_2['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_3['u_id'],
#     }
#     channel_return = requests.post(url + 'channel/invite', json=channel_profile).json()
#     assert channel_return == {}

#     channel_profile = {
#         'token'     : user_2['token'],
#         'channel_id': new_channel['channel_id'],
#     }
#     channel_information = requests.get(url + 'channel/details', json=channel_profile).json()
#     assert channel_information == {
#         'name': 'Group 1',
#         'owner_members': [
#             {
#                 'u_id': user_2['u_id'],
#                 'name_first': 'Jennie',
#                 'name_last': 'Lin',
#             },
#         ],
#         'all_members': [
#             {
#                 'u_id': user_2['u_id'],
#                 'name_first': 'Jennie',
#                 'name_last': 'Lin',
#             },
#             {
#                 'u_id': user_3['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Perry',
#             },
#         ],
#     }

#     channel_profile = {
#         'token'     : user_3['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_1['u_id'],
#     }
#     channel_return = requests.post(url + 'channel/invite', json=channel_profile).json()
#     assert channel_return == {}

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': new_channel['channel_id'],
#     }
#     channel_information = requests.get(url + 'channel/details', json=channel_profile).json()
#     assert channel_information == {
#         'name': 'Group 1',
#         'owner_members': [
#             {
#                 'u_id': user_2['u_id'],
#                 'name_first': 'Jennie',
#                 'name_last': 'Lin',
#             },
#             {
#                 'u_id': user_1['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Smith',
#             },
#         ],
#         'all_members': [
#             {
#                 'u_id': user_2['u_id'],
#                 'name_first': 'Jennie',
#                 'name_last': 'Lin',
#             },
#             {
#                 'u_id': user_3['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Perry',
#             },
#             {
#                 'u_id': user_1['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Smith',
#             },
#         ],
#     }
#     requests.delete(url + '/clear')
#     clear()

# #------------------------------------------------------------------------------#
# #                               channel/details                                #
# #------------------------------------------------------------------------------#

# #?-------------------------- Input/Access Error Testing ----------------------?#

# def test_channel_details_invalid_channel_HTTP(url):
#     """Testing if channel is invalid or does not exist
#     """
#     requests.delete(url + '/clear')
#     clear()
#     user_profile = {
#         'email'     : 'johnsmith@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Smith',
#     }
#     user = requests.post(url + 'auth/register', json=user_profile).json()

#     channel_profile = {
#         'token'     : user['token'],
#         'channel_id': -1,
#     }
#     error = requests.get(url + 'channel/details', json=channel_profile)
#     error.status_code == InputError.code

#     channel_profile = {
#         'token'     : user['token'],
#         'channel_id': -19,
#     }
#     error = requests.get(url + 'channel/details', json=channel_profile)
#     error.status_code == InputError.code

#     channel_profile = {
#         'token'     : user['token'],
#         'channel_id': '#@&!',
#     }
#     error = requests.get(url + 'channel/details', json=channel_profile)
#     error.status_code == InputError.code

#     channel_profile = {
#         'token'     : user['token'],
#         'channel_id': 121.12,
#     }
#     error = requests.get(url + 'channel/details', json=channel_profile)
#     error.status_code == InputError.code
#     requests.delete(url + '/clear')
#     clear()

# def test_channel_details_invalid_user_HTTP(url):
#     """Testing if unauthorized/invalid user is unable to access channel details
#     """
#     requests.delete(url + '/clear')
#     clear()
#     user_profile = {
#         'email'     : 'johnsmith@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Smith',
#     }
#     user_1 = requests.post(url + 'auth/register', json=user_profile).json()

#     user_profile = {
#         'email'     : 'jennielin@gmail.com',
#         'password'  : 'password',
#         'name_first': 'Jennie',
#         'name_last' : 'Lin',
#     }
#     user_2 = requests.post(url + 'auth/register', json=user_profile).json()
    
#     channel_profile = {
#         'token'    : user_1['token'],
#         'name'     : 'Group 1',
#         'is_public': True,
#     }
#     new_channel = requests.post(url + 'channels/create', json=channel_profile).json()

#     channel_profile = {
#         'token'     : user_2['token'],
#         'channel_id': new_channel['channel_id'],
#     }
#     error = requests.get(url + 'channel/details', json=channel_profile)
#     error.status_code == AccessError.code
#     requests.delete(url + '/clear')
#     clear()

# def test_channel_details_invalid_token_HTTP(url):
#     """Testing if given invalid token returns an AccessError
#     """
#     requests.delete(url + '/clear')
#     clear()
#     user_profile = {
#         'email'     : 'johnsmith@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Smith',
#     }
#     user_1 = requests.post(url + 'auth/register', json=user_profile).json()

#     channel_profile = {
#         'token'    : user_1['token'],
#         'name'     : 'Group 1',
#         'is_public': True,
#     }
#     new_channel = requests.post(url + 'channels/create', json=channel_profile).json()

#     channel_profile = {
#         'token'     : 6.333,
#         'channel_id': 0,
#     }
#     error = requests.get(url + 'channel/details', json=channel_profile)
#     error.status_code == AccessError.code

#     channel_profile = {
#         'token'     : '@^!&',
#         'channel_id': -3,
#     }
#     error = requests.get(url + 'channel/details', json=channel_profile)
#     error.status_code == AccessError.code

#     channel_profile = {
#         'token'     : -1,
#         'channel_id': new_channel['channel_id'],
#     }
#     error = requests.get(url + 'channel/details', json=channel_profile)
#     error.status_code == AccessError.code

#     channel_profile = {
#         'token'     : 'abcd',
#         'channel_id': new_channel['channel_id'],
#     }
#     error = requests.get(url + 'channel/details', json=channel_profile)
#     error.status_code == AccessError.code
#     requests.delete(url + '/clear')
#     clear()

# #?------------------------------ Output Testing ------------------------------?#

# def test_channel_details_authorized_user_HTTP(url):
#     """Testing the required correct details of a channel
#     """
#     requests.delete(url + '/clear')
#     clear()
#     user_profile = {
#         'email'     : 'johnsmith@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Smith',
#     }
#     user_1 = requests.post(url + 'auth/register', json=user_profile).json()

#     user_profile = {
#         'email'     : 'jennielin@gmail.com',
#         'password'  : 'password',
#         'name_first': 'Jennie',
#         'name_last' : 'Lin',
#     }
#     user_2 = requests.post(url + 'auth/register', json=user_profile).json()

#     user_profile = {
#         'email'     : 'johnperry@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Perry',
#     }
#     user_3 = requests.post(url + 'auth/register', json=user_profile).json()

#     user_profile = {
#         'email'     : 'prathsjag@gmail.com',
#         'password'  : 'password',
#         'name_first': 'Praths',
#         'name_last' : 'Jag',
#     }
#     user_4 = requests.post(url + 'auth/register', json=user_profile).json()

#     channel_profile = {
#         'token'    : user_1['token'],
#         'name'     : 'Group 1',
#         'is_public': True,
#     }
#     new_channel = requests.post(url + 'channels/create', json=channel_profile).json()

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_2['u_id'],
#     }
#     channel_return = requests.post(url + 'channel/invite', json=channel_profile).json()
#     assert channel_return == {}

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': new_channel['channel_id'],
#     }
#     channel_information = requests.get(url + 'channel/details', json=channel_profile).json()
#     assert channel_information == {
#         'name': 'Group 1',
#         'owner_members': [
#             {
#                 'u_id': user_1['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Smith',
#             },
#         ],
#         'all_members': [
#             {
#                 'u_id': user_1['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Smith',
#             },
#             {
#                 'u_id': user_2['u_id'],
#                 'name_first': 'Jennie',
#                 'name_last': 'Lin',
#             },
#         ],
#     }

#     channel_profile = {
#         'token'     : user_2['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_3['u_id'],
#     }
#     channel_return = requests.post(url + 'channel/invite', json=channel_profile).json()
#     assert channel_return == {}
    
#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': new_channel['channel_id'],
#     }
#     channel_information = requests.get(url + 'channel/details', json=channel_profile).json()
#     assert channel_information == {
#         'name': 'Group 1',
#         'owner_members': [
#             {
#                 'u_id': user_1['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Smith',
#             },
#         ],
#         'all_members': [
#             {
#                 'u_id': user_1['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Smith',
#             },
#             {
#                 'u_id': user_2['u_id'],
#                 'name_first': 'Jennie',
#                 'name_last': 'Lin',
#             },
#             {
#                 'u_id': user_3['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Perry',
#             },
#         ],
#     }

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': new_channel['channel_id'],
#         'u_id'      : user_4['u_id'],
#     }
#     channel_return = requests.post(url + 'channel/invite', json=channel_profile).json()
#     assert channel_return == {}

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': new_channel['channel_id'],
#     }
#     channel_information = requests.get(url + 'channel/details', json=channel_profile).json()    
#     assert channel_information == {
#         'name': 'Group 1',
#         'owner_members': [
#             {
#                 'u_id': user_1['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Smith',
#             },
#         ],
#         'all_members': [
#             {
#                 'u_id': user_1['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Smith',
#             },
#             {
#                 'u_id': user_2['u_id'],
#                 'name_first': 'Jennie',
#                 'name_last': 'Lin',
#             },
#             {
#                 'u_id': user_3['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Perry',
#             },
#             {
#                 'u_id': user_4['u_id'],
#                 'name_first': 'Praths',
#                 'name_last': 'Jag',
#             },
#         ],
#     }
#     requests.delete(url + '/clear')
#     clear()

# def test_output_details_twice_HTTP(url):
#     """Test if details will be shown when a second channel is created.
#     """
#     requests.delete(url + '/clear')
#     clear()
#     user_profile = {
#         'email'     : 'johnsmith@gmail.com',
#         'password'  : 'password',
#         'name_first': 'John',
#         'name_last' : 'Smith',
#     }
#     user_1 = requests.post(url + 'auth/register', json=user_profile).json()

#     user_profile = {
#         'email'     : 'jennielin@gmail.com',
#         'password'  : 'password',
#         'name_first': 'Jennie',
#         'name_last' : 'Lin',
#     }
#     user_2 = requests.post(url + 'auth/register', json=user_profile).json()
    
#     channel_profile = {
#         'token'    : user_1['token'],
#         'name'     : 'Group 2',
#         'is_public': True,
#     }
#     new_channel_2 = requests.post(url + 'channels/create', json=channel_profile).json()
    
#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': new_channel_2['channel_id'],
#         'u_id'      : user_2['u_id'],
#     }
#     channel_return = requests.post(url + 'channel/invite', json=channel_profile).json()
#     assert channel_return == {}

#     channel_profile = {
#         'token'     : user_1['token'],
#         'channel_id': new_channel_2['channel_id'],
#     }
#     channel_information = requests.get(url + 'channel/details', json=channel_profile).json()
#     assert channel_information == {
#         'name': 'Group 2',
#         'owner_members': [
#             {
#                 'u_id': user_1['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Smith',
#             },
#         ],
#         'all_members': [
#             {
#                 'u_id': user_1['u_id'],
#                 'name_first': 'John',
#                 'name_last': 'Smith',
#             },
#             {
#                 'u_id': user_2['u_id'],
#                 'name_first': 'Jennie',
#                 'name_last': 'Lin',
#             },
#         ],
#     }
#     requests.delete(url + '/clear')
#     clear()

# ------------------------------------------------------------------------------#
#                               channel/messages                               #
# ------------------------------------------------------------------------------#

# ?-------------------------- Input/Access Error Testing ----------------------?#


# ?------------------------------ Output Testing ------------------------------?#



# ------------------------------------------------------------------------------#
#                               channel/leave                                  #
# ------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_input_leave_channel_id(url, user_1):
    """Testing when an invalid channel_id is used as a parameter
    """
    payload = requests.post(f'{url}/channel/leave', json={
        'token': user_1['token'], 
        'channel_id': -1
    })
    assert payload.status_code == InputError.code

    payload = requests.post(f'{url}/channel/leave', json={
        'token': user_1['token'], 
        'channel_id': 0
    })
    assert payload.status_code == InputError.code

    payload = requests.post(f'{url}/channel/leave', json={
        'token': user_1['token'], 
        'channel_id': 1
    })
    assert payload.status_code == InputError.code

    requests.delete(f'{url}/clear')

def test_access_leave_user_is_member(url, user_1, user_2):
    """Testing if a user was not in the channel initially
    """
    channel_data_1 = requests.post(f'{url}/channels/create', json={
        'token': user_1['token'],
        'name': 'Group 1',
        'is_public': True,
    }).json()

    channel_data_2 = requests.post(f'{url}/channels/create', json={
        'token': user_2['token'],
        'name': 'Group 1',
        'is_public': True,
    }).json()

    payload = requests.post(f'{url}/channel/leave', json={
        'token': user_1['token'],
        'channel_id': channel_data_2['channel_id']
    })
    assert payload.status_code == AccessError.code

    payload = requests.post(f'{url}/channel/leave', json={
        'token': user_2['token'], 
        'channel_id': channel_data_1['channel_id']
    })
    assert payload.status_code == AccessError.code

    requests.delete(f'{url}/clear')


def test_access_leave_valid_token(url, user_1, default_channel):
    """Testing if token is valid
    """
    requests.post(f'{url}/auth/logout', json={'token': user_1['token']})

    payload = requests.post(f'{url}/channel/leave', json={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id']
    })
    assert payload.status_code == AccessError.code

    requests.delete(f'{url}/clear')


#?------------------------------ Output Testing ------------------------------?#

def test_output_user_leave_public(url, user_1, default_channel):
    """Testing if the user has successfully left a public channel
    """
    requests.post(f'{url}/channel/leave', json={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id']
    })

    payload = requests.get(f'{url}/channels/list', params={'token': user_1['token']}).json()
    assert payload['channels'] == []
    requests.delete(f'{url}/clear')

def test_output_user_leave_private(url, user_1, default_channel):
    """Testing if the user has successfully left a private channel
    """
    requests.post(f'{url}/channel/leave', json={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id']
    })

    payload = requests.get(f'{url}/channels/list', params={'token': user_1['token']}).json()
    assert payload['channels'] == []
    requests.delete(f'{url}/clear')


def test_output_user_leave_channels(url, user_1, default_channel):
    """Testing if user has left the correct channel and that channel is no longer
    on the user's own channel list
    """
    requests.post(f'{url}/channels/create', json={
        'token': user_1['token'],
        'name': 'Group 2',
        'is_public': False,
    })
    channel_3 = requests.post(f'{url}/channels/create', json={
        'token': user_1['token'],
        'name': 'Group 3',
        'is_public': False,
    }).json()
    requests.post(f'{url}/channel/leave', json={
        'token': user_1['token'],
        'channel_id': channel_3['channel_id']
    })

    payload = requests.get(f'{url}/channels/list', params={'token': user_1['token']}).json()
    leave_channel = {
        'channel_id': channel_3['channel_id'],
        'name': 'Group 3',
    }
    assert leave_channel not in payload['channels']
    requests.delete(f'{url}/clear')

@pytest.mark.skip(reason="testing relies on other routes")
def test_output_leave_channels(url, user_1, user_2):
    """Testing when user leaves multiple channels
    """
    channel_leave_1 = requests.post(f'{url}/channels/create', json={
        'token': user_1['token'],
        'name': 'Group 1',
        'is_public': False,
    }).json()
    requests.post(f'{url}/channel/leave', json={
        'token': user_1['token'],
        'channel_id': channel_leave_1['channel_id']
    })

    channel_leave_2 = requests.post(f'{url}/channels/create', json={
        'token': user_2['token'],
        'name': 'Group 1',
        'is_public': False,
    }).json()
    requests.post(f'{url}/channel/addowner', json={
        'token': user_2['token'], 
        'channel_id': channel_leave_2['channel_id'],
        'u_id': user_1['u_id']
    })

    requests.post(f'{url}/channel/leave', json={
        'token': user_1['token'],
        'channel_id': channel_leave_1['channel_id']
    })

    payload = requests.get(f'{url}/channels/list', params={'token': user_1['token']}).json()
    assert payload['channels'] == []
    requests.delete(f'{url}/clear')

def test_output_member_leave(url, user_1, user_2, user_3, default_channel):
    """Testing when a member leaves that it does not delete the channel. Covers 
    also if user infomation has been erased on channel's end.
    """
    requests.post(f'{url}/channel/invite', json={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id': user_2['u_id'],
    })
    requests.post(f'{url}/channel/invite', json={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id': user_3['u_id'],
    })
    requests.post(f'{url}/channel/leave', json={
        'token': user_3['token'],
        'channel_id': default_channel['channel_id']
    })

    payload = requests.get(f'{url}channel/details', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id']
    }).json()
    for member in payload['all_members']:
        assert member['u_id'] != user_3['u_id']
    requests.delete(f'{url}/clear')

@pytest.mark.skip(reason="testing relies on other routes")
def test_output_all_members_leave(url, user_1, user_2, default_channel):
    """Test if the channel is deleted when all members leave
    """
    requests.post(f'{url}/channel/invite', json={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id': user_2['u_id'],
    })
    
    requests.post(f'{url}/channel/leave', json={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id']
    })

    requests.post(f'{url}/channel/leave', json={
        'token': user_2['token'],
        'channel_id': default_channel['channel_id']
    })

    payload = requests.post(f'{url}/channels/listall', json={
        'token': user_1['token'],
    }).json()

    for curr_channel in payload['channels']:
        assert curr_channel['channel_id'] != default_channel['channel_id']

    requests.delete(f'{url}/clear')

@pytest.mark.skip(reason="testing relies on other routes")
def test_output_flockr_rejoin_channel(url, user_1, user_2, default_channel):
    """Test when the flockr owner leaves and comes back that the user status is an
    owner.
    """

    requests.post(f'{url}/channel/invite', json={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id': user_2['u_id'],
    })
    
    requests.post(f'{url}/channel/leave', json={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id']
    })

    requests.post(f'{url}/channel/join', json={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id']
    })

    payload = requests.post(f'{url}/channel/details', json={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id']
    }).json()

    user_1_details = {'u_id': user_1['u_id'], 'name_first': 'Jane', 'name_last': 'Smith'}
    assert user_1_details in payload['owner_members']
    assert user_1_details in payload['all_members']

    requests.delete(f'{url}/clear')

@pytest.mark.skip(reason="testing relies on other routes")
def test_output_creator_rejoin_channel(url, user_1, user_2, user_3, default_channel):
    """Test when the the creator leaves and comes back that the user status is a member.
    """

    requests.post(f'{url}/channel/invite', json={
        'token': user_2['token'],
        'channel_id': default_channel['channel_id'],
        'u_id': user_3['u_id'],
    })
    
    requests.post(f'{url}/channel/leave', json={
        'token': user_2['token'],
        'channel_id': default_channel['channel_id']
    })

    requests.post(f'{url}/channel/join', json={
        'token': user_2['token'],
        'channel_id': default_channel['channel_id']
    })

    payload = requests.post(f'{url}/channel/details', json={
        'token': user_2['token'],
        'channel_id': default_channel['channel_id']
    }).json()

    user_2_details = {'u_id': user_2['u_id'], 'name_first': 'Jane', 'name_last': 'Smith'}
    assert user_2_details not in payload['owner_members']
    assert user_2_details in payload['all_members']

    requests.delete(f'{url}/clear')
    

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



