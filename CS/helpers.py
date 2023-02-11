import sys
import requests
import json
import smtplib
import ssl
from datetime import datetime
from urllib.parse import quote_plus
from time import sleep
from os import environ
from os.path import dirname


# A collection of globally-shared helper functions

def init_log():
    """
    Open (create if does not exist) a log file named data_collection.log;
    Erase existing content if any;
    Set standard output to log file.
    """
    open("data_collection.log", "w").close()  # erase all content
    log_file = open("data_collection.log", "w")
    sys.stdout = log_file


def log(message):
    """
    Logs message to data_collection.log in real time;
    Assumes standard output is already set to log file.
    """
    print(datetime.now().strftime('%d/%m/%Y %H:%M:%S'), message, sep="\t\t")
    sys.stdout.flush()  # update log file in real time


def email_admin(status_code, message):
    """
    Send an alert email to admin; also save email content to log file.
    """
    try:
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "sluesportsresearch@gmail.com"
        receiver_email = "sluesportsresearch@gmail.com"
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

        # whenever we email admin, also print to log file
        log("email_admin()\n{}\n{}".format(status_code, message))

    except:
        log("email_admin() failed, logging instead: {}\n{}".format(
            status_code, message))


def cr_api_request(tag: str, action: str, i: int = 0) -> dict:
    """
    A function to send a /GET request to Clash Royale API with comprehensive error handling.
    :param tag: Either a player tag, clan tag, or location id (e.g., '#9YJUPU9LY' | '#QCQJ8JG' | '57000249');
    :param action: 'battle_log' | 'player_info' | 'clan_members' | 'player_rankings'
    :param i: An optional counter for potential recursive calls;
    :return: JSON response.
    """
    log('Entered cr_api_request(), tag = {}, action = {}, i = {}'.format(tag, action, i))

    # prep
    url = 'https://api.clashroyale.com/v1/'

    bannedTags = None

    if action == 'battle_log':
        url += 'players/' + quote_plus(tag) + '/battlelog'
    elif action == 'player_info':
        url += 'players/' + quote_plus(tag)
        fh = open('banned')
        bannedTags = set()
        for bannedTag in fh:
            bannedTags.add(bannedTag.strip())
        fh.close()
        # skip if it's a known banned tag
        if tag in bannedTags:
            return {'statusCode': 404, 'body': {"reason":"notFound"}}
    elif action == 'clan_members':
        url += 'clans/' + quote_plus(tag) + '/members'
    elif action == 'player_rankings':
        url += 'locations/' + quote_plus(tag) + '/rankings/players'
    else:
        log('action = [battle_log | player_info | clan_members | player_rankings]')
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

    try:
        res = response.json()
    except:
        email_admin(
            400, "response.json() failed, tag = {}, action = {}".format(tag, action))
        return {'statusCode': 400, 'body': {}}

    # handle error responses
    if status_code == 200:
        pass

    elif status_code == 403:
        # Fatal: IP address changed, need new key
        email_admin(403, str(res))
        exit(1)

    elif status_code == 404 and action == 'player_info':
        # player not found (likely banned)
        fh = open('banned', 'a')
        fh.write(tag + '\n')
        fh.close()
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
