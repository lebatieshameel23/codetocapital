# Calculate Profit Margins Across Two CSVs with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import pandas as pd

store = pd.read_csv("store.csv")
costs = pd.read_csv("costs.csv")
df = store.merge(costs, on="sku")
df["margin"] = df["price"] - df["cost"]
df.to_csv("margins.csv", index=False)
print(f"Wrote {len(df)} margin records")
