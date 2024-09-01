from flask_wtf import FlaskForm
from wtforms import StringField, SelectField,PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Optional
from app.models import Customers
from flask_babel import lazy_gettext as _l
from flask_babel import _

class NewCustomerForm(FlaskForm):
    name = StringField(_l('Last Name'), validators=[DataRequired()])
    first_name = StringField(_l('First Name'), validators=[Optional()])
    address = StringField(_l('Address'), validators=[Optional()])
    city = StringField(_l('City'), validators=[Optional()])
    # pob = IntegerField(_l('Pob'), validators=[Optional()])
    # zipcode = IntegerField(_l('Zipcode'),validators=[Optional()])
    phone =  StringField(_l('Phone'), validators=[Optional()])
    # fax =  StringField(_l('Fax'), validators=[Optional()])
    id_number =  IntegerField(_l('ID Number'), validators=[Optional()])
    # vat_number =  IntegerField(_l('Vat Number'), validators=[Optional()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])  # Email() - This is another stock validator that comes with WTForms that will ensure that what the user types in this field matches the structure of an email address.
    submit = SubmitField(_l('Register'))

    # When you add any methods that match the pattern validate_<field_name>, WTForms takes those as custom validators and invokes them in addition to the stock validators.
    def validate_username(self, name):
        customer = Customers.query.filter_by(name=name.data).first()
        if customer is not None:
            raise ValidationError(_('Please use a different name.'))

    def validate_email(self, email):
        customer = Customers.query.filter_by(email=email.data).first()
        if customer is not None:
            raise ValidationError(_('Please use a different email address.'))

    def validate_id_number(self, id_number):
        no = id_number.data
        if (len(str(no)) != 9):
            raise ValidationError(_('Id number is Illegal'))

class ActiveCustomerToService(FlaskForm):
    customer = SelectField(_l('Customer'),  choices=[], coerce=int)
    submit = SubmitField(_l('Register'))
