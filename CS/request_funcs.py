import requests
import json
from urllib.parse import quote_plus
from time import sleep
from os import environ


# TODO - how? google
def email_admin():
    pass


def player_request(player_tag: str, endpoint: str) -> dict:
    """
    A function to send a /GET request to Clash Royale API with comprehensive error handling.
    :param player_tag: A string (e.g., '#9YJUPU9LY');
    :param endpoint: 'info' | 'battlelog';
    :return: json.
    """
    url = 'https://api.clashroyale.com/v1/players/{}/{}'.format(
        quote_plus(player_tag), endpoint)

    token = environ.get('TOKEN')
    headers = {'Authorization': 'Bearer ' + token}

    # request
    try:
        response = requests.get(url, headers=headers)
    except:
        # TODO send email
        return {'statusCode': 500,
                'body': {'message': '/GET request failed; url = {}; Bearer token = {}.'.format(url, token)}}

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
            # TODO email: use up all keys, require immediate action
            print('used up all keys')
            exit(1)
        else:
            # use next available key
            next_key = key_names[curr_key_idx + 1]
            token = str(api_keys.get(next_key))

            # update environment variables
            environ['CURR_KEY'] = next_key
            environ['TOKEN'] = token

            # TODO email admin

            # retry request with new token
            player_request(player_tag, endpoint)

    elif status_code == 503:
        # service temprorarily unavailable due to maintenance
        i = 0
        while True:
            if i % 288 == 0:  # 1 iteration = 5 mins; 288 iterations = 1 day
                # TODO email admin every day
                print('service down for {} days'.format(i // 288))
            i += 1
            sleep(300)  # wait 5 mins then try again; loop
            player_request(player_tag, endpoint)

    else:
        # other errors: simply email admin
        pass
        # TODO email admin

    return {'statusCode': status_code, 'body': res}


if __name__ == '__main__':
    # ==========================================
    # load api key
    try:
        f = open('api_keys.json')
    except FileNotFoundError:
        print('api_keys.json not found. Make sure SYE/CS/ is your pwd.')
        exit(1)
        # TODO send email and quit instead?

    api_keys = json.load(f)
    curr_key = "Tom's Key"
    token = str(api_keys.get(curr_key))

    # save vars as environment variable
    environ['API_KEYS'] = json.dumps(api_keys)
    environ['CURR_KEY'] = curr_key
    environ['TOKEN'] = token
    # ==========================================

    # testing
    print(player_request('#9YJUPU9LY', 'battlelog'))
