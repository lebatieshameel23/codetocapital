# Batch Rename and Clean Messy Files in Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
from pathlib import Path
from datetime import date
today = str(date.today())
for p in Path("docs").glob("*.pdf"):
    tag = p.stem.strip().replace(" ", "_")
    new = f"{today}_{tag}.pdf"
    p.rename(p.with_name(new))
    print(f"Renamed: {new}")
