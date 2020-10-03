import pytest
import auth, channel, channels
from channels import channels_list
from error import InputError, AccessError
from other import clear

#------------------------------------------------------------------------------#
#                               channel_invite                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

# Testing invalid token for users which have logged out
def test_channel_invite_login_user():
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
        channel.channel_invite(user_2['token'], new_channel['channel_id'], user_3['u_id'])
        channel.channel_invite(user_3['token'], new_channel['channel_id'], user_3['u_id'])
        channel.channel_invite(user_4['token'], new_channel['channel_id'], user_3['u_id'])
    clear()

# Testing when wrong data types are used as input 
def test_channel_invite_wrong_data_type():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)

    with pytest.raises(InputError):
        channel.channel_invite(user['token'], new_channel['channel_id'], -1)
        channel.channel_invite(user['token'], new_channel['channel_id'], '@#$!')
        channel.channel_invite(user['token'], new_channel['channel_id'], 67.666)
    clear()

# Testing when invalid user is invited to channel
def test_channel_invite_invalid_user():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)

    with pytest.raises(InputError):
        channel.channel_invite(user['token'], new_channel['channel_id'], user['u_id'] + 1)
        channel.channel_invite(user['token'], new_channel['channel_id'], user['u_id'] - 1)
    clear()

# Testing when valid user is invited to invalid channel
def test_channel_invite_invalid_channel():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')

    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], -122, user_2['u_id'])
        channel.channel_invite(user_1['token'], -642, user_2['u_id'])
        channel.channel_invite(user_1['token'], '@#@!', user_2['u_id'])
        channel.channel_invite(user_1['token'], 212.11, user_2['u_id'])
    clear()

# Testing when user is not authorized to invite other users to channel
# (Assumption) This includes an invalid user inviting users to channel
def test_channel_invite_not_authorized():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    auth.auth_logout(user_1['token'])

    with pytest.raises(AccessError):
        channel.channel_invite(12, new_channel['channel_id'], user_3['u_id'])
        channel.channel_invite(-12, new_channel['channel_id'], user_3['u_id'])
        channel.channel_invite(121.11, new_channel['channel_id'], user_3['u_id'])
        channel.channel_invite(user_2['token'], new_channel['channel_id'], user_1['u_id'])
        channel.channel_invite(user_2['token'], new_channel['channel_id'], user_3['u_id'])
        channel.channel_invite(user_1['token'], new_channel['channel_id'], user_3['u_id'])
    clear()

# Testing when user is not allowed to invite him/herself to channel
# (Assumption testing) this error will be treated as AccessError
def test_channel_invite_invalid_self_invite():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)

    with pytest.raises(AccessError):
        channel.channel_invite(user['token'], new_channel['channel_id'], user['u_id'])
    clear()

# Testing when user invites a user multiple times 
# (Assumption testing) this error will be treated as AccessError
def test_channel_multiple_invite():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    assert channel.channel_invite(user_1['token'], new_channel['channel_id'], user_2['u_id']) == {}

    with pytest.raises(AccessError):
        channel.channel_invite(user_1['token'], new_channel['channel_id'], user_2['u_id'])
        channel.channel_invite(user_2['token'], new_channel['channel_id'], user_2['u_id'])
        channel.channel_invite(user_2['token'], new_channel['channel_id'], user_1['u_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

# Testing if user has successfully been invited to the channel
def test_channel_invite_successful():
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

# (Assumption testing) first person to register is flockr owner
# Testing if flockr owner has been successfully invited to channel and given ownership
def test_channel_invite_flockr_user():
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

#------------------------------------------------------------------------------#
#                               channel_details                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

# Testing if channel is invalid or does not exist
def test_channel_details_invalid_channel():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')

    with pytest.raises(InputError):
        channel.channel_details(user['token'], -1)
        channel.channel_details(user['token'], -19)
        channel.channel_details(user['token'], '#@&!')
        channel.channel_details(user['token'], 121.12)
    clear()

# Testing if unauthorized/invalid user is unable to access channel details
def test_channel_details_invalid_user():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)

    with pytest.raises(AccessError):
        channel.channel_details(user_2['token'], new_channel['channel_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

# Testing the required correct details of a channel
def test_channel_details_authorized_user():
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

# Testing if channel info has been added to user profile when added
def test_output_invite_user_list():
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
#                               channel_messages                               #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

# Testing when an invalid channel_id is used as a parameter
def test_input_messages_channel_id():
    clear()
    start = 0
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')

    with pytest.raises(InputError):
        channel.channel_messages(user['token'], -1, start)
        channel.channel_messages(user['token'], 0, start)
        channel.channel_messages(user['token'], 1, start)
        channel.channel_messages(user['token'], 5, start)
    clear()

# Testing when start is an invalid start value
# Start is greater than the total number of messages in the channel
def test_input_messages_start():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    with pytest.raises(InputError):
        channel.channel_messages(user['token'], new_channel['channel_id'], 1)
        channel.channel_messages(user['token'], new_channel['channel_id'], 10)
        channel.channel_messages(user['token'], new_channel['channel_id'], -1)
    clear()

# Testing if another user can access the channel
def test_access_messages_user_is_member():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    new_channel_1 = channels.channels_create(user_1['token'], 'Group 1', True)
    new_channel_2 = channels.channels_create(user_2['token'], 'Group 2', True)

    with pytest.raises(AccessError):
        channel.channel_messages(user_1['token'], new_channel_2['channel_id'], 0)
        channel.channel_messages(user_2['token'], new_channel_1['channel_id'], 0)
    clear()

# Testing if token is valid
def test_access_messages_valid_token():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    auth.auth_logout(user['token'])

    with pytest.raises(AccessError):
        channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    clear()
#?------------------------------ Output Testing ------------------------------?#

#----- Testing when a channel has no messages
def test_output_no_messages():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    result = channel.channel_messages(user['token'], new_channel['channel_id'], 0)
    assert result['messages'] == []
    assert result['start'] == -1
    assert result['end'] == -1
    clear()

#! These tests cannot be done in iteration 1.
#----- Testing when a channel has less than 50 messages
# Testing on the most recent message as the starting point
# def test_output_recent_message():
#     user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
#     channel.channel_invite(user['token'], 1, user['u_id'])
#     result = channel.channel_messages(user['token'], 1, 0)
#     assert result['messages'] == [
#         {
#             'message_id': 3,
#             'u_id': 1,
#             'message': 'Hello user2',
#             'time_created': 1582426791,
#         },
#         {
#             'message_id': 2,
#             'u_id': 2,
#             'message': 'Hello user1!',
#             'time_created': 1582426790,
#         },
#         {
#             'message_id': 1,
#             'u_id': 1,
#             'message': 'Hello world',
#             'time_created': 1582426789,
#         },
#     ]
#     assert result['start'] == 0
#     assert result['end'] == 3
#     clear()

# Testing on the middle recent message as the starting point
# def test_output_middle_message():
#     user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
#     channel.channel_invite(user['token'], 1, user['u_id'])
#     result = channel.channel_messages(user['token'], 1, 1)
#     assert result['messages'] == [
#         {
#             'message_id': 2,
#             'u_id': 2,
#             'message': 'Hello user1!',
#             'time_created': 1582426790,
#         },
#         {
#             'message_id': 1,
#             'u_id': 1,
#             'message': 'Hello world',
#             'time_created': 1582426789,
#         },
#     ]
#     assert result['start'] == 1
#     assert result['end'] == 2
#     clear()

# Testing on the last recent message as the starting point
# def test_output_last_message():
#     user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
#     channel.channel_invite(user['token'], 1, user['u_id'])
#     result = channel.channel_messages(user['token'], 1, 3)
#     assert result['messages'] == [
#         {
#             'message_id': 1,
#             'u_id': 1,
#             'message': 'Hello world',
#             'time_created': 1582426789,
#         },
#     ]
#     assert result['start'] == 3
#     assert result['end'] == -1
#     clear()

#----- Testing when a channel has exactly 50 messages

#----- Testing when a channel has more than 50 messages

#------------------------------------------------------------------------------#
#                               channel_leave                                  #
#------------------------------------------------------------------------------#

#?------------------------- Input/Access Error Testing -----------------------?#

# Testing when an invalid channel_id is used as a parameter
def test_input_leave_channel_id():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    with pytest.raises(InputError):
        channel.channel_leave(user['token'], -1)
        channel.channel_leave(user['token'], 0)
        channel.channel_leave(user['token'], 1)
        channel.channel_leave(user['token'], 5)
    clear()

# Testing if a user was not in the channel initially
def test_access_leave_user_is_member():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    new_channel_1 = channels.channels_create(user_1['token'], 'Group 1', True)
    new_channel_2 = channels.channels_create(user_2['token'], 'Group 2', True)

    with pytest.raises(AccessError):
        channel.channel_leave(user_1['token'], new_channel_2['channel_id'])
        channel.channel_leave(user_2['token'], new_channel_1['channel_id'])
    clear()

# Testing if token is valid
def test_access_leave_valid_token():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    auth.auth_logout(user['token'])

    with pytest.raises(AccessError):
        channel.channel_leave(user['token'], new_channel['channel_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

# Testing if the user has successfully left a public channel
def test_output_user_leave_public():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    channel_leave = channels.channels_create(user['token'], 'Group 1', True)
    channel.channel_leave(user['token'], channel_leave['channel_id'])
    channel_list = channels.channels_list(user['token'])
    for curr_channel in channel_list['channels']:
        assert curr_channel['channel_id'] is not channel_leave['channel_id']
    clear()

# Testing if the user has successfully left a private channel
def test_output_user_leave_private():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    channel_leave = channels.channels_create(user['token'], 'Group 1', False)
    channel.channel_leave(user['token'], channel_leave['channel_id'])

    channel_list = channels.channels_list(user['token'])
    for curr_channel in channel_list['channels']:
        assert curr_channel['channel_id'] is not channel_leave['channel_id']
    clear()

# Testing if user has left the correct channel.
def test_output_user_leave_channels():
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

# Testing when user leaves multiple channels
def test_output_leave_channels():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')

    channel_leave_1 = channels.channels_create(user_1['token'], 'Group 1', False)
    channel.channel_leave(user_1['token'], channel_leave_1['channel_id'])
    channel_leave_2 = channels.channels_create(user_2['token'], 'Group 1', True)
    channel.channel_addowner(user_2['token'], channel_leave_2['channel_id'], user_1['u_id'])
    channel.channel_leave(user_1['token'], channel_leave_2['channel_id'])

    channel_list = channels.channels_list(user_1['token'])
    for curr_channel in channel_list['channels']:
        assert curr_channel['channel_id'] != channel_leave_1['channel_id']
        assert curr_channel['channel_id'] != channel_leave_2['channel_id']
    clear()

# Testing when a member leaves that it does not delete the channel.
def test_output_member_leave():
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


# Testing Process: Tests suite that is designed to test the process of all
# owners leaving in which the user with the lowest u_id in the channel becomes 
# the owner automatically.
# Covers also if user access has been erased on channel end.
def test_output_all_owners_leave():
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
    assert len(channel_data['owner_members']) == 1 and lowest_u_id_user['u_id'] == channel_data['owner_members'][0]['u_id']

    # Check on the user end that the channel is not avialiable on their list.
    channel_list = channels.channels_list(user_1['token'])
    for curr_channel in channel_list['channels']:
        assert curr_channel['channel_id'] is not new_channel['channel_id']

    channel_list = channels.channels_list(user_2['token'])
    for curr_channel in channel_list['channels']:
        assert curr_channel['channel_id'] is not new_channel['channel_id']

    clear()

# Test if the channel is deleted when all members leave
def test_output_all_members_leave():
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

# Test when the flockr owner leaves and comes back that the user status is an
# owner.
def test_output_flockr_rejoin_channel():
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

# Test when the the reator leaves and comes back that the user status is a member.
def test_output_creator_rejoin_channel():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
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

#-------------------------- Input/Access Error Testing ------------------------#

# Testing when Channel ID is not a valid channel
def test_input_join_channel_id():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    with pytest.raises(InputError):
        channel.channel_join(user['token'], -1)
        channel.channel_join(user['token'], 0)
        channel.channel_join(user['token'], 1)
        channel.channel_join(user['token'], 5)
    clear()

# Testing if token is valid
def test_access_join_valid_token():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    auth.auth_logout(user['token'])

    with pytest.raises(AccessError):
        channel.channel_join(user['token'], new_channel['channel_id'])
    clear()

# Testing if channel_id refers to a channel that is private 
# (when the authorised user is not a global owner)
def test_access_join_user_is_member():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    user_3 = auth.auth_register('jonesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Channel is private
    new_channel_1 = channels.channels_create(user_1['token'], 'Group 1', False)
    new_channel_2 = channels.channels_create(user_2['token'], 'Group 2', False)

    with pytest.raises(AccessError):
        channel.channel_join(user_3['token'], new_channel_2['channel_id'])
        channel.channel_join(user_2['token'], new_channel_1['channel_id'])
    clear()

#------------------------------- Output Testing -------------------------------#

# Testing if the user has successfully joined a public channel
def test_output_user_join_public():
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
    assert in_channel == True

    # Check if channel appears in the user's channels list
    channel_user_list = channels.channels_list(user_2['token'])
    assert len(channel_user_list) == 1 
    clear()

# Test for flockr owner (flockr owner can join private channels)
def test_output_user_join_flockr_owner_list():
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
    for curr_channel in channel_list:
        if curr_channel['channel_id'] is channel_join['channel_id']:
            in_channel = True
            break
    assert in_channel
    clear()


# Test for flockr owner (flockr owner can join private channels)
def test_output_user_join_flockr_owner_details():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Make a private channel and check if flockr owner
    channel_join = channels.channels_create(user_2['token'], 'Private Group 1', False)

    # Assume that the first user is the flockr owner
    channel.channel_join(user_1['token'], channel_join['channel_id'])
    channel_list = channels.channels_list(user_2['token'])

    # Check if flockr owner is a channel member
    channel_data = channel.channel_details(user_2['token'], channel_join['channel_id'])
    is_member = False
    for member in channel_data['all_members']:
        if member['u_id'] == user_1['u_id']:
            is_member = True
            break
    assert is_member
    clear()


# Test for flockr owner (flockr owner can join private channels)
def test_output_user_join_flockr_owner_list():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Make a private channel and check if flockr owner
    channel_join = channels.channels_create(user_2['token'], 'Private Group 1', False)

    # Assume that the first user is the flockr owner
    channel.channel_join(user_1['token'], channel_join['channel_id'])
    channel_list = channels.channels_list(user_2['token'])

    # Flockr owner becomes owner after channel join
    owner = True
    channel_data = channel.channel_details(user_1['token'], channel_join['channel_id'])
    for member in channel_data['owner_members']:
        if member['u_id'] == user_1['u_id']:
            owner = False
    assert not owner
    clear()


# Test for a person joining again
def test_output_user_join_again():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', False)
    channel.channel_join(user['token'], new_channel['channel_id'])
    # Check channel details if the user is a member
    count_1 = 0
    channel_data = channel.channel_details(user['token'], new_channel['channel_id'])
    for member in channel_data['all_members']:
        if member['u_id'] is user['u_id']:
            count_1 += 1
        break
    assert count_1 == 1
    # Check if channel appears in the user's channels list
    channel_user_list = channels.channels_list(user['token'])
    assert len(channel_user_list) == 1 
    clear()
    
#------------------------------------------------------------------------------#
#                                channel_addowner                              #
#------------------------------------------------------------------------------#

#-------------------------- Input/Access Error Testing ------------------------#

# Testing when Channel ID is not a valid channel
def test_input_channelID_addowner():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    with pytest.raises(InputError):
        channel.channel_addowner(user['token'], -1, user['u_id'])
        channel.channel_addowner(user['token'], 0, user['u_id'])
        channel.channel_addowner(user['token'], 1, user['u_id'])
        channel.channel_addowner(user['token'], 5, user['u_id'])
    clear()

# Testing if token is valid
def test_access_add_valid_token():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    auth.auth_logout(user['token'])

    with pytest.raises(AccessError):
        channel.channel_addowner(user['token'], new_channel['channel_id'], user['u_id'])
    clear()

# Testing when u_id is not a valid u_id
def test_input_u_id_addowner():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', False)
    with pytest.raises(InputError):
        channel.channel_addowner(user['token'], new_channel['channel_id'], -1)
        channel.channel_addowner(user['token'], new_channel['channel_id'], 0)
        channel.channel_addowner(user['token'], new_channel['channel_id'], 5)
        channel.channel_addowner(user['token'], new_channel['channel_id'], 7)
    clear()

# Testing when user with user id u_id is already an owner of the channel
def test_add_user_is_already_owner():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Channel is private (creators are already owners)
    new_channel_1 = channels.channels_create(user_1['token'], 'Group 1', False)
    new_channel_2 = channels.channels_create(user_2['token'], 'Group 2', False)

    with pytest.raises(InputError):
        channel.channel_addowner(user_1['token'], new_channel_1['channel_id'], user_1['u_id'])
        channel.channel_addowner(user_2['token'], new_channel_2['channel_id'], user_2['u_id'])
    clear()

# Testing when the authorised user is not an owner of the flockr, or an owner of this channel
def test_auth_user_is_not_owner():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # User_1 is owner of new_channel_1 and User_2 is the owner of new_channel_2
    new_channel_1 = channels.channels_create(user_1['token'], 'Group 1', False)
    new_channel_2 = channels.channels_create(user_2['token'], 'Group 2', False)

    with pytest.raises(AccessError):
        channel.channel_addowner(user_1['token'], new_channel_2['channel_id'], user_1['u_id'])
        channel.channel_addowner(user_2['token'], new_channel_1['channel_id'], user_2['u_id'])
    clear()

#------------------------------- Output Testing -------------------------------#

# Testing if the user has successfully been added as owner of the channel (private)
def test_output_user_addowner_private():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Make a private channel
    channel_join = channels.channels_create(user_1['token'], 'Group 1', False)
    channel.channel_addowner(user_1['token'], channel_join['channel_id'], user_2['u_id'])

    channel_data = channel.channel_details(user_2['token'], channel_join['channel_id'])
    is_owner = False
    for curr_owner in channel_data['owner_members']:
        if curr_owner['u_id'] is user_2['u_id']:
            is_owner = True
            break
    assert is_owner == True
    clear()

# Testing if the user has successfully been added as owner of the channel (public)
def test_output_user_addowner_public():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Make a public channel
    channel_join = channels.channels_create(user_1['token'], 'Group 1', True)
    channel.channel_addowner(user_1['token'], channel_join['channel_id'], user_2['u_id'])

    channel_data = channel.channel_details(user_2['token'], channel_join['channel_id'])
    is_owner = False
    for curr_owner in channel_data['owner_members']:
        if curr_owner['u_id'] is user_2['u_id']:
            is_owner = True
            break
    assert is_owner == True

#------------------------------------------------------------------------------#
#                                channel_removeowner                           #
#------------------------------------------------------------------------------#

#-------------------------- Input/Access Error Testing ------------------------#

# Testing when Channel ID is not a valid channel
def test_input_removeowner():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    with pytest.raises(InputError):
        channel.channel_removeowner(user['token'], -1, user['u_id'])
        channel.channel_removeowner(user['token'], 0, user['u_id'])
        channel.channel_removeowner(user['token'], 1, user['u_id'])
        channel.channel_removeowner(user['token'], 5, user['u_id'])
    clear()

# Testing if token is valid
def test_access_remove_valid_token():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    auth.auth_logout(user['token'])

    with pytest.raises(AccessError):
        channel.channel_removeowner(user['token'], new_channel['channel_id'], user['u_id'])
    clear()

# Testing when u_id is not a valid u_id
def test_input_u_id_removeowner():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', False)
    with pytest.raises(InputError):
        channel.channel_removeowner(user['token'], new_channel['channel_id'], -1)
        channel.channel_removeowner(user['token'], new_channel['channel_id'], user['u_id'] + 1)
        channel.channel_removeowner(user['token'], new_channel['channel_id'], user['u_id'] - 1)
        channel.channel_removeowner(user['token'], new_channel['channel_id'], user['u_id'] + 7)
    clear()

# Testing when user with user id u_id is not an owner of the channel
def test_remove_user_is_not_owner():
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
        channel.channel_removeowner(user_2['token'], new_channel_2['channel_id'], user_3['u_id'])
    clear()

# Testing when the authorised user is not an owner of the flockr, or an owner of this channel
def test_remove_user_is_owner():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    # Channel is private (users are not owners)
    new_channel_1 = channels.channels_create(user_1['token'], 'Group 1', False)
    new_channel_2 = channels.channels_create(user_2['token'], 'Group 2', False)

    with pytest.raises(AccessError):
        channel.channel_removeowner(user_2['token'], new_channel_1['channel_id'], user_1['u_id'])
        channel.channel_removeowner(user_1['token'], new_channel_2['channel_id'], user_2['u_id'])
    clear()

#------------------------------- Output Testing -------------------------------#

# Testing if the user has successfully been removed as owner of the channel (private)
def test_output_user_removeowner_private():
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

# Testing if the user has successfully been removed as owner of the channel (public)
def test_output_user_removeowner_public():
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

