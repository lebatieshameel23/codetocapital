# Export Public Bank Holidays to CSV with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import pandas as pd

api = "https://date.nager.at/api/v3"
path = "/PublicHolidays/2025/US"
df = pd.read_json(api + path)
out = df[["date", "name"]]
out.to_csv("holidays.csv", index=False)
print(f"Saved {len(out)} holidays")
