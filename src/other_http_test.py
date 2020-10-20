import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json

from error import AccessError, InputError

OWNER = 1
MEMBER = 2

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
        'is_public': False,
    }).json()

# Example testing from echo_http_test.py
# def test_echo(url):
#     '''
#     A simple test to check echo
#     '''
#     resp = requests.get(url + 'echo', params={'data': 'hello'})
#     assert json.loads(resp.text) == {'data': 'hello'}

#------------------------------------------------------------------------------#
#                                   users/all                                  #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#



#------------------------------------------------------------------------------#
#                          admin/userpermission/change                         #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_access_admin_valid_token(url, user_1):
    """Test if token is invalid does not refer to a valid user
    """
    requests.post(f'{url}/auth/logout', json={'token': user_1['token']})
    payload = requests.post(f'{url}/admin/userpermission/change', json={
        'token': user_1['token'],
        'u_id': user_1['u_id'],
        'permission_id': OWNER
    })
    assert payload.status_code == AccessError.code

    payload = requests.post(f'{url}/admin/userpermission/change', json={
        'token': user_1['token'],
        'u_id': user_1['u_id'],
        'permission_id': MEMBER
    })
    assert payload.status_code == AccessError.code

    payload = requests.post(f'{url}/admin/userpermission/change', json={
        'token': "INVALID",
        'u_id': user_1['u_id'],
        'permission_id': OWNER
    })
    assert payload.status_code == AccessError.code
    requests.delete(url + '/clear')


def test_input_admin_valid_u_id(url, user_1):
    """u_id does not refer to a valid user
    """
    payload = requests.post(f'{url}/admin/userpermission/change', json={
        'token': user_1['token'],
        'u_id': user_1['u_id'] - 1,
        'permission_id': OWNER
    })
    assert payload.status_code == InputError.code

    payload = requests.post(f'{url}/admin/userpermission/change', json={
        'token': user_1['token'],
        'u_id': user_1['u_id'] + 1,
        'permission_id': MEMBER
    })
    assert payload.status_code == InputError.code
    requests.delete(url + '/clear')

def test_input_admin_valid_permission_id(url, user_1):
    """permission_id does not refer to a value permission
    """
    payload = requests.post(f'{url}/admin/userpermission/change', json={
        'token': user_1['token'],
        'u_id': user_1['u_id'],
        'permission_id': -1
    })
    assert payload.status_code == InputError.code

    payload = requests.post(f'{url}/admin/userpermission/change', json={
        'token': user_1['token'],
        'u_id': user_1['u_id'],
        'permission_id': 0
    })
    assert payload.status_code == InputError.code

    payload = requests.post(f'{url}/admin/userpermission/change', json={
        'token': user_1['token'],
        'u_id': user_1['u_id'],
        'permission_id': 2
    })
    assert payload.status_code == InputError.code
    requests.delete(url + '/clear')


def test_input_admin_first_owner_changes_to_member(url, user_1):
    """Test whether the first flockr owner cannot change themselves to a member
    """
    payload = requests.post(f'{url}/admin/userpermission/change', json={
        'token': user_1['token'],
        'u_id': user_1['u_id'],
        'permission_id': MEMBER
    })
    assert payload.status_code == InputError.code
    requests.delete(url + '/clear')


def test_input_admin_owner_change_first_owner_to_member(url, user_1, user_2):
    """Test whether the another flockr owner cannot change the first flockr owner
    to a member
    """
    requests.post(f'{url}/admin/userpermission/change', json={
        'token': user_1['token'],
        'u_id': user_2['u_id'],
        'permission_id': OWNER
    })
    payload = requests.post(f'{url}/admin/userpermission/change', json={
        'token': user_2['token'],
        'u_id': user_1['u_id'],
        'permission_id': MEMBER
    })
    assert payload.status_code == InputError.code
    requests.delete(url + '/clear')


def test_access_admin_not_owner_own(url, user_1, user_2, user_3):
    """Testing whether a member cannot change another user's permissions.
    """
    payload = requests.post(f'{url}/admin/userpermission/change', json={
        'token': user_2['token'],
        'u_id': user_3['u_id'],
        'permission_id': OWNER
    })
    assert payload.status_code == AccessError.code

    payload = requests.post(f'{url}/admin/userpermission/change', json={
        'token': user_2['token'],
        'u_id': user_1['u_id'],
        'permission_id': MEMBER
    })
    assert payload.status_code == AccessError.code
    requests.delete(url + '/clear')

#?------------------------------ Output Testing ------------------------------?#


def test_output_admin_owner_change_member_to_owner(url, user_1, user_2, default_channel):
    """Test whether a member has become a flockr owner by joining a private channel
    """
    requests.post(f'{url}/admin/userpermission/change', json={
        'token': user_1['token'],
        'u_id': user_2['u_id'],
        'permission_id': OWNER
    })

    payload = requests.post(url + '/channel/join', json={
        'token': user_2['token'],
        'name': default_channel['channel_id']
    })
    payload.status_code == 200
    requests.delete(url + '/clear')


def test_output_admin_owner_change_owner_to_member(url, user_1, user_2, default_channel):
    """Test whether an owner successfully change another owner to a member
    """
    requests.post(f'{url}/admin/userpermission/change', json={
        'token': user_1['token'],
        'u_id': user_2['u_id'],
        'permission_id': OWNER
    })

    payload = requests.post(f'{url}/channel/join', json={
        'token': user_2['token'],
        'channel_id': default_channel['channel_id'],
    })
    assert payload.status_code == 200
    requests.post(url + '/channel/leave', json={
        'token': user_2['token'],
        'channel_id': default_channel['channel_id']
    })

    requests.post(f'{url}/admin/userpermission/change', json={
        'token': user_1['token'],
        'u_id': user_2['u_id'],
        'permission_id': MEMBER
    })
    payload = requests.post(f'{url}/channel/join', json={
        'token': user_2['token'],
        'channel_id': default_channel['channel_id'],
    })
    assert payload.status_code == AccessError.code
    requests.delete(url + '/clear')


def test_output_admin_owner_change_to_member(url, user_1, user_2, default_channel):
    """Test whether the an owner can set themselves as an member
    """
    requests.post(f'{url}/admin/userpermission/change', json={
        'token': user_1['token'],
        'u_id': user_2['u_id'],
        'permission_id': OWNER
    })

    payload = requests.post(f'{url}/channel/join', json={
        'token': user_2['token'],
        'channel_id': default_channel['channel_id'],
    })
    assert payload.status_code == 200
    requests.post(url + '/channel/leave', json={
        'token': user_2['token'],
        'channel_id': default_channel['channel_id']
    })

    requests.post(f'{url}/admin/userpermission/change', json={
        'token': user_2['token'],
        'u_id': user_2['u_id'],
        'permission_id': MEMBER
    })
    payload = requests.post(f'{url}/channel/join', json={
        'token': user_2['token'],
        'channel_id': default_channel['channel_id'],
    })
    assert payload.status_code == AccessError.code
    requests.delete(url + '/clear')


#------------------------------------------------------------------------------#
#                                    search                                    #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#


