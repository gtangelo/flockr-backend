import auth, channel, channels
from other import clear
from data import data

#------------------------------------------------------------------------------#
#                                     clear                                    #
#------------------------------------------------------------------------------#

# Test if the list of active users has been cleared
def test_clear_users():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    clear()

    assert data['users'] == []

# Test if clear works intermediately 
def test_clear_intermediately():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    clear()
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith') 

    assert data['users'] == [
        {
            'u_id': user_2['u_id'],
            'email': 'janesmith@gmail.com',
            'password': 'password',
            'name_first': 'Jane',
            'name_last': 'Smith',
            'handle_str': 'jsmith',
            # List of channels that the user is a part of
            'channels': [],
            'is_flockr_owner': True,
        }
    ]
    clear()

# Test if clear works on active users
def test_clear_active_users():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    clear()

    assert data['active_users'] == []

# Test if clear works on channel
def test_clear_channel():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    channel = channels.channels_create(user_1['token'], 'Group 1', True)
    clear()

    assert data['channels'] == []

# Test if clear works on channel and its information
def test_clear_channel_and_information():
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)

    assert channel.channel_invite(user_1['token'], new_channel['channel_id'], user_2['u_id']) == {}
    clear()

    assert data['channels'] == []
