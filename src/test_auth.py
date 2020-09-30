import auth
import pytest
from error import InputError, AccessError
'''
Tests for auth.py
'''
#------------------------------------------------------------------------------------------#
#                                      register tests                                      #
#------------------------------------------------------------------------------------------#
# user should be able to login when registered
def test_register_login():
    user = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_login('testEmail@gmail.com', 'abcdefg')
    clear()

# should not be able to register with an invalid email, or an already existing email
def test_register_invalid_email():
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    with pytest.raises(InputError) as e:
        auth.auth_register('testEmail.com', 'abcdefg', 'Christian', 'Ilagan')
        auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    clear()
        
# checks invalid passwords
def test_register_password_length():
    with pytest.raises(InputError) as e:
        auth.auth_register('testEmail@gmail.com', 'abcde', 'Christian', 'Ilagan')
        auth.auth_register('testEmail@gmail.com', '123Ab', 'Christian', 'Ilagan')
    clear()

# checks the range of names (either first or last are greater or less than the inclusive range 1-50)
def test_register_invalid_names():
    with pytest.raises(InputError) as e:
        auth.auth_register('testEmail@gmail.com', 'abcdef', 'c'*51, 'Ilagan')
        auth.auth_register('testEmail@gmail.com', 'abcdef', 'Christian', 'c'*51)
        auth.auth_register('testEmail@gmail.com', 'abcdef', '', 'c')
        auth.auth_register('testEmail@gmail.com', 'abcdef', 'Christian', '')
    clear()

# limitations on password
def test_register_greaterthanmax_password():
    with pytest.raises(InputError) as e:
        auth.auth_register('testEmail@gmail.com', 'long'*200, 'Christian' ,'Ilagan')
    clear()

# limitations on email length
def test_register_email_max():
    with pytest.raises(InputError) as e:
        auth.auth_register('c'* 101 + '@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    clear()

# names should not include numbers and special characters other than '-'
def test_register_invalid_chars_name():
    auth.auth_register('testEmail@gmail.com', 'abcdef', 'Chris-tian', 'normal')
    with pytest.raises(InputError) as e:
        auth.auth_register('testEmail@gmail.com', 'abcdef', 'Chr@st!a1', 'normal')
        auth.auth_register('testEmail@gmail.com', 'abcdef', 'Christian', 'n0rmal')
    clear()

# test on non alpha-numeric email should only accept special chars (-.!#$%&'*+-/=?^_`{|}~)
# but should not be consecutive
def test_register_invalid_chars_email():
    auth.auth_register('test-Email@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    auth.auth_register('t-estEmai-l@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    with pytest.raises(InputError) as e:
        auth.auth_register('t--stEmail@gmail.com', 'abcdef', 'Christian', 'Ilagan')
        auth.auth_register('#%&*#&@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    clear()

# the local part of the email should be atleast 3 chars (before the @)
def test_minimum_email():
    auth.auth_register('abc@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    with pytest.raises(InputError) as e:
        auth.auth_register('ab@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    clear()


#------------------------------------------------------------------------------------------#
#                                      login tests                                         #
#------------------------------------------------------------------------------------------#

# using the incorrect password
def test_login_incorrect_password():
    user = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    with pytest.raises(InputError) as e:
        auth.auth_login('testEmail@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    clear()

# should not be able to login because email does not belong to a user
def test_login_invalid_user():
    user = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    with pytest.raises(InputError) as e:
        auth.auth_login('thisWasNeverRegistered@gmail.com', 'abcdefg')
    clear()

# should not be able to login when they are already logged in.
def test_already_loggedin():
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_login('testEmail@gmail.com', 'abcdefg')
    clear()

#------------------------------------------------------------------------------------------#
#                                      logout tests                                        #
#------------------------------------------------------------------------------------------#

def test_logout_basic():
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
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout('thiswasnotRegistered@gmail.com')
    clear()

    


