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


def player_request(player_tag: str, endpoint: str, i: int = 0) -> dict:
    """
    A function to send a /GET request to Clash Royale API with comprehensive error handling.
    :param player_tag: A string (e.g., '#9YJUPU9LY');
    :param endpoint: 'info' | 'battlelog';
    :param i: An optional counter for potential recursive calls;
    :return: JSON response.
    """
    url = 'https://api.clashroyale.com/v1/players/{}/{}'.format(
        quote_plus(player_tag), endpoint)

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
            player_request(player_tag, endpoint)

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
        player_request(player_tag, endpoint, i=i)

    else:
        # other errors: simply email admin
        message = '/GET request failed\n\nURL = {}\n\nBearer Token = {}\n\nResponse = {}'.format(
            url, token, res)
        email_admin(status_code, message)

    return {'statusCode': status_code, 'body': res}


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
    print(player_request('#9YJUPU9LY', 'battlelog'))
