# Check SSL Expiration on a Schedule with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import ssl, socket, time
h = "example.com"
c = ssl.create_default_context()
s = c.wrap_socket(socket.socket(),
                  server_hostname=h)
s.connect((h, 443))
t = s.getpeercert()["notAfter"]
e = time.mktime(time.strptime(
    t, "%b %d %H:%M:%S %Y %Z"))
print(f"{h}: {int(e-time.time())//86400}d")
