import auth
import channel
import channels
import pytest
from error import InputError, AccessError
from data import data

# channel_invite



# channel_details



# channel_messages

# Testing when an invalid channel_id is used as a parameter
def test_input_channel_id():
    start = 0
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')

    with pytest.raises(InputError):
        channel.channel_messages(user['token'], 0, start)
        channel.channel_messages(user['token'], -1, start)
        channel.channel_messages(user['token'], 3, start)

# Testing amount of messages on a newly created channel
def test_input_start():
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')
    channel_id = channels.channels_create(user['token'], 'Group 1', True)

    with pytest.raises(InputError):
        channel.channel_messages(user['token'], 0, 1)
        channel.channel_messages(user['token'], -1, 100)
        channel.channel_messages(user['token'], 3, 50)

# Testing is another user can access the channel
def test_access_member():
    user1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user2 = auth.auth_register('janesmith@gmail.com', 'password', 'Jane', 'Smith')
    auth.auth_login('johnsmith@gmail.com', 'password')
    channel_id = channels.channels_create(user2['token'], 'Group 1', True)

    with pytest.raises(AccessError):
        channel.channel_messages(user1['token'], channel_id, 0)



# channel_leave



# channel_join



# channel_addowner



# channel_removeowner



