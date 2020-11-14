# Extra Features

For the extra features, we mainly focused on some features that the specification stated such as:

- deployment
- OOP principles
- persistance

## 1. Object-Oriented Programming

In iteration 3, we have converted on how we interacted and store with our data. Previously, we opted to used a python dictionary to store values. Now, we store our data through a `Data` class. We used methods to interact and store data to a `Data` object and abstracted the interaction.

The reason for using a `Data` object rather than a `User` or `Channel` class was that it allows us to use methods that can interact with the entire `Data` object and better abstract our manipulation of the `Data` object.

## 2. Persistance using Pickle

We used the pickle library to ensure our data persists after the execution of the server.

## 3. Deployment on Heroku

We successfully deployed our flockr app (both frontend and backend) using Heroku. You can access it through these link:

- Main deployed website (frontend): https://flockr-wed15mango1.herokuapp.com/
- Server (backend): https://flockr-backend-wed15mango1.herokuapp.com/

## 4. More Reacts!

We added two more react options that a user can make for messages (thumbs down and love react).

## 5. Clear and Data Button for Debugging

Extra buttons used for debugging purposes. `Clear` button forces data to be reset whilst `Data` button returns the content of the `data` object. Only the first flockr owner has access to these buttons.
