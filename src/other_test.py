"""
other feature test implementation to test functions in channels.py

2020 T3 COMP1531 Major Project
"""

import pytest
import auth
import channel
import channels
from other import clear
from data import data

#------------------------------------------------------------------------------#
#                                     clear                                    #
#------------------------------------------------------------------------------#

def test_clear_users():
    """Test if the list of active users has been cleared
    """
    clear()
    auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    clear()

    assert data['users'] == []

def test_clear_intermediately():
    """Test if clear works intermediately
    """
    clear()
    auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
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

def test_clear_active_users():
    """Test if clear works on active users
    """
    clear()
    auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    clear()

    assert data['active_users'] == []

def test_clear_channel():
    """Test if clear works on channel
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    channels.channels_create(user_1['token'], 'Group 1', True)
    clear()

    assert data['channels'] == []

def test_clear_channel_and_information():
    """Test if clear works on channel and its information
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)

    assert channel.channel_invite(user_1['token'], new_channel['channel_id'], user_2['u_id']) == {}
    clear()

    assert data['channels'] == []
