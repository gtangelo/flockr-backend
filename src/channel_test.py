import auth
import channel
import channels
import pytest
from error import InputError, AccessError
from data import data

# channel_invite



# channel_details



# channel_messages

# Testing when an invalid channel_id is used as a parameter
def test_input_channel_id():
    start = 0
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')

    with pytest.raises(InputError):
        channel.channel_messages(user['token'], 0, start)
        channel.channel_messages(user['token'], -1, start)
        channel.channel_messages(user['token'], 3, start)

# Testing when start is an invalid value
def test_input_start():
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')
    channel_id = channels.channels_create(user['token'], 'Group 1', True)

    with pytest.raises(InputError):
        channel.channel_messages(user['token'], channel_id, 1)
        channel.channel_messages(user['token'], channel_id, 10)
        channel.channel_messages(user['token'], channel_id, -1)

# Testing if another user can access the channel
def test_access_member():
    user1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')
    channel_id1 = channels.channels_create(user1['token'], 'Group 1', True)
    channel_id2 = channels.channels_create(user2['token'], 'Group 2', True)

    with pytest.raises(AccessError):
        channel.channel_messages(user1['token'], channel_id2, 0)
        channel.channel_messages(user2['token'], channel_id1, 0)

# Testing when a channel has no messages
def test_output_no_messages():
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')
    channel_id = channels.channels_create(user['token'], 'Group 1', True)
    result = channel.channel_messages(user['token'], channel_id, 0)
    assert result['messages'] == []
    assert result['start'] == 0
    assert result['end'] == -1

# Testing when a channel has less than 50 messages

# Testing on the most recent message as the starting point
def test_output_with_messages_recent():
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')
    channel.channel_invite(user['token'], 1, user['id'])
    result = channel.channel_messages(user['token'], 1, 0)
    assert result['messages'] == [
        {
            'message_id': 3,
            'u_id': 1,
            'message': 'Hello user2',
            'time_created': 1582426791,
        },
        {
            'message_id': 2,
            'u_id': 2,
            'message': 'Hello user1!',
            'time_created': 1582426790,
        },
        {
            'message_id': 1,
            'u_id': 1,
            'message': 'Hello world',
            'time_created': 1582426789,
        },
    ]
    assert result['start'] == 0
    assert result['end'] == 3

# Testing on the middle recent message as the starting point
def test_output_with_messages_middle():
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')
    channel.channel_invite(user['token'], 1, user['id'])
    result = channel.channel_messages(user['token'], 1, 1)
    assert result['messages'] == [
        {
            'message_id': 2,
            'u_id': 2,
            'message': 'Hello user1!',
            'time_created': 1582426790,
        },
        {
            'message_id': 1,
            'u_id': 1,
            'message': 'Hello world',
            'time_created': 1582426789,
        },
    ]
    assert result['start'] == 1
    assert result['end'] == 2

# Testing on the last recent message as the starting point
def test_output_with_messages_last():
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')
    channel.channel_invite(user['token'], 1, user['id'])
    result = channel.channel_messages(user['token'], 1, 3)
    assert result['messages'] == [
        {
            'message_id': 1,
            'u_id': 1,
            'message': 'Hello world',
            'time_created': 1582426789,
        },
    ]
    assert result['start'] == 3
    assert result['end'] == -1



# channel_leave



# channel_join



# channel_addowner



# channel_removeowner



