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
    """Testing if user has left the correct channel.
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
    """Testing when a member leaves that it does not delete the channel.
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

    payload = requests.post(f'{url}/channel/details', json={
        'token': user_1['token'],
        'channel_id': channel_leave['channel_id']
    }).json()

    for member in payload['all_members']:
        assert member['u_id'] != user_3['u_id']
    requests.delete(f'{url}/clear')


# def test_output_all_owners_leave(url):
#     """Testing Process: Tests suite that is designed to test the process of all
#     owners leaving in which the user with the lowest u_id in the channel becomes
#     the owner automatically.
#     Covers also if user access has been erased on channel end.
#     """
#     clear()
#     user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
#     user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
#     user_3 = auth.auth_register('jacesmith@gmail.com', 'password', 'Jace', 'Smith')
#     user_4 = auth.auth_register('janicesmith@gmail.com', 'password', 'Janice', 'Smith')

#     new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
#     channel.channel_addowner(user_1['token'], new_channel['channel_id'], user_2['u_id'])
#     channel.channel_invite(user_1['token'], new_channel['channel_id'], user_3['u_id'])
#     channel.channel_invite(user_1['token'], new_channel['channel_id'], user_4['u_id'])

#     # When the first owner leaves
#     channel.channel_leave(user_1['token'], new_channel['channel_id'])

#     # Confirm that there is now one owner in the channel
#     channel_data = channel.channel_details(user_2['token'], new_channel['channel_id'])
#     curr_owner = {'u_id': user_2['u_id'], 'name_first': 'Jane', 'name_last': 'Smith'}
#     assert curr_owner in channel_data['owner_members'] and len(channel_data['owner_members']) == 1

#     # Check members in the channel
#     curr_members = []
#     curr_members.append({'u_id': user_2['u_id'], 'name_first': 'Jane', 'name_last': 'Smith'})
#     curr_members.append({'u_id': user_3['u_id'], 'name_first': 'Jace', 'name_last': 'Smith'})
#     curr_members.append({'u_id': user_4['u_id'], 'name_first': 'Janice', 'name_last': 'Smith'})

#     n_members = 0
#     for member_details in channel_data['all_members']:
#         if member_details in curr_members:
#             n_members += 1
#             curr_members.remove(member_details)

#     assert curr_members == [] and n_members == len(channel_data['all_members'])

#     # When all owners leave, automatically assign a user with the lowest u_id
#     # as the owner
#     channel.channel_leave(user_2['token'], new_channel['channel_id'])
#     channel_data = channel.channel_details(user_3['token'], new_channel['channel_id'])

#     # Check members
#     curr_members = []
#     curr_members.append({'u_id': user_3['u_id'], 'name_first': 'Jace', 'name_last': 'Smith'})
#     curr_members.append({'u_id': user_4['u_id'], 'name_first': 'Janice', 'name_last': 'Smith'})
#     lowest_u_id_user = user_3
#     n_members = 0
#     for member_details in channel_data['all_members']:
#         if member_details in curr_members:
#             n_members += 1
#             curr_members.remove(member_details)
#             # Find the member with the lowest u_id
#             if lowest_u_id_user['u_id'] > member_details['u_id']:
#                 lowest_u_id_user = member_details

#     assert curr_members == [] and n_members == len(channel_data['all_members'])

#     # Check if a new owner has been assigned
#     assert len(channel_data['owner_members']) == 1
#     assert lowest_u_id_user['u_id'] == channel_data['owner_members'][0]['u_id']

#     # Check on the user end that the channel is not avialiable on their list.
#     channel_list = channels.channels_list(user_1['token'])
#     for curr_channel in channel_list['channels']:
#         assert curr_channel['channel_id'] is not new_channel['channel_id']

#     channel_list = channels.channels_list(user_2['token'])
#     for curr_channel in channel_list['channels']:
#         assert curr_channel['channel_id'] is not new_channel['channel_id']

#     clear()
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


