__module_name__ = "URL Hints Mode"
__module_version__ = "1.0"
__module_description__ = ("Allows easy accessing of URLs. When active, links"
                          "can be launched with a few keypresses.")

import hexchat
import re
from time import time


# networks['network']['channel'][index] = {'time': message time, 'data': word,
#                                          'event': type of event}
networks = {}
uids = []
halt = False
hint_hook = None
hooked = False
scrollback = hexchat.get_prefs("text_max_lines")
# from http://daringfireball.net/2010/07/improved_regex_for_matching_urls
url_regex = (r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)"
              "(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+"
              "(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|"
              "[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")
url_regex = re.compile(url_regex)

def pretty_print(msg):
    print("\00307>> " + msg)

def eat_event(word, word_eol, event):
    if halt is True:
        return hexchat.EAT_PLUGIN

def new_msg(word, word_eol, event, attr):
    if halt is True:
        return hexchat.EAT_PLUGIN
    network = hexchat.get_info("network")
    channel = hexchat.get_info("channel")
    if not network in networks:
        networks[network] = {}
    if not channel in networks[network]:
        networks[network][channel] = []
    if attr.time is 0:
        msg_time = int(time())
    else:
        msg_time = attr.time
    networks[network][channel].append({'time': msg_time, 'data': word,
                                       'event': event})
    if len(networks[network][channel]) > scrollback:
        del networks[network][channel][-1]

def urlify(event, words, network, channel):
    ret = []
    try:
        msg = words[1].split(' ')
    except IndexError as err:
        # Not sure why this fails sometimes
        pretty_print(str(words))
        pretty_print(str(err))
        return words
    for word in msg:
        match = url_regex.match(word)
        if match is not None:
            uid = str(len(uids))
            uids.append(match.group(0))
            word += " \00307[%s]\017" % uid
        ret.append(word)
    return words[:1] + [' '.join(ret)] + words[2:]

def open_url(word, word_eol, userdata):
    global hooked
    network, channel = userdata
    if word[0] in ["65293", "65421", "65307"]:
        hooked = False
        hide_hints(network, channel)
        hexchat.unhook(hint_hook)
        # Escape
        if word[0] == "65307":
            return
        inputbox = hexchat.get_info("inputbox")
        hexchat.command("settext")
        try:
            hint = int(inputbox)
        except ValueError:
            pretty_print("Hint must be an integer!")
            return
        if hint <= len(uids):
            hexchat.command("URL %s" % uids[hint])
        else:
            pretty_print("Hint not found!")

def hide_hints(network, channel):
    global halt
    hexchat.command("clear")
    halt = True
    for msg in networks[network][channel]:
        hexchat.emit_print(msg['event'], *msg['data'], time=msg['time'])
    halt = False

def show_hints(word, word_eol, userdata):
    global halt, hint_hook, hooked
    if not word == ['88', '21', '\x18', '1']:
        return
    if hooked is True:
        hexchat.unhook(hint_hook)
        hooked = False
    network = hexchat.get_info("network")
    channel = hexchat.get_info("channel")
    if network not in networks or channel not in networks[network]:
        pretty_print("Nothing to print.")
        return
    hexchat.command("clear")
    uids.clear()
    halt = True
    hooked = True
    for msg in networks[network][channel]:
        data = urlify(msg['event'], msg['data'], network, channel)
        hexchat.emit_print(msg['event'], *data, time=msg['time'])
    pretty_print("Hint to follow?")
    hint_hook = hexchat.hook_print("Key Press", open_url, (network, channel))
    halt = False
    return hexchat.EAT_ALL


hooks = ["Your Message", "Channel Message",
         "Channel Msg Hilight", "Your Action", "Channel Action",
         "Channel Action Hilight", "Join", "Change Nick", "Part",
         "Part with Reason", "Quit"]
for hook in hooks:
    hexchat.hook_print_attrs(hook, new_msg, hook, hexchat.PRI_LOWEST)
    hexchat.hook_print(hook, eat_event, hook, hexchat.PRI_HIGHEST)
hexchat.hook_print("Key Press", show_hints)

print("\00304", __module_name__, "successfully loaded.\003")


