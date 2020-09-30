import auth
import pytest
'''
Tests for auth.py
'''
def test_register_twice():
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    assert auth.auth_register('testEmail@gmail.com', 'this is', 'already', 'registered') == False

def test_login():
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_login('testEmail@gmail.com', 'abcdefg')

def test_login_invalid():
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    assert auth.auth_login('ThisShouldNotWork@gmail.com', 'abcdefg') == False

def test_logout():
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    auth.auth_login('testEmail@gmail.com', 'abcdefg')
    assert auth.auth_logout('testEmail@gmail.com') == True

def test_uid():
    auth.auth_register('testEmail@gmail.com', 'abcdefg', 'Christian', 'Ilagan')
    for user in auth.data['users']:
        if user['email'] == 'testEmail@gmail.com':
            assert user['u_id'] == 1
    auth.auth_register('blah@gmail.com', 'abcde', 'George', 'Curious')
    auth.auth_register('blah2@gmail.com', 'abcde', 'George', 'Curious')
    auth.auth_register('blah3@gmail.com', 'abcde', 'George', 'Curious')
    for user in auth.data['users']:
        if user['email'] == 'blah2@gmail.com':
            assert user['u_id'] == 3


    


