from __future__ import print_function
import pickle
import hashlib
import os.path
import random
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import sqlite3 as sql
from werkzeug.security import generate_password_hash, check_password_hash


def generate_otp(email):
    return(str(int(hashlib.sha224(bytes(email, 'utf-8')).hexdigest()[-5:], 16)))


def quickstart():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    conn = sql.connect("db.sqlite")

    random.seed(41)

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = '1_k4i-Fq8W_IsI_W__dd38ZtwrbmByKHC5VUIsdXu1Pc'
    COMMITTEE_ABBREVIATIONS = {'DISEC': 'DI',
                               'UNSC': 'SC', 'ECOFIN': 'EF', 'UNHRC': 'HR'}
    COMMITTEE_ABBR_REV = {'DI': 'DISEC',
                          'SC': 'UNSC', 'EF': 'ECOFIN', 'HR': 'UNHRC'}
    # ALL_COMMITTEES = ['DISEC', 'UNSC', 'ECOFIN', 'UNHRC']
    ALL_COMMITTEES = ['Sheet1']
    SAMPLE_RANGE_NAME = ALL_COMMITTEES[0]
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    for SAMPLE_RANGE_NAME in ALL_COMMITTEES:

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])
        values = values[1:]

        delegates = {'disec': {}, 'ecofin': {}, 'unhrc': {}, 'unsc': {}}

        if not values:
            print('No data found.')
        else:
            for row in values:
                try:
                    # Print columns A and E, which correspond to indices 0 and 4.

                    if(row[4]):
                        if row[1].strip()[:2] == 'IP':
                            continue
                        delegate = {"id": row[2].strip(), "name": row[1].strip(), "email": row[4].strip(),
                                    "password": generate_otp(row[4].strip()), "country": row[8].strip(), "committee": COMMITTEE_ABBR_REV[row[2].strip()[:2]]}

                        delegate_info = {
                            'country': delegate['country'], 'name': delegate['name']}

                        delegates[COMMITTEE_ABBR_REV[delegate['id']
                                                     [:2]].lower()][delegate['id']] = delegate_info

                        with sql.connect("db.sqlite") as con:
                            cur = con.cursor()
                            cur.execute("INSERT INTO USER (ID, NAME, EMAIL, PASSWORD, COUNTRY, COMMITTEE) \
                            VALUES (?,?,?,?,?,?)", (delegate['id'], delegate['name'], delegate['email'], delegate['password'], delegate['country'], delegate['committee']))

                            con.commit()

                        print('%s, %s, %s, %s, %s, %s' % (
                            delegate['id'], delegate['name'], delegate['email'], delegate['password'], delegate['country'], delegate['committee']))
                    # generate_otp(row[1])

                except Exception as e:
                    print('Exception: ' + str(e))

            for committee_abbr in COMMITTEE_ABBREVIATIONS.values():
                delegate = {"id": f"{committee_abbr}EB",
                            "name": "EB",
                            "email": f"EB{committee_abbr}@ssn.edu.in",
                            "country": "No Country",
                            "password": generate_otp(f"EB{committee_abbr}@ssn.edu.in"),
                            "committee": SAMPLE_RANGE_NAME}

                try:
                    with sql.connect("db.sqlite") as con:
                        cur = con.cursor()
                        cur.execute("INSERT INTO USER (ID, NAME, EMAIL, PASSWORD, COUNTRY, COMMITTEE) \
                        VALUES (?,?,?,?,?,?)", (delegate['id'], delegate['name'], delegate['email'], delegate['password'], delegate['country'], delegate['committee']))

                        con.commit()

                except Exception as e:
                    print(e)

            for committee_json_name in COMMITTEE_ABBR_REV.values():
                committee_json_name = committee_json_name.lower()
                recv_json_path = "static/delegate_info/" + committee_json_name + ".json"

                with open(recv_json_path, 'w') as receiver_file:
                    json.dump(delegates[committee_json_name],
                              receiver_file, indent=2)


if __name__ == '__main__':
    quickstart()
