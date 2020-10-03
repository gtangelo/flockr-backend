data = {
    'active_users': [
        {
            'token': '12345',
            'u_id': 1,
        },
    ],
    'users': [
        {
            'u_id': 1,
            'email': 'cs1531@cse.unsw.edu.au',
            'password': 'abc1234',
            'name_first': 'Hayden',
            'name_last': 'Jacobs',
            'handle_str': 'hjacobs',
            # List of channels that the user is a part of
            'channels': [
                {
                    'channel_id': 1,
                    'name': 'My Channel',
                },
            ],
            'is_flockr_owner': True,
        },
        {
            'u_id': 2,
            'email': 'cs1521@cse.unsw.edu.au',
            'password': 'abc1234',
            'name_first': 'Andrew',
            'name_last': 'Taylor',
            'handle_str': 'hataylor',
            # List of channels that the user is a part of
            'channels': [

            ],
            'is_flockr_owner': False,
        },
    ],
    'channels': [
        {
            'channel_id': 1,
            'name' : 'channel1',
            'messages': [
                {
                    'message_id': 1,
                    'u_id': 1,
                    'message': 'Hello world',
                    'time_created': 1582426789,
                },
                {
                    'message_id': 2,
                    'u_id': 2,
                    'message': 'Hello user1!',
                    'time_created': 1582426790,
                },
                {
                    'message_id': 3,
                    'u_id': 1,
                    'message': 'Hello user2',
                    'time_created': 1582426791,
                },
            ],
            'all_members': [
                {
                    'u_id': 1,
                    'name_first' : 'Hayden',
                    'name_last': 'Jacobs'
                },
            ],
            'owner_members': [
                {
                    'u_id': 1,
                    'name_first' : 'Hayden',
                    'name_last': 'Jacobs'
                },
            ],
            'is_public': True,
        },
        {
            'channel_id': 2,
            'name' : 'channel2',
            'messages': [
            ],
            'all_members': [
                {
                    'u_id': 2,
                    'name_first' : 'Andrew',
                    'name_last': 'Taylor'
                },
            ],
            'owner_members': [
                {
                    'u_id': 1,
                    'name_first' : 'Andrew',
                    'name_last': 'Taylor'
                },
            ],
            'is_public': False,
        },
    ],
}
