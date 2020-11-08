"""
Helper functions for validating paramters for InputError and AccessError

2020 T3 COMP1531 Major Project

"""

from src.feature.validate import (
    validate_channel_id, 
    validate_message_id, 
    validate_react_id,
    validate_u_id,
    validate_token
)
from src.classes.error import InputError, AccessError


def confirm_token(data, token):
    if not validate_token(data, token):
        raise AccessError(description="AccessError: Token is invalid")

def confirm_channel_id(data, channel_id):
    if not validate_channel_id(data, channel_id):
        raise InputError(description="InputError: Invalid channel id")

def confirm_u_id(data, u_id):
    if not validate_u_id(data, u_id):
        raise InputError(description="InputError: Invalid user id")

def confirm_message_id(data, message_id):
    if not validate_message_id(data, message_id):
        raise InputError(description="InputError: Invalid message id")

def confirm_react_id(data, message_id, react_id):
    if not validate_react_id(data, react_id, message_id):
        raise InputError(description="InputError: Invalid react id")