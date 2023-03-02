from flask import Flask, session, redirect
from flask_migrate import Migrate, upgrade
from flask_mail import Mail
from flask_security import Security
from areas.admin.adminPage import adminBluePrint
from areas.customer.customerPage import customerBluePrint
from areas.site.sitePage import siteBluePrint
from areas.api.apiPage import apiBluePrint
from model import user_datastore, Transaction, Customer, Account
from datetime import timedelta, datetime

from flask_apscheduler import APScheduler
from consoleapp.consoleapp import check_email

from model import db, seedData

app = Flask(__name__)
app.config.from_object('config.ConfigDebug')
Mail(app)
db.app = app
db.init_app(app)
migrate = Migrate(app,db)
app.security = Security(app, user_datastore)            #had to move this here from model to make azure deploy work

app.register_blueprint(adminBluePrint)
app.register_blueprint(customerBluePrint)
app.register_blueprint(siteBluePrint)
app.register_blueprint(apiBluePrint)

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=20)



scheduler = APScheduler()

def scheduleTask():
    check_email(app, Transaction, Customer, Account)

today = datetime(datetime.now().year,datetime.now().month,datetime.now().day, 22, 00, 00)

if __name__  == "__main__":
    scheduler.add_job(id = 'Scheduled Task', func=scheduleTask, start_date=today, trigger="interval", hours=24)
    scheduler.start()
    with app.app_context():
        upgrade()
    
        seedData(app, db)
        app.run()

