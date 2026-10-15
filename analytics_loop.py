"""Growth loop: read how each Short performed and re-weight future topics toward what holds viewers.

Score per video = views x (average % viewed / 100) + 50 x subscribers gained.
Pillars whose videos score above average get picked more often; every pillar keeps a minimum share.
Writes content/performance.json, which generate_scripts.py reads.

Needs the YouTube Analytics API enabled in your Google Cloud project (README step 3).
"""
import datetime as dt
import json
import statistics

import youtube_api
from common import PERFORMANCE, load_config, load_history

MIN_AGE_DAYS = 3      # analytics data lags by a couple of days
MIN_VIDEOS = 6        # don't draw conclusions from a handful of videos


def update(verbose=True):
    hist = load_history()
    now = dt.datetime.now(dt.timezone.utc)
    ids = []
    for vid, v in hist["videos"].items():
        pub = dt.datetime.fromisoformat(v["publishAt"].replace("Z", "+00:00"))
        if now - pub >= dt.timedelta(days=MIN_AGE_DAYS):
            ids.append(vid)
    if len(ids) < MIN_VIDEOS:
        if verbose:
            print(f"analytics: only {len(ids)} videos old enough, need {MIN_VIDEOS}; skipping")
        return None

    ya = youtube_api.analytics_client()
    resp = ya.reports().query(
        ids="channel==MINE",
        startDate=(now - dt.timedelta(days=90)).date().isoformat(),
        endDate=now.date().isoformat(),
        metrics="views,averageViewPercentage,subscribersGained",
        dimensions="video",
        filters="video==" + ",".join(ids[:400]),
        maxResults=200,
    ).execute()

    scores = {}
    for vid, views, avg_pct, subs in resp.get("rows", []):
        scores[vid] = views * (avg_pct / 100.0) + 50 * subs
    if not scores:
        return None

    by_pillar = {}
    for vid, sc in scores.items():
        pillar = hist["videos"][vid].get("pillar")
        if pillar:
            by_pillar.setdefault(pillar, []).append(sc)
    overall = statistics.mean(scores.values()) or 1.0
    weights = {p: round(max(0.3, statistics.mean(v) / overall), 2) for p, v in by_pillar.items()}

    ranked = sorted(scores, key=scores.get, reverse=True)
    perf = {
        "updated": now.isoformat(),
        "videos_scored": len(scores),
        "pillar_weights": weights,
        "top": [hist["videos"][v]["title"] for v in ranked[:5]],
        "bottom": [hist["videos"][v]["title"] for v in ranked[-3:]],
    }
    PERFORMANCE.write_text(json.dumps(perf, indent=2, ensure_ascii=False))
    if verbose:
        print("analytics: updated pillar weights", weights)
    return perf


if __name__ == "__main__":
    update()
