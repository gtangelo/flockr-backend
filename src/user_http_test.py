import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
import auth
import channels
import channel
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
#                                 user/profile                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_user_authorised_to_return_profile(url):
    """Test whether user is authorised to return a user's profile.
    """
    requests.delete(f"{url}/clear")
    clear()
    payload_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    })
    user_reg_1 = payload_reg_1.json()

    # Log out the user.
    requests.post(f"{url}/auth/logout", json={
        'token': user_reg_1['token'],
    })

    profile_details = requests.get(f"{url}/user/profile", params={
        'token': user_reg_1['token'],
        'u_id': user_reg_1['u_id'],
    })

    assert profile_details.status_code == AccessError.code

def test_user_invalid(url):
    """Test for returning the profile of a non-existant user.
    """
    requests.delete(f"{url}/clear")
    clear()
    payload_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    })
    user_reg_1 = payload_reg_1.json()

    profile_details = requests.get(f"{url}/user/profile", params={
        'token': user_reg_1['token'],
        'u_id': user_reg_1['u_id'] + 1,
    })

    assert profile_details.status_code == InputError.code


#?------------------------------ Output Testing ------------------------------?#

def test_user_u_id(url):
    """Test whether the user profile u_id matches the u_id returned by auth_register.
    """
    requests.delete(f"{url}/clear")
    clear()
    user_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }).json()

    profile_details = requests.get(f"{url}/user/profile", params={
        'token': user_reg_1['token'],
        'u_id': user_reg_1['u_id'],
    }).json()

    assert user_reg_1['u_id'] == profile_details['user']['u_id']

def test_valid_user_name(url):
    """Test whether the first and last name of a user is the same as the names returned in
    user_profile.
    """
    requests.delete(f"{url}/clear")
    clear()
    user_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }).json()

    profile_details = requests.get(f"{url}/user/profile", params={
        'token': user_reg_1['token'],
        'u_id': user_reg_1['u_id'],
    }).json()

    assert profile_details['user']['name_first'] == 'Harry'
    assert profile_details['user']['name_last'] == 'Potter'

def test_valid_user_email(url):
    """Test whether the user's email matches the email returned in user_profile.
    """
    requests.delete(f"{url}/clear")
    clear()
    user_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }).json()

    profile_details = requests.get(f"{url}/user/profile", params={
        'token': user_reg_1['token'],
        'u_id': user_reg_1['u_id'],
    }).json()

    assert profile_details['user']['email'] == 'test_email@gmail.com'

def test_valid_user_handle(url):
    """Test whether the user's handle string matches the handle string returned in
    user_profile.
    """
    requests.delete(f"{url}/clear")
    clear()
    user_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }).json()

    profile_details = requests.get(f"{url}/user/profile", params={
        'token': user_reg_1['token'],
        'u_id': user_reg_1['u_id'],
    }).json()

    user_list = requests.get(f"{url}/users/all", params={
        'token': user_reg_1['token'],
    }).json()

    handle_str = None
    for account in user_list['users']:
        if account['u_id'] == user_reg_1['u_id']:
            handle_str = account['handle_str']

    assert handle_str == profile_details['user']['handle_str']


#------------------------------------------------------------------------------#
#                             user/profile/setname                             #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#


#------------------------------------------------------------------------------#
#                             user/profile/setemail                            #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_user_valid_setemail(url):
    """Test for whether the user is logged in and authorised to set their email.
    """
    requests.delete(f"{url}/clear")
    clear()
    user_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }).json()

    # Log out the user.
    requests.post(f"{url}/auth/logout", json={
        'token': user_reg_1['token'],
    })

    ret_email = requests.put(f"{url}/user/profile/setemail", json={
        'token': user_reg_1['token'],
        'email': 'test123@outlook.com',
    })

    assert ret_email.status_code == AccessError.code


def test_email_already_exists(url):
    """Test for setting an email that is already in use by another registered user.
    """
    pass

#?------------------------------ Output Testing ------------------------------?#



#------------------------------------------------------------------------------#
#                            user/profile/sethandle                            #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#
