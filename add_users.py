import sqlite3

conn = sqlite3.connect('db.sqlite')

view_all = int(input('View all records 1/0: '))
if view_all == 1:
    cursor = conn.execute("SELECT id, name, email from USER")
    for row in cursor:
        print("ID = ", row[0])
        print("NAME = ", row[1])
        print("EMAIL = ", row[2])
        print('--------------------')


add_user = int(input('Add user 1/0: '))
if add_user == 1:
    print('adding user')
    out = conn.execute("INSERT INTO USER (ID,NAME,EMAIL) \
      VALUES ('ADMIN3', 'Pritham', 'pritham123@gmail.com')")
    print(out)
