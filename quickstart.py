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

from create_credentials import create_ids, generate_otp


def quickstart():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """

    create_ids()
    print("IDs created successfully")

    conn = sql.connect("db.sqlite")

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = '1_k4i-Fq8W_IsI_W__dd38ZtwrbmByKHC5VUIsdXu1Pc'
    COMMITTEE_ABBREVIATIONS = {'ORF': 'OR',
                               'UNSC': 'SC', 'SFC': 'SF', 'UNHRC': 'HR'}
    COMMITTEE_ABBR_REV = {'OR': 'ORF',
                          'SC': 'UNSC', 'SF': 'SFC', 'HR': 'UNHRC'}
    # ALL_COMMITTEES = ['ORF', 'UNSC', 'SFC', 'UNHRC']
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

        delegates = {'orf': {}, 'sfc': {}, 'unhrc': {}, 'unsc': {}}

        if not values:
            print('No data found.')
        else:
            for row in values:
                try:
                    # Print columns A and E, which correspond to indices 0 and 4.

                    if(row[4]):
                        if row[1].strip()[:2] == 'IP':
                            continue

                        idx = ""
                        comm = ""
                        
                        if row[2].strip()[:2] == 'DI':
                            comm='OR'
                            idx = 'OR' + row[2].strip()[2:]
                        elif row[2].strip()[:2] == 'EF':
                            comm='SF'
                            idx = 'SF' + row[2].strip()[2:]
                        else:
                            comm = row[2].strip()[:2]
                            idx = row[2].strip()
                        
                        delegate = {"id": idx, "name": row[1].strip(), "email": row[4].strip(),
                                    "password": generate_otp(idx), "country": row[8].strip(), "committee": COMMITTEE_ABBR_REV[comm]}

                        delegate_info = {
                            'country': delegate['country'], 'name': delegate['name']}

                        delegates[COMMITTEE_ABBR_REV[delegate['id']
                                                     [:2]].lower()][delegate['id']] = delegate_info
                        
                        with sql.connect("db.sqlite") as con:
                            cur = con.cursor()
                            cur.execute("UPDATE USER SET NAME = ?, EMAIL = ?, COUNTRY = ? \
                            WHERE ID = ?", (delegate['name'], delegate['email'], delegate['country'], delegate['id']))

                            con.commit()

                        print('%s, %s, %s, %s, %s, %s' % (
                            delegate['id'], delegate['name'], delegate['email'], delegate['password'], delegate['country'], delegate['committee']))
                    # generate_otp(row[1])

                except Exception as e:
                    print('Exception: ' + str(e))

            for committee_json_name in COMMITTEE_ABBR_REV.values():
                committee_json_name = committee_json_name.lower()
                recv_json_path = "static/delegate_info/" + committee_json_name + ".json"

                with open(recv_json_path, 'w') as receiver_file:
                    json.dump(delegates[committee_json_name],
                              receiver_file, indent=2)


if __name__ == '__main__':
    quickstart()
