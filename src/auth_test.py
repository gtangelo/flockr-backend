"""
channels feature test implementation to test functions in channels.py

Feature implementation was written by Christian Ilagan.

2020 T3 COMP1531 Major Project
"""

import pytest
import auth
import channel
import channels
from error import InputError, AccessError
from other import clear
from data import data
import hashlib
import jwt
from action import SECRET
#------------------------------------------------------------------------------#
#                                 auth_register                                #
#------------------------------------------------------------------------------#

def test_register_logout():
    """
    user should be able to logout when registered
    """
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    logout = auth.auth_logout(result['token'])
    assert logout['is_success']
    clear()

def test_register_invalid_email():
    """
    should not be able to register with an invalid email, or an already existing email
    """
    clear()
    with pytest.raises(InputError):
        auth.auth_register('testEmail.com', 'abcdefg', 'Christian', 'Ilagan')
    clear()

def test_register_user_exists():
    """
    checks if the user is already registered
    """
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    with pytest.raises(InputError):
        auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    clear()

def test_register_company_email():
    '''
    checks if company emails can be inputted.
    '''
    clear()
    auth.auth_register('testEmail@thiscomp.com.co', 'abcdefg', 'Christian', 'Ilagan')
    clear()

def test_register_password_length():
    '''
    checks invalid passwords
    '''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('testEmail1@gmail.com', 'abcde', 'Christian', 'Ilagan')
    clear()

def test_register_invalid_names():
    '''
    checks the range of names (either first/last are greater or less than the inclusive range 1-50)
    '''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('testEmail@gmail.com', 'abcdef', 'c'*51, 'Ilagan')
    with pytest.raises(InputError):
        auth.auth_register('testEmail1@gmail.com', 'abcdef', 'Christian', 'c'*51)
    with pytest.raises(InputError):
        auth.auth_register('testEmail2@gmail.com', 'abcdef', '', 'c')
    with pytest.raises(InputError):
        auth.auth_register('testEmail3@gmail.com', 'abcdef', 'Christian', '')
    clear()

def test_register_greaterthanmax_password():
    '''
    limitations on password
    '''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('testEmail@gmail.com', 'long'*200, 'Christian', 'Ilagan')
    clear()

def test_register_email_max():
    '''
    limitations on email length
    '''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('c'* 321 + '@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    clear()

def test_register_invalid_chars_name():
    '''
    names should not include numbers and special characters other than '-'
    '''
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdef', 'Chris-tian', 'normal')
    with pytest.raises(InputError):
        auth.auth_register('testEmail1@gmail.com', 'abcdef', 'Chr@st!a1', 'normal')
    with pytest.raises(InputError):
        auth.auth_register('testEmail2@gmail.com', 'abcdef', 'Christian', 'n0rmal')
    clear()


def test_register_invalid_chars_email():
    '''
    test on non alpha-numeric email should only accept special chars (-.!#$%&'*+-/=?^_`{|}~)
    but should not be consecutive
    '''
    clear()
    auth.auth_register('test-Email@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    auth.auth_register('test.Email@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    with pytest.raises(InputError):
        auth.auth_register('t--stEmail@gmail.com', 'abcdef', 'Christian', 'Ilagan')
        auth.auth_register('#%&*#&@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    clear()

def test_minimum_email():
    '''
    the email should contain a domain (.com) and a local part
    '''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('@b', 'abcdef', 'Christian', 'Ilagan')

    with pytest.raises(InputError):
        auth.auth_register('a@b', 'abcdef', 'Christian', 'Ilagan')

    clear()

def test_case_sensitive_email():
    '''
    emails are not case sensitive, so capitalisation in inputs should not matter
    '''
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    with pytest.raises(InputError):
        auth.auth_register('TeStEMaiL@gmAiL.cOm', 'abcdef', 'Christian', 'Ilagan')
    clear()

def test_flock_owner():
    '''
    making sure the first user registered is a flockr owner
    '''
    clear()
    result1 = auth.auth_register('testEmail@gmail.com', 'abcdef', 'Chris', 'Ilag')
    result2 = auth.auth_register('testEmail2@gmail.com', 'abcdef', 'Bob', 'Smith')
    channel_data = channels.channels_create(result2['token'], 'blah', False)
    # Testing if flockr owner can join private channel
    channel.channel_join(result1['token'], channel_data['channel_id'])
    channel2_data = channels.channels_create(result1['token'], 'blah2', False)
    # user 2 should not have flockr ownership
    with pytest.raises(AccessError):
        channel.channel_join(result2['token'], channel2_data['channel_id'])
    clear()


def test_valid_passwords():
    '''
    passwords can contain all visible characters on the keyboard, except space
    '''
    clear()
    result = auth.auth_register('wierdPassword@gmail.com', '!@#$%^&*()_+-=][<>w;:"', 'who', 'where')
    auth.auth_logout(result['token'])
    auth.auth_login('wierdPassword@gmail.com', '!@#$%^&*()_+-=][<>w;:"')
    with pytest.raises(InputError):
        auth.auth_register('passwordnospace@gmail.com', 'h el$l o', 'who', 'where')
    clear()

def test_long_handle_str():
    '''
    Test long name for handle str
    '''
    clear()
    auth.auth_register('wierdPassword@gmail.com', 'password', 'John', 'abcdefghijklmnopqrstuvwxyz')
    clear()
#------------------------------------------------------------------------------#
#                                 auth_login                                   #
#------------------------------------------------------------------------------#

def test_login_incorrect_password():
    '''
    testing using the incorrect password
    '''
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout(result['token'])
    with pytest.raises(InputError):
        auth.auth_login('testEmail@gmail.com', 'abcdef')
    clear()

def test_login_invalid_email():
    '''
    tests if error handling in login is still valid for emails.
    '''
    clear()
    with pytest.raises(InputError):
        auth.auth_login('testemail.com', 'abcdef')
    clear()

def test_login_invalid_password():
    '''
    checks if the password inputted is correct, and that the user exists in the active users data
    '''
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout(result['token'])
    with pytest.raises(InputError):
        auth.auth_login('testEmail@gmail.com', 'abcde')
    clear()

def test_login_invalid_password_chars():
    '''
    Checks if the password inputted contains valid characters
    '''
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout(result['token'])
    with pytest.raises(InputError):
        auth.auth_login('testEmail@gmail.com', 'h $ e L ( 0')
    clear()

def test_login_invalid_user():
    '''
    should not be able to login because email does not belong to a user
    '''
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    with pytest.raises(InputError):
        auth.auth_login('thisWasNeverRegistered@gmail.com', 'abcdefg')
    clear()

def test_already_loggedin():
    '''
    should not be able to login when they are already logged in.
    '''
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    with pytest.raises(InputError):
        auth.auth_login('testEmail@gmail.com', 'abcdefg')
    clear()


#------------------------------------------------------------------------------#
#                                 auth_logout                                  #
#------------------------------------------------------------------------------#

def test_logout_basic():
    '''
    testing the basics of loging out and logging back in.
    '''
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout(result['token'])
    result2 = auth.auth_login('testEmail@gmail.com', 'abcdefg')
    auth.auth_logout(result2['token'])
    clear()
    result3 = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout(result3['token'])
    clear()

def test_logout_not_registered():
    '''
    make sure the token is required to log out.
    '''
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    false_token = 'invalid_tok'
    assert false_token != result['token']
    logout = auth.auth_logout(false_token)
    assert not logout['is_success']
    clear()

def test_logout_without_valid_token():
    '''
    make sure token is required to log out.
    '''
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout(result['token'])
    auth.auth_register('ThisShouldNotLogOut@gmail.com', 'abcdefg', 'Bob', 'Build')
    logout = auth.auth_logout(result['token'])
    assert not logout['is_success']
    with pytest.raises(AccessError):
        channels.channels_create(result['token'], 'name', True)
    clear()

def test_logout_before_registering():
    '''
    testing tokens are needed to logout.
    '''
    clear()
    result = auth.auth_logout('notValidtok@gmail.com')
    assert not result['is_success']
    clear()

def test_logout_failure():
    '''
    Testing failures when logging out
    '''
    clear()
    result = auth.auth_register('test1@gmail.com', 'abcdefg', 'Chris', 'Hie')
    logout = auth.auth_logout(result['token'])
    logout2 = auth.auth_logout(result['token'])
    assert logout['is_success']
    assert not logout2['is_success']
    clear()
#------------------------------------------------------------------------------#
#                                 misc_tests                                   #
#------------------------------------------------------------------------------#

def test_u_id():
    '''
    makes sure that all u_id's are unique
    '''
    clear()
    user1 = auth.auth_register('test1@gmail.com', 'abcdefg', 'Rich', 'Do')
    user2 = auth.auth_register('test2@gmail.com', 'abcdefg', 'Gab', 'Prath')
    user3 = auth.auth_register('test3@gmail.com', 'abcdefg', 'Chris', 'Rich')
    assert user1['u_id'] != user2['u_id']
    assert user3['u_id'] != user2['u_id']
    assert user3['u_id'] != user1['u_id']
    clear()

def test_token():
    '''
    makes sure that all tokens are unique
    '''
    clear()
    user1 = auth.auth_register('test1@gmail.com', 'abcdefg', 'Rich', 'Do')
    user2 = auth.auth_register('test2@gmail.com', 'abcdefg', 'Gab', 'Prath')
    user3 = auth.auth_register('test3@gmail.com', 'abcdefg', 'Chris', 'Rich')
    assert user1['token'] != user2['token']
    assert user3['token'] != user2['token']
    assert user3['token'] != user1['token']
    clear()

def test_password_hashing():
    '''
    Makes sure that password is hashed, or the actual password is not hashed
    '''
    clear()
    password = 'abcdefg'
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user1 = auth.auth_register('test1@gmail.com', password, 'Rich', 'Do')
    for user in data['users']:
        if user['u_id'] == user1['u_id']:
            assert hashed_password == user['password']
    clear()

def test_token_hashing():
    '''
    Makes sure that tokens are using jwt appropiately
    '''
    email = 'test1@gmail.com'
    user1 = auth.auth_register(email, 'abcdefg', 'Rich', 'Do') 
    encoded_jwt = jwt.encode({'email': email}, SECRET, algorithm='HS256')
    for user in data['active_users']:
        if user['u_id'] == user1['u_id']:
            assert user['token'] == str(encoded_jwt)