import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests


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
def public_channel_2(url, user_2):
    return requests.post(f'{url}/channels/create', json={
        'token': user_2['token'],
        'name': 'Group 2',
        'is_public': True,
    }).json()

@pytest.fixture
def public_channel_3(url, user_3):
    return requests.post(f'{url}/channels/create', json={
        'token': user_3['token'],
        'name': 'Group 3',
        'is_public': True,
    }).json()

@pytest.fixture
def public_channel_4(url, user_4):
    return requests.post(f'{url}/channels/create', json={
        'token': user_4['token'],
        'name': 'Group 4',
        'is_public': True,
    }).json()

@pytest.fixture
def private_channel_1(url, user_1):
    return requests.post(f'{url}/channels/create', json={
        'token': user_1['token'],
        'name': 'Group 1',
        'is_public': False,
    }).json()
#------------------------------------------------------------------------------#
#                                 user/profile                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#



#------------------------------------------------------------------------------#
#                             user/profile/setname                             #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#


#------------------------------------------------------------------------------#
#                             user/profile/setemail                            #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#



#------------------------------------------------------------------------------#
#                            user/profile/sethandle                            #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#


