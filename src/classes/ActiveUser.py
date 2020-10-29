class ActiveUser:
    def __init__(self, token, u_id):
        self.u_id = u_id
        self.token = token

    def get_details(self):
        return {
            'u_id': self.u_id,
            'token': self.token,
        }

    def get_u_id(self):
        return self.u_id

    def get_token(self):
        return self.token