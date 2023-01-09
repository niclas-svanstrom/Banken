from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade

from model import db, seedData, Customer

 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Nelsonpelson01@localhost/Bank'
db.app = app
db.init_app(app)
migrate = Migrate(app,db)
 
 

@app.route("/")
def startpage():
    return "Hej"
    # trendingCategories = Category.query.all()
    # return render_template("index.html", trendingCategories=trendingCategories)

@app.route("/customers")
def customers():
    customers = Customer.query.all()
    return render_template("customers.html", customers=customers)

@app.route("/customer/<id>")
def customer(id):
    customer = Customer.query.filter_by(Id=id).first()
    return render_template("customer.html", customer=customer)

@app.route("/category/<id>")
def category(id):
    return "Hej2"
    # products = Product.query.all()
    # return render_template("category.html", products=products)


if __name__  == "__main__":
    with app.app_context():
        upgrade()
    
        seedData(db)
        app.run()

