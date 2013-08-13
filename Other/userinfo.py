__module_name__ = 'XDA User info'
__module_version__ = '1.0.12'
__module_description__ = 'Gets an XDA User\'s info'
 
import json
import xchat
import lxml.html
from multiprocessing.pool import ThreadPool
try:
    from urllib.request import urlopen
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlopen, urlencode

msg = []
replace_dict = {'%3B': ';', '%3F': '?', '%2F': '/','%3A': ':', '%23': '#',
                '%26': '&', '%3D': '=', '%2B': '+', '%24': '$', '%2C': ',',
                '%20': ' ', '%25': '%', '%3C': '<', '%3E': '>', '%7E': '~',
                '%7B': '{', '%7D': '}', '%7C': '|', '%5C': '\\', '%5E': '^',
                '%5B': '[', '%5D': ']', '%60': '`', '%40': '@'}

class channels:
    allowed = [ "#gingerdx", "#xda-devs", "#atest" ]

def get_args(word):
    try:
        command = xchat.strip(word[1].split(' ', 1)[0]).rstrip()
    except IndexError:
        command = None
    try:
        username = xchat.strip(word[1].split(' ', 1)[1]).rstrip()
    except IndexError:
        username = None
    return command, username

def handler(word, word_eol, userdata):
    channel = xchat.get_info('channel')
    command, username = get_args(word)
    if channel.lower() in channels.allowed and command == "#userinfo":
        context = xchat.get_context()
        pool = ThreadPool(processes=1)
        pool.apply_async(get_user_info, (username, pool, context),
                         callback=send_message)
        return

def send_message(args):
    result, pool, context = args
    pool.close()
    for msg in result:
        context.command("say " + msg)

def get_user_info(username, pool, context):
    global msg
    url = google_query(username)
    if url is None:
        return (["Username %s not found." % username], pool, context)
    wpage = urlopen(url)
    wpage = lxml.html.parse(wpage)
    stats_u = wpage.xpath('//div[@class="nametitle"]/descendant::*/text()')
    stats_t = wpage.xpath('//fieldset[@class="statistics_group"]/ul/li/span[@class="shade"]/text()')
    stats_v = wpage.xpath('//fieldset[@class="statistics_group"]/ul/li/text()')
    msg = ["Stats for %s (%s):" % (stats_u[0], stats_u[1])]
    msg.extend(["          %s%s" % (t, v) for t, v in zip(stats_t, stats_v)])
    msg.append("          <%s>" % url)
    return (msg, pool, context)


def google_query(username):
    baseurl = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&rsz=1&'
    url = baseurl + urlencode({'q': ("\"View Profile: %s\""
                                     " site:xda-developers.com" % username)})
    resp = urlopen(url)
    resp = json.loads(resp.read().decode())
    if resp.get('responseStatus') == 200:
        results = resp.get('responseData').get('results')
        if len(results) < 1:
            return
        for item in results:
            url = item['url']
            for  key, value in replace_dict.items():
                url = url.replace(key, value)
            if url.startswith("http://forum.xda-developers.com/member.php"):
                return url

xchat.hook_print('Channel Msg Hilight', handler)
xchat.hook_print('Channel Message', handler)
xchat.hook_print('Your Message', handler)

print("\00304", __module_name__, "successfully loaded.\003")
