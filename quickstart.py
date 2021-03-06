from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1kFqoISnADprv9H71nzTq7vrjF-D5T-7W395C_kCyHOg'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'

TRADES_SPREADSHEET_ID = '1kFqoISnADprv9H71nzTq7vrjF-D5T-7W395C_kCyHOg'
TRADES_RANGE_NAME = 'LastDownload!A2:I'

def google_auth():
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
    return service

def get_sheet(service, sheet, srange):
    # Call the Sheets API

    resrange = sheet+'!'+srange

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TRADES_SPREADSHEET_ID,
                                range=resrange).execute()
    values = result.get('values', [])
    rows = []
    for row in values:
        i = 0
        while i < len(row):
            rows.append(row[i])
            i = i+1
    return rows

if __name__ == '__main__':
    googleapi = google_auth()
    print(get_sheet(googleapi, 'LastDownload', 'A2:B'))