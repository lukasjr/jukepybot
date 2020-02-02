import os

from jukepybot import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_vidya(client):
    response = client.post(
        '/vidya', data={'text': '', 'user_id': 'U3130P5AA'}, 
         headers={'X-Slack-Signature': os.environ['SLACK_SIGNATURE'],
                  'X-Slack-Request-Timestamp': os.environ['SLACK_TIMESTAMP']})
    assert b'Using Steam ID' in response.data
