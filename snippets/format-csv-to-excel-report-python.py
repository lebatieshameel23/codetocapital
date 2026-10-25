# Format Raw CSV Data into Excel Reports with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import csv, openpyxl
from openpyxl.styles import Font
wb = openpyxl.Workbook()
ws = wb.active
for r in csv.reader(open("data.csv")):
    ws.append(r)
for c in ws[1]:
    c.font = Font(bold=True, color="1F4E79")
ws.column_dimensions["A"].width = 20
wb.save("report.xlsx")
