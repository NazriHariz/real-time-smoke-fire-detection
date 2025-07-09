import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/drive.file']

service_cred = '/home/ir-nazri/Documents/yolov11/real-time-smoke-fire-detection/credentials.json'

def get_credentials():
    creds = None
    # 1. Check if token already exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # 2. If no valid creds, refresh or prompt login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Only prompt login if we don't have refreshable token
            flow = InstalledAppFlow.from_client_secrets_file(service_cred, SCOPES)
            creds = flow.run_local_server(port=0)

        # 3. Save token to reuse next time
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

    return creds

def upload_to_drive(filepath, filename):
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    folder_id = '1qoT4c5ZioWwwtzADho6QbLATZG7dgs0d'
    
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    media = MediaFileUpload(filepath, mimetype='video/mp4', resumable=True)

    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    file_id = file.get('id')
    print('Uploaded Succesfull -> File ID:', file_id)

    return file_id
