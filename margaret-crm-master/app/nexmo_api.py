import json
import requests
from flask import current_app
from flask_babel import _
from flask import jsonify


def nexmo_number_list(): # The function takes the text to translate and the source and destination language codes as arguments, and it returns a string with the translated text.
    res = api_nexemo_get('https://rest.nexmo.com/account/numbers')
    return res
def api_nexemo_get(url): ## return json
    if 'NEXMO_API_KEY' not in current_app.config or not current_app.config['NEXMO_API_KEY']: # #It starts by checking that there is a key for the translation service in the configuration, and if it isn't there it returns an error.
        return _('Error: the necemo service is not configured.') #The error is also a string, so from the outside, this is going to look like the translated text.
    ##  data = {'api_token': current_app.config['RIVHIT_API_TOKEN']}
    data = {'api_key': current_app.config['NEXMO_API_KEY'],
            'api_secret': current_app.config['NEXMO_API_SECRET']}
    response = requests.get(url, data)
    return json.loads(response.content.decode('utf-8-sig'))
    # if r.status_code == 200:
    # a = json.loads(cc)['count']

