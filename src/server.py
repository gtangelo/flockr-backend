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
from error import AccessError, InputError
from other import clear, users_all, admin_userpermission_change, search

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
    return dumps({
        'u_id': 1,
        'token': '12345',
    })



@APP.route("/auth/logout", methods=['POST'])
def route_auth_logout():
    return dumps({
        'is_success': True,
    })




@APP.route("/auth/register", methods=['POST'])
def route_auth_register():
    return dumps({
        'u_id': 1,
        'token': '12345',
    })


#------------------------------------------------------------------------------#
#                                  channel.py                                  #
#------------------------------------------------------------------------------#

@APP.route("/channel/invite", methods=['POST'])
def route_channel_invite():
    return dumps({})




@APP.route("/channel/details", methods=['GET'])
def route_channel_details():
    return dumps({
        'name': 'Hayden',
        'owner_members': [
            {
                'u_id': 1,
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
            }
        ],
        'all_members': [
            {
                'u_id': 1,
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
            }
        ],
    })






@APP.route("/channel/messages", methods=['GET'])
def route_channel_messages():
    return dumps({
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
        'start': 0,
        'end': 50,
    })






@APP.route("/channel/leave", methods=['POST'])
def route_channel_leave():
    return dumps({})




@APP.route("/channel/join", methods=['POST'])
def route_channel_join():
    return dumps({})




@APP.route("/channel/addowner", methods=['POST'])
def route_channel_addowner():
    return dumps({})



@APP.route("/channel/removeowner", methods=['POST'])
def route_channel_removeowner():
    return dumps({})



#------------------------------------------------------------------------------#
#                                 channels.py                                  #
#------------------------------------------------------------------------------#


@APP.route("/channels/list", methods=['GET'])
def route_channels_list():
    return dumps({
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    })






@APP.route("/channels/listall", methods=['GET'])
def route_channels_listall():
    return dumps({
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    })






@APP.route("/channels/create", methods=['POST'])
def route_channels_create():
    return dumps({
        'channel_id': 1,
    })




#------------------------------------------------------------------------------#
#                                  message.py                                  #
#------------------------------------------------------------------------------#

@APP.route("/message/send", methods=['POST'])
def route_message_send():
    return dumps({
        'message_id': 1,
    })





@APP.route("/message/remove", methods=['DELETE'])
def route_message_remove():
    return dumps({})




@APP.route("/message/edit", methods=['PUT'])
def route_message_edit():
    return dumps({})



#------------------------------------------------------------------------------#
#                                   user.py                                    #
#------------------------------------------------------------------------------#


@APP.route("/user/profile", methods=['GET'])
def route_user_profile():
    return dumps({
        'user': {
        	'u_id': 1,
        	'email': 'cs1531@cse.unsw.edu.au',
        	'name_first': 'Hayden',
        	'name_last': 'Jacobs',
        	'handle_str': 'hjacobs',
        },
    })







@APP.route("/user/profile/setname", methods=['PUT'])
def route_user_profile_setname():
    return dumps({})





@APP.route("/user/profile/setemail", methods=['PUT'])
def route_user_profile_setemail():
    return dumps({})




@APP.route("/user/profile/sethandle", methods=['PUT'])
def route_user_profile_sethandle():
    return dumps({})



#------------------------------------------------------------------------------#
#                                  other.py                                    #
#------------------------------------------------------------------------------#


@APP.route("/users/all", methods=['GET'])
def route_users_all():
    return dumps({
        'users': [
            {
                'u_id': 1,
                'email': 'cs1531@cse.unsw.edu.au',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'hjacobs',
            },
        ],
    })






@APP.route("/admin/userpermission/change", methods=['POST'])
def route_admin_userpermission_change():
    return dumps({})




@APP.route("/search", methods=['GET'])
def route_search():
    return dumps({
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
    })




@APP.route("/clear", methods=['DELETE'])
def route_clear():
    clear()
    return dumps({})


if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port
