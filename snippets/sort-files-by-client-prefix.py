# Group Files by Client Prefix in 8 Lines of Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
from pathlib import Path

for f in Path("inbox").glob("*_*.*"):
    vendor = f.stem.split("_")[0]
    dest = Path("sorted") / vendor
    dest.mkdir(exist_ok=True)
    f.rename(dest / f.name)
print("Sorted files into vendor folders")
