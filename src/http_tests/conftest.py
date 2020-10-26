"""
Pytest fixtures to use in testing files.

2020 T3 COMP1531 Major Project
"""
import requests
import pytest

from src.http_tests.helpers import register_default_user

# User fixtures
@pytest.fixture
def user_1(url):
    requests.delete(f'{url}clear')
    return register_default_user(url, 'John', 'Smith')

@pytest.fixture
def logout_user_1(url, user_1):
    return requests.post(f'{url}auth/logout', json={
        'token': user_1['token']
    }).json()

@pytest.fixture
def user_2(url):
    return register_default_user(url, 'Jane', 'Smith')
    
@pytest.fixture
def user_3(url):
    return register_default_user(url, 'Jace', 'Smith')
    
@pytest.fixture
def user_4(url):
    return register_default_user(url, 'Janice', 'Smith')

# Public channels fixtures
@pytest.fixture
def public_channel_1(url, user_1):
    return requests.post(f'{url}/channels/create', json={
        'token': user_1['token'],
        'name': 'Group 1',
        'is_public': True,
    }).json()

@pytest.fixture
def public_channel_2(url, user_2):
    return requests.post(f'{url}/channels/create', json={
        'token': user_2['token'],
        'name': 'Group 2',
        'is_public': True,
    }).json()

@pytest.fixture
def public_channel_3(url, user_3):
    return requests.post(f'{url}/channels/create', json={
        'token': user_3['token'],
        'name': 'Group 1',
        'is_public': True,
    }).json()

@pytest.fixture
def public_channel_4(url, user_4):
    return requests.post(f'{url}/channels/create', json={
        'token': user_4['token'],
        'name': 'Group 4',
        'is_public': True,
    }).json()

# Private channels fixtures
@pytest.fixture
def private_channel_1(url, user_1):
    return requests.post(f'{url}/channels/create', json={
        'token': user_1['token'],
        'name': 'Group 1',
        'is_public': False,
    }).json()

@pytest.fixture
def private_channel_2(url, user_2):
    return requests.post(f'{url}/channels/create', json={
        'token': user_2['token'],
        'name': 'Group 2',
        'is_public': False,
    }).json()

@pytest.fixture
def private_channel_3(url, user_3):
    return requests.post(f'{url}/channels/create', json={
        'token': user_3['token'],
        'name': 'Group 3',
        'is_public': False,
    }).json()

# Message fixture
@pytest.fixture
def default_message(url, user_1, public_channel_1):
    return requests.post(f'{url}/message/send', json={
        'token': user_1['token'],
        'channel_id': public_channel_1['channel_id'],
        'message': "Hey channel!",
    }).json()