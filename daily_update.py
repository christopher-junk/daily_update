from __future__ import print_function
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd 
import numpy as np 

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from googleapiclient.errors import HttpError

from datetime import datetime, timedelta

import pytz

import os

import os.path

wd = 'C:/Users/chris/Documents/daily_update'

os.chdir(wd)


#API Setup
## Define the scope/API to be used
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/calendar.readonly'
]

## Load the credentials
cred_file = 'C:/Users/chris/Documents/gcp/daily-update-439419-287695ff6d33.json'
creds = ServiceAccountCredentials.from_json_keyfile_name(cred_file, scope)

## Authorize the client
client = gspread.authorize(creds)

#Access Google Sheets 

##Define function to turn the google sheet into a pandas dataframe
def sheet_to_df(x):
    data = x.get_all_values() 

    df = pd.DataFrame(data[1:], columns = data[0])
    
    return df

## Open the Google Sheet
spreadsheet = client.open("Job Search")

### Open the applications worksheet and keep only rows where the last updated day is today
worksheet = spreadsheet.sheet1  # or spreadsheet.worksheet("Sheet1")

df = sheet_to_df(worksheet)

today = datetime.now().date()

today_update = df[df['update_date'] == str(today)].loc[:, ['company', 'app_date', 'current_status', 'position_name', 'location']]

today_update.rename(columns = {'company' : 'Company', 
                               'app_date' : 'Application Date', 
                               'current_status' : 'Status', 
                               'position_name' : 'Title', 
                               'location' : 'Location'}, 
                    inplace = True)

### Open the daily notes sheet and keep the notes from today
sh = spreadsheet.get_worksheet(1)
df = sheet_to_df(sh)
notes = df.loc[df['date'] == str(today), 'activity'].values[0]


# Access the Google Calendar API
service = build('calendar', 'v3', credentials=creds)

## Get tomorrow's date
tomorrow = datetime.now() + timedelta(days=1)
start_of_tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'  # Start of the day in UTC
end_of_tomorrow = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat() + 'Z'  # End of the day in UTC

### Get Tomorrow's events
try:
    events_result = service.events().list(calendarId='christopher.junk24@gmail.com', 
                                          timeMin=start_of_tomorrow,
                                          timeMax=end_of_tomorrow, 
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

except Exception as e:
    print(f"An error occurred: {e}")

### Convert the events into a dataframe and format the dataframe to just be the event name and the start time
events_df = pd.DataFrame(events)

events_df['start_time'] = events_df['start'].apply(lambda x: x.get('dateTime', x.get('date')))

# Convert 'start_time' to datetime
events_df['start_time'] = pd.to_datetime(events_df['start_time'])

# Format the time as HH:MM AM/PM
events_df['formatted_start_time'] = events_df['start_time'].dt.strftime('%I:%M %p')

# Display the updated DataFrame
events_df.rename(columns = {'summary' : 'Event', 
                            'formatted_start_time' : 'Time'}, 
                 inplace = True)

# Structure the email

subject = f'{today} job search update'

## Table of job application updates
html_table = today_update.to_html(index = False)

## Table of tomorrow's events
html_events = events_df[['Event', 'Time']].to_html(index = False)

## Formatted notes keeping line breaks
formatted_notes = notes.replace('\n', '<br>')

## HTML format of email
body = f"""
<html>
<head></head>
<body>
    <!-- Subheader -->
    <h3>Today's Notes</h3>

    <p>{formatted_notes}</p>
    <hr>

    <!-- Subheader -->
    <h3>Tomorrow's Scheduled Meetings</h3>

    {html_events}
    <hr>

    <p>Job applications and status updates</p>
    {html_table}
</body>
</html>
"""

## Email logistic details
sender_email = "christopher.junk24@gmail.com"
to_emails = ["clh3071@gmail.com", "emmaejunk17@gmail.com"]
password = os.getenv('email_password')

msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = ', '.join(to_emails)
msg['Subject'] = subject
msg.attach(MIMEText(body, 'html'))

# Send the email
try:
    # Connect to the server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)  # Use App Password
    server.send_message(msg)
    print("Email sent successfully!")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    server.quit()
