# Assumptions
## auth.py

The same email cannot be registered twice.
Limitations on password 128 characters. (based on research)
Limitations on email 320 characters. (based on research)
Email, passwords, should only contain alpha numeric characters and special characters (no emojis)
names should not contain special characters or numbers other than '-'
Registering automatically logs the user in.
Emails can contain special characters (non emojis), but they cant be consecutive and cant be at
the start or end of the email address (before the @).
The local part of the email should be atleast 3 characters long (before the @).
Names have a minimum character length of 1 and a maximum character length of 50 (inclusive).
Inputted names are only in English alphabet.
Inputted strings do not contain characters from other languages/cultures.
Handle strings are 20 characters long.
The first person to register is the owner of the flock.


## channel.py

Gabriel Ting

## channels.py
- Newly created channel automatically adds the user who created it and sets them as owner.
- Channel name length has to be between 1-20 characters inclusive. 
- Only logged in users are able to create channels. 
- Only users that are logged in are able to list channels (Both the users are a part of and not).
- Can't assume that created channels are going to be listed in order of creation.
- Can list both private and public channels.

## user.py



## message.py



## other.py


