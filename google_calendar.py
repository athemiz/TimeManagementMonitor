import os, pickle, pytz
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_credentials():
    creds, token_path = None, 'token.pickle'
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token: 
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds = creds.refresh(Request())
            with open(token_path, 'wb') as token: 
                pickle.dump(creds, token)
        else:
            creds = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES).run_local_server(port=0)
            with open(token_path, 'wb') as token: 
                pickle.dump(creds, token)
    return creds


def get_events_for_today():
    try:
        creds, service = get_credentials(), build('calendar', 'v3', credentials=get_credentials())
        tz, now_utc3 = pytz.timezone("Etc/GMT+3"), datetime.now(pytz.timezone("Etc/GMT+3"))
        start_of_day, end_of_day = now_utc3.replace(hour=0, minute=0, second=0, microsecond=0).isoformat(), now_utc3.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()
        events = service.events().list(calendarId='primary', timeMin=start_of_day, timeMax=end_of_day, singleEvents=True, orderBy='startTime', showDeleted=False).execute().get('items', [])
        return [(e['summary'], e['start'].get('dateTime', e['start'].get('date')), e['end'].get('dateTime', e['end'].get('date'))) for e in events if e['status'] != 'cancelled'] if events else None
    except HttpError as error: print(f'An error occurred: {error}'); return None

if __name__ == '__main__':
    if (events := get_events_for_today()): [print(f'{event_name}, {start_time}, {end_time}') for event_name, start_time, end_time in events]
