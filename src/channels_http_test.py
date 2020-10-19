import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
from other import clear

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
    result_reg = requests.post(f"{url}/auth/register", json = data_register)
    payload_reg = result_reg.json()
    requests.post(f"{url}/auth/logout", json = {'token': payload_reg['token']})

    data_input = {
        'token': payload_reg['token'],
        'name': 'Channel_1',
        'is_public': True,
    }
    new_channel = requests.post(f"{url}/channels/create", json = data_input)
    payload_create = new_channel.json()

    assert 'channel_id' in payload_create['channel_id']

def test_invalid_user(url):
    """Test for an invalid user creating a channel.
    """
    pass

def test_0_char_name(url):
    """Test for 0 character channel name.
    """
    requests.delete(f"{url}/clear")
    clear()
    pass

def test_1_char_name(url):
    """Test for 1 character channel name.
    """
    requests.delete(f"{url}/clear")
    clear()
    pass

def test_20_char_name(url):
    """Test for 20 character channel name.
    """
    requests.delete(f"{url}/clear")
    clear()
    pass

def test_21_char_name(url):
    """Test for 21 character channel name.
    """
    requests.delete(f"{url}/clear")
    clear()
    pass

#?------------------------------ Output Testing ------------------------------?#

def test_unique_id(url):
    pass
    

#------------------------------------------------------------------------------#
#                                channels/list                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#


#------------------------------------------------------------------------------#
#                               channels/listall                               #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#


