# Automate Daily Exchange Rates to CSV with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import csv, requests
url = "https://api.frankfurter.app/latest"
r = requests.get(url, params={"from":"USD"})
rates = r.json()["rates"]
with open("rates.csv", "w") as f:
    w = csv.writer(f)
    w.writerows(rates.items())
print("Updated rates.csv with live FX data")
