from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, SelectFieldBase, TextField, IntegerField, FormField, FieldList
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Required
from app.models import Dids, Countries
from flask_babel import lazy_gettext as _l
from flask_babel import _

class IMForm(Form):
    username = StringField()

class ContactForm(Form):
    first_name  = StringField()
    last_name   = StringField()


class FilterDid(FlaskForm):
    country_id = SelectField(_l('Country'), choices=[], coerce=int)
    vendor_id = SelectField(_l('Vendor'), choices=[], coerce=int)
    type_id =  SelectField(_l('Type'), choices=[], coerce=int)

class TelephoneForm(Form):
    outbound_number = StringField(validators=[DataRequired()])

class SmsForword(FlaskForm):
    # filter_did = FormField(FilterDid)
    # im_accounts = FieldList(FormField(IMForm))
    did = SelectField(_l('Did Number'), choices=[])
    customer = SelectField(_l('Customer Name'),  choices=[], coerce=int)
    a2b_username = StringField(_l('A2B Account Username'), validators=[DataRequired()])
    a2b_password = StringField(_l('A2B Account Password'), validators=[DataRequired()])
    outbound_number = StringField(_l('Phone Number'), validators=[DataRequired()])
    # authors = FieldList(StringField('Name', validators=[DataRequired()]))
    submit = SubmitField(_l('Register'))
# class wtforms.fields.FormField(form_class, default field arguments, separator='-')
# Encapsulate a form as a field in another form.
#
# Parameters:
# form_class – A subclass of Form that will be encapsulated.
# separator – A string which will be suffixed to this field’s name to create the prefix to enclosed fields. The default is fine for most uses.

    # def validate_number(self, number):
    #     did = Dids.query.filter_by(number=number.data).first()
    #     if did is not None:
    #         raise ValidationError(_('Number is in use.'))

    # def edit_dids(request, id):
    #     did = Dids.query.get(id)
    #     form = NewDIDForm(request.POST, obj=did)
    #     form.



class ContactForm(Form):
    first_name   = StringField()
    last_name    = StringField()
    mobile_phone = FormField(TelephoneForm)
    office_phone = FormField(TelephoneForm)