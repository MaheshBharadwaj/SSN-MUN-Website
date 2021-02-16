from openpyxl import Workbook
import os
import sqlite3 as sql


def generate_sheet():
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    file_name = 'Users.xlsx'

    workbook = Workbook()
    sheet = workbook.active

    sheet["A1"] = "ID"
    sheet["B1"] = "Name"
    sheet["C1"] = "E mail"
    sheet["D1"] = "Country"
    sheet["E1"] = "Password"

    conn = sql.connect(ROOT_DIR+"/db.sqlite")
    cursor = conn.execute(
        "SELECT id, name, email,  country, password from user")
    for i, row in enumerate(cursor):
        sheet[f"A{i+2}"] = row[0]
        sheet[f"B{i+2}"] = row[1]
        sheet[f"C{i+2}"] = row[2]
        sheet[f"D{i+2}"] = row[3]
        sheet[f"E{i+2}"] = row[4]

        # print(f"{row[0]} {row[3]} {row[4]}")
        # print("--------------------")

    workbook.save(filename=ROOT_DIR+'/static/' + file_name)


if __name__ == '__main__':
    generate_sheet()
