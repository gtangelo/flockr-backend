"""
standup feature implementation as specified by the specification

2020 T3 COMP1531 Major Project
"""

def standup_start(token, channel_id, length):
    """For a given channel, start the standup period whereby for the next 
    "length" seconds if someone calls "standup_send" with a message, it is 
    buffered during the X second window then at the end of the X second window 
    a message will be added to the message queue in the channel from the user 
    who started the standup. X is an integer that denotes the number of seconds 
    that the standup occurs for

    Args:
        token (string)
        channel_id (int)
        length (int)

    Returns:
        (dict): { time_finish }
    """
    return {
        "time_finish": 1000000000,
    }

def standup_active(token, channel_id):
    """For a given channel, return whether a standup is active in it, and what
    time the standup finishes. If no standup is active, then time_finish
    returns None

    Args:
        token (string)
        channel_id (int)

    Returns:
        (dict): { is_active, time_finish }
    """
    return {
        "is_active": True,
        "time_finish": 1000000000,
    }

def standup_send(token, channel_id, message):
    """Sending a message to get buffered in the standup queue, assuming a
    standup is currently active

    Args:
        token (string)
        channel_id (int)
        message (string)

    Returns:
        (dict): {}
    """
    return {}