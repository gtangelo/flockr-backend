"""
Implementation of the routes for the flockr backend using Flask. 

2020 T3 COMP1531 Major Project
"""
import sys
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from error import InputError

import action
import channel
import channels
import message
import user
import auth
from error import AccessError, InputError
from other import clear, users_all, admin_userpermission_change, search
from data import data

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

# Example
@APP.route("/echo", methods=['GET'])
def route_echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })


#------------------------------------------------------------------------------#
#                                   auth.py                                    #
#------------------------------------------------------------------------------#

@APP.route("/auth/login", methods=['POST'])
def route_auth_login():
    email = request.get_json()['email']
    password = request.get_json()['password']
    return dumps(auth.auth_login(email, password))



@APP.route("/auth/logout", methods=['POST'])
def route_auth_logout():
    token = request.get_json()['token']
    return dumps(auth.auth_logout(token))




@APP.route("/auth/register", methods=['POST'])
def route_auth_register():
    email = request.get_json()['email']
    password = request.get_json()['password']
    name_first = request.get_json()['name_first']
    name_last = request.get_json()['name_last']
    return dumps(auth.auth_register(email, password, name_first, name_last))


#------------------------------------------------------------------------------#
#                                  channel.py                                  #
#------------------------------------------------------------------------------#

@APP.route("/channel/invite", methods=['POST'])
def route_channel_invite():
    token = request.get_json()['token']
    channel_id = request.get_json()['channel_id']
    u_id = request.get_json()['u_id']

    empty_dict = channel.channel_invite(token, channel_id, u_id)
    return dumps(empty_dict)




@APP.route("/channel/details", methods=['GET'])
def route_channel_details():
    token = request.args.get('token')
    try:
        channel_id = int(request.args.get('channel_id'))
    except:
        channel_id = request.args.get('channel_id')
    channel_information = channel.channel_details(token, channel_id)
    return dumps(channel_information)





@APP.route("/channel/messages", methods=['GET'])
def route_channel_messages():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))
    return dumps(channel.channel_messages(token, channel_id, start))






@APP.route("/channel/leave", methods=['POST'])
def route_channel_leave():
    payload = request.get_json()
    return dumps(channel.channel_leave(payload['token'], payload['channel_id']))




@APP.route("/channel/join", methods=['POST'])
def route_channel_join():
    """Given a channel_id of a channel that the authorised user can join,
    adds them to that channel

    Returns:
        dict: {}
    """
    token = request.get_json()['token']
    channel_id = request.get_json()['channel_id']
    return dumps(channel.channel_join(token, channel_id))




@APP.route("/channel/addowner", methods=['POST'])
def route_channel_addowner():
    """Make user with user id u_id an owner of this channel

    Returns:
        dict: {}
    """
    token = request.get_json()['token']
    channel_id = request.get_json()['channel_id']
    u_id = request.get_json()['u_id']
    return dumps(channel.channel_addowner(token, channel_id, u_id))



@APP.route("/channel/removeowner", methods=['POST'])
def route_channel_removeowner():
    """Remove user with user id u_id an owner of this channel

    Returns:
        dict: {}
    """
    token = request.get_json()['token']
    channel_id = request.get_json()['channel_id']
    u_id = request.get_json()['u_id']
    return dumps(channel.channel_removeowner(token, channel_id, u_id))



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
    member_channels = channels.channels_list(request.args.get('token'))

    return dumps(member_channels)


@APP.route("/channels/listall", methods=['GET'])
def route_channels_listall():
    """Provide a list of all created channels (and their associated details)

    Args:
        token (string): unique identifer of user

    Returns:
        (dict): { channels }
    """
    all_channels = channels.channels_listall(request.args.get('token'))

    return dumps(all_channels)


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
    info = request.get_json()
    new_channel = channels.channels_create(info['token'], info['name'], info['is_public'])

    return dumps({
        'channel_id': int(new_channel['channel_id']),
    })


#------------------------------------------------------------------------------#
#                                  message.py                                  #
#------------------------------------------------------------------------------#

@APP.route("/message/send", methods=['POST'])
def route_message_send():
    """Send a message from authorised_user to the channel specified by channel_id

    Returns:
        dict: message_id
    """
    token = request.get_json()['token']
    channel_id = request.get_json()['channel_id']
    msg = request.get_json()['message']

    message_id = message.message_send(token, channel_id, msg)
    return dumps(message_id)





@APP.route("/message/remove", methods=['DELETE'])
def route_message_remove():
    token = request.get_json()['token']
    message_id = request.get_json()['message_id']
    empty_dict = message.message_remove(token, message_id)
    return dumps(empty_dict)



@APP.route("/message/edit", methods=['PUT'])
def route_message_edit():
    token = request.get_json()['token']
    message_id = request.get_json()['message_id']
    new_message = request.get_json()['message']
    empty_dict = message.message_edit(token, message_id, new_message)
    return dumps(empty_dict)

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
    profile = user.user_profile(token, u_id)
    return dumps(profile)


@APP.route("/user/profile/setname", methods=['PUT'])
def route_user_profile_setname():
    token = request.get_json()['token']
    name_first = request.get_json()['name_first']
    name_last = request.get_json()['name_last']
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
    info = request.get_json()
    return dumps(user.user_profile_setemail(info['token'], info['email']))


@APP.route("/user/profile/sethandle", methods=['PUT'])
def route_user_profile_sethandle():
    return dumps({})



#------------------------------------------------------------------------------#
#                                  other.py                                    #
#------------------------------------------------------------------------------#


@APP.route("/users/all", methods=['GET'])
def route_users_all():
    """Returns a list of all users and their associated details

    Returns:
        dict: users
    """
    return dumps(users_all(request.args.get('token')))






@APP.route("/admin/userpermission/change", methods=['POST'])
def route_admin_userpermission_change():
    payload = request.get_json()
    u_id = int(payload['u_id'])
    permission_id = int(payload['permission_id'])
    return dumps(admin_userpermission_change(payload['token'], u_id, permission_id))


@APP.route("/search", methods=['GET'])
def route_search():
    """Given a query string, return a collection of messages in all of the
    channels that the user has joined that match the query

    Returns:
        dict: messages
    """
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    return dumps(search(token, query_str))




@APP.route("/clear", methods=['DELETE'])
def route_clear():
    clear()
    return dumps({})


if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port
