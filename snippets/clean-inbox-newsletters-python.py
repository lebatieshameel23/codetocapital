# Clean Inbox Newsletters with 9 Lines of Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import imaplib
m = imaplib.IMAP4_SSL("imap.gmail.com")
m.login("user@gmail.com", "app_pass")
m.select("INBOX")
_, ids = m.search(None, 'HEADER List-ID ""')
for uid in ids[0].split():
    print(f"Dry-run match: {uid.decode()}")
m.close()
m.logout()
