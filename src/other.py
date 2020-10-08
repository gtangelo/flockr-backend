"""
other feature implementation as specified by the specification

2020 T3 COMP1531 Major Project
"""

from data import data

def clear():
    """Resets the internal data of the application to it's initial state
    """
    data['active_users'] = []
    data['users'] = []
    data['channels'] = []

def users_all(token):
    """Returns a list of all users and their associated details

    Args:
        token (string)

    Returns:
        (dict): { messages }
    """
    return {
        'users': [
            {
                'u_id': 1,
                'email': 'cs1531@cse.unsw.edu.au',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'hjacobs',
            },
        ],
    }

def admin_userpermission_change(token, u_id, permission_id):
    """Given a User by their user ID, set their permissions to new permissions 
    described by permission_id

    Args:
        token (string)
        u_id (int)
        permission_id (int)
    """
    pass

def search(token, query_str):
    """Given a query string, return a collection of messages in all of the
    channels that the user has joined that match the query

    Args:
        token (string)
        query_str (string)

    Returns:
        (dict): { messages }
    """
    return {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
    }