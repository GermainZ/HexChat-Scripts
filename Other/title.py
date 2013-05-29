__module_name__ = 'Page Title'
__module_version__ = '1.0'
__module_description__ = 'Gets links\' titles'

import time
import re
import urllib2
import threading
import xchat
import lxml.html

color = {'white': "\00300", 'black': "\00301", 'blue': "\00302",
        'green': "\00303", 'lred': "\00304", 'brown': "\00305",
        'purple': "\00306", 'orange':"\00307", 'yellow': "\00308",
        'lgreen': "\00309", 'cyan': "\00310", 'lcyan': "\00311",
        'lblue': "\00312", 'pink': "\00313", 'grey': "\00314",
        'lgrey': "\00315", 'bold': "\002", 'nobold': "\002",
        'nocolor': "\003"}
users = {}
times = {}
ignorep = 0
msg = ""
done = 0


class Channels(object):
    allowed = [ "#gingerdx", "#atest" ]


class IgnoreList(object):
    start = ['=== Searching for']
    end = ['=== Powered by ']
    single = ['::']


def title(word, word_eol, userdata):
    global ignorep
    channel = xchat.get_info('channel').lower()
    ignore = 0
    if channel in Channels.allowed:
        word_eol[0] = xchat.strip(word_eol[0])
        for item in IgnoreList.start:
            if item in word_eol[0]:
                ignorep=1
        for item in IgnoreList.end:
            if ignorep == 1 and item in word_eol[0]:
                ignorep=0
        for item in IgnoreList.single:
            if item in word_eol[0]:
                ignore=1
        if ignore == 0 and ignorep == 0 and "http" in word_eol[0]:
            url=word_eol[0]
            temp_urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]'
                              '|[!*\(\),]|(?:%[0-9a-fA-F]'
                              '[0-9a-fA-F]))+', url)
            urls=[]
            for url in temp_urls:
                if not url.lower().endswith(('.jpg', '.gif', '.png', '.jpeg',
                                     '.pdf')):
                    urls.append(url)
            if not urls:
                return xchat.EAT_NONE
            event = threading.Event()
            titlethread = threading.Thread(target=gettitle,
                                           args=(event, urls, word[0]))
            titlethread.start()
            xchat.hook_timer(100, sendMessage, (event, channel))
            return xchat.EAT_NONE


def gettitle(event, urls, username):
    global users, time, msg, done
    done = 0
    for url in urls:
        #resetc = threading.Thread(target=resetcount)
        #resetc.start()
        if (username in times and 
            times[username] + 15 < time.time()):
            users[username] = 0
        if username in users:
            users[username] += 1
        else:
            users[username] = 1
        times[username] = time.time()
        if users[username] > 3:
            msg = ''.join([color["lgrey"], 'Hey ', username,
                            ', don\'t be so abusive!'])
            break
        ##wtitle = lxml.html.parse(url).find(".//title").text
        try:
            req = urllib2.Request(url, headers={'User-Agent': "HexChat"})
            wpage = urllib2.urlopen(req)
            wtitle = lxml.html.parse(wpage)
            wtitle = wtitle.xpath("//title/text()")[0]
            #soup = BeautifulSoup.BeautifulSoup(urllib2.urlopen(url))
            #wtitle = soup.title.string
            msg = ''.join([color["lgrey"], '::Title: ', color["orange"],
                          wtitle, color["lgrey"], ' - ', color["cyan"],
                          url])
            msg = msg.encode('utf-8')
        except Exception, e:
            msg = ''.join([color["lgrey"],
                          '::Could not get webpage title for ',
                          url, " because of: ", str(e)])
            #xchat.prnt(str(e))
        event.set()
    done = 1


def resetcount():
    global users
    time.sleep(10)
    users.clear()


def sendMessage(userdata):
    global msg
    event, channel = userdata
    if event.isSet():
        xchat.command('msg ' + channel + ' ' + msg)
        event.clear()
        if done == 1:
            return 0
        else:
            return 1
    else:
        return 1


xchat.hook_print('Channel Message', title)
xchat.hook_print('Your Message', title)

print "\00304", __module_name__, "successfully loaded.\003"
