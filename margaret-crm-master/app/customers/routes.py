from flask import render_template, redirect, url_for, flash, request
from flask_babel import _
from app import db
from app.customers import bp
from app.customers.forms import NewCustomerForm, ActiveCustomerToService
from app.models import Customers, Rivhit_customer
from app.rivhit_api import rivhit_customer_list, rivhit_add_new_customer
from flask import jsonify, json
from flask_login import login_required
from app.customers.tables import All_customers_in_db

@bp.route('/new-customer', methods=['GET', 'POST'])
@login_required
def new_customer():
    form = NewCustomerForm()
    if form.validate_on_submit():
        customer = Rivhit_customer(last_name=form.name.data, email = form.email.data, first_name = form.first_name.data, address= form.address.data, city= form.city.data, id_number=form.id_number.data, phone=form.phone.data)
        rivhit_id = customer.add_to_rivhit()
        # rivhit_id = customer.printit()
        # flash(rivhit_id)
        if (rivhit_id) :
            customer.add_to_db()
            flash(_('Congratulations, new customer was added to the Rivhit!'))
        else:
            flash(_('Error'), 'error')

    return render_template('forms/form_page.html', title=_('New Customer'), form=form)

@bp.route('/all_customer', methods=['GET', 'POST'])
@login_required
def all_customers():
    customers = Customers.query.order_by('first_name')
    table = All_customers_in_db(customers)
    return render_template('tables/search_table_page.html', table=table, title = "All Customers")


def add_customer_to_system():
    form = ActiveCustomerToService()
    rivhit_list = rivhit_customer_list()
    form.customer.choices = [(c['customer_id'], c['first_name']) for c in rivhit_list]
    return render_template('basic_form.html', title=_('add'), form=form, titleh1 = _('Active Customer to the service'))

@bp.route('/add_all_customers_from_rivhit_to_the_system', methods=['GET', 'POST']) #this link will add all the new customers from Rivhit to Margaret and only theme.
def rivhit_customer_list_as_object():
    customer_list = rivhit_customer_list()
    for customer in customer_list:
        if customer["first_name"] != '' and customer["email"] !='' :
            c = Rivhit_customer(last_name=customer["last_name"], first_name=customer["first_name"],email=customer["email"],customer_id=customer["customer_id"] )
            c.add_to_db()
    return 'done'



