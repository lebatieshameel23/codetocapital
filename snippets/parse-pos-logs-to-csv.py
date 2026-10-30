# Parse Daily Sales Logs into CSV with 9 Lines of Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
from pathlib import Path
import re, csv
data = []
for f in Path("logs").glob("*.txt"):
    txt = f.read_text()
    val = re.findall(r"Total: \$(\S+)", txt)
    if val: data.append((f.name, val[0]))
with open("totals.csv", "w") as out:
    csv.writer(out).writerows(data)
