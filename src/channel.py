from error import InputError, AccessError
from validate import validate_channel_id, validate_user_in_channel
from data import data

def channel_invite(token, channel_id, u_id):
    return {
    }

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
    is_valid_id, channel_data = validate_channel_id(channel_id)

    # InputError Checks
    if not is_valid_id:
        raise InputError("Channel ID is not a valid channel")

    # AccessError Checks
    can_access = validate_user_in_channel(token, channel_data)
    if not can_access:
        raise AccessError("Authorised user is not a member of channel with channel_id")
    
    # Add the person to the channel
    channel_data['members'].append(token)
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

    # Add the person as owner to channel
    return {}

def channel_removeowner(token, channel_id, u_id):
    return {
    }