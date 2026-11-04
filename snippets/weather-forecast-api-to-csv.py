# Fetch 7-Day Weather Forecasts to CSV with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import requests, pandas as pd
u = "https://api.open-meteo.com/v1/forecast"
p = {"latitude": 40.7, "longitude": -74.0,
     "daily": "temperature_2m_max"}
r = requests.get(u, params=p).json()
pd.DataFrame(r["daily"]).to_csv(
    "weather.csv", index=False
)
print("Saved weather.csv")
