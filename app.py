from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from flask_security import roles_accepted, auth_required, logout_user, hash_password
from flask_login import current_user
import os
import pycountry
from datetime import datetime

from model import db, seedData, Customer, Account, Transaction, User, user_datastore, Security, Role
from forms import new_customer_form, debit_and_credit_form, transfer_form, new_user_form
 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Nelsonpelson01@localhost/Bank'
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'super secret key')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '1241848918926306')
app.config['REMEMBER_COOKIE_SAMESITE'] = "strict"
app.config['SESSION_COOKIE_SAMESITE'] = "strict"
app.config['SECURITY_REGISTERABLE'] = True
db.app = app
db.init_app(app)
migrate = Migrate(app,db)

api_customer_blueprint = Blueprint('api_customer',__name__)

class Api_Customer_Model:
    id = 0
    GivenName =  ""
    Surname = ""
    Streetaddress = ""
    City = ""
    Zipcode = ""
    Country = ""
    CountryCode = ""
    Birthday = ""
    NationalId = ""
    TelephoneCountryCode = ""
    Telephone = ""
    EmailAddress = ""

def _map_customer_to_api(customer):
    customer_api_model = Api_Customer_Model()
    customer_api_model.id = customer.Id
    customer_api_model.GivenName =  customer.GivenName
    customer_api_model.Surname = customer.Surname
    customer_api_model.Streetaddress = customer.Streetaddress
    customer_api_model.City = customer.City
    customer_api_model.Zipcode = customer.Zipcode
    customer_api_model.Country = customer.Country
    customer_api_model.CountryCode = customer.CountryCode
    customer_api_model.Birthday = customer.Birthday
    customer_api_model.NationalId = customer.NationalId
    customer_api_model.TelephoneCountryCode = customer.TelephoneCountryCode
    customer_api_model.Telephone = customer.Telephone
    customer_api_model.EmailAddress = customer.EmailAddress
    return customer_api_model

@app.route('/api/customer')
def all_customers():
    list_of_all = []
    for customer in Customer.query.all():
        Api_Customer_Model = _map_customer_to_api(customer)
        list_of_all.append(Api_Customer_Model)
    return jsonify([apicustomer.__dict__ for apicustomer in list_of_all])

@app.route('/api/customer/<id>')
def one_customer(id):
    customer = Customer.query.filter_by(Id=id).first()
    Api_Customer_Model = _map_customer_to_api(customer)
    return jsonify(Api_Customer_Model.__dict__)


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
    form = new_customer_form()
    if form.validate_on_submit():
        #spara i databas
        all_customers = Customer.query.all()
        for cus in all_customers:
            if form.nationalid.data == cus.NationalId:
                form.nationalid.errors += ('National ID already exists',)
        if len(form.nationalid.errors) == 0:
            customer = Customer()
            account = Account()
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
            account.AccountType = "Personal"
            account.Created = datetime.now()
            account.Balance = 0
            customer.Accounts.append(account)
            db.session.add(customer)
            db.session.commit()
            flash('Customer Created')
            return redirect("/customers" )
    return render_template("new_customer.html", form=form)

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
            flash('Account Created')
        except:
            a = Account.query.filter_by(Id = request.form['account_id']).first()
            if a.Balance > 0:
                error = 'no_money_alert()'
                # error = 'There is money on this account'
            else:
                db.session.delete(a)
                db.session.commit()
                flash('Account Deleted')
    accounts = Account.query.filter_by(CustomerId=id).all()
    account_count = len(accounts)
    return render_template("customer.html", customer=customer, accounts=accounts, account_count=account_count, error=error)

@app.route("/editcustomer/<int:id>", methods=['GET', 'POST'])
@auth_required()
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
        flash('Customer Edited')
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


@app.route("/customer/<c_id>/<a_id>")
@auth_required()
def account(c_id, a_id):
    account = Account.query.filter_by(Id=a_id).first()
    trans = Transaction.query.filter_by(AccountId=a_id).all()
    return render_template("account.html", account=account, trans=trans)

    
@app.route("/customer/<c_id>/<a_id>/debit", methods=['GET', 'POST'])
@auth_required()
def debit(c_id, a_id):
    error = None
    the_account = Account.query.filter_by(Id=a_id).first()
    accounts = Account.query.filter_by(CustomerId=c_id).all()
    customer = Customer.query.filter_by(Id=c_id).first()
    form = debit_and_credit_form()
    form.account.choices = [(a.Id, a.AccountType) for a in accounts]
    if form.validate_on_submit():
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
        return redirect(url_for('customer', id=c_id))
    if request.method == 'GET':
        form.account.data = str(the_account.Id)
    return render_template("debit.html", customer=customer, error=error, form=form)


@app.route("/customer/<c_id>/<a_id>/credit", methods=['GET', 'POST'])
@auth_required()
def credit(c_id, a_id):
    error = None
    account = Account.query.filter_by(Id=a_id).first()
    accounts = Account.query.filter_by(CustomerId=c_id).all()
    customer = Customer.query.filter_by(Id=c_id).first()
    form = debit_and_credit_form()
    form.account.choices = [(a.Id, a.AccountType) for a in accounts]
    if form.validate_on_submit():
        if form.amount.data > account.Balance:
            form.amount.errors += ('Not enough money on account',)
        else:
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
            return redirect(url_for('customer', id=c_id))
    if request.method == 'GET':
        form.account.data = str(account.Id)
    return render_template("credit.html", customer=customer, error=error, form=form)


@app.route("/customer/<c_id>/<a_id>/transfer", methods=['GET', 'POST'])
@auth_required()
def transfer(c_id, a_id):
    error = None
    accounts = Account.query.filter_by(CustomerId=c_id).all()
    customer = Customer.query.filter_by(Id=c_id).first()
    form = transfer_form()
    form.from_account.choices = [(a.Id, a.AccountType) for a in accounts]
    form.to_account.choices = [(a.Id, a.AccountType) for a in accounts]
    if form.validate_on_submit():
        t1 = Transaction()
        t2 = Transaction()
        a1 = Account.query.filter_by(Id=form.from_account.data, CustomerId=c_id).first()
        a2 = Account.query.filter_by(Id=form.to_account.data, CustomerId=c_id).first()
        if a1 == a2:
            form.from_account.errors += ("Can't transfer to the same account",)
        elif form.amount.data > a1.Balance:
            form.amount.errors += ('Not enough money on account',)
        else:
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
            return redirect(url_for('customer', id=c_id))
    return render_template("transfer.html", customer=customer, error=error, form=form)

@app.route("/adminpage", methods=['GET', 'POST'])
@auth_required()
@roles_accepted("Admin")
def adminpage():
    listOfUsers = [u for u in User.query.all() if u.email != current_user.email]
    if request.method == 'POST':
        app.security.datastore.delete_user(app.security.datastore.find_user(email=request.form['user']))
        app.security.datastore.db.session.commit()
        flash('User Deleted')
        return redirect(url_for('adminpage'))
    return render_template("adminpage.html", listOfUsers=listOfUsers)

@app.route("/register", methods=['GET', 'POST'])
@auth_required()
@roles_accepted("Admin")
def register():
    form = new_user_form()
    roles = Role.query.all()
    form.role.choices = [(r.name, r.name) for r in roles]
    if form.validate_on_submit():
        if not app.security.datastore.find_user(email=form.email.data):
            app.security.datastore.create_user(email=form.email.data, password=hash_password(form.password.data), roles=[form.role.data])
            app.security.datastore.db.session.commit()
            flash('User Registered')
            return redirect(url_for('adminpage'))
        else:
            form.email.errors += ('Email is already in use',)
    return render_template("new_user.html", form=form)



if __name__  == "__main__":
    with app.app_context():
        upgrade()
    
        seedData(app, db)
        app.run(debug=True)

