from flask import render_template, redirect, Blueprint, current_app
from flask_security import auth_required, logout_user, check_and_update_authn_fresh
from datetime import timedelta

from model import Customer, Account


siteBluePrint = Blueprint('site', __name__)

@siteBluePrint.route("/logout")
def logout():
    logout_user()
    return redirect("/")



@siteBluePrint.route("/")
@auth_required()
def startpage():
    customers=len(Customer.query.all())
    distinct = [x.Country for x in Customer.query.with_entities(Customer.Country).distinct()]
    total = []
    for c in distinct:
        total.append(len(Customer.query.filter_by(Country=c).all()))
    country_customer={d:t for (d,t) in zip(distinct, total)}
    return render_template("site/start.html", customers=customers, accounts=len(Account.query.all()), totalsaldo=sum([x.Balance for x in Account.query.all()]), country_customer=country_customer)


@siteBluePrint.route("/country/<c>")
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
    return render_template("site/country.html", customers=customers, list_of_customers=list_of_customers)