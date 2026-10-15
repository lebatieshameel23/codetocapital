"""Generate Short scripts (plus the paid kit for each) with a free LLM and queue the valid ones.

Pillars are picked by performance weight (see analytics_loop.py), so topics that hold viewers
longer get made more often, while every pillar keeps a minimum share so the channel keeps exploring.

Usage:
    export GEMINI_API_KEY=...      # free key from aistudio.google.com (or GROQ_API_KEY, free)
    python generate_scripts.py --count 5
"""
import argparse
import datetime as dt
import json
import random
import re
import sys

import llm
from common import (MAX_CODE_LINES, MAX_KIT_LINES, MAX_LINE_CHARS, QUEUE, load_config, load_history,
                    load_performance, queue_files, save_history, validate_script)

HOOK_STYLES = [
    "COST: open with a recurring cost the viewer recognises ('Say you pay someone $X a month to...'), with the sum shown.",
    "MISTAKE: 'Most people do this by hand in Excel every week. Here's the ten-line version.'",
    "TIME: 'This task eats an hour every Friday. Here's how to make it a single command.' (no invented timings)",
    "CURIOSITY: a specific gap that the video closes within 20 seconds ('There's a pandas one-liner that replaces VLOOKUP').",
    "RESULT FIRST: beat 1 has reveal 0 and an output line, so the viewer sees the finished result before the code appears.",
    "MYTH: 'You don't need paid software to do this.' then prove it with the code.",
]

SYSTEM = f"""You write scripts for 25-35 second YouTube Shorts for CodeToCapital: short, real Python/automation
snippets that save small businesses time and money. The goal is high watch-through and replays, earned by being
genuinely useful, fast and satisfying to watch, never by deceiving viewers.

RETENTION CRAFT (do all of these)
- The hook (beat 1) must land in the first 2 seconds and its promise must be fully paid off before the video ends.
- Fast pace: short sentences, no filler, no greetings, no "in this video".
- LOOP: write the final sentence so it flows naturally into the first sentence of beat 1 (the video replays
  automatically). Example: last "...because nobody should be typing this by hand." then first "Say you pay someone..."
- Each beat must change something on screen (reveal more code, show output, or show a badge).
- The second-to-last beat should deliver the satisfying payoff (the output).

HONESTY AND SAFETY (hard rules)
- Never invent a client, customer, company, or measured result. No fake speed or scale claims ("14,000 emails in
  8 seconds"). Frame money as a hypothetical ("Say you pay...") with correct, visible arithmetic.
  A terminal output line may only show what the code would print for a small sample (e.g. "wrote totals.csv").
- Mention one real limitation in the last beat.
- Never write scripts that: scrape personal contact details or build lead lists of private people; bypass logins,
  paywalls or CAPTCHAs; scrape sites whose terms forbid it (e.g. Amazon or social networks); send bulk or
  unsolicited messages; fake engagement; handle anyone else's credentials. Anything that deletes or moves files or
  emails must have a dry-run option in the kit code and say so.

FORMAT
- Free on-screen code ("code"): real, correct, standalone Python, at most {MAX_CODE_LINES} lines and
  {MAX_LINE_CHARS} characters per line, plain ASCII, standard library plus at most one common package
  (pandas, pypdf, requests, openpyxl). A blank line counts as a line.
- Narration: 50-95 words total, spoken, no emoji, no hashtags.
- 5 beats. Each beat: voice, reveal (code lines visible by the END of that beat; non-decreasing; the last beat
  reveals all lines), badge (<= 24 chars on-screen label or ""), output (terminal output line or "").
- hook_text: <= 38 characters, shown big at the top. title: <= 70 characters, search-friendly, no hashtags/emoji.
- Paid kit: "kit_code" is a more robust version of the same tool (argparse CLI, error handling, logging, clear
  comments, <= {MAX_KIT_LINES} lines, must compile). "kit_readme" is plain text with sections SETUP, HOW IT WORKS,
  ADAPTING IT, LIMITATIONS, SUPPORT (no warranty) and is at least 600 characters. In the readme and in
  the code docstring always call the kit script "tool.py". "product_name" and
  "product_blurb" (2 sentences, honest, no income claims) describe it for a store listing.

Reply with ONE JSON object and nothing else, with keys: slug (lowercase-hyphen), title, hook_text, description
(2 sentences), tags (5-8 short strings), code (string with \\n newlines), beats, kit_code, kit_readme,
product_name, product_blurb."""


extract_json = llm.extract_json


def choose_pillar(pillars, perf, rnd):
    weights = [max(0.3, float(perf.get("pillar_weights", {}).get(p, 1.0))) for p in pillars]
    return rnd.choices(pillars, weights=weights, k=1)[0]


def guidance(perf):
    out = ""
    if perf.get("top"):
        out += "Recent best performers (copy the angle and pacing, not the wording): " + "; ".join(perf["top"][:5]) + "\n"
    if perf.get("bottom"):
        out += "Recent weakest (avoid this angle): " + "; ".join(perf["bottom"][:3]) + "\n"
    return out


def generate_one(ai_cfg, pillar, hook_style, avoid, perf, feedback=""):
    user = (f"Content pillar: {pillar}\nHook style for this one: {hook_style}\n"
            f"Do not repeat or closely resemble these earlier titles: {avoid[-30:] or 'none yet'}\n"
            f"{guidance(perf)}{feedback}Write one new Short script now.")
    return extract_json(llm.complete(SYSTEM, user, max_tokens=6000, ai_cfg=ai_cfg))


def generate_batch(count, quiet=False):
    cfg, perf, hist = load_config(), load_performance(), load_history()
    if not llm.available(cfg.get("ai")):
        raise SystemExit("No LLM key set. Add GEMINI_API_KEY (free) or GROQ_API_KEY (free) - see README.")
    rnd = random.Random()
    counter = len(hist["used_titles"]) + len(queue_files())
    made = 0
    for i in range(count):
        pillar = choose_pillar(cfg["pillars"], perf, rnd)
        style = HOOK_STYLES[(counter + i) % len(HOOK_STYLES)]
        feedback, s = "", None
        for attempt in range(4):
            try:
                s = generate_one(cfg.get("ai"), pillar, style, hist["used_titles"], perf, feedback)
                problems = validate_script(s)
            except Exception as e:  # bad JSON, API hiccup...
                problems, s = [f"could not parse reply: {e}"], None
            if not problems:
                break
            feedback = "Your previous attempt was rejected: " + "; ".join(problems) + ". Fix these.\n"
            if not quiet:
                print(f"  retry {attempt + 1}: {problems}", file=sys.stderr)
        else:
            print(f"  gave up on one script for pillar: {pillar}", file=sys.stderr)
            continue
        s["pillar"] = pillar
        stamp = dt.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        QUEUE.mkdir(parents=True, exist_ok=True)
        path = QUEUE / f"{stamp}-{i:02d}-{s['slug']}.json"
        path.write_text(json.dumps(s, indent=2, ensure_ascii=False))
        hist["used_titles"].append(s["title"])
        made += 1
        if not quiet:
            print("queued:", path.name)
    save_history(hist)
    return made


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=5)
    args = ap.parse_args()
    n = generate_batch(args.count)
    print(f"{n}/{args.count} scripts queued")
    sys.exit(0 if n else 1)
