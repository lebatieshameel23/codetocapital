"""Text-to-speech with word timings. Uses free edge-tts; --offline makes silent placeholder audio."""
import asyncio
import pathlib
import subprocess


def _duration(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)], text=True)
    return float(out.strip())


def _even_words(text, duration):
    toks = text.split()
    step = duration / max(1, len(toks))
    return [(w, i * step, (i + 1) * step) for i, w in enumerate(toks)]


async def _synth(text, voice, rate, path):
    import edge_tts
    try:
        comm = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    except TypeError:  # older edge-tts versions only emit word boundaries by default
        comm = edge_tts.Communicate(text, voice, rate=rate)
    words = []
    with open(path, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                s = chunk["offset"] / 1e7
                words.append((chunk["text"], s, s + chunk["duration"] / 1e7))
    return words


def synth_beat(text, voice, rate, path, offline=False):
    """Create audio for one beat. Returns (duration_seconds, [(word, start, end), ...])."""
    path = pathlib.Path(path)
    if offline:
        dur = max(1.5, len(text.split()) / 2.8)
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
             "anullsrc=r=24000:cl=mono", "-t", f"{dur:.2f}", "-c:a", "libmp3lame", str(path)],
            check=True)
        return dur, _even_words(text, dur)
    words = asyncio.run(_synth(text, voice, rate, path))
    dur = _duration(path)
    if len(words) < max(1, len(text.split()) // 2):  # sentence-level timings only -> spread evenly
        words = _even_words(text, dur)
    return dur, words
