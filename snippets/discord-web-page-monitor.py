# Track Web Page Changes to Discord with 10 Lines of Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import pathlib, requests
u = 'https://example.com/rates'
hook = 'https://discord.com/webhook'
page = requests.get(u).text
p = pathlib.Path('cache.txt')
old = p.read_text() if p.exists() else ''
if page != old:
    requests.post(hook, json={'content': u})
    p.write_text(page)
    print('Alert sent: page updated')
