"""
channel feature test implementation to test functions in channel.py

Feature implementation was written by Gabriel Ting, Tam Do, Prathamesh Jagtap.

2020 T3 COMP1531 Major Project
"""
from datetime import datetime, timezone
import pytest
import auth
import channel
import channels
from message import message_send
from other import clear
from error import InputError, AccessError

#------------------------------------------------------------------------------#
#                               channel_invite                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_channel_invite_login_user():
    """Testing invalid token for users which have logged out
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    user_4 = auth.auth_register('prathsjag@gmail.com', 'password', 'Praths', 'Jag')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    auth.auth_logout(user_1['token'])
    auth.auth_logout(user_2['token'])
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])

    with pytest.raises(AccessError):
        channel.channel_invite(user_1['token'], new_channel['channel_id'], user_1['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(user_2['token'], new_channel['channel_id'], user_3['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(user_3['token'], new_channel['channel_id'], user_3['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(user_4['token'], new_channel['channel_id'], user_3['u_id'])
    clear()

def test_channel_invite_wrong_data_type():
    """Testing when wrong data types are used as input
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)

    with pytest.raises(InputError):
        channel.channel_invite(user['token'], new_channel['channel_id'], -1)
    with pytest.raises(InputError):
        channel.channel_invite(user['token'], new_channel['channel_id'], '@#$!')
    with pytest.raises(InputError):
        channel.channel_invite(user['token'], new_channel['channel_id'], 67.666)
    clear()

def test_channel_invite_invalid_user():
    """Testing when invalid user is invited to channel
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)

    with pytest.raises(InputError):
        channel.channel_invite(user['token'], new_channel['channel_id'], user['u_id'] + 1)
    with pytest.raises(InputError):
        channel.channel_invite(user['token'], new_channel['channel_id'], user['u_id'] - 1)
    clear()

def test_channel_invite_invalid_channel():
    """Testing when valid user is invited to invalid channel
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')

    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], -122, user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], -642, user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], '@#@!', user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], 212.11, user_2['u_id'])
    clear()

def test_channel_invite_not_authorized():
    """Testing when user is not authorized to invite other users to channel
    (Assumption) This includes an invalid user inviting users to channel
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    auth.auth_logout(user_1['token'])

    with pytest.raises(AccessError):
        channel.channel_invite(12, new_channel['channel_id'], user_3['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(-12, new_channel['channel_id'], user_3['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(121.11, new_channel['channel_id'], user_3['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(user_2['token'], new_channel['channel_id'], user_1['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(user_2['token'], new_channel['channel_id'], user_3['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(user_1['token'], new_channel['channel_id'], user_3['u_id'])
    clear()

def test_channel_invite_invalid_self_invite():
    """Testing when user is not allowed to invite him/herself to channel
    (Assumption testing) this error will be treated as AccessError
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)

    with pytest.raises(InputError):
        channel.channel_invite(user['token'], new_channel['channel_id'], user['u_id'])
    clear()

def test_channel_multiple_invite():
    """Testing when user invites a user multiple times
    (Assumption testing) this error will be treated as AccessError
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    assert channel.channel_invite(user_1['token'], new_channel['channel_id'], user_2['u_id']) == {}

    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], new_channel['channel_id'], user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_invite(user_2['token'], new_channel['channel_id'], user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_invite(user_2['token'], new_channel['channel_id'], user_1['u_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_channel_invite_successful():
    """Testing if user has successfully been invited to the channel
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    user_4 = auth.auth_register('prathsjag@gmail.com', 'password', 'Praths', 'Jag')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)

    channel.channel_invite(user_1['token'], new_channel['channel_id'], user_2['u_id'])
    assert channel.channel_details(user_1['token'], new_channel['channel_id']) == {
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
                'name_first': 'Jennie',
                'name_last': 'Lin',
            },
        ],
    }

    channel.channel_invite(user_2['token'], new_channel['channel_id'], user_3['u_id'])
    assert channel.channel_details(user_1['token'], new_channel['channel_id']) == {
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
                'name_first': 'Jennie',
                'name_last': 'Lin',
            },
            {
                'u_id': user_3['u_id'],
                'name_first': 'John',
                'name_last': 'Perry',
            },
        ],
    }

    channel.channel_invite(user_1['token'], new_channel['channel_id'], user_4['u_id'])
    assert channel.channel_details(user_1['token'], new_channel['channel_id']) == {
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
                'name_first': 'Jennie',
                'name_last': 'Lin',
            },
            {
                'u_id': user_3['u_id'],
                'name_first': 'John',
                'name_last': 'Perry',
            },
            {
                'u_id': user_4['u_id'],
                'name_first': 'Praths',
                'name_last': 'Jag',
            },
        ],
    }
    clear()

def test_channel_invite_flockr_user():
    """(Assumption testing) first person to register is flockr owner
    Testing if flockr owner has been successfully invited to channel and given ownership
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    new_channel = channels.channels_create(user_2['token'], 'Group 1', False)

    channel.channel_invite(user_2['token'], new_channel['channel_id'], user_3['u_id'])
    assert channel.channel_details(user_2['token'], new_channel['channel_id']) == {
        'name': 'Group 1',
        'owner_members': [
            {
                'u_id': user_2['u_id'],
                'name_first': 'Jennie',
                'name_last': 'Lin',
            },
        ],
        'all_members': [
            {
                'u_id': user_2['u_id'],
                'name_first': 'Jennie',
                'name_last': 'Lin',
            },
            {
                'u_id': user_3['u_id'],
                'name_first': 'John',
                'name_last': 'Perry',
            },
        ],
    }

    channel.channel_invite(user_3['token'], new_channel['channel_id'], user_1['u_id'])
    assert channel.channel_details(user_1['token'], new_channel['channel_id']) == {
        'name': 'Group 1',
        'owner_members': [
            {
                'u_id': user_2['u_id'],
                'name_first': 'Jennie',
                'name_last': 'Lin',
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
                'name_first': 'Jennie',
                'name_last': 'Lin',
            },
            {
                'u_id': user_3['u_id'],
                'name_first': 'John',
                'name_last': 'Perry',
            },
            {
                'u_id': user_1['u_id'],
                'name_first': 'John',
                'name_last': 'Smith',
            },
        ],
    }
    clear()

def test_output_invite_user_list():
    """Testing if channel info has been added to user profile when added
    """
    clear()
    channel_name = 'Group 1'
    channel_public = True
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    new_channel = channels.channels_create(user_1['token'], channel_name, channel_public)
    channel.channel_invite(user_1['token'], new_channel['channel_id'], user_2['u_id'])

    channel_list = channels.channels_list(user_1['token'])
    on_list = False
    for item in channel_list['channels']:
        if item['channel_id'] == new_channel['channel_id']:
            on_list = True
            break
    assert on_list

    channel_list = channels.channels_list(user_2['token'])
    on_list = False
    for curr_channel in channel_list['channels']:
        if curr_channel['channel_id'] == new_channel['channel_id']:
            on_list = True
            break
    assert on_list
    clear()

#------------------------------------------------------------------------------#
#                               channel_details                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_channel_details_invalid_channel():
    """Testing if channel is invalid or does not exist
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')

    with pytest.raises(InputError):
        channel.channel_details(user['token'], -1)
    with pytest.raises(InputError):
        channel.channel_details(user['token'], -19)
    with pytest.raises(InputError):
        channel.channel_details(user['token'], '#@&!')
    with pytest.raises(InputError):
        channel.channel_details(user['token'], 121.12)
    clear()

def test_channel_details_invalid_user():
    """Testing if unauthorized/invalid user is unable to access channel details
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)

    with pytest.raises(AccessError):
        channel.channel_details(user_2['token'], new_channel['channel_id'])
    clear()

def test_channel_details_invalid_token():
    """Testing if given invalid token returns an AccessError
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)

    with pytest.raises(AccessError):
        channel.channel_details(6.333, 0)
    with pytest.raises(AccessError):
        channel.channel_details('@^!&', -3)
    with pytest.raises(AccessError):
        channel.channel_details(-1, new_channel['channel_id'])
    with pytest.raises(AccessError):
        channel.channel_details('abcd', new_channel['channel_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_channel_details_authorized_user():
    """Testing the required correct details of a channel
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    user_4 = auth.auth_register('prathsjag@gmail.com', 'password', 'Praths', 'Jag')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)

    channel.channel_invite(user_1['token'], new_channel['channel_id'], user_2['u_id'])
    assert channel.channel_details(user_1['token'], new_channel['channel_id']) == {
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
                'name_first': 'Jennie',
                'name_last': 'Lin',
            },
        ],
    }

    channel.channel_invite(user_2['token'], new_channel['channel_id'], user_3['u_id'])
    assert channel.channel_details(user_1['token'], new_channel['channel_id']) == {
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
                'name_first': 'Jennie',
                'name_last': 'Lin',
            },
            {
                'u_id': user_3['u_id'],
                'name_first': 'John',
                'name_last': 'Perry',
            },
        ],
    }

    channel.channel_invite(user_1['token'], new_channel['channel_id'], user_4['u_id'])
    assert channel.channel_details(user_1['token'], new_channel['channel_id']) == {
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
                'name_first': 'Jennie',
                'name_last': 'Lin',
            },
            {
                'u_id': user_3['u_id'],
                'name_first': 'John',
                'name_last': 'Perry',
            },
            {
                'u_id': user_4['u_id'],
                'name_first': 'Praths',
                'name_last': 'Jag',
            },
        ],
    }
    clear()


def test_output_details_twice():
    """Test if details will be shown when a second channel is created.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    channels.channels_create(user_1['token'], 'Group 1', user_1['u_id'])
    new_channel_2 = channels.channels_create(user_1['token'], 'Group 2', user_1['u_id'])
    channel.channel_invite(user_1['token'], new_channel_2['channel_id'], user_2['u_id'])
    assert channel.channel_details(user_1['token'], new_channel_2['channel_id']) == {
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
            {
                'u_id': user_2['u_id'],
                'name_first': 'Jennie',
                'name_last': 'Lin',
            },
        ],
    }
    clear()

#------------------------------------------------------------------------------#
#                               channel_messages                               #
#------------------------------------------------------------------------------#

# Helper function to send messages
def create_messages(user, channel_id, i, j):
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
        message_info = message_send(user['token'], channel_id, f"{index}")
        result.append({
            'message_id': message_info['message_id'],
            'u_id': user['u_id'],
            'message': f"{index}",
            'time_created': time,
        })
    return result

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_input_messages_channel_id():
    """Testing when an invalid channel_id is used as a parameter
    """
    clear()
    start = 0
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')

    with pytest.raises(InputError):
        channel.channel_messages(user['token'], -1, start)
    with pytest.raises(InputError):
        channel.channel_messages(user['token'], 0, start)
    with pytest.raises(InputError):
        channel.channel_messages(user['token'], 1, start)
    with pytest.raises(InputError):
        channel.channel_messages(user['token'], 5, start)
    clear()

def test_input_messages_start():
    """Testing when start is an invalid start value. Start is greater than the
    total number of messages in the channel.
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    with pytest.raises(InputError):
        channel.channel_messages(user['token'], new_channel['channel_id'], 1)
    with pytest.raises(InputError):
        channel.channel_messages(user['token'], new_channel['channel_id'], 10)
    with pytest.raises(InputError):
        channel.channel_messages(user['token'], new_channel['channel_id'], -1)
    clear()

def test_input_messages_start_equal_1():
    """Testing when start index is equal to the total number of messages, it will
    instead raise an InputError (assumption).
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    create_messages(user, new_channel['channel_id'], 0, 1)
    with pytest.raises(InputError):
        channel.channel_messages(user['token'], new_channel['channel_id'], 1)
    clear()

def test_input_messages_start_equal_10():
    """Testing when start index is equal to the total number of messages, it will
    instead raise an InputError (assumption).
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    create_messages(user, new_channel['channel_id'], 0, 10)
    with pytest.raises(InputError):
        channel.channel_messages(user['token'], new_channel['channel_id'], 10)
    clear()

def test_access_messages_user_is_member():
    """Testing if another user can access the channel
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    new_channel_1 = channels.channels_create(user_1['token'], 'Group 1', True)
    new_channel_2 = channels.channels_create(user_2['token'], 'Group 2', True)

    with pytest.raises(AccessError):
        channel.channel_messages(user_1['token'], new_channel_2['channel_id'], 0)
    with pytest.raises(AccessError):
        channel.channel_messages(user_2['token'], new_channel_1['channel_id'], 0)
    clear()

def test_access_messages_valid_token():
    """Testing if token is valid
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    auth.auth_logout(user['token'])

    with pytest.raises(AccessError):
        channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    clear()
#?------------------------------ Output Testing ------------------------------?#

#! Testing when a channel has no messages
def test_output_no_messages():
    """Testing when a channel has no messages
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    assert result['messages'] == []
    assert result['start'] == -1
    assert result['end'] == -1
    clear()

#! Testing when a channel less than 50 messages
def test_output_messages_1():
    """Testing when a channel has a single message
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message_list = create_messages(user, new_channel['channel_id'], 0, 1)
    assert len(message_list) == 1
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    assert result['messages'] == message_list
    assert len(result['messages']) == 1
    assert result['start'] == 0
    assert result['end'] == -1
    clear()

def test_output_messages_10_start_0():
    """Testing when a channel has 10 messages at start 0.
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message_list = create_messages(user, new_channel['channel_id'], 0, 10)
    assert len(message_list) == 10
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    assert result['messages'] == message_list
    assert len(result['messages']) == 10
    assert result['start'] == 0
    assert result['end'] == -1
    clear()

def test_output_messages_10_start_5():
    """Testing when a channel has 10 messages at start 5.
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message_list = create_messages(user, new_channel['channel_id'], 0, 10)
    assert len(message_list) == 10
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 5)
    assert result['messages'] == message_list[5:]
    assert len(result['messages']) == 5
    assert result['start'] == 5
    assert result['end'] == -1
    clear()

def test_output_messages_49_start_0():
    """Testing when a channel has 49 total messages at start 0.
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message_list = create_messages(user, new_channel['channel_id'], 0, 49)
    assert len(message_list) == 49
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    assert result['messages'] == message_list
    assert len(result['messages']) == 49
    assert result['start'] == 0
    assert result['end'] == -1
    clear()

def test_output_messages_49_start_25():
    """Testing when a channel has 49 total messages at start 25.
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message_list = create_messages(user, new_channel['channel_id'], 0, 49)
    assert len(message_list) == 49
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 25)
    assert result['messages'] == message_list[25:]
    assert len(result['messages']) == 24
    assert result['start'] == 25
    assert result['end'] == -1
    clear()

#! Testing when a channel less than 50 messages
def test_output_messages_50_start_0():
    """Testing when a channel has 50 total messages at start 0.
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message_list = create_messages(user, new_channel['channel_id'], 0, 50)
    assert len(message_list) == 50
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    assert result['messages'] == message_list
    assert len(result['messages']) == 50
    assert result['start'] == 0
    assert result['end'] == -1
    clear()

def test_output_messages_50_start_25():
    """Testing when a channel has 50 total messages at start 25.
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message_list = create_messages(user, new_channel['channel_id'], 0, 50)
    assert len(message_list) == 50
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 25)
    assert result['messages'] == message_list[25:]
    assert len(result['messages']) == 25
    assert result['start'] == 25
    assert result['end'] == -1
    clear()

def test_output_messages_50_start_49():
    """Testing when a channel has 50 total messages at start 49.
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message_list = create_messages(user, new_channel['channel_id'], 0, 50)
    assert len(message_list) == 50
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 49)
    assert result['messages'] == message_list[49:]
    assert len(result['messages']) == 1
    assert result['start'] == 49
    assert result['end'] == -1
    clear()

#! Testing when a channel has more than 50 messages
def test_output_messages_51_start_0():
    """Testing when a channel has 51 total messages at start 0.
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message_list = create_messages(user, new_channel['channel_id'], 0, 51)
    assert len(message_list) == 51
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    assert result['messages'] == message_list[0:50]
    assert len(result['messages']) == 50
    assert result['start'] == 0
    assert result['end'] == 50
    clear()

def test_output_messages_51_start_25():
    """Testing when a channel has 51 total messages at start 25.
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message_list = create_messages(user, new_channel['channel_id'], 0, 51)
    assert len(message_list) == 51
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 25)
    assert result['messages'] == message_list[25:]
    assert len(result['messages']) == 26
    assert result['start'] == 25
    assert result['end'] == -1
    clear()

def test_output_messages_51_start_50():
    """Testing when a channel has 51 total messages at start 50.
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message_list = create_messages(user, new_channel['channel_id'], 0, 51)
    assert len(message_list) == 51
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 50)
    assert result['messages'] == message_list[50:]
    assert len(result['messages']) == 1
    assert result['start'] == 50
    assert result['end'] == -1
    clear()

def test_output_messages_100_start_10():
    """Testing when a channel has 100 total messages at start 10.
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message_list = create_messages(user, new_channel['channel_id'], 0, 100)
    assert len(message_list) == 100
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 10)
    assert result['messages'] == message_list[10:60]
    assert len(result['messages']) == 50
    assert result['start'] == 10
    assert result['end'] == 60
    clear()

#! Testing using examples provided in specification (refer to 6.5. Pagination)
def test_output_messages_125_start_0():
    """Testing when a channel has 125 total messages at start 0.
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message_list = create_messages(user, new_channel['channel_id'], 0, 125)
    assert len(message_list) == 125
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    assert result['messages'] == message_list[0:50]
    assert len(result['messages']) == 50
    assert result['start'] == 0
    assert result['end'] == 50
    clear()

def test_output_messages_125_start_50():
    """Testing when a channel has 125 total messages at start 50.
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message_list = create_messages(user, new_channel['channel_id'], 0, 125)
    assert len(message_list) == 125
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 50)
    assert result['messages'] == message_list[50:100]
    assert len(result['messages']) == 50
    assert result['start'] == 50
    assert result['end'] == 100
    clear()

def test_output_messages_125_start_100():
    """Testing when a channel has 125 total messages at start 100.
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    message_list = create_messages(user, new_channel['channel_id'], 0, 125)
    assert len(message_list) == 125
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 100)
    assert result['messages'] == message_list[100:]
    assert len(result['messages']) == 25
    assert result['start'] == 100
    assert result['end'] == -1
    clear()

#------------------------------------------------------------------------------#
#                               channel_leave                                  #
#------------------------------------------------------------------------------#

#?------------------------- Input/Access Error Testing -----------------------?#

def test_input_leave_channel_id():
    """Testing when an invalid channel_id is used as a parameter
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    with pytest.raises(InputError):
        channel.channel_leave(user['token'], -1)
    with pytest.raises(InputError):
        channel.channel_leave(user['token'], 0)
    with pytest.raises(InputError):
        channel.channel_leave(user['token'], 1)
    with pytest.raises(InputError):
        channel.channel_leave(user['token'], 5)
    clear()

def test_access_leave_user_is_member():
    """Testing if a user was not in the channel initially
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    new_channel_1 = channels.channels_create(user_1['token'], 'Group 1', True)
    new_channel_2 = channels.channels_create(user_2['token'], 'Group 2', True)

    with pytest.raises(AccessError):
        channel.channel_leave(user_1['token'], new_channel_2['channel_id'])
    with pytest.raises(AccessError):
        channel.channel_leave(user_2['token'], new_channel_1['channel_id'])
    clear()

def test_access_leave_valid_token():
    """Testing if token is valid
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    auth.auth_logout(user['token'])

    with pytest.raises(AccessError):
        channel.channel_leave(user['token'], new_channel['channel_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_output_user_leave_public():
    """Testing if the user has successfully left a public channel
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    channel_leave = channels.channels_create(user['token'], 'Group 1', True)
    channel.channel_leave(user['token'], channel_leave['channel_id'])
    channel_list = channels.channels_list(user['token'])
    assert channel_list['channels'] == []
    clear()

def test_output_user_leave_private():
    """Testing if the user has successfully left a private channel
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    channel_leave = channels.channels_create(user['token'], 'Group 1', False)
    channel.channel_leave(user['token'], channel_leave['channel_id'])

    channel_list = channels.channels_list(user['token'])
    assert channel_list['channels'] == []
    clear()

def test_output_user_leave_channels():
    """Testing if user has left the correct channel.
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')

    # Create new channels.
    channel_1 = channels.channels_create(user['token'], 'Group 1', True)
    channel_2 = channels.channels_create(user['token'], 'Group 2', True)
    channel_3 = channels.channels_create(user['token'], 'Group 3', False)

    channel.channel_leave(user['token'], channel_1['channel_id'])
    assert channels.channels_list(user['token']) == {
        'channels': [
            {
                'channel_id': channel_2['channel_id'],
                'name': 'Group 2',
            },
            {
                'channel_id': channel_3['channel_id'],
                'name': 'Group 3',
            },
        ],
    }
    clear()

def test_output_leave_channels():
    """Testing when user leaves multiple channels
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')

    channel_leave_1 = channels.channels_create(user_1['token'], 'Group 1', False)
    channel.channel_leave(user_1['token'], channel_leave_1['channel_id'])
    channel_leave_2 = channels.channels_create(user_2['token'], 'Group 1', True)
    channel.channel_addowner(user_2['token'], channel_leave_2['channel_id'], user_1['u_id'])
    channel.channel_leave(user_1['token'], channel_leave_2['channel_id'])

    channel_list = channels.channels_list(user_1['token'])
    assert channel_list['channels'] == []
    clear()

def test_output_member_leave():
    """Testing when a member leaves that it does not delete the channel.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    user_3 = auth.auth_register('jacesmith@gmail.com', 'password', 'Jace', 'Smith')

    channel_leave = channels.channels_create(user_1['token'], 'Group 1', False)
    channel.channel_invite(user_1['token'], channel_leave['channel_id'], user_2['u_id'])
    channel.channel_invite(user_1['token'], channel_leave['channel_id'], user_3['u_id'])

    channel.channel_leave(user_3['token'], channel_leave['channel_id'])
    channel_leave_details = channel.channel_details(user_1['token'], channel_leave['channel_id'])
    for member in channel_leave_details['all_members']:
        assert member['u_id'] != user_3['u_id']
    clear()


def test_output_all_owners_leave():
    """Testing Process: Tests suite that is designed to test the process of all
    owners leaving in which the user with the lowest u_id in the channel becomes
    the owner automatically.
    Covers also if user access has been erased on channel end.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    user_3 = auth.auth_register('jacesmith@gmail.com', 'password', 'Jace', 'Smith')
    user_4 = auth.auth_register('janicesmith@gmail.com', 'password', 'Janice', 'Smith')

    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    channel.channel_addowner(user_1['token'], new_channel['channel_id'], user_2['u_id'])
    channel.channel_invite(user_1['token'], new_channel['channel_id'], user_3['u_id'])
    channel.channel_invite(user_1['token'], new_channel['channel_id'], user_4['u_id'])

    # When the first owner leaves
    channel.channel_leave(user_1['token'], new_channel['channel_id'])

    # Confirm that there is now one owner in the channel
    channel_data = channel.channel_details(user_2['token'], new_channel['channel_id'])
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
    channel.channel_leave(user_2['token'], new_channel['channel_id'])
    channel_data = channel.channel_details(user_3['token'], new_channel['channel_id'])

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
        assert curr_channel['channel_id'] is not new_channel['channel_id']

    channel_list = channels.channels_list(user_2['token'])
    for curr_channel in channel_list['channels']:
        assert curr_channel['channel_id'] is not new_channel['channel_id']

    clear()

def test_output_all_members_leave():
    """Test if the channel is deleted when all members leave
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')

    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    channel.channel_invite(user_1['token'], new_channel['channel_id'], user_2['u_id'])

    channel.channel_leave(user_1['token'], new_channel['channel_id'])
    channel.channel_leave(user_2['token'], new_channel['channel_id'])

    all_channels = channels.channels_listall(user_1['token'])
    for curr_channel in all_channels['channels']:
        assert curr_channel['channel_id'] != new_channel['channel_id']

    clear()

def test_output_flockr_rejoin_channel():
    """Test when the flockr owner leaves and comes back that the user status is an
    owner.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')

    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)

    channel.channel_invite(user_1['token'], new_channel['channel_id'], user_2['u_id'])
    channel.channel_leave(user_1['token'], new_channel['channel_id'])
    channel.channel_join(user_1['token'], new_channel['channel_id'])
    new_channel_details = channel.channel_details(user_2['token'], new_channel['channel_id'])
    user_1_details = {'u_id': user_1['u_id'], 'name_first': 'John', 'name_last': 'Smith'}
    assert user_1_details in new_channel_details['owner_members']
    assert user_1_details in new_channel_details['all_members']

    clear()

def test_output_creator_rejoin_channel():
    """Test when the the creator leaves and comes back that the user status is a member.
    """
    clear()
    auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    user_3 = auth.auth_register('jacesmith@gmail.com', 'password', 'Jace', 'Smith')

    new_channel = channels.channels_create(user_2['token'], 'Group 1', True)

    channel.channel_invite(user_2['token'], new_channel['channel_id'], user_3['u_id'])
    channel.channel_leave(user_2['token'], new_channel['channel_id'])
    channel.channel_join(user_2['token'], new_channel['channel_id'])
    new_channel_details = channel.channel_details(user_2['token'], new_channel['channel_id'])
    user_2_details = {'u_id': user_2['u_id'], 'name_first': 'Jane', 'name_last': 'Smith'}
    assert user_2_details not in new_channel_details['owner_members']
    assert user_2_details in new_channel_details['all_members']

    clear()

#------------------------------------------------------------------------------#
#                                   channel_join                               #
#------------------------------------------------------------------------------#

#?------------------------- Input/Access Error Testing -----------------------?#

def test_input_join_channel_id():
    """Testing when Channel ID is not a valid channel
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    with pytest.raises(InputError):
        channel.channel_join(user['token'], -1)
    with pytest.raises(InputError):
        channel.channel_join(user['token'], 0)
    with pytest.raises(InputError):
        channel.channel_join(user['token'], 1)
    with pytest.raises(InputError):
        channel.channel_join(user['token'], 5)
    clear()

def test_access_join_valid_token():
    """Testing if token is valid
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    auth.auth_logout(user['token'])

    with pytest.raises(AccessError):
        channel.channel_join(user['token'], new_channel['channel_id'])
    clear()

def test_access_join_user_is_member():
    """Testing if channel_id refers to a channel that is private (when the
    authorised user is not a global owner)
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    user_3 = auth.auth_register('jonesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Channel is private
    new_channel_1 = channels.channels_create(user_1['token'], 'Group 1', False)
    new_channel_2 = channels.channels_create(user_2['token'], 'Group 2', False)

    with pytest.raises(AccessError):
        channel.channel_join(user_3['token'], new_channel_2['channel_id'])
    with pytest.raises(AccessError):
        channel.channel_join(user_2['token'], new_channel_1['channel_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_output_user_join_public():
    """Testing if the user has successfully joined a public channel
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Make a public channel and join user_2
    channel_join = channels.channels_create(user_1['token'], 'Group 1', True)
    channel.channel_join(user_2['token'], channel_join['channel_id'])

    # Check channel details if the user is a member
    channel_data = channel.channel_details(user_2['token'], channel_join['channel_id'])
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

def test_output_user_join_flockr_private():
    """Test for flockr owner (flockr owner can join private channels)
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Make a private channel and check if flockr owner
    channel_join = channels.channels_create(user_2['token'], 'Private Group 1', False)

    # Assume that the first user is the flockr owner
    channel.channel_join(user_1['token'], channel_join['channel_id'])
    channel_list = channels.channels_list(user_2['token'])

    # Check if flockr owner is in channel list
    in_channel = False
    for curr_channel in channel_list['channels']:
        if curr_channel['channel_id'] == channel_join['channel_id']:
            in_channel = True
            break
    assert in_channel
    clear()

def test_output_user_join_flockr_member_list():
    """Test for flockr owner (flockr owner can join private channels)
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Make a private channel and check if flockr owner
    channel_join = channels.channels_create(user_2['token'], 'Private Group 1', False)

    # Assume that the first user is the flockr owner
    channel.channel_join(user_1['token'], channel_join['channel_id'])

    # Check if flockr owner is a channel member
    channel_data = channel.channel_details(user_2['token'], channel_join['channel_id'])
    is_member = False
    for member in channel_data['all_members']:
        if member['u_id'] == user_1['u_id']:
            is_member = True
            break
    assert is_member
    clear()

def test_output_user_join_flockr_owner_list():
    """Test for flockr owner (flockr owner can join private channels)
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Make a private channel and check if flockr owner
    channel_join = channels.channels_create(user_2['token'], 'Private Group 1', False)

    # Assume that the first user is the flockr owner
    channel.channel_join(user_1['token'], channel_join['channel_id'])

    # Flockr owner becomes owner after channel join
    owner = True
    channel_data = channel.channel_details(user_1['token'], channel_join['channel_id'])
    for member in channel_data['owner_members']:
        if member['u_id'] == user_1['u_id']:
            owner = False
    assert not owner
    clear()

def test_output_user_join_again():
    """Test for a person joining again
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', False)
    channel_data = channel.channel_details(user['token'], new_channel['channel_id'])
    user_details = {'name_first': 'John', 'name_last': 'Smith', 'u_id': user['u_id']}
    assert user_details in channel_data['all_members']
    channel.channel_join(user['token'], new_channel['channel_id'])
    # Check channel details if the user is a member
    channel_data = channel.channel_details(user['token'], new_channel['channel_id'])
    assert user_details in channel_data['all_members']
    # Check if channel appears in the user's channels list
    channel_user_list = channels.channels_list(user['token'])
    assert len(channel_user_list) == 1
    clear()

#------------------------------------------------------------------------------#
#                                channel_addowner                              #
#------------------------------------------------------------------------------#

#?------------------------- Input/Access Error Testing -----------------------?#

def test_input_channel_id_addowner():
    """Testing when Channel ID is not a valid channel
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    with pytest.raises(InputError):
        channel.channel_addowner(user['token'], -1, user['u_id'])
    with pytest.raises(InputError):
        channel.channel_addowner(user['token'], 0, user['u_id'])
    with pytest.raises(InputError):
        channel.channel_addowner(user['token'], 1, user['u_id'])
    with pytest.raises(InputError):
        channel.channel_addowner(user['token'], 5, user['u_id'])
    clear()

def test_access_add_valid_token():
    """Testing if token is valid
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    auth.auth_logout(user['token'])

    with pytest.raises(AccessError):
        channel.channel_addowner(user['token'], new_channel['channel_id'], user['u_id'])
    clear()

def test_input_u_id_addowner():
    """Testing when u_id is not a valid u_id
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', False)
    with pytest.raises(InputError):
        channel.channel_addowner(user['token'], new_channel['channel_id'], -1)
    with pytest.raises(InputError):
        channel.channel_addowner(user['token'], new_channel['channel_id'], 0)
    with pytest.raises(InputError):
        channel.channel_addowner(user['token'], new_channel['channel_id'], 5)
    with pytest.raises(InputError):
        channel.channel_addowner(user['token'], new_channel['channel_id'], 7)
    clear()

def test_add_user_is_already_owner():
    """Testing when user with user id u_id is already an owner of the channel
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Channel is private (creators are already owners)
    new_channel_1 = channels.channels_create(user_1['token'], 'Group 1', False)
    new_channel_2 = channels.channels_create(user_2['token'], 'Group 2', False)

    with pytest.raises(InputError):
        channel.channel_addowner(user_1['token'], new_channel_1['channel_id'], user_1['u_id'])
    with pytest.raises(InputError):
        channel.channel_addowner(user_2['token'], new_channel_2['channel_id'], user_2['u_id'])
    clear()

def test_auth_user_is_not_owner():
    """Testing when the authorised user is not an owner of the flockr, or an owner of this channel
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # User_1 is owner of new_channel_1 and User_2 is the owner of new_channel_2
    new_channel_1 = channels.channels_create(user_1['token'], 'Group 1', False)
    new_channel_2 = channels.channels_create(user_2['token'], 'Group 2', False)

    with pytest.raises(AccessError):
        channel.channel_addowner(user_1['token'], new_channel_2['channel_id'], user_1['u_id'])
    with pytest.raises(AccessError):
        channel.channel_addowner(user_2['token'], new_channel_1['channel_id'], user_2['u_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_output_user_addowner_private():
    """Testing if the user has successfully been added as owner of the channel (private)
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Make a private channel
    channel_join = channels.channels_create(user_1['token'], 'Group 1', False)
    channel.channel_addowner(user_1['token'], channel_join['channel_id'], user_2['u_id'])

    channel_data = channel.channel_details(user_2['token'], channel_join['channel_id'])
    user_2_details = {'name_first': 'Jane', 'name_last': 'Smith', 'u_id': user_2['u_id']}
    assert user_2_details in channel_data['all_members']
    assert user_2_details in channel_data['owner_members']
    clear()

def test_output_user_addowner_public():
    """Testing if the user has successfully been added as owner of the channel (public)
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Make a public channel
    channel_join = channels.channels_create(user_1['token'], 'Group 1', True)
    channel.channel_addowner(user_1['token'], channel_join['channel_id'], user_2['u_id'])

    channel_data = channel.channel_details(user_2['token'], channel_join['channel_id'])
    user_2_details = {'name_first': 'Jane', 'name_last': 'Smith', 'u_id': user_2['u_id']}
    assert user_2_details in channel_data['all_members']
    assert user_2_details in channel_data['owner_members']
    clear()

def test_output_member_becomes_channel_owner():
    """Testing if the user has become a channel owner from a channel member
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Make a public channel
    channel_join = channels.channels_create(user_1['token'], 'Group 1', True)
    user_2_details = {'name_first': 'Jane', 'name_last': 'Smith', 'u_id': user_2['u_id']}
    channel.channel_join(user_2['token'], channel_join['channel_id'])
    channel_data = channel.channel_details(user_2['token'], channel_join['channel_id'])
    assert user_2_details in channel_data['all_members']
    assert user_2_details not in channel_data['owner_members']
    channel.channel_addowner(user_1['token'], channel_join['channel_id'], user_2['u_id'])
    channel_data = channel.channel_details(user_2['token'], channel_join['channel_id'])
    assert user_2_details in channel_data['all_members']
    assert user_2_details in channel_data['owner_members']
    clear()

#------------------------------------------------------------------------------#
#                                channel_removeowner                           #
#------------------------------------------------------------------------------#

#?------------------------- Input/Access Error Testing -----------------------?#

def test_input_removeowner():
    """Testing when Channel ID is not a valid channel
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    with pytest.raises(InputError):
        channel.channel_removeowner(user['token'], -1, user['u_id'])
    with pytest.raises(InputError):
        channel.channel_removeowner(user['token'], 0, user['u_id'])
    with pytest.raises(InputError):
        channel.channel_removeowner(user['token'], 1, user['u_id'])
    with pytest.raises(InputError):
        channel.channel_removeowner(user['token'], 5, user['u_id'])
    clear()

def test_access_remove_valid_token():
    """Testing if token is valid
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    auth.auth_logout(user['token'])

    with pytest.raises(AccessError):
        channel.channel_removeowner(user['token'], new_channel['channel_id'], user['u_id'])
    clear()

def test_input_u_id_removeowner():
    """Testing when u_id is not a valid u_id
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', False)
    with pytest.raises(InputError):
        channel.channel_removeowner(user['token'], new_channel['channel_id'], -1)
    with pytest.raises(InputError):
        channel.channel_removeowner(user['token'], new_channel['channel_id'], user['u_id'] + 1)
    with pytest.raises(InputError):
        channel.channel_removeowner(user['token'], new_channel['channel_id'], user['u_id'] - 1)
    with pytest.raises(InputError):
        channel.channel_removeowner(user['token'], new_channel['channel_id'], user['u_id'] + 7)
    clear()

def test_remove_user_is_not_owner():
    """Testing when user with user id u_id is not an owner of the channel
    """
    clear()
    # First user is always the flockr owner
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    user_3 = auth.auth_register('jonesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Channel is private (users are already owners)
    new_channel_1 = channels.channels_create(user_1['token'], 'Group 1', False)
    new_channel_2 = channels.channels_create(user_2['token'], 'Group 2', False)

    with pytest.raises(InputError):
        channel.channel_removeowner(user_1['token'], new_channel_1['channel_id'], user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_removeowner(user_2['token'], new_channel_2['channel_id'], user_3['u_id'])
    clear()

def test_remove_user_is_owner():
    """Testing when the authorised user is not an owner of the flockr, or an owner of this channel
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Channel is private (users are not owners)
    new_channel_1 = channels.channels_create(user_1['token'], 'Group 1', False)
    new_channel_2 = channels.channels_create(user_2['token'], 'Group 2', False)

    with pytest.raises(AccessError):
        channel.channel_removeowner(user_2['token'], new_channel_1['channel_id'], user_1['u_id'])
    with pytest.raises(AccessError):
        channel.channel_removeowner(user_1['token'], new_channel_2['channel_id'], user_2['u_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_output_user_removeowner_private():
    """Testing if the user has successfully been removed as owner of the channel (private)
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Make a private channel
    channel_join = channels.channels_create(user_1['token'], 'Group 1', False)
    channel.channel_addowner(user_1['token'], channel_join['channel_id'], user_2['u_id'])

    channel_data = channel.channel_details(user_2['token'], channel_join['channel_id'])
    channel.channel_removeowner(user_1['token'], channel_join['channel_id'], user_2['u_id'])
    for curr_owner in channel_data['owner_members']:
        assert curr_owner['u_id'] is not user_2['u_id']
    clear()

def test_output_user_removeowner_public():
    """Testing if the user has successfully been removed as owner of the channel (public)
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Make a public channel
    channel_join = channels.channels_create(user_1['token'], 'Group 1', True)
    channel.channel_addowner(user_1['token'], channel_join['channel_id'], user_2['u_id'])

    channel_data = channel.channel_details(user_2['token'], channel_join['channel_id'])
    channel.channel_removeowner(user_1['token'], channel_join['channel_id'], user_2['u_id'])
    for curr_owner in channel_data['owner_members']:
        assert curr_owner['u_id'] is not user_2['u_id']
    clear()
