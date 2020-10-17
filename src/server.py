"""
Implementation of the routes for the flockr backend using Flask. 

2020 T3 COMP1531 Major Project
"""
import sys
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from error import InputError

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
    return {
        'u_id': 1,
        'token': '12345',
    }



@APP.route("/auth/logout", methods=['POST'])
def route_auth_logout():
    return {
        'is_success': True,
    }




@APP.route("/auth/register", methods=['POST'])
def route_auth_register():
    return {
        'u_id': 1,
        'token': '12345',
    }


#------------------------------------------------------------------------------#
#                                  channel.py                                  #
#------------------------------------------------------------------------------#

@APP.route("/channel/invite", methods=['POST'])
def route_channel_invite():
    return {}




@APP.route("/channel/details", methods=['GET'])
def route_channel_details():
    return {
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
    }






@APP.route("/channel/messages", methods=['GET'])
def route_channel_messages():
    return {
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
    }






@APP.route("/channel/leave", methods=['POST'])
def route_channel_leave():
    return {}




@APP.route("/channel/join", methods=['POST'])
def route_channel_join():
    return {}




@APP.route("/channel/addowner", methods=['POST'])
def route_channel_addowner():
    return {}




@APP.route("/channel/removeowner", methods=['POST'])
def route_channel_removeowner():
    return {}



#------------------------------------------------------------------------------#
#                                 channels.py                                  #
#------------------------------------------------------------------------------#


@APP.route("/channels/list", methods=['GET'])
def route_channels_list():
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }






@APP.route("/channels/listall", methods=['GET'])
def route_channels_listall():
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }






@APP.route("/channels/create", methods=['POST'])
def route_channels_create():
    return {
        'channel_id': 1,
    }




#------------------------------------------------------------------------------#
#                                  message.py                                  #
#------------------------------------------------------------------------------#

@APP.route("/message/send", methods=['POST'])
def route_message_send():
    return {
        'message_id': 1,
    }





@APP.route("/message/remove", methods=['DELETE'])
def route_message_remove():
    return {}




@APP.route("/message/edit", methods=['PUT'])
def route_message_edit():
    return {}



#------------------------------------------------------------------------------#
#                                   user.py                                    #
#------------------------------------------------------------------------------#


@APP.route("/user/profile", methods=['GET'])
def route_user_profile():
    return {
        'user': {
        	'u_id': 1,
        	'email': 'cs1531@cse.unsw.edu.au',
        	'name_first': 'Hayden',
        	'name_last': 'Jacobs',
        	'handle_str': 'hjacobs',
        },
    }







@APP.route("/user/profile/setname", methods=['PUT'])
def route_user_profile_setname():
    return {}





@APP.route("/user/profile/setemail", methods=['PUT'])
def route_user_profile_setemail():
    return {}




@APP.route("/user/profile/sethandle", methods=['PUT'])
def route_user_profile_sethandle():
    return {}



#------------------------------------------------------------------------------#
#                                  other.py                                    #
#------------------------------------------------------------------------------#


@APP.route("/users/all", methods=['GET'])
def route_users_all():
    return {
        'users': [
            {
                'u_id': 1,
                'email': 'cs1531@cse.unsw.edu.au',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'hjacobs',
            },
        ],
    }






@APP.route("/admin/userpermission/change", methods=['POST'])
def route_admin_userpermission_change():
    return {}




@APP.route("/search", methods=['GET'])
def route_search():
    return {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
    }




@APP.route("/clear", methods=['DELETE'])
def route_clear():
    return {}




if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port
