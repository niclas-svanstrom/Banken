from model import Customer, Account


def get_customers_per_country():
    distinct = [x.Country for x in Customer.query.with_entities(Customer.Country).distinct()]
    total = []
    for c in distinct:
        total.append(len(Customer.query.filter_by(Country=c).all()))
    country_customer={d:t for (d,t) in zip(distinct, total)}
    return country_customer

def get_top_ten_from_selected_country(country):
    class Personas():
        def __init__(self, customer_id, money, name, lastname):
            self.__customer_id = customer_id
            self.__money = money
            self.__name = name
            self.__lastname = lastname
        def get_id(self):
            return self.__customer_id
        def get_money(self):
            return self.__money
        def get_name(self):
            return self.__name
        def get_lastname(self):
            return self.__lastname
    customers= Customer.query.filter_by(Country=country).all()
    list_of_customers = []
    for c in customers:
        accounts = Account.query.filter_by(CustomerId=c.Id).all()
        sum = 0
        for a in accounts:
            sum += a.Balance
        persona = Personas(c.Id,sum,c.GivenName,c.Surname)
        list_of_customers.append(persona)
    list_of_customers.sort(reverse=True, key=lambda x: x.get_money())
    return list_of_customers[:10]