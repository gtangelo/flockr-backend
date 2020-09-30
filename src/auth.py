"""
This feature covers the basic process of creating and managing users.
"""

data = {
    'users': []
}

def auth_login(email, password):
    for user in data['users']:
        if user['email'] == email:
            if user['password'] == password:
                user['online'] = True
                return True
    return False

def auth_logout(token):
    for user in data['users']:
        if user['token'] == token:
            user['online'] == False
            return True
    return False

def auth_register(email, password, name_first, name_last):
    for user in data['users']:
        if user['email'] == email:
            return False
    
    newUser = {
        'email': email,
        'password': password,
        'first_name': name_first,
        'last_name': name_last,
        'u_id': len(data['users']) + 1,
        'token': email,
        'online': False
    }
    data['users'].append(newUser)
    return True
