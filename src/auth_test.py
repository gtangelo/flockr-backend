import pytest
import auth, channels
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
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    logout = auth.auth_logout(result['token'])
    assert logout['is_success'] == True
    clear()

# should not be able to register with an invalid email, or an already existing email
def test_register_invalid_email():
    clear()
    with pytest.raises(InputError) as e:
        auth.auth_register('testEmail.com', 'abcdefg', 'Christian', 'Ilagan')
    clear()

# checks if the user is already registered
def test_register_user_exists():
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    with pytest.raises(InputError) as e:
        auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    clear()

# checks if company emails can be inputted.
def test_register_company_email():
    clear()
    auth.auth_register('testEmail@thiscomp.com.co', 'abcdefg', 'Christian', 'Ilagan')
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
        auth.auth_register('testEmail1@gmail.com', 'abcdef', 'Chr@st!a1', 'normal')
        auth.auth_register('testEmail2@gmail.com', 'abcdef', 'Christian', 'n0rmal')
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

# the email should be atleast 3 characters long
def test_minimum_email():
    clear()
    with pytest.raises(InputError) as e:
        auth.auth_register('@b', 'abcdef', 'Christian', 'Ilagan')
        auth.auth_register('a@b', 'abcdef', 'Christian', 'Ilagan')
    clear()

# emails are not case sensitive, so capitalisation in inputs should not matter
def test_case_sensitive_email():
    clear()
    auth.auth_register('testEmail@gmail.com', 'abcdef', 'Christian', 'Ilagan')
    with pytest.raises(InputError) as e:
        auth.auth_register('TeStEMaiL@gmAiL.cOm', 'abcdef', 'Christian', 'Ilagan')
    clear()

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

# tests if error handling in login is still valid for emails.
def test_login_invalid_email():
    clear()
    with pytest.raises(InputError) as e:
        auth.auth_login('testemail.com', 'abcdef')
    clear()

# checks if the password inputted is correct, and that the user exists in the active users data
def test_login_invalid_password():
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout(result['token'])
    with pytest.raises(InputError) as e:
        auth.auth_login('testEmail@gmail.com', 'abcde')
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

# passwords can contain all visible characters on the keyboard, except space
def test_valid_passwords():
    clear()
    auth.auth_register('wierdPassword@gmail.com', '!@#$%^&*()_+-=][<>w;:"', 'who', 'where')
    with pytest.raises(InputError) as e:
        auth.auth_register('passwordnospace@gmail.com', 'h el$l o', 'who', 'where')
    clear()

# passwords can contain all visible characters on the keyboard, except space
def test_invalid_password():
    clear()
    with pytest.raises(InputError) as e:
        auth.auth_register('wierdPassword@gmail.com', 'h e l $ l o', 'who', 'where' )
    clear()
#------------------------------------------------------------------------------------------#
#                                      logout tests                                        #
#------------------------------------------------------------------------------------------#

# testing the basics of loging out and logging back in.
def test_logout_basic():
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout(result['token'])
    result2 = auth.auth_login('testEmail@gmail.com', 'abcdefg')
    auth.auth_logout(result2['token'])
    clear()
    result3 = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout(result3['token'])
    clear()

# make sure the token is required to log out.
def test_logout_not_registered():
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    false_token = 'invalid_tok'
    assert false_token != result['token']
    with pytest.raises(AccessError) as e:
        auth.auth_logout(false_token)
    clear()

# make sure token is required to log out.
def test_logout_without_valid_token():
    clear()
    result = auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_logout(result['token'])
    result2 = auth.auth_register('ThisShouldNotLogOut@gmail.com', 'abcdefg', 'Bob', 'Build')
    with pytest.raises(AccessError) as e:
        auth.auth_logout(result['token'])
        channels.channels_create(result['token'], 'name', True)
    clear()

def test_logout_before_registering():
    clear()
    with pytest.raises(AccessError) as e:
        auth.auth_logout('notValidtok@gmail.com')
    clear()
    
#------------------------------------------------------------------------------------------#
#                                      misc tests                                          #
#------------------------------------------------------------------------------------------#

# makes sure that all u_id's are unique
def test_u_id():
    clear()
    user1 = auth.auth_register('test1@gmail.com', 'abcdefg', 'Rich', 'Do')
    user2 = auth.auth_register('test2@gmail.com', 'abcdefg', 'Gab', 'Prath')
    user3 = auth.auth_register('test3@gmail.com', 'abcdefg', 'Chris', 'Rich')
    assert user1['u_id'] != user2['u_id']
    assert user3['u_id'] != user2['u_id']
    assert user3['u_id'] != user1['u_id']
    clear()

# makes sure that all tokens are unique
def test_token():
    clear()
    user1 = auth.auth_register('test1@gmail.com', 'abcdefg', 'Rich', 'Do')
    user2 = auth.auth_register('test2@gmail.com', 'abcdefg', 'Gab', 'Prath')
    user3 = auth.auth_register('test3@gmail.com', 'abcdefg', 'Chris', 'Rich')
    assert user1['token'] != user2['token']
    assert user3['token'] != user2['token']
    assert user3['token'] != user1['token']
    clear()

