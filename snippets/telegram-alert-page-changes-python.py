# Send Telegram Alerts When a Web Page Changes in Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import hashlib, requests
url = "https://example.com/status"
cur = hashlib.sha1(
    requests.get(url).content).hexdigest()
if cur != "old_hash_value":
    api = "https://api.telegram.org/botX/"
    data = {"chat_id": 123, "text": url}
    requests.post(api + "sendMessage",
                  json=data)
    print("Telegram alert delivered")
