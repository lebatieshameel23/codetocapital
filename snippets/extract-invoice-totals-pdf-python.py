# Extract Invoice Totals from PDFs with 10 Lines of Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
from pypdf import PdfReader
import glob, re
lines = ["file,total"]
for f in glob.glob("*.pdf"):
    t = "".join(p.extract_text() or ""
        for p in PdfReader(f).pages)
    m = re.search(r"Total:\s*(\S+)", t)
    if m: lines.append(f"{f},{m.group(1)}")
open("out.csv", "w").write("\n".join(lines))
print("wrote out.csv")
