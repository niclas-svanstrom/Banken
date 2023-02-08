from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError
from wtforms.fields import IntegerField, SelectField, DateField, HiddenField, EmailField
import pycountry
from datetime import datetime

def emailContains(form, field):
    if not field.data.endswith('.se'):
        raise ValidationError('Måste sluta på .se dummer')

count= []
for country in pycountry.countries:
    c = (country.name,country.name)
    count.append(c)

def lower_than_one(form, field):
    if int(field.data) < 1:
        raise ValidationError("Can't be lower than 1")

class new_customer_form(FlaskForm):
    givenname = StringField('Firstname:', validators=[validators.DataRequired()])
    surname = StringField('Lastname:', validators=[validators.DataRequired()])
    streetaddress = StringField('Address:', validators=[validators.DataRequired()])
    city = StringField('City:', validators=[validators.DataRequired()])
    zipcode = IntegerField('Zipcode:', validators=[validators.DataRequired()])
    country = SelectField('Country:', choices=count, validators=[validators.DataRequired()])
    countrycode = HiddenField()
    birthday = DateField('Birthday:', validators=[validators.DataRequired()])
    nationalid = StringField('National ID:' , validators=[validators.DataRequired()])
    phonecountrycode = IntegerField('Phone Countrycode:')
    phonenumber = StringField('Phonenumber:', validators=[validators.DataRequired()])
    email = StringField('Emailaddress:', validators=[validators.DataRequired()])


class debit_and_credit_form(FlaskForm):
    amount = IntegerField('Amount:', validators=[validators.DataRequired(), lower_than_one])
    account = SelectField('Account:', choices=[], validators=[validators.DataRequired()])

class transfer_form(FlaskForm):
    amount = IntegerField('Amount:', validators=[validators.DataRequired(), lower_than_one])
    from_account = SelectField('Account:', choices=[], validators=[validators.DataRequired()])
    to_account = SelectField('Account:', choices=[], validators=[validators.DataRequired()])

class new_user_form(FlaskForm):
    email = EmailField('Email:', validators=[validators.DataRequired()])
    password = PasswordField('Password:', validators=[validators.DataRequired()])
    role = SelectField('Role', choices=[], validators=[validators.DataRequired()])