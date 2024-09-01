from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, SelectFieldBase
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import Dids, Countries
from flask_babel import lazy_gettext as _l
from flask_babel import _


class ActivateDid(FlaskForm):
    customer = SelectField(_l('Customer'),  choices=[], coerce=int)
    did = SelectField(_l('did'), choices=[], coerce=int)
    submit = SubmitField(_l('Register'))

    # def validate_number(self, number):
    #     did = Dids.query.filter_by(number=number.data).first()
    #     if did is not None:
    #         raise ValidationError(_('Number is in use.'))

    # def edit_dids(request, id):
    #     did = Dids.query.get(id)
    #     form = NewDIDForm(request.POST, obj=did)
    #     form.

class FilterDid(FlaskForm):
    country_id = SelectField(_l('Country'), choices=[], coerce=int)
    vendor_id = SelectField(_l('Vendor'), choices=[], coerce=int)

