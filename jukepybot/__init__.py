import os

from slackeventsapi import SlackEventAdapter
from slack import WebClient
from flask import Flask, request

from . import steam_helpers
from jukepybot.db import get_db


def create_app(test_config=None):
    # pylint: disable=unused-variable
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ["SECRET_KEY"],
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # Our app's Slack Event Adapter for receiving actions via the Events API
    slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
    slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events", app)

    # Create a WebClient for your bot to use for Web API requests
    slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
    slack_client = WebClient(slack_bot_token)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Example responder to greetings
    @slack_events_adapter.on("message")
    def handle_message(event_data):
        message = event_data["event"]
        for key, values in event_data.items():
            print(key, values)
        # If the incoming message contains "hi", then respond with a "Hello" message
        if message.get("subtype") is None and "hi" in message.get('text'):
            channel = message["channel"]
            message = "Hello <@%s>! :tada:" % message["user"]
            slack_client.chat_postMessage(channel=channel, text=message)

    # Example reaction emoji echo
    @slack_events_adapter.on("reaction_added")
    def reaction_added(event_data):
        for key, values in event_data.items():
            print(key, values)
        event = event_data["event"]
        emoji = event["reaction"]
        channel = event["item"]["channel"]
        text = ":%s:" % emoji
        slack_client.chat_postMessage(channel=channel, text=text)

    @app.route("/vidya", methods=['POST'])
    def vidya():
        # Verify slack signature using event adapter
        ts = request.headers.get('X-Slack-Request-Timestamp')
        sig = request.headers.get('X-Slack-Signature')
        slack_events_adapter.server.verify_signature(ts, sig)

        db = get_db()

        command_args = request.form.get('text').split(' ') # TODO: why form instead of args?
        param_slack_id = request.form.get('user_id')
        # print(command_args)
        # print(request.form) # outputs query parameters

        if ((command_args[0] == 'add') and (len(command_args) == 2)):
            param_steam_id = command_args[1]
            if not steam_helpers.validate_steam_id(param_steam_id):
                return "Invalid Steam ID"
            if steam_helpers.user_in_db(db, param_slack_id):
                return steam_helpers.update_db_id(db, param_slack_id, param_steam_id)
            else:
                return steam_helpers.add_new_id(db, param_slack_id, param_steam_id)
        elif ((command_args[0] == 'find') and (len(command_args) == 2)):
            param_vanity_url = command_args[1]
            return steam_helpers.find_steam_id(param_vanity_url)
        elif (command_args[0] != '' and len(command_args) >= 1):
            return 'Usage:\n `/vidya add <steam_id>`\n`/vidya find <vanity url name>`'

        if steam_helpers.user_in_db(db, param_slack_id) is None:
            response = "Add your steam ID using `/vidya add <steam_id>`\nFind your steam ID using `/vidya find <vanity url name>`"
        else:
            player_id = steam_helpers.get_db_steam_id(db, param_slack_id)
            steam_friends = steam_helpers.get_steam_friends(player_id)
            online_players = steam_helpers.get_online_players(steam_friends)
            response = f"Using Steam ID: `{player_id}`\n"
            response += steam_helpers.online_players_string(online_players)
        
        error = None

        return response

    # Error events
    @slack_events_adapter.on("error")
    def error_handler(err):
        print("ERROR: " + str(err))

    from . import db
    db.init_app(app)

    return app

