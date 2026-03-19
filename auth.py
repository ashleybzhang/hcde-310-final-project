import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

REDIRECT_URI = "http://localhost:5000/oauth2callback"
CREDENTIALS_FILE = "credentials.json"

# Store the flow globally so both steps share the same object
_flow = None


def get_auth_url():
    global _flow
    _flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    auth_url, _ = _flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return auth_url


def exchange_code_for_token(code):
    global _flow
    _flow.fetch_token(code=code)
    credentials = _flow.credentials

    return {
        "token":         credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri":     credentials.token_uri,
        "client_id":     credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes":        list(credentials.scopes),
    }


def get_credentials(token_dict):
    return Credentials(
        token=token_dict["token"],
        refresh_token=token_dict.get("refresh_token"),
        token_uri=token_dict["token_uri"],
        client_id=token_dict["client_id"],
        client_secret=token_dict["client_secret"],
        scopes=token_dict["scopes"],
    )
