# Organize Files by Month with 10 Lines of Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import shutil, time
from pathlib import Path

for p in Path("inbox").glob("*.*"):
    ym = time.strftime("%Y-%m",
        time.gmtime(p.stat().st_mtime))
    dest = Path("archive") / ym
    dest.mkdir(parents=True, exist_ok=True)
    shutil.move(p, dest / p.name)
    print(f"filed {p.name} -> {ym}")
