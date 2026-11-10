# Extract Due Dates from PDF Invoices with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
from pathlib import Path
import re, csv
from pypdf import PdfReader
out = []
for p in Path('.').glob('*.pdf'):
    t = PdfReader(p).pages[0].extract_text()
    m = re.search(r'Due:\s*(\S+)', t)
    if m: out.append([p.name, m.group(1)])
with open('due.csv', 'w', newline='') as f:
    csv.writer(f).writerows(out)
