"""
message feature test implementation to test functions in message.py

2020 T3 COMP1531 Major Project
"""
import requests

from src.classes.error import InputError, AccessError
from src.helpers.helpers_http_test import (
    request_message_send, 
    request_message_pin, 
    request_message_unpin,
)

#------------------------------------------------------------------------------#
#                                  message/pin                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_valid_message_id(url, user_1, default_message, public_channel_1):
    """
    Test whether the message_id is a valid id.
    """
    ret_pinned = request_message_pin(url, user_1['token'], default_message['message_id'] + 1)
    assert ret_pinned.status_code == InputError.code

    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hello World!").json()

    ret_pinned_1 = request_message_pin(url, user_1['token'], msg_1['message_id'] - 2)
    assert ret_pinned_1.status_code == InputError.code

    msg_2 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Now Way!?").json()

    ret_pinned_2 = request_message_pin(url, user_1['token'], msg_2['message_id'] + 100)
    assert ret_pinned_2.status_code == InputError.code

    requests.delete(url + '/clear')

def test_already_pinned(url, user_1, user_2, public_channel_1):
    """
    Test for pinning an already pinned message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_1['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hello World!").json()
    request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Now Way!?").json()

    request_message_pin(url, user_1['token'], msg_1['message_id'])
    ret_pinned = request_message_pin(url, user_1['token'], msg_1['message_id'])
    assert ret_pinned.status_code == InputError.code

    requests.delete(url + '/clear')
    
def test_user_is_member_of_channel_with_message(url, user_1, user_2, user_3, user_4, public_channel_2):
    """
    Test for user pinning a message in a channel that they are not a member of.
    """
    msg_1 = request_message_send(url, user_2['token'], public_channel_2['channel_id'], "I am amazing!").json()

    ret_pinned_1 = request_message_pin(url, user_3['token'], msg_1['message_id'])
    ret_pinned_2 = request_message_pin(url, user_4['token'], msg_1['message_id'])

    assert ret_pinned_1.status_code == AccessError.code
    assert ret_pinned_2.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_authorised_to_pin(url, user_1, default_message, logout_user_1):
    """
    Test for a logged out user trying to pin a message.
    """
    ret_pinned = request_message_pin(url, user_1['token'], default_message['message_id'])
    assert ret_pinned.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_non_owner_pin(url, user_1, user_2, public_channel_1):
    """
    Test for a user who is not an owner of the channel, pinning a message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hello World!").json()
    request_message_send(url, user_2['token'], public_channel_1['channel_id'], "Now Way!?").json()

    ret_pinned = request_message_pin(url, user_2['token'], msg_1['message_id'])
    assert ret_pinned.status_code == AccessError.code

    requests.delete(url + '/clear')


#?------------------------------ Output Testing ------------------------------?#

def test_pin_correct_message(url, user_1, user_2, public_channel_1):
    """
    Test for pinning the correct message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hello World!").json()
    msg_2 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hi").json()
    msg_3 = request_message_send(url, user_2['token'], public_channel_1['channel_id'], "What?!").json()
    request_message_send(url, user_2['token'], public_channel_1['channel_id'], "1521 Comp!").json()

    request_message_pin(url, user_1['token'], msg_2['message_id'])
    request_message_pin(url, user_1['token'], msg_3['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    count_msg_pinned = 0
    for curr_message in message_list['messages']:
        if curr_message['is_pinned'] and (curr_message['message'] in ['Hi', 'What?!']):
            count_msg_pinned += 1
        
    assert count_msg_pinned == 2

    requests.delete(url + '/clear')

def test_added_owner_can_pin(url, user_1, user_2, public_channel_1):
    """
    Test for pinning messages from a recently added owner.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hello World!").json()
    msg_2 = request_message_send(url, user_2['token'], public_channel_1['channel_id'], "Hi").json()

    requests.post(f"{url}/channel/addowner", json={
        'token': user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'u_id': user_2['u_id'],
    }).json()

    request_message_pin(url, user_2['token'], msg_2['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    for curr_message in message_list['messages']:
        if curr_message['message_id'] == msg_2['message_id']:
            assert curr_message['is_pinned']
    
    requests.delete(url + '/clear')

def test_pin_owned_message(url, user_1, public_channel_1):
    """
    Test for pinning the user's own messages.
    """
    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hello World!").json()
    request_message_pin(url, user_1['token'], msg_1['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    for curr_message in message_list['messages']:
        if curr_message['message_id'] == msg_1['message_id']:
            assert curr_message['is_pinned']

    requests.delete(url + '/clear')

def test_pin_other_messages(url, user_1, user_2, user_3, public_channel_2):
    """
    Test for pinning other user's messages.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_1['token'],
        'channel_id': public_channel_2['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_3['token'],
        'channel_id': public_channel_2['channel_id']
    })

    msg_1 = request_message_send(url, user_1['token'], public_channel_2['channel_id'], "Hello World!").json()
    msg_2 = request_message_send(url, user_1['token'], public_channel_2['channel_id'], "Hi").json()
    msg_3 = request_message_send(url, user_3['token'], public_channel_2['channel_id'], "What?!").json()
    msg_4 = request_message_send(url, user_3['token'], public_channel_2['channel_id'], "1521 Comp!").json()

    request_message_pin(url, user_2['token'], msg_1['message_id'])
    request_message_pin(url, user_2['token'], msg_2['message_id'])
    request_message_pin(url, user_2['token'], msg_3['message_id'])
    request_message_pin(url, user_2['token'], msg_4['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_1['token'],
        'channel_id': public_channel_2['channel_id'],
        'start': 0,
    }).json()

    count_msg_pinned = 0
    for curr_message in message_list['messages']:
        if curr_message['is_pinned'] and (curr_message['message'] in [
            'Hi', 'What?!', "Hello World!", "1521 Comp!"
            ]):
            count_msg_pinned += 1
        
    assert count_msg_pinned == 4

    requests.delete(url + '/clear')

def test_pin_multiple_messages(url, user_1, user_2, user_3, user_4, public_channel_3):
    """
    Test for pinning multiple different messages.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_1['token'],
        'channel_id': public_channel_3['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_3['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_4['token'],
        'channel_id': public_channel_3['channel_id']
    })

    requests.post(f"{url}/channel/addowner", json={
        'token': user_3['token'],
        'channel_id': public_channel_3['channel_id'],
        'u_id': user_4['u_id'],
    }).json()
    
    msg_1 = request_message_send(url, user_1['token'], public_channel_3['channel_id'], "Intelligence").json()
    msg_2 = request_message_send(url, user_2['token'], public_channel_3['channel_id'], "Is").json()
    msg_3 = request_message_send(url, user_2['token'], public_channel_3['channel_id'], "The").json()
    request_message_send(url, user_3['token'], public_channel_3['channel_id'], "Ability").json()
    msg_5 = request_message_send(url, user_3['token'], public_channel_3['channel_id'], "To Adapt").json()
    msg_6 = request_message_send(url, user_3['token'], public_channel_3['channel_id'], "To").json()
    msg_7 = request_message_send(url, user_4['token'], public_channel_3['channel_id'], "Change").json()

    request_message_pin(url, user_3['token'], msg_1['message_id'])
    request_message_pin(url, user_3['token'], msg_2['message_id'])
    request_message_pin(url, user_4['token'], msg_3['message_id'])
    request_message_pin(url, user_4['token'], msg_5['message_id'])
    request_message_pin(url, user_4['token'], msg_6['message_id'])
    request_message_pin(url, user_4['token'], msg_7['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_1['token'],
        'channel_id': public_channel_3['channel_id'],
        'start': 0,
    }).json()

    count_msg_pinned = 0
    for curr_message in message_list['messages']:
        if curr_message['is_pinned'] and (curr_message['message'] in [
            'Intelligence', 'Is', "The", "Ability", "To Adapt", "To", "Change"
            ]):
            count_msg_pinned += 1
        
    assert count_msg_pinned == 6

    requests.delete(url + '/clear')

def test_pin_in_private_channel(url, user_1, user_2, private_channel_1):
    """
    Test for pinning messages in private channels.
    """
    requests.post(f"{url}/channel/invite", json={
        'token': user_1['token'],
        'channel_id': private_channel_1['channel_id'],
        'u_id': user_2['u_id'],
    }).json()

    msg_1 = request_message_send(url, user_1['token'], private_channel_1['channel_id'], "Become").json()
    msg_2 = request_message_send(url, user_2['token'], private_channel_1['channel_id'], "A").json()
    msg_3 = request_message_send(url, user_2['token'], private_channel_1['channel_id'], "Hero").json()

    request_message_pin(url, user_1['token'], msg_1['message_id'])
    request_message_pin(url, user_1['token'], msg_2['message_id'])
    request_message_pin(url, user_1['token'], msg_3['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_1['token'],
        'channel_id': private_channel_1['channel_id'],
        'start': 0,
    }).json()

    count_msg_pinned = 0
    for curr_message in message_list['messages']:
        if curr_message['is_pinned'] and (curr_message['message'] in [
            'Become', 'A', "Hero"
            ]):
            count_msg_pinned += 1
        
    assert count_msg_pinned == 3

    requests.delete(url + '/clear')

def test_flockr_owner_pin_msg_in_nonmember_channels(url, user_1, user_2, private_channel_2):
    """
    (Assumption Testing) Test for the ability of flockr owner to pin messages in channels that
    they are not a part of.
    (Assumption) First user to register is flockr owner.
    """
    msg_1 = request_message_send(url, user_2['token'], private_channel_2['channel_id'], "I").json()
    msg_2 = request_message_send(url, user_2['token'], private_channel_2['channel_id'], "Am").json()
    msg_3 = request_message_send(url, user_2['token'], private_channel_2['channel_id'], "Insane").json()

    request_message_pin(url, user_1['token'], msg_1['message_id'])
    request_message_pin(url, user_1['token'], msg_2['message_id'])
    request_message_pin(url, user_1['token'], msg_3['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': private_channel_2['channel_id'],
        'start': 0,
    }).json()

    count_msg_pinned = 0
    for curr_message in message_list['messages']:
        if curr_message['is_pinned'] and (curr_message['message'] in [
            'I', 'Am', "Insane"
            ]):
            count_msg_pinned += 1
        
    assert count_msg_pinned == 3

    requests.delete(url + '/clear')


#------------------------------------------------------------------------------#
#                                 message/unpin                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_valid_message_id_unpin(url, user_1, default_message, public_channel_1):
    """
    Test whether the message_id is a valid id.
    """
    request_message_pin(url, user_1['token'], default_message['message_id'])
    ret_unpinned = request_message_unpin(url, user_1['token'], default_message['message_id'] + 1)

    assert ret_unpinned.status_code == InputError.code

    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hello World!").json()
    request_message_pin(url, user_1['token'], msg_1['message_id'])
    ret_unpinned_1 = request_message_unpin(url, user_1['token'], msg_1['message_id'] - 2)
    assert ret_unpinned_1.status_code == InputError.code

    msg_2 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Now Way!?").json()
    request_message_pin(url, user_1['token'], msg_2['message_id'])
    ret_unpinned_2 = request_message_pin(url, user_1['token'], msg_2['message_id'] + 100)
    assert ret_unpinned_2.status_code == InputError.code

    requests.delete(url + '/clear')

def test_already_unpinned(url, user_1, user_2, public_channel_1):
    """
    Test for pinning an already unpinned message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = request_message_send(url, user_2['token'], public_channel_1['channel_id'], "Hello World!").json()

    ret_unpinned = request_message_unpin(url, user_1['token'], msg_1['message_id'])
    assert ret_unpinned.status_code == InputError.code

    requests.delete(url + '/clear')

def test_user_is_member_of_channel_with_message_unpin(url, user_1, user_2, user_3, user_4, public_channel_2):
    """
    Test for user unpinning a message in a channel that they are not a member of.
    """
    msg_1 = request_message_send(url, user_2['token'], public_channel_2['channel_id'], "I am amazing!").json()
    msg_2 = request_message_send(url, user_2['token'], public_channel_2['channel_id'], "No you're not!").json()

    request_message_pin(url, user_2['token'], msg_1['message_id'])
    request_message_pin(url, user_2['token'], msg_2['message_id'])

    ret_unpinned_1 = request_message_unpin(url, user_3['token'], msg_1['message_id'])
    ret_unpinned_2 = request_message_unpin(url, user_4['token'], msg_2['message_id'])

    assert ret_unpinned_1.status_code == AccessError.code
    assert ret_unpinned_2.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_authorised_to_unpin(url, user_1, public_channel_1):
    """
    Test for a logged out user trying to unpin a message.
    """
    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "I am amazing!").json()
    request_message_pin(url, user_1['token'], msg_1['message_id'])

    requests.post(f"{url}/auth/logout", json={
        'token': user_1['token'],
    }).json()

    ret_unpinned = request_message_unpin(url, user_1['token'], msg_1['message_id'])
    assert ret_unpinned.status_code == AccessError.code

    requests.delete(url + '/clear')

def test_non_owner_unpin(url, user_1, user_2, public_channel_1):
    """
    Test for a user who is not an owner of the channel, unpinning a message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hello World!").json()
    request_message_pin(url, user_1['token'], msg_1['message_id'])

    ret_unpinned = request_message_unpin(url, user_2['token'], msg_1['message_id'])
    assert ret_unpinned.status_code == AccessError.code

    requests.delete(url + '/clear')


#?------------------------------ Output Testing ------------------------------?#

def test_unpin_correct_message(url, user_1, user_2, public_channel_1):
    """
    Test for unpinning the correct message.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hello World!").json()
    msg_2 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hi").json()
    msg_3 = request_message_send(url, user_2['token'], public_channel_1['channel_id'], "What?!").json()
    msg_4 = request_message_send(url, user_2['token'], public_channel_1['channel_id'], "1521 Comp!").json()

    request_message_pin(url, user_1['token'], msg_1['message_id'])
    request_message_pin(url, user_1['token'], msg_2['message_id'])
    request_message_pin(url, user_1['token'], msg_3['message_id'])
    request_message_pin(url, user_1['token'], msg_4['message_id'])

    request_message_unpin(url, user_1['token'], msg_1['message_id'])
    request_message_unpin(url, user_1['token'], msg_4['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    count_msg_unpinned = 0
    for curr_message in message_list['messages']:
        if not curr_message['is_pinned'] and (curr_message['message'] in ['Hello World!', '1521 Comp!']):
            count_msg_unpinned += 1
        
    assert count_msg_unpinned == 2

    requests.delete(url + '/clear')

def test_added_owner_can_unpin(url, user_1, user_2, public_channel_1):
    """
    Test for unpinning messages from a recently added owner.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id']
    })

    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hello World!").json()
    msg_2 = request_message_send(url, user_2['token'], public_channel_1['channel_id'], "Hi").json()
    request_message_pin(url, user_1['token'], msg_1['message_id'])
    request_message_pin(url, user_1['token'], msg_2['message_id'])

    requests.post(f"{url}/channel/addowner", json={
        'token': user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'u_id': user_2['u_id'],
    }).json()

    request_message_unpin(url, user_2['token'], msg_2['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    for curr_message in message_list['messages']:
        if curr_message['message_id'] == msg_2['message_id']:
            assert not curr_message['is_pinned']
    
    requests.delete(url + '/clear')

def test_unpin_owned_message(url, user_1, public_channel_1):
    """
    Test for unpinning the user's own messages.
    """
    msg_1 = request_message_send(url, user_1['token'], public_channel_1['channel_id'], "Hello World!").json()
    request_message_pin(url, user_1['token'], msg_1['message_id'])
    request_message_unpin(url, user_1['token'], msg_1['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'start': 0,
    }).json()

    for curr_message in message_list['messages']:
        if curr_message['message_id'] == msg_1['message_id']:
            assert not curr_message['is_pinned']

    requests.delete(url + '/clear')

def test_unpin_other_messages(url, user_1, user_2, user_3, public_channel_2):
    """
    Test for unpinning other user's messages.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_1['token'],
        'channel_id': public_channel_2['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_3['token'],
        'channel_id': public_channel_2['channel_id']
    })

    msg_1 = request_message_send(url, user_1['token'], public_channel_2['channel_id'], "Hello World!").json()
    msg_2 = request_message_send(url, user_1['token'], public_channel_2['channel_id'], "Hi").json()
    msg_3 = request_message_send(url, user_3['token'], public_channel_2['channel_id'], "What?!").json()
    msg_4 = request_message_send(url, user_3['token'], public_channel_2['channel_id'], "1521 Comp!").json()

    request_message_pin(url, user_2['token'], msg_1['message_id'])
    request_message_pin(url, user_2['token'], msg_2['message_id'])
    request_message_pin(url, user_2['token'], msg_3['message_id'])
    request_message_pin(url, user_2['token'], msg_4['message_id'])

    request_message_unpin(url, user_2['token'], msg_1['message_id'])
    request_message_unpin(url, user_2['token'], msg_3['message_id'])
    request_message_unpin(url, user_2['token'], msg_4['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_1['token'],
        'channel_id': public_channel_2['channel_id'],
        'start': 0,
    }).json()

    count_msg_unpinned = 0
    for curr_message in message_list['messages']:
        if not curr_message['is_pinned'] and (curr_message['message'] in [
            'Hello World!', 'What?!', "1521 Comp!"
            ]):
            count_msg_unpinned += 1
        
    assert count_msg_unpinned == 3

    requests.delete(url + '/clear')

def test_unpin_multiple_messages(url, user_1, user_2, user_3, user_4, public_channel_3):
    """
    Test for unpinning multiple different messages.
    """
    requests.post(f"{url}/channel/join", json={
        'token': user_1['token'],
        'channel_id': public_channel_3['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_2['token'],
        'channel_id': public_channel_3['channel_id']
    })
    requests.post(f"{url}/channel/join", json={
        'token': user_4['token'],
        'channel_id': public_channel_3['channel_id']
    })

    requests.post(f"{url}/channel/addowner", json={
        'token': user_3['token'],
        'channel_id': public_channel_3['channel_id'],
        'u_id': user_4['u_id'],
    }).json()
    
    msg_1 = request_message_send(url, user_1['token'], public_channel_3['channel_id'], "Intelligence").json()
    msg_2 = request_message_send(url, user_2['token'], public_channel_3['channel_id'], "Is").json()
    msg_3 = request_message_send(url, user_2['token'], public_channel_3['channel_id'], "The").json()
    request_message_send(url, user_3['token'], public_channel_3['channel_id'], "Ability").json()
    msg_5 = request_message_send(url, user_3['token'], public_channel_3['channel_id'], "To Adapt").json()
    msg_6 = request_message_send(url, user_3['token'], public_channel_3['channel_id'], "To").json()
    msg_7 = request_message_send(url, user_4['token'], public_channel_3['channel_id'], "Change").json()

    request_message_pin(url, user_3['token'], msg_1['message_id'])
    request_message_pin(url, user_3['token'], msg_2['message_id'])
    request_message_pin(url, user_4['token'], msg_3['message_id'])
    request_message_pin(url, user_4['token'], msg_5['message_id'])
    request_message_pin(url, user_4['token'], msg_6['message_id'])
    request_message_pin(url, user_4['token'], msg_7['message_id'])

    request_message_unpin(url, user_4['token'], msg_1['message_id'])
    request_message_unpin(url, user_4['token'], msg_2['message_id'])
    request_message_unpin(url, user_3['token'], msg_3['message_id'])
    request_message_unpin(url, user_4['token'], msg_5['message_id'])
    request_message_unpin(url, user_4['token'], msg_7['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_1['token'],
        'channel_id': public_channel_3['channel_id'],
        'start': 0,
    }).json()

    count_msg_unpinned = 0
    for curr_message in message_list['messages']:
        if not curr_message['is_pinned'] and (curr_message['message'] in [
            'Intelligence', 'Is', "The", "Ability", "To Adapt", "Change"
            ]):
            count_msg_unpinned += 1
        
    assert count_msg_unpinned == 6

    requests.delete(url + '/clear')

def test_unpin_in_private_channel(url, user_1, user_2, private_channel_1):
    """
    Test for unpinning messages in private channels.
    """
    requests.post(f"{url}/channel/invite", json={
        'token': user_1['token'],
        'channel_id': private_channel_1['channel_id'],
        'u_id': user_2['u_id'],
    }).json()

    msg_1 = request_message_send(url, user_1['token'], private_channel_1['channel_id'], "Become").json()
    msg_2 = request_message_send(url, user_2['token'], private_channel_1['channel_id'], "A").json()
    msg_3 = request_message_send(url, user_2['token'], private_channel_1['channel_id'], "Hero").json()

    request_message_pin(url, user_1['token'], msg_1['message_id'])
    request_message_pin(url, user_1['token'], msg_2['message_id'])
    request_message_pin(url, user_1['token'], msg_3['message_id'])

    request_message_unpin(url, user_1['token'], msg_2['message_id'])
    request_message_unpin(url, user_1['token'], msg_3['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_1['token'],
        'channel_id': private_channel_1['channel_id'],
        'start': 0,
    }).json()

    count_msg_unpinned = 0
    for curr_message in message_list['messages']:
        if not curr_message['is_pinned'] and (curr_message['message'] in [
            'A', "Hero"
            ]):
            count_msg_unpinned += 1
        
    assert count_msg_unpinned == 2

    requests.delete(url + '/clear')

def test_flockr_owner_unpin_msg_in_nonmember_channels(url, user_1, user_2, private_channel_2):
    """
    (Assumption Testing) Test for the ability of flockr owner to unpin messages in channels that
    they are not a part of.
    (Assumption) First user to register is flockr owner.
    """
    request_message_send(url, user_2['token'], private_channel_2['channel_id'], "I").json()
    msg_2 = request_message_send(url, user_2['token'], private_channel_2['channel_id'], "Am").json()
    msg_3 = request_message_send(url, user_2['token'], private_channel_2['channel_id'], "Insane").json()

    request_message_pin(url, user_1['token'], msg_2['message_id'])
    request_message_pin(url, user_1['token'], msg_3['message_id'])

    request_message_unpin(url, user_1['token'], msg_3['message_id'])

    message_list = requests.get(f"{url}/channel/messages", params={
        'token': user_2['token'],
        'channel_id': private_channel_2['channel_id'],
        'start': 0,
    }).json()

    count_msg_pinned = 0
    for curr_message in message_list['messages']:
        if not curr_message['is_pinned'] and (curr_message['message'] in [
            'I', "Insane"
            ]):
            count_msg_pinned += 1
        
    assert count_msg_pinned == 2

    requests.delete(url + '/clear')

