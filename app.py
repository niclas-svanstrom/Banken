from flask import Flask
from flask_migrate import Migrate, upgrade
from flask_mail import Mail
import os
from flask_security import Security
from areas.admin.adminPage import adminBluePrint
from areas.customer.customerPage import customerBluePrint
from areas.site.sitePage import siteBluePrint
from areas.api.apiPage import apiBluePrint
from model import user_datastore

from model import db, seedData
 
app = Flask(__name__)
app.config.from_object('config.ConfigDebug')
Mail(app)
db.app = app
db.init_app(app)
migrate = Migrate(app,db)
app.security = Security(app, user_datastore)

app.register_blueprint(adminBluePrint)
app.register_blueprint(customerBluePrint)
app.register_blueprint(siteBluePrint)
app.register_blueprint(apiBluePrint)



if __name__  == "__main__":
    with app.app_context():
        upgrade()
    
        seedData(app, db)
        app.run(debug=True)

