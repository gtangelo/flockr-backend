import hashlib
from src.feature.globals import MEMBER
 

class User:
    def __init__(self, email, password, name_first, name_last, u_id, hstring):
        self.u_id = u_id
        self.email = email
        self.password = hashlib.sha256(password.encode()).hexdigest()
        self.name_first = name_first
        self.name_last = name_last
        self.handle_str = hstring
        self.channels = []
        self.permission_id = MEMBER
        self.profile_img_url = ""

    def get_details(self):
        return {
            'u_id': self.u_id,
            'email': self.email,
            'password': self.password,
            'name_first': self.name_first,
            'name_last': self.name_last,
            'handle_str': self.handle_str,
            'channels': self.channels,
            'permission_id': self.permission_id,
            'profile_img_url': self.profile_img_url,
        }

    def get_u_id(self):
        return self.u_id

    def get_email(self):
        return self.email

    def get_password(self):
        return self.password

    def get_name_first(self):
        return self.name_first

    def get_name_last(self):
        return self.name_last

    def get_channels(self):
        return self.channels

    def get_handle_str(self):
        return self.handle_str
    
    def get_permission_id(self):
        return self.permission_id

    def get_profile_img_url(self):
        return self.profile_img_url

    def set_permission_id(self, permission_id):
        self.permission_id = permission_id

    def add_channels(self, channel):
        self.channels.append(channel)
    
    def remove_channels(self, channel):
        self.channels.remove(channel)

    def setname(self, name_first, name_last):
        self.name_first = name_first
        self.name_last = name_last
    
    def setemail(self, email):
        self.email = email
    
    def sethandle(self, handle):
        self.handle_str = handle
