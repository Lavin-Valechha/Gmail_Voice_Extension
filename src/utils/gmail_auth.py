import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Define necessary Gmail API scopes
SCOPES = [
    "https://mail.google.com/",  # Full access to Gmail (Read, Send, Modify, Delete)
]

def authenticate_gmail():
    """
    Handles authentication with Gmail API using OAuth 2.0
    """
    creds = None
    token_path = "token.pickle"

    # Load existing credentials if available
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    # If credentials are not valid or expired, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the new credentials
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    return creds

if __name__ == "__main__":
    authenticate_gmail()
    print("✅ Authentication successful! You can now use the Gmail API.")
