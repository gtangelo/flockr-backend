import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests

from datetime import datetime, timezone
from error import InputError, AccessError

DELAY = 150

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
def user_1_logout(url, user_1):
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
def default_channel(url, user_1):
    return requests.post(f'{url}/channels/create', json={
        'token': user_1['token'],
        'name': 'Group 1',
        'is_public': True,
    }).json()

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

#------------------------------------------------------------------------------#
#                               channel/invite                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_channel_invite_login_user_HTTP(url, user_1, user_2, user_3, user_4, default_channel):
    """Testing invalid token for users which have logged out
    """
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_1['token']}).json()
    assert log_out['is_success'] == True
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_2['token']}).json()
    assert log_out['is_success'] == True
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_3['token']}).json()
    assert log_out['is_success'] == True
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_4['token']}).json()
    assert log_out['is_success'] == True

    err = requests.post(f'{url}/channel/invite', json={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_1['u_id'],
    })
    assert err.status_code == AccessError.code

    err = requests.post(f'{url}/channel/invite', json={
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_3['u_id'],
    })
    assert err.status_code == AccessError.code

    err = requests.post(f'{url}/channel/invite', json={
        'token'     : user_3['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_3['u_id'],
    })
    assert err.status_code == AccessError.code

    err = requests.post(f'{url}/channel/invite', json={
        'token'     : user_4['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_3['u_id'],
    })
    assert err.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_channel_invite_invalid_user_HTTP(url, user_1, default_channel):
    """Testing when invalid user is invited to channel
    """
    err = requests.post(f'{url}/channel/invite', json={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_1['u_id'] + 1,
    })
    assert err.status_code == InputError.code

    err = requests.post(f'{url}/channel/invite', json={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_1['u_id'] - 1,
    })
    assert err.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_channel_invite_invalid_channel_HTTP(url, user_1, user_2):
    """Testing when valid user is invited to invalid channel
    """
    err = requests.post(f'{url}/channel/invite', json={
        'token'     : user_1['token'],
        'channel_id': 0,
        'u_id'      : user_2['u_id'],
    })
    assert err.status_code == InputError.code

    err = requests.post(f'{url}/channel/invite', json={
        'token'     : user_1['token'],
        'channel_id': 1,
        'u_id'      : user_2['u_id'],
    })
    assert err.status_code == InputError.code

    err = requests.post(f'{url}/channel/invite', json={
        'token'     : user_1['token'],
        'channel_id': -1,
        'u_id'      : user_2['u_id'],
    })
    assert err.status_code == InputError.code

    requests.delete(f'{url}/clear')

def test_channel_invite_not_authorized_HTTP(url, user_1, user_2, user_3):
    """Testing when user is not authorized to invite other users to channel
    (Assumption) This includes an invalid user inviting users to channel
    """
    default_channel = requests.post(f'{url}/channels/create', json={
        'token'    : user_3['token'],
        'name'     : 'Group 1',
        'is_public': True,
    }).json()
    log_out = requests.post(f'{url}/auth/logout', json={'token': user_1['token']}).json()
    assert log_out['is_success']

    err = requests.post(f'{url}/channel/invite', json={
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_1['u_id'],
    })
    assert err.status_code == AccessError.code

    err = requests.post(f'{url}/channel/invite', json={
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_3['u_id'],
    })
    assert err.status_code == AccessError.code

    err = requests.post(f'{url}/channel/invite', json={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_3['u_id'],
    })
    assert err.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_channel_invite_invalid_self_invite_HTTP(url, user_1, default_channel):
    """Testing when user is not allowed to invite him/herself to channel
    (Assumption testing) this error will be treated as InputError
    """
    err = requests.post(f'{url}/channel/invite', json={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_1['u_id'],
    })
    assert err.status_code == InputError.code
    requests.delete(f'{url}/clear')

def test_channel_multiple_invite_HTTP(url, user_1, user_2, default_channel):
    """Testing when user invites a user multiple times
    (Assumption testing) this error will be treated as AccessError
    """
    channel_return = requests.post(f'{url}/channel/invite', json={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_2['u_id'],
    }).json()
    assert channel_return == {}

    err = requests.post(f'{url}/channel/invite', json={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_2['u_id'],
    })
    assert err.status_code == InputError.code

    err = requests.post(f'{url}/channel/invite', json={
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_2['u_id'],
    })
    assert err.status_code == InputError.code

    err = requests.post(f'{url}/channel/invite', json={
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_1['u_id'],
    })
    assert err.status_code == InputError.code
    requests.delete(f'{url}/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_channel_invite_successful_HTTP(url, user_1, user_2, user_3, user_4, default_channel):
    """Testing if user has successfully been invited to the channel
    """
    channel_return = requests.post(f'{url}/channel/invite', json={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_2['u_id'],
    }).json()
    assert channel_return == {}

    channel_information = requests.get(f'{url}/channel/details', params={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
    }).json()
    assert channel_information == {
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
                'name_first': 'Jane',
                'name_last': 'Smith',
            },
        ],
    }

    channel_return = requests.post(f'{url}/channel/invite', json={
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_3['u_id'],
    }).json()
    assert channel_return == {}

    channel_information = requests.get(f'{url}/channel/details', params={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
    }).json()
    assert channel_information == {
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
                'name_first': 'Jane',
                'name_last': 'Smith',
            },
            {
                'u_id': user_3['u_id'],
                'name_first': 'Jace',
                'name_last': 'Smith',
            },
        ],
    }

    channel_return = requests.post(f'{url}/channel/invite', json={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_4['u_id'],
    }).json()
    assert channel_return == {}

    channel_information = requests.get(f'{url}/channel/details', params={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
    }).json()    
    assert channel_information == {
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
                'name_first': 'Jane',
                'name_last': 'Smith',
            },
            {
                'u_id': user_3['u_id'],
                'name_first': 'Jace',
                'name_last': 'Smith',
            },
            {
                'u_id': user_4['u_id'],
                'name_first': 'Janice',
                'name_last': 'Smith',
            },
        ],
    }
    requests.delete(f'{url}/clear')

def test_channel_invite_flockr_user_HTTP(url, user_1, user_2, user_3):
    """(Assumption testing) first person to register is flockr owner
    Testing if flockr owner has been successfully invited to channel and given ownership
    """
    default_channel = requests.post(f'{url}/channels/create', json={
        'token'    : user_2['token'],
        'name'     : 'Group 1',
        'is_public': False,
    }).json()

    channel_return = requests.post(f'{url}/channel/invite', json={
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_3['u_id'],
    }).json()
    assert channel_return == {}

    channel_information = requests.get(f'{url}/channel/details', params={
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
    }).json()
    assert channel_information == {
        'name': 'Group 1',
        'owner_members': [
            {
                'u_id': user_2['u_id'],
                'name_first': 'Jane',
                'name_last': 'Smith',
            },
        ],
        'all_members': [
            {
                'u_id': user_2['u_id'],
                'name_first': 'Jane',
                'name_last': 'Smith',
            },
            {
                'u_id': user_3['u_id'],
                'name_first': 'Jace',
                'name_last': 'Smith',
            },
        ],
    }

    channel_return = requests.post(f'{url}/channel/invite', json={
        'token'     : user_3['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_1['u_id'],
    }).json()
    assert channel_return == {}

    channel_information = requests.get(f'{url}/channel/details', params={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
    }).json()
    assert channel_information == {
        'name': 'Group 1',
        'owner_members': [
            {
                'u_id': user_2['u_id'],
                'name_first': 'Jane',
                'name_last': 'Smith',
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
                'name_first': 'Jane',
                'name_last': 'Smith',
            },
            {
                'u_id': user_3['u_id'],
                'name_first': 'Jace',
                'name_last': 'Smith',
            },
            {
                'u_id': user_1['u_id'],
                'name_first': 'John',
                'name_last': 'Smith',
            },
        ],
    }
    requests.delete(f'{url}/clear')

#------------------------------------------------------------------------------#
#                               channel/details                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_channel_details_invalid_channel_HTTP(url, user_1):
    """Testing if channel is invalid or does not exist
    """
    err = requests.get(f'{url}/channel/details', params={
        'token'     : user_1['token'],
        'channel_id': -1,
    })
    assert err.status_code == InputError.code

    err = requests.get(f'{url}/channel/details', params={
        'token'     : user_1['token'],
        'channel_id': 0,
    })
    assert err.status_code == InputError.code

    err = requests.get(f'{url}/channel/details', params={
        'token'     : user_1['token'],
        'channel_id': 1,
    })
    assert err.status_code == InputError.code

    requests.delete(f'{url}/clear')

def test_channel_details_invalid_user_HTTP(url, user_1, user_2, default_channel):
    """Testing if unauthorized/invalid user is unable to access channel details
    """    
    error = requests.get(f'{url}/channel/details', params={
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
    })
    assert error.status_code == AccessError.code
    requests.delete(f'{url}/clear')

def test_channel_details_invalid_token_HTTP(url, user_1, default_channel):
    """Testing if given invalid token returns an AccessError
    """
    requests.post(f'{url}/auth/logout', json={'token': user_1['token']})
    error = requests.get(f'{url}/channel/details', params={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
    })
    assert error.status_code == AccessError.code

    error = requests.get(f'{url}/channel/details', params={
        'token'     : '@^!&',
        'channel_id': default_channel['channel_id'],
    })
    assert error.status_code == AccessError.code

    requests.delete(f'{url}/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_channel_details_authorized_user_HTTP(url, user_1, user_2, user_3, user_4, default_channel):
    """Testing the required correct details of a channel
    """
    channel_return = requests.post(f'{url}/channel/invite', json={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_2['u_id'],
    }).json()
    assert channel_return == {}

    channel_information = requests.get(f'{url}/channel/details', params={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
    }).json()
    assert channel_information == {
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
                'name_first': 'Jane',
                'name_last': 'Smith',
            },
        ],
    }

    channel_return = requests.post(f'{url}/channel/invite', json={
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_3['u_id'],
    }).json()
    assert channel_return == {}
    
    channel_information = requests.get(f'{url}/channel/details', params={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
    }).json()
    assert channel_information == {
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
                'name_first': 'Jane',
                'name_last': 'Smith',
            },
            {
                'u_id': user_3['u_id'],
                'name_first': 'Jace',
                'name_last': 'Smith',
            },
        ],
    }

    channel_return = requests.post(f'{url}/channel/invite', json={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_4['u_id'],
    }).json()
    assert channel_return == {}

    channel_information = requests.get(f'{url}/channel/details', params={
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
    }).json()    
    assert channel_information == {
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
                'name_first': 'Jane',
                'name_last': 'Smith',
            },
            {
                'u_id': user_3['u_id'],
                'name_first': 'Jace',
                'name_last': 'Smith',
            },
            {
                'u_id': user_4['u_id'],
                'name_first': 'Janice',
                'name_last': 'Smith',
            },
        ],
    }
    requests.delete(f'{url}/clear')

def test_output_details_twice_HTTP(url, user_1, user_2, default_channel):
    """Test if details will be shown when a second channel is created.
    """
    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 2',
        'is_public': True,
    }
    default_channel_2 = requests.post(f'{url}/channels/create', json=channel_profile).json()

    invite_details = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_2['u_id'],
    }
    channel_return = requests.post(f'{url}/channel/invite', json=invite_details).json()
    assert channel_return == {}

    channel_profile = {
        'token'     : user_1['token'],
        'channel_id': default_channel_2['channel_id'],
    }
    channel_information = requests.get(f'{url}/channel/details', params=channel_profile).json()
    assert channel_information == {
        'name': 'Group 2',
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
        ],
    }

    channel_profile = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
    }
    channel_information = requests.get(f'{url}/channel/details', params=channel_profile).json()
    assert channel_information == {
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
                'name_first': 'Jane',
                'name_last': 'Smith',
            },
        ],
    }
    requests.delete(f'{url}/clear')

#------------------------------------------------------------------------------#
#                              channel/messages                                #
#------------------------------------------------------------------------------#
# Helper function to send messages
def create_messages(url, user, channel_id, i, j):
    """Sends n messages to the channel with channel_id in channel_data

    Args:
        user (dict): { u_id, token }
        channel_data (dict): { channel_id }
        i (int): start of a message string
        j (int): end of a message string

    Returns:
        (dict): { messages }
    """
    result = []
    for index in range(i, j):
        time = int(datetime.now().replace(tzinfo=timezone.utc).timestamp())
        message_info = requests.post(url + '/message/send', json={
            'token': user['token'],
            'channel_id': channel_id,
            'message': f'{index}'
        }).json()
        result.append({
            'message_id': message_info['message_id'],
            'u_id': user['u_id'],
            'message': f"{index}",
            'time_created': time,
        })
    return result

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_input_messages_channel_id(url, user_1):
    """Testing when an invalid channel_id is used as a parameter
    """
    start = 0
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': -1,
        'start': start,
    })
    assert resp.status_code == InputError.code

    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': 1,
        'start': start,
    })
    assert resp.status_code == InputError.code

    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': 0,
        'start': start,
    })
    assert resp.status_code == InputError.code
    requests.delete(url + '/clear')

def test_input_messages_start(url, user_1, default_channel):
    """Testing when start is an invalid start value. Start is greater than the
    total number of messages in the channel.
    """
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 1,
    })
    assert resp.status_code == InputError.code

    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 10,
    })
    assert resp.status_code == InputError.code

    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': -1,
    })
    assert resp.status_code == InputError.code

    requests.delete(url + '/clear')


def test_input_messages_start_equal_10(url, user_1, default_channel):
    """Testing when start index is equal to the total number of messages, it will
    instead raise an InputError (assumption).
    """
    create_messages(url, user_1, default_channel['channel_id'], 0, 10)
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 10,
    })
    assert resp.status_code == InputError.code

    requests.delete(url + '/clear')

def test_access_messages_user_is_member(url, user_1, user_2):
    """Testing if another user can access the channel
    """
    new_channel_1 = requests.post(url + '/channels/create', json={
        'token': user_1['token'],
        'name': 'Group 1',
        'is_public': True
    }).json()
    new_channel_2 = requests.post(url + '/channels/create', json={
        'token': user_2['token'],
        'name': 'Group 1',
        'is_public': True
    }).json()
    
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': new_channel_2['channel_id'],
        'start': 0,
    })
    assert resp.status_code == AccessError.code

    resp = requests.get(url + '/channel/messages', params={
        'token': user_2['token'],
        'channel_id': new_channel_1['channel_id'],
        'start': 0,
    })
    assert resp.status_code == AccessError.code

    requests.delete(url + '/clear')


def test_access_messages_valid_token(url, user_1, default_channel, user_1_logout):
    """Testing if token is valid
    """
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 0,
    })
    assert resp.status_code == AccessError.code

    requests.delete(url + '/clear')


#?------------------------------ Output Testing ------------------------------?#

#! Testing when a channel has no messages
def test_output_no_messages(url, user_1, default_channel):
    """Testing when a channel has no messages
    """
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 0,
    }).json()
    assert resp['messages'] == []
    assert resp['start'] == -1
    assert resp['end'] == -1
    requests.delete(url + '/clear')

#! Testing when a channel less than 50 messages
def test_output_messages_1(url, user_1, default_channel):
    """Testing when a channel has a single message
    """
    message_list = create_messages(url, user_1, default_channel['channel_id'], 0, 1)
    assert len(message_list) == 1
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 0,
    }).json()
    assert len(message_list) == len(resp['messages'])
    for index, item in enumerate(resp['messages']):
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(resp['messages']) == 1
    assert resp['start'] == 0
    assert resp['end'] == -1
    requests.delete(url + '/clear')

def test_output_messages_10_start_0(url, user_1, default_channel):
    """Testing when a channel has 10 messages at start 0.
    """
    message_list = create_messages(url, user_1, default_channel['channel_id'], 0, 10)
    assert len(message_list) == 10
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 0,
    }).json()
    assert len(message_list) == len(resp['messages'])
    for index, item in enumerate(resp['messages']):
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(resp['messages']) == 10
    assert resp['start'] == 0
    assert resp['end'] == -1
    requests.delete(url + '/clear')

def test_output_messages_10_start_5(url, user_1, default_channel):
    """Testing when a channel has 10 messages at start 5.
    """
    message_list = create_messages(url, user_1, default_channel['channel_id'], 0, 10)
    assert len(message_list) == 10
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 5,
    }).json()
    assert len(message_list[5:]) == len(resp['messages'])
    for index, item in enumerate(resp['messages']):
        index += 5
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(resp['messages']) == 5
    assert resp['start'] == 5
    assert resp['end'] == -1
    requests.delete(url + '/clear')

def test_output_messages_49_start_0(url, user_1, default_channel):
    """Testing when a channel has 49 total messages at start 0.
    """
    message_list = create_messages(url, user_1, default_channel['channel_id'], 0, 49)
    assert len(message_list) == 49
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 0,
    }).json()
    assert len(message_list) == len(resp['messages'])
    for index, item in enumerate(resp['messages']):
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(resp['messages']) == 49
    assert resp['start'] == 0
    assert resp['end'] == -1
    requests.delete(url + '/clear')

def test_output_messages_49_start_25(url, user_1, default_channel):
    """Testing when a channel has 49 total messages at start 25.
    """
    message_list = create_messages(url, user_1, default_channel['channel_id'], 0, 49)
    assert len(message_list) == 49
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 25,
    }).json()
    assert len(message_list[25:]) == len(resp['messages'])
    for index, item in enumerate(resp['messages']):
        index += 25
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(resp['messages']) == 24
    assert resp['start'] == 25
    assert resp['end'] == -1
    requests.delete(url + '/clear')

#! Testing when a channel exactly 50 messages
def test_output_messages_50_start_0(url, user_1, default_channel):
    """Testing when a channel has 50 total messages at start 0.
    """
    message_list = create_messages(url, user_1, default_channel['channel_id'], 0, 50)
    assert len(message_list) == 50
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 0,
    }).json()
    assert len(message_list) == len(resp['messages'])
    for index, item in enumerate(resp['messages']):
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    
    assert len(resp['messages']) == 50
    assert resp['start'] == 0
    assert resp['end'] == -1
    requests.delete(url + '/clear')

def test_output_messages_50_start_25(url, user_1, default_channel):
    """Testing when a channel has 50 total messages at start 25.
    """
    message_list = create_messages(url, user_1, default_channel['channel_id'], 0, 50)
    assert len(message_list) == 50
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 25,
    }).json()

    assert len(message_list[25:]) == len(resp['messages'])
    for index, item in enumerate(resp['messages']):
        index += 25
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)

    assert len(resp['messages']) == 25
    assert resp['start'] == 25
    assert resp['end'] == -1
    requests.delete(url + '/clear')

def test_output_messages_50_start_49(url, user_1, default_channel):
    """Testing when a channel has 50 total messages at start 49.
    """
    message_list = create_messages(url, user_1, default_channel['channel_id'], 0, 50)
    assert len(message_list) == 50
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 49,
    }).json()
    assert len(message_list[49:]) == len(resp['messages'])
    for index, item in enumerate(resp['messages']):
        index += 49
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(resp['messages']) == 1
    assert resp['start'] == 49
    assert resp['end'] == -1
    requests.delete(url + '/clear')

#! Testing when a channel has more than 50 messages
def test_output_messages_51_start_0(url, user_1, default_channel):
    """Testing when a channel has 51 total messages at start 0.
    """
    message_list = create_messages(url, user_1, default_channel['channel_id'], 0, 51)
    assert len(message_list) == 51
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 0,
    }).json()
    assert len(message_list[:50]) == len(resp['messages'])
    for index, item in enumerate(resp['messages']):
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(resp['messages']) == 50
    assert resp['start'] == 0
    assert resp['end'] == 50
    requests.delete(url + '/clear')

def test_output_messages_51_start_25(url, user_1, default_channel):
    """Testing when a channel has 51 total messages at start 25.
    """
    message_list = create_messages(url, user_1, default_channel['channel_id'], 0, 51)
    assert len(message_list) == 51
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 25,
    }).json()
    assert len(message_list[25:]) == len(resp['messages'])
    for index, item in enumerate(resp['messages']):
        index += 25
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(resp['messages']) == 26
    assert resp['start'] == 25
    assert resp['end'] == -1
    requests.delete(url + '/clear')

def test_output_messages_51_start_50(url, user_1, default_channel):
    """Testing when a channel has 51 total messages at start 50.
    """
    message_list = create_messages(url, user_1, default_channel['channel_id'], 0, 51)
    assert len(message_list) == 51
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 50,
    }).json()
    assert len(message_list[50:]) == len(resp['messages'])
    for index, item in enumerate(resp['messages']):
        index += 50
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(resp['messages']) == 1
    assert resp['start'] == 50
    assert resp['end'] == -1
    requests.delete(url + '/clear')

def test_output_messages_100_start_10(url, user_1, default_channel):
    """Testing when a channel has 100 total messages at start 10.
    """
    message_list = create_messages(url, user_1, default_channel['channel_id'], 0, 100)
    assert len(message_list) == 100
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 10,
    }).json()
    assert len(message_list[10:60]) == len(resp['messages'])
    for index, item in enumerate(resp['messages']):
        index += 10
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(resp['messages']) == 50
    assert resp['start'] == 10
    assert resp['end'] == 60
    requests.delete(url + '/clear')

#! Testing using examples provided in specification (refer to 6.5. Pagination)
def test_output_messages_125_start_0(url, user_1, default_channel):
    """Testing when a channel has 125 total messages at start 0.
    """
    message_list = create_messages(url, user_1, default_channel['channel_id'], 0, 125)
    assert len(message_list) == 125
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 0,
    }).json()
    assert len(message_list[0:50]) == len(resp['messages'])
    for index, item in enumerate(resp['messages']):
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(resp['messages']) == 50
    assert resp['start'] == 0
    assert resp['end'] == 50
    requests.delete(url + '/clear')

def test_output_messages_125_start_50(url, user_1, default_channel):
    """Testing when a channel has 125 total messages at start 50.
    """
    message_list = create_messages(url, user_1, default_channel['channel_id'], 0, 125)
    assert len(message_list) == 125
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 50,
    }).json()
    assert len(message_list[50:100]) == len(resp['messages'])
    for index, item in enumerate(resp['messages']):
        index += 50
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(resp['messages']) == 50
    assert resp['start'] == 50
    assert resp['end'] == 100
    requests.delete(url + '/clear')

def test_output_messages_125_start_100(url, user_1, default_channel):
    """Testing when a channel has 125 total messages at start 100.
    """
    message_list = create_messages(url, user_1, default_channel['channel_id'], 0, 125)
    assert len(message_list) == 125
    resp = requests.get(url + '/channel/messages', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id'],
        'start': 100,
    }).json()
    assert len(message_list[100:]) == len(resp['messages'])
    for index, item in enumerate(resp['messages']):
        index += 100
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(resp['messages']) == 25
    assert resp['start'] == 100
    assert resp['end'] == -1
    requests.delete(url + '/clear')

#------------------------------------------------------------------------------#
#                              channel/leave                                   #
#------------------------------------------------------------------------------#

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

    payload = requests.get(f'{url}/channels/listall', params={
        'token': user_1['token'],
    }).json()

    for curr_channel in payload['channels']:
        assert curr_channel['channel_id'] != default_channel['channel_id']

    requests.delete(f'{url}/clear')

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

    payload = requests.get(f'{url}/channel/details', params={
        'token': user_1['token'],
        'channel_id': default_channel['channel_id']
    }).json()

    user_1_details = {'u_id': user_1['u_id'], 'name_first': 'John', 'name_last': 'Smith'}
    assert user_1_details in payload['owner_members']
    assert user_1_details in payload['all_members']

    requests.delete(f'{url}/clear')

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

    payload = requests.get(f'{url}/channel/details', params={
        'token': user_2['token'],
        'channel_id': default_channel['channel_id']
    }).json()
    user_2_details = {'u_id': user_2['u_id'], 'name_first': 'Jane', 'name_last': 'Smith'}
    assert user_2_details not in payload['owner_members']
    assert user_2_details in payload['all_members']

    requests.delete(f'{url}/clear')
    
#------------------------------------------------------------------------------#
#                                   channel_join                               #
#------------------------------------------------------------------------------#

#?------------------------- Input/Access Error Testing -----------------------?#

def test_input_join_channel_id(url, user_1):
    """Testing when Channel ID is not a valid channel
    """
    arg_join = {
        'token'     : user_1['token'],
        'channel_id': -1,
    }
    res_err = requests.post(url + 'channel/join', json=arg_join)
    assert res_err.status_code == InputError.code

    arg_join = {
        'token'     : user_1['token'],
        'channel_id': 0,
    }
    res_err = requests.post(url + 'channel/join', json=arg_join)
    assert res_err.status_code == InputError.code

    arg_join = {
        'token'     : user_1['token'],
        'channel_id': 5,
    }
    res_err = requests.post(url + 'channel/join', json=arg_join)
    assert res_err.status_code == InputError.code

    arg_join = {
        'token'     : user_1['token'],
        'channel_id': 1,
    }
    res_err = requests.post(url + 'channel/join', json=arg_join)
    assert res_err.status_code == InputError.code
    requests.delete(url + '/clear')

def test_access_join_valid_token(url, user_1, default_channel):
    """Testing if token is valid
    """
    log_out = requests.post(url + 'auth/logout', json={'token': user_1['token']}).json()
    assert log_out['is_success']

    arg_join = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
    }
    res_err = requests.post(url + 'channel/join', json=arg_join)
    assert res_err.status_code == InputError.code
    requests.delete(url + '/clear')

def test_access_join_user_is_member(url, user_1, user_2, user_3):
    """Testing if channel_id refers to a channel that is private (when the
    authorised user is not a global owner)
    """
    # Channel is private
    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': False,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    channel_profile = {
        'token'    : user_2['token'],
        'name'     : 'Group 2',
        'is_public': False,
    }
    new_channel_2 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_join = {
        'token'     : user_3['token'],
        'channel_id': new_channel_2['channel_id'],
    }
    res_err = requests.post(url + 'channel/join', json=arg_join)
    assert res_err.status_code == AccessError.code

    arg_join = {
        'token'     : user_2['token'],
        'channel_id': new_channel_1['channel_id'],
    }
    res_err = requests.post(url + 'channel/join', json=arg_join)
    assert res_err.status_code == AccessError.code
    requests.delete(url + '/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_output_user_join_public(url, user_1, user_2, default_channel):
    """Testing if the user has successfully joined a public channel
    """
    arg_join = {
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    # Check channel details if the user is a member
    arg_details = {
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
    }
    channel_data = requests.get(url + 'channel/details', params=arg_details).json()
    in_channel = False
    for member in channel_data['all_members']:
        if member['u_id'] is user_2['u_id']:
            in_channel = True
            break
    assert in_channel

    # Check if channel appears in the user's channels list
    arg_list = {
        'token'     : user_2['token'],
    }
    channel_user_list = requests.get(url + 'channels/list', params=arg_list).json()
    assert len(channel_user_list) == 1
    requests.delete(url + '/clear')

def test_output_user_join_flockr_private(url, user_1, user_2):
    """Test for flockr owner (flockr owner can join private channels)
    """
    # Make a private channel and check if flockr owner
    channel_profile = {
        'token'    : user_2['token'],
        'name'     : 'Private Group 1',
        'is_public': False,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    # Assume that the first user is the flockr owner
    arg_join = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    arg_list = {
        'token'     : user_2['token'],
    }
    channel_list = requests.get(url + 'channels/list', params=arg_list).json()

    # Check if flockr owner is in channel list
    in_channel = False
    for curr_channel in channel_list['channels']:
        if curr_channel['channel_id'] == new_channel_1['channel_id']:
            in_channel = True
            break
    assert in_channel
    requests.delete(url + '/clear')

def test_output_user_join_flockr_member_list(url, user_1, user_2):
    """Test for flockr owner (flockr owner can join private channels)
    """
    # Make a private channel and check if flockr owner
    channel_profile = {
        'token'    : user_2['token'],
        'name'     : 'Private Group 1',
        'is_public': False,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    # Assume that the first user is the flockr owner
    arg_join = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    # Check if flockr owner is a channel member
    arg_details = {
        'token'     : user_2['token'],
        'channel_id': new_channel_1['channel_id'],
    }
    channel_data = requests.get(url + 'channel/details', params=arg_details).json()
    is_member = False
    for member in channel_data['all_members']:
        if member['u_id'] == user_1['u_id']:
            is_member = True
            break
    assert is_member
    requests.delete(url + '/clear')

def test_output_user_join_flockr_owner_list(url, user_1, user_2):
    """Test for flockr owner (flockr owner can join private channels)
    """
    # Make a private channel and check if flockr owner
    channel_profile = {
        'token'    : user_2['token'],
        'name'     : 'Private Group 1',
        'is_public': False,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    # Assume that the first user is the flockr owner
    arg_join = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    # Flockr owner becomes owner after channel join
    owner = True
    arg_details = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
    }
    channel_data = requests.get(url + 'channel/details', params=arg_details).json()
    for member in channel_data['owner_members']:
        if member['u_id'] == user_1['u_id']:
            owner = False
    assert not owner
    requests.delete(url + '/clear')

def test_output_user_join_again(url, user_1):
    """Test for a person joining again
    """
    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': False,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_details = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
    }
    channel_data = requests.get(url + 'channel/details', params=arg_details).json()

    user_details = {'name_first': 'John', 'name_last': 'Smith', 'u_id': user_1['u_id']}
    assert user_details in channel_data['all_members']

    arg_join = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    # Check channel details if the user is a member
    arg_details = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
    }
    channel_data = requests.get(url + 'channel/details', params=arg_details).json()
    assert user_details in channel_data['all_members']

    # Check if channel appears in the user's channels list
    arg_list = {
        'token'     : user_1['token'],
    }
    channel_user_list = requests.get(url + 'channels/list', params=arg_list).json()
    assert len(channel_user_list) == 1
    requests.delete(url + '/clear')

#------------------------------------------------------------------------------#
#                                channel_addowner                              #
#------------------------------------------------------------------------------#

#?------------------------- Input/Access Error Testing -----------------------?#

def test_input_channel_id_addowner(url, user_1):
    """Testing when Channel ID is not a valid channel
    """
    arg_addowner = {
        'token'     : user_1['token'],
        'channel_id': -1,
        'u_id'      : user_1['u_id'],
    }
    res_err = requests.post(url + 'channel/addowner', json=arg_addowner)
    assert res_err.status_code == InputError.code

    arg_addowner = {
        'token'     : user_1['token'],
        'channel_id': 0,
        'u_id'      : user_1['u_id'],
    }
    res_err = requests.post(url + 'channel/addowner', json=arg_addowner)
    assert res_err.status_code == InputError.code

    arg_addowner = {
        'token'     : user_1['token'],
        'channel_id': 1,
        'u_id'      : user_1['u_id'],
    }
    res_err = requests.post(url + 'channel/addowner', json=arg_addowner)
    assert res_err.status_code == InputError.code

    arg_addowner = {
        'token'     : user_1['token'],
        'channel_id': 5,
        'u_id'      : user_1['u_id'],
    }
    res_err = requests.post(url + 'channel/addowner', json=arg_addowner)
    assert res_err.status_code == InputError.code
    requests.delete(url + '/clear')

def test_access_add_valid_token(url, user_1, default_channel):
    """Testing if token is valid
    """
    log_out = requests.post(url + 'auth/logout', json={'token': user_1['token']}).json()
    assert log_out['is_success']

    arg_addowner = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_1['u_id'],
    }
    res_err = requests.post(url + 'channel/addowner', json=arg_addowner)
    assert res_err.status_code == AccessError.code
    requests.delete(url + '/clear')

def test_input_u_id_addowner(url, user_1):
    """Testing when u_id is not a valid u_id
    """
    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': False,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_addowner = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'u_id'      : -1,
    }
    res_err = requests.post(url + 'channel/addowner', json=arg_addowner)
    assert res_err.status_code == InputError.code

    arg_addowner = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'u_id'      : 0,
    }
    res_err = requests.post(url + 'channel/addowner', json=arg_addowner)
    assert res_err.status_code == InputError.code

    arg_addowner = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'u_id'      : 5,
    }
    res_err = requests.post(url + 'channel/addowner', json=arg_addowner)
    assert res_err.status_code == InputError.code

    arg_addowner = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'u_id'      : 7,
    }
    res_err = requests.post(url + 'channel/addowner', json=arg_addowner)
    assert res_err.status_code == InputError.code
    requests.delete(url + '/clear')

def test_add_user_is_already_owner(url, user_1, user_2):
    """Testing when user with user id u_id is already an owner of the channel
    """
    # Channel is private (creators are already owners)
    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': False,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    channel_profile = {
        'token'    : user_2['token'],
        'name'     : 'Group 2',
        'is_public': False,
    }
    new_channel_2 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_addowner = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'u_id'      : user_1['u_id'],
    }
    res_err = requests.post(url + 'channel/addowner', json=arg_addowner)
    assert res_err.status_code == InputError.code

    arg_addowner = {
        'token'     : user_2['token'],
        'channel_id': new_channel_2['channel_id'],
        'u_id'      : user_2['u_id'],
    }
    res_err = requests.post(url + 'channel/addowner', json=arg_addowner)
    assert res_err.status_code == InputError.code
    requests.delete(url + '/clear')

def test_auth_user_is_not_owner(url, user_1, user_2):
    """Testing when the authorised user is not an owner of the flockr, or an owner of this channel
    """
    # User_1 is owner of new_channel_1 and User_2 is the owner of new_channel_2
    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': False,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    channel_profile = {
        'token'    : user_2['token'],
        'name'     : 'Group 2',
        'is_public': False,
    }
    new_channel_2 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_addowner = {
        'token'     : user_1['token'],
        'channel_id': new_channel_2['channel_id'],
        'u_id'      : user_1['u_id'],
    }
    res_err = requests.post(url + 'channel/addowner', json=arg_addowner)
    res_err.status_code == AccessError.code

    arg_addowner = {
        'token'     : user_2['token'],
        'channel_id': new_channel_1['channel_id'],
        'u_id'      : user_2['u_id'],
    }
    res_err = requests.post(url + 'channel/addowner', json=arg_addowner)
    assert res_err.status_code == AccessError.code
    requests.delete(url + '/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_output_user_addowner_private(url, user_1, user_2):
    """Testing if the user has successfully been added as owner of the channel (private)
    """
    # Make a private channel
    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': False,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_addowner = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'u_id'      : user_2['u_id'],
    }
    requests.post(url + 'channel/addowner', json=arg_addowner).json()

    arg_details = {
        'token'     : user_2['token'],
        'channel_id': new_channel_1['channel_id'],
    }
    channel_data = requests.get(url + 'channel/details', params=arg_details).json()
    user_2_details = {'name_first': 'Jane', 'name_last': 'Smith', 'u_id': user_2['u_id']}
    assert user_2_details in channel_data['all_members']
    assert user_2_details in channel_data['owner_members']
    requests.delete(url + '/clear')

def test_output_user_addowner_public(url, user_1, user_2, default_channel):
    """Testing if the user has successfully been added as owner of the channel (public)
    """
    arg_addowner = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_2['u_id'],
    }
    requests.post(url + 'channel/addowner', json=arg_addowner).json()

    arg_details = {
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
    }
    channel_data = requests.get(url + 'channel/details', params=arg_details).json()
    user_2_details = {'name_first': 'Jane', 'name_last': 'Smith', 'u_id': user_2['u_id']}
    assert user_2_details in channel_data['all_members']
    assert user_2_details in channel_data['owner_members']
    requests.delete(url + '/clear')

def test_output_member_becomes_channel_owner(url, user_1, user_2, default_channel):
    """Testing if the user has become a channel owner from a channel member
    """
    user_2_details = {'name_first': 'Jane', 'name_last': 'Smith', 'u_id': user_2['u_id']}

    arg_join = {
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
    }
    requests.post(url + 'channel/join', json=arg_join).json()

    arg_details = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
    }
    channel_data = requests.get(url + 'channel/details', params=arg_details).json()

    assert user_2_details in channel_data['all_members']
    assert user_2_details not in channel_data['owner_members']

    arg_addowner = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_2['u_id'],
    }
    requests.post(url + 'channel/addowner', json=arg_addowner).json()

    arg_details = {
        'token'     : user_2['token'],
        'channel_id': default_channel['channel_id'],
    }
    channel_data = requests.get(url + 'channel/details', params=arg_details).json()
    assert user_2_details in channel_data['all_members']
    assert user_2_details in channel_data['owner_members']
    requests.delete(url + '/clear')

#------------------------------------------------------------------------------#
#                                channel_removeowner                           #
#------------------------------------------------------------------------------#

#?------------------------- Input/Access Error Testing -----------------------?#

def test_input_removeowner(url, user_1):
    """Testing when Channel ID is not a valid channel
    """
    arg_removeowner = {
        'token'     : user_1['token'],
        'channel_id': -1,
        'u_id'      : user_1['u_id'],
    }
    res_err = requests.post(url + 'channel/removeowner', json=arg_removeowner)
    assert res_err.status_code == InputError.code

    arg_removeowner = {
        'token'     : user_1['token'],
        'channel_id': 0,
        'u_id'      : user_1['u_id'],
    }
    res_err = requests.post(url + 'channel/removeowner', json=arg_removeowner)
    assert res_err.status_code == InputError.code

    arg_removeowner = {
        'token'     : user_1['token'],
        'channel_id': 1,
        'u_id'      : user_1['u_id'],
    }
    res_err = requests.post(url + 'channel/removeowner', json=arg_removeowner)
    assert res_err.status_code == InputError.code

    arg_removeowner = {
        'token'     : user_1['token'],
        'channel_id': 5,
        'u_id'      : user_1['u_id'],
    }
    res_err = requests.post(url + 'channel/removeowner', json=arg_removeowner)
    assert res_err.status_code == InputError.code
    requests.delete(url + '/clear')

def test_access_remove_valid_token(url, user_1, default_channel):
    """Testing if token is valid
    """
    log_out = requests.post(url + 'auth/logout', json={'token': user_1['token']}).json()
    assert log_out['is_success']

    arg_removeowner = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_1['u_id'],
    }
    res_err = requests.post(url + 'channel/removeowner', json=arg_removeowner)
    assert res_err.status_code == AccessError.code
    requests.delete(url + '/clear')

def test_input_u_id_removeowner(url, user_1):
    """Testing when u_id is not a valid u_id
    """
    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': False,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_removeowner = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'u_id'      : -1,
    }
    res_err = requests.post(url + 'channel/removeowner', json=arg_removeowner)
    assert res_err.status_code == InputError.code

    arg_removeowner = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'u_id'      : user_1['u_id'] + 1,
    }
    res_err = requests.post(url + 'channel/removeowner', json=arg_removeowner)
    assert res_err.status_code == InputError.code

    arg_removeowner = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'u_id'      : user_1['u_id'] - 1,
    }
    res_err = requests.post(url + 'channel/removeowner', json=arg_removeowner)
    assert res_err.status_code == InputError.code

    arg_removeowner = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'u_id'      : user_1['u_id'] + 7,
    }
    res_err = requests.post(url + 'channel/removeowner', json=arg_removeowner)
    assert res_err.status_code == InputError.code
    requests.delete(url + '/clear')

def test_remove_user_is_not_owner(url, user_1, user_2, user_3):
    """Testing when user with user id u_id is not an owner of the channel
    """
    # Channel is private (users are already owners)
    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': False,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    channel_profile = {
        'token'    : user_2['token'],
        'name'     : 'Group 2',
        'is_public': False,
    }
    new_channel_2 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_removeowner = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'u_id'      : user_2['u_id'] + 7,
    }
    res_err = requests.post(url + 'channel/removeowner', json=arg_removeowner)
    assert res_err.status_code == InputError.code

    arg_removeowner = {
        'token'     : user_2['token'],
        'channel_id': new_channel_2['channel_id'],
        'u_id'      : user_3['u_id'] + 7,
    }
    res_err = requests.post(url + 'channel/removeowner', json=arg_removeowner)
    assert res_err.status_code == InputError.code
    requests.delete(url + '/clear')

def test_remove_user_is_owner(url, user_1, user_2):
    """Testing when the authorised user is not an owner of the flockr, or an owner of this channel
    """
    # Channel is private (users are not owners)
    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': False,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    channel_profile = {
        'token'    : user_2['token'],
        'name'     : 'Group 2',
        'is_public': False,
    }
    new_channel_2 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_removeowner = {
        'token'     : user_2['token'],
        'channel_id': new_channel_1['channel_id'],
        'u_id'      : user_1['u_id'] + 7,
    }
    res_err = requests.post(url + 'channel/removeowner', json=arg_removeowner)
    assert res_err.status_code == AccessError.code

    arg_removeowner = {
        'token'     : user_1['token'],
        'channel_id': new_channel_2['channel_id'],
        'u_id'      : user_2['u_id'] + 7,
    }
    res_err = requests.post(url + 'channel/removeowner', json=arg_removeowner)
    assert res_err.status_code == AccessError.code
    requests.delete(url + '/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_output_user_removeowner_private(url, user_1, user_2):
    """Testing if the user has successfully been removed as owner of the channel (private)
    """
    # Make a private channel
    channel_profile = {
        'token'    : user_1['token'],
        'name'     : 'Group 1',
        'is_public': False,
    }
    new_channel_1 = requests.post(url + 'channels/create', json=channel_profile).json()

    arg_addowner = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'u_id'      : user_2['u_id'],
    }
    requests.post(url + 'channel/addowner', json=arg_addowner).json()

    arg_removeowner = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
        'u_id'      : user_2['u_id'],
    }
    requests.post(url + 'channel/removeowner', json=arg_removeowner).json()

    arg_details = {
        'token'     : user_1['token'],
        'channel_id': new_channel_1['channel_id'],
    }
    channel_data = requests.get(url + 'channel/details', params=arg_details).json()

    for curr_owner in channel_data['owner_members']:
        assert curr_owner['u_id'] is not user_2['u_id']
    requests.delete(url + '/clear')

def test_output_user_removeowner_public(url, user_1, user_2, default_channel):
    """Testing if the user has successfully been removed as owner of the channel (public)
    """
    arg_addowner = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_2['u_id'],
    }
    requests.post(url + 'channel/addowner', json=arg_addowner).json()

    arg_removeowner = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
        'u_id'      : user_2['u_id'],
    }
    requests.post(url + 'channel/removeowner', json=arg_removeowner).json()

    arg_details = {
        'token'     : user_1['token'],
        'channel_id': default_channel['channel_id'],
    }
    channel_data = requests.get(url + 'channel/details', params=arg_details).json()
    for curr_owner in channel_data['owner_members']:
        assert curr_owner['u_id'] is not user_2['u_id']
    requests.delete(url + '/clear')
