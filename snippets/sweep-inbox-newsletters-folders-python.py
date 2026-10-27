# Sweep Inbox Newsletters into Folders with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import imaplib
M = imaplib.IMAP4_SSL("imap.mail.com")
M.login("me@mail.com", "app_pass")
M.select("INBOX")
q = 'HEADER List-Unsubscribe ""'
_, data = M.search(None, q)
dry_run = True
for i in data[0].split():
    if dry_run: print("Would move:", i)
    else: M.copy(i, "Newsletters")
