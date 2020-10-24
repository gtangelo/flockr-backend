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

def test_update_max_name(url, user_1):
    ''' Testing the basic functionality of maximum length names
    ''' 
    requests.delete(f"{url}/clear")
    clear()
    data = {
        'token': user_1['token'],
        'name_first': 'c'*51,
        'name_last': 'Michael',
    }
    result = requests.put(f"{url}/user/profile/setname", json = data)
    assert result.status_code == InputError.code

    data_1 = {
        'token': user_1['token'],
        'name_first': 'c'*50,
        'name_last': 'c'*51,
    }
    result_1 = requests.put(f"{url}/user/profile/setname", json = data_1)
    assert result_1.status_code == InputError.code

    data_2 = {
        'token': user_1['token'],
        'name_first': 'c'*51,
        'name_last': 'c'*51,
    }
    result_2 = requests.put(f"{url}/user/profile/setname", json = data_2)
    assert result_2.status_code == InputError.code

    data_3 = {
        'token': user_1['token'],
        'name_first': 'c'*50,
        'name_last': 'c'*50,
    }
    requests.put(f"{url}/user/profile/setname", json = data_3)
    result_users = requests.get(f"{url}/users/all", params = {'token': user_1['token']}).json()
    for user in result_users['users']:
        if user['u_id'] == user_1['u_id']:
            assert user['name_first'] == 'c'*50
            assert user['name_last'] == 'c'*50
    
def test_update_min_name(url, user_1):
    ''' Testing the basic functionality of maximum length names
    ''' 
    requests.delete(f"{url}/clear")
    clear()

    data = {
        'token': user_1['token'],
        'name_first': '',
        'name_last': 'Michael',
    }
    result = requests.put(f"{url}/user/profile/setname", json = data)
    assert result.status_code == InputError.code

    data_1 = {
        'token': user_1['token'],
        'name_first': 'c'*50,
        'name_last': '',
    }
    result_1 = requests.put(f"{url}/user/profile/setname", json = data_1)
    assert result_1.status_code == InputError.code

    data_2 = {
        'token': user_1['token'],
        'name_first': '',
        'name_last': '',
    }
    result_2 = requests.put(f"{url}/user/profile/setname", json = data_2)
    assert result_2.status_code == InputError.code

    data_3 = {
        'token': user_1['token'],
        'name_first': 'c',
        'name_last': 'c',
    }
    requests.put(f"{url}/user/profile/setname", json = data_3)
    result_users = requests.get(f"{url}/users/all", params = {'token': user_1['token']})
    users_1 = result_users.json()
    for user in users_1['users']:
        if user['u_id'] == user_1['u_id']:
            assert user['name_first'] == 'c'
            assert user['name_last'] == 'c'

    
def test_update_invalid_token(url, user_1):
    requests.delete(f"{url}/clear")
    clear()
    
    requests.post(f"{url}/auth/logout", json = {'token': user_1['token']})
    data = {
        'token': user_1['token'],
        'name_first': 'Bobby',
        'name_last': 'Michael',
    }
    result = requests.put(f"{url}/user/profile/setname", json = data)
    assert result.status_code == InputError.code

def test_invalid_chars(url, user_1):
    requests.delete(f"{url}/clear")
    clear()
    data = {
        'token': user_1['token'],
        'name_first': '%#$$$2JE',
        'name_last': '42Hello',
    }
    result = requests.put(f"{url}/user/profile/setname", json = data)
    assert result.status_code == InputError.code
    data = {
        'token': user_1['token'],
        'name_first': 'Christian',
        'name_last': 'Michae l',
    }
    result = requests.put(f"{url}/user/profile/setname", json = data)
    assert result.status_code == InputError.code

#?------------------------------ Output Testing ------------------------------?#

def test_update_names(url, user_1):
    ''' Testing the basic functionality of changing names
    ''' 
    requests.delete(f"{url}/clear")
    clear()

    data = {
        'token': user_1['token'],
        'name_first': 'Bobby',
        'name_last': 'Michael',
    }
    requests.put(f"{url}/user/profile/setname", json = data)
    result_users = requests.get(f"{url}/users/all", params = {'token': user_1['token']})
    users = result_users.json()
    for user in users['users']:
        if user['u_id'] == user_1['u_id']:
            assert user['name_first'] == 'Bobby'
            assert user['name_last'] == 'Michael'

def test_update_name_first(url, user_1):
    ''' Testing the basic functionality of changing only the first name
    ''' 
    requests.delete(f"{url}/clear")
    clear()
    
    data = {
        'token': user_1['token'],
        'name_first': 'Michael',
        'name_last': 'Ilagan',
    }
    requests.put(f"{url}/user/profile/setname", json = data)
    result_users = requests.get(f"{url}/users/all", params = {'token': user_1['token']})
    users = result_users.json()
    for user in users['users']:
        if user['u_id'] == user_1['u_id']:
            assert user['name_first'] == 'Michael'
            assert user['name_last'] == 'Ilagan'

def test_update_name_last(url, user_1):
    ''' Testing the basic functionality of changing only the last name
    ''' 
    requests.delete(f"{url}/clear")
    clear()
    
    data = {
        'token': user_1['token'],
        'name_first': 'Christian',
        'name_last': 'Michael',
    }
    requests.put(f"{url}/user/profile/setname", json = data)
    result_users = requests.get(f"{url}/users/all", params = {'token': user_1['token']})
    users = result_users.json()
    for user in users['users']:
        if user['u_id'] == user_1['u_id']:
            assert user['name_first'] == 'Christian'
            assert user['name_last'] == 'Michael'

def test_update_consecutively(url, user_1):
    ''' Testing the basic functionality constantly changing names
    ''' 
    requests.delete(f"{url}/clear")
    clear()
    
    data = {
        'token': payload_reg['token'],
        'name_first': 'Bobby',
        'name_last': 'Michael',
    }
    requests.put(f"{url}/user/profile/setname", json = data)
    result_users = requests.get(f"{url}/users/all", params = {'token': user_1['token']})
    users = result_users.json()
    for user in users['users']:
        if user['u_id'] == user_1['u_id']:
            assert user['name_first'] == 'Bobby'
            assert user['name_last'] == 'Michael'
    data_1 = {
        'token': payload_reg['token'],
        'name_first': 'Chriss',
        'name_last': 'Smithh',
    }
    requests.put(f"{url}/user/profile/setname", json = data_1)
    result_users_1 = requests.get(f"{url}/users/all", params = {'token': user_1['token']})
    users_1 = result_users_1.json()
    for user in users_1['users']:
        if user['u_id'] == user_1['u_id']:
            assert user['name_first'] == 'Chriss'
            assert user['name_last'] == 'Smithh'
    data_2 = {
        'token': user_1['token'],
        'name_first': 'Harry',
        'name_last': 'John',
    }
    requests.put(f"{url}/user/profile/setname", json = data_2)
    result_users_2 = requests.get(f"{url}/users/all", params = {'token': user_1['token']})
    users_2 = result_users_2.json()
    for user in users_2['users']:
        if user['u_id'] == user_1['u_id']:
            assert user['name_first'] == 'Harry'
            assert user['name_last'] == 'John'
    
def test_update_multiple_users(url, user_1, user_2, user_3):
    requests.delete(f"{url}/clear")
    clear()

    data_1 = {
        'token': user_1['token'],
        'name_first': 'Chriss',
        'name_last': 'Smithh',
    }
    data_2 = {
        'token': user_2['token'],
        'name_first': 'Bobby',
        'name_last': 'Smithh',
    }
    data_3 = {
        'token': user_3['token'],
        'name_first': 'Chriss',
        'name_last': 'Smoothie',
    }
    requests.put(f"{url}/user/profile/setname", json = data_1)
    result_users_1 = requests.get(f"{url}/users/all", params = {'token': user_1['token']})
    users_1 = result_users_1.json()
    for user in users_1['users']:
        if user['u_id'] == user_1['u_id']:
            assert user['name_first'] == 'Chriss'
            assert user['name_last'] == 'Smithh'
    requests.put(f"{url}/user/profile/setname", json = data_2)
    result_users_2 = requests.get(f"{url}/users/all", params = {'token': user_2['token']})
    users_2 = result_users_2.json()
    for user in users_2['users']:
        if user['u_id'] == user_2['u_id']:
            assert user['name_first'] == 'Bobby'
            assert user['name_last'] == 'Smithh'
    requests.put(f"{url}/user/profile/setname", json = data_3)
    result_users_3 = requests.get(f"{url}/users/all", params = {'token': user_3['token']})
    users_3 = result_users_3.json()
    for user in users_3['users']:
        if user['u_id'] == user_3['u_id']:
            assert user['name_first'] == 'Chriss'
            assert user['name_last'] == 'Smoothie'

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
    requests.delete(f"{url}/clear")
    clear()
    user_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }).json()
    requests.post(f"{url}/auth/register", json={
        'email' : 'test2_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Ron',
        'name_last' : 'Weasly',
    }).json()

    ret_email = requests.put(f"{url}/user/profile/setemail", json={
        'token': user_reg_1['token'],
        'email': 'test2_email@gmail.com',
    })
    
    assert ret_email.status_code == InputError.code

def test_update_same_email(url):
    """Setting the email that the user already has raises an error.
    """
    requests.delete(f"{url}/clear")
    clear()
    user_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }).json()

    ret_email = requests.put(f"{url}/user/profile/setemail", json={
        'token': user_reg_1['token'],
        'email': 'test_email@gmail.com',
    })
    
    assert ret_email.status_code == InputError.code

def test_ivalid_domain(url):
    """Test for no '@' character and missing string in the domain.
    """
    requests.delete(f"{url}/clear")
    clear()
    user_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }).json()

    ret_email = requests.put(f"{url}/user/profile/setemail", json={
        'token': user_reg_1['token'],
        'email': 'harry.potter.com',
    })
    
    assert ret_email.status_code == InputError.code

def test_no_period(url):
    """Test for no period '.' in the domain.
    """
    requests.delete(f"{url}/clear")
    clear()
    user_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }).json()

    ret_email = requests.put(f"{url}/user/profile/setemail", json={
        'token': user_reg_1['token'],
        'email': 'harry\\potter@outlookcom',
    })
    
    assert ret_email.status_code == InputError.code

def test_capital_letter(url):
    """Setting a capital letter anywhere in the personal info part raises an 
    InputError. (Assumptions-based)
    """
    requests.delete(f"{url}/clear")
    clear()
    user_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }).json()

    ret_email = requests.put(f"{url}/user/profile/setemail", json={
        'token': user_reg_1['token'],
        'email': 'harry.Potter@outlook.com',
    })
    
    assert ret_email.status_code == InputError.code

def test_invalid_special_char(url):
    """Test for invalid characters (including special characters other than '\', '.' or '_').
    """
    requests.delete(f"{url}/clear")
    clear()
    user_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }).json()

    ret_email = requests.put(f"{url}/user/profile/setemail", json={
        'token': user_reg_1['token'],
        'email': 'h$rry_p*tter@gmail.com',
    })
    
    assert ret_email.status_code == InputError.code

def test_invalid_special_char_pos(url):
    """Test for characters '\', '.' or '_' at the end or start of the personal info part.
    """
    requests.delete(f"{url}/clear")
    clear()
    user_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }).json()

    email = r'\harry_potter@bigpond.net'
    ret_email = requests.put(f"{url}/user/profile/setemail", json={
        'token': user_reg_1['token'],
        'email': email,
    })

    assert ret_email.status_code == InputError.code

#?------------------------------ Output Testing ------------------------------?#

def test_valid_email(url):
    """Test for basic functionality for updating user email.
    """
    requests.delete(f"{url}/clear")
    clear()
    user_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }).json()

    requests.put(f"{url}/user/profile/setemail", json={
        'token': user_reg_1['token'],
        'email': 'harry_potter@bigpond.net',
    })

    profile_details = requests.get(f"{url}/user/profile", params={
        'token': user_reg_1['token'],
        'u_id': user_reg_1['u_id'],
    }).json()

    assert 'harry_potter@bigpond.net' == profile_details['user']['email']

def test_varying_domain(url):
    """Test for a domain other than @gmail.com
    """
    requests.delete(f"{url}/clear")
    clear()
    user_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }).json()

    requests.put(f"{url}/user/profile/setemail", json={
        'token': user_reg_1['token'],
        'email': 'harry.potter@company.co',
    })

    profile_details = requests.get(f"{url}/user/profile", params={
        'token': user_reg_1['token'],
        'u_id': user_reg_1['u_id'],
    }).json()
    
    assert 'harry.potter@company.co' == profile_details['user']['email']

def test_update_email_four_times(url):
    """Test for multiple attempts at updating a user email.
    """
    requests.delete(f"{url}/clear")
    clear()
    user_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }).json()

    requests.put(f"{url}/user/profile/setemail", json={
        'token': user_reg_1['token'],
        'email': 'harry.potter@company.co',
    })

    requests.put(f"{url}/user/profile/setemail", json={
        'token': user_reg_1['token'],
        'email': 'helloworld@company.co',
    })

    requests.put(f"{url}/user/profile/setemail", json={
        'token': user_reg_1['token'],
        'email': 'hogwarts@island.com',
    })

    profile_details = requests.get(f"{url}/user/profile", params={
        'token': user_reg_1['token'],
        'u_id': user_reg_1['u_id'],
    }).json()
    
    assert 'hogwarts@island.com' == profile_details['user']['email']

def test_min_requirements(url):
    """Test for an email with very minimal requirements (2 letters in the personal
    part, a '@' symbol, at least 1 letter before and after the period in the domain).
    (Assumption-based)
    """
    requests.delete(f"{url}/clear")
    clear()
    user_reg_1 = requests.post(f"{url}/auth/register", json={
        'email' : 'test_email@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Harry',
        'name_last' : 'Potter',
    }).json()

    requests.put(f"{url}/user/profile/setemail", json={
        'token': user_reg_1['token'],
        'email': 'ha@l.c',
    })

    profile_details = requests.get(f"{url}/user/profile", params={
        'token': user_reg_1['token'],
        'u_id': user_reg_1['u_id'],
    }).json()
    
    assert 'ha@l.c' == profile_details['user']['email']

#------------------------------------------------------------------------------#
#                            user/profile/sethandle                            #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_handle_exists(url, user_1, user_2):
    ''' Testing that a user cannot change their handle to an already existing handle
    '''
    requests.delete(f"{url}/clear")
    clear()

    requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': 'valid_handle0',
    })
    result = requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_2['token'],
        'handle_str': 'valid_handle0',
    })
    assert result.status_code == InputError.code

def test_handle_min(url, user_1):
    ''' Testing that a user cannot change their handle below the min chars
    '''
    requests.delete(f"{url}/clear")
    clear()

    requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': 'c'*3,
    })

    requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': 'c'*10,
    })

    result_1 = requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': 'c'*2,
    })
    result_2 = requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': '',
    })
    assert result_1.status_code == InputError.code
    assert result_2.status_code == InputError.code

def test_handle_max(url, user_1):
    ''' Testing that a user cannot change their handle above the max chars
    '''
    requests.delete(f"{url}/clear")
    clear()

    requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': 'c'*20,
    })

    requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': 'c'*15,
    })

    result_1 = requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': 'c'*21,
    })
    result_2 = requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': 'c'*50,
    })
    assert result_1.status_code == InputError.code
    assert result_2.status_code == InputError.code

def test_update_handle_invalid_token(url, user_1):
    ''' Testing that an invalid token will not allow you to change the handle
    '''
    requests.delete(f"{url}/clear")
    clear()

    requests.post(f"{url}/auth/logout", json = {'token': user_1['token']})
    result_1 = requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': 'c'*20,
    })
    assert result_1.status_code == InputError.code

def test_update_handle_same(url, user_1):
    ''' Testing that a user cannot change their handle to their current handle
    '''
    requests.delete(f"{url}/clear")
    clear()
    
    requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': 'c'*20,
    })
    result_1 = requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': 'c'*20,
    })
    assert result_1.status_code == InputError.code

def test_update_handle_chars(url, user_1):
    ''' Testing invalid chars in handle
    '''
    requests.delete(f"{url}/clear")
    clear()
    
    requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': 'Christian!'*20,
    })
    requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': 'Micha@l'*20,
    })
    requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': 'Micha@l'*20,
    })
    result_1 = requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': 'Hel @l'*20,
    })
    assert result_1.status_code == InputError.code
#?------------------------------ Output Testing ------------------------------?#

def test_handle_basic(url, user_1):
    ''' Testing the basic functionality of updating a handle
    '''
    requests.delete(f"{url}/clear")
    clear()

    requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': 'valid_handle',
    })

    profile_details = requests.get(f"{url}/user/profile", params={
        'token': user_1['token'],
        'u_id': user_1['u_id'],
    }).json()

    assert profile_details['user']['handle_str'] == 'valid_handle'

def test_handle_prefix(url, user_1, user_2, user_3):
    ''' Testing the basic functionality of updating a handle
    '''
    requests.delete(f"{url}/clear")
    clear()

    profile_details_1 = requests.get(f"{url}/user/profile", params={
        'token': user_1['token'],
        'u_id': user_1['u_id'],
    }).json()

    profile_details_2 = requests.get(f"{url}/user/profile", params={
        'token': user_2['token'],
        'u_id': user_2['u_id'],
    }).json()

    profile_details_3 = requests.get(f"{url}/user/profile", params={
        'token': user_3['token'],
        'u_id': user_3['u_id'],
    }).json()

    assert profile_details_1['user']['handle_str'] != profile_details_2['user']['handle_str']
    assert profile_details_2['user']['handle_str'] != profile_details_3['user']['handle_str']
    assert profile_details_1['user']['handle_str'] != profile_details_3['user']['handle_str']

    requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_1['token'],
        'handle_str': 'valid_handle0',
    })

    requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_2['token'],
        'handle_str': 'valid_handle1',
    })

    requests.put(f"{url}/user/profile/sethandle", json={
        'token': user_3['token'],
        'handle_str': 'valid_handle2',
    })

    profile_details_1 = requests.get(f"{url}/user/profile", params={
        'token': user_1['token'],
        'u_id': user_1['u_id'],
    }).json()

    profile_details_2 = requests.get(f"{url}/user/profile", params={
        'token': user_2['token'],
        'u_id': user_2['u_id'],
    }).json()

    profile_details_3 = requests.get(f"{url}/user/profile", params={
        'token': user_3['token'],
        'u_id': user_3['u_id'],
    }).json()
    assert profile_details_1['user']['handle_str'] == 'valid_handle0'
    assert profile_details_2['user']['handle_str'] == 'valid_handle1'
    assert profile_details_3['user']['handle_str'] == 'valid_handle2'
    assert profile_details_1['user']['handle_str'] != profile_details_2['user']['handle_str']
    assert profile_details_2['user']['handle_str'] != profile_details_3['user']['handle_str']
    assert profile_details_1['user']['handle_str'] != profile_details_3['user']['handle_str']


