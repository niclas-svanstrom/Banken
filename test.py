user1 = ["stefan.holmberg@systementor.se", "Hejsan123#", "Stefan", "Holmberg", 1]
user2 = ["stefan.holmberg@nackademin.se", "Hejsan123#", "Stefan", "Holmberg", 2]
user3 = ["niclas.svanstrom@hotmail.com", "password", "Niclas", "Svanström", 1]

userlist = {1:user1,2:user2,3:user3}
userlist2 = ["stefan.holmberg@systementor.se", "Blabla", "nädu"]

for u1 in userlist2:
    for u in userlist.values():
        print(u[0])
        continue