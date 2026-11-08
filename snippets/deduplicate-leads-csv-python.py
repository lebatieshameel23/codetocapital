# Deduplicate Messy CSV Leads Fast with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import pandas as pd

df = pd.read_csv("leads.csv")
df["date"] = pd.to_datetime(df["date"])
df.sort_values("date", inplace=True)
df.drop_duplicates("email", keep="last",
                   inplace=True)
df.to_csv("clean.csv", index=False)
print(f"{len(df)} unique leads saved")
