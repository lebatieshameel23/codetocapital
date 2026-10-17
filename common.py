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


# ---------- duplicate guard ----------
_STOP = {"a", "an", "and", "the", "of", "in", "into", "to", "with", "for", "from", "on", "your", "you", "stop",
         "using", "use", "fast", "faster", "quick", "quickly", "safe", "safely", "easy", "easily", "python",
         "pandas", "script", "tool", "kit", "cli", "lines", "line", "one", "hundreds", "automatically",
         "auto", "how", "make", "build", "no", "more", "by", "is", "are", "this", "that", "it", "stop"}


def _stem(w):
    for suf in ("ing", "ers", "er", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[: -len(suf)]
    return w


def topic_words(entry):
    text = " ".join(str(entry.get(k, "")) for k in ("slug", "title", "product_name")).lower()
    return {_stem(w) for w in re.findall(r"[a-z]{3,}", text)} - {_stem(w) for w in _STOP}


def script_library(hist):
    """Everything already made or queued, as {slug, title, product_name, pillar} dicts (some fields may be missing)."""
    lib, seen = [], set()

    def add(e):
        key = (e.get("slug") or "") + "|" + (e.get("title") or "")
        if key not in seen:
            seen.add(key)
            lib.append(e)
    for e in hist.get("library", []):
        add(e)
    for e in hist.get("videos", {}).values():
        add({"slug": e.get("slug"), "title": e.get("title"), "pillar": e.get("pillar")})
    for f in queue_files():
        try:
            q = json.loads(f.read_text())
            add({k: q.get(k) for k in ("slug", "title", "product_name", "pillar")})
        except (ValueError, OSError):
            pass
    snip = ROOT / "snippets"
    if snip.exists():
        for f in snip.glob("*.py"):
            add({"slug": f.stem})
    for t in hist.get("used_titles", []):
        add({"title": t})
    return lib


def too_similar(script, library, threshold=0.4):
    """Return a human-readable reason if `script` repeats something in `library`, else None."""
    import difflib
    mine, slug, title = topic_words(script), script.get("slug", ""), script.get("title", "").lower()
    for e in library:
        if slug and e.get("slug") == slug:
            return f"the slug '{slug}' is already used by '{e.get('title') or slug}'"
        other = e.get("title", "") or ""
        if other and difflib.SequenceMatcher(None, title, other.lower()).ratio() >= 0.72:
            return f"the title is nearly identical to '{other}'"
        theirs = topic_words(e)
        if mine and theirs and len(mine & theirs) / len(mine | theirs) >= threshold:
            return f"it covers the same task as '{other or e.get('slug')}'"
    return None


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
