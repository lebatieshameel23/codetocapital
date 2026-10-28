# Catch Invoice Math Errors Fast with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import pandas as pd

df = pd.read_csv("orders.csv")
calc = (df["qty"] * df["price"]).round(2)
bad = df[df["total"].round(2) != calc]
bad.to_csv("mismatches.csv", index=False)
print(f"Flagged {len(bad)} broken rows")
