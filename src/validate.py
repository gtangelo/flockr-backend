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
Returns whether or not the user is a member of a channel.

    Parameters:
        token (int): unique identifier for authorised user
        channel_data (dict): channel information

    Returns:
        (bool): whether the token is found within 'channel_data'
'''
def validate_user_in_channel(token, channel_data):
    for user in channel_data['members']:
        if user['token'] == token:
            return True
    return False

