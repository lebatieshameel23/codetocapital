# Monitor Website Uptime Hourly with 10 Lines of Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import time, urllib.request as u
from datetime import datetime as dt
url = "https://example.com"
t0 = time.time()
try:
    with u.urlopen(url, timeout=5) as r:
        s = r.status
except Exception: s = "DOWN"
ms = round((time.time() - t0) * 1000)
print(f"{dt.now():%H:%M} {url} {s} {ms}ms")
