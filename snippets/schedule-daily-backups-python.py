# Schedule Daily Backups with 10 Lines of Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import datetime, pathlib, shutil

src = pathlib.Path("live.db")
dst = pathlib.Path("backups")
dst.mkdir(exist_ok=True)
date = datetime.date.today().isoformat()
target = dst / f"backup_{date}.db"
if not target.exists():
    shutil.copy2(src, target)
    print(f"Saved: {target.name}")
