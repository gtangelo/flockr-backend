class Channel:
    def __init__(self, name, is_public, channel_id):
        self.name = name
        self.is_public = is_public
        self.channel_id = channel_id
        self.all_members = []
        self.owner_members = []
        self.messages = []

    def get_details(self):
        return {
            'name': self.name,
            'is_public': self.is_public,
            'channel_id': self.channel_id,
            'all_members': self.all_members,
            'owner_members': self.owner_members,
            'messages': self.messages,
        }

    def get_name(self):
        return self.name

    def get_is_public(self):
        return self.is_public
    
    def get_channel_id(self):
        return self.channel_id
    
    def get_messages(self):
        return self.messages
    
    def get_owner_members(self):
        return self.owner_members

    def get_all_members(self):
        return self.all_members

    def add_member(self, u_id, name_first, name_last):
        self.all_members.append({
            'u_id': u_id,
            'name_first': name_first,
            'name_last': name_last,
            # 'profile_img_url': profile_img_url,
        })
    
    def add_owner(self, u_id, name_first, name_last):
        self.owner_members.append({
            'u_id': u_id,
            'name_first': name_first,
            'name_last': name_last,
            # 'profile_img_url': profile_img_url,
        })

    def remove_member(self, u_id):
        member = list(filter(lambda member: member['u_id'] == u_id, self.all_members))
        if len(member) == 1:
            self.all_members.remove(member[0])

    def remove_owner(self, u_id):
        owner = list(filter(lambda member: member['u_id'] == u_id, self.owner_members))
        if len(owner) == 1:
            self.owner_members.remove(owner[0])

    def add_message(self, message):
        self.messages.insert(0, message)
    
    def remove_message(self, message_id):
        message = list(filter(lambda message: message['message_id'] == message_id, self.messages))
        self.messages.remove(message[0])
    
    def edit_message(self, message_id, message):
        message_object = list(filter(lambda message: message['message_id'] == message_id, self.messages))
        message_object[0]['message'] = message

