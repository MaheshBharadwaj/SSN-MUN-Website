import sqlite3 as sql
from werkzeug.security import generate_password_hash, check_password_hash

conn = sql.connect("db.sqlite")

view_all = int(input("View all records 1/0: "))
if view_all == 1:
    cursor = conn.execute("SELECT id, name, email, password, country, committee from user")
    for row in cursor:
        print("ID = ", row[0])
        print("NAME = ", row[1])
        print("EMAIL = ", row[2])
        print("PASSWORD = ", row[3])
        print("COUNTRY = ", row[4])
        print("COMMITTEE = ", row[5])
        print("--------------------")


add_user = int(input("Add user 1/0: "))
if add_user == 1:
    print("adding user")
    with sql.connect("db.sqlite") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO USER (ID, NAME, EMAIL, PASSWORD) \
               VALUES (?,?,?,?)",("ADMIN8", "Pritham3", "pritham181112712@cse.ssn.edu.in", generate_password_hash("admin@ssn", method="sha256")) )
            
            con.commit()
            msg = "Record successfully added"
    # print(out)
