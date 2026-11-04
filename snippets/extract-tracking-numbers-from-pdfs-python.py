# Extract Tracking Numbers from PDFs with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import glob, re
from pypdf import PdfReader as PR

out = []
for path in glob.glob("slips/*.pdf"):
    text = PR(path).pages[0].extract_text()
    m = re.search(r"TRK-\d{8}", text)
    if m:
        out.append((path, m.group()))
print(f"Saved {len(out)} tracking numbers")
