"""
auth feature test implementation to test functions in auth.py

2020 T3 COMP1531 Major Project
"""
import hashlib
import jwt
import pytest
import pickle
import src.feature.auth as auth
import src.feature.channel as channel
import src.feature.channels as channels
import src.feature.user as user

from src.feature.other import clear
from src.feature.error import InputError, AccessError

from src.globals import SECRET

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

def test_register_password_length():
    """
    checks invalid passwords
    """
    clear()
    with pytest.raises(InputError):
        auth.auth_register('testEmail1@gmail.com', 'abcde', 'Christian', 'Ilagan')
    clear()

def test_register_invalid_names():
    """
    checks the range of names (either first/last are greater or less than the inclusive range 1-50)
    """
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
    """
    limitations on password
    """
    clear()
    with pytest.raises(InputError):
        auth.auth_register('testEmail@gmail.com', 'long'*200, 'Christian', 'Ilagan')
    clear()

def test_register_email_max():
    """
    limitations on email length
    """
    clear()
    with pytest.raises(InputError):
        auth.auth_register('c'* 321 + '@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    clear()

def test_register_invalid_chars_name():
    """
    names should not include numbers and special characters other than '-'
    """
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdef', 'Chris-tian', 'normal')
    with pytest.raises(InputError):
        auth.auth_register('testEmail1@gmail.com', 'abcdef', 'Chr@st!a1', 'normal')
    with pytest.raises(InputError):
        auth.auth_register('testEmail2@gmail.com', 'abcdef', 'Christian', 'n0rmal')
    clear()


def test_register_invalid_chars_email():
    """
    test on non alpha-numeric email should only accept special chars (-.!#$%&'*+-/=?^_`{|}~)
    but should not be consecutive
    """
    clear()
    auth.auth_register('test-Email@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    auth.auth_register('test.Email@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    with pytest.raises(InputError):
        auth.auth_register('t--stEmail@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    with pytest.raises(InputError):
        auth.auth_register('#%&*#&@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    clear()

def test_minimum_email():
    """
    the email should contain a domain (.com) and a local part
    """
    clear()
    with pytest.raises(InputError):
        auth.auth_register('@b', 'abcdef', 'Christian', 'Ilagan')
    with pytest.raises(InputError):
        auth.auth_register('a@b', 'abcdef', 'Christian', 'Ilagan')

    clear()

def test_case_sensitive_email():
    """
    emails are not case sensitive, so capitalisation in inputs should not matter
    """
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    with pytest.raises(InputError):
        auth.auth_register('TeStEMaiL@gmAiL.cOm', 'abcdef', 'Christian', 'Ilagan')
    clear()

def test_flock_owner():
    """
    making sure the first user registered is a flockr owner
    """
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
    """
    passwords can contain all visible characters on the keyboard, except space
    """
    clear()
    result = auth.auth_register('wierdPassword@gmail.com', '!@#$%^&*()_+-=][<>w;:"', 'who', 'where')
    auth.auth_logout(result['token'])
    auth.auth_login('wierdPassword@gmail.com', '!@#$%^&*()_+-=][<>w;:"')
    with pytest.raises(InputError):
        auth.auth_register('passwordnospace@gmail.com', 'h el$l o', 'who', 'where')
    clear()

#------------------------------------------------------------------------------#
#                                 auth_login                                   #
#------------------------------------------------------------------------------#

def test_login_incorrect_password():
    """
    testing using the incorrect password
    """
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout(result['token'])
    with pytest.raises(InputError):
        auth.auth_login('testEmail@gmail.com', 'abcdef')
    clear()

def test_login_invalid_email():
    """
    tests if error handling in login is still valid for emails.
    """
    clear()
    with pytest.raises(InputError):
        auth.auth_login('testemail.com', 'abcdef')
    clear()

def test_login_invalid_password():
    """
    checks if the password inputted is correct, and that the user exists in the active users data
    """
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout(result['token'])
    with pytest.raises(InputError):
        auth.auth_login('testEmail@gmail.com', 'abcde')
    clear()

def test_login_invalid_password_chars():
    """
    Checks if the password inputted contains valid characters
    """
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout(result['token'])
    with pytest.raises(InputError):
        auth.auth_login('testEmail@gmail.com', 'h $ e L ( 0')
    clear()

def test_login_invalid_user():
    """
    should not be able to login because email does not belong to a user
    """
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    with pytest.raises(InputError):
        auth.auth_login('thisWasNeverRegistered@gmail.com', 'abcdefg')
    clear()

#------------------------------------------------------------------------------#
#                                 auth_logout                                  #
#------------------------------------------------------------------------------#

def test_logout_basic():
    """
    testing the basics of loging out and logging back in.
    """
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
    """
    make sure the token is required to log out.
    """
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    false_token = 'invalid_tok'
    assert false_token != result['token']
    logout = auth.auth_logout(false_token)
    assert not logout['is_success']
    clear()

def test_logout_without_valid_token():
    """
    make sure token is required to log out.
    """
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
    """
    testing tokens are needed to logout.
    """
    clear()
    result = auth.auth_logout('notValidtok@gmail.com')
    assert not result['is_success']
    clear()

def test_logout_failure():
    """
    Testing failures when logging out
    """
    clear()
    result = auth.auth_register('test1@gmail.com', 'abcdefg', 'Chris', 'Hie')
    logout = auth.auth_logout(result['token'])
    logout2 = auth.auth_logout(result['token'])
    assert logout['is_success']
    assert not logout2['is_success']
    clear()


#------------------------------------------------------------------------------#
#                          auth_passwordreset_request                          #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_reset_register():
    """
    Testing that when requested, a user is moved to a section of data that shows
    that they are trying to reset the password ie 'reset_users'
    """
    clear()
    email = 'test1@gmail.com'
    result = auth.auth_register(email, 'abcdefg', 'John', 'Smith')
    auth.auth_passwordreset_request(email)
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result['u_id']:
            assert user['email'] == email
    clear()

def test_request_multiple_users():
    """
    Testing multiple users who have requested to reset password
    """
    clear()
    email_1 = 'test1@gmail.com'
    email_2 = 'test2@gmail.com'
    email_3 = 'test3@gmail.com'
    email_4 = 'test4@gmail.com'
    result_1 = auth.auth_register(email_1, 'abcdefg', 'John', 'Smith')
    result_2 = auth.auth_register(email_2, 'abcdefg', 'John', 'Smith')
    result_3 = auth.auth_register(email_3, 'abcdefg', 'John', 'Smith')
    result_4 = auth.auth_register(email_4, 'abcdefg', 'John', 'Smith')
    auth.auth_passwordreset_request(email_1)
    auth.auth_passwordreset_request(email_2)
    auth.auth_passwordreset_request(email_3)
    auth.auth_passwordreset_request(email_4)
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result_1['u_id']:
            assert user['email'] == email_1
        if user['u_id'] == result_2['u_id']:
            assert user['email'] == email_2
        if user['u_id'] == result_3['u_id']:
            assert user['email'] == email_3
        if user['u_id'] == result_4['u_id']:
            assert user['email'] == email_4
    clear()

def test_request_not_registered():
    """
    Testing that a user who is not registered is not added to 'reset_users'
    """
    clear()
    email_1 = 'test1@gmail.com'
    with pytest.raises(InputError):
        auth.auth_passwordreset_request(email_1)
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        assert user['email'] != email_1
    clear()

def test_request_logged_out():
    """
    Testing that a user can request a password reset when logged out
    """
    clear()
    email_1 = 'test1@gmail.com'
    result_1 = auth.auth_register(email_1, 'abcdefg', 'John', 'Smith')
    auth.auth_logout(result_1['token'])
    auth.auth_passwordreset_request(email_1)
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result_1['u_id']:
            assert user['email'] == email_1 
    clear() 

def test_request_logged_in():
    """
    Testing that a user can request a password reset when logged in
    """
    clear()
    email_1 = 'test1@gmail.com'
    result_1 = auth.auth_register(email_1, 'abcdefg', 'John', 'Smith')
    auth.auth_passwordreset_request(email_1)
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result_1['u_id']:
            assert user['email'] == email_1 
    clear()

def test_request_multiple():
    """
    Testing that a user can request multiple password resets.
    """
    clear()
    email_1 = 'test1@gmail.com'
    result_1 = auth.auth_register(email_1, 'abcdefg', 'John', 'Smith')
    auth.auth_passwordreset_request(email_1)
    auth.auth_passwordreset_request(email_1)
    auth.auth_passwordreset_request(email_1)
    auth.auth_passwordreset_request(email_1)
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result_1['u_id']:
            assert user['email'] == email_1 
    # the same user should be able to request multiple times,
    # however it should not add the same user to reset_users
    # multiple times
    assert len(data.get_reset_users()) == 1
    clear() 

def test_secret_unique_user():
    """
    Testing that the secret generated is unique each time requested
    """
    clear()
    email_1 = 'test1@gmail.com'
    result_1 = auth.auth_register(email_1, 'abcdefg', 'John', 'Smith')
    auth.auth_passwordreset_request(email_1)
    secret_1 = ''
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result_1['u_id']:
            secret_1 = user['secret']
    auth.auth_passwordreset_request(email_1)
    secret_2 = ''
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result_1['u_id']:
            secret_2 = user['secret']
    auth.auth_passwordreset_request(email_1)
    secret_3 = ''
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result_1['u_id']:
            secret_3 = user['secret']

    assert secret_1 != secret_2
    assert secret_1 != secret_3
    assert secret_2 != secret_3
    clear()

def test_secret_unique_users():
    """
    Testing that no 2 users have the same secret
    """
    clear()
    email_1 = 'test1@gmail.com'
    email_2 = 'test2@gmail.com'
    email_3 = 'test3@gmail.com'
    result_1 = auth.auth_register(email_1, 'abcdefg', 'John', 'Smith')
    result_2 = auth.auth_register(email_2, 'abcdefg', 'John', 'Smith')
    result_3 = auth.auth_register(email_3, 'abcdefg', 'John', 'Smith')
    auth.auth_passwordreset_request(email_1)
    auth.auth_passwordreset_request(email_2)
    auth.auth_passwordreset_request(email_3)
    secret_1 = ''
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result_1['u_id']:
            secret_1 = user['secret']
    auth.auth_passwordreset_request(email_1)
    secret_2 = ''
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result_2['u_id']:
            secret_2 = user['secret']
    auth.auth_passwordreset_request(email_1)
    secret_3 = ''
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result_3['u_id']:
            secret_3 = user['secret']

    assert secret_1 != secret_2
    assert secret_1 != secret_3
    assert secret_2 != secret_3
    clear()

#?------------------------------ Output Testing ------------------------------?#


#------------------------------------------------------------------------------#
#                           auth_passwordreset_reset                           #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_reset_invalid_password_1():
    """
    Testing that invalid passwords cannot be used to reset
    """
    clear()
    email = 'test1@gmail.com'
    result = auth.auth_register(email, 'abcdefg', 'John', 'Smith')
    auth.auth_passwordreset_request(email)
    reset_code = ''
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result['u_id']:
            reset_code = user['secret']
    with pytest.raises(InputError):
        auth.auth_passwordreset_reset(reset_code, 'H AA : )')
    clear()

def test_reset_invalid_password_2():
    """
    Testing that invalid passwords cannot be used to reset
    """
    clear()
    email = 'test1@gmail.com'
    result = auth.auth_register(email, 'abcdefg', 'John', 'Smith')
    auth.auth_passwordreset_request(email)
    reset_code = ''
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result['u_id']:
            reset_code = user['secret']
    with pytest.raises(InputError):
        auth.auth_passwordreset_reset(reset_code, 'h'*129)
    clear()

def test_reset_invalid_password_3():
    """
    Testing that invalid passwords cannot be used to reset
    """
    clear()
    email = 'test1@gmail.com'
    result = auth.auth_register(email, 'abcdefg', 'John', 'Smith')
    auth.auth_passwordreset_request(email)
    reset_code = ''
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result['u_id']:
            reset_code = user['secret']
    with pytest.raises(InputError):
        auth.auth_passwordreset_reset(reset_code, 'h')
    clear()

def test_reset_invalid_secret():
    """
    Testing that invalid passwords cannot be used to reset
    """
    clear()
    email = 'test1@gmail.com'
    auth.auth_register(email, 'abcdefg', 'John', 'Smith')
    auth.auth_passwordreset_request(email)
    reset_code = 'invalid'
    with pytest.raises(InputError):
        auth.auth_passwordreset_reset(reset_code, 'new_password')
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_reset_password():
    """
    Testing that password is actually updated
    """
    clear()
    email = 'test1@gmail.com'
    result = auth.auth_register(email, 'abcdefg', 'John', 'Smith')
    auth.auth_passwordreset_request(email)
    reset_code = ''
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result['u_id']:
            reset_code = user['secret']

    password = 'new_password'
    auth.auth_passwordreset_reset(reset_code, password)
    # comparing hashed password
    hashed = hashlib.sha256(password.encode()).hexdigest()
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        assert user['u_id'] != result['u_id']
    # making sure new hashed password is stored
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_users():
        if user['u_id'] == result['u_id']:
            assert user['password'] == hashed
    clear()

def test_reset_done():
    """
    Testing that once the password has successfully been reset, user is removed from
    'reset_users' field.
    """
    clear()
    email = 'test1@gmail.com'
    result = auth.auth_register(email, 'abcdefg', 'John', 'Smith')
    auth.auth_passwordreset_request(email)
    reset_code = ''
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result['u_id']:
            reset_code = user['secret']
    auth.auth_passwordreset_reset(reset_code, 'new_password')
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        assert user['u_id'] != result['u_id']
    clear()
    
def test_reset_consecutive():
    """
    Testing that a user can consecutively request and reset their password.
    """
    clear()
    email = 'test1@gmail.com'
    result = auth.auth_register(email, 'abcdefg', 'John', 'Smith')
    auth.auth_passwordreset_request(email)
    reset_code = ''
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result['u_id']:
            reset_code = user['secret']
    password = 'new_password'
    auth.auth_passwordreset_reset(reset_code, password)
    # comparing hashed password
    hashed = hashlib.sha256(password.encode()).hexdigest()
    # making sure new hashed password is stored
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_users():
        if user['u_id'] == result['u_id']:
            assert user['password'] == hashed
    auth.auth_passwordreset_request(email)
    reset_code = ''
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result['u_id']:
            reset_code = user['secret']
    password = 'new_password_1'
    auth.auth_passwordreset_reset(reset_code, password)
    # comparing hashed password
    hashed = hashlib.sha256(password.encode()).hexdigest()
    # making sure new hashed password is stored
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_users():
        if user['u_id'] == result['u_id']:
            assert user['password'] == hashed
    auth.auth_passwordreset_request(email)
    reset_code = ''
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result['u_id']:
            reset_code = user['secret']
    password = 'new_password_2'
    auth.auth_passwordreset_reset(reset_code, password)
    # comparing hashed password
    hashed = hashlib.sha256(password.encode()).hexdigest()
    # making sure new hashed password is stored
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_users():
        if user['u_id'] == result['u_id']:
            assert user['password'] == hashed
    clear()

def test_reset_logout():
    """
    Testing that once password is successfully reset, the user is logged out.
    """
    clear()
    email = 'test1@gmail.com'
    result = auth.auth_register(email, 'abcdefg', 'John', 'Smith')
    auth.auth_passwordreset_request(email)
    reset_code = ''
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        if user['u_id'] == result['u_id']:
            reset_code = user['secret']
    password = 'new_password'
    auth.auth_passwordreset_reset(reset_code, password)
    # comparing hashed password
    hashed = hashlib.sha256(password.encode()).hexdigest()
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_reset_users():
        assert user['u_id'] != result['u_id']
    # making sure new hashed password is stored
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_users():
        if user['u_id'] == result['u_id']:
            assert user['password'] == hashed
    clear()

#------------------------------------------------------------------------------#
#                                 misc_tests                                   #
#------------------------------------------------------------------------------#

def test_u_id():
    """
    makes sure that all u_id's are unique
    """
    clear()
    user1 = auth.auth_register('test1@gmail.com', 'abcdefg', 'Rich', 'Do')
    user2 = auth.auth_register('test2@gmail.com', 'abcdefg', 'Gab', 'Prath')
    user3 = auth.auth_register('test3@gmail.com', 'abcdefg', 'Chris', 'Rich')
    assert user1['u_id'] != user2['u_id']
    assert user3['u_id'] != user2['u_id']
    assert user3['u_id'] != user1['u_id']
    clear()

def test_token():
    """
    makes sure that all tokens are unique
    """
    clear()
    user1 = auth.auth_register('test1@gmail.com', 'abcdefg', 'Rich', 'Do')
    user2 = auth.auth_register('test2@gmail.com', 'abcdefg', 'Gab', 'Prath')
    user3 = auth.auth_register('test3@gmail.com', 'abcdefg', 'Chris', 'Rich')
    assert user1['token'] != user2['token']
    assert user3['token'] != user2['token']
    assert user3['token'] != user1['token']
    clear()

def test_password_hashing():
    """
    Makes sure that password is hashed, or the actual password is not hashed
    """
    clear()
    password = 'abcdefg'
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user1 = auth.auth_register('test1@gmail.com', password, 'Rich', 'Do')
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_users():
        if user['u_id'] == user1['u_id']:
            assert hashed_password == user['password']
            assert hashed_password != password
    clear()

def test_token_hashing():
    """
    Makes sure that tokens are using jwt appropiately
    """
    clear()
    email = 'test1@gmail.com'
    user1 = auth.auth_register(email, 'abcdefg', 'Rich', 'Do')
    encoded_jwt = jwt.encode({'email': email}, SECRET, algorithm='HS256')
    data = pickle.load(open("data.p", "rb"))
    for user in data.get_active_users():
        if user['u_id'] == user1['u_id']:
            assert user['token'] == str(encoded_jwt)

def test_handle():
    """
    Testing the method of generating handles
    """
    user1 = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    user2 = auth.auth_register('testEmail1@gmail.com', 'abcdefg', 'Christian', 'Ilagan'*3)
    details_1 = user.user_profile(user1['token'], user1['u_id'])
    details_2 = user.user_profile(user2['token'], user2['u_id'])

    assert details_1['user']['handle_str'] == 'cilagan0'
    assert details_2['user']['handle_str'] == 'cilaganilaganilaga' + '0'

