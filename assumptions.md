# Assumptions

For our assumptions, we assume that all variables adhere to what the spec stated as their type.

## auth.py

#### Parameter Assumptions

- Limitations on `password` **128 characters**. (based on research)
- Limitations on `email` **320 characters**. (based on research)
- `email` should only contain **alpha numeric characters** and **special characters** (no emojis)
- `password` can only contain the visible ASCII values on the ascii table (characters available on keyboard)
- `email` can contain special characters (no emojis), but they cant be consecutive and cant be at the start or end of the email address (before the @). They should only appear once in the local part of the email
- `email` should contain an @ and a '.' after the @ symbol
- The same `email` cannot be registered twice.
- `emails` are not case sensitive, and are stored in lowercase form.
- `name_first` and `name_last` have a **minimum** character length of **1** and a **maximum** character length of **50** (both inclusive).
- `name_first` and `name_last` must not contain special characters or numbers other than **'-'**. Furthermore, characters can only be in the English alphabet.
- Inputted **strings** do not contain characters from other languages/cultures.
- Handle strings are concatenated from the first letter of the `name_first` and the remaining 19 letters from `name_last`

#### Implementation Assumptions

- Registering automatically logs the user in.
- Handle strings are at most **20 characters** long and atleast **3 characaters**.
- The first person to register is the **flockr owner**.
- user should be able to login if they are already logged in on another tab. **important for persistance**.
- cannot logout if not logged in

#### Password reset Assumptions

- a user can request a password reset when logged out
- a user that is not registered cannot request a password reset
- a user can request a password reset multiple times however only the most recent one is stored
- a user can recieve multiple secret codes however only the most recently recieved is valid.
- if a user is already part of the `reset_users` field in the data structure, do not add them again
- Secrets generated are unique each time a user requests.
- Password reset to the same password is valid.
- the length of the `reset_code` is **11 characters**.
- user has to manually log back in when the password is reset
- `AccessError` raised when user does not reset password and tries to login when requesting a `password_reset`.

## channel.py

- **Owners** of a channel must be members of that channel as well.

### Flockr Ownership in Channels

From our interpretation of the spec, we made the following assumptions regarding the user with **flockr ownership permissions**:

- **flockr owner** can use `channel_join` to join **private** channels
- For iteration 1, we assume that if the user with **flockr ownership permissions** joins to a channel by either using `channel_invite` or `channel_join`, the **flockr owner** immediately becomes one of the owners of the channel (treating **flockr ownership permissions** and **channel owners** as the same).
- `channel_removeowner`can be used to remove the **flockr owner** as an owner of the channel. The **flockr owner** will now instead be a member of the channel.

### channel_details

- Assuming that the return order of `owner_members` and `all_members` is when the user became a **member** or **owner**.

### channel_invite

- When a user is invited to a channel, he/she assumes **member** permissions in the channel.
- **Members** can invite other members to channel without being the owner of the channel.
- If the user is already in the channel and is invited again, an `InputError` will be presented.
- When a member invites a flockr owner to channel, the flockr owner automatically assumes the position of **owner** in the channel too

### channel_messages

- The `start` parameter is the index value of an array (i.e. If there are 10 elements in a list, `start` is valid when it is from 0 to 9 inclusively - index starts at zero).
- If `start` is equal to the total number of messages, it will raise an `InputError`. For example, if `start` is 5, however there are only 5 messages in the channel, this will raise an `InputError` since at index 5 of `start`, it is the 6th message.
- `start` can only be a positive number (including 0).
- Special Case: For the case where `start` is 0 and the total number of messages of a given channel is 0, then the returned `start` value in the dictionary will become -1 to signify that there are no messages as of yet.

### channel_leave

- If all owners have left but there are still members in the channel, the longest channel member automatically becomes the new owner of the channel.
- When everyone has left the channel, the channel will automatically be deleted from the database.
- `channel_leave` will remove user access to a channel and also that channel will never appear again when `channel_list` is called.
- When an owner leaves the channel, the owner status will be **cleared**. This means that if the user joins back to the channel using either `channel_invite` or `channel_join`, they will instead have **member permissions** initially (exemption applies to flockr owner).

### channel_join

- If an owner has left (the one who created the channel) and if they are joined back to the channel, the user will now have **member** permissions rather than **owner** permissions.
- A user that is a member of the channel can call `channel_join` as many times as they want however, for this case, it will do nothing instead.

### channel_addowner

- Any owner in the channel can add any user in flockr with the specified `u_id` as an owner of the channel. Furthermore, the user will now become a **member** of the channel.

### channel_removeowner

- If a user has been **removed** as an owner of a channel, they are still **member** of that channel.
- There must be at least one owner in the channel. If the last owner is attempted to be removed as a channel owner, it will raise an `InputError`.

## channels.py

- The user that has created a channel will automatically become the first **member** and **owner** of that channel.
- Channel `name` must be between **1 to 20 characters (inclusive)**.
- Only users that are logged in are able to list channels (Both the users are a part of and not).
- Assume that created channels are going to be listed in order channel_id (in ascending order of when it was created) when `channels_list` and `channels_listall` are called.
- `channels_listall` list all public and private channels.

## user.py

### user_profile_setname

- `name_first` and `name_last` can only contain letters from the english alphabet and can only contain the special character **'-'** and **'.'**
- two different users can have the same `name_first` and `name_last`
- `name_first` and `name_last` is updated on both the `active_users` and `users` section of data as well as the `all_members` and `owner_members` section in channels, as it would need to be updated immediately on the users screen, as well as stored in memory in the `users` section.

### user_profile_setemail

- `email` must be lowercase

### user_profile_sethandle

- `handle_str` can only contain characters available on the keyboard, cannot contain spaces **' '**
- `handle_str` is updated on both the `active_users` and `users` section of data, as it would need to be updated immediately on the users screen, as well as stored in memory in the `users` section.

### user_profile_uploadphoto

- Initially, the user's profile image url will be an empty string. i.e. `""`
- Old images that are not being served anymore will be deleted by the server.
- If user_profile_uploadphoto is called without a server running, it will raise an `AccessError` due to requiring the url from a server.
- x_end and y_end values must be greater than x_start and y_start respectively. Furthermore, x_end and y_end is inclusive within the image dimensions.

## message.py

### message_sendlater

- When the user makes the time sent as the current time, the function will just act as if it was just a message send

### message_remove & message_edit

- Flockr owner does not need to be a part of the channel to remove/edit messages but a flockr member has to be in the channel.
- Maximum length of new message is 1000 chars. Otherwise, it will throw an `InputError` if violated

### message_react and message_unreact

#### react_ids

- Each channel will have the same number of reacts.
- Message will have two reacts (thumbs up and thumbs down). Thumbs up have `react_id = 1` and thumbs down has `react_id = 2`.
- As a result from the above, only **one** react can be selected at any given time. This means that a user cannot have an active **thumbs up** and **thumbs down** shown on screen. If the user has a **thumbs up** reacted. Then, if the user tries to react to **thumbs down**, the assumption is that **thumbs up** will be unreacted automatically within the implementation and will now have **thumbs down** reacted instead.

#### Error/Scenario Assumptions

- Raises an `AccessError` when the authorised user reacts/unreacts to a message that the user is not a member of the channel. User has to be in the channel to react to a message. Exemption applies to flockr owner who does not need to be a part of the channel to react/unreact a message.
- If a user has left the channel, they cannot react/unreact to a message in that channel until the user becomes a channel member of that channel again. This will raise an `AccessError`.
- If `user` leaves the channel with messages already reacted to, the channel will still contain the information that `user` reacted to the messages. If `user` then returns back to the channel that `user` left, it will keep track which messages that `user` has reacted before `user` left the channel.

### message_pin & message_unpin

- Flockr owner does not need to be a part of the channel to pin/unpin messages
- Only owner members of channels can pin/unpin channel messages.

## other.py

### admin_userpermission_change

- The first flockr owner (the first person that register) can never become a member user. If the `u_id` of the first flockr owner is given and the `permission_id` given is a `MEMBER`, it will raise an `InputError`.
- Flockr owners can also change their own permission_id (i.e. an owner can become a member themselves).
- If a flockr owner calls admin_userpermission_change with the same `permission_id` as previous (i.e. owner becomes owner, member becomes member), the function will do nothing as they have the same `permission_id` already.

### search

- If the user has left the channel, the query will not consider that channel in its search.
- `query_str` has to be atleast `1 character long`. If the `query_str` is "", then it will raise an **InputError**.
- `search` will look for any matches that contains the `query_str` as a substring of the message.

### standup.py

### standup_start

- Whoever asks for standup_start in the given channel must be in that channel or will result in
  AccessError
- If length specified is less than or equal to 0, an InputError will be raised

### standup_active

- Whoever asks for standup_active in the given channel must be in that channel or will result in
  AccessError
