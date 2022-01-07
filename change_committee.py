import pickle
import hashlib
import os.path
import random
import json
import sys

import sqlite3 as sql
from werkzeug.security import generate_password_hash, check_password_hash

from create_credentials import generate_otp

def move_details(source_id, dest_committee):
    """
    Move details from source_id to a free ID in dest_committee.
    """

    COMMITTEE_ABBREVIATIONS = {'ORF': 'OR',
                               'UNSC': 'SC', 'SFC': 'SF', 'UNHRC': 'HR'}
    COMMITTEE_ABBR_REV = {'OR': 'ORF',
                          'SC': 'UNSC', 'SF': 'SFC', 'HR': 'UNHRC'}

    conn = sql.connect("db.sqlite")

    # Retrieve all details
    delegate_details = dict()
    try:
        with sql.connect("db.sqlite") as con:
            cur = con.cursor()
            cur.execute("SELECT ID,NAME,PASSWORD,COUNTRY,COMMITTEE FROM USER WHERE ID = '"+source_id+"'")
        rows = cur.fetchall()
        for row in rows:
            delegate_details = {"id": row[0].strip(), "name": row[1].strip(),
                                    "password": row[2].strip(), "country": row[3], "committee": row[4].strip()}
            break
    
    except Exception as e:
        print('Exception: ' + str(e))
    print(delegate_details)

    # Idenify free ID in the destination committee
    dest_id=""
    try:
        with sql.connect("db.sqlite") as con:
            cur = con.cursor()
            cur.execute(f"SELECT ID FROM USER \
            WHERE ID LIKE '{COMMITTEE_ABBREVIATIONS[dest_committee]}%' AND LENGTH(NAME) = 0" )
        rows = cur.fetchall()
        for row in rows:
            dest_id = row[0].strip()
            break
    except Exception as e:
        print('Exception: ' + str(e))

    print(f"New ID: {dest_id}")

    # Update details at the destination committee
    new_delegate_details = dict()
    try:
        new_delegate_details = {"id": dest_id, "name": delegate_details['name'],
                                    "password": generate_otp(dest_id), "country": delegate_details['country'], "committee": dest_committee}
        with sql.connect("db.sqlite") as con:
            cur = con.cursor()
            cur.execute("UPDATE USER SET NAME = ?, COUNTRY = ? \
            WHERE ID = ?", (new_delegate_details['name'], new_delegate_details['country'], new_delegate_details['id']))

            con.commit()

        print('%s, %s, %s, %s, %s, %s' % (
            new_delegate_details['id'], new_delegate_details['name'], new_delegate_details['password'], new_delegate_details['country'], new_delegate_details['committee']))
    except Exception as e:
        print('Exception: ' + str(e))
    
    # Delete details from the old committee

    try:
        with sql.connect("db.sqlite") as con:
            cur = con.cursor()
            cur.execute("UPDATE USER SET NAME = '', COUNTRY = '' \
            WHERE ID = '"+ source_id + "'")

            con.commit()
    except Exception as e:
        print('Exception: ' + str(e))
    

if __name__ == "__main__":
    n = len(sys.argv)
    source_id = sys.argv[1]
    dest_committee = sys.argv[2]
    move_details(source_id, dest_committee)