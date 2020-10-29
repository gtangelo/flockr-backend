"""
Testing implementation of helper functions in action.py and validate.py

Only testing some functions to ensure full coverage of action.py and validate.py

2020 T3 COMP1531 Major Project
"""

import src.feature.auth as auth
import src.feature.channels as channels

from src.feature.validate import validate_token_as_channel_member

def test_validate_token_as_channel_member_invalid_token():
    """Test if the token is invalid.
    """
    user = auth.auth_register("johnsmith@gmail.com", "password", "John", "Smith")
    channel_data = channels.channels_create(user['token'], "Test 1", True)
    auth.auth_logout(user['token'])
    assert not validate_token_as_channel_member(user['token'], channel_data['channel_id'])