from flask import Blueprint, jsonify, request, render_template
from model import Customer

apiBluePrint = Blueprint('api', __name__)

class Api_Customer_Model:
    id = 0
    GivenName =  ""
    Surname = ""
    Streetaddress = ""
    City = ""
    Zipcode = ""
    Country = ""
    CountryCode = ""
    Birthday = ""
    NationalId = ""
    TelephoneCountryCode = ""
    Telephone = ""
    EmailAddress = ""

def _map_customer_to_api(customer):
    customer_api_model = Api_Customer_Model()
    customer_api_model.id = customer.Id
    customer_api_model.GivenName =  customer.GivenName
    customer_api_model.Surname = customer.Surname
    customer_api_model.Streetaddress = customer.Streetaddress
    customer_api_model.City = customer.City
    customer_api_model.Zipcode = customer.Zipcode
    customer_api_model.Country = customer.Country
    customer_api_model.CountryCode = customer.CountryCode
    customer_api_model.Birthday = customer.Birthday
    customer_api_model.NationalId = customer.NationalId
    customer_api_model.TelephoneCountryCode = customer.TelephoneCountryCode
    customer_api_model.Telephone = customer.Telephone
    customer_api_model.EmailAddress = customer.EmailAddress
    return customer_api_model

@apiBluePrint.route("/api/customers")
def api_customerpage():
    customers = all_customers()
    return render_template("customer/apicustomers.html", customers=customers)

@apiBluePrint.route('/api/background_process_customer')
def all_customers():
    customers=[]
    page = int(request.args.get('page',1))
    custs = Customer.query.order_by(Customer.Id.desc()).paginate(page=page,per_page=10)
    for cust in custs.items:
        c = { "Id": cust.Id, "NationalId":cust.NationalId, "Firstname":cust.GivenName, "Lastname":cust.Surname, "Address":cust.Streetaddress, "City":cust.City }
        customers.append(c)
    return jsonify(customers)

@apiBluePrint.route('/api/customer/<id>')
def one_customer(id):
    customer = Customer.query.filter_by(Id=id).first()
    Api_Customer_Model = _map_customer_to_api(customer)
    return jsonify(Api_Customer_Model.__dict__)