import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests

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
def logout_user_1(url, user_1):
    return requests.post(f'{url}auth/logout', json={
        'token': user_1['token']
    }).json()

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
def public_channel_1(url, user_1):
    return requests.post(f'{url}/channels/create', json={
        'token': user_1['token'],
        'name': 'Group 1',
        'is_public': True,
    }).json()

@pytest.fixture
def public_channel_3(url, user_3):
    return requests.post(f'{url}/channels/create', json={
        'token': user_3['token'],
        'name': 'Group 1',
        'is_public': True,
    }).json()

@pytest.fixture
def private_channel_1(url, user_1):
    return requests.post(f'{url}/channels/create', json={
        'token': user_1['token'],
        'name': 'Group 1',
        'is_public': False,
    }).json()

@pytest.fixture
def private_channel_2(url, user_2):
    return requests.post(f'{url}/channels/create', json={
        'token': user_2['token'],
        'name': 'Group 2',
        'is_public': False,
    }).json()

@pytest.fixture
def private_channel_3(url, user_3):
    return requests.post(f'{url}/channels/create', json={
        'token': user_3['token'],
        'name': 'Group 3',
        'is_public': False,
    }).json()
#------------------------------------------------------------------------------#
#                               channels/create                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_user_authorised(url, user_1):
    """Test for whether the user is authorised to create a new channel.
    """
    data_input = {
        'token': user_1['token'],
        'name': 'Channel_1',
        'is_public': True,
    }
    new_channel = requests.post(f"{url}/channels/create", json=data_input)
    payload_create = new_channel.json()

    assert 'channel_id' in payload_create

def test_invalid_user(url, user_1):
    """Test for an invalid user creating a channel.
    """
    requests.post(f"{url}/auth/logout", json={'token': user_1['token']})

    data_input = {
        'token': user_1['token'],
        'name': 'Channel_1',
        'is_public': True,
    }
    new_channel = requests.post(f"{url}/channels/create", json=data_input)

    assert new_channel.status_code == AccessError.code

def test_0_char_name(url, user_1):
    """Test for 0 character channel name.
    """
    data_input = {
        'token': user_1['token'],
        'name': '',
        'is_public': True,
    }
    new_channel = requests.post(f"{url}/channels/create", json=data_input)

    assert new_channel.status_code == InputError.code

def test_1_char_name(url, user_1):
    """Test for 1 character channel name.
    """
    # Create new channel.
    data_input = {
        'token': user_1['token'],
        'name': 'C',
        'is_public': True,
    }
    payload_channel = requests.post(f"{url}/channels/create", json=data_input)
    new_channel = payload_channel.json()

    # Obtain channel details.
    detail_params = {
        'token': user_1['token'],
        'channel_id': new_channel['channel_id']
    }
    payload_details = requests.get(f"{url}/channel/details", params=detail_params)
    channel_details = payload_details.json()

    assert data_input['name'] in channel_details['name']


def test_20_char_name(url, user_1):
    """Test for 20 character channel name.
    """
    # Create new channel.
    data_input = {
        'token': user_1['token'],
        'name': 'Channel_Input1234567',
        'is_public': True,
    }
    payload_channel = requests.post(f"{url}/channels/create", json=data_input)
    new_channel = payload_channel.json()

    # Obtain channel details.
    detail_params = {
        'token': user_1['token'],
        'channel_id': new_channel['channel_id']
    }
    payload_details = requests.get(f"{url}/channel/details", params=detail_params)
    channel_details = payload_details.json()

    assert data_input['name'] in channel_details['name']

def test_21_char_name(url, user_1):
    """Test for 21 character channel name.
    """
    data_input = {
        'token': user_1['token'],
        'name': 'Channel_Input12345678',
        'is_public': True,
    }
    new_channel = requests.post(f"{url}/channels/create", json=data_input)

    assert new_channel.status_code == InputError.code

#?------------------------------ Output Testing ------------------------------?#

def test_unique_id(url, user_1):
    """Test for whether the generated channel_id is unique.
    """
    # Create new channels.
    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_1',
        'is_public': True,
    })
    payload_channel_2 = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_2',
        'is_public': True,
    })
    new_channel_1 = payload_channel_1.json()
    new_channel_2 = payload_channel_2.json()

    assert new_channel_1['channel_id'] != new_channel_2['channel_id']

def test_channel_member(url, user_1):
    """Test for whether user automatically becomes a member of their created channel.
    """
    # Create new channel.
    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_1',
        'is_public': True,
    })
    new_channel_1 = payload_channel_1.json()

    detail_params = {
        'token': user_1['token'],
        'channel_id': new_channel_1['channel_id']
    }
    payload_details = requests.get(f"{url}/channel/details", params=detail_params)
    channel_details = payload_details.json()

    test_case = False
    for member in channel_details['all_members']:
        if member['u_id'] == user_1['u_id']:
            test_case = True

    assert test_case

def test_channel_owner(url, user_1):
    """Test for whether user becomes owner of their created channel.
    """
    # Create new channel.
    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_1',
        'is_public': True,
    })
    new_channel_1 = payload_channel_1.json()

    detail_params = {
        'token': user_1['token'],
        'channel_id': new_channel_1['channel_id']
    }
    payload_details = requests.get(f"{url}/channel/details", params=detail_params)
    channel_details = payload_details.json()

    test_case = False
    for member in channel_details['owner_members']:
        if member['u_id'] == user_1['u_id']:
            test_case = True

    assert test_case

def test_private_channel(url, user_1, user_2):
    """Test whether a private channel works.
    """
    # Create new channel.
    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_1',
        'is_public': False,
    })
    new_channel_1 = payload_channel_1.json()

    payload_channel_join = requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': new_channel_1['channel_id']
    })
    assert payload_channel_join.status_code == AccessError.code

#------------------------------------------------------------------------------#
#                                channels/list                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_authorised_to_list(url, user_1):
    """Test list function from an unauthorised user.
    """
    # Create new channel.
    requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_1',
        'is_public': False,
    })

    # Log out the user.
    requests.post(f"{url}/auth/logout", json={
        'token': user_1['token'],
    })

    # Get channels list.
    payload_list = requests.get(f"{url}/channels/list", params={
        'token': user_1['token'],
    })

    assert payload_list.status_code == AccessError.code

#?------------------------------ Output Testing ------------------------------?#

def test_channels_list(url, user_1, user_2):
    """Basic test for listing channels that the user is a part of.
    """

    # Create new channel from user 1.
    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_1',
        'is_public': False,
    })
    payload_channel_2 = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_2',
        'is_public': False,
    })
    # Create new channel from user 2.
    payload_channel_3 = requests.post(f"{url}/channels/create", json={
        'token': user_2['token'],
        'name': 'Channel_3',
        'is_public': False,
    })
    new_channel_1 = payload_channel_1.json()
    new_channel_2 = payload_channel_2.json()
    new_channel_3 = payload_channel_3.json()

    payload_list = requests.get(f"{url}/channels/list", params={
        'token': user_1['token'],
    })
    channel_list = payload_list.json()

    assert {'channel_id': new_channel_1['channel_id'], 'name': 'Channel_1'} in channel_list['channels']
    assert {'channel_id': new_channel_2['channel_id'], 'name': 'Channel_2'} in channel_list['channels']
    assert {'channel_id': new_channel_3['channel_id'], 'name': 'Channel_3'} not in channel_list['channels']

def test_multiple_joined_channels(url, user_1, user_2, user_3):
    """Test for listing multiple joined channels.
    """
    # Create new channels.
    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_2['token'],
        'name': 'Channel_1',
        'is_public': False,
    })
    payload_channel_2 = requests.post(f"{url}/channels/create", json={
        'token': user_2['token'],
        'name': 'Channel_2',
        'is_public': False,
    })
    payload_channel_3 = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_3',
        'is_public': False,
    })
    payload_channel_4 = requests.post(f"{url}/channels/create", json={
        'token': user_3['token'],
        'name': 'Channel_4',
        'is_public': False,
    })
    payload_channel_5 = requests.post(f"{url}/channels/create", json={
        'token': user_2['token'],
        'name': 'Channel_5',
        'is_public': False,
    })
    new_channel_1 = payload_channel_1.json()
    new_channel_2 = payload_channel_2.json()
    new_channel_3 = payload_channel_3.json()
    new_channel_4 = payload_channel_4.json()
    new_channel_5 = payload_channel_5.json()

    payload_list = requests.get(f"{url}/channels/list", params={
        'token': user_2['token'],
    })
    channel_list = payload_list.json()

    assert {'channel_id': new_channel_1['channel_id'], 'name': 'Channel_1'} in channel_list['channels']
    assert {'channel_id': new_channel_2['channel_id'], 'name': 'Channel_2'} in channel_list['channels']
    assert {'channel_id': new_channel_5['channel_id'], 'name': 'Channel_5'} in channel_list['channels']
    assert {'channel_id': new_channel_3['channel_id'], 'name': 'Channel_3'} not in channel_list['channels']
    assert {'channel_id': new_channel_4['channel_id'], 'name': 'Channel_4'} not in channel_list['channels']

def test_channels_leave(url, user_1):
    """Test for leaving joined channels and then listing joined channels.
    """
    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_1',
        'is_public': False,
    })
    payload_channel_2 = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_2',
        'is_public': False,
    })
    payload_channel_3 = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_3',
        'is_public': False,
    })
    new_channel_1 = payload_channel_1.json()
    new_channel_2 = payload_channel_2.json()
    new_channel_3 = payload_channel_3.json()

    # Leave Channel_2.
    requests.post(f"{url}/channel/leave", json={
        'token': user_1['token'],
        'channel_id': new_channel_2['channel_id']
    })

    payload_list = requests.get(f"{url}/channels/list", params={
        'token': user_1['token'],
    })
    channel_list = payload_list.json()

    assert {'channel_id': new_channel_1['channel_id'], 'name': 'Channel_1'} in channel_list['channels']
    assert {'channel_id': new_channel_3['channel_id'], 'name': 'Channel_3'} in channel_list['channels']
    assert {'channel_id': new_channel_2['channel_id'], 'name': 'Channel_2'} not in channel_list['channels']
    
def test_empty_channels_list(url, user_1):
    """Test for empty channels list.
    """
    payload_list = requests.get(f"{url}/channels/list", params={
        'token': user_1['token'],
    })
    channel_list = payload_list.json()

    assert len(channel_list['channels']) == 0

#------------------------------------------------------------------------------#
#                               channels/listall                               #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_authorised_to_listall(url, user_1):
    """Test list all function from an unauthorised user.
    """

    # Create new channel.
    requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_1',
        'is_public': False,
    })

    # Log out the user.
    requests.post(f"{url}/auth/logout", json={
        'token': user_1['token'],
    })

    # Get channels list.
    payload_listall = requests.get(f"{url}/channels/listall", params={
        'token': user_1['token'],
    })

    assert payload_listall.status_code == AccessError.code

#?------------------------------ Output Testing ------------------------------?#

def test_channels_listall(url, user_1):
    """Test for basic functionality for list all feature.
    """
    # Create new channels.
    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_2['token'],
        'name': 'Channel_1',
        'is_public': True,
    })
    payload_channel_2 = requests.post(f"{url}/channels/create", json={
        'token': user_2['token'],
        'name': 'Channel_2',
        'is_public': True,
    })
    payload_channel_3 = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_3',
        'is_public': True,
    })
    payload_channel_4 = requests.post(f"{url}/channels/create", json={
        'token': user_3['token'],
        'name': 'Channel_4',
        'is_public': True,
    })
    payload_channel_5 = requests.post(f"{url}/channels/create", json={
        'token': user_2['token'],
        'name': 'Channel_5',
        'is_public': True,
    })
    new_channel_1 = payload_channel_1.json()
    new_channel_2 = payload_channel_2.json()
    new_channel_3 = payload_channel_3.json()
    new_channel_4 = payload_channel_4.json()
    new_channel_5 = payload_channel_5.json()

    payload_listall = requests.get(f"{url}/channels/listall", params={
        'token': user_3['token'],
    })
    channel_list = payload_listall.json()

    assert {'channel_id': new_channel_1['channel_id'], 'name': 'Channel_1'} in channel_list['channels']
    assert {'channel_id': new_channel_2['channel_id'], 'name': 'Channel_2'} in channel_list['channels']
    assert {'channel_id': new_channel_3['channel_id'], 'name': 'Channel_3'} in channel_list['channels']
    assert {'channel_id': new_channel_4['channel_id'], 'name': 'Channel_4'} in channel_list['channels']
    assert {'channel_id': new_channel_5['channel_id'], 'name': 'Channel_5'} in channel_list['channels']

def test_empty_channels_listall(url, user_1):
    """Test for no created channels.
    """
    # Create new channels.
    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_1',
        'is_public': False,
    })
    payload_channel_2 = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_2',
        'is_public': True,
    })
    payload_channel_3 = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_3',
        'is_public': False,
    })
    payload_channel_4 = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'Channel_4',
        'is_public': True,
    })
    new_channel_1 = payload_channel_1.json()
    new_channel_2 = payload_channel_2.json()
    new_channel_3 = payload_channel_3.json()
    new_channel_4 = payload_channel_4.json()

    payload_listall = requests.get(f"{url}/channels/listall", params={
        'token': user_1['token'],
    })
    channel_list = payload_listall.json()

    assert {'channel_id': new_channel_1['channel_id'], 'name': 'Channel_1'} in channel_list['channels']
    assert {'channel_id': new_channel_2['channel_id'], 'name': 'Channel_2'} in channel_list['channels']
    assert {'channel_id': new_channel_3['channel_id'], 'name': 'Channel_3'} in channel_list['channels']
    assert {'channel_id': new_channel_4['channel_id'], 'name': 'Channel_4'} in channel_list['channels']

def test_private_channels_listall(url, user_1):
    """Test for listing to include private channels.
    """
    payload_listall = requests.get(f"{url}/channels/listall", params={
        'token': user_1['token'],
    })
    channel_list = payload_listall.json()

    assert len(channel_list['channels']) == 0
