"""Daily automation: learn from analytics, top up the script queue, render, build kits, schedule uploads.

    python run_daily.py                 # real run (needs API keys)
    python run_daily.py --dry-run       # no network: renders the sample script with silent voice, no upload
    python run_daily.py --days 3        # schedule 3 days ahead instead of config's days_ahead
"""
import argparse
import datetime as dt
import json
import shutil
import sys
from zoneinfo import ZoneInfo

import build_kit
import render_video
from common import (OUT, ROOT, SNIPPETS, USED, build_description, load_config, load_history,
                    queue_files, save_history)


def pending_slots(cfg, hist, days):
    tz = ZoneInfo(cfg["timezone"])
    now = dt.datetime.now(tz)
    slots = []
    for d in range(1, days + 1):
        day = (now + dt.timedelta(days=d)).date()
        for s in cfg["schedule"]["slots"]:
            hh, mm = map(int, s.split(":"))
            when = dt.datetime(day.year, day.month, day.day, hh, mm, tzinfo=tz)
            if when > now + dt.timedelta(minutes=15) and when.isoformat() not in hist["scheduled"]:
                slots.append(when)
    return slots


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    cfg = load_config()

    if args.dry_run:
        script = json.loads((ROOT / "content/samples/episode-01.json").read_text())
        out = render_video.render(script, OUT / "dry-run.mp4", cfg, offline=True, ep=1)
        print("dry run OK ->", out)
        print("kit ->", build_kit.build(script, cfg))
        return

    import analytics_loop
    import generate_scripts
    import youtube_api  # noqa: F401  (fail early if libs are missing)
    from youtube_api import upload_scheduled

    hist = load_history()
    slots = pending_slots(cfg, hist, args.days or cfg["schedule"]["days_ahead"])
    if not slots:
        print("nothing to schedule")
        return

    try:
        analytics_loop.update()
    except BaseException as e:  # never let analytics block posting (API not enabled yet, no data, etc.)
        print(f"analytics skipped: {e}", file=sys.stderr)

    need = len(slots) + cfg["schedule"]["queue_buffer"] - len(queue_files())
    if need > 0:
        print(f"queue low, generating {need} scripts")
        generate_scripts.generate_batch(need, quiet=True)

    failures = 0
    for when in slots:
        files = queue_files()
        if not files:
            print("queue empty, stopping", file=sys.stderr)
            failures += 1
            break
        qf = files[0]
        script = json.loads(qf.read_text())
        ep = len(hist["videos"]) + 1
        try:
            mp4 = render_video.render(script, OUT / f"{script['slug']}.mp4", cfg, ep=ep)
            SNIPPETS.mkdir(exist_ok=True)
            (SNIPPETS / f"{script['slug']}.py").write_text(
                f"# {script['title']}\n# From the CodeToCapital YouTube channel. Test on a copy of your files first.\n"
                + script["code"] + "\n")
            build_kit.build(script, cfg)
            publish_utc = when.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            vid = upload_scheduled(mp4, script["title"], build_description(script, cfg),
                                   script["tags"], publish_utc)
        except SystemExit as e:
            print(f"FAILED {qf.name}: {e}", file=sys.stderr)
            failures += 1
            continue
        hist["scheduled"][when.isoformat()] = vid
        hist["videos"][vid] = {"slug": script["slug"], "title": script["title"],
                               "pillar": script.get("pillar"), "ep": ep, "publishAt": publish_utc}
        USED.mkdir(parents=True, exist_ok=True)
        shutil.move(str(qf), USED / qf.name)
        save_history(hist)
        print(f"scheduled {when.isoformat()} -> https://youtube.com/shorts/{vid}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
