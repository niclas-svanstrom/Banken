from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError
from wtforms.fields import IntegerField, SelectField, DateField, HiddenField, EmailField
import pycountry
from datetime import datetime
import re

def only_letters(form, field):
    if not field.data.isalpha():
        raise ValidationError('Can only be letters')

count= []
for country in pycountry.countries:
    if country.name == 'United States':
        c = ('USA','USA')
    else:
        c = (country.name,country.name)
    count.append(c)

def lower_than_one(form, field):
    if int(field.data) < 1:
        raise ValidationError('Can not be lower than 1')
    
def valid_zipcode(form, field):
    if not str(field.data).isdigit():
        raise ValidationError("Must be a number")
    elif field.data < 0:
        raise ValidationError("Zipcode can not be negative number")

def valid_adress(form, field):
    regex = re.compile(r'([A-Öa-ö0-9]+[\s])*([A-Äa-ö0-9]+[\s])+([0-9]{1,})+')
    regex2 = re.compile(r'([0-9]{1,}+[\s])+([A-Öa-ö0-9]+[\s])*([A-Äa-ö0-9])+')
    if not (re.fullmatch(regex, field.data) or  re.fullmatch(regex2, field.data)):
        raise ValidationError('Not a valid address must contain letters, whitespace and at leat one digit')

def valid_phonenumber(form, field):
    phonenumber = field.data
    if not phonenumber[0].isdigit():
        raise ValidationError('Can only start with a number')
    elif phonenumber.count("-") > 1:
        raise ValidationError('Can only be one - in the phonenumber')
    elif not (phonenumber.replace(" ","").isdigit() or phonenumber.replace("-","").isdigit()):
        raise ValidationError('Only digits in phonenumber except for -')
    
def valid_nationalid(form, field):
    regex = re.compile(r'([0-9]{8,8}+[-])+([0-9]{4,4})+')
    if not re.fullmatch(regex, field.data):
        raise ValidationError('Only in the form of xxxxxxxx-xxxx')
    
def valid_phonecountrycode(form, field):
    if field.data > 9999:
        raise ValidationError('Too high to be a phone country code')

class new_customer_form(FlaskForm):
    givenname = StringField('Firstname:', validators=[validators.DataRequired(), only_letters, validators.length(min=2, max=30, message="Firstname cannot be less than two letters or more than 30")])
    surname = StringField('Lastname:', validators=[validators.DataRequired(), only_letters, validators.length(min=2, max=30, message="Lastname cannot be less than two letters or more than 30")])
    streetaddress = StringField('Address:', validators=[validators.DataRequired(), valid_adress])
    city = StringField('City:', validators=[validators.DataRequired(), only_letters])
    zipcode = IntegerField('Zipcode:', validators=[validators.DataRequired(), valid_zipcode])
    country = SelectField('Country:', choices=count, validators=[validators.DataRequired()])
    countrycode = HiddenField()
    birthday = DateField('Birthday:', validators=[validators.DataRequired()])
    nationalid = StringField('National ID:' , validators=[validators.DataRequired(), valid_nationalid])
    phonecountrycode = IntegerField('Phone Countrycode:', validators=[validators.DataRequired(),valid_phonecountrycode])
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

class update_user_form(FlaskForm):
    email = EmailField('Email:', validators=[validators.DataRequired()])
    password = PasswordField('Password:', validators=[])
    role = SelectField('Role', choices=[])
    delete_role = SelectField('Role', choices=[])