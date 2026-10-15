"""Render a 1080x1920 Short built for retention: typed code in a terminal, word-synced captions,
sound effects, a punch-in on every beat, a drifting grid, and a seamless loop ending.

Usage:
    python render_video.py content/samples/episode-01.json --out out/ep1.mp4 [--offline] [--ep 7]
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

import sfx
import voice
from common import ROOT, load_config, validate_script

W, H, FPS = 1080, 1920, 30
BG, GRID = (30, 30, 46), (37, 37, 57)
TERM, BAR, EDGE = (17, 17, 27), (24, 24, 37), (46, 46, 68)
GREEN, YELLOW, WHITE, GRAY = (0, 255, 102), (255, 230, 0), (255, 255, 255), (108, 112, 134)

TX0, TY0, TX1, TY1 = 50, 430, 1030, 1135
CODE_X, CODE_Y, LINE_H = TX0 + 80, TY0 + 100, 46
OUT_SEP_Y = TY0 + 100 + 10 * LINE_H + 8

MONO = ["assets/fonts/mono.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/System/Library/Fonts/Menlo.ttc", "C:/Windows/Fonts/consola.ttf"]
BOLD = ["assets/fonts/bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"]


def font(cands, size):
    for c in cands:
        p = pathlib.Path(c)
        p = p if p.is_absolute() else ROOT / c
        if p.exists():
            return ImageFont.truetype(str(p), size)
    sys.exit("No usable font found. Put mono.ttf and bold.ttf into assets/fonts/.")


def clean(text):
    """Drop emoji / non-BMP characters the fonts can't draw."""
    return re.sub(r"[^\u0000-\uFFFF]", "", text)


def a(c):
    return c + (255,)


# ---------- syntax colouring ----------
KW = {"import", "from", "for", "in", "if", "else", "elif", "def", "return", "with", "as", "while",
      "try", "except", "class", "and", "or", "not", "None", "True", "False", "lambda", "await",
      "async", "raise", "pass", "break", "continue"}
TOKEN = re.compile(
    r"(#.*$)|([rbfRBF]?\"[^\"]*\"|[rbfRBF]?'[^']*')|(\b\d[\d_.]*\b)|([A-Za-z_]\w*(?=\())|([A-Za-z_]\w*)|(\s+)|(.)")
COLORS = [(98, 114, 164), (241, 250, 140), (189, 147, 249), (80, 250, 123), None, None, (248, 248, 242)]


def tokens(line):
    out = []
    for m in TOKEN.finditer(line):
        g, txt = m.lastindex, m.group(0)
        if g == 5:
            col = (255, 121, 198) if txt in KW else (248, 248, 242)
        elif g == 6:
            col = WHITE
        else:
            col = COLORS[g - 1]
        out.append((txt, col))
    return out


def wrap(text, f, max_w):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if f.getlength(t) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def stroke_text(d, xy, text, f, fill, anchor="ls", sw=7):
    d.text(xy, text, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0))


def make_layers(script, cfg, ep, f_ln, f_hook, f_hdr):
    """bg: plain background with vertical grid (horizontal lines are animated per frame).
    layer/mask: everything static that sits on top (terminal window, hook, handle, episode number)."""
    bg = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(bg)
    for x in range(0, W, 60):
        d.line([(x, 0), (x, H)], fill=GRID, width=1)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([TX0, TY0, TX1, TY1], radius=26, fill=a(TERM), outline=a(EDGE), width=3)
    d.rounded_rectangle([TX0, TY0, TX1, TY0 + 70], radius=26, fill=a(BAR))
    d.rectangle([TX0 + 3, TY0 + 40, TX1 - 3, TY0 + 70], fill=a(BAR))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([TX0 + 28 + i * 40, TY0 + 23, TX0 + 50 + i * 40, TY0 + 45], fill=a(c))
    d.line([(TX0 + 3, OUT_SEP_Y), (TX1 - 3, OUT_SEP_Y)], fill=a(EDGE), width=2)
    d.text((TX0 + 160, TY0 + 46), "script.py  (illustrative demo)", font=f_ln, fill=a(GRAY), anchor="ls")
    hook = wrap(clean(script["hook_text"]), f_hook, 940)[:3]
    for i, hl in enumerate(hook):
        d.text((W // 2, 215 + i * 90), hl, font=f_hook, fill=a(WHITE), anchor="ms")
    uy = 215 + (len(hook) - 1) * 90 + 32
    d.rectangle([W // 2 - 90, uy - 4, W // 2 + 90, uy + 4], fill=a(GREEN))
    d.text((60, 118), clean(cfg["channel"]["handle"]), font=f_hdr, fill=a(GREEN), anchor="ls")
    if ep:
        d.text((W - 60, 118), f"#{ep:03d}", font=f_hdr, fill=a(GRAY), anchor="rs")
    return bg, layer, layer.getchannel("A")


# ---------- audio ----------
def build_voice(script, cfg, workdir, offline):
    beats, words, t0, parts = [], [], 0.0, []
    for i, b in enumerate(script["beats"]):
        mp3 = workdir / f"beat{i}.mp3"
        dur, w = voice.synth_beat(clean(b["voice"]), cfg["voice"]["name"], cfg["voice"]["rate"], mp3, offline)
        beats.append({**b, "start": t0, "dur": dur})
        words += [(txt, t0 + s, t0 + e, i) for txt, s, e in w]
        parts.append(mp3)
        t0 += dur
    lst = workdir / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    voice_mp3 = workdir / "voice.mp3"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c:a", "libmp3lame", "-q:a", "2", str(voice_mp3)], check=True)
    return beats, words, t0, voice_mp3


def mix_audio(voice_mp3, sfx_wav, cfg, workdir):
    """Voice + sound effects (+ optional music from assets/music). Returns the mixed file."""
    inputs = ["-i", str(voice_mp3)]
    n = 1
    if sfx_wav:
        inputs += ["-i", str(sfx_wav)]
        n += 1
    mdir = ROOT / "assets" / "music"
    music = sorted(mdir.glob("*.mp3")) if mdir.exists() else []
    chain = "[0:a]volume=1[v0]"
    labels = "[v0]"
    if sfx_wav:
        chain += ";[1:a]volume=1[v1]"
        labels += "[v1]"
    if music:
        inputs += ["-stream_loop", "-1", "-i", str(music[0])]
        chain += f";[{n}:a]volume={cfg.get('music_volume', 0.07)}[v{n}]"
        labels += f"[v{n}]"
        n += 1
    if n == 1:
        return voice_mp3
    out = workdir / "mixed.wav"
    chain += f";{labels}amix=inputs={n}:duration=first:dropout_transition=0,volume={n}[a]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", chain,
                    "-map", "[a]", str(out)], check=True)
    return out


def caption_chunks(words):
    """Group words into short on-screen chunks (<= 3 words, <= 18 chars)."""
    chunks, cur = [], []
    for w in words:
        txt = clean(w[0])
        if not txt.strip():
            continue
        if cur and (len(cur) >= 3 or len(" ".join(x[0] for x in cur + [w])) > 18 or cur[0][3] != w[3]):
            chunks.append(cur)
            cur = []
        cur.append((txt,) + tuple(w[1:]))
    if cur:
        chunks.append(cur)
    return chunks


def punch(img, s):
    big = img.resize((int(W * s), int(H * s)), Image.BILINEAR)
    ox, oy = (big.width - W) // 2, (big.height - H) // 2
    return big.crop((ox, oy, ox + W, oy + H))


def render(script, out_path, cfg, offline=False, ep=None):
    problems = validate_script(script)
    if problems:
        sys.exit("Script problems:\n - " + "\n - ".join(problems))
    out_path = pathlib.Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = script["code"].split("\n")
    motion = cfg.get("motion", True)

    f_code, f_ln, f_out = font(MONO, 32), font(MONO, 26), font(MONO, 32)
    f_cap, f_badge = font(BOLD, 80), font(BOLD, 56)
    f_hook, f_hdr = font(BOLD, 74), font(MONO, 34)
    cw = f_code.getlength("M")
    bg, layer, mask = make_layers(script, cfg, ep, f_ln, f_hook, f_hdr)
    green_layer = Image.new("RGB", (W, H), GREEN)

    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        beats, words, speech_end, voice_mp3 = build_voice(script, cfg, td, offline)
        total = speech_end + 0.12            # no dead air at the end: the video loops straight into its hook
        chunks = caption_chunks(words)

        prev_reveal, events = 0, []
        for i, b in enumerate(beats):
            b["prev"], b["reveal"] = prev_reveal, b.get("reveal", prev_reveal)
            prev_reveal = b["reveal"]
            b["chars"] = sum(len(x) + 1 for x in lines[b["prev"]:b["reveal"]])
            b["type_dur"] = min(b["dur"] * 0.75, b["chars"] / 32) if b["chars"] else 0
            if i > 0:
                events.append(("whoosh", b["start"] - 0.04))
            for k in range(0, b["chars"], 2):
                events.append(("click", b["start"] + b["type_dur"] * k / b["chars"]))
            if b.get("output"):
                events.append(("ding", b["start"] + b["type_dur"] + 0.3))
            if b.get("badge"):
                events.append(("pop", b["start"] + 0.05))
        sfx_wav = None
        if cfg.get("sfx", True):
            sfx_wav = td / "sfx.wav"
            sfx.write(events, total, sfx_wav)
        audio = mix_audio(voice_mp3, sfx_wav, cfg, td)

        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(audio), "-t", f"{total:.2f}",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out_path)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

        for n in range(int(total * FPS)):
            t = n / FPS
            img = bg.copy()
            d = ImageDraw.Draw(img)
            off = int(t * 36) % 60                       # drifting grid
            for y in range(off - 60, H, 60):
                d.line([(0, y), (W, y)], fill=GRID, width=1)
            img.paste(layer, (0, 0), mask)
            d.rectangle([0, 36, int(W * min(1, t / total)), 44], fill=GREEN)

            bi = max((i for i, b in enumerate(beats) if b["start"] <= t), default=0)
            b = beats[bi]
            local = t - b["start"]
            typed = b["chars"] if b["type_dur"] == 0 else int(b["chars"] * min(1, local / b["type_dur"]))
            typing = typed < b["chars"]

            remaining, last_x, last_y = typed, None, None
            for li in range(b["reveal"]):
                line = lines[li]
                if li >= b["prev"]:
                    if remaining < 0:
                        break
                    take = min(len(line), remaining)
                    remaining -= len(line) + 1
                else:
                    take = len(line)
                y = CODE_Y + li * LINE_H
                d.text((CODE_X - 20, y), str(li + 1), font=f_ln, fill=GRAY, anchor="rs")
                x, shown = CODE_X, 0
                for txt, col in tokens(line):
                    seg = txt[:max(0, take - shown)]
                    if seg:
                        d.text((x, y), seg, font=f_code, fill=col, anchor="ls")
                    x += cw * len(seg)
                    shown += len(txt)
                    if shown >= take:
                        break
                last_x, last_y = CODE_X + cw * take, y
            if last_x is not None and (typing or int(t * 2) % 2 == 0):
                d.rectangle([last_x + 2, last_y - 28, last_x + cw - 2, last_y + 6], fill=GREEN)

            flash = 0.0
            for k in range(bi, -1, -1):
                bk = beats[k]
                if bk.get("output"):
                    shown_at = bk["start"] + bk["type_dur"] + 0.3
                    if t >= shown_at:
                        d.text((CODE_X - 20, OUT_SEP_Y + 52), "$ python script.py", font=f_out, fill=GRAY, anchor="ls")
                        d.text((CODE_X - 20, OUT_SEP_Y + 100), clean(bk["output"]), font=f_out, fill=GREEN, anchor="ls")
                        if t - shown_at < 0.18:
                            flash = 0.14 * (1 - (t - shown_at) / 0.18)
                        break

            if b.get("badge"):
                txt = clean(b["badge"])
                tw = f_badge.getlength(txt)
                d.rounded_rectangle([W // 2 - tw / 2 - 36, 1170, W // 2 + tw / 2 + 36, 1262], radius=46, fill=YELLOW)
                d.text((W // 2, 1234), txt, font=f_badge, fill=(20, 20, 30), anchor="ms")

            active = None
            for ch in chunks:
                if ch[0][1] <= t:
                    active = ch
            active = active or (chunks[0] if chunks else None)
            if active:
                space = f_cap.getlength(" ")
                widths = [f_cap.getlength(w[0].upper()) for w in active]
                x = W / 2 - (sum(widths) + space * (len(active) - 1)) / 2
                for w, ww in zip(active, widths):
                    col = YELLOW if w[1] <= t < w[2] + 0.05 else WHITE
                    stroke_text(d, (x, 1395), w[0].upper(), f_cap, col, "ls", 8)
                    x += ww + space

            if motion and local < 0.25:                  # quick punch-in at the start of every beat
                img = punch(img, 1 + 0.05 * (1 - local / 0.25))
            if flash:
                img = Image.blend(img, green_layer, flash)
            proc.stdin.write(img.tobytes())
        proc.stdin.close()
        if proc.wait() != 0:
            sys.exit("ffmpeg failed")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--out", default=None)
    ap.add_argument("--offline", action="store_true", help="silent placeholder voice (no network)")
    ap.add_argument("--ep", type=int, default=None, help="episode number shown top right")
    args = ap.parse_args()
    script = json.loads(pathlib.Path(args.script).read_text())
    out = args.out or str(ROOT / "out" / f"{script['slug']}.mp4")
    print("rendered:", render(script, out, load_config(), args.offline, args.ep))


if __name__ == "__main__":
    main()
