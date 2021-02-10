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

conn = sql.connect("db.sqlite")

random.seed(41)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1I6w3WamoWtfrtYXEr59UDYnfAk7MIrAY6rEUD4sFsQE'
COMMITTEE_ABBREVIATIONS = {'DISEC': 'DI', 'UNSC': 'SC', 'ECOFIN': 'EF', 'UNHRC': 'HR'}
ALL_COMMITTEES = ['DISEC', 'UNSC', 'ECOFIN', 'UNHRC']
SAMPLE_RANGE_NAME = ALL_COMMITTEES[0]

def generate_otp(email):
    return(str(int(hashlib.sha224(bytes(email, 'utf-8')).hexdigest()[-5:], 16)))

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
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

        delegates = {}

        if not values:
            print('No data found.')
        else:
            for row in values:
                try:
                    # Print columns A and E, which correspond to indices 0 and 4.
                    
                    if(row[5]):
                        delegate = {"id": row[5].strip(), "name": row[1].strip(), "email": row[2].strip(), 
                            "password": generate_otp(row[2].strip()), "country": row[0].strip(), "committee": SAMPLE_RANGE_NAME}

                        delegate_info = {'country': delegate['country'], 'name': delegate['name']}

                        delegates[delegate['id']] = delegate_info

                        with sql.connect("db.sqlite") as con:
                            cur = con.cursor()
                            cur.execute("INSERT INTO USER (ID, NAME, EMAIL, PASSWORD, COUNTRY, COMMITTEE) \
                            VALUES (?,?,?,?,?,?)",(delegate['id'] ,delegate['name'] ,delegate['email'] ,delegate['password'] ,delegate['country'] ,delegate['committee']))
                            
                            con.commit()
                        
                        # print('%s, %s, %s, %s, %s, %s' % (delegate['id'] ,delegate['name'] ,delegate['email'] ,delegate['password'] ,delegate['country'] ,delegate['committee']))
                    # generate_otp(row[1])
                    
                except Exception as e:
                    print(e)

            delegate = {"id": f"{COMMITTEE_ABBREVIATIONS[SAMPLE_RANGE_NAME]}EB", 
                "name": "EB", 
                "email": f"EB{COMMITTEE_ABBREVIATIONS[SAMPLE_RANGE_NAME]}@ssn.edu.in", 
                "country": "No Country", 
                "password": generate_otp(f"EB{COMMITTEE_ABBREVIATIONS[SAMPLE_RANGE_NAME]}@ssn.edu.in"),
                "committee": SAMPLE_RANGE_NAME}

            try:
                with sql.connect("db.sqlite") as con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO USER (ID, NAME, EMAIL, PASSWORD, COUNTRY, COMMITTEE) \
                    VALUES (?,?,?,?,?,?)",(delegate['id'] ,delegate['name'] ,delegate['email'] ,delegate['password'] ,delegate['country'] ,delegate['committee']))
                    
                    con.commit()

            except Exception as e:
                print(e)

            recv_json_path = "static/delegate_info/" + SAMPLE_RANGE_NAME.lower() + ".json" 

            with open(recv_json_path, 'w') as receiver_file:
                json.dump(delegates, receiver_file, indent=2)


if __name__ == '__main__':
    main()
