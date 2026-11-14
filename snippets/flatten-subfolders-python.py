# Flatten Cluttered Subfolders in 10 Lines of Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
from pathlib import Path
import shutil
src, dst = Path("nested"), Path("flat")
dst.mkdir(exist_ok=True)
for f in src.rglob("*"):
    if f.is_file():
        target = dst / f.name
        if not target.exists():
            shutil.move(f, target)
print("Flattened files into", dst)
