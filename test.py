import pycountry


countries = []
for country in pycountry.countries:
    countries.append(country.name)


code = pycountry.countries.get(name='Sweden').alpha_2

print(code)