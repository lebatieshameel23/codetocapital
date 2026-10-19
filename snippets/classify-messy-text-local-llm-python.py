# Classify Messy Text Fast with Python and Local AI
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import requests
url = "http://localhost:11434/api/generate"
for t in ["Refund order", "App crashes"]:
    p = f"Classify as Bug or Billing: {t}"
    data = {"model":"phi3","prompt":p,
            "stream":False}
    r = requests.post(url, json=data).json()
    print(t, "->", r["response"].strip())
