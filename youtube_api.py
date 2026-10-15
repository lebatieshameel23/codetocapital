"""YouTube API helpers: credentials from env vars, scheduled upload, analytics client."""
import os
import sys

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.force-ssl",
          "https://www.googleapis.com/auth/yt-analytics.readonly"]


def _creds():
    try:
        return Credentials(
            None,
            refresh_token=os.environ["YT_REFRESH_TOKEN"],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ["YT_CLIENT_ID"],
            client_secret=os.environ["YT_CLIENT_SECRET"],
            scopes=SCOPES,
        )
    except KeyError as e:
        sys.exit(f"Missing environment variable {e}. See README, step 3.")


def client():
    return build("youtube", "v3", credentials=_creds(), cache_discovery=False)


def analytics_client():
    return build("youtubeAnalytics", "v2", credentials=_creds(), cache_discovery=False)


def upload_scheduled(path, title, description, tags, publish_at_utc_iso):
    """Upload as private with a publishAt time; YouTube flips it public at that moment."""
    yt = client()
    body = {
        "snippet": {"title": title[:100], "description": description[:4900],
                    "tags": tags[:15], "categoryId": "28"},  # 28 = Science & Technology
        "status": {"privacyStatus": "private", "publishAt": publish_at_utc_iso,
                   "selfDeclaredMadeForKids": False},
    }
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(path), chunksize=-1, resumable=True))
    resp = None
    try:
        while resp is None:
            _, resp = req.next_chunk()
    except HttpError as e:
        sys.exit(f"YouTube upload failed: {e}")
    return resp["id"]
