from datetime import date, datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from model import Transaction, Customer, Account
from flask_mail import Mail, Message
from app import app, db
import sys
import os

migrate = Migrate(app,db)

#min setup på mailtrap
app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '58d9c9a416909a'
app.config['MAIL_PASSWORD'] = '67e4ae70d0ef4b'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)


def last_run(): 
    try:
        with open("lastrundate.txt", "r") as file:
            for line in file:
                date = line.replace("\n", "")
        return date
    except:
        return
    
def date_to_file():
    with open("lastrundate.txt", "w") as file:
        file.write(str(datetime.now()))

def write_to_file(text):
 with open("sendtoemail.txt", "a") as file:
        file.write(text)

def open_new_file():
    with open("sendtoemail.txt", "w") as file:
        return

if __name__  == "__main__":
    with app.app_context():
        # msg = Message('Shady Transactions', sender = '58d9c9a416909a', recipients = ['sweden@testbanken.se'])
        # msg.body = "This is the email body"
        # mail.send(msg)


        upgrade()
        now = datetime.now()

        start = now - timedelta(days = 3)
        then = last_run()
        distinct = [x.Country for x in Customer.query.with_entities(Customer.Country).distinct()]
        for co in distinct:
            msg = Message('Shady Transactions', sender = '58d9c9a416909a', recipients = [f'{co}@testbanken.se'])
            msg.body = ""
            open_new_file()
            for cu in Customer.query.filter_by(Country=co).all():
                for a in Account.query.filter_by(CustomerId=cu.Id).all():
                    big_amount = []
                    transa = []
                    summa = 0
                    for tr in Transaction.query.filter_by(AccountId=a.Id).all():
                        if tr.Amount >= 15000 and str(tr.Date) > last_run():
                            big_amount.append(f"Account: {tr.AccountId} Transaction: {tr.Id} Amount:{tr.Amount}")
                        if str(start) < str(tr.Date) < str(now):
                            summa += tr.Amount
                            transa.append(f"Account: {tr.AccountId} Transaction: {tr.Id} Amount:{tr.Amount}")
                    if summa > 23000 or len(big_amount) != 0:
                        write_to_file(f"Customer: {cu.Id}\n")
                        msg.body += f"Customer: {cu.Id}\n"
                    if len(big_amount) != 0:
                        for big in big_amount:
                            write_to_file("High Transaction:\n" + big + "\n")
                            msg.body += "High Transaction:\n" + big + "\n"
                    if summa > 23000:
                        write_to_file("Transactions over 23000 within 3 days:\n")
                        msg.body += "Transactions over 23000 within 3 days:\n"
                        for tran in transa:
                            write_to_file(tran + "\n" )
                            msg.body += f"{tran}\n"
                        write_to_file("Total:" + str(summa) + "\n")
                        msg.body += "Total:" + str(summa) + "\n"
            if os.path.getsize('sendtoemail.txt') == 0:
                print(f"inget i: {co}")
            else:
                mail.send(msg)
                with open("sendtoemail.txt", "r") as file:
                    for rows in file:
                        print(rows.replace("\n", ""))


        date_to_file()