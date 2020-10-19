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
    payload = requests.post(f'{url}auth/register', json=data)
    return payload.json()

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_input_leave_channel_id(url):
    """Testing when an invalid channel_id is used as a parameter
    """
    requests.delete(f'{url}/clear')
    user = register_default_user(url, 'John', 'Smith')

    payload = requests.post(f'{url}/channel/leave', json={
        'token': user['token'], 
        'channel_id': -1
    })
    assert payload.status_code == InputError.code

    payload = requests.post(f'{url}/channel/leave', json={
        'token': user['token'], 
        'channel_id': 0
    })
    assert payload.status_code == InputError.code

    payload = requests.post(f'{url}/channel/leave', json={
        'token': user['token'], 
        'channel_id': 1
    })
    assert payload.status_code == InputError.code

    requests.delete(f'{url}/clear')

def test_access_leave_user_is_member(url):
    """Testing if a user was not in the channel initially
    """
    requests.delete(f'{url}/clear')
    user_1 = register_default_user(url, 'John', 'Smith')
    user_2 = register_default_user(url, 'Jane', 'Smith')

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


def test_access_leave_valid_token(url):
    """Testing if token is valid
    """
    requests.delete(f'{url}/clear')
    user = register_default_user(url, 'John', 'Smith')

    channel_data = requests.post(f'{url}/channels/create', json={
        'token': user['token'],
        'name': 'Group 1',
        'is_public': True,
    }).json()
    requests.post(f'{url}/auth/logout', json={'token': user['token']})

    payload = requests.post(f'{url}/channel/leave', json={
        'token': user['token'],
        'channel_id': channel_data['channel_id']
    })
    assert payload.status_code == AccessError.code

    requests.delete(f'{url}/clear')


#?------------------------------ Output Testing ------------------------------?#

def test_output_user_leave_public(url):
    """Testing if the user has successfully left a public channel
    """
    requests.delete(f'{url}/clear')
    user = register_default_user(url, 'John', 'Smith')
    channel_data = requests.post(f'{url}/channels/create', json={
        'token': user['token'],
        'name': 'Group 1',
        'is_public': True,
    }).json()
    requests.post(f'{url}/channel/leave', json={
        'token': user['token'],
        'channel_id': channel_data['channel_id']
    })

    payload = requests.get(f'{url}/channels/list', json={'token': user['token']}).json()
    assert payload['channels'] == []
    requests.delete(f'{url}/clear')

def test_output_user_leave_private(url):
    """Testing if the user has successfully left a private channel
    """
    requests.delete(f'{url}/clear')
    user = register_default_user(url, 'John', 'Smith')
    channel_data = requests.post(f'{url}/channels/create', json={
        'token': user['token'],
        'name': 'Group 1',
        'is_public': False,
    }).json()
    requests.post(f'{url}/channel/leave', json={
        'token': user['token'],
        'channel_id': channel_data['channel_id']
    })

    payload = requests.get(f'{url}/channels/list', json={'token': user['token']}).json()
    assert payload['channels'] == []
    requests.delete(f'{url}/clear')


def test_output_user_leave_channels(url):
    """Testing if user has left the correct channel and that channel is no longer
    on the user's own channel list
    """
    requests.delete(f'{url}/clear')
    user = register_default_user(url, 'John', 'Smith')
    channel_data = requests.post(f'{url}/channels/create', json={
        'token': user['token'],
        'name': 'Group 1',
        'is_public': False,
    }).json()
    requests.post(f'{url}/channels/create', json={
        'token': user['token'],
        'name': 'Group 2',
        'is_public': False,
    })
    requests.post(f'{url}/channels/create', json={
        'token': user['token'],
        'name': 'Group 3',
        'is_public': False,
    })
    requests.post(f'{url}/channel/leave', json={
        'token': user['token'],
        'channel_id': channel_data['channel_id']
    })

    payload = requests.get(f'{url}/channels/list', json={'token': user['token']}).json()
    leave_channel = {
        'channel_id': channel_data['channel_id'],
        'name': 'Group 1',
    }
    assert leave_channel not in payload['channels']
    requests.delete(f'{url}/clear')

@pytest.mark.skip(reason="testing relies on other routes")
def test_output_leave_channels(url):
    """Testing when user leaves multiple channels
    """

    requests.delete(f'{url}/clear')
    user_1 = register_default_user(url, 'John', 'Smith')
    user_2 = register_default_user(url, 'Jane', 'Smith')
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

    payload = requests.get(f'{url}/channels/list', json={'token': user_1['token']}).json()
    assert payload['channels'] == []
    requests.delete(f'{url}/clear')

def test_output_member_leave(url):
    """Testing when a member leaves that it does not delete the channel. Covers 
    also if user infomation has been erased on channel's end.
    """
    requests.delete(f'{url}/clear')
    user_1 = register_default_user(url, 'John', 'Smith')
    user_2 = register_default_user(url, 'Jane', 'Smith')
    user_3 = register_default_user(url, 'Jace', 'Smith')

    channel_leave = requests.post(f'{url}/channels/create', json={
        'token': user_1['token'],
        'name': 'Group 1',
        'is_public': True,
    }).json()

    requests.post(f'{url}/channel/invite', json={
        'token': user_1['token'],
        'channel_id': channel_leave['channel_id'],
        'u_id': user_2['u_id'],
    })
    requests.post(f'{url}/channel/invite', json={
        'token': user_1['token'],
        'channel_id': channel_leave['channel_id'],
        'u_id': user_3['u_id'],
    })
    
    requests.post(f'{url}/channel/leave', json={
        'token': user_3['token'],
        'channel_id': channel_leave['channel_id']
    })

    payload = requests.get(f'{url}/channel/details', json={
        'token': user_1['token'],
        'channel_id': channel_leave['channel_id']
    }).json()
    for member in payload['all_members']:
        assert member['u_id'] != user_3['u_id']
    requests.delete(f'{url}/clear')

@pytest.mark.skip(reason="testing relies on other routes")
def test_output_all_members_leave(url):
    """Test if the channel is deleted when all members leave
    """
    requests.delete(f'{url}/clear')
    user_1 = register_default_user(url, 'John', 'Smith')
    user_2 = register_default_user(url, 'Jane', 'Smith')

    channel_leave = requests.post(f'{url}/channels/create', json={
        'token': user_1['token'],
        'name': 'Group 1',
        'is_public': True,
    }).json()

    requests.post(f'{url}/channel/invite', json={
        'token': user_1['token'],
        'channel_id': channel_leave['channel_id'],
        'u_id': user_2['u_id'],
    })
    
    requests.post(f'{url}/channel/leave', json={
        'token': user_1['token'],
        'channel_id': channel_leave['channel_id']
    })

    requests.post(f'{url}/channel/leave', json={
        'token': user_2['token'],
        'channel_id': channel_leave['channel_id']
    })

    payload = requests.post(f'{url}/channels/listall', json={
        'token': user_1['token'],
    }).json()

    for curr_channel in payload['channels']:
        assert curr_channel['channel_id'] != channel_leave['channel_id']

    requests.delete(f'{url}/clear')

@pytest.mark.skip(reason="testing relies on other routes")
def test_output_flockr_rejoin_channel(url):
    """Test when the flockr owner leaves and comes back that the user status is an
    owner.
    """
    requests.delete(f'{url}/clear')
    user_1 = register_default_user(url, 'John', 'Smith')
    user_2 = register_default_user(url, 'Jane', 'Smith')

    channel_leave = requests.post(f'{url}/channels/create', json={
        'token': user_1['token'],
        'name': 'Group 1',
        'is_public': True,
    }).json()

    requests.post(f'{url}/channel/invite', json={
        'token': user_1['token'],
        'channel_id': channel_leave['channel_id'],
        'u_id': user_2['u_id'],
    })
    
    requests.post(f'{url}/channel/leave', json={
        'token': user_1['token'],
        'channel_id': channel_leave['channel_id']
    })

    requests.post(f'{url}/channel/join', json={
        'token': user_1['token'],
        'channel_id': channel_leave['channel_id']
    })

    payload = requests.post(f'{url}/channel/details', json={
        'token': user_1['token'],
        'channel_id': channel_leave['channel_id']
    }).json()

    user_1_details = {'u_id': user_1['u_id'], 'name_first': 'Jane', 'name_last': 'Smith'}
    assert user_1_details in payload['owner_members']
    assert user_1_details in payload['all_members']

    requests.delete(f'{url}/clear')

@pytest.mark.skip(reason="testing relies on other routes")
def test_output_creator_rejoin_channel(url):
    """Test when the the creator leaves and comes back that the user status is a member.
    """
    requests.delete(f'{url}/clear')
    register_default_user(url, 'John', 'Smith')
    user_2 = register_default_user(url, 'Jane', 'Smith')
    user_3 = register_default_user(url, 'Jace', 'Smith')

    channel_leave = requests.post(f'{url}/channels/create', json={
        'token': user_2['token'],
        'name': 'Group 1',
        'is_public': True,
    }).json()

    requests.post(f'{url}/channel/invite', json={
        'token': user_2['token'],
        'channel_id': channel_leave['channel_id'],
        'u_id': user_3['u_id'],
    })
    
    requests.post(f'{url}/channel/leave', json={
        'token': user_2['token'],
        'channel_id': channel_leave['channel_id']
    })

    requests.post(f'{url}/channel/join', json={
        'token': user_2['token'],
        'channel_id': channel_leave['channel_id']
    })

    payload = requests.post(f'{url}/channel/details', json={
        'token': user_2['token'],
        'channel_id': channel_leave['channel_id']
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


