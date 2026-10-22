# Find Duplicate Charges Fast with 8 Lines of Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import pandas as pd

df = pd.read_csv("charges.csv")
dupes = df[df.duplicated(
    subset=["client", "amount"], keep=False
)].sort_values("client")
dupes.to_csv("flagged.csv", index=False)
print(f"Flagged {len(dupes)} duplicates")
