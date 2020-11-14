"""
Testing implementation of helper functions in action.py and validate.py

Only testing some functions to ensure full coverage of action.py and validate.py

2020 T3 COMP1531 Major Project
"""

from src.feature.other import clear
from src.feature.action import find_message_id_in_channel, generate_token, token_to_handle_name
from src.globals import NON_EXIST
import src.feature.auth as auth
import src.feature.channels as channels
import pickle

from src.feature.validate import validate_token_as_channel_member

def test_validate_token_as_channel_member_invalid_token(user_1, public_channel_1, logout_user_1):
    """Test if the token is invalid.
    """
    data = pickle.load(open("data.p", "rb"))
    assert not validate_token_as_channel_member(data, user_1['token'], public_channel_1['channel_id'])

def test_generate_token(user_1):
    data = pickle.load(open("data.p", "rb"))
    assert generate_token(data, NON_EXIST) == NON_EXIST

def test_convert_token_to_u_id():
    data = pickle.load(open("data.p", "rb"))
    assert generate_token(data, "12345") == NON_EXIST
    clear()

def test_token_to_handle_name():
    data = pickle.load(open("data.p", "rb"))
    assert token_to_handle_name(data, "12345") == NON_EXIST
    clear()

def test_find_message_id_in_channel(user_1, public_channel_1):
    data = pickle.load(open("data.p", "rb"))
    assert find_message_id_in_channel(data, NON_EXIST) == NON_EXIST
    clear()