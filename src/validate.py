from data import data

'''
Returns whether or not channel_id is a valid channel id.

    Parameters:
        channel_id (int): channel id

    Returns:
        (bool, dict): whether channel_id is a valid channel id in the data. 
            - If valid, returns True and 'channel_data' which stores all relevant
            information in a dictionary belonging to the channel with the 
            'channel_id'
            - Otherwise, returns False
'''
def validate_channel_id(channel_id):
    for channel in data['channels']:
        if channel_id == channel['id']:
            channel_data = channel
            return True, channel_data
    return False

'''
Determines whether or not the user has been authorised.

    Parameters:
        token (int): unique identifier for authorised user

    Returns:
        (bool): whether the token is valid
'''
def user_is_authorise(token):
    for user in data['active_users']:
        if user['token'] == token:
            return True
    return False

'''
Returns the user details based on the given token

    Parameters:
        token (int): unique identifier for authorised user

    Returns:
        (dict): dictionary containing user details
'''
def convert_token_to_user(token):
    user_details = {}
    for user in data['active_users']:
        if user['token'] == token:
            user_details = user
            break
    return user_details

'''
Returns whether or not the user is a member of a channel.

    Parameters:
        token (int): unique identifier for authorised user
        channel_data (dict): channel information

    Returns:
        (bool): whether the token is found within 'channel_data'
'''
def validate_user_in_channel(token, channel_data):
    if user_is_authorise(token):
        user_details = convert_token_to_user(token)
        for user in channel_data['members']:
            if user['id'] == user_details['id']:
                return True
    return False
