"""
channel feature test implementation to test functions in channel.py

Feature implementation was written by Gabriel Ting, Tam Do, Prathamesh Jagtap.

2020 T3 COMP1531 Major Project
"""
import pytest

import src.feature.auth as auth
import src.feature.channel as channel
import src.feature.channels as channels

from src.feature.other import clear
from src.feature.error import InputError, AccessError
from src.helpers.helpers_test import create_messages


DELAY = 100

#------------------------------------------------------------------------------#
#                               channel_invite                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_channel_invite_login_user(user_1, user_2, user_3, user_4, public_channel_1):
    """Testing invalid token for users which have logged out
    """
    auth.auth_logout(user_1['token'])
    auth.auth_logout(user_2['token'])
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])

    with pytest.raises(AccessError):
        channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_1['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_3['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(user_3['token'], public_channel_1['channel_id'], user_3['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(user_4['token'], public_channel_1['channel_id'], user_3['u_id'])
    clear()

def test_channel_invite_wrong_data_type(user_1, public_channel_1):
    """Testing when wrong data types are used as input
    """

    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], public_channel_1['channel_id'], -1)
    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], public_channel_1['channel_id'], '@#$!')
    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], public_channel_1['channel_id'], 67.666)
    clear()

def test_channel_invite_invalid_user(user_1, public_channel_1):
    """Testing when invalid user is invited to channel
    """

    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_1['u_id'] + 1)
    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_1['u_id'] - 1)
    clear()

def test_channel_invite_invalid_channel(user_1, user_2):
    """Testing when valid user is invited to invalid channel
    """
    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], -122, user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], -642, user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], '@#@!', user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], 212.11, user_2['u_id'])
    clear()

def test_channel_invite_not_authorized(user_1, user_2, user_3, public_channel_1, logout_user_1):
    """Testing when user is not authorized to invite other users to channel
    (Assumption) This includes an invalid user inviting users to channel
    """
    with pytest.raises(AccessError):
        channel.channel_invite(12, public_channel_1['channel_id'], user_3['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(-12, public_channel_1['channel_id'], user_3['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(121.11, public_channel_1['channel_id'], user_3['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_1['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_3['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_3['u_id'])
    clear()

def test_channel_invite_invalid_self_invite(user_1, public_channel_1):
    """Testing when user is not allowed to invite him/herself to channel
    (Assumption testing) this error will be treated as AccessError
    """
    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_1['u_id'])
    clear()

def test_channel_multiple_invite(user_1, user_2, public_channel_1):
    """Testing when user invites a user multiple times
    (Assumption testing) this error will be treated as AccessError
    """
    assert channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id']) == {}

    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_1['u_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_channel_invite_successful(user_1, user_2, user_3, user_4, public_channel_1):
    """Testing if user has successfully been invited to the channel
    """
    channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    assert channel.channel_details(user_1['token'], public_channel_1['channel_id']) == {
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

    channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_3['u_id'])
    assert channel.channel_details(user_1['token'], public_channel_1['channel_id']) == {
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

    channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_4['u_id'])
    assert channel.channel_details(user_1['token'], public_channel_1['channel_id']) == {
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
    clear()

def test_channel_invite_flockr_user(user_1, user_2, user_3, public_channel_2):
    """(Assumption testing) first person to register is flockr owner
    Testing if flockr owner has been successfully invited to channel and given ownership
    """
    channel.channel_invite(user_2['token'], public_channel_2['channel_id'], user_3['u_id'])
    assert channel.channel_details(user_2['token'], public_channel_2['channel_id']) == {
        'name': 'Group 2',
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

    channel.channel_invite(user_3['token'], public_channel_2['channel_id'], user_1['u_id'])
    assert channel.channel_details(user_1['token'], public_channel_2['channel_id']) == {
        'name': 'Group 2',
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
    clear()

def test_output_invite_user_list(user_1, user_2, public_channel_1):
    """Testing if channel info has been added to user profile when added
    """
    channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])

    channel_list = channels.channels_list(user_1['token'])
    on_list = False
    for item in channel_list['channels']:
        if item['channel_id'] == public_channel_1['channel_id']:
            on_list = True
            break
    assert on_list

    channel_list = channels.channels_list(user_2['token'])
    on_list = False
    for curr_channel in channel_list['channels']:
        if curr_channel['channel_id'] == public_channel_1['channel_id']:
            on_list = True
            break
    assert on_list
    clear()

#------------------------------------------------------------------------------#
#                               channel_details                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_channel_details_invalid_channel(user_1):
    """Testing if channel is invalid or does not exist
    """
    with pytest.raises(InputError):
        channel.channel_details(user_1['token'], -1)
    with pytest.raises(InputError):
        channel.channel_details(user_1['token'], -19)
    with pytest.raises(InputError):
        channel.channel_details(user_1['token'], '#@&!')
    with pytest.raises(InputError):
        channel.channel_details(user_1['token'], 121.12)
    clear()

def test_channel_details_invalid_user(user_1, user_2, public_channel_1):
    """Testing if unauthorized/invalid user is unable to access channel details
    """
    with pytest.raises(AccessError):
        channel.channel_details(user_2['token'], public_channel_1['channel_id'])
    clear()

def test_channel_details_invalid_token(user_1, public_channel_1):
    """Testing if given invalid token returns an AccessError
    """
    with pytest.raises(AccessError):
        channel.channel_details(6.333, 0)
    with pytest.raises(AccessError):
        channel.channel_details('@^!&', -3)
    with pytest.raises(AccessError):
        channel.channel_details(-1, public_channel_1['channel_id'])
    with pytest.raises(AccessError):
        channel.channel_details('abcd', public_channel_1['channel_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_channel_details_authorized_user(user_1, user_2, user_3, user_4, public_channel_1):
    """Testing the required correct details of a channel
    """

    channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    assert channel.channel_details(user_1['token'], public_channel_1['channel_id']) == {
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

    channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_3['u_id'])
    assert channel.channel_details(user_1['token'], public_channel_1['channel_id']) == {
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

    channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_4['u_id'])
    assert channel.channel_details(user_1['token'], public_channel_1['channel_id']) == {
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
    clear()


def test_output_details_twice(user_1, user_2, public_channel_1, public_channel_2):
    """Test if details will be shown when a second channel is created.
    """
    channel.channel_invite(user_2['token'], public_channel_2['channel_id'], user_1['u_id'])
    assert channel.channel_details(user_1['token'], public_channel_2['channel_id']) == {
        'name': 'Group 2',
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
                'u_id': user_1['u_id'],
                'name_first': 'John',
                'name_last': 'Smith',
            },
        ],
    }
    clear()

#------------------------------------------------------------------------------#
#                               channel_messages                               #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_input_messages_channel_id(user_1):
    """Testing when an invalid channel_id is used as a parameter
    """
    start = 0

    with pytest.raises(InputError):
        channel.channel_messages(user_1['token'], -1, start)
    with pytest.raises(InputError):
        channel.channel_messages(user_1['token'], 0, start)
    with pytest.raises(InputError):
        channel.channel_messages(user_1['token'], 1, start)
    with pytest.raises(InputError):
        channel.channel_messages(user_1['token'], 5, start)
    clear()

def test_input_messages_start(user_1, public_channel_1):
    """Testing when start is an invalid start value. Start is greater than the
    total number of messages in the channel.
    """
    with pytest.raises(InputError):
        channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 1)
    with pytest.raises(InputError):
        channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 10)
    with pytest.raises(InputError):
        channel.channel_messages(user_1['token'], public_channel_1['channel_id'], -1)
    clear()

def test_input_messages_start_equal_1(user_1, public_channel_1):
    """Testing when start index is equal to the total number of messages, it will
    instead raise an InputError (assumption).
    """
    create_messages(user_1, public_channel_1['channel_id'], 0, 1)
    with pytest.raises(InputError):
        channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 1)
    clear()

def test_input_messages_start_equal_10(user_1, public_channel_1):
    """Testing when start index is equal to the total number of messages, it will
    instead raise an InputError (assumption).
    """
    create_messages(user_1, public_channel_1['channel_id'], 0, 10)
    with pytest.raises(InputError):
        channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 10)
    clear()

def test_access_messages_user_is_member(user_1, user_2, public_channel_1, public_channel_2):
    """Testing if another user can access the channel
    """
    with pytest.raises(AccessError):
        channel.channel_messages(user_1['token'], public_channel_2['channel_id'], 0)
    with pytest.raises(AccessError):
        channel.channel_messages(user_2['token'], public_channel_1['channel_id'], 0)
    clear()

def test_access_messages_valid_token(user_1, public_channel_1, logout_user_1):
    """Testing if token is valid
    """
    with pytest.raises(AccessError):
        channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    clear()
#?------------------------------ Output Testing ------------------------------?#

#! Testing when a channel has no messages
def test_output_no_messages(user_1, public_channel_1):
    """Testing when a channel has no messages
    """
    result = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    assert result['messages'] == []
    assert result['start'] == -1
    assert result['end'] == -1
    clear()

#! Testing when a channel less than 50 messages
def test_output_messages_1(user_1, public_channel_1):
    """Testing when a channel has a single message
    """
    message_list = create_messages(user_1, public_channel_1['channel_id'], 0, 1)
    assert len(message_list) == 1
    result = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    assert len(message_list) == len(result['messages'])
    for index, item in enumerate(result['messages']):
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(result['messages']) == 1
    assert result['start'] == 0
    assert result['end'] == -1
    clear()

def test_output_messages_10_start_0(user_1, public_channel_1):
    """Testing when a channel has 10 messages at start 0.
    """
    message_list = create_messages(user_1, public_channel_1['channel_id'], 0, 10)
    assert len(message_list) == 10
    result = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    assert len(message_list) == len(result['messages'])
    for index, item in enumerate(result['messages']):
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(result['messages']) == 10
    assert result['start'] == 0
    assert result['end'] == -1
    clear()

def test_output_messages_10_start_5(user_1, public_channel_1):
    """Testing when a channel has 10 messages at start 5.
    """
    message_list = create_messages(user_1, public_channel_1['channel_id'], 0, 10)
    assert len(message_list) == 10
    result = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 5)
    assert len(message_list[5:]) == len(result['messages'])
    for index, item in enumerate(result['messages']):
        index += 5
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(result['messages']) == 5
    assert result['start'] == 5
    assert result['end'] == -1
    clear()

def test_output_messages_49_start_0(user_1, public_channel_1):
    """Testing when a channel has 49 total messages at start 0.
    """
    message_list = create_messages(user_1, public_channel_1['channel_id'], 0, 49)
    assert len(message_list) == 49
    result = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    assert len(message_list) == len(result['messages'])
    for index, item in enumerate(result['messages']):
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(result['messages']) == 49
    assert result['start'] == 0
    assert result['end'] == -1
    clear()

def test_output_messages_49_start_25(user_1, public_channel_1):
    """Testing when a channel has 49 total messages at start 25.
    """
    message_list = create_messages(user_1, public_channel_1['channel_id'], 0, 49)
    assert len(message_list) == 49
    result = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 25)
    assert len(message_list[25:]) == len(result['messages'])
    for index, item in enumerate(result['messages']):
        index += 25
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(result['messages']) == 24
    assert result['start'] == 25
    assert result['end'] == -1
    clear()

#! Testing when a channel exactly 50 messages
def test_output_messages_50_start_0(user_1, public_channel_1):
    """Testing when a channel has 50 total messages at start 0.
    """
    message_list = create_messages(user_1, public_channel_1['channel_id'], 0, 50)
    assert len(message_list) == 50
    result = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    assert len(message_list) == len(result['messages'])
    for index, item in enumerate(result['messages']):
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(result['messages']) == 50
    assert result['start'] == 0
    assert result['end'] == -1
    clear()

def test_output_messages_50_start_25(user_1, public_channel_1):
    """Testing when a channel has 50 total messages at start 25.
    """
    message_list = create_messages(user_1, public_channel_1['channel_id'], 0, 50)
    assert len(message_list) == 50
    result = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 25)
    assert len(message_list[25:]) == len(result['messages'])
    for index, item in enumerate(result['messages']):
        index += 25
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(result['messages']) == 25
    assert result['start'] == 25
    assert result['end'] == -1
    clear()

def test_output_messages_50_start_49(user_1, public_channel_1):
    """Testing when a channel has 50 total messages at start 49.
    """
    message_list = create_messages(user_1, public_channel_1['channel_id'], 0, 50)
    assert len(message_list) == 50
    result = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 49)
    assert len(message_list[49:]) == len(result['messages'])
    for index, item in enumerate(result['messages']):
        index += 49
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(result['messages']) == 1
    assert result['start'] == 49
    assert result['end'] == -1
    clear()

#! Testing when a channel has more than 50 messages
def test_output_messages_51_start_0(user_1, public_channel_1):
    """Testing when a channel has 51 total messages at start 0.
    """
    message_list = create_messages(user_1, public_channel_1['channel_id'], 0, 51)
    assert len(message_list) == 51
    result = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    assert len(message_list[0:50]) == len(result['messages'])
    for index, item in enumerate(result['messages']):
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(result['messages']) == 50
    assert result['start'] == 0
    assert result['end'] == 50
    clear()

def test_output_messages_51_start_25(user_1, public_channel_1):
    """Testing when a channel has 51 total messages at start 25.
    """
    message_list = create_messages(user_1, public_channel_1['channel_id'], 0, 51)
    assert len(message_list) == 51
    result = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 25)
    assert len(message_list[25:]) == len(result['messages'])
    for index, item in enumerate(result['messages']):
        index += 25
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(result['messages']) == 26
    assert result['start'] == 25
    assert result['end'] == -1
    clear()

def test_output_messages_51_start_50(user_1, public_channel_1):
    """Testing when a channel has 51 total messages at start 50.
    """
    message_list = create_messages(user_1, public_channel_1['channel_id'], 0, 51)
    assert len(message_list) == 51
    result = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 50)
    assert len(message_list[50:]) == len(result['messages'])
    for index, item in enumerate(result['messages']):
        index += 50
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(result['messages']) == 1
    assert result['start'] == 50
    assert result['end'] == -1
    clear()

def test_output_messages_100_start_10(user_1, public_channel_1):
    """Testing when a channel has 100 total messages at start 10.
    """
    message_list = create_messages(user_1, public_channel_1['channel_id'], 0, 100)
    assert len(message_list) == 100
    result = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 10)
    assert len(message_list[10:60]) == len(result['messages'])
    for index, item in enumerate(result['messages']):
        index += 10
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(result['messages']) == 50
    assert result['start'] == 10
    assert result['end'] == 60
    clear()

#! Testing using examples provided in specification (refer to 6.5. Pagination)
def test_output_messages_125_start_0(user_1, public_channel_1):
    """Testing when a channel has 125 total messages at start 0.
    """
    message_list = create_messages(user_1, public_channel_1['channel_id'], 0, 125)
    assert len(message_list) == 125
    result = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    assert len(message_list[0:50]) == len(result['messages'])
    for index, item in enumerate(result['messages']):
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(result['messages']) == 50
    assert result['start'] == 0
    assert result['end'] == 50
    clear()

def test_output_messages_125_start_50(user_1, public_channel_1):
    """Testing when a channel has 125 total messages at start 50.
    """
    message_list = create_messages(user_1, public_channel_1['channel_id'], 0, 125)
    assert len(message_list) == 125
    result = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 50)
    assert len(message_list[50:100]) == len(result['messages'])
    for index, item in enumerate(result['messages']):
        index += 50
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)
    assert len(result['messages']) == 50
    assert result['start'] == 50
    assert result['end'] == 100
    clear()

def test_output_messages_125_start_100(user_1, public_channel_1):
    """Testing when a channel has 125 total messages at start 100.
    """
    message_list = create_messages(user_1, public_channel_1['channel_id'], 0, 125)
    assert len(message_list) == 125
    result = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 100)

    assert len(message_list[100:]) == len(result['messages'])
    for index, item in enumerate(result['messages']):
        index += 100
        assert item['message_id'] == message_list[index]['message_id']
        assert item['u_id'] == message_list[index]['u_id']
        assert item['message'] == message_list[index]['message']
        assert (message_list[index]['time_created'] - DELAY) <= item['time_created']
        assert item['time_created'] <= (message_list[index]['time_created'] + DELAY)

    assert len(result['messages']) == 25
    assert result['start'] == 100
    assert result['end'] == -1
    clear()

#------------------------------------------------------------------------------#
#                               channel_leave                                  #
#------------------------------------------------------------------------------#

#?------------------------- Input/Access Error Testing -----------------------?#

def test_input_leave_channel_id(user_1):
    """Testing when an invalid channel_id is used as a parameter
    """
    with pytest.raises(InputError):
        channel.channel_leave(user_1['token'], -1)
    with pytest.raises(InputError):
        channel.channel_leave(user_1['token'], 0)
    with pytest.raises(InputError):
        channel.channel_leave(user_1['token'], 1)
    with pytest.raises(InputError):
        channel.channel_leave(user_1['token'], 5)
    clear()

def test_access_leave_user_is_member(user_1, user_2, public_channel_1, public_channel_2):
    """Testing if a user was not in the channel initially
    """

    with pytest.raises(AccessError):
        channel.channel_leave(user_1['token'], public_channel_2['channel_id'])
    with pytest.raises(AccessError):
        channel.channel_leave(user_2['token'], public_channel_1['channel_id'])
    clear()

def test_access_leave_valid_token(user_1, public_channel_1, logout_user_1):
    """Testing if token is valid
    """
    with pytest.raises(AccessError):
        channel.channel_leave(user_1['token'], public_channel_1['channel_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_output_user_leave_public(user_1, public_channel_1):
    """Testing if the user has successfully left a public channel
    """
    channel.channel_leave(user_1['token'], public_channel_1['channel_id'])
    channel_list = channels.channels_list(user_1['token'])
    assert channel_list['channels'] == []
    clear()

def test_output_user_leave_private(user_1, private_channel_1):
    """Testing if the user has successfully left a private channel
    """
    channel.channel_leave(user_1['token'], private_channel_1['channel_id'])
    channel_list = channels.channels_list(user_1['token'])
    assert channel_list['channels'] == []
    clear()

def test_output_user_leave_channels(user_1, public_channel_1):
    """Testing if user has left the correct channel.
    """
    public_channel_2 = channels.channels_create(user_1['token'], 'Group 2', True)
    public_channel_3 = channels.channels_create(user_1['token'], 'Group 3', True)
    channel.channel_leave(user_1['token'], public_channel_2['channel_id'])
    assert channels.channels_list(user_1['token']) == {
        'channels': [
            {
                'channel_id': public_channel_1['channel_id'],
                'name': 'Group 1',
            },
            {
                'channel_id': public_channel_3['channel_id'],
                'name': 'Group 3',
            },
        ],
    }
    clear()

def test_output_leave_channels(user_1, user_2, public_channel_1, public_channel_2):
    """Testing when user leaves multiple channels
    """
    channel.channel_leave(user_1['token'], public_channel_1['channel_id'])
    channel.channel_addowner(user_2['token'], public_channel_2['channel_id'], user_1['u_id'])
    channel.channel_leave(user_1['token'], public_channel_2['channel_id'])

    channel_list = channels.channels_list(user_1['token'])
    assert channel_list['channels'] == []
    clear()

def test_output_all_members_leave(user_1, user_2, public_channel_1):
    """Test if the channel is deleted when all members leave
    """
    channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    channel.channel_leave(user_1['token'], public_channel_1['channel_id'])
    channel.channel_leave(user_2['token'], public_channel_1['channel_id'])

    all_channels = channels.channels_listall(user_1['token'])
    for curr_channel in all_channels['channels']:
        assert curr_channel['channel_id'] != public_channel_1['channel_id']
    clear()

def test_output_flockr_rejoin_channel(user_1, user_2, public_channel_1):
    """Test when the flockr owner leaves and comes back that the user status is an
    owner.
    """
    channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    channel.channel_leave(user_1['token'], public_channel_1['channel_id'])
    channel.channel_join(user_1['token'], public_channel_1['channel_id'])
    new_channel_details = channel.channel_details(user_2['token'], public_channel_1['channel_id'])
    user_1_details = {'u_id': user_1['u_id'], 'name_first': 'John', 'name_last': 'Smith'}
    assert user_1_details in new_channel_details['owner_members']
    assert user_1_details in new_channel_details['all_members']
    clear()

def test_output_creator_rejoin_channel(user_1, user_2, user_3, public_channel_2):
    """Test when the the creator leaves and comes back that the user status is a member.
    """
    channel.channel_invite(user_2['token'], public_channel_2['channel_id'], user_3['u_id'])
    channel.channel_leave(user_2['token'], public_channel_2['channel_id'])
    channel.channel_join(user_2['token'], public_channel_2['channel_id'])
    new_channel_details = channel.channel_details(user_2['token'], public_channel_2['channel_id'])
    user_2_details = {'u_id': user_2['u_id'], 'name_first': 'Jane', 'name_last': 'Smith'}
    assert user_2_details not in new_channel_details['owner_members']
    assert user_2_details in new_channel_details['all_members']
    clear()

def test_output_member_leave(user_1, user_2, user_3, public_channel_1):
    """Testing when a member leaves that it does not delete the channel.
    """
    channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_3['u_id'])

    channel.channel_leave(user_3['token'], public_channel_1['channel_id'])
    channel_leave_details = channel.channel_details(user_1['token'], public_channel_1['channel_id'])
    for member in channel_leave_details['all_members']:
        assert member['u_id'] != user_3['u_id']
    clear()


def test_output_all_owners_leave(user_1, user_2, user_3, user_4, public_channel_1):
    """Testing Process: Tests suite that is designed to test the process of all
    owners leaving in which the user with the lowest u_id in the channel becomes
    the owner automatically.
    Covers also if user access has been erased on channel end.
    """
    channel.channel_addowner(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_3['u_id'])
    channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_4['u_id'])

    # When the first owner leaves
    channel.channel_leave(user_1['token'], public_channel_1['channel_id'])

    # Confirm that there is now one owner in the channel
    channel_data = channel.channel_details(user_2['token'], public_channel_1['channel_id'])
    curr_owner = {'u_id': user_2['u_id'], 'name_first': 'Jane', 'name_last': 'Smith'}
    assert curr_owner in channel_data['owner_members'] and len(channel_data['owner_members']) == 1

    # Check members in the channel
    curr_members = []
    curr_members.append({'u_id': user_2['u_id'], 'name_first': 'Jane', 'name_last': 'Smith'})
    curr_members.append({'u_id': user_3['u_id'], 'name_first': 'Jace', 'name_last': 'Smith'})
    curr_members.append({'u_id': user_4['u_id'], 'name_first': 'Janice', 'name_last': 'Smith'})

    n_members = 0
    for member_details in channel_data['all_members']:
        if member_details in curr_members:
            n_members += 1
            curr_members.remove(member_details)

    assert curr_members == [] and n_members == len(channel_data['all_members'])

    # When all owners leave, automatically assign a user with the lowest u_id
    # as the owner
    channel.channel_leave(user_2['token'], public_channel_1['channel_id'])
    channel_data = channel.channel_details(user_3['token'], public_channel_1['channel_id'])

    # Check members
    curr_members = []
    curr_members.append({'u_id': user_3['u_id'], 'name_first': 'Jace', 'name_last': 'Smith'})
    curr_members.append({'u_id': user_4['u_id'], 'name_first': 'Janice', 'name_last': 'Smith'})
    lowest_u_id_user = user_3
    n_members = 0
    for member_details in channel_data['all_members']:
        if member_details in curr_members:
            n_members += 1
            curr_members.remove(member_details)
            # Find the member with the lowest u_id
            if lowest_u_id_user['u_id'] > member_details['u_id']:
                lowest_u_id_user = member_details

    assert curr_members == [] and n_members == len(channel_data['all_members'])

    # Check if a new owner has been assigned
    assert len(channel_data['owner_members']) == 1
    assert lowest_u_id_user['u_id'] == channel_data['owner_members'][0]['u_id']

    # Check on the user end that the channel is not avialiable on their list.
    channel_list = channels.channels_list(user_1['token'])
    for curr_channel in channel_list['channels']:
        assert curr_channel['channel_id'] is not public_channel_1['channel_id']

    channel_list = channels.channels_list(user_2['token'])
    for curr_channel in channel_list['channels']:
        assert curr_channel['channel_id'] is not public_channel_1['channel_id']

    clear()

#------------------------------------------------------------------------------#
#                                   channel_join                               #
#------------------------------------------------------------------------------#

#?------------------------- Input/Access Error Testing -----------------------?#

def test_input_join_channel_id(user_1):
    """Testing when Channel ID is not a valid channel
    """
    with pytest.raises(InputError):
        channel.channel_join(user_1['token'], -1)
    with pytest.raises(InputError):
        channel.channel_join(user_1['token'], 0)
    with pytest.raises(InputError):
        channel.channel_join(user_1['token'], 1)
    with pytest.raises(InputError):
        channel.channel_join(user_1['token'], 5)
    clear()

def test_access_join_valid_token(user_1, public_channel_1, logout_user_1):
    """Testing if token is valid
    """
    with pytest.raises(AccessError):
        channel.channel_join(user_1['token'], public_channel_1['channel_id'])
    clear()

def test_access_join_user_is_member(user_1, user_2, user_3, private_channel_1):
    """Testing if channel_id refers to a channel that is private (when the
    authorised user is not a global owner)
    """
    # Channel is private
    with pytest.raises(AccessError):
        channel.channel_join(user_3['token'], private_channel_1['channel_id'])
    with pytest.raises(AccessError):
        channel.channel_join(user_2['token'], private_channel_1['channel_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_output_user_join_public(user_1, user_2, public_channel_1):
    """Testing if the user has successfully joined a public channel
    """
    # Make a public channel and join user_2
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])

    # Check channel details if the user is a member
    channel_data = channel.channel_details(user_2['token'], public_channel_1['channel_id'])
    in_channel = False
    for member in channel_data['all_members']:
        if member['u_id'] is user_2['u_id']:
            in_channel = True
            break
    assert in_channel

    # Check if channel appears in the user's channels list
    channel_user_list = channels.channels_list(user_2['token'])
    assert len(channel_user_list) == 1
    clear()

def test_output_user_join_flockr_private(user_1, user_2, private_channel_2):
    """Test for flockr owner (flockr owner can join private channels)
    """
    # Assume that the first user is the flockr owner
    channel.channel_join(user_1['token'], private_channel_2['channel_id'])
    channel_list = channels.channels_list(user_2['token'])

    # Check if flockr owner is in channel list
    in_channel = False
    for curr_channel in channel_list['channels']:
        if curr_channel['channel_id'] == private_channel_2['channel_id']:
            in_channel = True
    assert in_channel
    clear()

def test_output_user_join_flockr_member_list(user_1, user_2, private_channel_2):
    """Test for flockr owner (flockr owner can join private channels)
    """
    # Assume that the first user is the flockr owner
    channel.channel_join(user_1['token'], private_channel_2['channel_id'])

    # Check if flockr owner is a channel member
    channel_data = channel.channel_details(user_2['token'], private_channel_2['channel_id'])
    is_member = False
    for member in channel_data['all_members']:
        if member['u_id'] == user_1['u_id']:
            is_member = True
    assert is_member
    clear()

def test_output_user_join_flockr_owner_list(user_1, user_2, private_channel_2):
    """Test for flockr owner (flockr owner can join private channels)
    """
    # Assume that the first user is the flockr owner
    channel.channel_join(user_1['token'], private_channel_2['channel_id'])

    # Flockr owner becomes owner after channel join
    owner = True
    channel_data = channel.channel_details(user_1['token'], private_channel_2['channel_id'])
    for member in channel_data['owner_members']:
        if member['u_id'] == user_1['u_id']:
            owner = False
    assert not owner
    clear()

def test_output_user_join_again(user_1, public_channel_1):
    """Test for a person joining again
    """
    channel_data = channel.channel_details(user_1['token'], public_channel_1['channel_id'])
    user_details = {'name_first': 'John', 'name_last': 'Smith', 'u_id': user_1['u_id']}
    assert user_details in channel_data['all_members']
    channel.channel_join(user_1['token'], public_channel_1['channel_id'])
    # Check channel details if the user is a member
    channel_data = channel.channel_details(user_1['token'], public_channel_1['channel_id'])
    assert user_details in channel_data['all_members']
    # Check if channel appears in the user's channels list
    channel_user_list = channels.channels_list(user_1['token'])
    assert len(channel_user_list) == 1
    clear()

#------------------------------------------------------------------------------#
#                                channel_addowner                              #
#------------------------------------------------------------------------------#

#?------------------------- Input/Access Error Testing -----------------------?#

def test_input_channel_id_addowner(user_1, user_2):
    """Testing when Channel ID is not a valid channel
    """
    with pytest.raises(InputError):
        channel.channel_addowner(user_1['token'], -1, user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_addowner(user_1['token'], 0, user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_addowner(user_1['token'], 1, user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_addowner(user_1['token'], 5, user_2['u_id'])
    clear()

def test_access_add_valid_token(user_1, user_2, public_channel_1, logout_user_1):
    """Testing if token is valid
    """
    with pytest.raises(AccessError):
        channel.channel_addowner(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    clear()

def test_input_u_id_addowner(user_1, public_channel_1):
    """Testing when u_id is not a valid u_id
    """
    with pytest.raises(InputError):
        channel.channel_addowner(user_1['token'], public_channel_1['channel_id'], user_1['u_id'] + 1)
    with pytest.raises(InputError):
        channel.channel_addowner(user_1['token'], public_channel_1['channel_id'], user_1['u_id'] - 1)
    clear()

def test_add_user_is_already_owner(user_1, user_2, public_channel_1, public_channel_2):
    """Testing when user with user id u_id is already an owner of the channel
    """
    with pytest.raises(InputError):
        channel.channel_addowner(user_1['token'], public_channel_1['channel_id'], user_1['u_id'])
    with pytest.raises(InputError):
        channel.channel_addowner(user_2['token'], public_channel_2['channel_id'], user_2['u_id'])
    clear()

def test_auth_user_is_not_owner(user_1, user_2, public_channel_1, public_channel_2):
    """Testing when the authorised user is not an owner of the flockr, or an owner of this channel
    """
    with pytest.raises(AccessError):
        channel.channel_addowner(user_1['token'], public_channel_2['channel_id'], user_1['u_id'])
    with pytest.raises(AccessError):
        channel.channel_addowner(user_2['token'], public_channel_1['channel_id'], user_2['u_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_output_user_addowner_private(user_1, user_2, private_channel_1):
    """Testing if the user has successfully been added as owner of the channel (private)
    """
    # Make a private channel
    channel.channel_addowner(user_1['token'], private_channel_1['channel_id'], user_2['u_id'])

    channel_data = channel.channel_details(user_2['token'], private_channel_1['channel_id'])
    user_2_details = {'name_first': 'Jane', 'name_last': 'Smith', 'u_id': user_2['u_id']}
    assert user_2_details in channel_data['all_members']
    assert user_2_details in channel_data['owner_members']
    clear()

def test_output_user_addowner_public(user_1, user_2, public_channel_1):
    """Testing if the user has successfully been added as owner of the channel (public)
    """
    channel.channel_addowner(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    channel_data = channel.channel_details(user_2['token'], public_channel_1['channel_id'])
    user_2_details = {'name_first': 'Jane', 'name_last': 'Smith', 'u_id': user_2['u_id']}
    assert user_2_details in channel_data['all_members']
    assert user_2_details in channel_data['owner_members']
    clear()

def test_output_member_becomes_channel_owner(user_1, user_2, public_channel_1):
    """Testing if the user has become a channel owner from a channel member
    """
    user_2_details = {'name_first': 'Jane', 'name_last': 'Smith', 'u_id': user_2['u_id']}
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])
    channel_data = channel.channel_details(user_2['token'], public_channel_1['channel_id'])
    assert user_2_details in channel_data['all_members']
    assert user_2_details not in channel_data['owner_members']
    channel.channel_addowner(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    channel_data = channel.channel_details(user_2['token'], public_channel_1['channel_id'])
    assert user_2_details in channel_data['all_members']
    assert user_2_details in channel_data['owner_members']
    clear()

#------------------------------------------------------------------------------#
#                                channel_removeowner                           #
#------------------------------------------------------------------------------#

#?------------------------- Input/Access Error Testing -----------------------?#

def test_input_removeowner(user_1, user_2):
    """Testing when Channel ID is not a valid channel
    """
    with pytest.raises(InputError):
        channel.channel_removeowner(user_1['token'], -1, user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_removeowner(user_1['token'], 0, user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_removeowner(user_1['token'], 1, user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_removeowner(user_1['token'], 5, user_2['u_id'])
    clear()

def test_access_remove_valid_token(user_1, user_2, public_channel_1):
    """Testing if token is valid
    """
    channel.channel_addowner(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    auth.auth_logout(user_1['token'])
    with pytest.raises(AccessError):
        channel.channel_removeowner(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    clear()

def test_input_u_id_removeowner(user_1, public_channel_1):
    """Testing when u_id is not a valid u_id
    """
    with pytest.raises(InputError):
        channel.channel_removeowner(user_1['token'], public_channel_1['channel_id'], user_1['u_id'] + 1)
    with pytest.raises(InputError):
        channel.channel_removeowner(user_1['token'], public_channel_1['channel_id'], user_1['u_id'] - 1)
    with pytest.raises(InputError):
        channel.channel_removeowner(user_1['token'], public_channel_1['channel_id'], user_1['u_id'] + 7)
    clear()

def test_remove_user_is_not_owner(user_1, user_2, user_3, public_channel_1, public_channel_2):
    """Testing when user with user id u_id is not an owner of the channel
    """
    with pytest.raises(InputError):
        channel.channel_removeowner(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_removeowner(user_2['token'], public_channel_2['channel_id'], user_3['u_id'])
    clear()

def test_remove_user_is_owner(user_1, user_2, public_channel_1, public_channel_2):
    """Testing when the authorised user is not an owner of the flockr, or an owner of this channel
    """

    with pytest.raises(AccessError):
        channel.channel_removeowner(user_2['token'], public_channel_1['channel_id'], user_1['u_id'])
    with pytest.raises(AccessError):
        channel.channel_removeowner(user_1['token'], public_channel_2['channel_id'], user_2['u_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_output_user_removeowner_private(user_1, user_2, private_channel_1):
    """Testing if the user has successfully been removed as owner of the channel (private)
    """
    channel.channel_addowner(user_1['token'], private_channel_1['channel_id'], user_2['u_id'])

    channel_data = channel.channel_details(user_2['token'], private_channel_1['channel_id'])
    channel.channel_removeowner(user_1['token'], private_channel_1['channel_id'], user_2['u_id'])
    for curr_owner in channel_data['owner_members']:
        assert curr_owner['u_id'] is not user_2['u_id']
    clear()

def test_output_user_removeowner_public(user_1, user_2, public_channel_1):
    """Testing if the user has successfully been removed as owner of the channel (public)
    """
    channel.channel_addowner(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])

    channel_data = channel.channel_details(user_2['token'], public_channel_1['channel_id'])
    channel.channel_removeowner(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    for curr_owner in channel_data['owner_members']:
        assert curr_owner['u_id'] is not user_2['u_id']
    clear()
