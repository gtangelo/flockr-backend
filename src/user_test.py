# """
# user feature test implementation to test functions in message.py

# Feature implementation was written by Christian Ilagan and Richard Quisumbing.

# 2020 T3 COMP1531 Major Project
# """

import pytest
import user
import auth
from error import AccessError, InputError
from other import clear, users_all

# #------------------------------------------------------------------------------#
# #                                 user_profile                                 #
# #------------------------------------------------------------------------------#

# #------------------------------------------------------------------------------#
# #                              user_profile_setname                            #
# #------------------------------------------------------------------------------#
def test_update_name():
    ''' Testing the basic functionality of updating a name
    '''
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user.user_profile_setname(result['token'], 'Bobby', 'Smith')
    user_list = users_all(result['token'])
    for account in user_list:
        if account['u_id'] == result['u_id']:
            assert account['name_first'] == 'Bobby'
            assert account['name_last'] == 'Smith'
    clear()

def test_update_name_first():
    ''' Testing the basic functionality of updating only the first name
    '''
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user.user_profile_setname(result['token'], 'Bobby', '')
    user_list = users_all(result['token'])
    for account in user_list:
        if account['u_id'] == result['u_id']:
            assert account['name_first'] == 'Bobby'
            assert account['name_last'] == 'Ilagan'
    clear()

def test_update_name_last():
    ''' Testing the basic functionality of updating only the last name
    '''
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user.user_profile_setname(result['token'], '', 'Smith')
    user_list = users_all(result['token'])
    for account in user_list:
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
    for account in user_list:
        if account['u_id'] == result['u_id']:
            assert account['name_first'] == 'Snake'
            assert account['name_last'] == 'City'
    user.user_profile_setname(result['token'], 'Goku', 'Vegeta')
    for account in user_list:
        if account['u_id'] == result['u_id']:
            assert account['name_first'] == 'Goku'
            assert account['name_last'] == 'Vegeta'
    user.user_profile_setname(result['token'], 'Will', 'Smith')
    for account in user_list:
        if account['u_id'] == result['u_id']:
            assert account['name_first'] == 'Will'
            assert account['name_last'] == 'Smith'
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
        user.user_profile_setname(result['token'], 'Chris', 'S' * 51)
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
    user.user_profile_setname(result['token'], '', 'Smith')
    user.user_profile_setname(result['token'], 'Bob', '')
    user.user_profile_setname(result['token'], '', '')
    clear()

def test_update_invalid_token():
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
    for account in user_list:
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
# #------------------------------------------------------------------------------#
# #                             user_profile_setemail                            #
# #------------------------------------------------------------------------------#

# #------------------------------------------------------------------------------#
# #                             user_profile_sethandle                           #
# #------------------------------------------------------------------------------#

def test_update_handle():
    clear()
    user_one = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    # getting the current handle string
    prev_handle = ''
    user_list = users_all(user_one['token'])
    for account in user_list:
        if account['u_id'] == user_one['u_id']:
            prev_handle = account['handle_str']
    user.user_profile_sethandle(user_one['token'], 'newHandle')
    # getting the updated handle string
    new_handle = ''
    for account in user_list:
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
    for account in user_list:
        if account['u_id'] == user_one['u_id']:
            assert account['handle_str'] == 'newHandle'
    user.user_profile_sethandle(user_one['token'], 'newHandle1')
    for account in user_list:
        if account['u_id'] == user_one['u_id']:
            assert account['handle_str'] == 'newHandle1'
    user.user_profile_sethandle(user_one['token'], 'newHandle2')
    for account in user_list:
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
    with pytest.raises(InputError):
        user.user_profile_sethandle(user_one['token'], 'c' * 21)
    clear()

def test_handle_min():
    ''' Testing the minimum characters a handle can achieve
    '''
    clear()
    user_one = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user.user_profile_sethandle(user_one['token'], 'c' * 3)
    with pytest.raises(InputError):
        user.user_profile_sethandle(user_one['token'], 'c' * 2)
    clear()