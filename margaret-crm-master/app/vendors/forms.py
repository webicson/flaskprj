from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, SelectFieldBase
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import Countries, Vendors
from flask_babel import lazy_gettext as _l
from flask_babel import _


class NewVendorForm(FlaskForm):
    name = StringField(_l('Name'), validators=[DataRequired()])
    short = StringField(_l('Short Name'), validators=[DataRequired()])
    submit = SubmitField(_l('Add'))

    def validate_name(self, name):
        vendor = Vendors.query.filter_by(name=name.data).first()
        if vendor is not None:
            raise ValidationError(_('Vendor name is in use.'))

    def validate_short_name(self, name):
        vendor = Vendors.query.filter_by(short=short.data).first()
        if vendor is not None:
            raise ValidationError(_('Vendor short name is in use.'))