class Personas():
    def __init__(self, customer_id, money):
        self.__customer_id = customer_id
        self.__money = money
    def get_money(self):
        return self.__money
    def __repr__(self):
        return f'{self.__customer_id} {self.__money}'

persona = [
        Personas(2, 2000),
        Personas(1, 5000),
        Personas(3, 3000),
        Personas(4, 5000),
        Personas(5, 2500),
        Personas(6, 3000),
        Personas(7, 6000),
        Personas(8, 1000),
        Personas(9, 7000),
        Personas(10, 6500),
        Personas(11, 3400),
        Personas(12, 2000),
    ]

persona.sort(reverse=True, key=lambda x: x.get_money())

persona = persona[:5]
 
    # output: [{Joe, Finance, 25}, {John, IT, 28}, {Sam, Banking, 20}]
print(persona)