from flask import request, flash
from model import Customer, Account, Transaction, db
import pycountry
from datetime import datetime

def sort_what_column(sort_column,sort_order,q):
    list_of_customers = Customer.query

    list_of_customers = list_of_customers.filter(
        Customer.GivenName.like('%' + q + '%') |
        Customer.City.like('%' + q + '%')
    )
    if sort_column == "GivenName":
        if sort_order == "asc":
            list_of_customers = list_of_customers.order_by(Customer.GivenName.asc())
        else:
            list_of_customers = list_of_customers.order_by(Customer.GivenName.desc())
    elif sort_column == "Surname":
        if sort_order == "asc":
            list_of_customers = list_of_customers.order_by(Customer.Surname.asc())
        else:
            list_of_customers = list_of_customers.order_by(Customer.Surname.desc())
    elif sort_column == "NationalId":
        if sort_order == "asc":
            list_of_customers = list_of_customers.order_by(Customer.NationalId.asc())
        else:
            list_of_customers = list_of_customers.order_by(Customer.NationalId.desc())
    elif sort_column == "Streetaddress":
        if sort_order == "asc":
            list_of_customers = list_of_customers.order_by(Customer.Streetaddress.asc())
        else:
            list_of_customers = list_of_customers.order_by(Customer.Streetaddress.desc())
    elif sort_column == "City":
        if sort_order == "asc":
            list_of_customers = list_of_customers.order_by(Customer.City.asc())
        else:
            list_of_customers = list_of_customers.order_by(Customer.City.desc())
    elif sort_column == "Id":
        if sort_order == "asc":
            list_of_customers = list_of_customers.order_by(Customer.Id.asc())
        else:
            list_of_customers = list_of_customers.order_by(Customer.Id.desc())
    return list_of_customers

def new_customer_service(form):
        customer = Customer()
        account = Account()
        customer.GivenName =  form.givenname.data
        customer.Surname = form.surname.data
        customer.Streetaddress = form.streetaddress.data
        customer.City = form.city.data
        customer.Zipcode = form.zipcode.data
        customer.Country = form.country.data
        if form.country.data == 'USA':
            customer.CountryCode = pycountry.countries.get(name='United States').alpha_2
        else:
            customer.CountryCode = pycountry.countries.get(name=form.country.data).alpha_2
        customer.Birthday = form.birthday.data
        customer.NationalId = form.nationalid.data
        customer.TelephoneCountryCode = form.phonecountrycode.data
        customer.Telephone = form.phonenumber.data.replace(" ","")
        customer.EmailAddress = form.email.data
        account.AccountType = "Personal"
        account.Created = datetime.now()
        account.Balance = 0
        customer.Accounts.append(account)
        db.session.add(customer)
        db.session.commit()

def check_if_customer_exists(form):
    all_customers = Customer.query.all()
    for cus in all_customers:
        if form.nationalid.data == cus.NationalId:
            form.nationalid.errors += ('National ID already exists',)
        elif form.email.data == cus.EmailAddress:
            form.email.errors += ('Email already exists',)


def customer_delete_or_create_account(id):
    error = None
    customer = Customer.query.filter_by(Id=id).first()
    if request.method == 'POST':
        try:
            a = Account()
            a.AccountType = request.form['account_type']
            a.Created = datetime.now()
            a.Balance = 0
            customer.Accounts.append(a)
            db.session.commit()
            flash('Account Created')
        except:
            a = Account.query.filter_by(Id = request.form['account_id']).first()
            if a.Balance > 0:
                error = 'no_money_alert()'
            else:
                db.session.delete(a)
                db.session.commit()
                flash('Account Deleted')
    return error

def check_if_update_possible(customer,form):
    all_customers = Customer.query.all()
    for cus in all_customers:
        if cus.NationalId == customer.NationalId:
            pass
        elif cus.EmailAddress == customer.EmailAddress:
            pass
        else:
            if form.nationalid.data == cus.NationalId:
                form.nationalid.errors += ('National ID already exists',)
            elif form.email.data == cus.EmailAddress:
                form.email.errors += ('Email already exists',)


def update_customer(customer,form):
    customer.GivenName =  form.givenname.data
    customer.Surname = form.surname.data
    customer.Streetaddress = form.streetaddress.data
    customer.City = form.city.data
    customer.Zipcode = form.zipcode.data
    customer.Country = form.country.data
    if form.country.data == 'USA':
        customer.CountryCode = pycountry.countries.get(name='United States').alpha_2
    else:
        customer.CountryCode = pycountry.countries.get(name=form.country.data).alpha_2
    customer.Birthday = form.birthday.data
    customer.NationalId = form.nationalid.data
    customer.TelephoneCountryCode = form.phonecountrycode.data
    customer.Telephone = form.phonenumber.data.replace(" ","")
    customer.EmailAddress = form.email.data
    customer.verified = True
    db.session.commit()
    flash('Customer Edited')

def insert_customer_values(customer,form):
    form.givenname.data = customer.GivenName
    form.surname.data = customer.Surname
    form.streetaddress.data = customer.Streetaddress
    form.city.data = customer.City
    form.zipcode.data = customer.Zipcode
    form.country.data = customer.Country
    form.countrycode.data = customer.CountryCode
    form.birthday.data = customer.Birthday
    form.nationalid.data = customer.NationalId
    form.phonecountrycode.data = customer.TelephoneCountryCode
    form.phonenumber.data = customer.Telephone
    form.email.data = customer.EmailAddress

def debit_func(form,c_id):
    t = Transaction()
    a = Account.query.filter_by(Id=form.account.data, CustomerId=c_id).first()
    a.Balance = a.Balance + form.amount.data
    t.Type = "Debit"
    t.Operation = "Deposit cash"
    t.Date = datetime.now()
    t.Amount = form.amount.data
    t.NewBalance = a.Balance
    t.AccountId = a.Id
    db.session.add(t)
    db.session.commit()
    flash('Debit Completed')

def credit_func(form,c_id):
    t = Transaction()
    a = Account.query.filter_by(Id=form.account.data, CustomerId=c_id).first()
    a.Balance = a.Balance - form.amount.data
    t.Type = "Credit"
    t.Operation = "Bank withdrawal"
    t.Date = datetime.now()
    t.Amount = form.amount.data
    t.NewBalance = a.Balance
    t.AccountId = a.Id
    db.session.add(t)
    db.session.commit()
    flash('Credit Completed')

def transfer_func(form,a1,a2,t1,t2):
    a1.Balance = a1.Balance - form.amount.data
    a2.Balance = a2.Balance + form.amount.data
    t1.Type = "Credit"
    t1.Operation = "Transfer"
    t1.Date = datetime.now()
    t1.Amount = form.amount.data
    t1.NewBalance = a1.Balance
    t1.AccountId = a1.Id
    t2.Type = "Debit"
    t2.Operation = "Transfer"
    t2.Date = datetime.now()
    t2.Amount = form.amount.data
    t2.NewBalance = a2.Balance
    t2.AccountId = a2.Id
    db.session.add(t1)
    db.session.add(t2)
    db.session.commit()
    flash('Transfer Completed')