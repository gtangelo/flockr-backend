"""
message feature test implementation to test functions in message.py

2020 T3 COMP1531 Major Project
"""
import requests

from src.classes.error import InputError, AccessError
from src.helpers.helpers_http_test import (
    request_channel_invite, 
    request_channel_messages, 
    request_channel_leave, 
    request_message_send, 
    request_message_react,
    request_message_unreact,
)
from src.globals import THUMBS_UP, THUMBS_DOWN

#------------------------------------------------------------------------------#
#                                 message/react                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_react_input_message_id_1(url, user_1, public_channel_1):
    """Testing invalid message_id when a channel has no messages
    """
    data_1 = {
        'token': user_1['token'],
        'message_id': 1,
        'react_id': THUMBS_UP,
    }
    data_2 = {
        'token': user_1['token'],
        'message_id': 2,
        'react_id': THUMBS_UP,
    }
    data_3 = {
        'token': user_1['token'],
        'message_id': 0,
        'react_id': THUMBS_UP,
    }
    result_1 = requests.post(f"{url}/message/react", json=data_1)
    result_2 = requests.post(f"{url}/message/react", json=data_2)
    result_3 = requests.post(f"{url}/message/react", json=data_3)
    assert result_1.status_code == InputError.code
    assert result_2.status_code == InputError.code
    assert result_3.status_code == InputError.code


def test_react_input_message_id_2(url, user_1, public_channel_1, default_message):
    """Testing invalid message_id when a channel has a message
    """
    data_1 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'] + 1,
        'react_id': THUMBS_UP,
    }
    data_2 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'] - 1,
        'react_id': THUMBS_UP,
    }
    result_1 = requests.post(f"{url}/message/react", json=data_1)
    result_2 = requests.post(f"{url}/message/react", json=data_2)
    assert result_1.status_code == InputError.code
    assert result_2.status_code == InputError.code

def test_react_input_react_id(url, user_1, public_channel_1, default_message):
    """Test when the react_id is invalid
    """
    data_1 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'react_id': 0,
    }
    data_2 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'react_id': -1,
    }
    data_3 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'react_id': -1,
    }
    data_4 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'react_id': 1000,
    }
    result_1 = requests.post(f"{url}/message/react", json=data_1)
    result_2 = requests.post(f"{url}/message/react", json=data_2)
    result_3 = requests.post(f"{url}/message/react", json=data_3)
    result_4 = requests.post(f"{url}/message/react", json=data_4)
    assert result_1.status_code == InputError.code
    assert result_2.status_code == InputError.code
    assert result_3.status_code == InputError.code
    assert result_4.status_code == InputError.code

def test_react_input_reacted_message_thumbs_up(url, user_1, public_channel_1, thumbs_up_default_message):
    """Test if the message with message_id already contains an active React with
    react_id from the authorised user (thumbs up)
    """
    data_1 = {
        'token': user_1['token'],
        'message_id': thumbs_up_default_message['message_id'],
        'react_id': THUMBS_UP,
    }
    result_1 = requests.post(f"{url}/message/react", json=data_1)
    assert result_1.status_code == InputError.code

def test_react_input_reacted_message_thumbs_down(url, user_1, public_channel_1, thumbs_down_default_message):
    """Test if the message with message_id already contains an active React with
    react_id from the authorised user (thumbs down)
    """
    data_1 = {
        'token': user_1['token'],
        'message_id': thumbs_down_default_message['message_id'],
        'react_id': THUMBS_DOWN,
    }
    result_1 = requests.post(f"{url}/message/react", json=data_1)
    assert result_1.status_code == InputError.code

def test_react_access_invalid_token(url, user_1, public_channel_1, default_message, logout_user_1):
    """Test if token is invalid
    """
    data_1 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'react_id': THUMBS_UP,
    }
    data_2 = {
        'token': user_1['token'],
        'message_id': default_message['message_id'],
        'react_id': THUMBS_DOWN,
    }
    result_1 = requests.post(f"{url}/message/react", json=data_1)
    result_2 = requests.post(f"{url}/message/react", json=data_2)
    assert result_1.status_code == InputError.code
    assert result_2.status_code == InputError.code

def test_react_access_user_not_in_channel(url, user_1, user_2, public_channel_1, default_message):
    """(Assumption testing): testing when a flockr member not in the channel 
    calling message_react will raise an AccessError.
    """
    result_1 = request_message_react(url, user_2['token'], default_message['message_id'], THUMBS_UP)
    result_2 = request_message_react(url, user_2['token'], default_message['message_id'], THUMBS_DOWN)
    assert result_1.status_code == AccessError.code
    assert result_2.status_code == AccessError.code
    
#?------------------------------ Output Testing ------------------------------?#

def test_react_output_basic_react_thumbs_up(url, user_1, public_channel_1, thumbs_up_default_message):
    """Basic test whether a message has indeed been reacted by the user who created
    the message (thumbs up).
    """
    data_1 = {
        'token': user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }
    channel_details = requests.get(f"{url}/channel/messages", params = data_1).json()
    message_details = channel_details['messages'][0]
    assert message_details['reacts'][0]['react_id'] == THUMBS_UP
    assert message_details['reacts'][0]['u_ids'] == [user_1['u_id']]
    assert message_details['reacts'][0]['is_this_user_reacted'] == True
    assert message_details['reacts'][1]['u_ids'] == []
    

def test_react_output_basic_react_thumbs_down(url, user_1, public_channel_1, thumbs_down_default_message):
    """Basic test whether a message has indeed been reacted by the user who created
    the message (thumbs down).
    """
    data_1 = {
        'token': user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }
    channel_details = requests.get(f"{url}/channel/messages", params = data_1).json()
    message_details = channel_details['messages'][0]
    assert message_details['reacts'][1]['react_id'] == THUMBS_DOWN
    assert message_details['reacts'][1]['u_ids'] == [user_1['u_id']]
    assert message_details['reacts'][1]['is_this_user_reacted'] == True
    assert message_details['reacts'][0]['u_ids'] == []
    

def test_react_output_another_user_thumbs_up(url, user_1, user_2, public_channel_1, default_message):
    """Test if another user can react a message created by another user (thumbs up).
    """
    request_channel_invite(url, user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    request_message_react(url, user_2['token'], default_message['message_id'], THUMBS_UP)
    channel_details = request_channel_messages(url, user_2['token'], public_channel_1['channel_id'], 0).json()
    message_details = channel_details['messages'][0]
    assert message_details['reacts'][0]['react_id'] == THUMBS_UP
    assert message_details['reacts'][0]['u_ids'] == [user_2['u_id']]
    assert message_details['reacts'][0]['is_this_user_reacted'] == True
    assert message_details['reacts'][1]['u_ids'] == []

def test_react_output_another_user_thumbs_down(url, user_1, user_2, public_channel_1, default_message):
    """Test if another user can react a message created by another user (thumbs down).
    """
    request_channel_invite(url, user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    request_message_react(url, user_2['token'], default_message['message_id'], THUMBS_DOWN)
    channel_details = request_channel_messages(url, user_2['token'], public_channel_1['channel_id'], 0).json()
    message_details = channel_details['messages'][0]
    assert message_details['reacts'][1]['react_id'] == THUMBS_DOWN
    assert message_details['reacts'][1]['u_ids'] == [user_2['u_id']]
    assert message_details['reacts'][1]['is_this_user_reacted'] == True
    assert message_details['reacts'][0]['u_ids'] == []
    
def test_react_output_is_this_user_reacted_false_thumbs_up(url, user_1, user_2, public_channel_1, default_message):
    """Test is_this_user_reacted field is false for another user that has not
    reacted to a message that has been reacted by another user (thumbs up).
    """
    request_channel_invite(url, user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    request_message_react(url, user_2['token'], default_message['message_id'], THUMBS_UP)
    channel_details = request_channel_messages(url, user_1['token'], public_channel_1['channel_id'], 0).json()
    message_details = channel_details['messages'][0]
    assert message_details['reacts'][0]['react_id'] == THUMBS_UP
    assert message_details['reacts'][0]['u_ids'] == [user_2['u_id']]
    assert message_details['reacts'][0]['is_this_user_reacted'] == False
    assert message_details['reacts'][1]['u_ids'] == []

def test_react_output_is_this_user_reacted_false_thumbs_down(url, user_1, user_2, public_channel_1, default_message):
    """Test is_this_user_reacted field is false for another user that has not
    reacted to a message that has been reacted by another user (thumbs down).
    """
    request_channel_invite(url, user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    request_message_react(url, user_2['token'], default_message['message_id'], THUMBS_DOWN)
    channel_details = request_channel_messages(url, user_1['token'], public_channel_1['channel_id'], 0).json()
    message_details = channel_details['messages'][0]
    assert message_details['reacts'][1]['react_id'] == THUMBS_DOWN
    assert message_details['reacts'][1]['u_ids'] == [user_2['u_id']]
    assert message_details['reacts'][1]['is_this_user_reacted'] == False
    assert message_details['reacts'][0]['u_ids'] == []

def test_react_output_two_reacts(url, user_1, public_channel_1, default_message):
    """(Assumption testing): Test when if a user switches reacts (i.e. react 
    with thumbs up then react to thumbs down), this behavior should not raise any
    errors. However, only the thumbs down react should only be active due to the
    assumption.
    """
    request_message_react(url, user_1['token'], default_message['message_id'], THUMBS_UP)
    channel_details = request_channel_messages(url, user_1['token'], public_channel_1['channel_id'], 0).json()
    message_details = channel_details['messages'][0]
    assert message_details['reacts'][0]['react_id'] == THUMBS_UP
    assert message_details['reacts'][0]['u_ids'] == [user_1['u_id']]
    assert message_details['reacts'][0]['is_this_user_reacted'] == True

    assert message_details['reacts'][1]['u_ids'] == []
    assert message_details['reacts'][1]['is_this_user_reacted'] == False

    request_message_react(url, user_1['token'], default_message['message_id'], THUMBS_DOWN)
    channel_details = request_channel_messages(url, user_1['token'], public_channel_1['channel_id'], 0).json()
    message_details = channel_details['messages'][0]
    assert message_details['reacts'][1]['react_id'] == THUMBS_DOWN
    assert message_details['reacts'][1]['u_ids'] == [user_1['u_id']]
    assert message_details['reacts'][1]['is_this_user_reacted'] == True

    assert message_details['reacts'][0]['u_ids'] == []
    assert message_details['reacts'][0]['is_this_user_reacted'] == False

def test_react_output_unreact_two_react(url, user_1, public_channel_1, default_message):
    """Test when a user reacts a message, then unreacts, then reacts the same
    message with a different react_id
    """
    request_message_react(url, user_1['token'], default_message['message_id'], THUMBS_UP)
    channel_details = request_channel_messages(url, user_1['token'], public_channel_1['channel_id'], 0).json()
    message_details = channel_details['messages'][0]
    assert message_details['reacts'][0]['react_id'] == THUMBS_UP
    assert message_details['reacts'][0]['u_ids'] == [user_1['u_id']]
    assert message_details['reacts'][0]['is_this_user_reacted'] == True

    assert message_details['reacts'][1]['u_ids'] == []
    assert message_details['reacts'][1]['is_this_user_reacted'] == False

    request_message_unreact(url, user_1['token'], default_message['message_id'], THUMBS_UP)
    channel_details = request_channel_messages(url, user_1['token'], public_channel_1['channel_id'], 0).json()
    message_details = channel_details['messages'][0]
    assert message_details['reacts'][0]['react_id'] == THUMBS_UP
    assert message_details['reacts'][0]['u_ids'] == []
    assert message_details['reacts'][0]['is_this_user_reacted'] == False

    assert message_details['reacts'][1]['u_ids'] == []
    assert message_details['reacts'][1]['is_this_user_reacted'] == False

    request_message_react(url, user_1['token'], default_message['message_id'], THUMBS_DOWN)
    channel_details = request_channel_messages(url, user_1['token'], public_channel_1['channel_id'], 0).json()
    message_details = channel_details['messages'][0]
    assert message_details['reacts'][1]['react_id'] == THUMBS_DOWN
    assert message_details['reacts'][1]['u_ids'] == [user_1['u_id']]
    assert message_details['reacts'][1]['is_this_user_reacted'] == True

    assert message_details['reacts'][0]['u_ids'] == []
    assert message_details['reacts'][0]['is_this_user_reacted'] == False

    request_message_unreact(url, user_1['token'], default_message['message_id'], THUMBS_DOWN)
    channel_details = request_channel_messages(url, user_1['token'], public_channel_1['channel_id'], 0).json()
    message_details = channel_details['messages'][0]
    assert message_details['reacts'][0]['react_id'] == THUMBS_UP
    assert message_details['reacts'][0]['u_ids'] == []
    assert message_details['reacts'][0]['is_this_user_reacted'] == False

    assert message_details['reacts'][1]['u_ids'] == []
    assert message_details['reacts'][1]['is_this_user_reacted'] == False

def test_react_output_user_leaves_state_thumbs_up(url, user_1, user_2, public_channel_1, thumbs_up_default_message):
    """(Assumption testing): Test when a user leaves that all the messages that
    they reacted previously persist in the channel details. (thumbs up)
    """
    request_channel_invite(url, user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    request_channel_leave(url, user_1['token'], public_channel_1['channel_id'])
    channel_details = request_channel_messages(url, user_2['token'], public_channel_1['channel_id'], 0).json()
    message_details = channel_details['messages'][0]
    assert message_details['reacts'][0]['react_id'] == THUMBS_UP
    assert message_details['reacts'][0]['u_ids'] == [user_1['u_id']]
    assert message_details['reacts'][0]['is_this_user_reacted'] == False

    assert message_details['reacts'][1]['u_ids'] == []
    assert message_details['reacts'][1]['is_this_user_reacted'] == False

def test_react_output_user_leaves_state_thumbs_down(url, user_1, user_2, public_channel_1, thumbs_down_default_message):
    """(Assumption testigng): Test when a user leaves that all the messages that
    they reacted previously persist in the channel details. (thumbs down)
    """
    request_channel_invite(url, user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    request_channel_leave(url, user_1['token'], public_channel_1['channel_id'])
    channel_details = request_channel_messages(url, user_2['token'], public_channel_1['channel_id'], 0).json()
    message_details = channel_details['messages'][0]
    assert message_details['reacts'][0]['react_id'] == THUMBS_UP
    assert message_details['reacts'][0]['u_ids'] == []
    assert message_details['reacts'][0]['is_this_user_reacted'] == False

    assert message_details['reacts'][1]['u_ids'] == [user_1['u_id']]
    assert message_details['reacts'][1]['is_this_user_reacted'] == False

def test_react_output_multiple_users_react(url, user_1, user_2, user_3, user_4, public_channel_1, default_message):
    """Testing process where multiple users likes and dislike a message
    """
    request_channel_invite(url, user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    request_channel_invite(url, user_1['token'], public_channel_1['channel_id'], user_3['u_id'])
    request_channel_invite(url, user_1['token'], public_channel_1['channel_id'], user_4['u_id'])

    request_message_react(url, user_1['token'], default_message['message_id'], THUMBS_UP)
    request_message_react(url, user_2['token'], default_message['message_id'], THUMBS_UP)
    request_message_react(url, user_3['token'], default_message['message_id'], THUMBS_DOWN)
    request_message_react(url, user_4['token'], default_message['message_id'], THUMBS_UP)

    channel_details = request_channel_messages(url, user_1['token'], public_channel_1['channel_id'], 0).json()
    message_details = channel_details['messages'][0]
    assert message_details['reacts'][0]['react_id'] == THUMBS_UP
    assert sorted(message_details['reacts'][0]['u_ids']) == sorted([user_1['u_id'], user_2['u_id'], user_4['u_id']])
    assert message_details['reacts'][0]['is_this_user_reacted'] == True

    assert message_details['reacts'][1]['react_id'] == THUMBS_DOWN
    assert sorted(message_details['reacts'][1]['u_ids']) == [user_3['u_id']]
    assert message_details['reacts'][1]['is_this_user_reacted'] == False

#------------------------------------------------------------------------------#
#                                message/unreact                               #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_authorised_to_unreact(url, user_1, public_channel_1):
    """
    Test for logged out user trying to unreact to a message.
    """
    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hello").json()
    request_message_react(url, user_1['token'], msg_1['message_id'], THUMBS_UP)

    requests.post(f"{url}/auth/logout", json={
        'token': user_1['token']
    })

    ret_unreact = request_message_unreact(url, user_1['token'], msg_1['message_id'], THUMBS_UP)
    assert ret_unreact.status_code == AccessError.code
    
    requests.delete(url + '/clear')

def test_nonmember_unreact(url, user_2, user_3, public_channel_2):
    """
    Test for users outside of the channel that the message is in trying to unreact that message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_3['token'],
        'channel_id': public_channel_2['channel_id']
    })

    msg_1 = request_message_send(url, user_2['token'], public_channel_2['channel_id'], "Hello").json()
    request_message_react(url, user_3['token'], msg_1['message_id'], THUMBS_UP)

    requests.post(f"{url}/channel/leave", json={
        'token': user_3['token'],
        'channel_id': public_channel_2['channel_id']
    })

    ret_unreact = request_message_unreact(url, user_3['token'], msg_1['message_id'], THUMBS_UP)
    assert ret_unreact.status_code == AccessError.code
    
    requests.delete(url + '/clear')

def test_valid_message_id_unreact(url, user_1, public_channel_1):
    """
    Test if the message exists or not.
    """
    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hello").json()
    request_message_react(url, user_1['token'], msg_1['message_id'], THUMBS_UP)

    ret_unreact_1 = request_message_unreact(url, user_1['token'], msg_1['message_id'] + 1, THUMBS_UP)
    assert ret_unreact_1.status_code == InputError.code
    ret_unreact_2 = request_message_unreact(url, user_1['token'], msg_1['message_id'] - 1, THUMBS_UP)
    assert ret_unreact_2.status_code == InputError.code
    ret_unreact_3 = request_message_unreact(url, user_1['token'], msg_1['message_id'] + 500, THUMBS_UP)
    assert ret_unreact_3.status_code == InputError.code

    requests.delete(url + '/clear')
    

def test_valid_react_id_unreact(url, user_1, public_channel_1):
    """
    Test if the specific react exists.
    """
    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hello").json()
    request_message_react(url, user_1['token'], msg_1['message_id'], THUMBS_UP)

    ret_unreact_1 = request_message_unreact(url, user_1['token'], msg_1['message_id'], 3)
    assert ret_unreact_1.status_code == InputError.code
    ret_unreact_2 = request_message_unreact(url, user_1['token'], msg_1['message_id'], -1)
    assert ret_unreact_2.status_code == InputError.code
    ret_unreact_3 = request_message_unreact(url, user_1['token'], msg_1['message_id'], -13)
    assert ret_unreact_3.status_code == InputError.code
    ret_unreact_4 = request_message_unreact(url, user_1['token'], msg_1['message_id'], 21)
    assert ret_unreact_4.status_code == InputError.code

    requests.delete(url + '/clear')

def test_message_already_unreacted(url, user_1, user_2, public_channel_1):
    """
    Test for unreacting to a message that is already unreacted to.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hello").json()
    msg_2 = request_message_send(url, user_2['token'], public_channel_1['channel_id'], "Hola").json()
    request_message_react(url, user_2['token'], msg_2['message_id'], THUMBS_UP)

    ret_unreact_1 = request_message_unreact(url, user_2['token'], msg_1['message_id'], THUMBS_UP)
    assert ret_unreact_1.status_code == InputError.code
    ret_unreact_2 = request_message_unreact(url, user_2['token'], msg_2['message_id'], THUMBS_DOWN)
    assert ret_unreact_2.status_code == InputError.code

    requests.delete(url + '/clear')

#?------------------------------ Output Testing ------------------------------?#

def test_unreact_correct_message_thumbsup(url, user_1, user_2, public_channel_1):
    """
    Basic test for unreacting a react_id in a message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hello").json()
    msg_2 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hola").json()
    msg_3 = request_message_send(url, user_2['token'], public_channel_1['channel_id'], "Mate").json()
    request_message_send(url, user_2['token'], public_channel_1['channel_id'], "What?!").json()

    request_message_react(url, user_1['token'], msg_2['message_id'], THUMBS_UP)
    request_message_react(url, user_1['token'], msg_3['message_id'], THUMBS_UP)
    request_message_react(url, user_2['token'], msg_3['message_id'], THUMBS_UP)

    request_message_unreact(url, user_1['token'], msg_3['message_id'], THUMBS_UP)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    count_msg_unreacted_1 = 0
    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] == THUMBS_UP:
                if user_1['u_id'] not in react['u_ids'] and (curr_message['message'] in [
                    'Hello', 'Mate', 'What?!'
                ]):
                    count_msg_unreacted_1 += 1
    assert count_msg_unreacted_1 == 3
    
    requests.delete(url + '/clear')

def test_unreact_correct_message_thumbsdown(url, user_1, user_2, public_channel_1):
    """
    Basic test for unreacting a react_id in a message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hola").json()
    msg_2 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Mate").json()

    request_message_react(url, user_2['token'], msg_1['message_id'], THUMBS_DOWN)
    request_message_react(url, user_2['token'], msg_2['message_id'], THUMBS_DOWN)

    request_message_unreact(url, user_2['token'], msg_2['message_id'], THUMBS_DOWN)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    count_msg_unreacted_1 = 0
    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] == THUMBS_DOWN:
                if user_2['u_id'] not in react['u_ids'] and (curr_message['message'] == 'Mate'):
                    count_msg_unreacted_1 += 1
    assert count_msg_unreacted_1 == 1

    requests.delete(url + '/clear')

def test_unreact_owned_messages(url, user_1, user_2, public_channel_1):
    """
    Test for unreacting owned messages.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hola").json()
    msg_2 = request_message_send(url, user_2['token'], public_channel_1['channel_id'], "Mate").json()
    msg_3 = request_message_send(url, user_2['token'], public_channel_1['channel_id'], "Hi").json()
    msg_4 = request_message_send(url, user_2['token'], public_channel_1['channel_id'], "What?").json()

    request_message_react(url, user_2['token'], msg_2['message_id'], THUMBS_UP)
    request_message_react(url, user_2['token'], msg_3['message_id'], THUMBS_UP)
    request_message_react(url, user_2['token'], msg_4['message_id'], THUMBS_UP)
    request_message_react(url, user_1['token'], msg_1['message_id'], THUMBS_UP)

    request_message_unreact(url, user_2['token'], msg_2['message_id'], THUMBS_UP)
    request_message_unreact(url, user_2['token'], msg_3['message_id'], THUMBS_UP)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    count_msg_unreacted_1 = 0
    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] == THUMBS_UP:
                if user_2['u_id'] not in react['u_ids'] and (curr_message['message'] in [
                    'Hola', 'Hi', 'Mate'
                    ]):
                    count_msg_unreacted_1 += 1
    assert count_msg_unreacted_1 == 3

    requests.delete(url + '/clear')

def test_unreact_other_messages(url, user_1, user_2, user_3, public_channel_3):
    """
    Test for unreacting other user's messages.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_1['token'],
        'channel_id': public_channel_3['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_3['channel_id']
    })

    msg_1 = request_message_send(url, user_1['token'], public_channel_3['channel_id'], "Hola").json()
    msg_2 = request_message_send(url, user_1['token'], public_channel_3['channel_id'], "Mate").json()
    msg_3 = request_message_send(url, user_2['token'], public_channel_3['channel_id'], "Hi").json()
    request_message_send(url, user_2['token'], public_channel_3['channel_id'], "What?").json()
    msg_5 = request_message_send(url, user_2['token'], public_channel_3['channel_id'], "OKAY").json()

    request_message_react(url, user_3['token'], msg_1['message_id'], THUMBS_UP)
    request_message_react(url, user_3['token'], msg_2['message_id'], THUMBS_UP)
    request_message_react(url, user_3['token'], msg_3['message_id'], THUMBS_UP)
    request_message_react(url, user_3['token'], msg_5['message_id'], THUMBS_UP)

    request_message_unreact(url, user_3['token'], msg_2['message_id'], THUMBS_UP)
    request_message_unreact(url, user_3['token'], msg_3['message_id'], THUMBS_UP)
    request_message_unreact(url, user_3['token'], msg_5['message_id'], THUMBS_UP)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_3['channel_id'],
        'start': 0,
    }).json()

    count_msg_unreacted_1 = 0
    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] == THUMBS_UP:
                if user_3['u_id'] not in react['u_ids'] and (curr_message['message'] in [
                    'Hi', 'Mate', 'What?', 'OKAY'
                    ]):
                    count_msg_unreacted_1 += 1
    assert count_msg_unreacted_1 == 4

    requests.delete(url + '/clear')

def test_unreact_multiple_messages(url, user_1, user_2, user_3, public_channel_2):
    """
    Test for unreacting multiple messages.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_1['token'],
        'channel_id': public_channel_2['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_3['token'],
        'channel_id': public_channel_2['channel_id']
    })

    msg_1 = request_message_send(url, user_1['token'], public_channel_2['channel_id'], "Hola").json()
    msg_2 = request_message_send(url, user_1['token'], public_channel_2['channel_id'], "Mate").json()
    request_message_send(url, user_1['token'], public_channel_2['channel_id'], "Hi").json()
    msg_4 = request_message_send(url, user_1['token'], public_channel_2['channel_id'], "What?").json()
    msg_5 = request_message_send(url, user_2['token'], public_channel_2['channel_id'], "OKAY").json()
    msg_6 = request_message_send(url, user_2['token'], public_channel_2['channel_id'], "I").json()
    msg_7 = request_message_send(url, user_2['token'], public_channel_2['channel_id'], "Am").json()
    msg_8 = request_message_send(url, user_2['token'], public_channel_2['channel_id'], "Good").json()

    request_message_react(url, user_3['token'], msg_1['message_id'], THUMBS_UP)
    request_message_react(url, user_3['token'], msg_2['message_id'], THUMBS_UP)
    request_message_react(url, user_3['token'], msg_4['message_id'], THUMBS_UP)
    request_message_react(url, user_3['token'], msg_5['message_id'], THUMBS_UP)
    request_message_react(url, user_3['token'], msg_6['message_id'], THUMBS_UP)
    request_message_react(url, user_3['token'], msg_7['message_id'], THUMBS_DOWN)
    request_message_react(url, user_3['token'], msg_8['message_id'], THUMBS_DOWN)

    request_message_unreact(url, user_3['token'], msg_1['message_id'], THUMBS_UP)
    request_message_unreact(url, user_3['token'], msg_4['message_id'], THUMBS_UP)
    request_message_unreact(url, user_3['token'], msg_5['message_id'], THUMBS_UP)
    request_message_unreact(url, user_3['token'], msg_6['message_id'], THUMBS_UP)
    request_message_unreact(url, user_3['token'], msg_8['message_id'], THUMBS_DOWN)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_2['channel_id'],
        'start': 0,
    }).json()

    count_msg_unreacted_1 = 0
    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] in (THUMBS_UP, THUMBS_DOWN):
                if user_3['u_id'] not in react['u_ids']:
                    count_msg_unreacted_1 += 1
    # Each message has 2 react options, and there should be a total of 13 non-active reacts for user_3.
    assert count_msg_unreacted_1 == 14
    
    requests.delete(url + '/clear')

def test_unreact_same_react_from_different_users(url, user_1, user_2, user_3, public_channel_1):
    """
    Test for unreacting the same react from a message from multiple users (thumbs down).
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_3['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hola").json()

    request_message_react(url, user_1['token'], msg_1['message_id'], THUMBS_DOWN)
    request_message_react(url, user_2['token'], msg_1['message_id'], THUMBS_DOWN)
    request_message_react(url, user_3['token'], msg_1['message_id'], THUMBS_DOWN)

    request_message_unreact(url, user_1['token'], msg_1['message_id'], THUMBS_DOWN)
    request_message_unreact(url, user_2['token'], msg_1['message_id'], THUMBS_DOWN)
    request_message_unreact(url, user_3['token'], msg_1['message_id'], THUMBS_DOWN)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] == THUMBS_DOWN:
                assert user_1['u_id'] not in react['u_ids']
                assert user_2['u_id'] not in react['u_ids']
                assert user_3['u_id'] not in react['u_ids']

    requests.delete(url + '/clear')

def test_unreact_latest_reacts_from_message(url, user_1, user_2, user_3, public_channel_1):
    """
    Test for unreacting latest react from the same message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_3['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hola").json()

    request_message_react(url, user_1['token'], msg_1['message_id'], THUMBS_UP)
    request_message_react(url, user_1['token'], msg_1['message_id'], THUMBS_DOWN)
    request_message_react(url, user_2['token'], msg_1['message_id'], THUMBS_UP)
    request_message_react(url, user_2['token'], msg_1['message_id'], THUMBS_DOWN)
    request_message_react(url, user_3['token'], msg_1['message_id'], THUMBS_DOWN)
    request_message_react(url, user_3['token'], msg_1['message_id'], THUMBS_UP)

    request_message_unreact(url, user_2['token'], msg_1['message_id'], THUMBS_DOWN)
    request_message_unreact(url, user_3['token'], msg_1['message_id'], THUMBS_UP)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] == THUMBS_UP:
                assert user_1['u_id'] not in react['u_ids']
                assert user_2['u_id'] not in react['u_ids']
                assert user_3['u_id'] not in react['u_ids']
            elif react['react_id'] == THUMBS_DOWN:
                assert user_1['u_id'] in react['u_ids']
                assert user_2['u_id'] not in react['u_ids']
                assert user_3['u_id'] not in react['u_ids']

    requests.delete(url + '/clear')

def test_flockr_owner_unreact_messages(url, user_1, user_2, public_channel_2):
    """
    (Assumption Test) Test for a flockr owner unreacting a react_id in a message from 
    outside the channel.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_1['token'],
        'channel_id': public_channel_2['channel_id']
    })

    msg_1 = request_message_send(url, user_1['token'], public_channel_2['channel_id'], "Hola").json()

    request_message_react(url, user_1, msg_1['message_id'], THUMBS_DOWN)

    requests.post(f"{url}/channel/leave", json={
        'token': user_1['token'],
        'channel_id': public_channel_2['channel_id']
    })

    request_message_unreact(url, user_1, msg_1['message_id'], THUMBS_DOWN)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_2['channel_id'],
        'start': 0,
    }).json()

    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] == THUMBS_UP:
                assert user_1['u_id'] not in react['u_ids']
            elif react['react_id'] == THUMBS_DOWN:
                assert user_1['u_id'] not in react['u_ids']

    requests.delete(url + '/clear')

def test_unreact_in_private_channel(url, user_1, user_2, user_3, private_channel_2):
    """
    Test for unreacting in a private channel.
    """
    requests.post(f"{url}/channel/invite", json={
        'token': user_2['token'],
        'channel_id': private_channel_2['channel_id'],
        'u_id': user_3['u_id'],
    })

    msg_1 = request_message_send(url, user_2['token'], private_channel_2['channel_id'], "Be right back").json()

    request_message_react(url, user_3['token'], msg_1['message_id'], THUMBS_UP)
    request_message_react(url, user_3['token'], msg_1['message_id'], THUMBS_DOWN)

    request_message_unreact(url, user_3['token'], msg_1['message_id'], THUMBS_DOWN)

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': private_channel_2['channel_id'],
        'start': 0,
    }).json()

    for curr_message in message_list['messages']:
        for react in curr_message['reacts']:
            if react['react_id'] == THUMBS_UP:
                assert user_3['u_id'] not in react['u_ids']
            elif react['react_id'] == THUMBS_DOWN:
                assert user_3['u_id'] not in react['u_ids']

    requests.delete(url + '/clear')
