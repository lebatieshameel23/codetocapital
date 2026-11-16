# Format Sales Summaries in Excel with 10 Lines of Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import pandas as pd, openpyxl as ox
df = pd.read_csv("sales.csv")
rep = df.groupby("rep")["rev"].sum()
rep.to_excel("summary.xlsx", "Sales")
wb = ox.load_workbook("summary.xlsx")
ws = wb.active
for cell in ws["B"][1:]:
    cell.number_format = "$#,##0"
wb.save("summary.xlsx")
print("saved summary.xlsx")
