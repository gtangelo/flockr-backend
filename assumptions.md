# Assumptions
## auth.py

## register
The same email cannot be registered twice.
Limitations on password 128 characters. (based on research)
Limitations on email 320 characters. (based on research)
Email, passwords, should only contain alpha numeric characters and special characters (no emojis)
names should not contain special characters or numbers other than '-'
Registering automatically logs the user in.
Emails can contain special characters (non emojis), but they cant be consecutive and cant be at
the start or end of the email address (before the @).
The email should contain a domain with a '.'
Names have a minimum character length of 1 and a maximum character length of 50 (inclusive).
Inputted names are only in English alphabet.
Inputted strings do not contain characters from other languages/cultures.
Handle strings are 20 characters long.
The first person to register is the owner of the flock.
The only characters being inputted in the auth file exist only on the keyboard.
Email domains can have multiple dots, e.g. company emails, or .uk emails
Emails are not case sensitive, and are stored in lowercase form.
Passwords can only contain the visibile ASCII values on the ascii table (characters available on keyboard)
## login
The user should not be able to log in when they already logged in.
Passwords can only contain the visibile ASCII values on the ascii table (characters available on keyboard)
cannot login if not registered.

## logout
cannot logout if not logged in.
Tokens exist only in the active users section.



## channel.py



## channels.py



## user.py



## message.py



## other.py


