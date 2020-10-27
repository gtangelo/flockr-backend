"""
Helper functions that can used to streamline testing.

2020 T3 COMP1531 Major Project
"""
from datetime import datetime, timezone
from src.feature.message import message_send

def create_messages(user, channel_id, i, j):
    """Sends n messages to the channel with channel_id in channel_data

    Args:
        user (dict): { u_id, token }
        channel_data (dict): { channel_id }
        i (int): start of a message string
        j (int): end of a message string

    Returns:
        (dict): { messages }
    """
    result = []
    for index in range(i, j):
        time = int(datetime.now(tz=timezone.utc).timestamp())
        message_info = message_send(user['token'], channel_id, f"{index}")
        result.insert(0, {
            'message_id': message_info['message_id'],
            'u_id': user['u_id'],
            'message': f"{index}",
            'time_created': time,
        })
    return result