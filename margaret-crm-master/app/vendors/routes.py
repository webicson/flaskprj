from flask import render_template, redirect, url_for, flash, request
from flask_babel import _
from app import db
from app.vendors import bp
from app.vendors.forms import NewVendorForm
from app.models import Dids, Countries, Vendors
from flask_login import login_required

@bp.route('/new_vendor', methods=['GET', 'POST'])
@login_required
def new_vendor():
    form = NewVendorForm()
    # form.country_id.choices= [(c.id, c.name) for c in Countries.query.order_by('name')];
    # form.vendor_id.choices = [(v.id, v.name) for v in Vendors.query.order_by('name')];
    if form.validate_on_submit():
        vendor = Vendors(name=form.name.data, short=form.short.data)
        db.session.add(vendor)
        db.session.commit()
        flash(_('Congratulations, new vendor was added to the system!'))
        # return redirect(url_for('customer.login'))
    return render_template('forms/form_page.html', title=_('Vendors'), form=form)
