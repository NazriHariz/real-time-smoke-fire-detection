import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/drive.file']

service_cred = '/home/ir-nazri/Documents/yolov11/real-time-smoke-fire-detection/credentials.json'

def get_credentials() -> Credentials:
    creds = None

    # 1. Load saved token if it exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # 2. If no valid creds, refresh or start a new auth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(service_cred, SCOPES)
            creds = flow.run_local_server(port=0)

        # 3. Persist token for next run
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

    return creds


def upload_to_drive(filepath: str, filename: str) -> str:
    """Upload a file and make it ‘Anyone with the link → Viewer’."""
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds, cache_discovery=False)

    folder_id = "1qoT4c5ZioWwwtzADho6QbLATZG7dgs0d"   # your destination folder

    # --- 1. Upload the file ---
    file_metadata = {"name": filename, "parents": [folder_id]}
    media = MediaFileUpload(filepath, mimetype="video/mp4", resumable=True)

    new_file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    file_id = new_file["id"]
    print("✅ Uploaded — File ID:", file_id)

    # --- 2. Change permission (anyone can view) ---
    permission_body = {"type": "anyone", "role": "reader"}
    service.permissions().create(
        fileId=file_id,
        body=permission_body,
        fields="id",
    ).execute()
    print("🔓 Permission set to ‘Anyone with the link can view’")
