# Lookup City and State from ZIP Codes in Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import csv, requests
rows = [["zip", "city", "state"]]
for z in ["90210", "10001", "60601"]:
    u = f"https://api.zippopotam.us/us/{z}"
    p = requests.get(u).json()["places"][0]
    city, st = p["place name"], p["state"]
    rows.append([z, city, st])
with open("out.csv", "w", newline="") as f:
    csv.writer(f).writerows(rows)
