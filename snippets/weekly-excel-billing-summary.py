# Build Weekly Excel Reports with 10 Lines of Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import csv, openpyxl as ox
from openpyxl.styles import Font
wb = ox.Workbook()
ws = wb.active
for r in csv.reader(open("billing.csv")):
    ws.append(r)
for c in ws[1]: c.font = Font(bold=True)
ws.append(["Total", "=SUM(B2:B99)"])
wb.save("billing_summary.xlsx")
print("wrote billing_summary.xlsx")
