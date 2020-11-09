# Extra Features

## 1. Object-Oriented Programming

In iteration 3, we have converted on how we interacted and store with our data. Previously, we opted to used a python dictionary to store values. Now, we store our data through a `Data` class. We used methods to interact and store data to a `Data` object and abstracted the interaction.

## 2. Persistance using Pickle

We used the pickle library to ensure our data persists after the execution of the server.

## 3. Deployment on Heroku

We successfully deployed our flockr app (both frontend and backend) using Heroku. You can access it through these link:

- Main deployed website: https://flockr-wed15mango1.herokuapp.com/
- Server: https://flockr-backend-wed15mango1.herokuapp.com/

## 4. More Reacts!

We added two more react options that a user can make for messages (thumbs down and love react).

## 5. Clear Button for Debugging

It is a button that when clicked, calls of the `/clear` request in the flask server. Only works for the first flockr owner to help us easily reset the data of the flockr app on the frontend. Mainly used to help ease of debugging/testing.
