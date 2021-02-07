from __future__ import print_function
import pickle
import hashlib
import os.path
import random
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
SAMPLE_RANGE_NAME = 'UNHRC'

def generate_otp(email):
    return(hashlib.sha224(bytes(email, 'utf-8')).hexdigest()[-5:])

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

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    values = values[1:5]

    if not values:
        print('No data found.')
    else:
        for row in values:
            try:
                # Print columns A and E, which correspond to indices 0 and 4.
                print('%s %s %d' % (row[1], row[2], int(generate_otp(row[6])[-5:], 16)))
                # generate_otp(row[1])
            except:
                print("", end = "")

if __name__ == '__main__':
    main()
