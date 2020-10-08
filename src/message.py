"""
message feature implementation as specified by the specification

Feature implementation was written by Tam Do and Prathamesh Jagtap.

2020 T3 COMP1531 Major Project
"""

def message_send(token, channel_id, message):
    """Send a message from authorised_user to the channel specified by channel_id

    Args:
        token (string)
        channel_id (int)
        message (string)

    Returns:
        (dict): { message_id }
    """
    return {
        'message_id': 1,
    }

def message_remove(token, message_id):
    """Given a message_id for a message, this message is removed from the channel

    Args:
        token (string)
        message_id (int)

    Returns:
        (dict): {}
    """
    return {
    }

def message_edit(token, message_id, message):
    """Given a message, update it's text with new text. If the new message is an
    empty string, the message is deleted.

    Args:
        token (string)
        message_id (int)
        message (string)

    Returns:
        (dict): {}
    """
    return {
    }