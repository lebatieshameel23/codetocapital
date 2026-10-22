# Find and Delete Duplicate Files Safely with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
from pathlib import Path
from hashlib import md5

seen = set()
for p in Path("files").rglob("*"):
    if p.is_file():
        h = md5(p.read_bytes()).digest()
        if h in seen:
            p.unlink()
        seen.add(h)
