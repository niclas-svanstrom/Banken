from datetime import datetime, timedelta
from flask_migrate import upgrade
# from model import Transaction, Customer, Account
from flask_mail import Mail, Message
# from app import app
import os


# app.config.from_object('config.ConfigDebug')

# mail = Mail(app)


def last_run(): 
    try:
        with open("consoleapp/lastrundate.txt", "r") as file:
            for line in file:
                date = line.replace("\n", "")
        return date
    except:
        return str(datetime.now() - timedelta(hours = 72))
    
def date_to_file():
    with open("consoleapp/lastrundate.txt", "w") as file:
        file.write(str(datetime.now()))

def write_to_file(text):
 with open("consoleapp/sendtoemail.txt", "a") as file:
        file.write(text)

def open_new_file():
    with open("consoleapp/sendtoemail.txt", "w") as file:
        return

#made so that the program also creates a txt file to write what it sends to email to show my teacher that it is working, but it is also good so that if i want i can send
#it in the email, it replaces everytime a new country has some shady transactions tho but i will also write out in the terminal what it have found :)

# if __name__  == "__main__":
def check_for_shady_transactions(app, Transaction, Customer, Account):
    with app.app_context():
    #     upgrade()
        now = datetime.now()

        start = now - timedelta(hours = 72)
        distinct = [x.Country for x in Customer.query.with_entities(Customer.Country).distinct()]
        for co in distinct:
            msg = Message('Shady Transactions', sender = '58d9c9a416909a', recipients = [f'{co}@testbanken.se'])
            msg.body = ""
            open_new_file()
            for cu in Customer.query.filter_by(Country=co).all():
                for a in Account.query.filter_by(CustomerId=cu.Id).all():
                    big_amount = []
                    transactions = []
                    sum = 0
                    for tr in Transaction.query.filter_by(AccountId=a.Id).filter(Transaction.Date > start).all():
                        if tr.Amount >= 15000 and str(tr.Date) > last_run():
                            big_amount.append(f"Account: {tr.AccountId} Transaction: {tr.Id} Amount:{tr.Amount}")
                        sum += tr.Amount
                        transactions.append(f"Account: {tr.AccountId} Transaction: {tr.Id} Amount:{tr.Amount}")
                    if sum > 23000 or len(big_amount) != 0:
                        write_to_file(f"Customer: {cu.Id}\n")
                        msg.body += f"Customer: {cu.Id}\n"
                    if len(big_amount) != 0:
                        for big in big_amount:
                            write_to_file("High Transaction:\n" + big + "\n")
                            msg.body += "High Transaction:\n" + big + "\n"
                    if sum > 23000:
                        write_to_file("Transactions over 23000 within 72 hours:\n")
                        msg.body += "Transactions over 23000 within 72 hours:\n"
                        for tran in transactions:
                            write_to_file(tran + "\n" )
                            msg.body += f"{tran}\n"
                        write_to_file("Total:" + str(sum) + "\n")
                        msg.body += "Total:" + str(sum) + "\n"
            if os.path.getsize('consoleapp/sendtoemail.txt') == 0:
                print(f"inget i: {co}")
            else:
                # mail = Mail(app)
                # mail.send(msg)
                with open("consoleapp/sendtoemail.txt", "r") as file:
                    for rows in file:
                        print(rows.replace("\n", ""))
        date_to_file()