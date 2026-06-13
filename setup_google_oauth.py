# setup_google_auth.py

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive"
]

flow = InstalledAppFlow.from_client_secrets_file(
    "credentials.json",
    SCOPES
)

creds = flow.run_local_server(
    host="localhost",
    port=8080
)

with open("token.json", "w") as f:
    f.write(creds.to_json())

print("token.json created")