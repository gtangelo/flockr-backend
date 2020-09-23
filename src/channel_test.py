import pytest
import auth, channel, channels
from error import InputError, AccessError


# channel_invite



# channel_details


#------------------------------------------------------------------------------#
#                               channel_messages                               #
#------------------------------------------------------------------------------#

#-------------------------- Input/Access Error Testing ------------------------#

# Testing when an invalid channel_id is used as a parameter
def test_input_messages_channel_id():
    start = 0
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')

    with pytest.raises(InputError):
        channel.channel_messages(user['token'], 0, start)
        channel.channel_messages(user['token'], -1, start)
        channel.channel_messages(user['token'], 3, start)

# Testing when start is an invalid value
def test_input_messages_start():
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    with pytest.raises(InputError):
        channel.channel_messages(user['token'], new_channel['channel_id'], 1)
        channel.channel_messages(user['token'], new_channel['channel_id'], 10)
        channel.channel_messages(user['token'], new_channel['channel_id'], -1)

# Testing if another user can access the channel
def test_access_messages_user_is_member():
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')
    new_channel_1 = channels.channels_create(user_1['token'], 'Group 1', True)
    new_channel_2 = channels.channels_create(user_2['token'], 'Group 2', True)

    with pytest.raises(AccessError):
        channel.channel_messages(user_1['token'], new_channel_2['channel_id'], 0)
        channel.channel_messages(user_2['token'], new_channel_1['channel_id'], 0)

#------------------------------- Output Testing -------------------------------#

# Testing when a channel has no messages
def test_output_no_messages():
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    assert result['messages'] == []
    assert result['start'] == 0
    assert result['end'] == -1

#----- Testing when a channel has less than 50 messages
# Testing on the most recent message as the starting point
def test_output_recent_message():
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')
    channel.channel_invite(user['token'], 1, user['u_id'])
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
def test_output_middle_message():
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')
    channel.channel_invite(user['token'], 1, user['u_id'])
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
def test_output_last_message():
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')
    channel.channel_invite(user['token'], 1, user['u_id'])
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

#----- Testing when a channel has exactly 50 messages

#----- Testing when a channel has more than 50 messages

#------------------------------------------------------------------------------#
#                               channel_leave                                  #
#------------------------------------------------------------------------------#

#-------------------------- Input/Access Error Testing ------------------------#

# Testing when an invalid channel_id is used as a parameter
def test_input_leave_channel_id():
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    with pytest.raises(InputError):
        channel.channel_leave(user['token'], new_channel['channel_id'] + 1)
        channel.channel_leave(user['token'], 0)
        channel.channel_leave(user['token'], -1)

# Testing if a user was not in the channel initially
def test_access_leave_user_is_member():
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')
    new_channel_1 = channels.channels_create(user_1['token'], 'Group 1', True)
    new_channel_2 = channels.channels_create(user_2['token'], 'Group 2', True)

    with pytest.raises(AccessError):
        channel.channel_leave(user_1['token'], new_channel_2['channel_id'], 0)
        channel.channel_leave(user_2['token'], new_channel_1['channel_id'], 0)

#------------------------------- Output Testing -------------------------------#

# Testing if the user has successfully left the channel
def test_output_user_leave():
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')
    channel_leave = channels.channels_create(user['token'], 'Group 1', True)
    channel.channel_leave(user['token'], channel_leave['channel_id'])

    channel_list = channels.channels_list(user['token'])
    for curr_channel in channel_list['channels']:
        assert curr_channel['channel_id'] is not channel_leave['channel_id']


# channel_join



# channel_addowner



# channel_removeowner



