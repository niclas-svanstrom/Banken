import unittest
from flask import Flask, render_template, request, url_for, redirect
from app import app
from model import db, Customer, User,Role, Account
from flask_security import Security,SQLAlchemyUserDatastore, hash_password
from sqlalchemy import create_engine
from datetime import datetime

def create_a_customer():
    customer = Customer()
    account1 = Account()
    account2 = Account()
    customer.GivenName =  "Peter"
    customer.Surname = "Pan"
    customer.Streetaddress = "Nånting 1"
    customer.City = "Ingenstans"
    customer.Zipcode = "23477"
    customer.Country = "Ingenstans"
    customer.CountryCode = "IN"
    customer.Birthday = datetime.now()
    customer.NationalId = "19900101-0000"
    customer.TelephoneCountryCode = "47"
    customer.Telephone = "07125585157"
    customer.EmailAddress = "Peter@Pan.com"
    account1.AccountType = "Personal"
    account1.Created = datetime.now()
    account1.Balance = 100
    account2.AccountType = "Personal"
    account2.Created = datetime.now()
    account2.Balance = 100
    customer.Accounts.append(account1)
    customer.Accounts.append(account2)
    db.session.add(customer)
    db.session.commit()

def set_current_user(app, ds, email):
    """Set up so that when request is received,
    the token will cause 'user' to be made the current_user
    """

    def token_cb(request):
        if request.headers.get("Authentication-Token") == "token":
            return ds.find_user(email=email)
        return app.security.login_manager.anonymous_user()

    app.security.login_manager.request_loader(token_cb)


init = False

class FormsTestCases(unittest.TestCase):
    # def __init__(self, *args, **kwargs):
    #     super(FormsTestCases, self).__init__(*args, **kwargs)
    def tearDown(self):
        self.ctx.pop()
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        #self.client = app.test_client()
        app.config["SERVER_NAME"] = "stefan.se"
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['WTF_CSRF_METHODS'] = []  # This is the magic
        app.config['TESTING'] = True
        app.config['LOGIN_DISABLED'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['SECURITY_FRESHNESS_GRACE_PERIOD'] = 123454



        global init
        if not init:
            db.init_app(app)
            db.create_all()
            init = True
            user_datastore = SQLAlchemyUserDatastore(db, User, Role)
            app.security = Security(app, user_datastore,register_blueprint=False)
            app.security.init_app(app, user_datastore,register_blueprint=False)
            app.security.datastore.db.create_all()

   


    def test_when_withdrawing_more_than_balance_should_show_errormessage(self):
        # app.security.datastore.create_role(name="Admin")
        # app.security.datastore.create_user(email="unittest@me.com", password=hash_password("password"), roles=["Admin"])
        # app.security.datastore.commit()
        # set_current_user(app, app.security.datastore, "unittest@me.com")
        test_client = app.test_client()

        create_a_customer()
        customer = Customer.query.get(1)
        with test_client:
            url = f'/customer/{customer.Id}/1/credit'
            response = test_client.post(url, data={ "amount":"200", "account":"1"},  headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"} )
            s = response.data.decode("utf-8") 
            ok = 'Not enough money on account' in s
            self.assertTrue(ok)


    def test_when_credit_minus_amount_should_show_errormessage(self):
        # set_current_user(app, app.security.datastore, "unittest@me.com")
        test_client = app.test_client()
        create_a_customer()
        customer = Customer.query.get(1)
        with test_client:
            url = f'/customer/{customer.Id}/1/credit'
            response = test_client.post(url, data={ "amount":"-100", "account":"1"},  headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"} )
            s = response.data.decode("utf-8") 
            ok = "Can not be lower than 1" in s
            self.assertTrue(ok)

    def test_when_transfering_more_than_balance_should_show_errormessage(self):
        # set_current_user(app, app.security.datastore, "unittest@me.com")
        test_client = app.test_client()
        create_a_customer()
        customer = Customer.query.get(1)
        with test_client:
            url = f'/customer/{customer.Id}/1/transfer'
            response = test_client.post(url, data={ "amount":"200", "from_account":"1", "to_account":"2"},  headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"} )
            s = response.data.decode("utf-8") 
            ok = 'Not enough money on account' in s
            self.assertTrue(ok)


    def test_when_debit_minus_amount_should_show_errormessage(self):
        # set_current_user(app, app.security.datastore, "unittest@me.com")
        test_client = app.test_client()
        with test_client:
            url = '/customer/1/1/debit'
            response = test_client.post(url, data={ "amount":"-100", "account":"1"},  headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"} )
            s = response.data.decode("utf-8") 
            ok = "Can not be lower than 1" in s
            self.assertTrue(ok)

    def test_when_creating_new_customer_name_should_validate_lenght_less_than_two(self):
        test_client = app.test_client()
        with test_client:
            url = '/new_customer'
            response = test_client.post(url, data={ "givenname":"h", "surname":"Pan", "streetaddress":"Nånting 1", "city":"Ingenstans", "zipcode":23477, "Country":"Ingenstans",
                 "CountryCode":"IN", "BirthDay":datetime.now(), "NationalId":"19900101-0000", "TelephoneCountryCode":"47","Telephone":"07125585157", "EmailAddress":"Peter@Pan.com"}, headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"} )
            s = response.data.decode("utf-8") 
            ok = 'Firstname cannot be less than two letters or more than 30' in s
            self.assertTrue(ok)

    def test_when_creating_new_customer_addrees_should_validate_right_form(self):
        test_client = app.test_client()
        with test_client:
            url = '/new_customer'
            response = test_client.post(url, data={ "givenname":"Peter", "surname":"Pan", "streetaddress":"Nånting1", "city":"Ingenstans", "zipcode":23477, "Country":"Ingenstans",
                 "CountryCode":"IN", "BirthDay":datetime.now(), "NationalId":"19900101-0000", "TelephoneCountryCode":"47","Telephone":"07125585157", "EmailAddress":"Peter@Pan.com"}, headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"} )
            s = response.data.decode("utf-8") 
            ok = 'Not a valid address must contain letters, whitespace and at leat one digit' in s
            self.assertTrue(ok)

    def test_when_creating_new_customer_city_validate_only_letters(self):
        test_client = app.test_client()
        with test_client:
            url = '/new_customer'
            response = test_client.post(url, data={ "givenname":"Peter", "surname":"Pan", "streetaddress":"Nånting 1", "city":"Ingenstans2", "zipcode":23477, "Country":"Ingenstans",
                 "CountryCode":"IN", "BirthDay":datetime.now(), "NationalId":"19900101-0000", "TelephoneCountryCode":"47","Telephone":"07125585157", "EmailAddress":"Peter@Pan.com"}, headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"} )
            s = response.data.decode("utf-8") 
            ok = 'Can only be letters' in s
            self.assertTrue(ok)

    def test_when_creating_new_customer_zipcode_validate_minus_digit(self):
        test_client = app.test_client()
        with test_client:
            url = '/new_customer'
            response = test_client.post(url, data={ "givenname":"Peter", "surname":"Pan", "streetaddress":"Nånting 1", "city":"Ingenstans", "zipcode":-23477, "Country":"Ingenstans",
                 "CountryCode":"IN", "BirthDay":datetime.now(), "NationalId":"19900101-0000", "TelephoneCountryCode":"47","Telephone":"07125585157", "EmailAddress":"Peter@Pan.com"}, headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"} )
            s = response.data.decode("utf-8") 
            ok = "Zipcode can not be negative number" in s
            self.assertTrue(ok)
    
    def test_when_creating_new_customer_nationalID_validate_right_form(self):
        test_client = app.test_client()
        with test_client:
            url = '/new_customer'
            response = test_client.post(url, data={ "givenname":"Peter", "surname":"Pan", "streetaddress":"Nånting 1", "city":"Ingenstans", "zipcode":23477, "Country":"Ingenstans",
                    "CountryCode":"IN", "BirthDay":datetime.now(), "nationalid":"199402661231", "TelephoneCountryCode":"47","Telephone":"07125585157", "EmailAddress":"Peter@Pan.com"}, headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"} )
            s = response.data.decode("utf-8") 
            ok = "Only in the form of xxxxxxxx-xxxx" in s
            self.assertTrue(ok)

    def test_when_creating_new_customer_phonenumber_validate_if_plus_right_form(self):
        test_client = app.test_client()
        with test_client:
            url = '/new_customer'
            response = test_client.post(url, data={"phonenumber":"+07125585123"}, headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"} )
            s = response.data.decode("utf-8") 
            ok = "Only phonenumber not with the phonecountrycode" in s
            self.assertTrue(ok)
    
    def test_when_creating_new_customer_phonenumber_validate_if_right_form(self):
        test_client = app.test_client()
        with test_client:
            url = '/new_customer'
            response = test_client.post(url, data={"phonenumber":"071255851asd3"}, headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"} )
            s = response.data.decode("utf-8") 
            ok = "Only digits in phonenumber except for -" in s
            self.assertTrue(ok)

    # def test_when_creating_new_should_be_ok_when_name_is_ok(self):
    #     test_client = app.test_client()
    #     with test_client:
    #         url = '/newcustomer'
    #         response = test_client.post(url, data={ "name":"Kalle.se", "city":"Teststad", "age":"12", "countryCode":"SE", "Amount":"0" },headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"} )
    #         self.assertEqual('302 FOUND', response.status)




if __name__ == "__main__":
    unittest.main()
