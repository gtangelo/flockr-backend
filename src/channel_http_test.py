import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json

from datetime import datetime, timezone
from decimal import InvalidContext
import auth
import channel
import channels
from message import message_send
from other import clear
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

def test_channel_invite_login_user(url):
    """Testing invalid token for users which have logged out
    """
    clear()
    user_profile = {
        'email'     : 'johnsmith@gmail.com',
        'password'  : 'password',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    user_1 = requests.post(url + 'auth/register', params=user_profile).json()

    user_profile = {
        'email'     : 'jennielin@gmail.com',
        'password'  : 'password',
        'name_first': 'Jennie',
        'name_last' : 'Lin',
    }
    user_2 = requests.post(url + 'auth/register', params=user_profile).json()

    user_profile = {
        'email'     : 'johnperry@gmail.com',
        'password'  : 'password',
        'name_first': 'John',
        'name_last' : 'Perry',
    }
    user_3 = requests.post(url + 'auth/register', params=user_profile).json()

    user_profile = {
        'email'     : 'prathsjag@gmail.com',
        'password'  : 'password',
        'name_first': 'Praths',
        'name_last' : 'Jag',
    }
    user_4 = requests.post(url + 'auth/register', params=user_profile).json()

    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': True,
    }
    new_channel = requests.post(url + 'channels/create', params=channel_profile).json()

    log_out = requests.post(url + 'auth/logout', params={'token': user_1['token']}).json()
    assert log_out == True
    log_out = requests.post(url + 'auth/logout', params={'token': user_2['token']}).json()
    assert log_out == True
    log_out = requests.post(url + 'auth/logout', params={'token': user_3['token']}).json()
    assert log_out == True
    log_out = requests.post(url + 'auth/logout', params={'token': user_4['token']}).json()
    assert log_out == True

    with pytest.raises(AccessError):
        channel_profile = {
            'token'     : user_1['token'],
            'channel_id': new_channel['channel_id'],
            'u_id'      : user_1['u_id'],
        }
        requests.post(url + 'channel/invite', params=channel_profile).json()

    with pytest.raises(AccessError):
        channel_profile = {
            'token'     : user_2['token'],
            'channel_id': new_channel['channel_id'],
            'u_id'      : user_3['u_id'],
        }
        requests.post(url + 'channel/invite', params=channel_profile).json()

    with pytest.raises(AccessError):
        channel_profile = {
            'token'     : user_3['token'],
            'channel_id': new_channel['channel_id'],
            'u_id'      : user_3['u_id'],
        }
        requests.post(url + 'channel/invite', params=channel_profile).json()

    with pytest.raises(AccessError):
        channel_profile = {
            'token'     : user_4['token'],
            'channel_id': new_channel['channel_id'],
            'u_id'      : user_3['u_id'],
        }
        requests.post(url + 'channel/invite', params=channel_profile).json()
    clear()

def test_channel_invite_wrong_data_type():
    """Testing when wrong data types are used as input
    """
    clear()
    user_profile = {
        'email'     : 'johnsmith@gmail.com',
        'password'  : 'password',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    user = requests.post(url + 'auth/register', params=user_profile).json()
    
    channel_profile = {
        'token'    : user['token'],
        'name'     : 'Group 1',
        'is_public': True,
    }
    new_channel = requests.post(url + 'channels/create', params=channel_profile).json()

    with pytest.raises(InputError):
        channel_profile = {
            'token'     : user['token'],
            'channel_id': new_channel['channel_id'],
            'u_id'      : -1,
        }
        requests.post(url + 'channel/invite', params=channel_profile).json()

    with pytest.raises(InputError):
        channel_profile = {
            'token'     : user['token'],
            'channel_id': new_channel['channel_id'],
            'u_id'      : '@#$!',
        }
        requests.post(url + 'channel/invite', params=channel_profile).json()

    with pytest.raises(InputError):
        channel_profile = {
            'token'     : user['token'],
            'channel_id': new_channel['channel_id'],
            'u_id'      : 67.666,
        }
        requests.post(url + 'channel/invite', params=channel_profile).json()
    clear()

def test_channel_invite_invalid_user():
    """Testing when invalid user is invited to channel
    """
    clear()
    user_profile = {
        'email'     : 'johnsmith@gmail.com',
        'password'  : 'password',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    user = requests.post(url + 'auth/register', params=user_profile).json()

    channel_profile = {
        'token'    : user['token'],
        'name'     : 'Group 1',
        'is_public': True,
    }
    new_channel = requests.post(url + 'channels/create', params=channel_profile).json()

    with pytest.raises(InputError):
        channel_profile = {
            'token'     : user['token'],
            'channel_id': new_channel['channel_id'],
            'u_id'      : user['u_id'] + 1,
        }
        requests.post(url + 'channel/invite', params=channel_profile).json()

    with pytest.raises(InputError):
        channel_profile = {
            'token'     : user['token'],
            'channel_id': new_channel['channel_id'],
            'u_id'      : user['u_id'] - 1,
        }
        requests.post(url + 'channel/invite', params=channel_profile).json()
    clear()

def test_channel_invite_invalid_channel():
    """Testing when valid user is invited to invalid channel
    """
    clear()
    user_profile = {
        'email'     : 'johnsmith@gmail.com',
        'password'  : 'password',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    user_1 = requests.post(url + 'auth/register', params=user_profile).json()

    user_profile = {
        'email'     : 'jennielin@gmail.com',
        'password'  : 'password',
        'name_first': 'Jennie',
        'name_last' : 'Lin',
    }
    user_2 = requests.post(url + 'auth/register', params=user_profile).json()

    with pytest.raises(InputError):
        channel_profile = {
            'token'     : user_1['token'],
            'channel_id': -122,
            'u_id'      : user_2['u_id'],
        }
        requests.post(url + 'channel/invite', params=channel_profile).json()

    with pytest.raises(InputError):
        channel_profile = {
            'token'     : user_1['token'],
            'channel_id': -642,
            'u_id'      : user_2['u_id'],
        }
        requests.post(url + 'channel/invite', params=channel_profile).json()

    with pytest.raises(InputError):
        channel_profile = {
            'token'     : user_1['token'],
            'channel_id': '@#@!',
            'u_id'      : user_2['u_id'],
        }
        requests.post(url + 'channel/invite', params=channel_profile).json()

    with pytest.raises(InputError):
        channel_profile = {
            'token'     : user_1['token'],
            'channel_id': 212.11,
            'u_id'      : user_2['u_id'],
        }
        requests.post(url + 'channel/invite', params=channel_profile).json()
    clear()

def test_channel_invite_not_authorized():
    """Testing when user is not authorized to invite other users to channel
    (Assumption) This includes an invalid user inviting users to channel
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    auth.auth_logout(user_1['token'])

    with pytest.raises(AccessError):
        channel.channel_invite(12, new_channel['channel_id'], user_3['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(-12, new_channel['channel_id'], user_3['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(121.11, new_channel['channel_id'], user_3['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(user_2['token'], new_channel['channel_id'], user_1['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(user_2['token'], new_channel['channel_id'], user_3['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(user_1['token'], new_channel['channel_id'], user_3['u_id'])
    clear()

def test_channel_invite_invalid_self_invite():
    """Testing when user is not allowed to invite him/herself to channel
    (Assumption testing) this error will be treated as AccessError
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)

    with pytest.raises(InputError):
        channel.channel_invite(user['token'], new_channel['channel_id'], user['u_id'])
    clear()

def test_channel_multiple_invite():
    """Testing when user invites a user multiple times
    (Assumption testing) this error will be treated as AccessError
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    assert channel.channel_invite(user_1['token'], new_channel['channel_id'], user_2['u_id']) == {}

    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], new_channel['channel_id'], user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_invite(user_2['token'], new_channel['channel_id'], user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_invite(user_2['token'], new_channel['channel_id'], user_1['u_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_channel_invite_successful():
    """Testing if user has successfully been invited to the channel
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    user_4 = auth.auth_register('prathsjag@gmail.com', 'password', 'Praths', 'Jag')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)

    channel.channel_invite(user_1['token'], new_channel['channel_id'], user_2['u_id'])
    assert channel.channel_details(user_1['token'], new_channel['channel_id']) == {
        'name': 'Group 1',
        'owner_members': [
            {
                'u_id': user_1['u_id'],
                'name_first': 'John',
                'name_last': 'Smith',
            },
        ],
        'all_members': [
            {
                'u_id': user_1['u_id'],
                'name_first': 'John',
                'name_last': 'Smith',
            },
            {
                'u_id': user_2['u_id'],
                'name_first': 'Jennie',
                'name_last': 'Lin',
            },
        ],
    }

    channel.channel_invite(user_2['token'], new_channel['channel_id'], user_3['u_id'])
    assert channel.channel_details(user_1['token'], new_channel['channel_id']) == {
        'name': 'Group 1',
        'owner_members': [
            {
                'u_id': user_1['u_id'],
                'name_first': 'John',
                'name_last': 'Smith',
            },
        ],
        'all_members': [
            {
                'u_id': user_1['u_id'],
                'name_first': 'John',
                'name_last': 'Smith',
            },
            {
                'u_id': user_2['u_id'],
                'name_first': 'Jennie',
                'name_last': 'Lin',
            },
            {
                'u_id': user_3['u_id'],
                'name_first': 'John',
                'name_last': 'Perry',
            },
        ],
    }

    channel.channel_invite(user_1['token'], new_channel['channel_id'], user_4['u_id'])
    assert channel.channel_details(user_1['token'], new_channel['channel_id']) == {
        'name': 'Group 1',
        'owner_members': [
            {
                'u_id': user_1['u_id'],
                'name_first': 'John',
                'name_last': 'Smith',
            },
        ],
        'all_members': [
            {
                'u_id': user_1['u_id'],
                'name_first': 'John',
                'name_last': 'Smith',
            },
            {
                'u_id': user_2['u_id'],
                'name_first': 'Jennie',
                'name_last': 'Lin',
            },
            {
                'u_id': user_3['u_id'],
                'name_first': 'John',
                'name_last': 'Perry',
            },
            {
                'u_id': user_4['u_id'],
                'name_first': 'Praths',
                'name_last': 'Jag',
            },
        ],
    }
    clear()

def test_channel_invite_flockr_user():
    """(Assumption testing) first person to register is flockr owner
    Testing if flockr owner has been successfully invited to channel and given ownership
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    new_channel = channels.channels_create(user_2['token'], 'Group 1', False)

    channel.channel_invite(user_2['token'], new_channel['channel_id'], user_3['u_id'])
    assert channel.channel_details(user_2['token'], new_channel['channel_id']) == {
        'name': 'Group 1',
        'owner_members': [
            {
                'u_id': user_2['u_id'],
                'name_first': 'Jennie',
                'name_last': 'Lin',
            },
        ],
        'all_members': [
            {
                'u_id': user_2['u_id'],
                'name_first': 'Jennie',
                'name_last': 'Lin',
            },
            {
                'u_id': user_3['u_id'],
                'name_first': 'John',
                'name_last': 'Perry',
            },
        ],
    }

    channel.channel_invite(user_3['token'], new_channel['channel_id'], user_1['u_id'])
    assert channel.channel_details(user_1['token'], new_channel['channel_id']) == {
        'name': 'Group 1',
        'owner_members': [
            {
                'u_id': user_2['u_id'],
                'name_first': 'Jennie',
                'name_last': 'Lin',
            },
            {
                'u_id': user_1['u_id'],
                'name_first': 'John',
                'name_last': 'Smith',
            },
        ],
        'all_members': [
            {
                'u_id': user_2['u_id'],
                'name_first': 'Jennie',
                'name_last': 'Lin',
            },
            {
                'u_id': user_3['u_id'],
                'name_first': 'John',
                'name_last': 'Perry',
            },
            {
                'u_id': user_1['u_id'],
                'name_first': 'John',
                'name_last': 'Smith',
            },
        ],
    }
    clear()

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

#?-------------------------- Input/Access Error Testing ----------------------?#


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


