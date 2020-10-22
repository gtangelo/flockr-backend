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

@pytest.fixture
def user_1():
    clear()
    return auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')

@pytest.fixture
def logout_user_1(user_1):
    return auth.auth_logout(user_1['token'])

@pytest.fixture
def user_2():
    return auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    
@pytest.fixture
def public_channel_1(user_1):
    return channels.channels_create(user_1['token'], 'Group 1', True)

@pytest.fixture
def private_channel_1(user_1):
    return channels.channels_create(user_1['token'], 'Group 1', False)
#------------------------------------------------------------------------------#
#                               channels_create                                #
#------------------------------------------------------------------------------#

def test_channels_create(user_1):
    """Test for a create channel (We create 2 channels and test whether the 2 channel id's
    are unique).
    """
    # Create 2 new channels.
    new_channel_1 = channels.channels_create(user_1['token'], 'Channel_1', True)
    new_channel_2 = channels.channels_create(user_1['token'], 'Channel_2', True)

    # Ensure that they are unique.
    assert new_channel_1['channel_id'] is not new_channel_2['channel_id']
    clear()


def test_create_unique_id(user_1):
    """Verify if channel id is unique (Since leaving a channel as the only member should
    destroy the channel).
    """
    # Create 3 channels.
    new_channel1 = channels.channels_create(user_1['token'], 'Channel_1', True)
    new_channel2 = channels.channels_create(user_1['token'], 'Channel_2', True)
    new_channel3 = channels.channels_create(user_1['token'], 'Channel_3', True)

    # Leave 2nd channel.
    channel.channel_leave(user_1['token'], new_channel2['channel_id'])

    # Create a new channel.
    new_channel4 = channels.channels_create(user_1['token'], 'Channel_4', True)

    assert new_channel1['channel_id'] != new_channel3['channel_id']
    assert new_channel3['channel_id'] != new_channel4['channel_id']
    clear()



def test_channels_invalid(user_1):
    """Testing for an invalid channel name (Invalid when name is outside the range of 0-20
    (inclusive) characters).
    """
    with pytest.raises(InputError):
        channels.channels_create(user_1['token'], 'Invalid_Channels_Name', True)
    clear()

def test_channels_create_member(user_1, public_channel_1):
    """Test for whether user automatically becomes a member of their created channel.
    """
    # Obtain channel details.
    new_channel_details = channel.channel_details(user_1['token'], public_channel_1['channel_id'])

    test_case = False
    for member in new_channel_details['all_members']:
        if member['u_id'] == user_1['u_id']:
            test_case = True

    assert test_case
    clear()

def test_channels_create_owner(user_1, public_channel_1):
    """Test for whether user becomes owner of their created channel.
    """
    # Obtain channel details.
    new_channel_details = channel.channel_details(user_1['token'], public_channel_1['channel_id'])

    test_case = False
    for member in new_channel_details['owner_members']:
        if member['u_id'] == user_1['u_id']:
            test_case = True

    assert test_case
    clear()

def test_channels_create_private(user_1, user_2, private_channel_1):
    """Test for a private channel. (test_user created the new_channel and is therefore
    already a part of it).
    """
    with pytest.raises(AccessError):
        channel.channel_join(user_2['token'], private_channel_1['channel_id'])
    clear()



def test_channels_create_0char(user_1):
    """Test for 0 character name.
    """
    with pytest.raises(InputError):
        channels.channels_create(user_1['token'], '', False)
    clear()

def test_channels_create_1char(user_1):
    """Test for 1 character name.
    """
    new_channel = channels.channels_create(user_1['token'], '1', False)
    assert 'channel_id' in new_channel
    clear()

def test_channels_create_20char(user_1):
    """Test for 20 character name.
    """
    new_channel = channels.channels_create(user_1['token'], 'Channel_Name12345678', False)

    assert 'channel_id' in new_channel
    clear()

def test_channels_create_21char(user_1):
    """Test for 21 character name.
    """
    with pytest.raises(InputError):
        channels.channels_create(user_1['token'], 'Channel_Name123456789', False)
    clear()


#------------------------------------------------------------------------------#
#                               channels_list                                  #
#------------------------------------------------------------------------------#

#?------------------------------ Output Testing ------------------------------?#

def test_channels_list(user_1, user_2):
    """Test for multiple created channels.
    """
    # Create new channels.
    channel_1 = channels.channels_create(user_1['token'], 'Channel_1', True)
    channel_2 = channels.channels_create(user_1['token'], 'Channel_2', True)
    channel_3 = channels.channels_create(user_1['token'], 'Channel_3', True)
    channels.channels_create(user_2['token'], 'Channel_4', True)

    assert channels.channels_list(user_1['token']) == {
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

def test_channels_leave(user_1):
    """Test for leaving joined channels and then listing joined channels.
    """
    # Create new channels.
    channel_1 = channels.channels_create(user_1['token'], 'Channel_1', True)
    channel_2 = channels.channels_create(user_1['token'], 'Channel_2', True)
    channel_3 = channels.channels_create(user_1['token'], 'Channel_3', True)

    # Leave the first channel.
    channel.channel_leave(user_1['token'], channel_1['channel_id'])

    assert channels.channels_list(user_1['token']) == {
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


def test_channels_list_empty(user_1):
    """Test for empty channels.
    """
    list_channels = channels.channels_list(user_1['token'])

    assert len(list_channels['channels']) == 0
    clear()


#------------------------------------------------------------------------------#
#                               channels_listall                               #
#------------------------------------------------------------------------------#

def test_channels_listall(user_1, user_2):
    """Test list all channels.
    """
    # Create new channels.
    channel_1 = channels.channels_create(user_1['token'], 'Channel_1', True)
    channel_2 = channels.channels_create(user_1['token'], 'Channel_2', True)
    channel_3 = channels.channels_create(user_1['token'], 'Channel_3', True)
    channel_4 = channels.channels_create(user_2['token'], 'Channel_4', True)
    channel_5 = channels.channels_create(user_2['token'], 'Channel_5', True)

    assert channels.channels_listall(user_1['token']) == {
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

def test_channels_listall_empty(user_1):
    """Test for empty channels.
    """
    list_channels = channels.channels_listall(user_1['token'])

    assert len(list_channels['channels']) == 0
    clear()

def test_channels_listall_private(user_1):
    """Test for private channels.
    """
    # Channel 1 and 3 are private channels.
    channel_1 = channels.channels_create(user_1['token'], 'Channel_1', False)
    channel_2 = channels.channels_create(user_1['token'], 'Channel_2', True)
    channel_3 = channels.channels_create(user_1['token'], 'Channel_3', False)
    channel_4 = channels.channels_create(user_1['token'], 'Channel_4', True)

    assert channels.channels_listall(user_1['token']) == {
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

def test_access_leave_valid_token1(user_1, logout_user_1):
    """Testing if token is valid in the channels create function.
    """
    # Token should now be invalid.
    with pytest.raises(AccessError):
        channels.channels_create(user_1['token'], 'Group 1', False)
    clear()

def test_access_leave_valid_token2(user_1, logout_user_1):
    """Testing if token is valid in the channels list function.
    """
    # Token should now be invalid.
    with pytest.raises(AccessError):
        channels.channels_list(user_1['token'])
    clear()

def test_access_leave_valid_token3(user_1, logout_user_1):
    """Testing if token is valid in the channels list all functions.
    """
    # Token should now be invalid.
    with pytest.raises(AccessError):
        channels.channels_listall(user_1['token'])
    clear()
