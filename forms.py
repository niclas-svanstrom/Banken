from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError
from wtforms.fields import IntegerField, SelectField, DateField, HiddenField, EmailField
import pycountry
from datetime import datetime

def only_letters(form, field):
    if not field.data.isalpha():
        raise ValidationError('Can only be letters')

count= []
for country in pycountry.countries:
    c = (country.name,country.name)
    count.append(c)

def lower_than_one(form, field):
    if int(field.data) < 1:
        raise ValidationError('Can not be lower than 1')
    
def valid_zipcode(form, field):
    zip_code = field.data.strip(" ")
    if zip_code.isdigit():
        if zip_code < 0:
            raise ValidationError("Zipcode can't be negative number")
        if len(zip_code) > 10:
            raise ValidationError("Zipcode can't be more than 10 digits")
    else:
        raise ValidationError('Zipcode must be numbers only')
    
def valid_adress(form, field):
    digits = 0
    adress = field.data
    for ch in adress:
        if ch.isdigit():
            digits += 1
    result = ''.join([i for i in adress if not i.isdigit()])
    if result.strip(" ").isalpha(): 
        if digits == 0:
            raise ValidationError('Address must contain at least one digit')
    else:
        raise ValidationError('Address must contain letters and at leat one digit')

def valid_phonenumber(form, field):
    phonenumber = field.data
    if phonenumber[0] == "+":
        raise ValidationError('Only phonenumber not with the phonecountrycode')
    elif not phonenumber.strip(" ").isdigit() or not phonenumber.strip("-").isdigit():
        raise ValidationError('Only digits in phonenumber except for -')
    

class new_customer_form(FlaskForm):
    givenname = StringField('Firstname:', validators=[validators.DataRequired(), only_letters, validators.length(min=2, max=30, message="Firstname cannot be less than two letters or more than 30")])
    surname = StringField('Lastname:', validators=[validators.DataRequired(), only_letters, validators.length(min=2, max=30, message="Lastname cannot be less than two letters or more than 30")])
    streetaddress = StringField('Address:', validators=[validators.DataRequired(), valid_adress])
    city = StringField('City:', validators=[validators.DataRequired(), only_letters])
    zipcode = IntegerField('Zipcode:', validators=[validators.DataRequired(), valid_zipcode])
    country = SelectField('Country:', choices=count, validators=[validators.DataRequired()])
    countrycode = HiddenField()
    birthday = DateField('Birthday:', validators=[validators.DataRequired()])
    nationalid = StringField('National ID:' , validators=[validators.DataRequired()])
    phonecountrycode = IntegerField('Phone Countrycode:', validators=[validators.DataRequired()])
    phonenumber = StringField('Phonenumber:', validators=[validators.DataRequired(), valid_phonenumber])
    email = EmailField('Emailaddress:', validators=[validators.DataRequired()])


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