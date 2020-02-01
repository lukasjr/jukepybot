from jukepybot import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_vidya(client):
    response = client.post(
        '/vidya', data={'text': '', 'user_id': 'U3130P5AA'}, 
         headers={'X-Slack-Signature': 'v0=d1fbb780735dd5fc6415b939a6862116560c519cadcd16e9cee655dd690f1a79',
                  'X-Slack-Request-Timestamp': '1580594621'})
    assert b'Using Steam ID' in response.data
