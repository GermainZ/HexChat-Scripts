__module_name__ = 'XDA User info'
__module_version__ = '1.0.12'
__module_description__ = 'Gets an XDA User\'s info'
 
import simplejson
import urllib
import urllib2
import xchat
import lxml.html
import threading

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

def handler( word, word_eol, userdata ):
    channel = xchat.get_info('channel')
    command, username = get_args(word)
    if channel.lower() in channels.allowed and command == "#userinfo":
        event = threading.Event()
        infothread = threading.Thread(target=get_user_info,
                                   args=(event, username))
        infothread.start()
        xchat.hook_timer(100, send_message, (event, channel))
        return xchat.EAT_NONE

def send_message(userdata):
    global msg
    event, channel = userdata
    if event.isSet():
        for message in msg:
            xchat.command('msg ' + channel + ' ' + message)
        event.clear()
        return 0
    else:
        return 1


def get_user_info(event, username):
    global msg
    url = google_query(username)
    if url is None:
        msg = ["Username %s not found." % username]
        event.set()
        return
    wpage = urllib2.urlopen(url)
    wpage = lxml.html.parse(wpage)
    stats_u = wpage.xpath('//div[@class="nametitle"]/descendant::*/text()')
    stats_t = wpage.xpath('//fieldset[@class="statistics_group"]/ul/li/span[@class="shade"]/text()')
    stats_v = wpage.xpath('//fieldset[@class="statistics_group"]/ul/li/text()')
    msg = ["Stats for %s (%s):" % (stats_u[0], stats_u[1])]
    msg.extend(["          %s%s" % (t, v) for t, v in zip(stats_t, stats_v)])
    msg.append("          <%s>" % url)
    event.set()

def google_query(username):
    baseurl = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&rsz=large&'
    query = urllib.urlencode({'q': "\"View Profile: %s\" site:xda-developers.com" % username})
    fullurl = baseurl + query.encode('utf8')
    response = urllib2.urlopen(fullurl)
    json = simplejson.loads(response.read())
    if json['responseStatus'] == 200 and len(json['responseData']['results']) >= 1:
        results = json ['responseData'] ['results']
        for item in results:
            url = item['url'].encode('utf8')
            for  key, value in replace_dict.iteritems():
                url = url.replace(key, value)
            if url.startswith("http://forum.xda-developers.com/member.php?u="):
                return url
            #~ else:
                #~ print str(url)
    else:
        #~ print "resp: " + str(json['responseStatus'])
        #~ print "len: " + str(len(json['responseData']['results']))
        return

xchat.hook_print('Channel Msg Hilight', handler)
xchat.hook_print('Channel Message', handler)
xchat.hook_print('Your Message', handler)

print "\00304", __module_name__, "successfully loaded.\003"
