from error import InputError, AccessError
from validate import user_is_authorise, validate_channel_id, validate_user_in_channel, convert_token_to_user
from data import data

def channel_invite(token, channel_id, u_id):
    invited_user_found = False
    authorized_to_invite = False
    user_already_in_channel = False

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

    # (Assumption test)
    # raise AccessError if inviting him/herself
    user_details = convert_token_to_user(token)
    if user_details['u_id'] == u_id:
        raise AccessError("User not allowed to invite him/herself")
    
    # raise an AccessError if same user is invited more than once (add tests)
    for channels in data['channels']:
        if channels['channel_id'] == channel_id:
            for members in channels['all_members']:
                if members['u_id'] == u_id:
                    user_already_in_channel = True

    if user_already_in_channel == True:
        raise AccessError("User is already part of the channel")

    # TODO: if user is flockr owner: make him the group owner too (add tests)
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

                            return {}

                    # raise InputError if u_id is invalid
                    if not invited_user_found:
                        raise InputError("Invited user not found")
    
    # raise AccessError if not authorized to invite
    if not authorized_to_invite:
        raise AccessError("User is not authorized to invite members to channel")

def channel_details(token, channel_id):
    authorized_for_details = False

    # reject immediately if found false data type
    if type(token) != str:
        raise InputError("User token is not type string")
    elif type(channel_id) != int:
        raise InputError("Channel ID is not type int")

    # raises AccessError if token is invalid
    user_authorized = user_is_authorise(token)
    if not user_authorized:
        raise AccessError("Token is invalid, please register/login")

    # raise InputError if channel_id is invalid
    channel_valid = validate_channel_id(channel_id)
    if not channel_valid:
        raise InputError("Channel ID is not a valid channel")

    # check whether user is authorized to see channel details
    user_details = convert_token_to_user(token)
    for channels in data['channels']:
        if channels['channel_id'] == channel_id:
            for members in channels['all_members']:
                if members['u_id'] == user_details['u_id']:
                    authorized_for_details = True

                    channel_info = {
                        'name'         : channels['name'],
                        'owner_members': channels['owner_members'],
                        'all_members'  : channels['all_members'],
                    }
                    
                    return channel_info

    # raise AccessError if not authorized to see details
    if not authorized_for_details:
        raise AccessError("User is not authorized to see channel details")

    '''
    required style
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
    '''

def channel_messages(token, channel_id, start):
    is_valid_id, channel_data = validate_channel_id(channel_id)

    if not is_valid_id:
        raise InputError("Channel ID is not a valid channel")
    if start > len(channel_data['messages']):
        raise InputError("start is greater than the total number of messages in the channel")
    if not user_is_authorise(token):
        raise AccessError("Token is not valid")
    if not validate_user_in_channel(token, channel_data):
        raise AccessError("Authorised user is not a member of channel with channel_id")
    
    # Case where there are no messages in the channel
    if len(channel_data['messages']) == 0:
        return {
            'messages': [],
            'start': -1,
            'end': -1,
        }
    
    # Case where there are messages in the channel
    end = start + 50
    if end > len(channel_data['messages']):
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
    if not is_valid_id:
        raise InputError("Channel ID is not a valid channel")
    if not user_is_authorise(token):
        raise AccessError("Token is not valid")
    if not validate_user_in_channel(token, channel_data):
        raise AccessError("Authorised user is not a member of channel with channel_id")
    
    
    user_details = convert_token_to_user(token)
    channel_index = data['channels'].index(channel_data)

    # Remove user as member
    for user in channel_data['all_members']:
        if user['u_id'] == user_details['u_id']:
            channel_data['all_members'].remove(user)
            break
    # Remove user as owner
    for user in channel_data['owner_members']:
        if user['u_id'] == user_details['u_id']:
            channel_data['owner_members'].remove(user)
            break

    data['channels'][channel_index] = channel_data

    # Remove channel from user list
    for user_index, user in enumerate(data['users']):
        if user['u_id'] == user_details['u_id']:
            for channel_index, curr_channel in enumerate(user['channels']):
                if curr_channel['channel_id'] == channel_id:
                    data['users'][user_index]['channels'].remove(curr_channel)                

    # Case where all owners have left, assign a user with the lowest u_id as
    # new owner
    if len(channel_data['owner_members']) == 0 and len(channel_data['all_members']) != 0:
        lowest_u_id_user = channel_data['all_members'][0]
        for user in channel_data['all_members']:
            if lowest_u_id_user['u_id'] > user['u_id']:
                lowest_u_id_user = user
        channel_data['owner_members'].append(lowest_u_id_user)

    # Case where all members have left, delete channel from database
    if len(channel_data['all_members']) == 0:
        data['channels'].pop(channel_index)
        
    return {}

def channel_join(token, channel_id):

    # Checking if person is already part of channel

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

    # Add the person to the channel
    user_details = convert_token_to_user(token)
    channel_data['members'].append(user_details)
    data['channels'][channel_index] = channel_data['members']
    return {}

def channel_addowner(token, channel_id, u_id):
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

    # Add the person as owner to channel
    user_details = convert_token_to_user(token)
    channel_data['members'].append(user_details)
    channel_data['owner_members'].append(user_details)
    data['channels'][channel_index] = channel_data['members']
    data['channels'][channel_index] = channel_data['owner_members']
    return {}

def channel_removeowner(token, channel_id, u_id):
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

    # Remove the person as owner to channel
    # Find the index where the user data is being stored within channel_data['members']
    i = 0
    for user in channel_data['members']:
        if user['token'] == token:
            break
        i += 1
    channel_data['owner_members'].pop(i)
    data['channels'][channel_index] = channel_data['owner_members']
    return {}