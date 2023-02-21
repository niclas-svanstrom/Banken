from flask import Flask
from flask_migrate import Migrate, upgrade
import os
from areas.admin.adminPage import adminBluePrint
from areas.customer.customerPage import customerBluePrint
from areas.site.sitePage import siteBluePrint
from areas.api.apiPage import apiBluePrint

from model import db, seedData
 
app = Flask(__name__)
app.config.from_object('config.ConfigDebug')

db.app = app
db.init_app(app)
migrate = Migrate(app,db)

app.register_blueprint(adminBluePrint)
app.register_blueprint(customerBluePrint)
app.register_blueprint(siteBluePrint)
app.register_blueprint(apiBluePrint)




if __name__  == "__main__":
    with app.app_context():
        upgrade()
    
        seedData(app, db)
        app.run(debug=True)

