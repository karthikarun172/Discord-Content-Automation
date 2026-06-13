from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from config.settings import SCOPES


def get_google_services():

    creds = Credentials.from_authorized_user_file(
        "token.json",
        SCOPES
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return (
        build("docs", "v1", credentials=creds),
        build("drive", "v3", credentials=creds)
    )