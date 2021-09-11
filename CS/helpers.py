import requests
import json
import smtplib
import ssl
from urllib.parse import quote_plus
from time import sleep
from os import environ
from os.path import dirname


# A collection of globally-shared helper functions

def email_admin(status_code, message):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "tom.zhang.dev@gmail.com"
    receiver_email = "tom.zhang.dev@gmail.com"
    pass_file = open(
        '{}/credentials/dev-gmail-pass.txt'.format(dirname(__file__)))
    password = pass_file.readline()
    pass_file.close()

    msg_template = """Subject: {}

    {}"""

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email,
                        msg_template.format(status_code, message))


def cr_api_request(tag: str, action: str, i: int = 0) -> dict:
    """
    A function to send a /GET request to Clash Royale API with comprehensive error handling.
    :param tag: Either a player tag, clan tag, or location id (e.g., '#9YJUPU9LY' | '#QCQJ8JG' | '57000249');
    :param action: 'battle_log' | 'player_info' | 'clan_members' | 'player_rankings'
    :param i: An optional counter for potential recursive calls;
    :return: JSON response.
    """
    # prep
    url = 'https://api.clashroyale.com/v1/'

    if action == 'battle_log':
        url += 'players/' + quote_plus(tag) + '/battlelog'
    elif action == 'player_info':
        url += 'players/' + quote_plus(tag)
    elif action == 'clan_members':
        url += 'clans/' + quote_plus(tag) + '/members'
    elif action == 'player_rankings':
        url += 'locations/' + quote_plus(tag) + '/rankings/players'
    else:
        print(
            'action = [battle_log | player_info | clan_members | player_rankings]')
        exit(1)

    token = environ.get('TOKEN')
    headers = {'Authorization': 'Bearer ' + token}

    # request
    try:
        response = requests.get(url, headers=headers)
    except:
        message = '/GET request failed; URL = {}; Bearer Token = {}.'.format(
            url, token)
        email_admin(500, message)
        return {'statusCode': 500, 'body': {'message': message}}

    status_code = response.status_code
    res = response.json()

    # handle error responses
    if status_code == 200:
        pass

    elif status_code == 429:
        # request throttled: amount of requests exceeded threshold defined for API token
        # switch to another api key & notify admin
        api_keys = json.loads(environ.get('API_KEYS'))
        curr_key = environ.get('CURR_KEY')
        key_names = list(api_keys.keys())
        curr_key_idx = key_names.index(curr_key)

        if curr_key_idx >= len(api_keys) - 1:
            # email admin: used up all keys, require immediate action
            message = 'Used up all API keys. Program terminated. Immediate action required: Create new tokens and update api_keys.json'
            email_admin(429, message)
            exit(1)  # terminate program because it is a critical failure
        else:
            # use next available key
            next_key = key_names[curr_key_idx + 1]
            token = str(api_keys.get(next_key))

            # update environment variables
            environ['CURR_KEY'] = next_key
            environ['TOKEN'] = token

            # email admin: using next available key
            message = 'Current key "{}" obsolete. Retrying request with next available key in api_keys.json: "{}"'.format(
                curr_key, next_key)
            email_admin(429, message)

            # retry request with new token
            cr_api_request(tag, action)

    elif status_code == 503:
        # service temprorarily unavailable due to maintenance
        if i == 0:
            email_admin(
                503, 'Service down (initial alert). Retrying request every 5 minutes.')

        # email admin every hour the service is down
        elif i % 12 == 0:  # 1 iteration = 5 mins; 12 iterations = 1 hour
            message = 'Service down for {} hours. Still retrying request every 5 minutes.'.format(
                i // 12)
            email_admin(503, message)

        i += 1
        sleep(300)  # wait 5 mins then try again by recursion
        cr_api_request(tag, action, i=i)

    else:
        # other errors: simply email admin
        message = '/GET request failed\n\nURL = {}\n\nBearer Token = {}\n\nResponse = {}'.format(
            url, token, res)
        email_admin(status_code, message)

    return {'statusCode': status_code, 'body': res}


def get_clanmate_tags(player_tag: str) -> list:
    """
    A function to get the player tags of each clanmate for the given player.
    :param player_tag: A string (e.g., '#9YJUPU9LY');
    :return: A list of player tags.
    """
    # get player info
    player_info_res = cr_api_request(player_tag, 'player_info')

    if player_info_res.get('statusCode') != 200:
        return None  # request failed

    player = player_info_res.get('body')
    clan = player.get('clan')

    if clan is not None:
        clan_tag = clan.get('tag')
    else:
        return []  # not part of a clan

    # get clan members
    clan_members_res = cr_api_request(clan_tag, 'clan_members')

    if clan_members_res.get('statusCode') != 200:
        return None  # request failed

    else:
        clan = clan_members_res.get('body')
        members = clan.get('items')
        tags = []
        for member in members:
            tag = member.get('tag')
            if tag != player_tag:
                tags.append(tag)

    return tags
