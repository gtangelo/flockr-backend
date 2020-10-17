import auth
import channels
from action import get_lowest_u_id_user_in_channel
from other import clear
from validate import validate_token_as_channel_member

def test_get_lowest_u_id_user_in_channel_no_users():
    """ Test if a channel has no members
    """
    clear()
    channel = {}
    channel['all_members'] = []
    assert get_lowest_u_id_user_in_channel(channel) == {}
    clear()

def test_validate_token_as_channel_member_invalid_token():
    """Test if the token is invalid.
    """
    user = auth.auth_register("johnsmith@gmail.com", "password", "John", "Smith")
    channel_data = channels.channels_create(user['token'], "Test 1", True)
    auth.auth_logout(user['token'])
    assert not validate_token_as_channel_member(user['token'], channel_data['channel_id'])