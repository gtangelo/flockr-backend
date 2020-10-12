"""
channels feature test implementation to test functions in channels.py

Feature implementation was written by Richard Quisumbing.

2020 T3 COMP1531 Major Project
"""

import pytest
import auth
import channel
import channels
from error import InputError, AccessError
from other import clear

#------------------------------------------------------------------------------#
#                               channels_create                                #
#------------------------------------------------------------------------------#

def test_channels_create():
    """Test for a create channel (We create 2 channels and test whether the 2 channel id's are unique).
    """
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')

    # Create 2 new channels.
    new_channel_1 = channels.channels_create(test_user['token'], 'Channel_1', True)
    new_channel_2 = channels.channels_create(test_user['token'], 'Channel_2', True)

    # Ensure that they are unique.
    assert new_channel_1['channel_id'] is not new_channel_2['channel_id']
    clear()

def test_create_unique_id():
    """Verify if channel id is unique (Since leaving a channel as the only member should destroy the channel).
    """
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')

    # Create 3 channels.
    new_channel1 = channels.channels_create(test_user['token'], 'Channel_1', True)
    new_channel2 = channels.channels_create(test_user['token'], 'Channel_2', True)
    new_channel3 = channels.channels_create(test_user['token'], 'Channel_3', True)

    # Leave 2nd channel.
    channel.channel_leave(test_user['token'], new_channel2['channel_id'])

    # Create a new channel.
    new_channel4 = channels.channels_create(test_user['token'], 'Channel_4', True)

    assert (new_channel1['channel_id'] != new_channel3['channel_id']) and (new_channel3['channel_id'] != new_channel4['channel_id'])
    clear()

def test_channels_invalid():
    """Testing for an invalid channel name (Invalid when name is outside the range of 0-20 (inclusive) characters).
    """
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')

    with pytest.raises(InputError):
        channels.channels_create(test_user['token'], 'Invalid_Channels_Name', True)
    clear()

# Test for whether user automatically becomes a member of their created channel.
def test_channels_create_member():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    new_channel = channels.channels_create(test_user['token'], 'Channel_1', False)

    # Obtain channel details.
    new_channel_details = channel.channel_details(test_user['token'], new_channel['channel_id'])

    test_case = False
    for member in new_channel_details['all_members']:
        if member['u_id'] == test_user['u_id']:
            test_case = True

    assert test_case == True
    clear()

# Test for whether user becomes owner of their created channel.
def test_channels_create_owner():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    new_channel = channels.channels_create(test_user['token'], 'Channel_1', False)

    # Obtain channel details.
    new_channel_details = channel.channel_details(test_user['token'], new_channel['channel_id'])

    test_case = False
    for member in new_channel_details['owner_members']:
        if member['u_id'] == test_user['u_id']:
            test_case = True

    assert test_case == True
    clear()

# Test for a private channel. (test_user created the new_channel and is therefore already a part of it).
def test_channels_create_private():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    test_user2 = auth.auth_register('test2Email@gmail.com', 'password123', 'Jon', 'Snow')
    new_channel = channels.channels_create(test_user['token'], 'Channel_1', False)

    with pytest.raises(AccessError):
        channel.channel_join(test_user2['token'], new_channel['channel_id'])
    clear()


# Test for 0 character name.
def test_channels_create_0char():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')

    with pytest.raises(InputError):
        channels.channels_create(test_user['token'], '', False)
    clear()

# Test for 1 character name.
def test_channels_create_1char():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    new_channel = channels.channels_create(test_user['token'], '1', False)

    assert 'channel_id' in new_channel
    clear()

# Test for 20 character name.
def test_channels_create_20char():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    new_channel = channels.channels_create(test_user['token'], 'Channel_Name12345678', False)

    assert 'channel_id' in new_channel
    clear()

# Test for 21 character name.
def test_channels_create_21char():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')

    with pytest.raises(InputError):
        channels.channels_create(test_user['token'], 'Channel_Name123456789', False)
    clear()


#------------------------------------------------------------------------------#
#                               channels_list                                  #
#------------------------------------------------------------------------------#

#?------------------------------ Output Testing ------------------------------?#

# Test for multiple created channels.
def test_channels_list():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')
    test_user2 = auth.auth_register('test2Email@gmail.com', 'password123', 'Indiana', 'Jones')

    # Create new channels.
    channel_1 = channels.channels_create(test_user['token'], 'Channel_1', True)
    channel_2 = channels.channels_create(test_user['token'], 'Channel_2', True)
    channel_3 = channels.channels_create(test_user['token'], 'Channel_3', True)
    channels.channels_create(test_user2['token'], 'Channel_4', True)

    assert channels.channels_list(test_user['token']) == {
        'channels': [
            {
                'channel_id': channel_1['channel_id'],
                'name': 'Channel_1',
            },
            {
                'channel_id': channel_2['channel_id'],
                'name': 'Channel_2',
            },
            {
                'channel_id': channel_3['channel_id'],
                'name': 'Channel_3',
            },
        ],
    }
    clear()

# Test for leaving joined channels and then listing joined channels.
def test_channels_leave():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')

    # Create new channels.
    channel_1 = channels.channels_create(test_user['token'], 'Channel_1', True)
    channel_2 = channels.channels_create(test_user['token'], 'Channel_2', True)
    channel_3 = channels.channels_create(test_user['token'], 'Channel_3', True)

    # Leave the first channel.
    channel.channel_leave(test_user['token'], channel_1['channel_id'])

    assert channels.channels_list(test_user['token']) == {
        'channels': [
            {
                'channel_id': channel_2['channel_id'],
                'name': 'Channel_2',
            },
            {
                'channel_id': channel_3['channel_id'],
                'name': 'Channel_3',
            },
        ],
    }
    clear()

# Test for empty channels.
def test_channels_list_empty():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')

    list_channels = channels.channels_list(test_user['token'])

    assert len(list_channels['channels']) == 0
    clear()


#------------------------------------------------------------------------------#
#                               channels_listall                               #
#------------------------------------------------------------------------------#

# Test list all channels.
def test_channels_listall():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')
    test_user2 = auth.auth_register('test2Email@gmail.com', 'password123', 'Indiana', 'Jones')

    # Create new channels.
    channel_1 = channels.channels_create(test_user['token'], 'Channel_1', True)
    channel_2 = channels.channels_create(test_user['token'], 'Channel_2', True)
    channel_3 = channels.channels_create(test_user['token'], 'Channel_3', True)
    channel_4 = channels.channels_create(test_user2['token'], 'Channel_4', True)
    channel_5 = channels.channels_create(test_user2['token'], 'Channel_5', True)

    assert channels.channels_listall(test_user['token']) == {
        'channels': [
            {
                'channel_id': channel_1['channel_id'],
                'name': 'Channel_1',
            },
            {
                'channel_id': channel_2['channel_id'],
                'name': 'Channel_2',
            },
            {
                'channel_id': channel_3['channel_id'],
                'name': 'Channel_3',
            },
            {
                'channel_id': channel_4['channel_id'],
                'name': 'Channel_4',
            },
            {
                'channel_id': channel_5['channel_id'],
                'name': 'Channel_5',
            },
        ]
    }
    clear()

# Test for empty channels.
def test_channels_listall_empty():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')

    list_channels = channels.channels_listall(test_user['token'])

    assert len(list_channels['channels']) == 0
    clear()

# Test for private channels
def test_channels_listall_private():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')

    # Channel 1 and 3 are private channels.
    channel_1 = channels.channels_create(test_user['token'], 'Channel_1', False)
    channel_2 = channels.channels_create(test_user['token'], 'Channel_2', True)
    channel_3 = channels.channels_create(test_user['token'], 'Channel_3', False)
    channel_4 = channels.channels_create(test_user['token'], 'Channel_4', True)

    assert channels.channels_listall(test_user['token']) == {
        'channels': [
            {
                'channel_id': channel_1['channel_id'],
                'name': 'Channel_1',
            },
            {
                'channel_id': channel_2['channel_id'],
                'name': 'Channel_2',
            },
            {
                'channel_id': channel_3['channel_id'],
                'name': 'Channel_3',
            },
            {
                'channel_id': channel_4['channel_id'],
                'name': 'Channel_4',
            },
        ],
    }
    clear()

#------------------------------------------------------------------------------#
#                               misc                                           #
#------------------------------------------------------------------------------#

# Testing if token is valid
def test_access_leave_valid_token():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    channels.channels_create(user['token'], 'Group 1', True)
    auth.auth_logout(user['token'])

    # Token should now be invalid.
    with pytest.raises(AccessError):
        channels.channels_create(user['token'], 'Group 1', False)
        channels.channels_list(user['token'])
        channels.channels_listall(user['token'])
    clear()
