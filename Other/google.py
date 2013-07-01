__module_name__ = 'Google'
__module_version__ = '1.0'
__module_description__ = 'Google'

import xchat
import json
from multiprocessing.pool import ThreadPool
try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen
replace_dict = {'<b>' : "", '</b>': "", '&lt': "<", '&gt': ">", '&amp': "&",
                '&quot;':"\"", '&#39;': "\'"}

def send_message(args):
    result, pool, context = args
    pool.close()
    for msg in result:
        context.command("say " + msg)

def google(word, word_eol, userdata):
    if word[1].startswith("#google"):
        results = '3'
    elif word[1].startswith("#g"):
        results = '1'
    else:
        return
    context = xchat.get_context()
    search = ' '.join(word[1].split(' ')[1:])
    pool = ThreadPool(processes=1)
    pool.apply_async(google_query, (search, results, pool, context),
                     callback=send_message)
    return

def google_query(search, results, pool, context):
    baseurl = ("http://ajax.googleapis.com/ajax/services/search/"
               "web?v=1.0&rsz=%s&" % results)
    url = baseurl + "&q=" + search.rstrip()
    resp = urlopen(url)
    resp = json.loads(resp.read().decode())
    if resp.get('responseStatus') == 200:
        results = resp.get('responseData').get('results')
        if len(results) < 1:
            return (["No results found"], pool, context)
        items = []
        for item in results:
            title = item['title']
            for key, value in replace_dict.items():
                title = title.replace(key, value)
            items.append("%s: \00302<%s>" % (title, item['url']))
        return (items, pool, context)
    else:
        return (["An error has occured."], pool, context)

xchat.hook_print("Your Message", google)
xchat.hook_print("Channel Message", google)

print("\00304", __module_name__, "successfully loaded.\003")
