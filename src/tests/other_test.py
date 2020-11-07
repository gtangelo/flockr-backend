"""
other feature test implementation to test functions in other.py

2020 T3 COMP1531 Major Project
"""

import pytest
import pickle

import src.feature.auth as auth
import src.feature.channel as channel
import src.feature.channels as channels
import src.feature.message as message

from src.feature.other import clear, admin_userpermission_change, users_all, search
from src.feature.error import AccessError, InputError

from src.globals import OWNER, MEMBER

#------------------------------------------------------------------------------#
#                                     clear                                    #
#------------------------------------------------------------------------------#

def test_clear_users(user_1, user_2):
    """Test if the list of active users has been cleared
    """
    data = pickle.load(open("data.p", "rb"))
    assert len(data.get_users()) == 2
    assert len(data.get_active_users()) == 2
    clear()
    data = pickle.load(open("data.p", "rb"))
    assert len(data.get_users()) == 0
    assert len(data.get_active_users()) == 0

def test_clear_channel(user_1, public_channel_1, private_channel_1):
    """Test if clear works on channel
    """
    data = pickle.load(open("data.p", "rb"))
    assert len(data.get_channels()) == 2
    clear()
    data = pickle.load(open("data.p", "rb"))
    assert len(data.get_channels()) == 0

def test_clear_reset_data(user_1, user_2, public_channel_1):
    """Test if clear resets the data structure
    """
    data = pickle.load(open("data.p", "rb"))
    assert data.get_users() != []
    assert data.get_active_users() != []
    assert data.get_channels() != []
    assert data.get_first_owner_u_id() == user_1['u_id']
    assert data.get_total_messages() == 0
    clear()
    data = pickle.load(open("data.p", "rb"))
    assert data.get_users() == []
    assert data.get_active_users() == []
    assert data.get_channels() == []
    assert data.get_first_owner_u_id() == None
    assert data.get_total_messages() == 0


#------------------------------------------------------------------------------#
#                         admin_userpermission_change                          #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_access_admin_valid_token(user_1):
    """Test if token is invalid does not refer to a valid user
    """
    auth.auth_logout(user_1['token'])
    with pytest.raises(AccessError):
        admin_userpermission_change(user_1["token"], user_1["u_id"], OWNER)
    with pytest.raises(AccessError):
        admin_userpermission_change(user_1["token"], user_1["u_id"], MEMBER)
    with pytest.raises(AccessError):
        admin_userpermission_change("INVALID", user_1["u_id"], MEMBER)
    clear()

def test_input_admin_valid_u_id(user_1):
    """u_id does not refer to a valid user
    """
    with pytest.raises(InputError):
        admin_userpermission_change(user_1["token"], user_1["u_id"] + 1, OWNER)
    with pytest.raises(InputError):
        admin_userpermission_change(user_1["token"], user_1["u_id"] - 1, MEMBER)
    clear()

def test_input_admin_valid_permission_id(user_1):
    """permission_id does not refer to a value permission
    """
    with pytest.raises(InputError):
        admin_userpermission_change(user_1["token"], user_1["u_id"], -1)
    with pytest.raises(InputError):
        admin_userpermission_change(user_1["token"], user_1["u_id"], 0)
    with pytest.raises(InputError):
        admin_userpermission_change(user_1["token"], user_1["u_id"], 2)
    clear()

def test_input_admin_first_owner_changes_to_member(user_1):
    """Test whether the first flockr owner cannot change themselves to a member
    """
    with pytest.raises(InputError):
        admin_userpermission_change(user_1["token"], user_1["u_id"], MEMBER)
    clear()

def test_input_admin_owner_change_first_owner_to_member(user_1, user_2):
    """Test whether the another flockr owner cannot change the first flockr owner
    to a member
    """
    admin_userpermission_change(user_1["token"], user_2["u_id"], OWNER)
    with pytest.raises(InputError):
        admin_userpermission_change(user_2["token"], user_1["u_id"], MEMBER)
    clear()

def test_access_admin_not_owner_own(user_1, user_2):
    """Testing whether a member can change their own permissions
    """
    with pytest.raises(AccessError):
        admin_userpermission_change(user_2["token"], user_2["u_id"], OWNER)
    with pytest.raises(AccessError):
        admin_userpermission_change(user_2["token"], user_2["u_id"], MEMBER)
    clear()

def test_access_admin_not_owner_else_owner(user_1, user_2, user_3):
    """Testing whether a member can change someone else's permissions to owner
    """
    with pytest.raises(AccessError):
        admin_userpermission_change(user_2["token"], user_3["u_id"], OWNER)
    clear()

def test_access_admin_not_owner_else_member(user_1, user_2, user_3):
    """Testing whether a member can change someone else's permissions to member
    """
    admin_userpermission_change(user_1["token"], user_3["u_id"], OWNER)
    with pytest.raises(AccessError):
        admin_userpermission_change(user_2["token"], user_3["u_id"], MEMBER)
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_output_admin_owner_change_member_to_owner(user_1, user_2):
    """Test whether a member has become a flockr owner by joining a private channel
    """
    admin_userpermission_change(user_1["token"], user_2["u_id"], OWNER)
    channel_info = channels.channels_create(user_1['token'], "Group 1", False)
    # Owner can join any channels including private
    # Testing user, with now as flockr owner to join private channel
    channel.channel_join(user_2['token'], channel_info['channel_id'])
    clear()

def test_output_admin_owner_change_member_to_owner_logout(user_1, user_2, public_channel_1):
    """Testing whether the permission change carry through after user logout and
    logs back in.
    """
    admin_userpermission_change(user_1["token"], user_2["u_id"], OWNER)
    auth.auth_logout(user_2["token"])
    user_2 = auth.auth_login('janesmith@gmail.com', 'password')
    # Owner can join any channels including private
    # Testing user, with now as flockr owner to join private channel
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])
    clear()

def test_output_admin_owner_change_owner_to_member(user_1, user_2, private_channel_1):
    """Test whether an owner successfully change another owner to a member
    """
    admin_userpermission_change(user_1["token"], user_2["u_id"], OWNER)
    admin_userpermission_change(user_1["token"], user_2["u_id"], MEMBER)
    with pytest.raises(AccessError):
        channel.channel_join(user_2['token'], private_channel_1['channel_id'])
    clear()

def test_output_admin_owner_change_owner_to_member_logout(user_1, user_2, private_channel_1):
    """Test whether permission change carry through after logout
    """
    admin_userpermission_change(user_1["token"], user_2["u_id"], OWNER)
    admin_userpermission_change(user_1["token"], user_2["u_id"], MEMBER)
    auth.auth_logout(user_2['token'])
    user_2 = auth.auth_login('janesmith@gmail.com', 'password')
    with pytest.raises(AccessError):
        channel.channel_join(user_2['token'], private_channel_1['channel_id'])
    clear()

def test_output_admin_owner_change_to_member(user_1, user_2, private_channel_1):
    """Test whether the an owner can set themselves as an member
    """
    admin_userpermission_change(user_1["token"], user_2["u_id"], OWNER)
    admin_userpermission_change(user_2["token"], user_2["u_id"], MEMBER)
    with pytest.raises(AccessError):
        channel.channel_join(user_2['token'], private_channel_1['channel_id'])
    clear()

def test_output_admin_owner_change_to_owner(user_1, user_2, public_channel_1):
    """Test whether an owner is changed to an owner, the function will do nothing.
    """
    admin_userpermission_change(user_1["token"], user_2["u_id"], OWNER)
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])
    channel.channel_leave(user_2['token'], public_channel_1['channel_id'])
    admin_userpermission_change(user_2["token"], user_2["u_id"], OWNER)
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])
    clear()

def test_output_admin_member_change_to_member(user_1, user_2, private_channel_1):
    """Test whether a member is changed to a member, the function will do nothing.
    """
    with pytest.raises(AccessError):
        channel.channel_join(user_2['token'], private_channel_1['channel_id'])
    admin_userpermission_change(user_1["token"], user_2["u_id"], MEMBER)
    with pytest.raises(AccessError):
        channel.channel_join(user_2['token'], private_channel_1['channel_id'])
    clear()

def test_output_admin_owner_change_first_owner_to_owner(user_1, user_2, public_channel_1):
    """Test whether another flockr owner successfully change another the first
    flockr owner to an owner (essentially does nothing as permission has not changed)
    """
    admin_userpermission_change(user_1["token"], user_2["u_id"], OWNER)
    admin_userpermission_change(user_2["token"], user_1["u_id"], OWNER)
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])
    clear()

#------------------------------------------------------------------------------#
#                                   users_all                                  #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_users_all_valid_token(user_1):
    """Test if token does not refer to a valid user
    """
    auth.auth_logout(user_1['token'])
    with pytest.raises(AccessError):
        users_all(user_1['token'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_users_all(user_1, user_2, user_3, user_4):
    """Test if a list all users details is returned
    """
    all_users = users_all(user_1['token'])
    user_count = 0
    test_1 = False
    test_2 = False
    test_3 = False
    test_4 = False
    for user in all_users['users']:
        if user['u_id'] is user_1['u_id']:
            test_1 = True
        if user['u_id'] is user_2['u_id']:
            test_2 = True
        if user['u_id'] is user_3['u_id']:
            test_3 = True
        if user['u_id'] is user_4['u_id']:
            test_4 = True
        user_count += 1
    assert user_count == 4
    assert test_1
    assert test_2
    assert test_3
    assert test_4
    clear()

def test_users_all_logout(user_1, user_2, user_3, user_4):
    """Test if some users log out, their details are still returned
    """
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])
    all_users = users_all(user_1['token'])
    user_count = 0
    test_1 = False
    test_2 = False
    test_3 = False
    for user in all_users['users']:
        if user['u_id'] is user_1['u_id']:
            test_1 = True
        if user['u_id'] is user_2['u_id']:
            test_2 = True
        if user['u_id'] is user_3['u_id']:
            test_3 = True
        user_count += 1
    assert user_count == 4
    assert test_1
    assert test_2
    assert test_3
    clear()

#------------------------------------------------------------------------------#
#                                   search                                     #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_search_valid_token(user_1):
    """Test if token does not refer to a valid user
    """
    auth.auth_logout(user_1['token'])
    with pytest.raises(AccessError):
        search(user_1['token'], "Test")
    clear()

def test_search_invalid_query_str(user_1):
    """Test if query string is less than a character
    """
    with pytest.raises(InputError):
        search(user_1['token'], "")
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_search_standard(user_1, user_2, user_3, user_4, public_channel_1, public_channel_2, public_channel_3, public_channel_4):
    """Test searching messages in multiple channels
    """
    message_str_1 = "Welcome to group 1!"
    message_str_2 = "Welcome to group 2!"
    message_str_3 = "Welcome to group 3!"
    message_str_4 = "Welcome to group 4!"
    message_str_5 = "Hiya guys!"
    message_str_6 = "sup"
    message_str_7 = "Let's get down to business!"
    query_str = "Welcome"
    channel.channel_join(user_1['token'], public_channel_2['channel_id'])
    channel.channel_join(user_1['token'], public_channel_3['channel_id'])
    channel.channel_join(user_1['token'], public_channel_4['channel_id'])
    message.message_send(user_1['token'], public_channel_1['channel_id'], message_str_1)
    message.message_send(user_2['token'], public_channel_2['channel_id'], message_str_2)
    message.message_send(user_3['token'], public_channel_3['channel_id'], message_str_3)
    message.message_send(user_4['token'], public_channel_4['channel_id'], message_str_4)
    message.message_send(user_1['token'], public_channel_1['channel_id'], message_str_5)
    message.message_send(user_1['token'], public_channel_2['channel_id'], message_str_6)
    message.message_send(user_1['token'], public_channel_2['channel_id'], message_str_7)
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

def test_search_no_match(user_1, public_channel_1):
    """Test searching messages with 0 results
    """
    message_str_1 = "Welcome to group 1!"
    query_str = "ZzZ"
    message.message_send(user_1['token'], public_channel_1['channel_id'], message_str_1)
    msg_list = search(user_1['token'], query_str)
    assert len(msg_list['messages']) == 0
    clear()

def test_search_not_in_channel(user_1, user_2, public_channel_1):
    """Test searching messages when the user is not part of the channel.
    """
    query_str = "ZzZ"
    message.message_send(user_1['token'], public_channel_1['channel_id'], query_str)
    msg_list = search(user_2['token'], query_str)
    assert len(msg_list['messages']) == 0
    clear()

def test_search_leave_channel(user_1, public_channel_1):
    """Test searching messages when user has left channel the channel
    """
    query_str = "ZzZ"
    message.message_send(user_1['token'], public_channel_1['channel_id'], query_str)
    channel.channel_leave(user_1['token'], public_channel_1['channel_id'])
    msg_list = search(user_1['token'], query_str)
    assert len(msg_list['messages']) == 0
    clear()
