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
    pass




@APP.route("/auth/logout", methods=['POST'])
def route_auth_logout():
    pass




@APP.route("/auth/register", methods=['POST'])
def route_auth_register():
    pass



#------------------------------------------------------------------------------#
#                                  channel.py                                  #
#------------------------------------------------------------------------------#

@APP.route("/channel/invite", methods=['POST'])
def route_channel_invite():
    pass




@APP.route("/channel/details", methods=['GET'])
def route_channel_details():
    pass




@APP.route("/channel/messages", methods=['GET'])
def route_channel_messages():
    pass




@APP.route("/channel/leave", methods=['POST'])
def route_channel_leave():
    pass




@APP.route("/channel/join", methods=['POST'])
def route_channel_join():
    pass




@APP.route("/channel/addowner", methods=['POST'])
def route_channel_addowner():
    pass




@APP.route("/channel/removeowner", methods=['POST'])
def route_channel_removeowner():
    pass



#------------------------------------------------------------------------------#
#                                 channels.py                                  #
#------------------------------------------------------------------------------#


@APP.route("/channels/list", methods=['GET'])
def route_channels_list():
    pass



@APP.route("/channels/listall", methods=['GET'])
def route_channels_listall():
    pass




@APP.route("/channels/create", methods=['POST'])
def route_channels_create():
    pass



#------------------------------------------------------------------------------#
#                                  message.py                                  #
#------------------------------------------------------------------------------#

@APP.route("/message/send", methods=['POST'])
def route_message_send():
    pass




@APP.route("/message/remove", methods=['DELETE'])
def route_message_remove():
    pass




@APP.route("/message/edit", methods=['PUT'])
def route_message_edit():
    pass



#------------------------------------------------------------------------------#
#                                   user.py                                    #
#------------------------------------------------------------------------------#


@APP.route("/user/profile", methods=['GET'])
def route_user_profile():
    pass





@APP.route("/user/profile/setname", methods=['PUT'])
def route_user_profile_setname():
    pass





@APP.route("/user/profile/setemail", methods=['PUT'])
def route_user_profile_setemail():
    pass




@APP.route("/user/profile/sethandle", methods=['PUT'])
def route_user_profile_sethandle():
    pass



#------------------------------------------------------------------------------#
#                                  other.py                                    #
#------------------------------------------------------------------------------#


@APP.route("/users/all", methods=['GET'])
def route_users_all():
    pass




@APP.route("/admin/userpermission/change", methods=['POST'])
def route_admin_userpermission_change():
    pass




@APP.route("/search", methods=['GET'])
def route_search():
    pass




@APP.route("/clear", methods=['DELETE'])
def route_clear():
    pass




if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port
