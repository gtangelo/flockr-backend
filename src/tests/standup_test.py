"""
standup feature test implementation to test functions in message.py

2020 T3 COMP1531 Major Project
"""
import time
import pytest
import pickle
from datetime import timezone, datetime

import src.feature.auth as auth
import src.feature.user as user
import src.feature.channel as channel
import src.feature.standup as standup

from src.feature.other import clear
from src.classes.error import InputError, AccessError
from src.globals import STANDUP_DELAY

#------------------------------------------------------------------------------#
#                               standup_start                                  #
#------------------------------------------------------------------------------#

#?------------------------ Input/Access Error Testing ------------------------?#

def test_standup_start_expired_token(user_1, user_2, user_3, user_4, public_channel_1):
    """Testing expired token for users which have logged out
    """
    auth.auth_logout(user_1['token'])
    auth.auth_logout(user_2['token'])
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])

    with pytest.raises(AccessError):
        standup.standup_start(user_1['token'], public_channel_1['channel_id'], 10)
    with pytest.raises(AccessError):
        standup.standup_start(user_2['token'], public_channel_1['channel_id'], 10)
    with pytest.raises(AccessError):
        standup.standup_start(user_3['token'], public_channel_1['channel_id'], 10)
    with pytest.raises(AccessError):
        standup.standup_start(user_4['token'], public_channel_1['channel_id'], 10)
    clear()

def test_standup_start_invalid_token(public_channel_1):
    """Testing invalid token for users
    """
    with pytest.raises(AccessError):
        standup.standup_start(-1, public_channel_1['channel_id'], 10)
    with pytest.raises(AccessError):
        standup.standup_start('@#&!', public_channel_1['channel_id'], 10)
    with pytest.raises(AccessError):
        standup.standup_start(43.333, public_channel_1['channel_id'], 10)
    clear()

def test_standup_start_invalid_channel(user_1, user_2):
    """Testing invalid channel_ids
    """
    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], -122, 10)
    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], -642, 10)
    with pytest.raises(InputError):
        standup.standup_start(user_2['token'], '@#@!', 10)
    with pytest.raises(InputError):
        standup.standup_start(user_2['token'], 212.11, 10)
    clear()

def test_standup_start_invalid_length(user_1, user_2, public_channel_1):
    """Testing invalid time length
    """
    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], public_channel_1['channel_id'], -10)
    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], public_channel_1['channel_id'], 0)
    clear()

def test_standup_start_already_started(user_1, public_channel_1):
    """Testing when a standup is already running in channel 
    """
    standup_duration = 120
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = standup.standup_start(user_1['token'], public_channel_1['channel_id'], 120)
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], public_channel_1['channel_id'], 5)
    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], public_channel_1['channel_id'], 50)
    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], public_channel_1['channel_id'], 120)
    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], public_channel_1['channel_id'], 240)
    with pytest.raises(InputError):
        standup.standup_start(user_1['token'], public_channel_1['channel_id'], 360)
    clear()

def test_standup_start_unauthorized_user(user_1, user_2, user_3, public_channel_1):
    """(Assumption testing) Testing when a user who is not part of the channel
       tries to start a standup
    """
    with pytest.raises(AccessError):
        standup.standup_start(user_2['token'], public_channel_1['channel_id'], 2)
    with pytest.raises(AccessError):
        standup.standup_start(user_3['token'], public_channel_1['channel_id'], 2)
    clear()


#?------------------------------ Output Testing ------------------------------?#

def test_standup_start_working_example(user_1, user_2, user_3, public_channel_1):
    """Testing when standup is working, via message collation
    """
    assert channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id']) == {}
    assert channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_3['u_id']) == {}

    standup_duration = 5
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = standup.standup_start(user_1['token'], public_channel_1['channel_id'], standup_duration)
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)
    
    data = pickle.load(open("data.p", "rb"))
    assert data.specify_standup_status(public_channel_1['channel_id'])['is_active'] == True

    on_list = False
    user_one_handle = user.user_profile(user_1['token'], user_1['u_id'])['user']['handle_str']
    assert standup.standup_send(user_1['token'], public_channel_1['channel_id'], 'Hey guys!') == {}
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message'] == f'{user_one_handle}: Hey guys!':
            on_list = True
    assert not on_list

    on_list = False
    user_two_handle = user.user_profile(user_2['token'], user_2['u_id'])['user']['handle_str']
    assert standup.standup_send(user_2['token'], public_channel_1['channel_id'], 'Its working!') == {}
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message'] == f'{user_one_handle}: Hey guys!\n{user_two_handle}: Its working!':
            on_list = True
    assert not on_list

    assert standup.standup_send(user_3['token'], public_channel_1['channel_id'], 'Wohoo!') == {}
    
    data = pickle.load(open("data.p", "rb"))
    assert data.specify_standup_status(public_channel_1['channel_id'])['is_active'] == True
    time.sleep(8)
    
    data = pickle.load(open("data.p", "rb"))
    assert data.specify_standup_status(public_channel_1['channel_id'])['is_active'] == False

    on_list = False
    user_three_handle = user.user_profile(user_3['token'], user_3['u_id'])['user']['handle_str']
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message'] == f'{user_one_handle}: Hey guys!\n{user_two_handle}: Its working!\n{user_three_handle}: Wohoo!':
            on_list = True
    assert on_list
    clear()

#------------------------------------------------------------------------------#
#                               standup_active                                 #
#------------------------------------------------------------------------------#

#?------------------------ Input/Access Error Testing ------------------------?#

def test_standup_active_expired_token(user_1, user_2, user_3, user_4, public_channel_1):
    """Testing invalid token for users which have logged out
    """
    auth.auth_logout(user_1['token'])
    auth.auth_logout(user_2['token'])
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])

    with pytest.raises(AccessError):
        standup.standup_active(user_1['token'], public_channel_1['channel_id'])
    with pytest.raises(AccessError):
        standup.standup_active(user_2['token'], public_channel_1['channel_id'])
    with pytest.raises(AccessError):
        standup.standup_active(user_3['token'], public_channel_1['channel_id'])
    with pytest.raises(AccessError):
        standup.standup_active(user_4['token'], public_channel_1['channel_id'])
    clear()

def test_standup_active_invalid_token(public_channel_1):
    """Testing invalid token for users
    """
    with pytest.raises(AccessError):
        standup.standup_active(-1, public_channel_1['channel_id'])
    with pytest.raises(AccessError):
        standup.standup_active('@#&!', public_channel_1['channel_id'])
    with pytest.raises(AccessError):
        standup.standup_active(43.333, public_channel_1['channel_id'])
    clear()

def test_standup_active_invalid_channel(user_1, user_2):
    """Testing invalid channel_ids
    """
    with pytest.raises(InputError):
        standup.standup_active(user_1['token'], -122)
    with pytest.raises(InputError):
        standup.standup_active(user_1['token'], -642)
    with pytest.raises(InputError):
        standup.standup_active(user_2['token'], '@#@!')
    with pytest.raises(InputError):
        standup.standup_active(user_2['token'], 212.11)
    clear()

def test_standup_active_unauthorized_user(user_1, user_2, user_3, public_channel_1):
    """(Assumption testing) Testing when a user who is not part of the channel
       tries to see if a standup is active in that channel
    """
    standup_duration = 2
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = standup.standup_start(user_1['token'], public_channel_1['channel_id'], standup_duration)
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    information = standup.standup_active(user_1['token'], public_channel_1['channel_id'])
    assert information['is_active']
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    with pytest.raises(AccessError):
        standup.standup_active(user_2['token'], public_channel_1['channel_id'])
    with pytest.raises(AccessError):
        standup.standup_active(user_3['token'], public_channel_1['channel_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_standup_active_is_active(user_1, user_2, user_3, public_channel_1):
    """Testing when standup is active
    """
    assert channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id']) == {}
    assert channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_3['u_id']) == {}

    standup_duration = 2
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = standup.standup_start(user_1['token'], public_channel_1['channel_id'], standup_duration)
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    information = standup.standup_active(user_1['token'], public_channel_1['channel_id'])
    assert information['is_active']
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    information = standup.standup_active(user_2['token'], public_channel_1['channel_id'])
    assert information['is_active']
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    information = standup.standup_active(user_3['token'], public_channel_1['channel_id'])
    assert information['is_active']
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)
    clear()

def test_standup_active_not_active(user_1, user_2, user_3, public_channel_1):
    """Testing when standup is not active
    """
    assert channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id']) == {}
    assert channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_3['u_id']) == {}

    standup_duration = 2
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = standup.standup_start(user_1['token'], public_channel_1['channel_id'], standup_duration)
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)
    time.sleep(4)

    information = standup.standup_active(user_1['token'], public_channel_1['channel_id'])
    assert not information['is_active']
    assert information['time_finish'] == None

    information = standup.standup_active(user_2['token'], public_channel_1['channel_id'])
    assert not information['is_active']
    assert information['time_finish'] == None

    information = standup.standup_active(user_3['token'], public_channel_1['channel_id'])
    assert not information['is_active']
    assert information['time_finish'] == None
    clear()

#------------------------------------------------------------------------------#
#                                standup_send                                  #
#------------------------------------------------------------------------------#

#?------------------------ Input/Access Error Testing ------------------------?#

def test_standup_send_expired_token(user_1, user_2, user_3, user_4, public_channel_1):
    """Testing expired token for users which have logged out
    """
    auth.auth_logout(user_1['token'])
    auth.auth_logout(user_2['token'])
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])

    with pytest.raises(AccessError):
        standup.standup_send(user_1['token'], public_channel_1['channel_id'], 'Hey')
    with pytest.raises(AccessError):
        standup.standup_send(user_2['token'], public_channel_1['channel_id'], 'Hey')
    with pytest.raises(AccessError):
        standup.standup_send(user_3['token'], public_channel_1['channel_id'], 'Hey')
    with pytest.raises(AccessError):
        standup.standup_send(user_4['token'], public_channel_1['channel_id'], 'Hey')
    clear()

def test_standup_send_invalid_token(public_channel_1):
    """Testing invalid token for users
    """
    with pytest.raises(AccessError):
        standup.standup_send(-1, public_channel_1['channel_id'], 'Hey')
    with pytest.raises(AccessError):
        standup.standup_send('@#&!', public_channel_1['channel_id'], 'Hey')
    with pytest.raises(AccessError):
        standup.standup_send(43.333, public_channel_1['channel_id'], 'Hey')
    clear()

def test_standup_send_invalid_channel(user_1, user_2):
    """Testing invalid channel_ids
    """
    with pytest.raises(InputError):
        standup.standup_send(user_1['token'], -122, 'Hey')
    with pytest.raises(InputError):
        standup.standup_send(user_1['token'], -642, 'Hey')
    with pytest.raises(InputError):
        standup.standup_send(user_2['token'], '@#@!', 'Hey')
    with pytest.raises(InputError):
        standup.standup_send(user_2['token'], 212.11, 'Hey')
    clear()

def test_standup_send_more_than_1000_char(user_1, public_channel_1):
    """Testing when the message to send via standup send is over 1000 characters
    """
    message_str_1 = ("Hello" * 250)
    message_str_2 = ("HI " * 500)
    message_str_3 = ("My name is blah" * 100)

    standup_duration = 2
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = standup.standup_start(user_1['token'], public_channel_1['channel_id'], standup_duration)
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    with pytest.raises(InputError):
        standup.standup_send(user_1['token'], public_channel_1['channel_id'], message_str_1)
    with pytest.raises(InputError):
        standup.standup_send(user_1['token'], public_channel_1['channel_id'], message_str_2)
    with pytest.raises(InputError):
        standup.standup_send(user_1['token'], public_channel_1['channel_id'], message_str_3)
    clear()

def test_standup_send_no_standup(user_1, user_2, user_3, public_channel_1):
    """Testing when no standup is currently running in channel specified
    """
    assert channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id']) == {}
    assert channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_3['u_id']) == {}

    with pytest.raises(InputError):
        standup.standup_send(user_1['token'], public_channel_1['channel_id'], 'Hey')
    with pytest.raises(InputError):
        standup.standup_send(user_2['token'], public_channel_1['channel_id'], 'Hey')
    with pytest.raises(InputError):
        standup.standup_send(user_3['token'], public_channel_1['channel_id'], 'Hey')
    clear()

def test_standup_send_unauthorized_user(user_1, user_2, user_3, public_channel_1):
    """Testing when a user who is not part of the channel tries to send a standup to
       that channel
    """
    standup_duration = 2
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = standup.standup_start(user_1['token'], public_channel_1['channel_id'], standup_duration)
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    information = standup.standup_active(user_1['token'], public_channel_1['channel_id'])
    assert information['is_active']
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    with pytest.raises(AccessError):
        standup.standup_send(user_2['token'], public_channel_1['channel_id'], 'Hey')
    with pytest.raises(AccessError):
        standup.standup_send(user_3['token'], public_channel_1['channel_id'], 'Hey')
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_standup_send_working_example(user_1, user_2, user_3, public_channel_1):
    """Testing when standup send is working, via message collation
    """
    assert channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id']) == {}
    assert channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_3['u_id']) == {}

    standup_duration = 5
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    information = standup.standup_start(user_1['token'], public_channel_1['channel_id'], 2)
    assert (curr_time + standup_duration - STANDUP_DELAY) <= information['time_finish'] and\
    information['time_finish'] <= (curr_time + standup_duration + STANDUP_DELAY)

    on_list = False
    user_one_handle = user.user_profile(user_1['token'], user_1['u_id'])['user']['handle_str']
    assert standup.standup_send(user_1['token'], public_channel_1['channel_id'], 'Pizza!') == {}
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message'] == f'{user_one_handle}: Pizza!':
            on_list = True
    assert not on_list
    
    assert standup.standup_send(user_2['token'], public_channel_1['channel_id'], 'Water!') == {}
    assert standup.standup_send(user_3['token'], public_channel_1['channel_id'], 'Melon!') == {}
    time.sleep(7)

    on_list = False
    user_two_handle = user.user_profile(user_2['token'], user_2['u_id'])['user']['handle_str']
    user_three_handle = user.user_profile(user_3['token'], user_3['u_id'])['user']['handle_str']
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message'] == f'{user_one_handle}: Pizza!\n{user_two_handle}: Water!\n{user_three_handle}: Melon!':
            on_list = True
    assert on_list
    clear()

#------------------------------------------------------------------------------#
#                          user_profile_uploadphoto                            #
#------------------------------------------------------------------------------#

#?------------------------ Input/Access Error Testing ------------------------?#

def test_img_url_invalid_token(user_1, logout_user_1):
    """Test for a non-registered/invalid user. (Invalid token)
    """
    img_url = "https://www.ottophoto.com/kirlian/kirlian_1/kirlian12.jpg"
    with pytest.raises(AccessError):
        user.user_profile_uploadphoto(user_1['token'], img_url, 0, 0, 1, 1)
    clear()

def test_img_url_status_not_200(user_1):
    """ Test case where img_url returns a HTTP status other than 200.
    """
    x_start = 0
    x_end = 1
    y_start = 0
    y_end = 1
    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_1['token'], 'https://fake_img', x_start, y_start, x_end, y_end)
    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_1['token'], 'https://', x_start, y_start, x_end, y_end)
    clear()

def test_img_url_xy_dimensions_not_valid(user_1):
    """ Test case when any of x_start, y_start, x_end, y_end are not within the
    dimensions of the image at the URL.
    """
    img_url = "https://www.ottophoto.com/kirlian/kirlian_1/kirlian12.jpg"
    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_1['token'], img_url, -1, -7, -1000, -777)
    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_1['token'], img_url, 'a', 'b', 'c', 'd')
    clear()

def test_img_url_forbidden_access(user_1):
    """ Test case where image uploaded cannot fetch its url due to a forbidden access
    """
    img_url = "http://pngimg.com/uploads/circle/circle_PNG62.png"
    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_1['token'], img_url, 0, 0, 1, 1)
    clear()

def test_img_url_not_jpg(user_1):
    """ Test case where image uploaded is not a JPG
    """
    img_url = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_1['token'], img_url, 0, 0, 1, 1)
    clear()

#?--------------------------- Output Testing ---------------------------------?#

def test_img_url_normal_case(user_1):
    """Test for a normal case where user uploads a jpg img
    """
    x_start = 0
    x_end = 500
    y_start = 0
    y_end = 341
    img_url = "https://www.ottophoto.com/kirlian/kirlian_1/kirlian12.jpg"
    user.user_profile_uploadphoto(user_1['token'], img_url, x_start, y_start, x_end, y_end)
    user_profile = user.user_profile(user_1['token'], user_1['u_id'])
    user_handle_1 = data.get_user_details(user_1['u_id'])
    assert user_profile['user']['profile_img_url'] == f'static/{user_handle_1["handle_str"]}.jpg'
    clear()

def test_img_url_multiple_users_upload_and_change(user_1, user_2, user_3):
    """Test for a when multiple users upload profile images and some change them.
    """
    x_start = 0
    x_end = 500
    y_start = 0
    y_end = 341
    img_url_1 = "https://www.ottophoto.com/kirlian/kirlian_1/kirlian12.jpg"
    user.user_profile_uploadphoto(user_1['token'], img_url_1, x_start, y_start, x_end, y_end)
    user_profile_1 = user.user_profile(user_1['token'], user_1['u_id'])
    user_handle_1 = data.get_user_details(user_1['u_id'])
    assert user_profile_1['user']['profile_img_url'] == f'static/{user_handle_1["handle_str"]}.jpg'

    x_start = 0
    x_end = 500
    y_start = 0
    y_end = 341
    img_url_2 = "https://2017.brucon.org/images/b/bc/Twitter_logo.jpg"
    user.user_profile_uploadphoto(user_1['token'], img_url_2, x_start, y_start, x_end, y_end)
    user_handle_1 = data.get_user_details(user_1['u_id'])

    x_start = 0
    x_end = 400
    y_start = 0
    y_end = 350
    img_url_3 = "https://www.w3schools.com/w3css/img_nature.jpg"
    user.user_profile_uploadphoto(user_2['token'], img_url_3, x_start, y_start, x_end, y_end)
    user_handle_2 = data.get_user_details(user_2['u_id'])

    x_start = 500
    x_end = 1500
    y_start = 500
    y_end = 1000
    img_url_4 = "https://upload.wikimedia.org/wikipedia/commons/4/41/Sunflower_from_Silesia2.jpg"
    user.user_profile_uploadphoto(user_3['token'], img_url_4, x_start, y_start, x_end, y_end)
    user_handle_3 = data.get_user_details(user_3['u_id'])

    user_profile_1 = user.user_profile(user_1['token'], user_1['u_id'])
    user_profile_2 = user.user_profile(user_2['token'], user_2['u_id'])
    user_profile_3 = user.user_profile(user_3['token'], user_3['u_id'])
    assert user_profile_1['user']['profile_img_url'] == f'static/{user_handle_1["handle_str"]}.jpg'
    assert user_profile_2['user']['profile_img_url'] == f'static/{user_handle_2["handle_str"]}.jpg'
    assert user_profile_3['user']['profile_img_url'] == f'static/{user_handle_3["handle_str"]}.jpg'
    clear()
