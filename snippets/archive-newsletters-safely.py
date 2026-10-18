# Archive Newsletters Safely with Python IMAP
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import imaplib; DRY_RUN = True
m = imaplib.IMAP4_SSL("imap.mail.com")
m.login("user@mail.com", "pass")
m.select("INBOX")
q = 'HEADER List-Unsubscribe ""'
_, [b] = m.search(None, q)
ids = b.split()
print(f"Dry run: {len(ids)} to move")
if not DRY_RUN:
    for i in ids: m.copy(i, "Archive")
