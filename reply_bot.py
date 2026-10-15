"""Reply to comments that say CODE with the link to that Short's snippet. Safe to run repeatedly."""
import re
import sys

from googleapiclient.errors import HttpError

import youtube_api
from common import load_config, load_history, save_history, store_line

TRIGGER = re.compile(r"\bcode\b", re.I)


def main():
    cfg, hist = load_config(), load_history()
    yt = youtube_api.client()
    me = yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]
    threads = yt.commentThreads().list(part="snippet", allThreadsRelatedToChannelId=me,
                                       maxResults=100, order="time", textFormat="plainText").execute()
    sent = 0
    for th in threads.get("items", []):
        top = th["snippet"]["topLevelComment"]
        cid, sn = top["id"], top["snippet"]
        vid = sn.get("videoId")
        if cid in hist["replied"] or vid not in hist["videos"]:
            continue
        if sn.get("authorChannelId", {}).get("value") == me:
            continue
        if len(sn["textDisplay"]) > 40 or not TRIGGER.search(sn["textDisplay"]):
            continue
        slug = hist["videos"][vid]["slug"]
        link = f"https://github.com/{cfg['channel']['github_repo']}/blob/main/snippets/{slug}.py"
        text = f"Here you go: {link}\nTest it on a copy of your files first."
        if store_line(cfg):
            text += f"\n{store_line(cfg)}"
        try:
            yt.comments().insert(part="snippet", body={"snippet": {
                "parentId": th["id"], "textOriginal": text}}).execute()
        except HttpError as e:
            print("reply failed:", e, file=sys.stderr)
            continue
        hist["replied"].append(cid)
        sent += 1
    save_history(hist)
    print(f"replied to {sent} comment(s)")


if __name__ == "__main__":
    main()
