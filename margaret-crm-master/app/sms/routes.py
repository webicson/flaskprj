from flask import render_template, redirect, url_for, flash, request
from flask import Flask, request, jsonify
from pprint import pprint
from app.models import NexmoSms
from app import db
from flask_login import login_required
from app.sms.tables import SmsTable, NexmoNumbersTable, SingleDidDetails, MangeSms
from flask_babel import _
from app.nexmo_api import nexmo_number_list
import json
import requests
from flask import current_app
from flask_babel import _
from flask import jsonify
import urllib
from app.sms.forms import SmsForword, FilterDid
from app.models import Countries, Vendors, Customers, A2b_account, Forword_sms_to_phone, Outbuond_number
# Sms_forword_sms

# app = Flask(__name__)

from app.sms import bp


@bp.route('/webhooks/inbound-sms', methods=['GET', 'POST'])
# Any messages sent to one of your Nexmo virtual numbers are sent to your webhook using a GET or POST request.
def inbound_sms():
    if request.is_json:
        # pprint(request.get_json())
        data = request.get_json()
    else:
        data = dict(request.form) or dict(request.args)


    # save the data nexmo-sms data into db
    msisdn = data['msisdn']
    did = data['to']
    sms = NexmoSms(type=data['type'], msisdn=data['msisdn'], to=data['to'], messageId=data['messageId'],
                   messageTimestamp=data['message-timestamp'])
    #
    if 'timestamp' in data:
        sms.timestamp = data['timestamp']
    if 'text' in data:
        message = data['text']
        sms.text = data['text']
        sms.keyword = data['keyword']
    if 'data' in data:
        message = data['data']
        sms.data = data['data']
        sms.data = data['udh']
    if 'concat' in data:
        sms.concat = data['concat']
        sms.concatPart = data['concat-part']
        sms.concatRef = data['concat-ref']
        sms.concatTotal = data['concat-total']

    db.session.add(sms)
    db.session.commit()

    outbounds = get_all_outbuond_number_for_did(did[0])
    for outbound in outbounds:
        forword_sms(text=message,
                    username=outbound.account_username,
                    password=outbound.account_password,
                    from_mumber=msisdn,
                    to_number =  outbound.phone_number)
    # Forword_sms_to_phone.msisdn, A2b_account.account_username, A2b_account.account_password,
        #Outbuond_number.phone_number

    return ('',
            204)  # When you receive a message on your webhook, you must send a 200 OK response. If you don't, then Nexmo will assume that you have not received the message and will keep resending it for the next 24 hours.
    # app.run(port=5000)


def forword_sms(username, password, text, from_mumber,to_number):
    # username='7046859009', password='4333490497', text='Hello World', from_mumber='09999',
    #             to_number='00972548366736'
    url = 'https://sip1.israelnumber.com/a2billing/customer/sendsms.php'
    data = {'username': username,
            'password': password,
            'from': from_mumber,
            'to': to_number,  # Numbers should be entered in a full international format:
            #  For example for send SMS to UK mobile type please number in the next format: 004477XXXXXXX
            'text': str(text[0])}
    r = requests.post(url, data)
    print("here!!!")
    print(str(data))
    print(r.status_code, r.reason)
    print('###########')
    if r.status_code == 1701:
        return 1
        # SUCCESS. Message Submitted Successfully.
    if r.status_code == 1702:
        return 0
        # - 1702: INVALID URL.One of the parameters was not provided or left blank.
    if r.status_code == 1706:
        return 0
        # - 1706: INVALID DESTINATION.
        # - HOST NOT AVAILABLE. Error in IP or user/password identification
        # - INSUFFICIENT CREDIT. The balance is not enough to send SMS
    if r.status_code == 1025:
        return 0
        # - 1025: INTERNAL ERROR. Please contact ITC support (support@israelnumber.com)


# this page will show all the sms the system get from nexmo.
@bp.route('/sms_table', methods=['GET', 'POST'])
@login_required
def sms_table():
    nexmo_sms = NexmoSms.query.order_by('id')
    table = SmsTable(nexmo_sms)
    # return render_template('customers/new-customer.html', title=_('New Customer'), form=form, customers=customers)
    return render_template('tables/search_table_page.html', title='sms', table=table)


# this page will show all the did numbers the system  from nexmo.
@bp.route('/all_nexmo_numbers', methods=['GET', 'POST'])
#  all the inbound numbers associated with your Nexmo account.
@login_required
def all_nexmo_numbers():
    list = nexmo_number_list();
    list = list['numbers']
    table = NexmoNumbersTable(list)
    return render_template('tables/search_table_page.html', title='Nexmo Number List', table=table)


@bp.route('/outbound_sms', methods=['GET', 'POST'])
@login_required
def outbound_sms():
    form = SmsForword()
    form_filter = FilterDid()
    DEFAULT = [('0', '')]

    form_filter.country_id.choices = DEFAULT + [(c.id, c.name) for c in Countries.query.order_by('name')]
    form_filter.vendor_id.choices = DEFAULT + [(v.id, v.name) for v in Vendors.query.order_by('name')]
    form.customer.choices = [(c.id, c.first_name) for c in Customers.query.order_by('first_name')]
    # form.did.choices = [(c.id, c.number) for c in Dids.query.order_by('number')]
    nexmo_did = nexmo_number_list()
    nexmo_did = nexmo_did['numbers']
    form.did.choices = [(c['msisdn'], c['msisdn']) for c in nexmo_did]

    if form.validate_on_submit():
        customer_id = form.customer.data
        a2b_account = A2b_account(customer_id=customer_id, account_username=form.a2b_username.data,
                                  account_password=form.a2b_password.data)
        # activation = Activations(did_id = form.did.data, customer_id = form.customer.data)
        numbers = form.outbound_number.data
        numbers = numbers.split(',')
        for number in numbers:
            outbuond_number = Outbuond_number(customer_id=customer_id, phone_number=number)
            db.session.add(a2b_account)
            db.session.add(outbuond_number)
            db.session.commit()
            forword_sms = Forword_sms_to_phone(msisdn=form.did.data, outbuond_number_id=outbuond_number.id,
                                           a2b_account_id=a2b_account.id, customer_id=customer_id)
            db.session.add(forword_sms)
            db.session.commit()

        flash(_('!') + str(a2b_account.id))
    return render_template('forms/form_page.html', title=_('SMS'), form=form, second_form=form_filter)


@bp.route('/did/<msisdn>')
@login_required
def user(msisdn):
    forword_sms = get_all_outbuond_number_for_did(msisdn)
    table = SingleDidDetails(forword_sms)
    return render_template('tables/search_table_page.html', title='sms', table=table)

def get_all_outbuond_number_for_did(msisdn): # msisdn is did number
    list = db.session.query(
        Forword_sms_to_phone.msisdn, A2b_account.account_username, A2b_account.account_password,
        Outbuond_number.phone_number
    ).filter(Forword_sms_to_phone.a2b_account_id == A2b_account.id
             ).filter(Forword_sms_to_phone.outbuond_number_id == Outbuond_number.id
                      ).filter(Forword_sms_to_phone.msisdn == msisdn).all()

    return list

@bp.route('/all_outbounded_sms')
@login_required
def all_outbounded_sms():
    # print (get_all_outbuond_number())
    num = get_all_outbuond_number()
    table = MangeSms(num)
    return render_template('tables/search_table_page.html', title='Outbounded SMS List', table=table)

def get_all_outbuond_number():
    list = db.session.query(
        Forword_sms_to_phone.msisdn, A2b_account.account_username, A2b_account.account_password,
        Outbuond_number.phone_number, Customers.first_name, Customers.last_name, Customers.email
    ).filter(Forword_sms_to_phone.a2b_account_id == A2b_account.id
             ).filter(Forword_sms_to_phone.outbuond_number_id == Outbuond_number.id
                      ).filter(Forword_sms_to_phone.customer_id == Customers.id).all()

    return list
