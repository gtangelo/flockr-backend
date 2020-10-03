# Provides a list of all the channels that the user is in.
'''
This feature implements the ability to list and create channels.

'''

from data import data
from error import InputError, AccessError
from validate import user_is_authorise, validate_user_in_channel, convert_token_to_user

# Provides a list of all channels that the user is a part of.
def channels_list(token):
    
    # Reject for a false token.
    if type(token) != str:
        raise InputError("User token is not type string")

    # Authorised user check.
    authorised_to_list = user_is_authorise(token)
    if not authorised_to_list:
        raise AccessError("User cannot list channels, log in first.")

    # Get user ID from token.
    user_details = convert_token_to_user(token)
    u_id = user_details['u_id']
    
    # Add channels the user is a part of into joined_channels.
    joined_channels = {}
    joined_channels['channels'] = []

    for curr_channel in data['channels']:
        for member in curr_channel['all_members']:
            if member['u_id'] == u_id:
                channel_id_name = {
                    'channel_id': curr_channel['channel_id'],
                    'name': curr_channel['name']
                }
                joined_channels['channels'].append(channel_id_name)

    return joined_channels

    '''
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }
    '''

# Provides a list of all available channels (and their associated details) 
def channels_listall(token):

    # Reject for a false token.
    if type(token) != str:
        raise InputError("User token is not type string")

    # Authorised user check
    authorised_to_list = user_is_authorise(token)
    if not authorised_to_list:
        raise AccessError("User cannot list channels, log in first.")

    # Add all available channels into all_channels (both public and private).
    all_channels = {}
    all_channels['channels'] = []

    for curr_channel in data['channels']:
        channel_id_name = {
            'channel_id': curr_channel['channel_id'],
            'name': curr_channel['name']
        }
        all_channels['channels'].append(channel_id_name)

    return all_channels

    '''
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }
    '''

# Creates a new channel with that name that is either public (True) or private (False)
def channels_create(token, name, is_public):
    
    # Reject for false data types.
    if type(token) != str:
        raise InputError("User token is not type string")
    elif type(name) != str:
        raise InputError("Channel name is not type string")
    elif type(is_public) != bool:
        raise InputError("Channel status is not type bool")

    # Raise InputError if the channel name is invalid. 
    if len(name) > 20 or len(name) < 1:
        raise InputError("Channel name is invalid, please enter a name between 1-20 characters.")
    
    # Create new channel and populate its keys.
    channel_id = len(data['channels']) + 1
    channel_details = {}

    channel_details['channel_id'] = channel_id
    channel_details['name'] = name
    channel_details['is_public'] = is_public
    channel_details['all_members'] = []
    channel_details['owner_members'] = []
    channel_details['messages'] = []

    # Obtain u_id from token and then add the user into the channel member lists.
    user_details = {}
    creator = convert_token_to_user(token)
    user_details['u_id'] = creator['u_id']
    user_details['name_first'] = creator['name_first']
    user_details['name_last'] = creator['name_last']

    # Add user to created channel as well as making them owner.
    channel_details['all_members'].append(user_details)
    channel_details['owner_members'].append(user_details)

    # Store channel_details into data.py user channels as well as channels.
    data['channels'].append(channel_details)
    
    for user in data['users']:
        if user['u_id'] == u_id:
            user['channels'].append(channel_details)

    return {
        'channel_id': channel_id,
    }
