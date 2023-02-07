from datetime import date, datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from model import Transaction, Customer, Account
from app import app, db
import sys
import os

migrate = Migrate(app,db)


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
        file.write(str(date.today()))

def write_to_file(text):
 with open("sendtoemail.txt", "a") as file:
        file.write(text)

def open_new_file():
    with open("sendtoemail.txt", "w") as file:
        return

if __name__  == "__main__":
    with app.app_context():
        upgrade()
        now = date.today()
        # if last_run() == str(now):
        #     sys.exit()

        start = now - timedelta(days = 3)
        then = last_run()
        print(start)
        distinct = [x.Country for x in Customer.query.with_entities(Customer.Country).distinct()]
        for co in distinct:
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
                    if len(big_amount) != 0:
                        for big in big_amount:
                            write_to_file("High Transaction:\n" + big + "\n")
                    if summa > 23000:
                        write_to_file("Transactions over 23000 within 3days:\n")
                        for tran in transa:
                            write_to_file(tran + "\n" )
                        write_to_file("Total:" + str(summa) + "\n")
            if os.path.getsize('sendtoemail.txt') == 0:
                print(f"inget i: {co}")
            else:
                with open("sendtoemail.txt", "r") as file:
                    for rows in file:
                        print(rows.replace("\n", ""))

        # for t in Transaction.query.all():
        #     if str(t.Date) > "2017-01-01":
        #         print(f"{t.Type} {t.Date} {t.AccountId}")


        date_to_file()