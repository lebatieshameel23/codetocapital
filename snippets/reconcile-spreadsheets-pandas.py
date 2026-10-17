# Stop Using VLOOKUP: Reconcile Spreadsheets in Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import pandas as pd
inv = pd.read_csv("invoices.csv")
bank = pd.read_csv("bank.csv")
m = inv.merge(bank, on="id", how="left")
m["paid"] = m["amount_y"].notna()
m.to_csv("reconciled.csv", index=False)
print(f"Reconciled {len(m)} rows")
