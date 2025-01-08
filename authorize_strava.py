import json
import requests
import webbrowser
from datetime import datetime
from urllib.parse import urlparse, parse_qs

CLIENT_ID = "" # removed personal CLIENT_ID
CLIENT_SECRET = "" # removed personal CLIENT_SECRET
REDIRECT_URI = "http://localhost"

TOKEN_FILE = "token.json"

def get_authorization_code():
    # Get authorization code
    auth_url = (
        f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&response_type=code&scope=activity:read"
    )
    webbrowser.open(auth_url)
    print("After authorizing the app, you'll be redirected to a URL.")
    auth_code = input("Enter the URL: ")
    # Parse URL to get the 'code' query parameter
    parsed_url = urlparse(auth_code)
    query_params = parse_qs(parsed_url.query)
    code = query_params.get('code', [None])[0]
    return code

def get_token(auth_code):
    # Get access token from authorization code
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    return response.json()

def save_tokens(access_token, refresh_token):
    # save tokens to token.json
    date_accessed = datetime.now()
    date_string = date_accessed.isoformat()
    with open(TOKEN_FILE, "w") as file:
        file.write("")
        json.dump([{"Access_token": access_token}, {"Refresh_token": refresh_token}, {"Date": date_string}], file)

def load_tokens():
    # Load tokens from token.json
    try:
        with open(TOKEN_FILE, "r") as file:
            tokens = json.load(file)
            access_token = tokens[0].get("Access_token")
            refresh_token = tokens[1].get("Refresh_token")
            return access_token, refresh_token

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading tokens: {e}")
        return None, None

def refresh_access_token(refresh_token):
    # Automatically get new access token when token expires
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    return response.json()

def get_valid_access_token():
    # Loads tokens from token.json
    access_token, refresh_token = load_tokens()
    # Returns existing access token if exists
    if access_token:
        return access_token
    # otherwise, starts Oauth again
    else:
        print("No access token found, starting the OAuth process.")
        auth_code = get_authorization_code()
        token_data = get_token(auth_code)
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        save_tokens(access_token, refresh_token)
        print("Tokens saved.")
        return access_token

def get_fresh_access_token():
    # Gets new access token
    access_token, refresh_token = load_tokens()
    # If refresh token found, get and access token
    if refresh_token:
        token_data = refresh_access_token(refresh_token)
        access_token = token_data["access_token"]
        save_tokens(access_token, refresh_token)
        return access_token
    # If no refresh token, get valid access token
    else:
        print("No refresh token found. Starting new OAuth process.")
        return get_valid_access_token()

if __name__ == "__main__":
    auth_code = get_authorization_code()
    token_data = get_token(auth_code)
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    save_tokens(access_token, refresh_token)
    print("You've successfully authorized your Strava account!")