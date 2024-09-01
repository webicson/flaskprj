# from app.test import test
import json

import requests
from flask import current_app
from flask import jsonify
from flask import render_template, flash, request
from flask_babel import _
from flask_login import login_required

from app import db
from app.mange import bp
from app.mange.forms import ActivateDid, FilterDid
from app.models import Dids, Countries, Vendors, Customers, Activations
from app.rivhit_api import rivhit_customer_list
from app.mange.tables import Mange



@bp.route('/all_activations')
@login_required
def all_activations():
    # print (get_all_outbuond_number())
    num = get_all_activations()
    table = Mange(num)
    return render_template('tables/search_table_page.html', title='All activations', table=table)

def get_all_activations():
    list = db.session.query(
        Activations.time_start, Activations.time_end,
        Customers.first_name, Customers.last_name, Customers.email, Dids.number
    ).filter(Activations.customer_id == Customers.id
             ).filter( Activations.did_id == Dids.id
                      ).all()

    return list

@bp.route('/activate_did', methods=['GET', 'POST'])
@login_required
def activate_did():
    form = ActivateDid()
    form_filter = FilterDid()
    DEFAULT = [('0', '')]

    form.customer.choices = [(c.id, c.first_name) for c in Customers.query.order_by('first_name')]
    form_filter.country_id.choices = DEFAULT + [(c.id, c.name) for c in Countries.query.order_by('name')]
    form_filter.vendor_id.choices = DEFAULT + [(v.id, v.name) for v in Vendors.query.order_by('name')]

    # form.did.choices = [(c.id, c.number) for c in Dids.query.order_by('number')]
    form.did.choices = available_bids(Dids.query.all())

    # form.did.choices = [(n.id, n.number) for n in Dids.query.filter_by(country_id='21').all()];
    if form.validate_on_submit():
        activation = Activations(did_id = form.did.data, customer_id = form.customer.data)
        db.session.add(activation)
        db.session.commit()
        flash(_('!'))
        # return redirect(url_for('customer.login'))
    # return render_template('mange/activate_did.html', title=_('Mange'), form=form, second_form =form_filter)
    return render_template('forms/form_page.html', title=_('Mange'), form=form, second_form=form_filter)


@bp.route('/filter_dids', methods=['GET', 'POST'])
def filter_dids():
    country_id= request.values.get('country_id', None)
    vendor_id = request.values.get('vendor_id', None)
    if (country_id == '0') and (vendor_id == '0'):
        dids = (Dids.query.order_by('number'));
    elif country_id == '0':
        dids = Dids.query.filter_by(vendor_id=vendor_id).order_by('number')
    elif vendor_id == '0':
        dids = Dids.query.filter_by(country_id=country_id).order_by('number')
    else:
        dids = Dids.query.filter_by(country_id=country_id, vendor_id=vendor_id).order_by('number')
    return jsonify(available_bids(dids))

@bp.route('/all_dids',  methods=['GET', 'POST'])
def all_did():
    dids = Dids.query.order_by('number')
    # dids = available_bids_the_full_info(dids)
    return render_template('mange/all_dids.html', title=_('Dids'), dids = dids )

def available_bids(dids_list):
    dids = []
    for aa in dids_list:
        if aa.is_active() == False:
            b = (aa.id, aa.number)
            dids.append(b)
    return dids

@bp.route('/test2' , methods=['GET', 'POST'])
def test2():
    return 'ggg'

@bp.route('/test1' , methods=['GET', 'POST'])
def test1():
    a = {'api_token': 'sss'}
    r  = None
    r = {'ddas': 'sss'}
    if type(r) is dict:
        a.update(r)

    return jsonify(a)


@bp.route('/api_test' , methods=['GET', 'POST'])
def ttt():
    cc = rivhit_customer_list()
    a = [(c['last_name'], c['customer_id']) for c in cc]
    return jsonify(cc)

    # return jsonify(rivhit_customer_list())

def api_test():
    if 'RIVHIT_API_TOKEN' not in current_app.config or not current_app.config['RIVHIT_API_TOKEN']: # #It starts by checking that there is a key for the translation service in the configuration, and if it isn't there it returns an error.
        return _('Error: the riv service is not configured.') #The error is also a string, so from the outside, this is going to look like the translated text.

    data = {'api_token': current_app.config['RIVHIT_API_TOKEN']}

    r = requests.post('https://api.rivhit.co.il/online/RivhitOnlineAPI.svc/Customer.List', '', data)

    if r.status_code != 200:
        return _('Error: the translation service failed.')
    # return json.loads(r.content.decode('utf-8-sig'))
    # return  json.dumps(r.content.decode('utf-8-sig'))
    data = json.loads(r.content.decode('utf-8-sig'))['data']

    arr = []
    for aa in data['customer_list']:
        arr.append((aa['first_name']))


    # return jsonify(arr)
    return str(data['customer_list'])