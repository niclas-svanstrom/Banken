from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify
from flask_security import auth_required
from flask_login import current_user
import pycountry
from datetime import datetime


from model import db, Customer, Account, Transaction
from forms import new_customer_form, debit_and_credit_form, transfer_form



customerBluePrint = Blueprint('customer', __name__)

@customerBluePrint.route("/customers")
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
    if sortColumn == "fname":
        if sortOrder == "asc":
            listOfCustomers = listOfCustomers.order_by(Customer.GivenName.asc())
        else:
            listOfCustomers = listOfCustomers.order_by(Customer.GivenName.desc())
    elif sortColumn == "lname":
        if sortOrder == "asc":
            listOfCustomers = listOfCustomers.order_by(Customer.Surname.asc())
        else:
            listOfCustomers = listOfCustomers.order_by(Customer.Surname.desc())
    elif sortColumn == "nid":
        if sortOrder == "asc":
            listOfCustomers = listOfCustomers.order_by(Customer.NationalId.asc())
        else:
            listOfCustomers = listOfCustomers.order_by(Customer.NationalId.desc())
    elif sortColumn == "address":
        if sortOrder == "asc":
            listOfCustomers = listOfCustomers.order_by(Customer.Streetaddress.asc())
        else:
            listOfCustomers = listOfCustomers.order_by(Customer.Streetaddress.desc())
    elif sortColumn == "city":
        if sortOrder == "asc":
            listOfCustomers = listOfCustomers.order_by(Customer.City.asc())
        else:
            listOfCustomers = listOfCustomers.order_by(Customer.City.desc())
    elif sortColumn == "id":
        if sortOrder == "asc":
            listOfCustomers = listOfCustomers.order_by(Customer.Id.asc())
        else:
            listOfCustomers = listOfCustomers.order_by(Customer.Id.desc())

    paginationObject = listOfCustomers.paginate(page=page, per_page=25, error_out=False)
    return render_template("customer/customers.html", 
                                listOfCustomers=paginationObject.items, 
                                pages = paginationObject.pages, 
                                sortOrder=sortOrder, 
                                has_next=paginationObject.has_next,
                                has_prev=paginationObject.has_prev,
                                page=page,
                                sortColumn=sortColumn, 
                                q=q 
                                )


@customerBluePrint.route("/new_customer", methods=['GET', 'POST'])
# @auth_required()
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
            return redirect(url_for("customer.customers"))
    return render_template("customer/new_customer.html", form=form)

@customerBluePrint.route("/customer/<id>", methods=['GET', 'POST'])
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
    return render_template("customer/customer.html", customer=customer, accounts=accounts, account_count=account_count, error=error)

@customerBluePrint.route("/editcustomer/<int:id>", methods=['GET', 'POST'])
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
        return redirect(url_for("customer.customers"))
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
    return render_template("customer/edit_customer.html", formen=form, customer=customer )

@customerBluePrint.route('/customer/background_process_customer/<c_id>/<a_id>')
def all_transactions(c_id, a_id):
    transactions=[]
    page = int(request.args.get('page',1))
    transac = Transaction.query.filter_by(AccountId=a_id).order_by(Transaction.Date.desc()).paginate(page=page,per_page=10)
    for tr in transac.items:
        t = {"Type":tr.Type, "Operation":tr.Operation, "Amount":tr.Amount, "Date":tr.Date}
        transactions.append(t)
    return jsonify(transactions)

@customerBluePrint.route("/customer/<c_id>/<a_id>")
@auth_required()
def account(c_id, a_id):
    account = Account.query.filter_by(Id=a_id).first()
    trans = Transaction.query.filter_by(AccountId=a_id).all()
    return render_template("customer/account.html", trans=trans, c_id=c_id, account=account)

    
@customerBluePrint.route("/customer/<c_id>/<a_id>/debit", methods=['GET', 'POST'])
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
        return redirect(url_for('customer.customer', id=c_id))
    if request.method == 'GET':
        form.account.data = str(the_account.Id)
    return render_template("customer/debit.html", customer=customer, error=error, form=form)


@customerBluePrint.route("/customer/<c_id>/<a_id>/credit", methods=['GET', 'POST'])
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
            return redirect(url_for('customer.customer', id=c_id))
    if request.method == 'GET':
        form.account.data = str(account.Id)
    return render_template("customer/credit.html", customer=customer, error=error, form=form)


@customerBluePrint.route("/customer/<c_id>/<a_id>/transfer", methods=['GET', 'POST'])
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
            return redirect(url_for('customer.customer', id=c_id))
    return render_template("customer/transfer.html", customer=customer, error=error, form=form)