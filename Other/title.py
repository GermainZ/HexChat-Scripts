__module_name__ = 'Page Title'
__module_version__ = '1.0'
__module_description__ = 'Gets links\' titles'

import re
try:
    from urllib.request import urlopen, Request
    from urllib.parse import urlparse
except ImportError:
    from urllib2 import urlopen, Request, urlparse
from multiprocessing.pool import ThreadPool
import xchat
import lxml.html


allowed_chans = ["#gingerdx", "#atest"]

def title(word, word_eol, userdata):
    channel = xchat.get_info('channel').lower()
    if channel in allowed_chans:
        urls = re.findall("(?<!<)http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]"
                          "|[!*\(\),]|(?:%[0-9a-fA-F]"
                          "[0-9a-fA-F]))+", xchat.strip(word_eol[0]))
        if len(urls) > 0:
            context = xchat.get_context()
            pool = ThreadPool(processes=1)
            pool.apply_async(gettitle, (urls, pool, context),
                             callback=send_message)

def gettitle(urls, pool, context):
    result = []
    for url in urls:
        try:
            req = Request(url, headers={'User-Agent': "HexChat"})
            wpage = urlopen(req)
            domain = urlparse(url).netloc
            wtitle = lxml.html.parse(wpage)
            wtitle = wtitle.xpath("//title/text()")[0]
            wtitle = ' '.join(wtitle.split()) # Remove line breaks and tabs
            msg = "Title: %s (at \00307<%s>\017)" % (wtitle, domain)
        except Exception:
            pass
            #return None
        result.append(msg)
    return (result, pool, context)

def send_message(args): #result, pool, context):
    if args is None:
        return
    result, pool, context = args
    pool.close()
    for msg in result:
        context.command("say " + msg)


xchat.hook_print("Channel Message", title)
xchat.hook_print("Your Message", title)

print("\00304", __module_name__, "successfully loaded.\003")
