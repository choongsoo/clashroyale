import requests
import json
import smtplib
import ssl
from urllib.parse import quote_plus
from time import sleep
from os import environ
from os.path import dirname


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
    :param tag: Either a player tag or clan tag (e.g., '#9YJUPU9LY' | '#QCQJ8JG');
    :param action: 'battle_log' | 'player_info' | 'clan_members'
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
    else:
        print('action = [battle_log | player_info | clan_members]')
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


def get_participant_tags(player_tag: str) -> list:
    """
    A function to get the player tags of each participant in the given player's battle log.
    These include both teammates (if any) and opponents.
    :param player_tag: A string (e.g., '#9YJUPU9LY');
    :return: A list of player tags.
    """
    battle_log_res = cr_api_request(player_tag, 'battle_log')

    if battle_log_res.get('statusCode') != 200:
        return None  # request failed

    else:
        battle_log = battle_log_res.get('body')
        tags = []

        for battle in battle_log:
            # team
            team = battle.get('team')
            for player in team:
                tag = player.get('tag')
                if tag != player_tag:
                    tags.append(tag)

            # opponent
            for player in battle.get('opponent'):
                tags.append(player.get('tag'))

        return tags


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


if __name__ == '__main__':
    # ==========================================
    #                Load API Key
    # ==========================================
    # open api_keys.json
    try:
        f = open('{}/credentials/api_keys.json'.format(dirname(__file__)))
    except FileNotFoundError:
        print('ERROR: SYE/CS/credentials/api_keys.json not found.')
        exit(1)

    # load api keys
    try:
        api_keys = json.load(f)
    except json.decoder.JSONDecodeError:
        print('ERROR: Invalid JSON content in api_keys.json')
        exit(1)

    # validate length
    key_names = list(api_keys.keys())
    if len(key_names) == 0:
        print('ERROR: No API key found in api_keys.json')

    # use first key available
    curr_key = key_names[0]

    # get bearer token
    try:
        token = api_keys[curr_key]
    except KeyError:
        print('ERROR: API key "{}" does not exist in api_keys.json'.format(curr_key))
        exit(1)

    # save vars as environment variables
    environ['API_KEYS'] = json.dumps(api_keys)
    environ['CURR_KEY'] = str(curr_key)
    environ['TOKEN'] = str(token)
    # ==========================================

    # testing
    print(cr_api_request('#9YJUPU9LY', 'battle_log'), '\n')
    print(cr_api_request('#QCQJ8JG', 'clan_members'), '\n')
    print(get_participant_tags('#9YJUPU9LY'), '\n')
    print(get_clanmate_tags('#9YJUPU9LY'))
