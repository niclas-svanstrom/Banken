from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from flask_security import roles_accepted, auth_required, logout_user
import os
import pycountry
from datetime import datetime

from model import db, seedData, Customer, Account, Transaction
from forms import new_customer_form
 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Nelsonpelson01@localhost/Bank'
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'super secret key')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '1241848918926306')
app.config['REMEMBER_COOKIE_SAMESITE'] = "strict"
app.config['SESSION_COOKIE_SAMESITE'] = "strict"
db.app = app
db.init_app(app)
migrate = Migrate(app,db)


# @app.route("/")
# def login():
#     return render_template("login_user.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
@auth_required()
def startpage():
    customers=len(Customer.query.all())
    distinct = [x.Country for x in Customer.query.with_entities(Customer.Country).distinct()]
    total = []
    for c in distinct:
        total.append(len(Customer.query.filter_by(Country=c).all()))
    country_customer={d:t for (d,t) in zip(distinct,total)}
    return render_template("start.html", customers=customers, accounts=len(Account.query.all()), totalsaldo=sum([x.Balance for x in Account.query.all()]), country_customer=country_customer)


@app.route("/country/<c>")
@auth_required()
def country(c):
    class Personas():
        def __init__(self, customer_id, money, name, lastname):
            self.__customer_id = customer_id
            self.__money = money
            self.__name = name
            self.__lastname = lastname
        def get_id(self):
            return self.__customer_id
        def get_money(self):
            return self.__money
        def get_name(self):
            return self.__name
        def get_lastname(self):
            return self.__lastname
    customers= Customer.query.filter_by(Country=c).all()
    list_of_customers = []
    for c in customers:
        accounts = Account.query.filter_by(CustomerId=c.Id).all()
        sum = 0
        for a in accounts:
            sum += a.Balance
        persona = Personas(c.Id,sum,c.GivenName,c.Surname)
        list_of_customers.append(persona)
    list_of_customers.sort(reverse=True, key=lambda x: x.get_money())
    list_of_customers = list_of_customers[:10]
    return render_template("country.html", customers=customers, list_of_customers=list_of_customers)


@app.route("/customers")
@auth_required()
def customers():
    sortColumn = request.args.get('sortColumn', 'namn')
    sortOrder = request.args.get('sortOrder', 'asc')
    q = request.args.get('q', '')
    page = int(request.args.get('page', 1))

    listOfCustomers = Customer.query

    listOfCustomers = listOfCustomers.filter(
        Customer.GivenName.like('%' + q + '%') |
        Customer.City.like('%' + q + '%')
    )
    if sortColumn == "namn":
        if sortOrder == "asc":
            listOfCustomers = listOfCustomers.order_by(Customer.GivenName.asc())
        else:
            listOfCustomers = listOfCustomers.order_by(Customer.GivenName.desc())
    elif sortColumn == "city":
        if sortOrder == "asc":
            listOfCustomers = listOfCustomers.order_by(Customer.City.asc())
        else:
            listOfCustomers = listOfCustomers.order_by(Customer.City.desc())

    paginationObject = listOfCustomers.paginate(page=page, per_page=25, error_out=False)
    return render_template("customers.html", 
                                listOfCustomers=paginationObject.items, 
                                pages = paginationObject.pages, 
                                sortOrder=sortOrder, 
                                has_next=paginationObject.has_next,
                                has_prev=paginationObject.has_prev,
                                page=page,
                                sortColumn=sortColumn, 
                                q=q 
                                )


@app.route("/new_customer", methods=['GET', 'POST'])
@auth_required()
def new_customer():
    error = None
    countries = []
    for country in pycountry.countries:
        c = {country.name:country.name}
        countries.append(c)
    if request.method == 'POST':
        all_customers = Customer.query.all()
        for cus in all_customers:
            if request.form['national_id'] == cus.NationalId:
                error = 'National ID already exists'
        if error == None:
            c = Customer()
            a = Account()
            c.GivenName =  request.form['first_name']
            c.Surname = request.form['last_name']
            c.Streetaddress = request.form['address']
            c.City = request.form['city']
            c.Zipcode = request.form['zipcode']
            c.Country = request.form['country']
            c.CountryCode = pycountry.countries.get(name=request.form['country']).alpha_2
            c.Birthday = request.form['birth']
            c.NationalId = request.form['national_id']
            c.TelephoneCountryCode = request.form['phone_code']
            c.Telephone = request.form['phone_number']
            c.EmailAddress = request.form['email']
            start = datetime.now()
            a.AccountType = "Personal"
            a.Created = start
            a.Balance = 0
            c.Accounts.append(a)
            db.session.add(c)
            db.session.commit()
            return redirect(url_for('startpage'))

    return render_template("new_customer.html", countries=countries, error=error)

@app.route("/customer/<id>", methods=['GET', 'POST'])
@auth_required()
def customer(id):
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
        except:
            a = Account.query.filter_by(Id = request.form['account_id']).first()
            if a.Balance > 0:
                error = 'no_money_alert()'
                # error = 'There is money on this account'
            else:
                db.session.delete(a)
                db.session.commit()
    accounts = Account.query.filter_by(CustomerId=id).all()
    account_count = len(accounts)
    return render_template("customer.html", customer=customer, accounts=accounts, account_count=account_count, error=error)

@app.route("/editcustomer/<int:id>", methods=['GET', 'POST'])
def editcustomer(id):
    customer = Customer.query.filter_by(Id=id).first()
    form = new_customer_form()
    if form.validate_on_submit():
        #spara i databas
        customer.GivenName =  form.givenname.data
        customer.Surname = form.surname.data
        customer.Streetaddress = form.streetaddress.data
        customer.City = form.city.data
        customer.Zipcode = form.zipcode.data
        customer.Country = form.country.data
        customer.CountryCode = pycountry.countries.get(name=form.country.data).alpha_2
        customer.Birthday = form.birthday.data
        customer.NationalId = form.nationalid.data
        customer.TelephoneCountryCode = form.phonecountrycode.data
        customer.Telephone = form.phonenumber.data
        customer.EmailAddress = form.email.data
        customer.verified = True
        db.session.commit()
        return redirect("/customers" )
    if request.method == 'GET':
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
    return render_template("edit_customer.html", formen=form )

@app.route("/new_account/<id>")
@auth_required()
def new_account(id):
    accounts = Account.query.filter_by(CustomerId=id).all()
    customer = Customer.query.filter_by(Id=id).first()
    account_count = len(accounts)
    return render_template("new_account.html", customer=customer, accounts=accounts, account_count=account_count)


@app.route("/customer/<c_id>/<a_id>")
@auth_required()
def account(c_id, a_id):
    account = Account.query.filter_by(Id=a_id).first()
    trans = Transaction.query.filter_by(AccountId=a_id).all()
    return render_template("account.html", account=account, trans=trans)

    
@app.route("/customer/<c_id>/<a_id>/debit", methods=['GET', 'POST'])
@auth_required()
def debit(c_id, a_id):
    account = Account.query.filter_by(Id=a_id).first()
    accounts = Account.query.filter_by(CustomerId=c_id).all()
    trans = Transaction.query.filter_by(AccountId=a_id).all()
    customer = Customer.query.filter_by(Id=c_id).first()
    if request.method == 'POST':
        t = Transaction()
        a = Account.query.filter_by(AccountType=request.form['account'], CustomerId=c_id).first()
        if request.form['sum'] < 0:
            error = 'Can not be less than 0'
        else:
            a.Balance = a.Balance + int(request.form['sum'])
            t.Type = "Debit"
            t.Operation = "Deposit cash"
            t.Date = datetime.now()
            t.Amount = request.form['sum']
            t.NewBalance = a.Balance
            t.AccountId = a.Id
            db.session.add(t)
            db.session.commit()
            return redirect(url_for('customer', id=c_id))
    return render_template("debit.html", account=account, trans=trans, accounts=accounts, customer=customer, error=error)


@app.route("/customer/<c_id>/<a_id>/credit", methods=['GET', 'POST'])
@auth_required()
def credit(c_id, a_id):
    error = None
    account = Account.query.filter_by(Id=a_id).first()
    accounts = Account.query.filter_by(CustomerId=c_id).all()
    trans = Transaction.query.filter_by(AccountId=a_id).all()
    customer = Customer.query.filter_by(Id=c_id).first()
    if request.method == 'POST':
        t = Transaction()
        a = Account.query.filter_by(AccountType=request.form['account'], CustomerId=c_id).first()
        if request.form['sum'] > a.Balance:
            error = 'Not enough money on account'
        elif request.form['sum'] < 0:
            error = 'Can not be less than 0'
        else:
            a.Balance = a.Balance - int(request.form['sum'])
            t.Type = "Debit"
            t.Operation = "Deposit cash"
            t.Date = datetime.now()
            t.Amount = request.form['sum']
            t.NewBalance = a.Balance
            t.AccountId = a.Id
            db.session.add(t)
            db.session.commit()
            return redirect(url_for('customer', id=c_id))
    return render_template("credit.html", account=account, trans=trans, accounts=accounts, customer=customer, error=error)


@app.route("/customer/<c_id>/<a_id>/transfer", methods=['GET', 'POST'])
@auth_required()
def transfer(c_id, a_id):
    error = None
    account = Account.query.filter_by(Id=a_id).first()
    accounts = Account.query.filter_by(CustomerId=c_id).all()
    trans = Transaction.query.filter_by(AccountId=a_id).all()
    customer = Customer.query.filter_by(Id=c_id).first()
    if request.method == 'POST':
        t1 = Transaction()
        t2 = Transaction()
        a1 = Account.query.filter_by(AccountType=request.form['from_account'], CustomerId=c_id).first()
        a2 = Account.query.filter_by(AccountType=request.form['to_account'], CustomerId=c_id).first()
        if a1 == a2:
            error = 'Can not transfer the same account'
        elif request.form['sum'] > a1.Balance:
            error = 'Not enough money on account'
        else:
            a1.Balance = a1.Balance - int(request.form['sum'])
            a2.Balance = a2.Balance + int(request.form['sum'])
            t1.Type = "Credit"
            t1.Operation = "Transfer"
            t1.Date = datetime.now()
            t1.Amount = request.form['sum']
            t1.NewBalance = a1.Balance
            t1.AccountId = a1.Id
            t2.Type = "Debit"
            t2.Operation = "Transfer"
            t2.Date = datetime.now()
            t2.Amount = request.form['sum']
            t2.NewBalance = a2.Balance
            t2.AccountId = a2.Id
            db.session.add(t1)
            db.session.add(t2)
            db.session.commit()
            return redirect(url_for('customer', id=c_id))
    return render_template("transfer.html", account=account, trans=trans, accounts=accounts, customer=customer, error=error)



if __name__  == "__main__":
    with app.app_context():
        upgrade()
    
        seedData(app, db)
        app.run(debug=True)

