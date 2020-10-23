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
def test_echo(url):
    '''
    A simple test to check echo
    '''
    resp = requests.get(url + 'echo', params={'data': 'hello'})
    assert json.loads(resp.text) == {'data': 'hello'}




#------------------------------------------------------------------------------#
#                                 auth/login                                   #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_login_incorrect_password(url):
    ''' Testing using the incorrect password
    '''
    requests.delete(f"{url}/clear")
    clear()
    data_register = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    result_reg = requests.post(f"{url}/auth/register", json = data_register)
    payload_reg = result_reg.json()
    requests.post(f"{url}/auth/logout", json = {'token': payload_reg['token']})
    data_in = {
        'email': 'testEmail@gmail.com',
        'password': 'Incorrectpass',
    }
    result = requests.post(f"{url}/auth/login", json = data_in)
    assert result.status_code == InputError.code

def test_login_invalid_email(url):
    ''' Tests if error handling in login is still valid for emails.
    '''
    requests.delete(f"{url}/clear")
    clear()
    data_in = {
        'email': 'testemail.com',
        'password': 'abcdef',
    }
    result = requests.post(f"{url}/auth/login", json = data_in)
    assert result.status_code == InputError.code

def test_login_invalid_email_0(url):
    ''' Tests if error handling in login is still valid for emails.
    '''
    requests.delete(f"{url}/clear")
    clear()
    data_in = {
        'email': 'testemail@gmailcom',
        'password': 'abcdef',
    }
    result = requests.post(f"{url}/auth/login", json = data_in)
    assert result.status_code == InputError.code

def test_login_invalid_email_1(url):
    ''' Tests if error handling in login is still valid for emails.
    '''
    requests.delete(f"{url}/clear")
    clear()
    data_in = {
        'email': '@gmailcom',
        'password': 'abcdef',
    }
    result = requests.post(f"{url}/auth/login", json = data_in)
    assert result.status_code == InputError.code
    

def test_login_invalid_email_2(url):
    ''' Tests if error handling in login is still valid for emails.
    '''
    requests.delete(f"{url}/clear")
    clear()
    data_in = {
        'email': 'test--email@gmail.com',
        'password': 'abcdef',
    }
    result = requests.post(f"{url}/auth/login", json = data_in)
    assert result.status_code == InputError.code

def test_login_invalid_email_3(url):
    ''' Tests if error handling in login is still valid for emails.
    '''
    requests.delete(f"{url}/clear")
    clear()
    data_in = {
        'email': '',
        'password': 'abcdef',
    }
    result = requests.post(f"{url}/auth/login", json = data_in)
    assert result.status_code == InputError.code

def test_login_invalid_password_chars(url):
    ''' Tests if chars in login is valid for passwords
    '''
    requests.delete(f"{url}/clear")
    clear()
    data_in = {
        'email': 'test-email@gmail.com',
        'password': 'abc',
    }
    result = requests.post(f"{url}/auth/login", json = data_in)
    assert result.status_code == InputError.code
    
def test_login_invalid_password_chars_1(url):
    ''' Tests if chars in login is valid for passwords
    '''
    requests.delete(f"{url}/clear")
    clear()
    data_in = {
        'email': 'test-email@gmail.com',
        'password': 'abc',
    }
    result = requests.post(f"{url}/auth/login", json = data_in)
    assert result.status_code == InputError.code

def test_login_invalid_password_chars_2(url):
    ''' Tests if chars in login is valid for passwords
    '''
    requests.delete(f"{url}/clear")
    clear()
    data_in = {
        'email': 'test-email@gmail.com',
        'password': 'In va lid',
    }
    result = requests.post(f"{url}/auth/login", json = data_in)
    assert result.status_code == InputError.code

def test_login_invalid_password_chars_3(url):
    ''' Tests if chars in login is valid for passwords
    '''
    requests.delete(f"{url}/clear")
    clear()
    data_in = {
        'email': 'test-email@gmail.com',
        'password': '#@&*!@! Hi',
    }
    result = requests.post(f"{url}/auth/login", json = data_in)
    assert result.status_code == InputError.code

def test_login_invalid_password(url):
    ''' Checks if password inputted is valid but not correct
    '''
    requests.delete(f"{url}/clear")
    clear()
    data_register = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    result_reg = requests.post(f"{url}/auth/register", json = data_register)
    payload_reg = result_reg.json()
    requests.post(f"{url}/auth/logout", json = {'token': payload_reg['token']})
    data_in = {
        'email': 'testEmail@gmail.com',
        'password': 'incorrect'
    }
    result = requests.post(f"{url}/auth/login", json = data_in)
    assert result.status_code == InputError.code

def test_login_invalid_user(url):
    ''' Should not be able to login because email does not belong to a user
    '''
    requests.delete(f"{url}/clear")
    clear()
    data_in = {
        'email': 'notRegistered@gmail.com',
        'password': 'Hello!',
    }
    result = requests.post(f"{url}/auth/login", json = data_in)
    assert result.status_code == InputError.code

def test_already_loggedin(url):
    ''' Should not be able to login when they are already logged in.
    '''
    requests.delete(f"{url}/clear")
    clear()
    data_register = {
        'email' : 'testEmail.com',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    requests.post(f"{url}/auth/register", json = data_register)
    data_in = {
        'email': 'testEmail@gmail.com',
        'password': 'abcdefg',
    }
    result = requests.post(f"{url}/auth/login", json = data_in)
    assert result.status_code == InputError.code

#?------------------------------ Output Testing ------------------------------?#

def test_login_basic(url):
    ''' Testing the basic process of logging in.
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_register = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first' : 'Christian',
        'name_last' : 'Ilagan',
    }
    result_reg = requests.post(f"{url}/auth/register", json = data_register)
    payload_reg = result_reg.json()
    requests.post(f"{url}/auth/logout", json = {'token': payload_reg['token']})
    data_in = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
    }
    result = requests.post(f"{url}/auth/login", json = data_in)
    payload = result.json()
    # testing against registering
    assert payload['token'] == payload_reg['token']
    assert payload['u_id'] == payload_reg['u_id']

def test_login_u_id(url):
    ''' Testing that each login has a unique id
    '''
    requests.delete(f"{url}/clear")
    clear()
    data_register_1 = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first' : 'Christian',
        'name_last' : 'Ilagan',
    }
    result_reg_1 = requests.post(f"{url}/auth/register", json = data_register_1)
    payload_reg_1 = result_reg_1.json()
    requests.post(f"{url}/auth/logout", json = {'token': payload_reg_1['token']})
    data_register_2 = {
        'email' : 'testEmail1@gmail.com',
        'password' : 'abcdefg',
        'name_first' : 'Christian',
        'name_last' : 'Ilagan',
    }
    result_reg_2 = requests.post(f"{url}/auth/register", json = data_register_2)
    payload_reg_2 = result_reg_2.json()
    requests.post(f"{url}/auth/logout", json = {'token': payload_reg_2['token']})
    data_register_3 = {
        'email' : 'testEmail2@gmail.com',
        'password' : 'abcdefg',
        'name_first' : 'Christian',
        'name_last' : 'Ilagan',
    }
    result_reg_3 = requests.post(f"{url}/auth/register", json = data_register_3)
    payload_reg_3 = result_reg_3.json()
    requests.post(f"{url}/auth/logout", json = {'token': payload_reg_3['token']})

    # Logging in
    data_in_1 = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
    }
    result_1 = requests.post(f"{url}/auth/login", json = data_in_1)
    payload_1 = result_1.json()

    data_in_2 = {
        'email' : 'testEmail1@gmail.com',
        'password' : 'abcdefg',
    }
    result_2 = requests.post(f"{url}/auth/login", json = data_in_2)
    payload_2 = result_2.json()

    data_in_3 = {
        'email' : 'testEmail2@gmail.com',
        'password' : 'abcdefg',
    }
    result_3 = requests.post(f"{url}/auth/login", json = data_in_3)
    payload_3 = result_3.json()

    assert payload_1['u_id'] is not payload_2['u_id']
    assert payload_2['u_id'] is not payload_3['u_id']
    assert payload_3['u_id'] is not payload_1['u_id']

def test_login_token(url):
    ''' Testing that each login has a unique id
    '''
    requests.delete(f"{url}/clear")
    clear()
    data_register_1 = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first' : 'Christian',
        'name_last' : 'Ilagan',
    }
    result_reg_1 = requests.post(f"{url}/auth/register", json = data_register_1)
    payload_reg_1 = result_reg_1.json()
    requests.post(f"{url}/auth/logout", json = {'token': payload_reg_1['token']})
    data_register_2 = {
        'email' : 'testEmail1@gmail.com',
        'password' : 'abcdefg',
        'name_first' : 'Christian',
        'name_last' : 'Ilagan',
    }
    result_reg_2 = requests.post(f"{url}/auth/register", json = data_register_2)
    payload_reg_2 = result_reg_2.json()
    requests.post(f"{url}/auth/logout", json = {'token': payload_reg_2['token']})
    data_register_3 = {
        'email' : 'testEmail2@gmail.com',
        'password' : 'abcdefg',
        'name_first' : 'Christian',
        'name_last' : 'Ilagan',
    }
    result_reg_3 = requests.post(f"{url}/auth/register", json = data_register_3)
    payload_reg_3 = result_reg_3.json()
    requests.post(f"{url}/auth/logout", json = {'token': payload_reg_3['token']})

     # Logging in
    data_in_1 = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
    }
    result_1 = requests.post(f"{url}/auth/login", json = data_in_1)
    payload_1 = result_1.json()

    data_in_2 = {
        'email' : 'testEmail1@gmail.com',
        'password' : 'abcdefg',
    }
    result_2 = requests.post(f"{url}/auth/login", json = data_in_2)
    payload_2 = result_2.json()

    data_in_3 = {
        'email' : 'testEmail2@gmail.com',
        'password' : 'abcdefg',
    }
    result_3 = requests.post(f"{url}/auth/login", json = data_in_3)
    payload_3 = result_3.json()

    assert payload_1['token'] is not payload_2['token']
    assert payload_2['token'] is not payload_3['token']
    assert payload_3['token'] is not payload_1['token']
#------------------------------------------------------------------------------#
#                                 auth/logout                                  #
#------------------------------------------------------------------------------#

#?------------------------------ Output Testing ------------------------------?#

def test_logout_basic(url):
    ''' Testing basic functionality of logging out
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    r = requests.post(f"{url}/auth/register", json = data_in)
    payload = r.json()
    logout = requests.post(f"{url}/auth/logout", json = {'token': payload['token']})
    payload_log = logout.json()
    assert payload_log['is_success']

def test_logout_invalid_token(url):
    ''' Logging out with and invalid token should not work
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    r = requests.post(f"{url}/auth/register", json = data_in)
    payload = r.json()
    requests.post(f"{url}/auth/logout", json = {'token': payload['token']})
    logout = requests.post(f"{url}/auth/logout", json = {'token': payload['token']})
    payload_log = logout.json()
    assert not payload_log['is_success']
    
def test_logout_multiple(url):
    ''' Testing logging out multiple users
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in_1 = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    r_1 = requests.post(f"{url}/auth/register", json = data_in_1)
    payload_1 = r_1.json()
    data_in_2 = {
        'email' : 'testEmail1@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    r_2 = requests.post(f"{url}/auth/register", json = data_in_2)
    payload_2 = r_2.json()
    data_in_3 = {
        'email' : 'testEmail2@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    r_3 = requests.post(f"{url}/auth/register", json = data_in_3)
    payload_3 = r_3.json()

    logout_1 = requests.post(f"{url}/auth/logout", json = {'token': payload_1['token']})
    payload_1_log = logout_1.json()
    assert payload_1_log['is_success']
    logout_2 = requests.post(f"{url}/auth/logout", json = {'token': payload_2['token']})
    payload_2_log = logout_2.json()
    assert payload_2_log['is_success']
    logout_3 = requests.post(f"{url}/auth/logout", json = {'token': payload_3['token']})
    payload_3_log = logout_3.json()
    assert payload_3_log['is_success']

def test_logout_not_registered(url):
    requests.delete(f"{url}/clear")
    clear()
    invalid_tok = 'hfioeahfsdknlfea'
    logout_1 = requests.post(f"{url}/auth/logout", json = {'token': invalid_tok})
    payload_log = logout_1.json()
    assert not payload_log['is_success']

def test_logout_failures(url):
    ''' Testing basic failures for logout function
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    r = requests.post(f"{url}/auth/register", json = data_in)
    payload = r.json()
    logout = requests.post(f"{url}/auth/logout", json = {'token': payload['token']})
    payload_log = logout.json()
    # user is already logged out
    logout_2 = requests.post(f"{url}/auth/logout", json = {'token': payload['token']})
    payload_2_log = logout_2.json()
    assert payload_log['is_success']
    assert not payload_2_log['is_success']
    
#------------------------------------------------------------------------------#
#                                 auth/register                                #
#------------------------------------------------------------------------------#


#?-------------------------- Input/Access Error Testing ----------------------?#
def test_register_invalid_email(url):
    ''' Testing the process of registering an invalid email
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in = {
        'email' : 'testEmail.com',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    r = requests.post(f"{url}/auth/register", json = data_in)
    assert r.status_code == InputError.code

def test_register_invalid_email_1(url):
    ''' Testing the process of registering an invalid email
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in = {
        'email' : '@com',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    r = requests.post(f"{url}/auth/register", json = data_in)
    assert r.status_code == InputError.code

def test_register_invalid_email_2(url):
    ''' Testing the process of registering an invalid email
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in = {
        'email' : '@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    r = requests.post(f"{url}/auth/register", json = data_in)
    assert r.status_code == InputError.code

def test_register_invalid_email_3(url):
    ''' Testing the process of registering an invalid email
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in = {
        'email' : 'firewall@gmailcom',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    r = requests.post(f"{url}/auth/register", json = data_in)
    assert r.status_code == InputError.code

def test_register_invalid_email_4(url):
    ''' Testing the process of registering an invalid email
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in = {
        'email' : 'test--email@gmailcom',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    r = requests.post(f"{url}/auth/register", json = data_in)
    assert r.status_code == InputError.code

def test_register_invalid_email_5(url):
    ''' Testing the process of registering an invalid email
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in = {
        'email' : '',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    r = requests.post(f"{url}/auth/register", json = data_in)
    assert r.status_code == InputError.code

def test_register_invalid_password_1(url):
    ''' Testing the process of registering with an invalid password
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in = {
        'email' : 'test-email@gmailcom',
        'password' : 'abc',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    r = requests.post(f"{url}/auth/register", json = data_in)
    assert r.status_code == InputError.code

def test_register_invalid_password_2(url):
    ''' Testing the process of registering with an invalid password
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in = {
        'email' : 'test-email@gmailcom',
        'password' : 'H E L L o 3 9',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    r = requests.post(f"{url}/auth/register", json = data_in)
    assert r.status_code == InputError.code


def test_register_invalid_names_1(url):
    ''' Testing the process of registering with an invalid name
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in = {
        'email' : 'test-email@gmailcom',
        'password' : 'abcdefg',
        'name_first': 'Ch@is Ti1an',
        'name_last' : 'Ilagan',
    }
    r = requests.post(f"{url}/auth/register", json = data_in)
    assert r.status_code == InputError.code

def test_register_invalid_names_2(url):
    ''' Testing the process of registering with an invalid name
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in = {
        'email' : 'test-email@gmailcom',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'M@chA3 el',
    }
    r = requests.post(f"{url}/auth/register", json = data_in)
    assert r.status_code == InputError.code

def test_register_exists(url):
    ''' Testing that the same email cannot be registered more than once
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in_1 = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    data_in_2 = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    result_1 = requests.post(f"{url}/auth/register", json = data_in_1)
    assert result_1.status_code != InputError.code
    result_2 = requests.post(f"{url}/auth/register", json = data_in_2)
    assert result_2.status_code == InputError.code

def test_register_password_length(url):
    ''' Checks if a password is too long or too short
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in_1 = {
        'email' : 'testEmail@gmail.com',
        'password' : 'a'*4,
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    data_in_2 = {
        'email' : 'testEmail1@gmail.com',
        'password' : 'a'*201,
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    data_in_3 = {
        'email' : 'testEmail2@gmail.com',
        'password' : 'a'*128,
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    data_in_4 = {
        'email' : 'testEmail3@gmail.com',
        'password' : 'a'*6,
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    result_1 = requests.post(f"{url}/auth/register", json = data_in_1)
    result_2 = requests.post(f"{url}/auth/register", json = data_in_2)
    assert result_1.status_code == InputError.code
    assert result_2.status_code == InputError.code
    # valid passwords in length
    result_3 = requests.post(f"{url}/auth/register", json = data_in_3)
    result_4 = requests.post(f"{url}/auth/register", json = data_in_4)
    assert result_3.status_code != InputError.code
    assert result_4.status_code != InputError.code
    

def test_register_invalid_names(url):
    ''' Checks if inputted names are valid
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in_1 = {
        'email' : 'testEmail@gmail.com',
        'password' : 'a'*6,
        'name_first': '',
        'name_last' : 'Ilagan',
    }
    data_in_2 = {
        'email' : 'testEmail1@gmail.com',
        'password' : 'a'*6,
        'name_first': 'Christian',
        'name_last' : '',
    }
    data_in_3 = {
        'email' : 'testEmail2@gmail.com',
        'password' : 'a'*6,
        'name_first': '',
        'name_last' : '',
    }
    data_in_4 = {
        'email' : 'testEmail3@gmail.com',
        'password' : 'a'*6,
        'name_first': 'c'*51,
        'name_last' : 'Ilagan',
    }
    data_in_5 = {
        'email' : 'testEmail4@gmail.com',
        'password' : 'a'*6,
        'name_first': 'Christian',
        'name_last' : 'c'*51,
    }
    data_in_6 = {
        'email' : 'testEmail5@gmail.com',
        'password' : 'a'*6,
        'name_first': 'C'*51,
        'name_last' : 'c'*51,
    }
    result_1 = requests.post(f"{url}/auth/register", json = data_in_1)
    result_2 = requests.post(f"{url}/auth/register", json = data_in_2)
    result_3 = requests.post(f"{url}/auth/register", json = data_in_3)
    result_4 = requests.post(f"{url}/auth/register", json = data_in_4)
    result_5 = requests.post(f"{url}/auth/register", json = data_in_5)
    result_6 = requests.post(f"{url}/auth/register", json = data_in_6)
    assert result_1.status_code == InputError.code
    assert result_2.status_code == InputError.code
    assert result_3.status_code == InputError.code
    assert result_4.status_code == InputError.code
    assert result_5.status_code == InputError.code
    assert result_6.status_code == InputError.code


def test_register_email_length(url):
    ''' Checks if the length of the email is valid
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in_1 = {
        'email' : 'c'*321 + 'gmail.com',
        'password' : 'a'*6,
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    data_in_2 = {
        'email' : 'a@b',
        'password' : 'a'*6,
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    data_in_3 = {
        'email' : 'bcjksacbwaudabjksdasdbjk@gmail.com',
        'password' : 'a'*6,
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    result_1 = requests.post(f"{url}/auth/register", json = data_in_1)
    result_2 = requests.post(f"{url}/auth/register", json = data_in_2)
    result_3 = requests.post(f"{url}/auth/register", json = data_in_3)
    assert result_1.status_code == InputError.code
    assert result_2.status_code == InputError.code
    assert result_3.status_code != InputError.code
    
    # with pytest.raises(InputError):
    #     requests.post(f"{url}/auth/register", json = data_in_1)
    # with pytest.raises(InputError):
    #     requests.post(f"{url}/auth/register", json = data_in_2)
    # requests.post(f"{url}/auth/register", json = data_in_3)

def test_case_sensitive_email(url):
    ''' Emails are not case sensitive, so capitalisation in inputs should not matter
    '''
    requests.delete(f"{url}/clear")
    clear()
    data_in_1 = {
        'email' : 'testEmail@gmail.com',
        'password' : 'a'*6,
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    data_in_2 = {
        'email' : 'tEStEmAiL@gmAil.Com',
        'password' : 'a'*6,
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    result_1 = requests.post(f"{url}/auth/register", json = data_in_1)
    assert result_1.status_code != InputError.code
    result_2 = requests.post(f"{url}/auth/register", json = data_in_2)
    assert result_2.status_code == InputError.code
    

#?------------------------------ Output Testing ------------------------------?#

def test_register_basic(url):
    ''' Testing the basic process of registering.
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'Christian',
        'name_last' : 'Ilagan',
    }
    result = requests.post(f"{url}/auth/register", json = data_in)
    payload = result.json()
    # testing against non flask implementation
    result_auth = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    assert payload['u_id'] == result_auth['u_id']
    assert payload['token'] == result_auth['token']

def test_register_multiple(url):
    ''' Testing the process of multiple users registering.
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in_1 = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    data_in_2 = {
        'email' : 'testEmail1@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    data_in_3 = {
        'email' : 'testEmail2@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    result_1 = requests.post(f"{url}/auth/register", json = data_in_1)
    payload_1 = result_1.json()
    result_auth_1 = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'John', 'Smith')
    assert payload_1['u_id'] == result_auth_1['u_id']
    assert payload_1['token'] == result_auth_1['token']
    result_2 = requests.post(f"{url}/auth/register", json = data_in_2)
    payload_2 = result_2.json()
    result_auth_2 = auth.auth_register('testEmail1@gmail.com', 'abcdefg', 'John', 'Smith')
    assert payload_2['u_id'] == result_auth_2['u_id']
    assert payload_2['token'] == result_auth_2['token']
    result_3 = requests.post(f"{url}/auth/register", json = data_in_3)
    payload_3 = result_3.json()
    result_auth_3 = auth.auth_register('testEmail2@gmail.com', 'abcdefg', 'John', 'Smith')
    assert payload_3['u_id'] == result_auth_3['u_id']
    assert payload_3['token'] == result_auth_3['token']

def test_register_unique_id(url):
    ''' Testing that each user recieves a unique id
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in_1 = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    data_in_2 = {
        'email' : 'testEmail1@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    data_in_3 = {
        'email' : 'testEmail2@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    result_1 = requests.post(f"{url}/auth/register", json = data_in_1)
    payload_1 = result_1.json()
    result_2 = requests.post(f"{url}/auth/register", json = data_in_2)
    payload_2 = result_2.json()
    result_3 = requests.post(f"{url}/auth/register", json = data_in_3)
    payload_3 = result_3.json()
    assert payload_1['u_id'] is not payload_2['u_id']
    assert payload_2['u_id'] is not payload_3['u_id']
    assert payload_3['u_id'] is not payload_1['u_id']

def test_register_unique_token(url):
    ''' Testing that each user recieves a unique token
    '''
    requests.delete(f"{url}/clear")
    clear()
    # initialising data
    data_in_1 = {
        'email' : 'testEmail@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    data_in_2 = {
        'email' : 'testEmail1@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    data_in_3 = {
        'email' : 'testEmail2@gmail.com',
        'password' : 'abcdefg',
        'name_first': 'John',
        'name_last' : 'Smith',
    }
    result_1 = requests.post(f"{url}/auth/register", json = data_in_1)
    payload_1 = result_1.json()
    result_2 = requests.post(f"{url}/auth/register", json = data_in_2)
    payload_2 = result_2.json()
    result_3 = requests.post(f"{url}/auth/register", json = data_in_3)
    payload_3 = result_3.json()
    assert payload_1['token'] is not payload_2['token']
    assert payload_2['token'] is not payload_3['token']
    assert payload_3['token'] is not payload_1['token']
