import json
import requests
from flask import current_app
from flask_babel import _

def translate(text, source_language, dest_language): # The function takes the text to translate and the source and destination language codes as arguments, and it returns a string with the translated text.
    if 'MS_TRANSLATOR_KEY' not in current_app.config or not current_app.config['MS_TRANSLATOR_KEY']: # #It starts by checking that there is a key for the translation service in the configuration, and if it isn't there it returns an error.
        return _('Error: the translation service is not configured.') #The error is also a string, so from the outside, this is going to look like the translated text.
    auth = {'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY']}
    r = requests.get('https://api.microsofttranslator.com/v2/Ajax.svc'
                     '/Translate?text={}&from={}&to={}'.format(
                         text, source_language, dest_language),
                     headers=auth)
    if r.status_code != 200:
        return _('Error: the translation service failed.')
    return json.loads(r.content.decode('utf-8-sig'))