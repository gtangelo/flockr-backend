import json
import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests

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
#                               channels/create                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_user_authorised(url):
    """Test for whether the user is authorised to create a new channel.
    """
    requests.delete(f"{url}/clear")
    clear()
    data_register = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }
    result_reg = requests.post(f"{url}/auth/register", json=data_register)
    payload_reg = result_reg.json()

    data_input = {
        'token': payload_reg['token'],
        'name': 'Channel_1',
        'is_public': True,
    }
    new_channel = requests.post(f"{url}/channels/create", json=data_input)
    payload_create = new_channel.json()

    assert 'channel_id' in payload_create

def test_invalid_user(url):
    """Test for an invalid user creating a channel.
    """
    requests.delete(f"{url}/clear")
    clear()
    data_register = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }
    result_reg = requests.post(f"{url}/auth/register", json=data_register)
    payload_reg = result_reg.json()
    requests.post(f"{url}/auth/logout", json={'token': payload_reg['token']})

    data_input = {
        'token': payload_reg['token'],
        'name': 'Channel_1',
        'is_public': True,
    }
    new_channel = requests.post(f"{url}/channels/create", json=data_input)

    assert new_channel.status_code == AccessError.code

def test_0_char_name(url):
    """Test for 0 character channel name.
    """
    requests.delete(f"{url}/clear")
    clear()
    data_register = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }
    result_reg = requests.post(f"{url}/auth/register", json=data_register)
    payload_reg = result_reg.json()

    data_input = {
        'token': payload_reg['token'],
        'name': '',
        'is_public': True,
    }
    new_channel = requests.post(f"{url}/channels/create", json=data_input)

    assert new_channel.status_code == InputError.code

def test_1_char_name(url):
    """Test for 1 character channel name.
    """
    # Register a user.
    requests.delete(f"{url}/clear")
    clear()
    data_register = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }
    result_reg = requests.post(f"{url}/auth/register", json=data_register)
    payload_reg = result_reg.json()

    # Create new channel.
    data_input = {
        'token': payload_reg['token'],
        'name': 'C',
        'is_public': True,
    }
    payload_channel = requests.post(f"{url}/channels/create", json=data_input)
    new_channel = payload_channel.json()

    # Obtain channel details.
    detail_params = {
        'token': payload_reg['token'],
        'channel_id': new_channel['channel_id']
    }
    payload_details = requests.get(f"{url}/channel/details", params=detail_params)
    channel_details = payload_details.json()

    assert data_input['name'] in channel_details['name']


def test_20_char_name(url):
    """Test for 20 character channel name.
    """
    # Register a user.
    requests.delete(f"{url}/clear")
    clear()
    data_register = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }
    result_reg = requests.post(f"{url}/auth/register", json=data_register)
    payload_reg = result_reg.json()

    # Create new channel.
    data_input = {
        'token': payload_reg['token'],
        'name': 'Channel_Input1234567',
        'is_public': True,
    }
    payload_channel = requests.post(f"{url}/channels/create", json=data_input)
    new_channel = payload_channel.json()

    # Obtain channel details.
    detail_params = {
        'token': payload_reg['token'],
        'channel_id': new_channel['channel_id']
    }
    payload_details = requests.get(f"{url}/channel/details", params=detail_params)
    channel_details = payload_details.json()

    assert data_input['name'] in channel_details['name']

def test_21_char_name(url):
    """Test for 21 character channel name.
    """
    requests.delete(f"{url}/clear")
    clear()
    data_register = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }
    result_reg = requests.post(f"{url}/auth/register", json=data_register)
    payload_reg = result_reg.json()

    data_input = {
        'token': payload_reg['token'],
        'name': 'Channel_Input12345678',
        'is_public': True,
    }
    new_channel = requests.post(f"{url}/channels/create", json=data_input)

    assert new_channel.status_code == InputError.code

#?------------------------------ Output Testing ------------------------------?#

def test_unique_id(url):
    """Test for whether the generated channel_id is unique.
    """
    # Register a user.
    requests.delete(f"{url}/clear")
    clear()
    data_register = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }
    payload_reg = requests.post(f"{url}/auth/register", json=data_register)
    user_reg = payload_reg.json()

    # Create new channels.
    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_reg['token'],
        'name': 'Channel_1',
        'is_public': True,
    })
    payload_channel_2 = requests.post(f"{url}/channels/create", json={
        'token': user_reg['token'],
        'name': 'Channel_2',
        'is_public': True,
    })
    new_channel_1 = payload_channel_1.json()
    new_channel_2 = payload_channel_2.json()

    assert new_channel_1['channel_id'] != new_channel_2['channel_id']

def test_channel_member(url):
    """Test for whether user automatically becomes a member of their created channel.
    """
    # Register a user.
    requests.delete(f"{url}/clear")
    clear()
    data_register = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }
    payload_reg = requests.post(f"{url}/auth/register", json=data_register)
    user_reg = payload_reg.json()

    # Create new channel.
    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_reg['token'],
        'name': 'Channel_1',
        'is_public': True,
    })
    new_channel_1 = payload_channel_1.json()

    detail_params = {
        'token': user_reg['token'],
        'channel_id': new_channel_1['channel_id']
    }
    payload_details = requests.get(f"{url}/channel/details", params=detail_params)
    channel_details = payload_details.json()

    test_case = False
    for member in channel_details['all_members']:
        if member['u_id'] == user_reg['u_id']:
            test_case = True

    assert test_case

def test_channel_owner(url):
    """Test for whether user becomes owner of their created channel.
    """
    # Register a user.
    requests.delete(f"{url}/clear")
    clear()
    data_register = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }
    payload_reg = requests.post(f"{url}/auth/register", json=data_register)
    user_reg = payload_reg.json()

    # Create new channel.
    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_reg['token'],
        'name': 'Channel_1',
        'is_public': True,
    })
    new_channel_1 = payload_channel_1.json()

    detail_params = {
        'token': user_reg['token'],
        'channel_id': new_channel_1['channel_id']
    }
    payload_details = requests.get(f"{url}/channel/details", params=detail_params)
    channel_details = payload_details.json()

    test_case = False
    for member in channel_details['owner_members']:
        if member['u_id'] == user_reg['u_id']:
            test_case = True

    assert test_case

def test_private_channel(url):
    """Test whether a private channel works.
    """
    # Register a user.
    requests.delete(f"{url}/clear")
    clear()
    payload_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    })
    payload_reg_2 = requests.post(f"{url}/auth/register", json={
        'email' : 'test1Email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Richard',
        'name_last' : 'Quisumbing',
    })
    user_reg_1 = payload_reg_1.json()
    user_reg_2 = payload_reg_2.json()

    # Create new channel.
    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_1['token'],
        'name': 'Channel_1',
        'is_public': False,
    })
    new_channel_1 = payload_channel_1.json()

    payload_channel_join = requests.post(f"{url}/channel/join", json={
        'token': user_reg_2['token'],
        'channel_id': new_channel_1['channel_id']
    })
    assert payload_channel_join.status_code == AccessError.code

#------------------------------------------------------------------------------#
#                                channels/list                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_authorised_to_list(url):
    """Test list function from an unauthorised user.
    """
    # Register a user.
    requests.delete(f"{url}/clear")
    clear()
    payload_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    })
    user_reg_1 = payload_reg_1.json()

    # Create new channel.
    requests.post(f"{url}/channels/create", json={
        'token': user_reg_1['token'],
        'name': 'Channel_1',
        'is_public': False,
    })

    # Log out the user.
    requests.post(f"{url}/auth/logout", json={
        'token': user_reg_1['token'],
    })

    # Get channels list.
    payload_list = requests.get(f"{url}/channels/list", params={
        'token': user_reg_1['token'],
    })

    assert payload_list.status_code == AccessError.code

#?------------------------------ Output Testing ------------------------------?#

def test_channels_list(url):
    """Basic test for listing channels that the user is a part of.
    """
    # Register a user.
    requests.delete(f"{url}/clear")
    clear()
    payload_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    })
    payload_reg_2 = requests.post(f"{url}/auth/register", json={
        'email' : 'test1Email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Richard',
        'name_last' : 'Quisumbing',
    })
    user_reg_1 = payload_reg_1.json()
    user_reg_2 = payload_reg_2.json()

    # Create new channel from user 1.
    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_1['token'],
        'name': 'Channel_1',
        'is_public': False,
    })
    payload_channel_2 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_1['token'],
        'name': 'Channel_2',
        'is_public': False,
    })
    # Create new channel from user 2.
    payload_channel_3 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_2['token'],
        'name': 'Channel_3',
        'is_public': False,
    })
    new_channel_1 = payload_channel_1.json()
    new_channel_2 = payload_channel_2.json()
    new_channel_3 = payload_channel_3.json()

    payload_list = requests.get(f"{url}/channels/list", params={
        'token': user_reg_1['token'],
    })
    channel_list = payload_list.json()

    assert {'channel_id': new_channel_1['channel_id'], 'name': 'Channel_1'} in channel_list['channels']
    assert {'channel_id': new_channel_2['channel_id'], 'name': 'Channel_2'} in channel_list['channels']
    assert {'channel_id': new_channel_3['channel_id'], 'name': 'Channel_3'} not in channel_list['channels']

def test_multiple_joined_channels(url):
    """Test for listing multiple joined channels.
    """
    # Register users.
    requests.delete(f"{url}/clear")
    clear()
    payload_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    })
    payload_reg_2 = requests.post(f"{url}/auth/register", json={
        'email' : 'test1Email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Richard',
        'name_last' : 'Quisumbing',
    })
    payload_reg_3 = requests.post(f"{url}/auth/register", json={
        'email' : 'test2Email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Mike',
        'name_last' : 'Tyson',
    })
    user_reg_1 = payload_reg_1.json()
    user_reg_2 = payload_reg_2.json()
    user_reg_3 = payload_reg_3.json()

    # Create new channels.
    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_2['token'],
        'name': 'Channel_1',
        'is_public': False,
    })
    payload_channel_2 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_2['token'],
        'name': 'Channel_2',
        'is_public': False,
    })
    payload_channel_3 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_1['token'],
        'name': 'Channel_3',
        'is_public': False,
    })
    payload_channel_4 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_3['token'],
        'name': 'Channel_4',
        'is_public': False,
    })
    payload_channel_5 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_2['token'],
        'name': 'Channel_5',
        'is_public': False,
    })
    new_channel_1 = payload_channel_1.json()
    new_channel_2 = payload_channel_2.json()
    new_channel_3 = payload_channel_3.json()
    new_channel_4 = payload_channel_4.json()
    new_channel_5 = payload_channel_5.json()

    payload_list = requests.get(f"{url}/channels/list", params={
        'token': user_reg_2['token'],
    })
    channel_list = payload_list.json()

    assert {'channel_id': new_channel_1['channel_id'], 'name': 'Channel_1'} in channel_list['channels']
    assert {'channel_id': new_channel_2['channel_id'], 'name': 'Channel_2'} in channel_list['channels']
    assert {'channel_id': new_channel_5['channel_id'], 'name': 'Channel_5'} in channel_list['channels']
    assert {'channel_id': new_channel_3['channel_id'], 'name': 'Channel_3'} not in channel_list['channels']
    assert {'channel_id': new_channel_4['channel_id'], 'name': 'Channel_4'} not in channel_list['channels']

def test_channels_leave(url):
    """Test for leaving joined channels and then listing joined channels.
    """
    # Register users.
    requests.delete(f"{url}/clear")
    clear()
    payload_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    })
    user_reg_1 = payload_reg_1.json()

    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_1['token'],
        'name': 'Channel_1',
        'is_public': False,
    })
    payload_channel_2 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_1['token'],
        'name': 'Channel_2',
        'is_public': False,
    })
    payload_channel_3 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_1['token'],
        'name': 'Channel_3',
        'is_public': False,
    })
    new_channel_1 = payload_channel_1.json()
    new_channel_2 = payload_channel_2.json()
    new_channel_3 = payload_channel_3.json()

    # Leave Channel_2.
    requests.post(f"{url}/channel/leave", json={
        'token': user_reg_1['token'],
        'channel_id': new_channel_2['channel_id']
    })

    payload_list = requests.get(f"{url}/channels/list", params={
        'token': user_reg_1['token'],
    })
    channel_list = payload_list.json()

    assert {'channel_id': new_channel_1['channel_id'], 'name': 'Channel_1'} in channel_list['channels']
    assert {'channel_id': new_channel_3['channel_id'], 'name': 'Channel_3'} in channel_list['channels']
    assert {'channel_id': new_channel_2['channel_id'], 'name': 'Channel_2'} not in channel_list['channels']
    
def test_empty_channels_list(url):
    """Test for empty channels list.
    """
    # Register users.
    requests.delete(f"{url}/clear")
    clear()
    payload_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    })
    user_reg_1 = payload_reg_1.json()

    payload_list = requests.get(f"{url}/channels/list", params={
        'token': user_reg_1['token'],
    })
    channel_list = payload_list.json()

    assert len(channel_list['channels']) == 0

#------------------------------------------------------------------------------#
#                               channels/listall                               #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_authorised_to_listall(url):
    """Test list all function from an unauthorised user.
    """
    # Register a user.
    requests.delete(f"{url}/clear")
    clear()
    payload_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    })
    user_reg_1 = payload_reg_1.json()

    # Create new channel.
    requests.post(f"{url}/channels/create", json={
        'token': user_reg_1['token'],
        'name': 'Channel_1',
        'is_public': False,
    })

    # Log out the user.
    requests.post(f"{url}/auth/logout", json={
        'token': user_reg_1['token'],
    })

    # Get channels list.
    payload_listall = requests.get(f"{url}/channels/listall", params={
        'token': user_reg_1['token'],
    })

    assert payload_listall.status_code == AccessError.code

#?------------------------------ Output Testing ------------------------------?#

def test_channels_listall(url):
    """Test for basic functionality for list all feature.
    """
    # Register users.
    requests.delete(f"{url}/clear")
    clear()
    payload_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    })
    payload_reg_2 = requests.post(f"{url}/auth/register", json={
        'email' : 'test1Email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Richard',
        'name_last' : 'Quisumbing',
    })
    payload_reg_3 = requests.post(f"{url}/auth/register", json={
        'email' : 'test2Email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Mike',
        'name_last' : 'Tyson',
    })
    user_reg_1 = payload_reg_1.json()
    user_reg_2 = payload_reg_2.json()
    user_reg_3 = payload_reg_3.json()

    # Create new channels.
    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_2['token'],
        'name': 'Channel_1',
        'is_public': True,
    })
    payload_channel_2 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_2['token'],
        'name': 'Channel_2',
        'is_public': True,
    })
    payload_channel_3 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_1['token'],
        'name': 'Channel_3',
        'is_public': True,
    })
    payload_channel_4 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_3['token'],
        'name': 'Channel_4',
        'is_public': True,
    })
    payload_channel_5 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_2['token'],
        'name': 'Channel_5',
        'is_public': True,
    })
    new_channel_1 = payload_channel_1.json()
    new_channel_2 = payload_channel_2.json()
    new_channel_3 = payload_channel_3.json()
    new_channel_4 = payload_channel_4.json()
    new_channel_5 = payload_channel_5.json()

    payload_listall = requests.get(f"{url}/channels/listall", params={
        'token': user_reg_3['token'],
    })
    channel_list = payload_listall.json()

    assert {'channel_id': new_channel_1['channel_id'], 'name': 'Channel_1'} in channel_list['channels']
    assert {'channel_id': new_channel_2['channel_id'], 'name': 'Channel_2'} in channel_list['channels']
    assert {'channel_id': new_channel_3['channel_id'], 'name': 'Channel_3'} in channel_list['channels']
    assert {'channel_id': new_channel_4['channel_id'], 'name': 'Channel_4'} in channel_list['channels']
    assert {'channel_id': new_channel_5['channel_id'], 'name': 'Channel_5'} in channel_list['channels']

def test_empty_channels_listall(url):
    """Test for no created channels.
    """
    # Register users.
    requests.delete(f"{url}/clear")
    clear()
    payload_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    })
    user_reg_1 = payload_reg_1.json()

    # Create new channels.
    payload_channel_1 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_1['token'],
        'name': 'Channel_1',
        'is_public': False,
    })
    payload_channel_2 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_1['token'],
        'name': 'Channel_2',
        'is_public': True,
    })
    payload_channel_3 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_1['token'],
        'name': 'Channel_3',
        'is_public': False,
    })
    payload_channel_4 = requests.post(f"{url}/channels/create", json={
        'token': user_reg_1['token'],
        'name': 'Channel_4',
        'is_public': True,
    })
    new_channel_1 = payload_channel_1.json()
    new_channel_2 = payload_channel_2.json()
    new_channel_3 = payload_channel_3.json()
    new_channel_4 = payload_channel_4.json()

    payload_listall = requests.get(f"{url}/channels/listall", params={
        'token': user_reg_1['token'],
    })
    channel_list = payload_listall.json()

    assert {'channel_id': new_channel_1['channel_id'], 'name': 'Channel_1'} in channel_list['channels']
    assert {'channel_id': new_channel_2['channel_id'], 'name': 'Channel_2'} in channel_list['channels']
    assert {'channel_id': new_channel_3['channel_id'], 'name': 'Channel_3'} in channel_list['channels']
    assert {'channel_id': new_channel_4['channel_id'], 'name': 'Channel_4'} in channel_list['channels']

def test_private_channels_listall(url):
    """Test for listing to include private channels.
    """
    # Register users.
    requests.delete(f"{url}/clear")
    clear()
    payload_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    })
    user_reg_1 = payload_reg_1.json()

    payload_listall = requests.get(f"{url}/channels/listall", params={
        'token': user_reg_1['token'],
    })
    channel_list = payload_listall.json()

    assert len(channel_list['channels']) == 0
