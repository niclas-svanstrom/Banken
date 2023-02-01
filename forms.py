from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError
from wtforms.fields import IntegerField, SelectField, DateField, HiddenField
import pycountry
from datetime import datetime

def emailContains(form, field):
    if not field.data.endswith('.se'):
        raise ValidationError('Måste sluta på .se dummer')

count= []
for country in pycountry.countries:
    c = (country.name,country.name)
    count.append(c)

def countrycodefunc(inputname):
    code = pycountry.countries.get(name=inputname).alpha_2
    return code

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


