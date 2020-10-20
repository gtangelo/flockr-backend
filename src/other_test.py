"""
other feature test implementation to test functions in channels.py

2020 T3 COMP1531 Major Project
"""

import pytest
import auth
import channel
import channels
import message
from other import clear, admin_userpermission_change, users_all, search
from action import convert_token_to_user
from error import AccessError, InputError
from data import data

OWNER = 1
MEMBER = 2

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
    auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    clear()
    assert data['active_users'] == []
    assert data['users'] == []
    assert data['channels'] == []
    assert data['first_owner_u_id'] is None
    assert data['total_messages'] is None

def test_clear_active_users():
    """Test if clear works on active users
    """
    clear()
    auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    clear()

    assert data['active_users'] == []
    assert data['users'] == []
    assert data['channels'] == []
    assert data['first_owner_u_id'] is None
    assert data['total_messages'] is None


def test_clear_channel():
    """Test if clear works on channel
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    channels.channels_create(user_1['token'], 'Group 1', True)
    clear()

    assert data['active_users'] == []
    assert data['users'] == []
    assert data['channels'] == []
    assert data['first_owner_u_id'] is None
    assert data['total_messages'] is None


def test_clear_channel_and_information():
    """Test if clear works on channel and its information
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)

    assert channel.channel_invite(user_1['token'], new_channel['channel_id'], user_2['u_id']) == {}
    clear()

    assert data['active_users'] == []
    assert data['users'] == []
    assert data['channels'] == []
    assert data['first_owner_u_id'] is None
    assert data['total_messages'] is None


#------------------------------------------------------------------------------#
#                         admin_userpermission_change                          #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_access_admin_valid_token():
    """Test if token is invalid does not refer to a valid user
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_logout(user['token'])
    with pytest.raises(AccessError):
        admin_userpermission_change(user["token"], user["u_id"], OWNER)
    with pytest.raises(AccessError):
        admin_userpermission_change(user["token"], user["u_id"], MEMBER)
    with pytest.raises(AccessError):
        admin_userpermission_change("INVALID", user["u_id"], MEMBER)
    clear()

def test_input_admin_valid_u_id():
    """u_id does not refer to a valid user
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    with pytest.raises(InputError):
        admin_userpermission_change(user["token"], user["u_id"] + 1, OWNER)
    with pytest.raises(InputError):
        admin_userpermission_change(user["token"], user["u_id"] - 1, MEMBER)
    clear()

def test_input_admin_valid_permission_id():
    """permission_id does not refer to a value permission
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    with pytest.raises(InputError):
        admin_userpermission_change(user["token"], user["u_id"], -1)
    with pytest.raises(InputError):
        admin_userpermission_change(user["token"], user["u_id"], 0)
    with pytest.raises(InputError):
        admin_userpermission_change(user["token"], user["u_id"], 2)
    clear()

def test_input_admin_first_owner_changes_to_member():
    """Test whether the first flockr owner cannot change themselves to a member
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    with pytest.raises(InputError):
        admin_userpermission_change(user["token"], user["u_id"], MEMBER)
    clear()

def test_input_admin_owner_change_first_owner_to_member():
    """Test whether the another flockr owner cannot change the first flockr owner
    to a member
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    admin_userpermission_change(user_1["token"], user_2["u_id"], OWNER)
    with pytest.raises(InputError):
        admin_userpermission_change(user_2["token"], user_1["u_id"], MEMBER)
    clear()

def test_access_admin_not_owner_own():
    """Testing whether a member can change their own permissions
    """
    clear()
    auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    with pytest.raises(AccessError):
        admin_userpermission_change(user_2["token"], user_2["u_id"], OWNER)
    with pytest.raises(AccessError):
        admin_userpermission_change(user_2["token"], user_2["u_id"], MEMBER)
    clear()

def test_access_admin_not_owner_else_owner():
    """Testing whether a member can change someone else's permissions to owner
    """
    clear()
    auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    user_3 = auth.auth_register('jacesmith@gmail.com', 'password', 'Jace', 'Smith')
    with pytest.raises(AccessError):
        admin_userpermission_change(user_2["token"], user_3["u_id"], OWNER)
    clear()

def test_access_admin_not_owner_else_member():
    """Testing whether a member can change someone else's permissions to member
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    user_3 = auth.auth_register('jacesmith@gmail.com', 'password', 'Jace', 'Smith')
    admin_userpermission_change(user_1["token"], user_3["u_id"], OWNER)
    with pytest.raises(AccessError):
        admin_userpermission_change(user_2["token"], user_3["u_id"], MEMBER)
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_output_admin_owner_change_member_to_owner():
    """Test whether a member has become a flockr owner by joining a private channel
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    admin_userpermission_change(user_1["token"], user_2["u_id"], OWNER)
    channel_info = channels.channels_create(user_1['token'], "Group 1", False)
    # Owner can join any channels including private
    # Testing user, with now as flockr owner to join private channel
    channel.channel_join(user_2['token'], channel_info['channel_id'])
    clear()

def test_output_admin_owner_change_member_to_owner_logout():
    """Testing whether the permission change carry through after user logout and
    logs back in.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    admin_userpermission_change(user_1["token"], user_2["u_id"], OWNER)
    auth.auth_logout(user_2["token"])
    channel_info = channels.channels_create(user_1['token'], "Group 1", False)
    user_2 = auth.auth_login('janesmith@gmail.com', 'password')
    # Owner can join any channels including private
    # Testing user, with now as flockr owner to join private channel
    channel.channel_join(user_2['token'], channel_info['channel_id'])
    clear()

def test_output_admin_owner_change_owner_to_member():
    """Test whether an owner successfully change another owner to a member
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    admin_userpermission_change(user_1["token"], user_2["u_id"], OWNER)
    channel_info = channels.channels_create(user_1['token'], "Group 1", False)
    admin_userpermission_change(user_1["token"], user_2["u_id"], MEMBER)
    with pytest.raises(AccessError):
        channel.channel_join(user_2['token'], channel_info['channel_id'])
    clear()

def test_output_admin_owner_change_owner_to_member_logout():
    """Test whether permission change carry through after logout
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    admin_userpermission_change(user_1["token"], user_2["u_id"], OWNER)
    channel_info = channels.channels_create(user_1['token'], "Group 1", False)
    admin_userpermission_change(user_1["token"], user_2["u_id"], MEMBER)
    auth.auth_logout(user_2['token'])
    user_2 = auth.auth_login('janesmith@gmail.com', 'password')
    with pytest.raises(AccessError):
        channel.channel_join(user_2['token'], channel_info['channel_id'])
    clear()

def test_output_admin_owner_change_to_member():
    """Test whether the an owner can set themselves as an member
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    admin_userpermission_change(user_1["token"], user_2["u_id"], OWNER)
    channel_info = channels.channels_create(user_1['token'], "Group 1", False)
    admin_userpermission_change(user_2["token"], user_2["u_id"], MEMBER)
    with pytest.raises(AccessError):
        channel.channel_join(user_2['token'], channel_info['channel_id'])
    clear()

def test_output_admin_owner_change_to_owner():
    """Test whether an owner is changed to an owner, the function will do nothing.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    admin_userpermission_change(user_1["token"], user_2["u_id"], OWNER)
    channel_info = channels.channels_create(user_1['token'], "Group 1", False)
    channel.channel_join(user_2['token'], channel_info['channel_id'])
    channel.channel_leave(user_2['token'], channel_info['channel_id'])
    admin_userpermission_change(user_2["token"], user_2["u_id"], OWNER)
    channel.channel_join(user_2['token'], channel_info['channel_id'])
    clear()

def test_output_admin_member_change_to_member():
    """Test whether a member is changed to a member, the function will do nothing.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    channel_info = channels.channels_create(user_1['token'], "Group 1", False)
    with pytest.raises(AccessError):
        channel.channel_join(user_2['token'], channel_info['channel_id'])
    admin_userpermission_change(user_1["token"], user_2["u_id"], MEMBER)
    with pytest.raises(AccessError):
        channel.channel_join(user_2['token'], channel_info['channel_id'])
    clear()

def test_output_admin_owner_change_first_owner_to_owner():
    """Test whether another flockr owner successfully change the first
    flockr owner to an owner (essentially does nothing as permission has not changed)
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    admin_userpermission_change(user_1["token"], user_2["u_id"], OWNER)
    channel_info = channels.channels_create(user_1['token'], "Group 1", False)
    admin_userpermission_change(user_2["token"], user_1["u_id"], OWNER)
    channel.channel_join(user_2['token'], channel_info['channel_id'])
    clear()

#------------------------------------------------------------------------------#
#                                   users_all                                  #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_users_all_valid_token():
    """Test if token does not refer to a valid user
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_logout(user_1['token'])
    with pytest.raises(AccessError):
        users_all(user_1['token'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_users_all():
    """Test if a list all users details is returned
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    user_4 = auth.auth_register('prathsjag@gmail.com', 'password', 'Praths', 'Jag')
    all_users = users_all(user_1['token'])
    user_count = 0
    test_1 = False
    test_2 = False
    test_3 = False
    for user in all_users['users']:
        if user['u_id'] is user_3['u_id']:
            test_1 = True
        if user['u_id'] is user_2['u_id']:
            test_2 = True
        if user['u_id'] is user_4['u_id']:
            test_3 = True
        user_count += 1
    assert user_count == 4
    assert True in (test_1, test_2, test_3)
    clear()

def test_users_all_logout():
    """Test if some users log out, their details are still returned
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    user_4 = auth.auth_register('prathsjag@gmail.com', 'password', 'Praths', 'Jag')
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])
    all_users = users_all(user_1['token'])
    user_count = 0
    test_1 = False
    test_2 = False
    for user in all_users['users']:
        if user['u_id'] is user_3['u_id']:
            test_1 = True
        if user['u_id'] is user_2['u_id']:
            test_2 = True
        user_count += 1
    assert user_count == 4
    assert True in (test_1, test_2)
    clear()

#------------------------------------------------------------------------------#
#                                   search                                     #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_search_valid_token():
    """Test if token does not refer to a valid user
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_logout(user_1['token'])
    with pytest.raises(AccessError):
        search(user_1['token'], "Test")
    clear()

def test_search_invalid_query_str():
    """Test if query string is less than a character
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    with pytest.raises(InputError):
        search(user['token'], "")
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_search_standard():
    """Test searching messages in multiple channels
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    user_4 = auth.auth_register('prathsjag@gmail.com', 'password', 'Praths', 'Jag')
    channel_1 = channels.channels_create(user_1['token'], 'Group 1', True)
    channel_2 = channels.channels_create(user_2['token'], 'Group 2', True)
    channel_3 = channels.channels_create(user_3['token'], 'Group 3', True)
    channel_4 = channels.channels_create(user_4['token'], 'Group 4', True)
    message_str_1 = "Welcome to group 1!"
    message_str_2 = "Welcome to group 2!"
    message_str_3 = "Welcome to group 3!"
    message_str_4 = "Welcome to group 4!"
    message_str_5 = "Hiya guys!"
    message_str_6 = "sup"
    message_str_7 = "Let's get down to business!"
    query_str = "Welcome"
    channel.channel_join(user_1['token'], channel_2['channel_id'])
    channel.channel_join(user_1['token'], channel_3['channel_id'])
    channel.channel_join(user_1['token'], channel_4['channel_id'])
    message.message_send(user_1['token'], channel_1['channel_id'], message_str_1)
    message.message_send(user_2['token'], channel_2['channel_id'], message_str_2)
    message.message_send(user_3['token'], channel_3['channel_id'], message_str_3)
    message.message_send(user_4['token'], channel_4['channel_id'], message_str_4)
    message.message_send(user_1['token'], channel_1['channel_id'], message_str_5)
    message.message_send(user_1['token'], channel_2['channel_id'], message_str_6)
    message.message_send(user_1['token'], channel_2['channel_id'], message_str_7)
    msg_list = search(user_1['token'], query_str)
    msg_count = 0
    msg_cmp_2 = []
    for msg in msg_list['messages']:
        msg_cmp_2.append(msg['message'])
        msg_count += 1
    assert msg_count == 4
    msg_cmp_1 = [message_str_1, message_str_2, message_str_3, message_str_4]
    msg_cmp_1.sort()
    msg_cmp_2.sort()
    assert msg_cmp_1 == msg_cmp_2
    clear()

def test_search_no_match():
    """Test searching messages with 0 results
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    channel_1 = channels.channels_create(user_1['token'], 'Group 1', True)
    message_str_1 = "Welcome to group 1!"
    query_str = "ZzZ"
    message.message_send(user_1['token'], channel_1['channel_id'], message_str_1)
    msg_list = search(user_1['token'], query_str)
    assert len(msg_list['messages']) == 0
    clear()

def test_search_not_in_channel():
    """Test searching messages when the user has not been part of the channel before
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    channel_1 = channels.channels_create(user_2['token'], 'Group 1', True)
    query_str = "ZzZ"
    message.message_send(user_2['token'], channel_1['channel_id'], query_str)
    msg_list = search(user_1['token'], query_str)
    assert len(msg_list['messages']) == 0
    clear()

def test_search_leave_channel():
    """Test searching messages when user has left channel the channel
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    channel_1 = channels.channels_create(user_1['token'], 'Group 1', True)
    query_str = "ZzZ"
    message.message_send(user_1['token'], channel_1['channel_id'], query_str)
    channel.channel_leave(user_1['token'], channel_1['channel_id'])
    msg_list = search(user_1['token'], query_str)
    assert len(msg_list['messages']) == 0
    clear()
