# Flag Inventory Discrepancies Across CSVs with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import pandas as pd
w = pd.read_csv("scan.csv")
s = pd.read_csv("system.csv")
df = w.merge(s, on="sku")
df["diff"] = df["counted"] - df["system"]
bad = df[df["diff"] != 0]
bad.to_csv("mismatch.csv", index=False)
print(f"Flagged {len(bad)} mismatches")
