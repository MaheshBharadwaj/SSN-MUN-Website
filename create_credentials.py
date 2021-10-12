import pickle
import hashlib
import os.path
import random
import json

import sqlite3 as sql
from werkzeug.security import generate_password_hash, check_password_hash

def generate_otp(id):
    return hashlib.sha256(id.encode()).hexdigest()[-6:]

def create_ids():
    """
    Creates 799 IDs and passwords for all committees.
    """
    conn = sql.connect("db.sqlite")

    random.seed(41)

    COMMITTEE_ABBREVIATIONS = {'ORF': 'OR',
                               'UNSC': 'SC', 'SFC': 'SF', 'UNHRC': 'HR'}
    COMMITTEE_ABBR_REV = {'OR': 'ORF',
                          'SC': 'UNSC', 'SF': 'SFC', 'HR': 'UNHRC'}
    
    for committee_abbr in COMMITTEE_ABBREVIATIONS.values():
        for i in range(1, 800):
            idx = str(i)
            while len(idx) < 3:
                idx = "0" + idx
            
            id = committee_abbr + idx

            try:
                delegate = {"id": id, "name": "", "email": "",
                                "password": generate_otp(id), "country": "", "committee": COMMITTEE_ABBR_REV[committee_abbr]}
                # print(delegate['id'], delegate['password'])
                with sql.connect("db.sqlite") as con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO USER (ID, NAME, EMAIL, PASSWORD, COUNTRY, COMMITTEE) \
                    VALUES (?,?,?,?,?,?)", (delegate['id'], delegate['name'], delegate['email'], delegate['password'], delegate['country'], delegate['committee']))

                    con.commit()
            except Exception as e:
                print('Exception: ' + str(e))
    
    # Insert EB details
    for committee_abbr in COMMITTEE_ABBREVIATIONS.values():
        delegate = {"id": f"{committee_abbr}EB",
                    "name": "EB",
                    "email": f"EB{committee_abbr}@ssn.edu.in",
                    "country": "No Country",
                    "password": generate_otp(f"{committee_abbr}EB"),
                    "committee": committee_abbr}

        try:
            with sql.connect("db.sqlite") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO USER (ID, NAME, EMAIL, PASSWORD, COUNTRY, COMMITTEE) \
                VALUES (?,?,?,?,?,?)", (delegate['id'], delegate['name'], delegate['email'], delegate['password'], delegate['country'], delegate['committee']))

                con.commit()

        except Exception as e:
            print(e)