__module_name__ = 'Lyrics'
__module_version__ = '1.0'
__module_description__ = 'Fetches song lyrics'

import xchat
import lxml.html
import urllib
import threading


color = {'white': "\00300", 'black': "\00301", 'blue': "\00302",
        'green': "\00303", 'lred': "\00304", 'brown': "\00305",
        'purple': "\00306", 'orange':"\00307", 'yellow': "\00308",
        'lgreen': "\00309", 'cyan': "\00310", 'lcyan': "\00311",
        'lblue': "\00312", 'pink': "\00313", 'grey': "\00314",
        'lgrey': "\00315", 'bold': "\002", 'nobold': "\002",
        'nocolor': "\017"}
msg = []


class channels:
    allowed = ["#gingerdx", "#atest"]


def sendMessage(userdata):
    global msg
    event, channel = userdata
    if event.isSet():
        for line in msg:
            xchat.command('msg ' + channel + ' ' + line.encode('utf-8'))
        msg = []
        event.clear()
        return 0
    else:
        return 1


def lyricwikicase(s):
    """Return a string in LyricWiki case.
    Substitutions are performed as described at 
    <http://lyrics.wikia.com/LyricWiki:Page_Names>.
    Essentially that means capitalizing every word and substituting certain 
    characters."""

    words = s.split()
    newwords = []
    for word in words:
        newwords.append(word[0].capitalize() + word[1:])
    s = "_".join(newwords)
    s = s.replace("<", "Less_Than")
    s = s.replace(">", "Greater_Than")
    s = s.replace("#", "Number_") # FIXME: "Sharp" is also an allowed substitution
    s = s.replace("[", "(")
    s = s.replace("]", ")")
    s = s.replace("{", "(")
    s = s.replace("}", ")")
    s = urllib.urlencode([(0, s)])[2:]
    return s


def getlyrics(event, artist, title):
    """Get and return the lyrics for the given song.
    Raises an IOError if the lyrics couldn't be found.
    Raises an IndexError if there is no lyrics tag.
    Returns None if there are no lyrics (it's instrumental)."""

    global msg

    #url = lyricwikiurl(artist, title)
    url = "http://lyrics.wikia.com/index.php?search=" + "%s:%s" % (lyricwikicase(artist), lyricwikicase(title))
    try:
        doc = urllib.urlopen(url)
        doc = lxml.html.parse(doc)
    except IOError,e:
        msg.append(color["lgrey"] + str(e))
        event.set()
        return

    try:
        lyricbox = doc.getroot().cssselect(".lyricbox")[0]
    except IndexError:
        msg.append(color["lgrey"] + "Couldn't get lyrics.")
        event.set()
        return

    # look for a sign that it's instrumental
    if len(doc.getroot().cssselect(".lyricbox a[title=\"Instrumental\"]")):
        msg.append(color["lgrey"] + "Song is instrumental.")
        event.set()
        return

    # prepare output
    lyrics = []
    if lyricbox.text is not None:
        lyrics.append(lyricbox.text)
    for node in lyricbox:
        if str(node.tag).lower() == "br":
            pass
            #lyrics.append("\n")
        if node.tail is not None:
            lyrics.append(node.tail)
    #lyrics_text = "".join(lyrics).strip()
    #lyrics_text = lyrics_text.split('\n', 4)
    msg.append(color["cyan"] + artist + " - " + title)
    for line in lyrics[:4]:
        msg.append(color["lcyan"] + line)
    msg.append(color["cyan"] + "::Lyrics from: " + doc.docinfo.URL)
    event.set()
    return


def lyricswiki(word, word_eol, userdata):
    channel = xchat.get_info('channel').lower()
    if channel in channels.allowed and word[1].startswith('#lyrics'):
        command = word[1].split(' ', 1)[1]
        try:
            artist = command.split(',', 1)[0].strip()
            title = command.split(',', 1)[1].strip()
        except:
            try:
                artist = command.split('-', 1)[0].strip()
                title = command.split('-', 1)[1].strip()
            except:
                for line in ("Usage:", "       !lyrics artist - song",
                             "    or !lyrics artist, song"):
                    line = color["lcyan"] + line
                    xchat.command('msg ' + channel + ' ' + line)
                return xchat.EAT_NONE
        event = threading.Event()
        lyricsthread = threading.Thread(target=getlyrics,
                                   args=(event, artist, title))
        lyricsthread.start()
        xchat.hook_timer(100, sendMessage, (event, channel))
        return xchat.EAT_NONE


xchat.hook_print('Channel Msg Hilight', lyricswiki)
xchat.hook_print('Channel Message', lyricswiki)
xchat.hook_print('Your Message', lyricswiki)

print "\00304", __module_name__, "successfully loaded.\003"
