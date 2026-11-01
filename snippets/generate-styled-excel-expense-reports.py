# Generate Styled Excel Expense Reports with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import csv, openpyxl
wb = openpyxl.Workbook()
ws = wb.active
with open('expenses.csv') as f:
    for cat, amt in csv.reader(f):
        ws.append([cat, float(amt)])
for c in ws['B']:
    c.number_format = '$#,##0.00'
wb.save('expense_report.xlsx')
print('Created expense_report.xlsx')
