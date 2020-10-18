"""
user feature test implementation to test functions in message.py

Feature implementation was written by Christian Ilagan and Richard Quisumbing.

2020 T3 COMP1531 Major Project
"""

import pytest
import user
import auth
from error import AccessError, InputError
from other import clear, users_all

#------------------------------------------------------------------------------#
#                                 user_profile                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_user_authorised_user():
    """Test for returning profile of a non-registered/invalid user. (Invalid token
    and u_id)
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_logout(user_1['token'])

    with pytest.raises(AccessError):
        user.user_profile(user_1['token'], user_1['u_id'])
    clear()

def test_user_u_id():
    """Test for returning the profile of a non-existant user.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')

    with pytest.raises(InputError):
        user.user_profile(user_1['token'], user_1['u_id'] + 1)
    clear()

#?-------------------------- Output Testing ---------------------------------?#

def test_user_id():
    """Test whether the user profile u_id matches the u_id returned by auth_register.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')

    user_details = user.user_profile(user_1['token'], user_1['u_id'])

    assert user_1['u_id'] == user_details['user']['u_id']
    clear()

def test_valid_user_name():
    """Test whether the first and last name of a user is the same as the names in
    user_profile.
    """
    clear()
    auth.auth_register('test1@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('test2@gmail.com', 'password', 'Jon', 'Snow')
    auth.auth_register('test3@gmail.com', 'password', 'Ant', 'Hill')

    result_list = users_all(user_2['token'])
    result_profile = user.user_profile(user_2['token'], user_2['u_id'])

    for account in result_list['users']:
        if account['u_id'] == result_profile['user']['u_id']:
            assert result_profile['user']['name_first'] == account['name_first']
            assert result_profile['user']['name_last'] == account['name_last']

def test_valid_user_email():
    """Test whether the user's email matches the email in user_profile.
    """
    clear()
    auth.auth_register('test1@gmail.com', 'password', 'John', 'Smith')
    auth.auth_register('test2@gmail.com', 'password', 'Jon', 'Snow')
    user_3 = auth.auth_register('test3@gmail.com', 'password', 'Ant', 'Hill')

    result_list = users_all(user_3['token'])
    result_profile = user.user_profile(user_3['token'], user_3['u_id'])

    for account in result_list['users']:
        if account['u_id'] == result_profile['user']['u_id']:
            assert result_profile['user']['email'] == account['email']

def test_valid_user_handle_str():
    """Test whether the user's handle string matches the handle string in
    user_profile.
    """
    clear()
    auth.auth_register('test1@gmail.com', 'password', 'John', 'Smith')
    user2 = auth.auth_register('test2@gmail.com', 'password', 'Jon', 'Snow')
    auth.auth_register('test3@gmail.com', 'password', 'Ant', 'Hill')

    result_list = users_all(user2['token'])
    result_profile = user.user_profile(user2['token'], user2['u_id'])

    for account in result_list['users']:
        if account['u_id'] == result_profile['user']['u_id']:
            assert result_profile['user']['handle_str'] == account['handle_str']

#------------------------------------------------------------------------------#
#                              user_profile_setname                            #
#------------------------------------------------------------------------------#
def test_update_name():
    ''' Testing the basic functionality of updating a name
    '''
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user.user_profile_setname(result['token'], 'Bobby', 'Smith')
    user_list = users_all(result['token'])
    for account in user_list['users']:
        if account['u_id'] == result['u_id']:
            assert account['name_first'] == 'Bobby'
            assert account['name_last'] == 'Smith'
    clear()

def test_update_name_first():
    ''' Testing the basic functionality of updating only the first name
    '''
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user.user_profile_setname(result['token'], 'Bobby', 'Ilagan')
    user_list = users_all(result['token'])
    for account in user_list['users']:
        if account['u_id'] == result['u_id']:
            assert account['name_first'] == 'Bobby'
            assert account['name_last'] == 'Ilagan'
    clear()

def test_update_name_last():
    ''' Testing the basic functionality of updating only the last name
    '''
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user.user_profile_setname(result['token'], 'Christian', 'Smith')
    user_list = users_all(result['token'])
    for account in user_list['users']:
        if account['u_id'] == result['u_id']:
            assert account['name_first'] == 'Christian'
            assert account['name_last'] == 'Smith'
    clear()

def test_update_consecutively():
    ''' Testing wheter the same token allows users to continously change their name
    '''
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user.user_profile_setname(result['token'], 'Bobby', 'Smith')
    user.user_profile_setname(result['token'], 'Snake', 'City')
    user_list = users_all(result['token'])
    for account in user_list['users']:
        if account['u_id'] == result['u_id']:
            assert account['name_first'] == 'Snake'
            assert account['name_last'] == 'City'
            break
    user.user_profile_setname(result['token'], 'Goku', 'Vegeta')
    user_list = users_all(result['token'])
    for account in user_list['users']:
        if account['u_id'] == result['u_id']:
            assert account['name_first'] == 'Goku'
            assert account['name_last'] == 'Vegeta'
            break
    user.user_profile_setname(result['token'], 'Will', 'Smith')
    user_list = users_all(result['token'])
    for account in user_list['users']:
        if account['u_id'] == result['u_id']:
            assert account['name_first'] == 'Will'
            assert account['name_last'] == 'Smith'
            break
    clear()


def test_update_max_name():
    ''' Testing the maximum limits of what a user can change their name to
    '''
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user.user_profile_setname(result['token'], 'C' * 50, 'Smith')
    user.user_profile_setname(result['token'], 'Chris', 'S' * 50)
    user.user_profile_setname(result['token'], 'C' * 50, 'S' * 50)
    with pytest.raises(InputError):
        user.user_profile_setname(result['token'], 'C' * 51, 'Smith')
    with pytest.raises(InputError):
        user.user_profile_setname(result['token'], 'Chris', 'S' * 51)
    with pytest.raises(InputError):
        user.user_profile_setname(result['token'], 'C' * 51, 'S' * 51)
    clear()

def test_update_min_name():
    ''' Testing the minimum limits of what a user can change their name to.
    '''
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user.user_profile_setname(result['token'], 'C', 'S')
    user.user_profile_setname(result['token'], 'Chris', 'S')
    user.user_profile_setname(result['token'], 'C', 'Smith')
    # empty string does not change the name
    with pytest.raises(InputError):
        user.user_profile_setname(result['token'], '', 'Smith')
    with pytest.raises(InputError):
        user.user_profile_setname(result['token'], 'Bob', '')
    with pytest.raises(InputError):
        user.user_profile_setname(result['token'], '', '')
    clear()

def test_update_invalid_token():
    ''' Testing user cant change name with an invalid token
    '''
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout(result['token'])
    with pytest.raises(InputError):
        user.user_profile_setname(result['token'], 'Bobby', 'Smith')
    clear()

def test_update_multiple_users():
    ''' Testing if users name fields are appropiately changed in largely stored data
    '''
    clear()
    user_one = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user_two = auth.auth_register('freeEmail@gmail.com', 'abcdefg', 'Bobby', 'Smith')
    user_three = auth.auth_register('k9smith@gmail.com', 'abcdefg', 'Jorge', 'Bob')
    user_four = auth.auth_register('baller@gmail.com', 'abcdefg', 'Goku', 'Vegeta')
    user.user_profile_setname(user_three['token'], 'Popcorn', 'Smoothie')
    user.user_profile_setname(user_two['token'], 'Krillin', 'Bulma')
    user_list = users_all(user_one['token'])
    for account in user_list['users']:
        if account['u_id'] == user_two['u_id']:
            assert account['name_first'] == 'Krillin'
            assert account['name_last'] == 'Bulma'
        if account['u_id'] == user_three['u_id']:
            assert account['name_first'] == 'Popcorn'
            assert account['name_last'] == 'Smoothie'
        if account['u_id'] == user_one['u_id']:
            assert account['name_first'] == 'Christian'
            assert account['name_last'] == 'Ilagan'
        if account['u_id'] == user_four['u_id']:
            assert account['name_first'] == 'Goku'
            assert account['name_last'] == 'Vegeta'
    clear()

def test_invalid_chars():
    ''' Testing if non english alphabets are rejected, with the exception of '-'
    '''
    clear()
    user_one = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    with pytest.raises(InputError):
        user.user_profile_setname(user_one['token'], 'A92!0F', 'Smith')
        user.user_profile_setname(user_one['token'], 'Smith', 'A92!0F')
        user.user_profile_setname(user_one['token'], 'A92!0F', 'A92!0F')
    clear()
#------------------------------------------------------------------------------#
#                             user_profile_setemail                            #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_user_valid():
    """Test for whether the user is logged in and authorised to set their email.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_logout(user_1['token'])

    with pytest.raises(AccessError):
        user.user_profile_setemail(user_1['token'], 'test123@gmail.com')
    clear()

def test_email_already_in_use():
    """Test for an email that is already in use by another active user.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jonsnow@gmail.com', 'password', 'Jon', 'Snow')
    user_3 = auth.auth_register('anthill@gmail.com', 'password', 'Ant', 'Hill')
    user.user_profile_setemail(user_1['token'], 'test123@gmail.com')
    user.user_profile_setemail(user_3['token'], 'test987@gmail.com')

    with pytest.raises(InputError):
        user.user_profile_setemail(user_2['token'], 'test123@gmail.com')
    clear()

def test_update_email_same_twice():
    """Setting the email that the user already has raises an error.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user.user_profile_setemail(user_1['token'], 'test123@gmail.com')

    with pytest.raises(InputError):
        user.user_profile_setemail(user_1['token'], 'test123@gmail.com')
    clear()

def test_invalid_email_domain():
    """Test for no @ character and missing string in the domain.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')

    with pytest.raises(InputError):
        user.user_profile_setemail(user_1['token'], 'test123.com')
    clear()

def test_invalid_email_domain_period():
    """Test for no full stop in the domain.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')

    with pytest.raises(InputError):
        user.user_profile_setemail(user_1['token'], 'test123@gmailcom')
    clear()

def test_invalid_email_personal_info():
    """Test for whether an email beginning with a capital letter is a valid email.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')

    with pytest.raises(InputError):
        user.user_profile_setemail(user_1['token'], 'Helloworld@outlook.com')
    clear()

def test_invalid_email_personal_info_special():
    """Test for invalid characters (including special characters other than '\', '.' or '_').
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')

    with pytest.raises(InputError):
        user.user_profile_setemail(user_1['token'], 'john_smi&th@gmail.com')
    clear()

def test_invalid_email_personal_info_special_2():
    """Test for invalid characters (including special characters other than '\', '.' or '_').
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')

    with pytest.raises(InputError):
        user.user_profile_setemail(user_1['token'], 'john_smi#^th@gmail.com')
    clear()

def test_invalid_position():
    """Test for characters '\', '.' or '_' at the end or start of the personal info part.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')

    with pytest.raises(InputError):
        user.user_profile_setemail(user_1['token'], '.john_smith@gmail.com')
    clear()

#?-------------------------- Output Testing ---------------------------------?#

def test_valid_email():
    """Test for basic functionality for updating user email.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user.user_profile_setemail(user_1['token'], 'helloworld@gmail.com')

    user_details = user.user_profile(user_1['token'], user_1['u_id'])

    assert 'helloworld@gmail.com' in user_details['user']['email']
    clear()

def test_email_varying_domain():
    """Test for a domain other than @gmail.com
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user.user_profile_setemail(user_1['token'], 'hello.world@ourearth.org')

    user_details = user.user_profile(user_1['token'], user_1['u_id'])

    assert 'hello.world@ourearth.org' in user_details['user']['email']
    clear()

def test_update_email():
    """Basic test for updating email twice and checking if the current email is the
    last set.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user.user_profile_setemail(user_1['token'], 'helloworld@gmail.com')
    user.user_profile_setemail(user_1['token'], 'changedemail@gmail.com')

    user_details = user.user_profile(user_1['token'], user_1['u_id'])

    assert 'changedemail@gmail.com' in user_details['user']['email']
    clear()

def test_multiple_update_email():
    """Test for multiple attempts at updating a user email.
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user.user_profile_setemail(user_1['token'], 'helloworld@gmail.com')
    user.user_profile_setemail(user_1['token'], 'changedemail@gmail.com')
    user.user_profile_setemail(user_1['token'], 'buzzlightyear@gmail.com')
    user.user_profile_setemail(user_1['token'], 'bowser@gmail.com')

    user_details = user.user_profile(user_1['token'], user_1['u_id'])

    assert 'bowser@gmail.com' in user_details['user']['email']
    clear()

def test_email_min_requirements():
    """Test for an email with very minimal requirements (2 letters in the personal
    part, a '@' symbol, at least 1 letter before and after the period in the domain).
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user.user_profile_setemail(user_1['token'], 'hw@g.com')

    user_details = user.user_profile(user_1['token'], user_1['u_id'])

    assert 'hw@g.com' in user_details['user']['email']
    clear()

#------------------------------------------------------------------------------#
#                             user_profile_sethandle                           #
#------------------------------------------------------------------------------#

def test_update_handle():
    ''' Testing the basic functionality of updating a handle
    '''
    clear()
    user_one = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    # getting the current handle string
    prev_handle = ''
    user_list = users_all(user_one['token'])
    for account in user_list['users']:
        if account['u_id'] == user_one['u_id']:
            prev_handle = account['handle_str']
    user.user_profile_sethandle(user_one['token'], 'newHandle')
    # getting the updated handle string
    new_handle = ''
    user_list = users_all(user_one['token'])
    for account in user_list['users']:
        if account['u_id'] == user_one['u_id']:
            new_handle = account['handle_str']

    assert new_handle is not prev_handle
    clear()

def test_handle_prefix():
    ''' Testing basic handle name changes.
    '''
    clear()
    user_one = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user_two = auth.auth_register('testEmail2@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user_three = auth.auth_register('testEmail3@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user.user_profile_sethandle(user_one['token'], 'newHandle')
    user.user_profile_sethandle(user_two['token'], 'newHandle1')
    user.user_profile_sethandle(user_three['token'], 'newHandle2')
    clear()

# fix method of assertion
def test_handle_consecutive():
    ''' Testing the process of changing handle string consecutively
    '''
    clear()
    user_one = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user.user_profile_sethandle(user_one['token'], 'newHandle')
    user_list = users_all(user_one['token'])
    for account in user_list['users']:
        if account['u_id'] == user_one['u_id']:
            assert account['handle_str'] == 'newHandle'
    user.user_profile_sethandle(user_one['token'], 'newHandle1')
    user_list = users_all(user_one['token'])
    for account in user_list['users']:
        if account['u_id'] == user_one['u_id']:
            assert account['handle_str'] == 'newHandle1'
    user.user_profile_sethandle(user_one['token'], 'newHandle2')
    user_list = users_all(user_one['token'])
    for account in user_list['users']:
        if account['u_id'] == user_one['u_id']:
            assert account['handle_str'] == 'newHandle2'
    clear()

def test_handle_exists():
    ''' Testing changing to a user handle that already exists.
    '''
    clear()
    user_one = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user_two = auth.auth_register('testEmail2@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user.user_profile_sethandle(user_one['token'], 'sameHandle')
    with pytest.raises(InputError):
        user.user_profile_sethandle(user_two['token'], 'sameHandle')
    clear()

def test_handle_max():
    ''' Testing the maximum characters a handle can achieve
    '''
    clear()
    user_one = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user.user_profile_sethandle(user_one['token'], 'c' * 20)
    user.user_profile_sethandle(user_one['token'], 'c' * 15)
    with pytest.raises(InputError):
        user.user_profile_sethandle(user_one['token'], 'c' * 21)
    clear()

def test_handle_min():
    ''' Testing the minimum characters a handle can achieve
    '''
    clear()
    user_one = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user.user_profile_sethandle(user_one['token'], 'c' * 3)
    user.user_profile_sethandle(user_one['token'], 'c' * 10)
    with pytest.raises(InputError):
        user.user_profile_sethandle(user_one['token'], 'c' * 2)
    with pytest.raises(InputError):
        user.user_profile_sethandle(user_one['token'], '')
    clear()

def test_update_handle_invalid_token():
    ''' Testing that an invalid token will not allow you to change the handle
    '''
    clear()
    user_one = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout(user_one['token'])
    with pytest.raises(InputError):
        user.user_profile_sethandle(user_one['token'], 'blahblah')
    clear()
