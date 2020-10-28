class Data:
    def __init__(self):
        self.first_owner_u_id = None
        self.total_messages = 0
        self.active_users = []
        self.reset_users = []
        self.users = []
        self.channels = []

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
        """(list of ActiveUser): list of the class ActiveUser
        """
        return self.active_users

    def get_reset_users(self):
        """(list of ResetUser): list of the class ResetUser
        """
        return self.reset_users

    def get_users(self):
        """(list of User): list of the class User
        """
        return self.users

    def get_channels(self):
        """(list of Channel): list of the class Channel
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
        return list(map(lambda channel: channel.get_channel_id(), self.channels))

    def get_user_ids(self):
        """Returns:
            (list): list of u_id
        """
        return list(map(lambda user: user.get_u_id(), self.users))
    
    def get_active_tokens(self):
        """Returns:
            (list): list of valid token
        """
        return list(map(lambda user: user.get_token(), self.active_users))
    
    def get_active_u_ids(self):
        """Returns:
            (list): list of logged in u_id
        """
        return list(map(lambda user: user.get_u_id(), self.active_users))

#?------------------------------- Object Methods -----------------------------?#
    def get_channel_object(self, channel_id):
        """Returns:
            (Channel object)
        """
        channel_details = list(filter(
            lambda channel: channel.get_channel_id() == channel_id, 
            self.channels))
        return channel_details[0]

    def get_user_object(self, u_id):
        """Returns:
            (User object)
        """
        user_details = list(filter(
            lambda user: user.get_u_id() == u_id, 
            self.users))
        return user_details[0]
    
    def get_active_user_object(self, token):
        """Returns:
            (ActiveUser object)
        """
        user_details = list(filter(
            lambda user: user.get_token() == token, 
            self.active_users))
        return user_details[0]

#?------------------------------ Details Methods -----------------------------?#
    def get_channel_details(self, channel_id):
        """Returns entire details of the channel specified by the channel_id

        Args:
            channel_id (int)

        Returns:
            (dict): { name, is_public, channel_id, all_members, owner_members, messages }
        """
        channel_details = list(filter(lambda channel: channel.get_channel_id() == channel_id, self.channels))
        print(channel_details[0].get_details())
        return channel_details[0].get_details()
    
    def get_user_details(self, u_id):
        """Returns entire details of the channel specified by the channel_id

        Args:
            channel_id (int)

        Returns:
            (dict): { name, is_public, channel_id, all_members, owner_members, messages }
        """
        user_details = list(filter(lambda user: user.get_u_id() == u_id, self.users))
        return user_details[0].get_details()

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
#------------------------------------------------------------------------------#
#                              add/remove methods                              #
#------------------------------------------------------------------------------#
#?------------------------------ Simple Methods ------------------------------?#
    def add_active_users(self, user):
        """Appends `user` to active_users

        Args:
            user (ActiveUser object)
        """
        self.active_users.append(user)

    def add_reset_users(self, user):
        """Appends `user` to reset_users

        Args:
            user (ResetUser object)
        """
        self.reset_users.append(user)

    def add_users(self, user):
        """Appends `user` to users

        Args:
            user (User object)
        """
        self.users.append(user)

    def add_channels(self, channel):
        """Appends `channel` to channels

        Args:
            user (Channel object)
        """
        self.channels.append(channel)
    
#?------------------------------ Complex Methods -----------------------------?#
    def add_member_to_channel(self, u_id, channel_id):
        """Adds u_id user to channel with channel_id as a member

        Args:
            u_id (int)
            channel_id (int)
        """
        user = self.get_user_object(u_id)
        for channel in self.channels:
            if channel.get_channel_id() == channel_id:
                name_first = user.get_name_first()
                name_last = user.get_name_last()
                profile_img_url = user.get_profile_img_url()
                channel.add_member(u_id, name_first, name_last)

    def add_owner_to_channel(self, u_id, channel_id):
        """Adds u_id user to channel with channel_id as an owner

        Args:
            u_id (int)
            channel_id (int)
        """
        user = self.get_user_object(u_id)
        for channel in self.channels:
            if channel.get_channel_id() == channel_id:
                name_first = user.get_name_first()
                name_last = user.get_name_last()
                # profile_img_url = user.get_profile_img_url()
                channel.add_owner(u_id, name_first, name_last)
    
    def add_channel_to_user_list(self, u_id, channel_id):
        """Add the channel information on the user list
        """
        channel = self.get_channel_details(channel_id)
        for user in self.users:
            if user.get_u_id() == u_id:
                user.add_channels({
                    'channel_id': channel_id,
                    'name': channel['name'],
                    'is_public': channel['is_public']
                })
    
    def add_message_to_channel(self, channel_id, message):
        """Sends a message to that particular channel
        """
        channel = self.get_channel_object(channel_id)
        channel.add_message(message)            

#------------------------------------------------------------------------------#
#                                delete methods                                #
#------------------------------------------------------------------------------#
    def remove_member_from_channel(self, u_id, channel_id):
        """Remove the member with u_id from channel with channel_id

        Args:
            u_id (int)
            channel_id (int)
        """
        for channel in self.channels:
            if channel.get_channel_id() == channel_id:
                channel.remove_member(u_id)

    def remove_owner_from_channel(self, u_id, channel_id):
        """Remove the member with u_id from channel with channel_id

        Args:
            u_id (int)
            channel_id (int)
        """
        for channel in self.channels:
            if channel.get_channel_id() == channel_id:
                channel.remove_owner(u_id)
    
    
    def delete_channel(self, channel_id):
        """Deletes the channel with channel_id in the database
        """
        channel_object = self.get_channel_object(channel_id)
        self.channels.remove(channel_object)

    def remove_channel_from_user_list(self, u_id, channel_id):
        """Removes the channel on the user list
        """
        user_details = self.get_user_object(u_id)
        channels = user_details.get_channels()
        channel = list(filter(lambda channel: channel['channel_id'] == channel_id, channels))
        user_details.remove_channels(channel[0])

    def remove_active_user(self, token):
        """Removes user on active list - logging out
        """
        user = self.get_active_user_object(token)
        self.active_users.remove(user)