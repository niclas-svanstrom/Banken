from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
import pycountry
from datetime import datetime

from model import db, seedData, Customer, Account, Transaction, Users

 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Nelsonpelson01@localhost/Bank'
app.config['SECRET_KEY'] = 'super secret key'
db.app = app
db.init_app(app)
migrate = Migrate(app,db)
 

@app.route("/", methods=['GET', 'POST'])
def login():
    error = None
    users = Users.query.all()
    if request.method == 'POST':
        for us in users:
            if request.form['username'] == us.EmailAddress and request.form['password'] == us.Password:
                session['loggedin'] = True
                session['username'] = request.form['username']
                session['password'] = request.form['password']
                return redirect(url_for('startpage'))
        error = 'Invalid Credentials. Please try Again'
    return render_template("login.html", error=error)

@app.route("/startpage/logout")
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('login'))


@app.route("/startpage")
def startpage():
    customers=len(Customer.query.all())
    user = Users.query.filter_by(EmailAddress = session['username']).first()
    distinct = [x.Country for x in Customer.query.with_entities(Customer.Country).distinct()]
    total = []
    for c in distinct:
        total.append(len(Customer.query.filter_by(Country=c).all()))
    country_customer={d:t for (d,t) in zip(distinct,total)}
    if 'loggedin' in session:
        return render_template("start.html", user=user, customers=customers, accounts=len(Account.query.all()), totalsaldo=sum([x.Balance for x in Account.query.all()]), country_customer=country_customer)
    else:
        return redirect(url_for('login'))

@app.route("/customers")
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
    if 'loggedin' in session:
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
    else:
        return redirect(url_for('login'))

@app.route("/new_customer", methods=['GET', 'POST'])
def new_customer():
    error = None
    countries = []
    for country in pycountry.countries:
        countries.append(country.name)
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
    if 'loggedin' in session:
        return render_template("new_customer.html", countries=countries, error=error)
    else:
        return redirect(url_for('login'))

@app.route("/customer/<id>")
def customer(id):
    accounts = Account.query.filter_by(CustomerId=id).all()
    customer = Customer.query.filter_by(Id=id).first()
    account_count = len(accounts)
    if 'loggedin' in session:
        return render_template("customer.html", customer=customer, accounts=accounts, account_count=account_count)
    else:
        return redirect(url_for('login'))

@app.route("/customer/<c_id>/<a_id>")
def account(c_id, a_id):
    account = Account.query.filter_by(Id=a_id).first()
    trans = Transaction.query.filter_by(AccountId=a_id).all()
    if 'loggedin' in session:
        return render_template("account.html", account=account, trans=trans)
    else:
        return redirect(url_for('login'))
    
@app.route("/customer/<c_id>/<a_id>/debit", methods=['GET', 'POST'])
def debit(c_id, a_id):
    account = Account.query.filter_by(Id=a_id).first()
    accounts = Account.query.filter_by(CustomerId=c_id).all()
    trans = Transaction.query.filter_by(AccountId=a_id).all()
    customer = Customer.query.filter_by(Id=c_id).first()
    if request.method == 'POST':
        t = Transaction()
        a = Account.query.filter_by(AccountType=request.form['account'], CustomerId=c_id).first()
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
    if 'loggedin' in session:
        return render_template("debit.html", account=account, trans=trans, accounts=accounts, customer=customer)
    else:
        return redirect(url_for('login'))

@app.route("/customer/<c_id>/<a_id>/credit", methods=['GET', 'POST'])
def credit(c_id, a_id):
    account = Account.query.filter_by(Id=a_id).first()
    accounts = Account.query.filter_by(CustomerId=c_id).all()
    trans = Transaction.query.filter_by(AccountId=a_id).all()
    customer = Customer.query.filter_by(Id=c_id).first()
    if request.method == 'POST':
        t = Transaction()
        a = Account.query.filter_by(AccountType=request.form['account'], CustomerId=c_id).first()
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
    if 'loggedin' in session:
        return render_template("credit.html", account=account, trans=trans, accounts=accounts, customer=customer)
    else:
        return redirect(url_for('login'))

@app.route("/customer/<c_id>/<a_id>/transfer")
def transfer(c_id, a_id):
    account = Account.query.filter_by(Id=a_id).first()
    accounts = Account.query.filter_by(CustomerId=c_id).all()
    trans = Transaction.query.filter_by(AccountId=a_id).all()
    customer = Customer.query.filter_by(Id=c_id).first()
    if 'loggedin' in session:
        return render_template("transfer.html", account=account, trans=trans, accounts=accounts, customer=customer)
    else:
        return redirect(url_for('login'))


if __name__  == "__main__":
    with app.app_context():
        # upgrade()
    
        seedData(db)
        app.run(debug=True)

