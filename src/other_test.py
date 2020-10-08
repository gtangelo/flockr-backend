"""
other feature test implementation to test functions in channels.py

2020 T3 COMP1531 Major Project
"""

import pytest
import auth
import channel
import channels
from error import AccessError, InputError
from other import clear, admin_userpermission_change
from data import data, OWNER, MEMBER

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

#------------------------------------------------------------------------------#
#                         admin_userpermission_change                          #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_access_admin_valid_token():
    """Test if u_id does not refer to a valid user
    """
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_logout(user['token'])
    with pytest.raises(AccessError):
        admin_userpermission_change(user["token"], user["u_id"], OWNER)
        admin_userpermission_change(user["token"], user["u_id"], MEMBER)
        admin_userpermission_change("INVALID", user["u_id"], MEMBER)

def test_input_admin_valid_u_id():
    """u_id does not refer to a valid user
    """
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    with pytest.raises(InputError):
        admin_userpermission_change(user["token"], user["u_id"] + 1, OWNER)
        admin_userpermission_change(user["token"], user["u_id"] - 1, MEMBER)

def test_input_admin_valid_permission_id():
    """permission_id does not refer to a value permission
    """
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    with pytest.raises(InputError):
        admin_userpermission_change(user["token"], user["u_id"], -1)
        admin_userpermission_change(user["token"], user["u_id"], 0)
        admin_userpermission_change(user["token"], user["u_id"], 2)

def test_access_admin_not_owner_own():
    """Testing whether a member can change their own permissions
    """
    auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    with pytest.raises(InputError):
        admin_userpermission_change(user_2["token"], user_2["u_id"], OWNER)
        admin_userpermission_change(user_2["token"], user_2["u_id"], MEMBER)

def test_access_admin_not_owner_else():
    """Testing whether a member can change someone else's permissions to owner
    """
    auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    user_3 = auth.auth_register('jacesmith@gmail.com', 'password', 'Jace', 'Smith')
    with pytest.raises(InputError):
        admin_userpermission_change(user_2["token"], user_3["u_id"], OWNER)

def test_access_admin_not_owner_else():
    """Testing whether a member can change someone else's permissions to member
    """
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    user_3 = auth.auth_register('jacesmith@gmail.com', 'password', 'Jace', 'Smith')
    admin_userpermission_change(user_1["token"], user_3["u_id"], OWNER)
    with pytest.raises(InputError):
        admin_userpermission_change(user_2["token"], user_3["u_id"], MEMBER)

#?------------------------------ Output Testing ------------------------------?#
