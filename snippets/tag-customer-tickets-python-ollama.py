# Tag Customer Tickets Fast with 8 Lines of Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import requests
url = "http://localhost:11434/api/generate"
prompt = "Tag (Urgent/Normal): Broken box"
payload = {"model": "llama3.2",
           "prompt": prompt,
           "stream": False}
res = requests.post(url, json=payload)
print(res.json()["response"].strip())
