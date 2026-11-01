# Combine Every Monthly CSV into One File with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import glob
import pandas as pd

files = glob.glob("monthly_*.csv")
dfs = [pd.read_csv(f) for f in files]
out = pd.concat(dfs, ignore_index=True)
out.to_csv("combined.csv", index=False)
print(f"Combined {len(files)} reports")
