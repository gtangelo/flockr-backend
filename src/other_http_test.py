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

def test_users_all_valid_token(url, user_1):
    """Test if token does not refer to a valid user
    """
    log_out = requests.post(url + 'auth/logout', json={'token': user_1['token']}).json()
    assert log_out['is_success']

    all_users = requests.get(url + 'users/all', params={'token': user_1['token']})
    assert all_users.status_code == AccessError.code

    requests.delete(url + '/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_users_all(url, user_1, user_2, user_3, user_4):
    """Test if a list all users details is returned
    """
    all_users = requests.get(url + 'users/all', params={'token': user_1['token']}).json()
    user_count = 0
    test_1 = False
    test_2 = False
    test_3 = False
    for user in all_users['users']:
        if user['u_id'] is user_3['u_id']:
            test_1 = True
        if user['u_id'] is user_2['u_id']:
            test_2 = True
        if user['u_id'] is user_4['u_id']:
            test_3 = True
        user_count += 1
    assert user_count == 4
    assert True in (test_1, test_2, test_3)
    requests.delete(url + '/clear')

def test_users_all_logout(url, user_1, user_2, user_3, user_4):
    """Test if some users log out, their details are still returned
    """
    log_out = requests.post(url + 'auth/logout', json={'token': user_3['token']}).json()
    assert log_out['is_success']
    log_out = requests.post(url + 'auth/logout', json={'token': user_4['token']}).json()
    assert log_out['is_success']
    all_users = requests.get(url + 'users/all', params={'token': user_1['token']}).json()
    user_count = 0
    test_1 = False
    test_2 = False
    for user in all_users['users']:
        if user['u_id'] is user_3['u_id']:
            test_1 = True
        if user['u_id'] is user_2['u_id']:
            test_2 = True
        user_count += 1
    assert user_count == 4
    assert True in (test_1, test_2)
    requests.delete(url + '/clear')

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

def test_search_valid_token(url, user_1):
    """Test if token does not refer to a valid user
    """
    log_out = requests.post(url + 'auth/logout', json={'token': user_1['token']}).json()
    assert log_out['is_success']

    search = requests.get(f'{url}/search', params={
        'token': user_1['token'],
        'query_str': 'Test',
    })
    assert search.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_search_invalid_query_str(url, user_1):
    """Test if query string is less than a character
    """
    search = requests.get(f'{url}/search', params={
        'token': user_1['token'],
        'query_str': '',
    })
    assert search.status_code == InputError.code

    requests.delete(url + '/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_search_standard(url, user_1, user_2, user_3, user_4):
    """Test searching messages in multiple channels
    """
    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': True,
    }
    channel_1 = requests.post(f'{url}/channels/create', json=channel_profile).json()

    channel_profile = {
        'token'    : user_2['token'],
        'name'     : 'Group 2',
        'is_public': True,
    }
    channel_2 = requests.post(f'{url}/channels/create', json=channel_profile).json()

    channel_profile = {
        'token'    : user_3['token'],
        'name'     : 'Group 3',
        'is_public': True,
    }
    channel_3 = requests.post(f'{url}/channels/create', json=channel_profile).json()

    channel_profile = {
        'token'    : user_4['token'],
        'name'     : 'Group 4',
        'is_public': True,
    }
    channel_4 = requests.post(f'{url}/channels/create', json=channel_profile).json()

    msg_str_1 = "Welcome to group 1!"
    msg_str_2 = "Welcome to group 2!"
    msg_str_3 = "Welcome to group 3!"
    msg_str_4 = "Welcome to group 4!"
    msg_str_5 = "Hiya guys!"
    msg_str_6 = "sup"
    msg_str_7 = "Let's get down to business!"
    query_str = "Welcome"

    requests.post(f'{url}/channel/join', json={
        'token': user_1['token'],
        'channel_id': channel_2['channel_id']
    })

    requests.post(f'{url}/channel/join', json={
        'token': user_1['token'],
        'channel_id': channel_3['channel_id']
    })

    requests.post(f'{url}/channel/join', json={
        'token': user_1['token'],
        'channel_id': channel_4['channel_id']
    })

    requests.post(url + 'message/send', json={
        'token'     : user_1['token'],
        'channel_id': channel_1['channel_id'],
        'message'   : msg_str_1,
    })

    requests.post(url + 'message/send', json={
        'token'     : user_2['token'],
        'channel_id': channel_2['channel_id'],
        'message'   : msg_str_2,
    })

    requests.post(url + 'message/send', json={
        'token'     : user_3['token'],
        'channel_id': channel_3['channel_id'],
        'message'   : msg_str_3,
    })

    requests.post(url + 'message/send', json={
        'token'     : user_4['token'],
        'channel_id': channel_4['channel_id'],
        'message'   : msg_str_4,
    })

    requests.post(url + 'message/send', json={
        'token'     : user_1['token'],
        'channel_id': channel_1['channel_id'],
        'message'   : msg_str_5,
    })

    requests.post(url + 'message/send', json={
        'token'     : user_1['token'],
        'channel_id': channel_2['channel_id'],
        'message'   : msg_str_6,
    })

    requests.post(url + 'message/send', json={
        'token'     : user_1['token'],
        'channel_id': channel_2['channel_id'],
        'message'   : msg_str_7,
    })

    msg_list = requests.get(f'{url}/search', params={
        'token': user_1['token'],
        'query_str': query_str,
    }).json()

    msg_count = 0
    msg_cmp_2 = []
    for msg in msg_list['messages']:
        msg_cmp_2.append(msg['message'])
        msg_count += 1
    assert msg_count == 4
    msg_cmp_1 = [msg_str_1, msg_str_2, msg_str_3, msg_str_4]
    msg_cmp_1.sort()
    msg_cmp_2.sort()
    assert msg_cmp_1 == msg_cmp_2
    requests.delete(url + '/clear')

def test_search_no_match(url, user_1, default_channel):
    """Test searching messages with 0 results
    """
    msg_str_1 = "Welcome to group 1!"
    query_str = "ZzZ"

    requests.post(url + 'message/send', json={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'message'   : msg_str_1,
    })

    msg_list = requests.get(f'{url}/search', params={
        'token': user_1['token'],
        'query_str': query_str,
    }).json()

    assert len(msg_list['messages']) == 0
    requests.delete(url + '/clear')

def test_search_not_in_channel(url, user_1, user_2, default_channel):
    """Test searching messages when the user has not been part of the channel before
    """
    query_str = "ZzZ"
    requests.post(url + 'message/send', json={
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
        'message'   : query_str,
    })

    msg_list = requests.get(f'{url}/search', params={
        'token': user_1['token'],
        'query_str': query_str,
    }).json()

    assert len(msg_list['messages']) == 0
    requests.delete(url + '/clear')

def test_search_leave_channel(url, user_1, default_channel):
    """Test searching messages when user has left channel the channel
    """
    query_str = "ZzZ"
    requests.post(url + 'message/send', json={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'message'   : query_str,
    })

    requests.post(f'{url}/channel/leave', json={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id']
    })

    msg_list = requests.get(f'{url}/search', params={
        'token': user_1['token'],
        'query_str': query_str,
    }).json()

    assert len(msg_list['messages']) == 0
    requests.delete(url + '/clear')
