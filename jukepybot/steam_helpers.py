from steam.webapi import WebAPI
from steam.steamid import SteamID
from requests.exceptions import HTTPError
import os

# steam_api is triggering no-member due to the way interfaces are created (I think)
# pylint: disable=no-member

steam_api_key = os.environ["STEAM_API_KEY"]
steam_api = WebAPI(key=steam_api_key)


def validate_steam_id(steam_id):
    try:
        steam_api.ISteamUser.GetFriendList(steamid=steam_id)
        return True
    except HTTPError:
        return False


def find_steam_id(vanity_url_user):
    """ https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/? """
    response = steam_api.ISteamUser.ResolveVanityURL(vanityurl=vanity_url_user)
    print(response)
    if 'steamid' in response['response']:
        return f"Your steam ID is {response['response']['steamid']}"
    else:
        return f"No match using {vanity_url_user}"
    


def get_steam_friends(player_id):
    """ Return friends in a string that is comma delimited list """
    response = steam_api.ISteamUser.GetFriendList(steamid=player_id)
    friend_ids = ""
    for friend in response['friendslist']['friends']:
        friend_ids += "{},".format(friend['steamid'])
    return friend_ids


def get_online_players(player_list):
    """ Return a dictionary of all players online and what game they are playing"""
    online_players = {}
    player_summaries = steam_api.ISteamUser.GetPlayerSummaries(steamids=player_list)
    for player in player_summaries['response']['players']:
        if 'gameextrainfo' in player:
            online_players[player['personaname']] = player['gameextrainfo']
    return online_players


def online_players_string(online_players):
    """ Constructs the string to return to slack """
    online_players_string = ""
    for player, game in online_players.items():
        online_players_string += "{} is playing {}\n".format(player, game)
    if not online_players_string: online_players_string = "No friends are playing games"
    return online_players_string


def user_in_db(db, username):
    return db.execute(
        'SELECT slack_id FROM user WHERE slack_id = ?', (username,)
    ).fetchone()


def update_db_id(db, slack_id, steam_id):
    db.execute(
        'UPDATE user SET steam_id = ? WHERE slack_id = ?', (steam_id, slack_id)
    )
    db.commit()
    return "Steam ID updated"


def add_new_id(db, slack_id, steam_id):
    db.execute(
        'INSERT INTO user (slack_id, steam_id) VALUES (?, ?)', (slack_id, steam_id)
    )
    db.commit()
    return "Steam ID added"


def get_db_steam_id(db, slack_id):
    return db.execute(
        'SELECT steam_id FROM user WHERE slack_id = ?', (slack_id,)
    ).fetchone()[0]

