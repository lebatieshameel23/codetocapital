# Extract Action Items from Meeting Notes with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import requests
url = "http://localhost:11434/api/generate"
notes = open("notes.txt").read()
data = {
    "model": "llama3.2",
    "prompt": f"Extract tasks:\n{notes}",
    "stream": False,
}
out = requests.post(url, json=data).json()
print(out["response"].strip())
