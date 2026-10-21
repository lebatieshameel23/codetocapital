# Alert Discord When a File Changes with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import hashlib, requests
WEBHOOK = "https://discord.com/api/hook"
raw = open("terms.pdf", "rb").read()
h = hashlib.sha256(raw).hexdigest()
try: old = open(".h").read()
except: old = ""
if h != old:
    msg = {"content": "terms.pdf updated"}
    requests.post(WEBHOOK, json=msg)
    open(".h", "w").write(h)
