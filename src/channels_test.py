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
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    auth.auth_login('testEmail@gmail.com', 'password123')

    # Create 2 new channels.
    new_channel_1 = channels.channels_create(test_user['token'], 'Channel_1', True)
    new_channel_2 = channels.channels_create(test_user['token'], 'Channel_2', True)

    # Ensure that they are unique.
    assert new_channel_1['channel_id'] is not new_channel_2['channel_id']
    clear()

# Testing for an invalid channel name (Invalid when name is outside the range of 0-20 (inclusive) characters).
def test_channels_invalid():
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    auth.auth_login('testEmail@gmail.com', 'password123')

    with pytest.raises(InputError) as e:
        channels.channels_create(test_user['token'], 'Invalid_Channels_Name', True)
    clear()

# Test for whether user automatically becomes a member of their created channel.
def test_channels_create_member():
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
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    auth.auth_login('testEmail@gmail.com', 'password123')
    test_user2 = auth.auth_register('test2Email@gmail.com', 'password123', 'Jon', 'Snow')
    auth.auth_login('test2Email@gmail.com', 'password123')
    new_channel = channels.channels_create(test_user['token'], 'Channel_1', False)

    with pytest.raises(AccessError) as e:
        channel.channel_join(test_user2['token'], new_channel['channel_id'])
    clear()


#------------------------------------------------------------------------------#
#                               channels_list                                  #
#------------------------------------------------------------------------------#

# Test for multiple created channels.
def test_channels_list():
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')
    auth.auth_login('testEmail@gmail.com', 'password123')

    # Create new channels.
    channels.channels_create(test_user['token'], 'Channel_1', True)
    channels.channels_create(test_user['token'], 'Channel_2', True)
    channels.channels_create(test_user['token'], 'Channel_3', True)
    
    # Join new channels.
    channel.channel_join(test_user['token'], 1)
    channel.channel_join(test_user['token'], 2)

    # Store channels that the user is in into a list.
    result = channels.channels_list(test_user['token'])
    list_channels = []
    for cur_channel in result['channels']:
        list_channels.append(channel['channel_id'])

    assert list_channels == [1, 2]
    clear()

# Test for leaving joined channels and then listing joined channels.
def test_channels_leave():
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')
    auth.auth_login('testEmail@gmail.com', 'password123')

    # Create new channels.
    channels.channels_create(test_user['token'], 'Channel_1', True)
    channels.channels_create(test_user['token'], 'Channel_2', True)
    channels.channels_create(test_user['token'], 'Channel_3', True)

    # Join the first 2 channels and then leave the first channel.
    channel.channel_join(test_user['token'], 1)
    channel.channel_join(test_user['token'], 2)
    channel.channel_leave(test_user['token'], 1)

    result = channels.channels_list(test_user['token'])

    assert result[0]['channel_id'] == 2
    clear()

# Test for empty channels.
def test_channels_list_empty():
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')
    auth.auth_login('testEmail@gmail.com', 'password123')


    clear()


#------------------------------------------------------------------------------#
#                               channels_listall                               #
#------------------------------------------------------------------------------#

# Test list all channels.
def test_channels_listall():
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')
    auth.auth_login('testEmail@gmail.com', 'password123')

    # Create new channels.
    channels.channels_create(test_user['token'], 'Channel_1', True)
    channels.channels_create(test_user['token'], 'Channel_2', True)
    channels.channels_create(test_user['token'], 'Channel_3', True)
    channels.channels_create(test_user['token'], 'Channel_4', True)

    result = channels.channels_listall(test_user['token'])

    list_channels = []
    for channel in result['channels']:
        list_channels.append(channel['channel_id'])

    #FIX THIS (Can't guarantee that channels_listall will list them in the order that they were created)
    assert list_channels == [1, 2, 3, 4]
    clear()

# Test for empty channels.
def test_channels_listall_empty():

    clear()