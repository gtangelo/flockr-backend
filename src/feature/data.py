"""
Global variable as a data structure for our backend

2020 T3 COMP1531 Major Project
"""

#==============================================================================#
# This file is now redundant due to using classes and pickle to persist data.  #
# However, the following below provides what the data strcutrue looks like in  #
# the Data class.                                                              #
#==============================================================================#

# from src.classes.Data import Data
# from src.globals import OWNER, MEMBER

# data = Data()

# # ! The following below should be how our data structure should look like in the 
# # ! data object.
# # TODO: How would we handle timed messages?
# data = {
#     'first_owner_u_id': None,
#     'total_messages': 0,
#     # TODO: Added reset_users for auth/request/reset
#     'reset_users': [
#         {
#             'secret': "0000000",
#             'u_id': 1,
#             'email': email,
#         }
#     ],
#     'active_users': [
#         {
#             'token': '12345',
#             'u_id': 1,
#         },
#     ],
#     'users': [
#         {
#             'u_id': 1,
#             'email': 'cs1531@cse.unsw.edu.au',
#             'password': 'abc1234',
#             'name_first': 'Hayden',
#             'name_last': 'Jacobs',
#             'handle_str': 'hjacobs',
#             'channels': [
#                 {
#                     'channel_id': 1,
#                     'name': 'My Channel',
#                     'is_public': True,
#                 },
#             ],
#             'permission_id': OWNER,
#             'profile_img_url': 'http://localhost:5001/imgurl/adfnajnerkn23k4234.jpg',
#         },
#         {
#             'u_id': 2,
#             'email': 'cs1521@cse.unsw.edu.au',
#             'password': 'abc1234',
#             'name_first': 'Andrew',
#             'name_last': 'Taylor',
#             'handle_str': 'hataylor',
#             'channels': [

#             ],
#             'permission_id': MEMBER,
#             'profile_img_url': 'http://localhost:5001/imgurl/adfnajnerkn23k4234.jpg',
#         },
#     ],
#     'channels': [
#         {
#             'channel_id': 1,
#             'name' : 'channel1',
#             'messages': [
#                 {
#                     'is_pinned': True,
#                     'message_id': 1,
#                     'u_id': 1,
#                     'message': 'Hello world',
#                     'time_created': 1582426789,
#                     'reacts': [
#                         # React id 1 - thumbs up
#                         {
#                             "react_id": 1,
#                             "u_ids": [1, 2, 3]
#                         },
#                         {
#                             "react_id": 2,
#                             "u_ids": [1, 2, 3]
#                         },
#                         {
#                             "react_id": 3,
#                             "u_ids": [1, 2, 3]
#                         }
#                     ]
#                 },
#                 {
#                     'is_pinned': False,
#                     'message_id': 2,
#                     'u_id': 2,
#                     'message': 'Hello user1!',
#                     'time_created': 1582426790,
#                     'reacts': [
#                         # React id 1 - thumbs up
#                         {
#                             "react_id": 1,
#                             "u_ids": [1, 2, 3]
#                         },
#                         {
#                             "react_id": 2,
#                             "u_ids": [1, 2, 3]
#                         },
#                         {
#                             "react_id": 3,
#                             "u_ids": [1, 2, 3]
#                         }
#                     ]
#                 },
#             ],
#             'all_members': [
#                 {
#                     'u_id': 1,
#                     'name_first' : 'Hayden',
#                     'name_last': 'Jacobs',
#                     'profile_img_url': "",
#                 },
#             ],
#             'owner_members': [
#                 {
#                     'u_id': 1,
#                     'name_first' : 'Hayden',
#                     'name_last': 'Jacobs',
#                     'profile_img_url': "",
#                 },
#             ],
#             'is_public': True,
#         },
#         {
#             'channel_id': 2,
#             'name' : 'channel2',
#             'messages': [
#             ],
#             'all_members': [
#                 {
#                     'u_id': 2,
#                     'name_first' : 'Andrew',
#                     'name_last': 'Taylor',
#                     'profile_img_url': "",
#                 },
#             ],
#             'owner_members': [
#                 {
#                     'u_id': 1,
#                     'name_first' : 'Andrew',
#                     'name_last': 'Taylor',
#                     'profile_img_url': "",
#                 },
#             ],
#             'is_public': False,
#         },
#     ],
# }
