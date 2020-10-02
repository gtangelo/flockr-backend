from error import InputError, AccessError
from validate import user_is_authorise, validate_channel_id, validate_user_in_channel, convert_token_to_user
from data import data

def channel_invite(token, channel_id, u_id):
    invited_user_found = False
    authorized_to_invite = False

    # reject immediately if found false data type
    if type(token) != str:
        raise InputError("User token is not type string")
    elif type(channel_id) != int:
        raise InputError("Channel ID is not type int")
    elif type(u_id) != int:
        raise InputError("User ID is not type int")

    # raises AccessError if token is invalid
    user_authorized = user_is_authorise(token)
    if not user_authorized:
        raise AccessError("Token is invalid, please register/login")

    # raise InputError if channel_id is invalid
    channel_valid = validate_channel_id(channel_id)
    if not channel_valid:
        raise InputError("Channel ID is not a valid channel")

    # raise AccessError if inviting him/herself
    user_details = convert_token_to_user(token)
    if user_details['u_id'] == u_id:
        raise AccessError("User not allowed to invite him/herself")

    # check if inviter is authorized to invite by being a member of channel
    for channels in data['channels']:
        if channels['channel_id'] == channel_id:
            for members in channels['all_members']:
                if members['u_id'] == user_details['u_id']:
                    authorized_to_invite = True

                    for users in data['users']:
                        if users['u_id'] == u_id:
                            invited_user_found = True

                            # add user info to channel database
                            invited_user = {
                                'u_id'      : u_id,
                                'name_first': users['name_first'],
                                'name_last' : users['name_last'],
                            }
                            channels['all_members'].append(invited_user)

                            # add channel info to user database
                            channel_info = {
                                'channel_id': channel_id,
                                'name'      : channels['name'],
                            }
                            users['channels'].append(channel_info)

                    # raise InputError if u_id is invalid
                    if not invited_user_found:
                        raise InputError("Invited user not found")
    
    # raise AccessError if not authorized to invite
    if not authorized_to_invite:
        raise AccessError("User is not authorized to invite members to channel")

def channel_details(token, channel_id):
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

def channel_messages(token, channel_id, start):
    is_valid_id, channel_data = validate_channel_id(channel_id)

    # InputError Checks
    if not is_valid_id:
        raise InputError("Channel ID is not a valid channel")
    if start > channel_data['total_messages']:
        raise InputError("start is greater than the total number of messages in the channel")

    # AccessError Checks
    can_access = validate_user_in_channel(token, channel_data)
    if not can_access:
        raise AccessError("Authorised user is not a member of channel with channel_id")
    
    # Case where there are no messages in the channel
    if channel_data['total_messages'] == 0:
        return {
            'messages': [],
            'start': -1,
            'end': -1,
        }
    
    # Case where there are messages in the channel
    end = start + 50
    if end > channel_data['total_messages']:
        end = -1

    message_list = []
    for message in channel_data['messages']:
        message_list.append(message)
    
    if end == -1:
        return {
            'messages': message_list[start:],
            'start': start,
            'end': end
        }
    else:
        return {
            'messages': message_list[start:end],
            'start': start,
            'end': end
        }

def channel_leave(token, channel_id):
    is_valid_id, channel_data = validate_channel_id(channel_id)

    # InputError Checks
    if not is_valid_id:
        raise InputError("Channel ID is not a valid channel")

    # AccessError Checks
    can_access = validate_user_in_channel(token, channel_data)
    if not can_access:
        raise AccessError("Authorised user is not a member of channel with channel_id")
    
    # Find the index of where the channel is being stored
    channel_index = 0
    for channel in data['channels']:
        if channel['id'] == channel_id:
            break
        channel_index += 1
    # Find the index where the user data is being stored within channel_data['members']
    i = 0
    for user in channel_data['members']:
        if user['token'] == token:
            break
        i += 1
    channel_data['members'].pop(i)
    data['channels'][channel_index] = channel_data['members']
    return {}

def channel_join(token, channel_id):
    return {
    }

def channel_addowner(token, channel_id, u_id):
    return {
    }

def channel_removeowner(token, channel_id, u_id):
    return {
    }