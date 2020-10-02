# Assumptions
## auth.py



## channel.py



### channel_messages
- If no messages have been made in a channel, both the `start` and `end` value will be -1.
- The `start` parameter will always be positive (including 0).


### channel_leave
- If all owners have left but there are still members in the channel, the user with the lowest u_id automatically becomes the new owner of the channel.
- When everyone has left the channel, the channel will automatically be deleted from the database.
- `channel_leave` will remove user access to a channel and also that channel will never appear again when `channel_list` is called.

### channel_join
- Test for private (error)
- Test for flockr owner (flockr owner can join private channels)
- Test for a person joining again
- Flockr owner becomes owner after channel join

### channel_addowner
- Can add anyone from flockr with u_id (doesn't matter if they are not a member of the channel)
- Owners are also added as members

### channel_removeowner
- If person is removed as owner, they are still member of the channel
- If owner channel_leaves and channel_removeowner, then it should raise an error
- If remove owner removes flockr owner, then flockr owner should be member 
- `channel_leave` will remove user access to that specific channel and also it will never appear again when `channel_list` is called.
- When an owner leaves the channel, the owner status will be cleared. This means that if the user joins back to the channel using either `channel_invite` or `channel_join`, they will instead have member permissions only.

## channels.py
- Newly created channel automatically adds the user who created it and sets them as owner.
- Channel name length has to be between 0-20 characters inclusive. 
- The user is logged in first to create channels. 
- Only users that are logged in are able to list channels (Both the users are a part of and not).
- Can't assume that created channels are going to be listed in order of creation.
- Can list both private and public channels.

## user.py



## message.py



## other.py


