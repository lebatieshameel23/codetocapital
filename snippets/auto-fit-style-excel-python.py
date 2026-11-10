# Auto-Fit and Style Raw Excel Sheets with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import openpyxl as ox
wb = ox.load_workbook("sales.xlsx")
ws = wb.active
cd = ws.column_dimensions
for col in ws.columns:
    w = max(len(str(c.value)) for c in col)
    cd[col[0].column_letter].width = w + 3
for c in ws["C"][1:]:
    c.number_format = "$#,##0.00"
wb.save("styled.xlsx")
