import json
from os import environ
from os.path import dirname


# open api_keys.json
try:
    f = open('{}/../credentials/api_keys.json'.format(dirname(__file__)))
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
