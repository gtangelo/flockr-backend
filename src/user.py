"""
user feature implementation as specified by the specification

Feature implementation was written by Christian Ilagan and Richard Quisumbing.

2020 T3 COMP1531 Major Project
"""
from data import data
import validate
import action
from error import AccessError, InputError
def user_profile(token, u_id):
    """For a valid user, returns information about their user_id, email, first
    name, last name, and handle

    Args:
        token (string)
        u_id (int)

    Returns:
        (dict): { user }
    """
    return {
        'user': {
        	'u_id': 1,
        	'email': 'cs1531@cse.unsw.edu.au',
        	'name_first': 'Hayden',
        	'name_last': 'Jacobs',
        	'handle_str': 'hjacobs',
        },
    }

def user_profile_setname(token, name_first, name_last):
    """Update the authorised user's first and last name

    Args:
        token (string)
        name_first (string)
        name_last (string)

    Returns:
        (dict): {}
    """
    return {
    }

def user_profile_setemail(token, email):
    return {
    }

def user_profile_sethandle(token, handle_str):
    return {
    }