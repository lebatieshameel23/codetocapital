"""Shared helpers: config, history/state, script validation, description builder."""
import ast
import json
import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parent
CONTENT = ROOT / "content"
QUEUE = CONTENT / "queue"
USED = CONTENT / "used"
SNIPPETS = ROOT / "snippets"
OUT = ROOT / "out"
HISTORY = CONTENT / "history.json"
PERFORMANCE = CONTENT / "performance.json"

MAX_CODE_LINES = 10
MAX_LINE_CHARS = 44
MAX_KIT_LINES = 160


def load_config():
    return yaml.safe_load((ROOT / "config.yaml").read_text())


def load_history():
    h = json.loads(HISTORY.read_text()) if HISTORY.exists() else {}
    h.setdefault("used_titles", [])
    h.setdefault("scheduled", {})   # ISO local slot -> video id
    h.setdefault("videos", {})      # video id -> {slug, title, pillar, ep, publishAt}
    h.setdefault("replied", [])     # comment ids already answered
    return h


def save_history(h):
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(h, indent=2, ensure_ascii=False))


def load_performance():
    return json.loads(PERFORMANCE.read_text()) if PERFORMANCE.exists() else {}


def queue_files():
    QUEUE.mkdir(parents=True, exist_ok=True)
    return sorted(QUEUE.glob("*.json"))


def validate_script(s):
    """Return a list of problems (empty list = script is good to render)."""
    p = []
    for k in ("slug", "title", "hook_text", "description", "tags", "code", "beats",
              "kit_code", "kit_readme", "product_name", "product_blurb"):
        if not s.get(k):
            p.append(f"missing key: {k}")
    if p:
        return p
    if not re.fullmatch(r"[a-z0-9-]{3,60}", s["slug"]):
        p.append("slug must be lowercase letters, digits, hyphens")
    if len(s["title"]) > 90:
        p.append("title longer than 90 chars")
    lines = s["code"].split("\n")
    if len(lines) > MAX_CODE_LINES:
        p.append(f"code has {len(lines)} lines (max {MAX_CODE_LINES})")
    for i, ln in enumerate(lines, 1):
        if len(ln) > MAX_LINE_CHARS:
            p.append(f"code line {i} is {len(ln)} chars (max {MAX_LINE_CHARS})")
    for name, src in (("code", s["code"]), ("kit_code", s["kit_code"])):
        try:
            ast.parse(src)
        except SyntaxError as e:
            p.append(f"{name} does not compile: {e}")
    if len(s["kit_code"].split("\n")) > MAX_KIT_LINES:
        p.append(f"kit_code longer than {MAX_KIT_LINES} lines")
    if len(s["kit_readme"]) < 300:
        p.append("kit_readme is too short to be a useful setup guide")
    beats = s["beats"]
    if not 4 <= len(beats) <= 7:
        p.append("need 4-7 beats")
    prev, words = 0, 0
    for i, b in enumerate(beats):
        if not b.get("voice"):
            p.append(f"beat {i} has no voice text")
            continue
        words += len(b["voice"].split())
        r = b.get("reveal", prev)
        if r < prev or r > len(lines):
            p.append(f"beat {i} reveal={r} is out of order or too large")
        prev = r
    if beats and beats[-1].get("reveal") != len(lines):
        p.append("last beat must reveal all code lines")
    if not 50 <= words <= 100:
        p.append(f"narration is {words} words (want 50-100)")
    if not isinstance(s["tags"], list):
        p.append("tags must be a list")
    return p


def store_line(cfg):
    url = (cfg.get("store") or {}).get("url", "").strip()
    return f"Extended kit with error handling and a setup guide (paid, I sell this): {url}" if url else ""


def build_description(script, cfg):
    repo = cfg["channel"]["github_repo"]
    link = f"https://github.com/{repo}/blob/main/snippets/{script['slug']}.py"
    tags = " ".join("#" + t.replace(" ", "") for t in script["tags"][:5])
    parts = [script["description"].strip(),
             f"Free core code: {link}\nComment CODE and I'll reply with the link."]
    if store_line(cfg):
        parts.append(store_line(cfg))
    parts.append("The scenario and numbers in this video are illustrative, not a real client case. "
                 "The code is a working starting point, so test it on a copy of your files first.")
    parts.append(f"{tags} #Shorts #coding #automation")
    return "\n\n".join(parts)
