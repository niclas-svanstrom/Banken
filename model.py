from flask_sqlalchemy import SQLAlchemy
import barnum
import random
from datetime import datetime  
from datetime import timedelta  

db = SQLAlchemy()

class Users(db.Model):
    __tablename__= "Users"
    Id = db.Column(db.Integer, primary_key=True)
    EmailAddress = db.Column(db.String(50), unique=False, nullable=False)
    Password = db.Column(db.String(20), unique=False, nullable=False)
    GivenName = db.Column(db.String(50), unique=False, nullable=False)
    Surname = db.Column(db.String(50), unique=False, nullable=False)
    RoleId = db.Column(db.Integer, db.ForeignKey('Role.Id'), nullable=False)

class Role(db.Model):
    __tablename__= "Role"
    Id = db.Column(db.Integer, primary_key=True)
    Role = db.Column(db.String(10), unique=False, nullable=False)
    User_Role = db.relationship('Users', backref='Role',
     lazy=True)

class Customer(db.Model):
    __tablename__= "Customers"
    Id = db.Column(db.Integer, primary_key=True)
    GivenName = db.Column(db.String(50), unique=False, nullable=False)
    Surname = db.Column(db.String(50), unique=False, nullable=False)
    Streetaddress = db.Column(db.String(50), unique=False, nullable=False)
    City = db.Column(db.String(50), unique=False, nullable=False)
    Zipcode = db.Column(db.String(10), unique=False, nullable=False)
    Country = db.Column(db.String(30), unique=False, nullable=False)
    CountryCode = db.Column(db.String(2), unique=False, nullable=False)
    Birthday = db.Column(db.DateTime, unique=False, nullable=False)
    NationalId = db.Column(db.String(20), unique=False, nullable=False)
    TelephoneCountryCode = db.Column(db.Integer, unique=False, nullable=False)
    Telephone = db.Column(db.String(20), unique=False, nullable=False)
    EmailAddress = db.Column(db.String(50), unique=False, nullable=False)

    Accounts = db.relationship('Account', backref='Customer',
     lazy=True)

class Account(db.Model):
    __tablename__= "Accounts"
    Id = db.Column(db.Integer, primary_key=True)
    AccountType = db.Column(db.String(10), unique=False, nullable=False)
    Created = db.Column(db.DateTime, unique=False, nullable=False)
    Balance = db.Column(db.Integer, unique=False, nullable=False)
    Transactions = db.relationship('Transaction', backref='Account',
     lazy=True)
    CustomerId = db.Column(db.Integer, db.ForeignKey('Customers.Id'), nullable=False)


class Transaction(db.Model):
    __tablename__= "Transactions"
    Id = db.Column(db.Integer, primary_key=True)
    Type = db.Column(db.String(20), unique=False, nullable=False)
    Operation = db.Column(db.String(50), unique=False, nullable=False)
    Date = db.Column(db.DateTime, unique=False, nullable=False)
    Amount = db.Column(db.Integer, unique=False, nullable=False)
    NewBalance = db.Column(db.Integer, unique=False, nullable=False)
    AccountId = db.Column(db.Integer, db.ForeignKey('Accounts.Id'), nullable=False)



def seedData(db):
    count = Role.query.count()
    if count < 2:
        role1 = Role()
        role1.Role = "Admin"
        db.session.add(role1)
        db.session.commit()
        role2 = Role()
        role2.Role = "Cashier"
        db.session.add(role2)
        db.session.commit()
        count += 1

    users = Users.query.all()
    user1 = ["stefan.holmberg@systementor.se", "Hejsan123#", "Stefan", "Holmberg", 1]
    user2 = ["stefan.holmberg@nackademin.se", "Hejsan123#", "Stefan", "Holmberg", 2]
    user3 = ["niclas.svanstrom@hotmail.com", "password", "Niclas", "Svanström", 1]
    userlist = {1:user1,2:user2,3:user3}
    current = []
    for us in users:
        current.append(us.EmailAddress)
    for u1 in userlist.values():
        if u1[0] in current:
            continue
        else:
            user = Users()
            user.EmailAddress = u1[0]
            user.Password = u1[1]
            user.GivenName = u1[2]
            user.Surname = u1[3]
            user.RoleId = u1[4]
            db.session.add(user)
            db.session.commit()



    antal =  Customer.query.count()
    while antal < 500:
        customer = Customer()
        
        customer.GivenName, customer.Surname = barnum.create_name()

        customer.Streetaddress = barnum.create_street()
        customer.Zipcode, customer.City, _  = barnum.create_city_state_zip()
        customer.Country = "USA"
        customer.CountryCode = "US"
        customer.Birthday = barnum.create_birthday()
        n = barnum.create_cc_number()
        customer.NationalId = customer.Birthday.strftime("%Y%m%d-") + n[1][0][0:4]
        customer.TelephoneCountryCode = 55
        customer.Telephone = barnum.create_phone()
        customer.EmailAddress = barnum.create_email().lower()

        for x in range(random.randint(1,4)):
            account = Account()

            c = random.randint(0,100)
            if c < 33:
                account.AccountType = "Personal"    
            elif c < 66:
                account.AccountType = "Checking"    
            else:
                account.AccountType = "Savings"    


            start = datetime.now() + timedelta(days=-random.randint(1000,10000))
            account.Created = start
            account.Balance = 0
            
            for n in range(random.randint(0,30)):
                belopp = random.randint(0,30)*100
                tran = Transaction()
                start = start+ timedelta(days=-random.randint(10,100))
                if start > datetime.now():
                    break
                tran.Date = start
                account.Transactions.append(tran)
                tran.Amount = belopp
                if account.Balance - belopp < 0:
                    tran.Type = "Debit"
                else:
                    if random.randint(0,100) > 70:
                        tran.Type = "Debit"
                    else:
                        tran.Type = "Credit"

                r = random.randint(0,100)
                if tran.Type == "Debit":
                    account.Balance = account.Balance + belopp
                    if r < 20:
                        tran.Operation = "Deposit cash"
                    elif r < 66:
                        tran.Operation = "Salary"
                    else:
                        tran.Operation = "Transfer"
                else:
                    account.Balance = account.Balance - belopp
                    if r < 40:
                        tran.Operation = "ATM withdrawal"
                    if r < 75:
                        tran.Operation = "Payment"
                    elif r < 85:
                        tran.Operation = "Bank withdrawal"
                    else:
                        tran.Operation = "Transfer"

                tran.NewBalance = account.Balance


            customer.Accounts.append(account)

        db.session.add(customer)
        db.session.commit()
        
        antal = antal + 1


