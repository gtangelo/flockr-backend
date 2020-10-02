import auth
import pytest
from error import InputError, AccessError
from other import clear
'''
Tests for auth.py
'''
#------------------------------------------------------------------------------------------#
#                                      register tests                                      #
#------------------------------------------------------------------------------------------#

# user should be able to logout when registered
def test_register_logout():
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    logout = auth.auth_logout('testEmail@gmail.com')
    assert logout['is_success'] == True
    clear()

# should not be able to register with an invalid email, or an already existing email
def test_register_invalid_email():
    clear()
    with pytest.raises(InputError) as e:
        auth.auth_register('testEmail.com', 'abcdefg', 'Christian', 'Ilagan')
    clear()

def test_register_user_exists():
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    with pytest.raises(InputError) as e:
        auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    clear()
        
# checks invalid passwords
def test_register_password_length():
    clear()
    with pytest.raises(InputError) as e:
        auth.auth_register('testEmail1@gmail.com', 'abcde', 'Christian', 'Ilagan')
        auth.auth_register('testEmail2@gmail.com', '123Ab', 'Christian', 'Ilagan')
    clear()

# checks the range of names (either first or last are greater or less than the inclusive range 1-50)
def test_register_invalid_names():
    clear()
    with pytest.raises(InputError) as e:
        auth.auth_register('testEmail@gmail.com', 'abcdef', 'c'*51, 'Ilagan')
        auth.auth_register('testEmail1@gmail.com', 'abcdef', 'Christian', 'c'*51)
        auth.auth_register('testEmail2@gmail.com', 'abcdef', '', 'c')
        auth.auth_register('testEmail3@gmail.com', 'abcdef', 'Christian', '')
    clear()

# limitations on password
def test_register_greaterthanmax_password():
    clear()
    with pytest.raises(InputError) as e:
        auth.auth_register('testEmail@gmail.com', 'long'*200, 'Christian' ,'Ilagan')
    clear()

# limitations on email length
def test_register_email_max():
    clear()
    with pytest.raises(InputError) as e:
        auth.auth_register('c'* 321 + '@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    clear()

# names should not include numbers and special characters other than '-'
def test_register_invalid_chars_name():
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdef', 'Chris-tian', 'normal')
    with pytest.raises(InputError) as e:
        auth.auth_register('testEmail@gmail.com', 'abcdef', 'Chr@st!a1', 'normal')
        auth.auth_register('testEmail@gmail.com', 'abcdef', 'Christian', 'n0rmal')
    clear()

# test on non alpha-numeric email should only accept special chars (-.!#$%&'*+-/=?^_`{|}~)
# but should not be consecutive
def test_register_invalid_chars_email():
    clear()
    auth.auth_register('test-Email@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    auth.auth_register('t-estEmai-l@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    with pytest.raises(InputError) as e:
        auth.auth_register('t--stEmail@gmail.com', 'abcdef', 'Christian', 'Ilagan')
        auth.auth_register('#%&*#&@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    clear()

# the local part of the email should be atleast 3 chars (before the @)
# def test_minimum_email():
#     clear()
#     auth.auth_register('abc@gmail.com', 'abcdef', 'Christian', 'Ilagan')
#     auth.auth_logout('abc@gmail.com')
#     with pytest.raises(InputError) as e:
#         auth.auth_register('ab@gmail.com', 'abcdef', 'Christian', 'Ilagan')
#     clear()


#------------------------------------------------------------------------------------------#
#                                      login tests                                         #
#------------------------------------------------------------------------------------------#

# using the incorrect password
def test_login_incorrect_password():
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    with pytest.raises(InputError) as e:
        auth.auth_login('testEmail@gmail.com', 'abcdef')
    clear()

# should not be able to login because email does not belong to a user
def test_login_invalid_user():
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    with pytest.raises(InputError) as e:
        auth.auth_login('thisWasNeverRegistered@gmail.com', 'abcdefg')
    clear()

# should not be able to login when they are already logged in.
def test_already_loggedin():
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    with pytest.raises(InputError) as e:
        auth.auth_login('testEmail@gmail.com', 'abcdefg')
    clear()

#------------------------------------------------------------------------------------------#
#                                      logout tests                                        #
#------------------------------------------------------------------------------------------#

def test_logout_basic():
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout('testEmail@gmail.com')
    auth.auth_login('testEmail@gmail.com', 'abcdefg')
    auth.auth_logout('testEmail@gmail.com')
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout('testEmail@gmail.com')
    clear()

# if the individual, cant log out, if has an account, cannot logout

def test_logout_not_registered():
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    with pytest.raises(InputError) as e:
        auth.auth_logout('thiswasnotRegistered@gmail.com')
    clear()

def test_logout_without_valid_token():
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout('testEmail@gmail.com')
    auth.auth_register('ThisShouldNotLogOut@gmail.com', 'abcdefg', 'Bob', 'Build')
    with pytest.raises(InputError) as e:
        auth.auth_logout('testEmail@gmail.com')
    clear()

def test_logout_before_registering():
    clear()
    with pytest.raises(InputError) as e:
        auth.auth_logout('testEmail@gmail.com')
    clear()
    
#------------------------------------------------------------------------------------------#
#                                      misc tests                                          #
#------------------------------------------------------------------------------------------#

def test_u_id():
    clear()
    user1 = auth.auth_register('test1@gmail.com', 'abcdefg', 'Rich', 'Do')
    user2 = auth.auth_register('test2@gmail.com', 'abcdefg', 'Gab', 'Prath')
    assert user1['u_id'] != user2['u_id']
    clear()

def test_token():
    clear()
    user1 = auth.auth_register('test1@gmail.com', 'abcdefg', 'Rich', 'Do')
    user2 = auth.auth_register('test2@gmail.com', 'abcdefg', 'Gab', 'Prath')
    assert user1['token'] != user2['token']
    clear()

