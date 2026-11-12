# Summarize Customer Feedback Fast with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import requests
url = "http://localhost:11434/api/generate"
txt = open("feedback.txt").read()
payload = {"model": "llama3.2",
 "prompt": "One-line summary:\n" + txt,
 "stream": False}
res = requests.post(url, json=payload)
print(res.json()["response"].strip())
