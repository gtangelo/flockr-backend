"""
Pytest fixtures to use in testing files.

2020 T3 COMP1531 Major Project
"""

import pytest

import src.feature.auth as auth
import src.feature.channels as channels
import src.feature.message as message

from src.feature.other import clear

THUMBS_UP = 1
THUMBS_DOWN = 2

# User register fixtures
@pytest.fixture
def user_1():
    clear()
    return auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')

@pytest.fixture
def logout_user_1(user_1):
    return auth.auth_logout(user_1['token'])

@pytest.fixture
def user_2():
    return auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    
@pytest.fixture
def user_3():
    return auth.auth_register('jacesmith@gmail.com', 'password', 'Jace', 'Smith')
    
@pytest.fixture
def user_4():
    return auth.auth_register('janicesmith@gmail.com', 'password', 'Janice', 'Smith')

# Public channels fixtures
@pytest.fixture
def public_channel_1(user_1):
    return channels.channels_create(user_1['token'], 'Group 1', True)

@pytest.fixture
def public_channel_2(user_2):
    return channels.channels_create(user_2['token'], 'Group 2', True)

@pytest.fixture
def public_channel_3(user_3):
    return channels.channels_create(user_3['token'], 'Group 3', True)

@pytest.fixture
def public_channel_4(user_4):
    return channels.channels_create(user_4['token'], 'Group 4', True)

# Private channels fixtures
@pytest.fixture
def private_channel_1(user_1):
    return channels.channels_create(user_1['token'], 'Group 1', False)

@pytest.fixture
def private_channel_2(user_2):
    return channels.channels_create(user_2['token'], 'Group 1', False)

# Message fixture
@pytest.fixture
def default_message(user_1, public_channel_1):
    return message.message_send(user_1['token'], public_channel_1['channel_id'], "Hey channel!")

@pytest.fixture
def thumbs_up_default_message(user_1, public_channel_1):
    payload = message.message_send(user_1['token'], public_channel_1['channel_id'], "Hey channel!")
    message.message_react(user_1['token'], payload['message_id'], THUMBS_UP)
    return payload

@pytest.fixture
def thumbs_down_default_message(user_1, public_channel_1):
    payload = message.message_send(user_1['token'], public_channel_1['channel_id'], "Hey channel!")
    message.message_react(user_1['token'], payload['message_id'], THUMBS_DOWN)
    return payload
