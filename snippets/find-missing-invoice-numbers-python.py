# Find Missing Invoice Numbers with 9 Lines of Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import pandas as pd

df = pd.read_csv("invoices.csv")
seen = set(df["inv_id"])
full = set(range(min(seen), max(seen) + 1))
gaps = sorted(full - seen)
out = pd.DataFrame({"missing_id": gaps})
out.to_csv("missing.csv", index=False)
print(f"Found {len(gaps)} missing invoices")
