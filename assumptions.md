# Assumptions
## auth.py



## channel.py



### channel_messages
- If no messages have been made in a channel, both the `start` and `end` value will be -1.


### channel_leave
- If all owners have left but there are still members in the channel, the user with the lowest u_id automatically becomes the new owner of the channel.
- When everyone has left the channel, the channel will automatically be deleted from the database.
- `channel_leave` will remove user access to a channel and also that channel will never appear again when `channel_list` is called.


## channels.py



## user.py



## message.py



## other.py


