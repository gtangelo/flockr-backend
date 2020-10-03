import pytest
import channels, channel, auth
from error import InputError, AccessError
from other import clear

'''
Tests for channels.py
'''

# Tokens are set to be the user's email.

#------------------------------------------------------------------------------#
#                               channels_create                                #
#------------------------------------------------------------------------------#

# Test for a create channel (We create 2 channels and test whether the 2 channel id's are unique).
def test_channels_create():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    auth.auth_login('testEmail@gmail.com', 'password123')

    # Create 2 new channels.
    new_channel_1 = channels.channels_create(test_user['token'], 'Channel_1', True)
    new_channel_2 = channels.channels_create(test_user['token'], 'Channel_2', True)

    # Ensure that they are unique.
    assert new_channel_1['channel_id'] is not new_channel_2['channel_id']
    clear()

# Verify if channel id is unique (Since leaving a channel as the only member should destroy the channel).
def test_create_unique_id():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    auth.auth_login('testEmail@gmail.com', 'password123')

    new_channel = channels.channels_create(test_user['token'], 'Channel_1', True)
    channel1_id = new_channel['channel_id']
    channel.channel_leave(test_user['token'], new_channel['channel_id'])
    new_channel2 = channels.channels_create(test_user['token'], 'Channel_2', True)
    channel2_id = new_channel2['channel_id']

    assert channel1_id != channel2_id
    clear()

# Testing for an invalid channel name (Invalid when name is outside the range of 0-20 (inclusive) characters).
def test_channels_invalid():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    auth.auth_login('testEmail@gmail.com', 'password123')

    with pytest.raises(InputError) as e:
        channels.channels_create(test_user['token'], 'Invalid_Channels_Name', True)
    clear()

# Test for whether user automatically becomes a member of their created channel.
def test_channels_create_member():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    auth.auth_login('testEmail@gmail.com', 'password123')
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
    auth.auth_login('testEmail@gmail.com', 'password123')
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
    auth.auth_login('testEmail@gmail.com', 'password123')
    test_user2 = auth.auth_register('test2Email@gmail.com', 'password123', 'Jon', 'Snow')
    auth.auth_login('test2Email@gmail.com', 'password123')
    new_channel = channels.channels_create(test_user['token'], 'Channel_1', False)

    with pytest.raises(AccessError) as e:
        channel.channel_join(test_user2['token'], new_channel['channel_id'])
    clear()


# Test for 0 character name. 
def test_channels_create_0char():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    auth.auth_login('testEmail@gmail.com', 'password123')

    with pytest.raises(InputError) as e:
        channels.channels_create(test_user['token'], '', False)
    clear()

# Test for 1 character name.
def test_channels_create_1char():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    auth.auth_login('testEmail@gmail.com', 'password123')
    new_channel = channels.channels_create(test_user['token'], '1', False)

    assert 'channel_id' in new_channel
    clear()

# Test for 20 character name. 
def test_channels_create_20char():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    auth.auth_login('testEmail@gmail.com', 'password123')
    new_channel = channels.channels_create(test_user['token'], 'Channel_Name12345678', False)

    assert 'channel_id' in new_channel
    clear()

# Test for 21 character name.
def test_channels_create_21char():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    auth.auth_login('testEmail@gmail.com', 'password123')

    with pytest.raises(InputError) as e:
        channels.channels_create(test_user['token'], '1', False)
    clear()


#------------------------------------------------------------------------------#
#                               channels_list                                  #
#------------------------------------------------------------------------------#

# Test for multiple created channels.
def test_channels_list():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')
    auth.auth_login('testEmail@gmail.com', 'password123')
    test_user2 = auth.auth_register('test2Email@gmail.com', 'password123', 'Indiana', 'Jones')
    auth.auth_login('test2Email@gmail.com', 'password123')

    # Create new channels.
    channels.channels_create(test_user['token'], 'Channel_1', True)
    channels.channels_create(test_user['token'], 'Channel_2', True)
    channels.channels_create(test_user['token'], 'Channel_3', True)
    channels.channels_create(test_user2['token'], 'Channel_4', False)

    result = channels.channels_list(test_user['token'])

    assert len(result['channels']) == 3
    clear()

# Test for leaving joined channels and then listing joined channels.
def test_channels_leave():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')
    auth.auth_login('testEmail@gmail.com', 'password123')

    # Create new channels.
    new_channel_1 = channels.channels_create(test_user['token'], 'Channel_1', True)
    channels.channels_create(test_user['token'], 'Channel_2', True)
    channels.channels_create(test_user['token'], 'Channel_3', True)

    # Leave the first channel.
    channel.channel_leave(test_user['token'], new_channel_1['channel_id'])

    result = channels.channels_list(test_user['token'])
    
    assert len(result['channels']) == 2
    clear()

# Test for empty channels.
def test_channels_list_empty():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')
    auth.auth_login('testEmail@gmail.com', 'password123')

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
    auth.auth_login('testEmail@gmail.com', 'password123')
    test_user2 = auth.auth_register('test2Email@gmail.com', 'password123', 'Indiana', 'Jones')
    auth.auth_login('test2Email@gmail.com', 'password123')

    # Create new channels.
    channels.channels_create(test_user['token'], 'Channel_1', True)
    channels.channels_create(test_user['token'], 'Channel_2', True)
    channels.channels_create(test_user['token'], 'Channel_3', True)
    channels.channels_create(test_user2['token'], 'Channel_4', True)
    channels.channels_create(test_user2['token'], 'Channel_5', True)

    result = channels.channels_listall(test_user['token'])

    assert len(result['channels']) == 5
    clear()

# Test for empty channels.
def test_channels_listall_empty():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')
    auth.auth_login('testEmail@gmail.com', 'password123')

    list_channels = channels.channels_list(test_user['token']) 

    assert len(list_channels['channels']) == 0
    clear()

# Test for private channels
def test_channels_listall_private():
    clear()
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')
    auth.auth_login('testEmail@gmail.com', 'password123')

    # Channel 1 and 3 are private channels.
    channels.channels_create(test_user['token'], 'Channel_1', False)
    channels.channels_create(test_user['token'], 'Channel_2', True)
    channels.channels_create(test_user['token'], 'Channel_3', False)
    channels.channels_create(test_user['token'], 'Channel_4', True)

    result = channels.channels_listall(test_user['token'])

    assert len(result['channels']) == 4
    clear()

#------------------------------------------------------------------------------#
#                               misc                                           #
#------------------------------------------------------------------------------#

# Testing if token is valid
def test_access_leave_valid_token():
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    new_channel = channels.channels_create(user['token'], 'Group 1', True)
    auth.auth_logout(user['token'])

    with pytest.raises(AccessError):
        channel.channel_leave(user['token'], new_channel['channel_id'])
    clear()