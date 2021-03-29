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

def generate_email_body_html(row: dict):
    return f'''
    <html>
        <body>
            <p">Hi {row['Owner Name']}!</p>
            <p>I made a sweet little lofi track with lyrics. The song talks about lost friendships throughout the years. 
            Writing and producing it kinda helped me find peace. The track is pretty meaningful to me. 
            I was thinking it could be a nice fit in your <i>{row['Name']}</i> playlist. Let me know what you think!</p>
            <p"><a href="https://open.spotify.com/track/6o3egSS1DEob4VW6SBH18X?si=e9c36fc2aa4a4fd9">P-Side - Call Me Another Day</a></p>
            <p>Have an awesome day!</p>
            {generate_email_signature_html()} 
        </body>  
    </html>
    '''

def generate_email_signature_html():
    return f'''
    <p><span style="color: #808080;">--</span></p>
    <p><span style="color: #808080;">Paul Brière (P-Side)</span><br />
    <a href="https://pside.contactin.bio/">p-side.com</a></p>
    '''

def generate_email_subject(row: dict):
    return f'Submission (Call Me Another Day)'

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

def main():
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

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])

    # Import CSV files
    csv_file_path = "./CSV/*.csv"
    csv_file_list = glob.glob(csv_file_path)
    for csv_file_name in csv_file_list:
        with open(csv_file_name) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                body_html = generate_email_body_html(row)
                subject = generate_email_subject(row)
                print(body_html)
                # Send Email
                message = create_message("P-Side", row['Email'], subject, body_html)
                send_message(service, message)
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