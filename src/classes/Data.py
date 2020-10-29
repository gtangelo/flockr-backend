from datetime import datetime, timezone
import hashlib
from src.feature.globals import MEMBER

class Data:
    def __init__(self):
        self.first_owner_u_id = None
        self.total_messages = 0
        self.active_users = []
        self.reset_users = []
        self.users = []
        self.channels = []
    
    def __str__(self):
        return str(self.__dict__)

    # User structure
    def create_user(self, email, password, name_first, name_last, u_id, hstring):
        user = {
            'email': email,
            'name_first': name_first,
            'name_last': name_last,
            'u_id': u_id,
            'handle_str': hstring,
            'password': hashlib.sha256(password.encode()).hexdigest(),
            'channels': [],
            'permission_id': MEMBER,
            'profile_img_url': ""
        }
        self.users.append(user)
    
    def get_user_details(self, u_id):
        """Returns entire details of the channel specified by the channel_id

        Args:
            channel_id (int)

        Returns:
            (dict): { name, is_public, channel_id, all_members, owner_members, messages }
        """
        user_details = list(filter(lambda user: user['u_id'] == u_id, self.users))
        return user_details[0]
    
    def set_user_permission_id(self, u_id, permission_id):
        user_details = list(filter(lambda user: user['u_id'] == u_id, self.users))
        user_details[0]['permission_id'] = permission_id

    def add_channels_to_user(self, u_id, channel_id):
        user_details = list(filter(lambda user: user['u_id'] == u_id, self.users))
        user_details[0]['channels'].append(channel_id)
    
    def remove_channels(self, u_id, channel_id):
        user_details = list(filter(lambda user: user['u_id'] == u_id, self.users))
        user_details[0]['channels'].append(channel_id)

    def setname(self, u_id, name_first, name_last):
        user_details = list(filter(lambda user: user['u_id'] == u_id, self.users))
        user_details[0]['name_first'] = name_first
        user_details[0]['name_last'] = name_last
    
    def setemail(self, u_id, email):
        user_details = list(filter(lambda user: user['u_id'] == u_id, self.users))
        user_details[0]['email'] = email
    
    def sethandle(self, u_id, handle):
        user_details = list(filter(lambda user: user['u_id'] == u_id, self.users))
        user_details[0]['handle_str'] = handle
    
    # Active users
    def create_active_user(self, u_id, token):
        user = {
            'u_id': u_id,
            'token': token,
        }
        self.active_users.append(user)

    def get_active_user_details(self, token):
        user_details = list(filter(lambda user: user['token'] == token, self.active_users))
        return user_details[0]
    
    # Channel
    def create_channel(self, name, is_public, channel_id):
        channel = {
            'name': name,
            'is_public': is_public,
            'channel_id': channel_id,
            'all_members': [],
            'owner_members': [],
            'messages': [],
        }
        self.channels.append(channel)
    
    def get_channel_details(self, channel_id):
        """Returns entire details of the channel specified by the channel_id

        Args:
            channel_id (int)

        Returns:
            (dict): { name, is_public, channel_id, all_members, owner_members, messages }
        """
        channel_details = list(filter(lambda channel: channel['channel_id'] == channel_id, self.channels))
        return channel_details[0]

    def add_member_to_channel(self, u_id, channel_id):
        """Adds u_id user to channel with channel_id as a member

        Args:
            u_id (int)
            channel_id (int)
        """
        user = self.get_user_details(u_id)
        for channel in self.channels:
            if channel['channel_id'] == channel_id:
                name_first = user['name_first']
                name_last = user['name_last']
                # profile_img_url = user.get_profile_img_url()
                channel['all_members'].append({
                    'u_id': u_id,
                    'name_first': name_first, 
                    'name_last': name_last
                })

    def add_owner_to_channel(self, u_id, channel_id):
        """Adds u_id user to channel with channel_id as an owner

        Args:
            u_id (int)
            channel_id (int)
        """
        user = self.get_user_details(u_id)
        for channel in self.channels:
            if channel['channel_id'] == channel_id:
                name_first = user['name_first']
                name_last = user['name_last']
                # profile_img_url = user.get_profile_img_url()
                channel['owner_members'].append({
                    'u_id': u_id,
                    'name_first': name_first, 
                    'name_last': name_last
                })
    
    def add_channel_to_user_list(self, u_id, channel_id):
        """Add the channel information on the user list
        """
        channel = self.get_channel_details(channel_id)
        for user in self.users:
            if user['u_id'] == u_id:
                user['channels'].append({
                    'channel_id': channel_id,
                    'name': channel['name'],
                    'is_public': channel['is_public']
                })
    
    def create_message(self, u_id, channel_id, message_id, message):
        """Sends a message to that particular channel
        """
        channel = self.get_channel_details(channel_id)
        channel['messages'].insert(0, {
            'message_id': message_id,
            'u_id': u_id,
            'message': message,
            'time_created': int(datetime.now(tz=timezone.utc).timestamp()),
            'reacts': []
        })
          
    def remove_message(self, channel_id, message_id):
        channel = self.get_channel_details(channel_id)
        message = list(filter(lambda message: message['message_id'] == message_id, channel['messages']))
        channel['messages'].remove(message[0])
    
    def edit_message(self, channel_id, message_id, message):
        channel = self.get_channel_details(channel_id)
        message_details = list(filter(lambda message: message['message_id'] == message_id, channel['messages']))
        message_details[0]['message'] = message

    def remove_member_from_channel(self, u_id, channel_id):
        """Remove the member with u_id from channel with channel_id

        Args:
            u_id (int)
            channel_id (int)
        """
        channel = self.get_channel_details(channel_id)
        for user in channel['all_members']:
            if user['u_id'] == u_id:
                channel['all_members'].remove(user)

    def remove_owner_from_channel(self, u_id, channel_id):
        """Remove the member with u_id from channel with channel_id

        Args:
            u_id (int)
            channel_id (int)
        """
        channel = self.get_channel_details(channel_id)
        for user in channel['owner_members']:
            if user['u_id'] == u_id:
                channel['owner_members'].remove(user)
    
    
    def delete_channel(self, channel_id):
        """Deletes the channel with channel_id in the database
        """
        channel = self.get_channel_details(channel_id)
        self.channels.remove(channel)

    def remove_channel_from_user_list(self, u_id, channel_id):
        """Removes the channel on the user list
        """
        user_details = self.get_user_details(u_id)
        channels = user_details['channels']
        channel = list(filter(lambda channel: channel['channel_id'] == channel_id, channels))
        user_details['channels'].remove(channel[0])

    def remove_active_user(self, token):
        """Removes user on active list - logging out
        """
        user = self.get_active_user_details(token)
        self.active_users.remove(user)

#------------------------------------------------------------------------------#
#                                 clear methods                                #
#------------------------------------------------------------------------------#
    def clear_first_owner_u_id(self):
        """(int): first_owner_u_id
        """
        self.first_owner_u_id = None
    
    def clear_total_messages(self):
        """Clear total_messages
        """
        self.total_messages = 0
    
    def clear_active_users(self):
        """Clear active_users
        """
        self.active_users = []

    def clear_reset_users(self):
        """Clear reset_users
        """
        self.reset_users = []

    def clear_users(self):
        """Clear users
        """
        self.users = []

    def clear_channels(self):
        """Clear channels
        """
        self.channels = []

#------------------------------------------------------------------------------#
#                                  get methods                                 #
#------------------------------------------------------------------------------#
#?------------------------------ Simple Methods ------------------------------?#

    def get_active_users(self):
        """(list of dicts): { u_id, token }
        """
        return self.active_users

    def get_reset_users(self):
        """(list of dicts): { u_id, token }
        """
        return self.reset_users

    def get_users(self):
        """(list of dicts): { u_id, email, password, name_first, name_last, 
        handle_str, password, channels [channel_ids], permission_id, profile_img_url }
        """
        return self.users

    def get_channels(self): 
        """(list of dicts): {name, is_public, channel_id, all_members, owner_members, messages }
        """
        return self.channels

    def get_first_owner_u_id(self):
        """(int): first_owner_u_id
        """
        return self.first_owner_u_id
    
    def get_total_messages(self):
        """(int): total_messages
        """
        return self.total_messages
    
#?-------------------------------- List Methods ------------------------------?#
    def get_channel_ids(self):
        """Returns:
            (list): list of channel_id
        """
        return list(map(lambda channel: channel['channel_id'], self.channels))

    def get_user_ids(self):
        """Returns:
            (list): list of u_id
        """
        return list(map(lambda user: user['u_id'], self.users))
    
    def get_active_tokens(self):
        """Returns:
            (list): list of valid token
        """
        return list(map(lambda user: user['token'], self.active_users))
    
    def get_active_u_ids(self):
        """Returns:
            (list): list of logged in u_id
        """
        return list(map(lambda user: user['u_id'], self.active_users))

#------------------------------------------------------------------------------#
#                                 set methods                                  #
#------------------------------------------------------------------------------#
    def set_first_owner_u_id(self, u_id):
        """Set first_owner_u_id to the u_id given
        """
        self.first_owner_u_id = u_id
    
    def generate_message_id(self):
        """Generates a unique message_id
        """
        self.total_messages += 1
        return self.total_messages
