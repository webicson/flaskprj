import json
import requests
from flask import current_app
from flask_babel import _
from flask import jsonify



def rivhit_customer_list(): # The function takes the text to translate and the source and destination language codes as arguments, and it returns a string with the translated text.
    res = api_rivhit_get('https://api.rivhit.co.il/online/RivhitOnlineAPI.svc/Customer.List')
    return res['customer_list']

def rivhit_add_new_customer(data):
    res = api_rivhit_get('https://api.rivhit.co.il/online/RivhitOnlineAPI.svc/Customer.New',data)
    if type(res) is dict:
        if res.get('customer_id'):
            return res['customer_id']
        else:
            return res
    else:
        data['id_number'] = 0
        return rivhit_add_new_customer(data)
    # return res

def api_rivhit_get(url, additional_data = None):
    if 'RIVHIT_API_TOKEN' not in current_app.config or not current_app.config['RIVHIT_API_TOKEN']: # #It starts by checking that there is a key for the translation service in the configuration, and if it isn't there it returns an error.
        return _('Error: the riv service is not configured.') #The error is also a string, so from the outside, this is going to look like the translated text.
    data = {'api_token': current_app.config['RIVHIT_API_TOKEN']}

    if type(additional_data) is dict:
        data.update(additional_data)

    r = requests.post(url, '', data)
    if r.status_code == 401:
        return _('Error: UNAUTHORIZED.')
    if r.status_code == 500:
        return _('Error: INVALID ID NUMBER.')
    if r.status_code != 200:
        return str(r.status_code)
        return _('Error: status - ' + str(r.status_code))
    else:
        data = json.loads(r.content.decode('utf-8-sig'))['data']
       # return jsonify(arr)
        return (data)
