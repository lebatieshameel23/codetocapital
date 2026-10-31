# Isolate and Archive Newsletter Emails with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import imaplib
m = imaplib.IMAP4_SSL("imap.host.com")
m.login("me@host.com", "token")
m.select("INBOX")
_, ids = m.search(None, 'TEXT "opt out"')
uids = ids[0].split()
for u in uids:
    m.copy(u, "Archive")
    m.store(u, "+FLAGS", "\\Deleted")
print(f"Archived {len(uids)} items")
