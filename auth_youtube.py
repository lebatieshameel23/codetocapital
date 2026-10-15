"""One-time login. Run this on your own computer (it opens a browser).

Needs client_secret.json (OAuth client of type "Desktop app") next to this file.
Prints the three values to save as GitHub secrets: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.
"""
import json

from google_auth_oauthlib.flow import InstalledAppFlow

from youtube_api import SCOPES

flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
info = json.load(open("client_secret.json"))
info = info.get("installed") or info.get("web")
print("\nSave these as secrets (never commit them):")
print("YT_CLIENT_ID     =", info["client_id"])
print("YT_CLIENT_SECRET =", info["client_secret"])
print("YT_REFRESH_TOKEN =", creds.refresh_token)
