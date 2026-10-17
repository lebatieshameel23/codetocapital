# Sort Hundreds of Files into Folders with 8 Lines of Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import csv, shutil, os

for r in csv.DictReader(open("map.csv")):
    src, dst = r["file"], r["folder"]
    if os.path.exists(src):
        os.makedirs(dst, exist_ok=True)
        shutil.move(src, dst)
print("Files sorted.")
