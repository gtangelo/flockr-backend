"""
Implementation of the routes for the flockr backend using Flask. 

2020 T3 COMP1531 Major Project
"""
import sys
from json import dumps
from flask import Flask, request
from flask_cors import CORS

import src.feature.auth as auth
import src.feature.channel as channel
import src.feature.channels as channels
import src.feature.message as message
import src.feature.standup as standup
import src.feature.user as user

from src.feature.other import clear, users_all, admin_userpermission_change, search

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#------------------------------------------------------------------------------#
#                                   auth.py                                    #
#------------------------------------------------------------------------------#

@APP.route("/auth/login", methods=['POST'])
def route_auth_login():
    """Given a registered users' email and password and generates a valid token
    for the user to remain authenticated

    Args:
        email (string)
        password (string)

    Returns:
        (dict): { u_id, token }
    """
    payload = request.get_json()
    return dumps(auth.auth_login(payload['email'], payload['password']))


@APP.route("/auth/logout", methods=['POST'])
def route_auth_logout():
    """Given an active token, invalidates the token to log the user out. If a
    valid token is given, and the user is successfully logged out, it returns
    true, otherwise false.

    Args:
        token (string): unique identifier for user

    Returns:
        (dict): { is_success }
    """
    payload = request.get_json()
    return dumps(auth.auth_logout(payload['token']))


@APP.route("/auth/register", methods=['POST'])
def route_auth_register():
    """Given a user's first and last name, email address, and password, create
    a new account for them and return a new token for authentication in their
    session. A handle is generated that is the concatentation of a lowercase-only
    first name and last name. If the concatenation is longer than 20 characters,
    it is cutoff at 20 characters. If the handle is already taken, you may modify
    the handle in any way you see fit to make it unique.

    Args:
        email (string)
        password (string)
        name_first (string)
        name_last (string)

    Returns:
        (dict): { u_id, token }
    """
    payload = request.get_json()
    email = payload['email']
    password = payload['password']
    name_first = payload['name_first']
    name_last = payload['name_last']
    return dumps(auth.auth_register(email, password, name_first, name_last))

@APP.route("/auth/passwordreset/request", methods=['POST'])
def route_auth_passwordreset_request():
    """Given an email address, if the user is a registered user, send's them a 
    an email containing a specific secret code, that when entered in 
    auth_passwordreset_reset, shows that the user trying to reset the password 
    is the one who got sent this email.

    Args:
        email (string)

    Returns:
        (dict): {}
    """
    payload = request.get_json()
    email = payload['email']
    return dumps(auth.auth_passwordreset_request(email))    

@APP.route("/auth/passwordreset/reset", methods=['POST'])
def route_auth_passwordreset_reset():
    """Given a reset code for a user, set that user's new password to the 
    password provided

    Args:
        reset_code (string)
        new_password (string)

    Returns:
        (dict): {}
    """
    payload = request.get_json()
    reset_code = payload['reset_code']
    new_password = payload['new_password']
    return dumps(auth.auth_passwordreset_reset(reset_code, new_password))

#------------------------------------------------------------------------------#
#                                  channel.py                                  #
#------------------------------------------------------------------------------#

@APP.route("/channel/invite", methods=['POST'])
def route_channel_invite():
    """Invites a user (with user id u_id) to join a channel with ID channel_id.
    Once invited the user is added to the channel immediately

    Args:
        token (string)
        channel_id (int)
        u_id (int):

    Returns:
        (dict): {}
    """
    payload = request.get_json()
    channel_id = int(payload['channel_id'])
    u_id = int(payload['u_id'])
    return dumps(channel.channel_invite(payload['token'], channel_id, u_id))


@APP.route("/channel/details", methods=['GET'])
def route_channel_details():
    """Given a Channel with ID channel_id that the authorised user is part of,
    provide basic details about the channel

    Args:
        token (string)
        channel_id (int)

    Returns:
        (dict): { name, owner_members, all_members }
    """
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return dumps(channel.channel_details(token, channel_id))


@APP.route("/channel/messages", methods=['GET'])
def route_channel_messages():
    """Given a Channel with ID channel_id that the authorised user is part of,
    return up to 50 messages between index "start" and "start + 50". Message
    with index 0 is the most recent message in the channel. This function returns
    a new index "end" which is the value of "start + 50", or, if this function
    has returned the least recent messages in the channel, returns -1 in "end"
    to indicate there are no more messages to load after this return.

    Args:
        token (string)
        channel_id (int)
        start (int)

    Returns:
        (dict): { messages, start, end }
    """
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))
    return dumps(channel.channel_messages(token, channel_id, start))


@APP.route("/channel/leave", methods=['POST'])
def route_channel_leave():
    """Given a channel ID, the user removed as a member of this channel

    Args:
        token (string)
        channel_id (int)

    Returns:
        (dict): {}
    """
    payload = request.get_json()
    channel_id = int(payload['channel_id'])
    return dumps(channel.channel_leave(payload['token'], channel_id))


@APP.route("/channel/join", methods=['POST'])
def route_channel_join():
    """Given a channel_id of a channel that the authorised user can join, adds
    them to that channel

    Args:
        token (string)
        channel_id (int)

    Returns:
        (dict): {}
    """
    payload = request.get_json()
    channel_id = int(payload['channel_id'])
    return dumps(channel.channel_join(payload['token'], channel_id))


@APP.route("/channel/addowner", methods=['POST'])
def route_channel_addowner():
    """Make user with user id u_id an owner of this channel

    Args:
        token (string)
        channel_id (int)
        u_id (int)

    Returns:
        (dict): {}
    """
    payload = request.get_json()
    channel_id = int(payload['channel_id'])
    u_id = int(payload['u_id'])
    return dumps(channel.channel_addowner(payload['token'], channel_id, u_id))


@APP.route("/channel/removeowner", methods=['POST'])
def route_channel_removeowner():
    """Remove user with user id u_id an owner of this channel

    Args:
        token (string)
        channel_id (int)
        u_id (int)

    Returns:
        (dict): {}
    """
    payload = request.get_json()
    channel_id = int(payload['channel_id'])
    u_id = int(payload['u_id'])
    return dumps(channel.channel_removeowner(payload['token'], channel_id, u_id))

#------------------------------------------------------------------------------#
#                                 channels.py                                  #
#------------------------------------------------------------------------------#


@APP.route("/channels/list", methods=['GET'])
def route_channels_list():
    """Provide a list of all channels (and their associated details) that the
    authorised user is part of

    Args:
        token (string): unique identifer of user

    Returns:
        (dict): { channels }
    """
    return dumps(channels.channels_list(request.args.get('token')))


@APP.route("/channels/listall", methods=['GET'])
def route_channels_listall():
    """Provide a list of all created channels (and their associated details)

    Args:
        token (string): unique identifer of user

    Returns:
        (dict): { channels }
    """
    return dumps(channels.channels_listall(request.args.get('token')))


@APP.route("/channels/create", methods=['POST'])
def route_channels_create():
    """Creates a new channel with that name that is either a public or private.

    Args:
        token (string)
        name (string)
        is_public (bool)

    Returns:
        (dict): { channel_id }
    """
    payload = request.get_json()
    is_public = bool(payload['is_public'])
    return dumps(channels.channels_create(payload['token'], payload['name'], is_public))


#------------------------------------------------------------------------------#
#                                  message.py                                  #
#------------------------------------------------------------------------------#

@APP.route("/message/send", methods=['POST'])
def route_message_send():
    """Send a message from authorised_user to the channel specified by channel_id

    Args:
        token (string)
        channel_id (int)
        message (string)

    Returns:
        (dict): { message_id }
    """
    payload = request.get_json()
    channel_id = int(payload['channel_id'])
    return dumps(message.message_send(payload['token'], channel_id, payload['message']))


@APP.route("/message/remove", methods=['DELETE'])
def route_message_remove():
    """Given a message_id for a message, this message is removed from the channel

    Args:
        token (string)
        message_id (int)

    Returns:
        (dict): {}
    """
    payload = request.get_json()
    message_id = int(payload['message_id'])
    return dumps(message.message_remove(payload['token'], message_id))


@APP.route("/message/edit", methods=['PUT'])
def route_message_edit():
    """Given a message, update it's text with new text. If the new message is an
    empty string, the message is deleted.

    Args:
        token (string)
        message_id (int)
        message (string)

    Returns:
        (dict): {}
    """
    payload = request.get_json()
    message_id = int(payload['message_id'])
    return dumps(message.message_edit(payload['token'], message_id, payload['message']))


@APP.route("/message/sendlater", methods=['POST'])
def route_message_sendlater():
    """Given a message, update it's text with new text. If the new message is an
    empty string, the message is deleted.

    Args:
        token (string)
        message_id (int)
        message (string)

    Returns:
        (dict): {}
    """
    payload = request.get_json()
    channel_id = int(payload['channel_id'])
    time_sent = int(payload['time_sent'])
    return dumps(message.message_sendlater(payload['token'], channel_id, payload['message'], time_sent))


@APP.route("/message/react", methods=['POST'])
def route_message_react():
    """Given a message within a channel the authorised user is part of, add 
    a "react" to that particular message

    Args:
        token (string)
        message_id (int)
        react_id (int)

    Returns:
        (dict): {}
    """
    return dumps({})

@APP.route("/message/unreact", methods=['POST'])
def route_message_unreact():
    """Given a message within a channel the authorised user is part of, 
    remove a "react" to that particular message

    Args:
        token (string)
        message_id (int)
        react_id (int)

    Returns:
        (dict): {}
    """
    return dumps({})

@APP.route("/message/pin", methods=['POST'])
def route_message_pin():
    """Given a message within a channel, mark it as "pinned" to be given 
    special display treatment by the frontend

    Args:
        token (string)
        message_id (int)

    Returns:
        (dict)
    """
    return dumps({})

@APP.route("/message/unpin", methods=['POST'])
def route_message_unpin():
    """Given a message within a channel, remove it's mark as unpinned

    Args:
        token (string)
        message_id (int)

    Returns:
        (dict)
    """
    return dumps({})

#------------------------------------------------------------------------------#
#                                   user.py                                    #
#------------------------------------------------------------------------------#


@APP.route("/user/profile", methods=['GET'])
def route_user_profile():
    """For a valid user, returns information about their user_id, email, first
    name, last name, and handle

    Args:
        token (string)
        u_id (int)

    Returns:
        (dict): { user }
    """
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    return dumps(user.user_profile(token, u_id))


@APP.route("/user/profile/setname", methods=['PUT'])
def route_user_profile_setname():
    payload = request.get_json()
    token = payload['token']
    name_first = payload['name_first']
    name_last = payload['name_last']
    return dumps(user.user_profile_setname(token, name_first, name_last))


@APP.route("/user/profile/setemail", methods=['PUT'])
def route_user_profile_setemail():
    """Update the authorised user's email.

    Args:
        token (string): unique identifier of user.
        email (string): what the email will be set to.

    Returns:
        (dict): Contains no key types.
    """
    payload = request.get_json()
    return dumps(user.user_profile_setemail(payload['token'], payload['email']))


@APP.route("/user/profile/sethandle", methods=['PUT'])
def route_user_profile_sethandle():
    payload = request.get_json()
    return dumps(user.user_profile_sethandle(payload['token'], payload['handle_str']))

@APP.route("/user/profile/uploadphoto", methods=['POST'])
def route_user_profile_uploadphoto():
    """Given a URL of an image on the internet, crops the image within bounds (x_start, y_start) and (x_end, y_end). Position (0,0) is the top left.

    Args:
        token (string)
        img_url (string)
        x_start (int)
        y_start (int)
        x_end (int)
        y_end (int)

    Returns:
        (dict): {}
    """
    return dumps({})

#------------------------------------------------------------------------------#
#                                 standup.py                                   #
#------------------------------------------------------------------------------#

@APP.route("/standup/start", methods=['POST'])
def route_standup_start():
    """For a given channel, start the standup period whereby for the next 
    "length" seconds if someone calls "standup_send" with a message, it is 
    buffered during the X second window then at the end of the X second window 
    a message will be added to the message queue in the channel from the user 
    who started the standup. X is an integer that denotes the number of seconds 
    that the standup occurs for

    Args:
        token (string)
        channel_id (int)
        length (int)

    Returns:
        (dict): { time_finish }
    """
    payload = request.get_json()
    token = payload['token']
    channel_id = int(payload['channel_id'])
    length = int(payload['length'])
    return dumps(standup.standup_start(token, channel_id, length))


@APP.route("/standup/active", methods=['GET'])
def route_standup_active():
    """For a given channel, return whether a standup is active in it, and what
    time the standup finishes. If no standup is active, then time_finish
    returns None

    Args:
        token (string)
        channel_id (int)

    Returns:
        (dict): { is_active, time_finish }
    """
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return dumps(standup.standup_active(token, channel_id))


@APP.route("/standup/send", methods=['POST'])
def route_standup_send():
    """Sending a message to get buffered in the standup queue, assuming a
    standup is currently active

    Args:
        token (string)
        channel_id (int)
        message (string)

    Returns:
        (dict): {}
    """
    payload = request.get_json()
    token = payload['token']
    channel_id = int(payload['channel_id'])
    message = payload['message']
    return dumps(standup.standup_send(token, channel_id, message))

#------------------------------------------------------------------------------#
#                                  other.py                                    #
#------------------------------------------------------------------------------#

@APP.route("/users/all", methods=['GET'])
def route_users_all():
    """Returns a list of all users and their associated details

    Args:
        token (string)

    Returns:
        (dict): { users }
    """
    return dumps(users_all(request.args.get('token')))


@APP.route("/admin/userpermission/change", methods=['POST'])
def route_admin_userpermission_change():
    """Given a User by their user ID, set their permissions to new permissions
    described by permission_id

    Args:
        token (string)
        u_id (int)
        permission_id (int)
    """
    payload = request.get_json()
    u_id = int(payload['u_id'])
    permission_id = int(payload['permission_id'])
    return dumps(admin_userpermission_change(payload['token'], u_id, permission_id))


@APP.route("/search", methods=['GET'])
def route_search():
    """Given a query string, return a collection of messages in all of the
    channels that the user has joined that match the query

    Args:
        token (string)
        query_str (string)

    Returns:
        (dict): { messages }
    """
    return dumps(search(request.args.get('token'), request.args.get('query_str')))


@APP.route("/clear", methods=['DELETE'])
def route_clear():
    """Resets the internal data of the application to it's initial state

    Returns:
        (dict): {}
    """
    return dumps(clear())


if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port
