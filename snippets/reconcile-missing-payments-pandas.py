# Find Unpaid Invoices Across Two Sheets with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import pandas as pd

a = pd.read_csv("orders.csv")
b = pd.read_csv("payouts.csv")
m = a.merge(b, on="id", how="left")
missing = m[m["paid_date"].isna()]
missing.to_csv("unpaid.csv", index=False)
print(f"Found {len(missing)} unpaid")
