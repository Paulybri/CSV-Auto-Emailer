from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import base64
import csv
import glob
import argparse
import chevron

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--test", action='store_true', help="run in test mode")

SENDER_NAME = "P-Side"
TEST_EMAIL = "pb.sledge.94@gmail.com"

def generate_email_html(row: dict):
    with open('template.mustache', 'r') as f:
        return chevron.render(f, {'owner': row['Owner Name'], 'name' : row['Name']})  

def generate_email_subject(row: dict):
    return f'Submission (Call Me Another Day)'

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

def main():

    args = parser.parse_args()
    TEST_MODE = args.test

    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    # Import CSV files
    csv_file_path = "./CSV/*.csv"
    csv_file_list = glob.glob(csv_file_path)
    for csv_file_name in csv_file_list:
        total_rows = len(open(csv_file_name).readlines())
        with open(csv_file_name) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            first_row = True
            
            for row in csv_reader:
                body_html = generate_email_html(row)
                subject = generate_email_subject(row)
                if (first_row and not TEST_MODE):
                    if input(f'''
Ready to send this template to {total_rows} recipients:

Subject: {subject}

Body: 
{body_html}

****************************************************************

If you are ready to send, type 'yes'
'''                 )!= 'yes':
                        return 
                    first_row = False
                # Send Email
                email = TEST_EMAIL if TEST_MODE else row['Email']
                message = create_message(SENDER_NAME, email, subject, body_html)
                print(f"\nSending to: {email}")
                send_message(service, message)
                if (TEST_MODE):
                    return

def create_message(sender, to, subject, message_html):
  message = MIMEText(message_html, 'html')
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
  return {
    'raw': raw_message.decode("utf-8")
  }

def send_message(service, message):
  try:
    message = service.users().messages().send(userId='me', body=message).execute()
    print('Message Id: %s' % message['id'])
    return message
  except Exception as e:
    print('An error occurred: %s' % e)
    return None

if __name__ == '__main__':
    main()