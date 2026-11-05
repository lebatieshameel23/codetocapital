# Safely Triage Newsletter Subscriptions with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import imaplib
m = imaplib.IMAP4_SSL("imap.mail.com")
m.login("user@mail.com", "app_pwd")
m.select("INBOX")
q = '(HEADER List-Unsubscribe "")'
_, data = m.search(None, q)
ids = data[0].split()
print(f"Dry run: {len(ids)} to archive")
# m.copy(b",".join(ids), "Archive")
m.logout()
