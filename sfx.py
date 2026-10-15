"""Synthesised sound effects (typing clicks, whoosh, ding, pop). Generated from scratch, so no licensing worries."""
import math
import random
import struct
import wave

SR = 24000
GAIN = {"click": 0.10, "whoosh": 0.30, "ding": 0.25, "pop": 0.25}


def _click(rnd):
    n = int(0.03 * SR)
    return [math.exp(-i / (0.004 * SR)) * (0.6 * (rnd.random() * 2 - 1) + 0.4 * math.sin(2 * math.pi * 2400 * i / SR))
            for i in range(n)]


def _whoosh(rnd):
    n, lp, out = int(0.4 * SR), 0.0, []
    for i in range(n):
        x = i / n
        lp += (0.05 + 0.5 * x) * ((rnd.random() * 2 - 1) - lp)   # low-pass whose cutoff sweeps upward
        out.append(math.sin(math.pi * x) ** 2 * lp * 1.8)
    return out


def _ding():
    n = int(0.6 * SR)
    return [math.exp(-i / (0.18 * SR)) * (0.6 * math.sin(2 * math.pi * 880 * i / SR)
                                           + 0.4 * math.sin(2 * math.pi * 1320 * i / SR)) for i in range(n)]


def _pop():
    n = int(0.08 * SR)
    return [math.exp(-i / (0.02 * SR)) * math.sin(2 * math.pi * 650 * i / SR) for i in range(n)]


def write(events, total, path):
    """events: [(kind, time_seconds)]. Writes a mono 16-bit wav of length `total`."""
    rnd = random.Random(7)
    buf = [0.0] * (int(total * SR) + SR)
    makers = {"click": lambda: _click(rnd), "whoosh": lambda: _whoosh(rnd), "ding": _ding, "pop": _pop}
    for kind, t in events:
        start = int(max(0.0, t) * SR)
        g = GAIN[kind]
        for i, s in enumerate(makers[kind]()):
            if start + i < len(buf):
                buf[start + i] += s * g
    data = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in buf[:int(total * SR)])
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)
