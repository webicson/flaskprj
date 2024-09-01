from flask import render_template, redirect, url_for, flash, request
from flask_babel import _
from app import db
from app.dids import bp
from app.dids.forms import NewDIDForm
from app.models import Dids, Countries, Vendors
from flask_login import login_required
from app.dids.tables import All_available_dids

@bp.route('/new_dids', methods=['GET', 'POST'])
@login_required
def new_dids():
    form = NewDIDForm()
    form.country_id.choices= [(c.id, c.name) for c in Countries.query.order_by('name')];
    form.vendor_id.choices = [(v.id, v.name) for v in Vendors.query.order_by('name')];
    if form.validate_on_submit():
        did = Dids(number=form.number.data, country_id=form.country_id.data, vendor_id=form.vendor_id.data)
        db.session.add(did)
        db.session.commit()
        flash(_('Congratulations, new did was added to the system!'))
        # return redirect(url_for('customer.login'))
    return render_template('forms/form_page.html', title=_('Dids'), form=form)

@bp.route('/all_dids',  methods=['GET', 'POST'])
def all_dids():
    all_dids = Dids.query.all()
    table = All_available_dids(all_dids)
    return render_template('tables/search_table_page.html', title=_('All Dids'), table=table)