"""
user feature test implementation to test functions in user.py

Feature implementation was written by Christian Ilagan and Richard Quisumbing.

2020 T3 COMP1531 Major Project
"""

import pytest

import src.feature.auth as auth
import src.feature.user as user
import src.feature.channel as channel
import src.feature.channels as channels

from src.feature.other import clear, users_all
from src.feature.error import AccessError, InputError

#------------------------------------------------------------------------------#
#                                 user_profile                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_user_authorised_user(user_1, logout_user_1):
    """Test for returning profile of a non-registered/invalid user. (Invalid token
    and u_id)
    """
    with pytest.raises(AccessError):
        user.user_profile(user_1['token'], user_1['u_id'])
    clear()

def test_user_u_id(user_1):
    """Test for returning the profile of a non-existant user.
    """
    with pytest.raises(InputError):
        user.user_profile(user_1['token'], user_1['u_id'] + 1)
    clear()

#?--------------------------- Output Testing ---------------------------------?#

def test_user_id(user_1):
    """Test whether the user profile u_id matches the u_id returned by auth_register.
    """
    user_details = user.user_profile(user_1['token'], user_1['u_id'])

    assert user_1['u_id'] == user_details['user']['u_id']
    clear()

def test_valid_user_name(user_1, user_2, user_3):
    """Test whether the first and last name of a user is the same as the names in
    user_profile.
    """
    user_1_list = users_all(user_2['token'])
    user_1_profile = user.user_profile(user_2['token'], user_2['u_id'])

    for account in user_1_list['users']:
        if account['u_id'] == user_1_profile['user']['u_id']:
            assert user_1_profile['user']['name_first'] == account['name_first']
            assert user_1_profile['user']['name_last'] == account['name_last']

def test_valid_user_email(user_1, user_2, user_3):
    """Test whether the user's email matches the email in user_profile.
    """
    user_1_list = users_all(user_3['token'])
    user_1_profile = user.user_profile(user_3['token'], user_3['u_id'])

    for account in user_1_list['users']:
        if account['u_id'] == user_1_profile['user']['u_id']:
            assert user_1_profile['user']['email'] == account['email']

def test_valid_user_handle_str(user_1, user_2, user_3):
    """Test whether the user's handle string matches the handle string in
    user_profile.
    """
    user_1_list = users_all(user_2['token'])
    user_1_profile = user.user_profile(user_2['token'], user_2['u_id'])

    for account in user_1_list['users']:
        if account['u_id'] == user_1_profile['user']['u_id']:
            assert user_1_profile['user']['handle_str'] == account['handle_str']

#------------------------------------------------------------------------------#
#                              user_profile_setname                            #
#------------------------------------------------------------------------------#
def test_update_name(user_1):
    """ Testing the basic functionality of updating a name
    """
    user.user_profile_setname(user_1['token'], 'Bobby', 'Smith')
    user_list = users_all(user_1['token'])
    for account in user_list['users']:
        if account['u_id'] == user_1['u_id']:
            assert account['name_first'] == 'Bobby'
            assert account['name_last'] == 'Smith'
    clear()

def test_update_name_first(user_1):
    """ Testing the basic functionality of updating only the first name
    """
    user.user_profile_setname(user_1['token'], 'Bobby', 'Ilagan')
    user_list = users_all(user_1['token'])
    for account in user_list['users']:
        if account['u_id'] == user_1['u_id']:
            assert account['name_first'] == 'Bobby'
            assert account['name_last'] == 'Ilagan'
    clear()

def test_update_name_last(user_1):
    """ Testing the basic functionality of updating only the last name
    """
    user.user_profile_setname(user_1['token'], 'Christian', 'Smith')
    user_list = users_all(user_1['token'])
    for account in user_list['users']:
        if account['u_id'] == user_1['u_id']:
            assert account['name_first'] == 'Christian'
            assert account['name_last'] == 'Smith'
    clear()

def test_update_consecutively(user_1):
    """ Testing wheter the same token allows users to continously change their name
    """
    user.user_profile_setname(user_1['token'], 'Bobby', 'Smith')
    user.user_profile_setname(user_1['token'], 'Snake', 'City')
    user_list = users_all(user_1['token'])
    for account in user_list['users']:
        if account['u_id'] == user_1['u_id']:
            assert account['name_first'] == 'Snake'
            assert account['name_last'] == 'City'
            break
    user.user_profile_setname(user_1['token'], 'Goku', 'Vegeta')
    user_list = users_all(user_1['token'])
    for account in user_list['users']:
        if account['u_id'] == user_1['u_id']:
            assert account['name_first'] == 'Goku'
            assert account['name_last'] == 'Vegeta'
            break
    user.user_profile_setname(user_1['token'], 'Will', 'Smith')
    user_list = users_all(user_1['token'])
    for account in user_list['users']:
        if account['u_id'] == user_1['u_id']:
            assert account['name_first'] == 'Will'
            assert account['name_last'] == 'Smith'
            break
    clear()


def test_update_max_name(user_1):
    """ Testing the maximum limits of what a user can change their name to
    """
    user.user_profile_setname(user_1['token'], 'C' * 50, 'Smith')
    user.user_profile_setname(user_1['token'], 'Chris', 'S' * 50)
    user.user_profile_setname(user_1['token'], 'C' * 50, 'S' * 50)
    with pytest.raises(InputError):
        user.user_profile_setname(user_1['token'], 'C' * 51, 'Smith')
    with pytest.raises(InputError):
        user.user_profile_setname(user_1['token'], 'Chris', 'S' * 51)
    with pytest.raises(InputError):
        user.user_profile_setname(user_1['token'], 'C' * 51, 'S' * 51)
    clear()

def test_update_min_name(user_1):
    """ Testing the minimum limits of what a user can change their name to.
    """
    user.user_profile_setname(user_1['token'], 'C', 'S')
    user.user_profile_setname(user_1['token'], 'Chris', 'S')
    user.user_profile_setname(user_1['token'], 'C', 'Smith')
    # empty string does not change the name
    with pytest.raises(InputError):
        user.user_profile_setname(user_1['token'], '', 'Smith')
    with pytest.raises(InputError):
        user.user_profile_setname(user_1['token'], 'Bob', '')
    with pytest.raises(InputError):
        user.user_profile_setname(user_1['token'], '', '')
    clear()

def test_update_invalid_token(user_1, logout_user_1):
    """ Testing user cant change name with an invalid token
    """
    auth.auth_logout(user_1['token'])
    with pytest.raises(InputError):
        user.user_profile_setname(user_1['token'], 'Bobby', 'Smith')
    clear()

def test_update_multiple_users(user_1, user_2, user_3, user_4):
    """ Testing if users name fields are appropiately changed in largely stored data
    """
    user.user_profile_setname(user_3['token'], 'Popcorn', 'Smoothie')
    user.user_profile_setname(user_2['token'], 'Krillin', 'Bulma')
    user_list = users_all(user_1['token'])
    for account in user_list['users']:
        if account['u_id'] == user_2['u_id']:
            assert account['name_first'] == 'Krillin'
            assert account['name_last'] == 'Bulma'
        if account['u_id'] == user_3['u_id']:
            assert account['name_first'] == 'Popcorn'
            assert account['name_last'] == 'Smoothie'
        if account['u_id'] == user_1['u_id']:
            assert account['name_first'] == 'John'
            assert account['name_last'] == 'Smith'
        if account['u_id'] == user_4['u_id']:
            assert account['name_first'] == 'Janice'
            assert account['name_last'] == 'Smith'
    clear()

def test_invalid_chars(user_1):
    """ Testing if non english alphabets are rejected, with the exception of '-'
    """
    with pytest.raises(InputError):
        user.user_profile_setname(user_1['token'], 'A92!0F', 'Smith')
    with pytest.raises(InputError):
        user.user_profile_setname(user_1['token'], 'Smith', 'A92!0F')
    with pytest.raises(InputError):
        user.user_profile_setname(user_1['token'], 'A92!0F', 'A92!0F')
    clear()

def test_change_channel_data(user_1, user_2):
    """ Testing that name is updated in channels section in data structure.
    """
    # creating a new channel
    new_channel = channels.channels_create(user_1['token'], 'Group 1', True)
    channel.channel_invite(user_1['token'], new_channel['channel_id'], user_2['u_id'])
    channel.channel_join(user_2['token'], new_channel['channel_id'])
    channel.channel_addowner(user_1['token'], new_channel['channel_id'], user_2['u_id'])
    details = channel.channel_details(user_1['token'], new_channel['channel_id'])
    for member in details['all_members']:
        if member['u_id'] == user_1['u_id']:
            assert member['name_first'] == 'John'
            assert member['name_last'] == 'Smith'
        if member['u_id'] == user_2['u_id']:
            assert member['name_first'] == 'Jane'
            assert member['name_last'] == 'Smith'

    for owner in details['owner_members']:
        if owner['u_id'] == user_1['u_id']:
            assert owner['name_first'] == 'John'
            assert owner['name_last'] == 'Smith'
        if owner['u_id'] == user_2['u_id']:
            assert owner['name_first'] == 'Jane'
            assert owner['name_last'] == 'Smith'

    user.user_profile_setname(user_2['token'], 'Bobby', 'Wills')
    for member in details['all_members']:
        if member['u_id'] == user_2['u_id']:
            assert member['name_first'] == 'Bobby'
            assert member['name_last'] == 'Wills'                    
    
    for owner in details['owner_members']:
        if owner['u_id'] == user_2['u_id']:
            assert owner['name_first'] == 'Bobby'
            assert owner['name_last'] == 'Wills'
    clear()

#------------------------------------------------------------------------------#
#                             user_profile_setemail                            #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_user_valid(user_1, logout_user_1):
    """Test for whether the user is logged in and authorised to set their email.
    """
    with pytest.raises(AccessError):
        user.user_profile_setemail(user_1['token'], 'test123@gmail.com')
    clear()

def test_email_already_in_use(user_1, user_2, user_3):
    """Test for an email that is already in use by another active user.
    """
    user.user_profile_setemail(user_1['token'], 'test123@gmail.com')
    user.user_profile_setemail(user_3['token'], 'test987@gmail.com')

    with pytest.raises(InputError):
        user.user_profile_setemail(user_2['token'], 'test123@gmail.com')
    clear()

def test_update_email_same_twice(user_1):
    """Setting the email that the user already has raises an error.
    """
    user.user_profile_setemail(user_1['token'], 'test123@gmail.com')

    with pytest.raises(InputError):
        user.user_profile_setemail(user_1['token'], 'test123@gmail.com')
    clear()

def test_invalid_email_domain(user_1):
    """Test for no @ character and missing string in the domain.
    """
    with pytest.raises(InputError):
        user.user_profile_setemail(user_1['token'], 'test123.com')
    clear()

def test_invalid_email_domain_period(user_1):
    """Test for no full stop in the domain.
    """
    with pytest.raises(InputError):
        user.user_profile_setemail(user_1['token'], 'test123@gmailcom')
    clear()

def test_invalid_email_personal_info(user_1):
    """Test for whether an email beginning with a capital letter is a valid email.
    """
    with pytest.raises(InputError):
        user.user_profile_setemail(user_1['token'], 'Helloworld@outlook.com')
    clear()

def test_invalid_email_personal_info_special(user_1):
    """Test for invalid characters (including special characters other than '\', '.' or '_').
    """
    with pytest.raises(InputError):
        user.user_profile_setemail(user_1['token'], 'john_smi&th@gmail.com')
    clear()

def test_invalid_email_personal_info_special_2(user_1):
    """Test for invalid characters (including special characters other than '\', '.' or '_').
    """
    with pytest.raises(InputError):
        user.user_profile_setemail(user_1['token'], 'john_smi#^th@gmail.com')
    clear()

def test_invalid_position(user_1):
    """Test for characters '\', '.' or '_' at the end or start of the personal info part.
    """
    with pytest.raises(InputError):
        user.user_profile_setemail(user_1['token'], '.john_smith@gmail.com')
    clear()

#?--------------------------- Output Testing ---------------------------------?#

def test_valid_email(user_1):
    """Test for basic functionality for updating user email.
    """
    user.user_profile_setemail(user_1['token'], 'helloworld@gmail.com')

    user_details = user.user_profile(user_1['token'], user_1['u_id'])

    assert 'helloworld@gmail.com' in user_details['user']['email']
    clear()

def test_email_varying_domain(user_1):
    """Test for a domain other than @gmail.com
    """
    user.user_profile_setemail(user_1['token'], 'hello.world@ourearth.org')

    user_details = user.user_profile(user_1['token'], user_1['u_id'])

    assert 'hello.world@ourearth.org' in user_details['user']['email']
    clear()

def test_update_email(user_1):
    """Basic test for updating email twice and checking if the current email is the
    last set.
    """
    user.user_profile_setemail(user_1['token'], 'helloworld@gmail.com')
    user.user_profile_setemail(user_1['token'], 'changedemail@gmail.com')

    user_details = user.user_profile(user_1['token'], user_1['u_id'])

    assert 'changedemail@gmail.com' in user_details['user']['email']
    clear()

def test_multiple_update_email(user_1):
    """Test for multiple attempts at updating a user email.
    """
    user.user_profile_setemail(user_1['token'], 'helloworld@gmail.com')
    user.user_profile_setemail(user_1['token'], 'changedemail@gmail.com')
    user.user_profile_setemail(user_1['token'], 'buzzlightyear@gmail.com')
    user.user_profile_setemail(user_1['token'], 'bowser@gmail.com')

    user_details = user.user_profile(user_1['token'], user_1['u_id'])

    assert 'bowser@gmail.com' in user_details['user']['email']
    clear()

def test_email_min_requirements(user_1):
    """Test for an email with very minimal requirements (2 letters in the personal
    part, a '@' symbol, at least 1 letter before and after the period in the domain).
    """
    user.user_profile_setemail(user_1['token'], 'hw@g.com')

    user_details = user.user_profile(user_1['token'], user_1['u_id'])

    assert 'hw@g.com' in user_details['user']['email']
    clear()

#------------------------------------------------------------------------------#
#                             user_profile_sethandle                           #
#------------------------------------------------------------------------------#

def test_update_handle(user_1):
    """ Testing the basic functionality of updating a handle
    """
    # getting the current handle string
    prev_handle = ''
    user_list = users_all(user_1['token'])
    for account in user_list['users']:
        if account['u_id'] == user_1['u_id']:
            prev_handle = account['handle_str']
    user.user_profile_sethandle(user_1['token'], 'newHandle')
    # getting the updated handle string
    new_handle = ''
    user_list = users_all(user_1['token'])
    for account in user_list['users']:
        if account['u_id'] == user_1['u_id']:
            new_handle = account['handle_str']

    assert new_handle is not prev_handle
    clear()

def test_handle_prefix(user_1, user_2, user_3):
    """ Testing basic handle name changes.
    """
    user.user_profile_sethandle(user_1['token'], 'newHandle')
    user.user_profile_sethandle(user_2['token'], 'newHandle1')
    user.user_profile_sethandle(user_3['token'], 'newHandle2')
    clear()

def test_handle_consecutive(user_1):
    """ Testing the process of changing handle string consecutively
    """
    user.user_profile_sethandle(user_1['token'], 'newHandle')
    user_list = users_all(user_1['token'])
    for account in user_list['users']:
        if account['u_id'] == user_1['u_id']:
            assert account['handle_str'] == 'newHandle'
    user.user_profile_sethandle(user_1['token'], 'newHandle1')
    user_list = users_all(user_1['token'])
    for account in user_list['users']:
        if account['u_id'] == user_1['u_id']:
            assert account['handle_str'] == 'newHandle1'
    user.user_profile_sethandle(user_1['token'], 'newHandle2')
    user_list = users_all(user_1['token'])
    for account in user_list['users']:
        if account['u_id'] == user_1['u_id']:
            assert account['handle_str'] == 'newHandle2'
    clear()

def test_handle_exists(user_1, user_2):
    """ Testing changing to a user handle that already exists.
    """
    user.user_profile_sethandle(user_1['token'], 'sameHandle')
    with pytest.raises(InputError):
        user.user_profile_sethandle(user_2['token'], 'sameHandle')
    clear()

def test_handle_max(user_1):
    """ Testing the maximum characters a handle can achieve
    """
    user.user_profile_sethandle(user_1['token'], 'c' * 20)
    user.user_profile_sethandle(user_1['token'], 'c' * 15)
    with pytest.raises(InputError):
        user.user_profile_sethandle(user_1['token'], 'c' * 21)
    clear()

def test_handle_min(user_1):
    """ Testing the minimum characters a handle can achieve
    """
    user.user_profile_sethandle(user_1['token'], 'c' * 3)
    user.user_profile_sethandle(user_1['token'], 'c' * 10)
    with pytest.raises(InputError):
        user.user_profile_sethandle(user_1['token'], 'c' * 2)
    with pytest.raises(InputError):
        user.user_profile_sethandle(user_1['token'], '')
    clear()

def test_update_handle_invalid_token(user_1):
    """ Testing that an invalid token will not allow you to change the handle
    """
    auth.auth_logout(user_1['token'])
    with pytest.raises(InputError):
        user.user_profile_sethandle(user_1['token'], 'blahblah')
    clear()


#------------------------------------------------------------------------------#
#                          user_profile_uploadphoto                            #
#------------------------------------------------------------------------------#

#?------------------------ Input/Access Error Testing ------------------------?#

#?--------------------------- Output Testing ---------------------------------?#
