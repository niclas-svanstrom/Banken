from flask import Blueprint, jsonify
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

@apiBluePrint.route('/api/customer')
def all_customers():
    list_of_all = []
    for customer in Customer.query.all():
        Api_Customer_Model = _map_customer_to_api(customer)
        list_of_all.append(Api_Customer_Model)
    return jsonify([apicustomer.__dict__ for apicustomer in list_of_all])

@apiBluePrint.route('/api/customer/<id>')
def one_customer(id):
    customer = Customer.query.filter_by(Id=id).first()
    Api_Customer_Model = _map_customer_to_api(customer)
    return jsonify(Api_Customer_Model.__dict__)