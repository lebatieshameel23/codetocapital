# Split One Master CSV into Client Files with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import pandas as pd

df = pd.read_csv("master.csv")
for name, data in df.groupby("Client"):
    out = f"{name}.csv"
    data.to_csv(out, index=False)
    print(f"Saved {out}: {len(data)}")
