# Get Email Alerts When a File Updates in Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import hashlib, smtplib, time
last = ""
while True:
    raw = open("data.csv", "rb").read()
    now = hashlib.md5(raw).digest()
    if last and now != last:
        m = smtplib.SMTP("localhost")
        m.sendmail("a@b", "c@d", "Alert")
        print("Alert sent: file changed")
    last = now; time.sleep(10)
