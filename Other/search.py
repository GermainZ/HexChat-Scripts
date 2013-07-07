__module_name__ = "Search"
__module_version__ = "1.0"
__module_description__ = "Searches channel messages by user, message or both" \
                         "and prints matches in a new window."

import xchat
from time import time, strftime, localtime
from shlex import split

networks = {}
RCOLORS = [19, 20, 22, 21, 25, 26, 27, 28, 29]


def color(name):
    """Returns a color code for the nickname"""
    i = 0
    col = 0
    for i in range(len(name)):
        col += ord(name[i])
        i += 1
    col %= len(RCOLORS)# // 1
    return '\003%s' % RCOLORS[col]

def new_msg(word, world_eol, userdata):
    """Adds messages to the network/channel they belong to, so we can use them
    later:
    networks = {network: {channel: [timestamp, nickname, message]}}
          e.g.  freenode  #mychan    s. since  "mynick"  "hello"
                                    the epoch

    The time stamp, nickname and message are added as three separate list
    entries.

    """
    channel = xchat.get_info("channel")
    network = xchat.get_info("network")
    if network not in networks:
        networks[network] = {}
    if channel not in networks[network]:
        networks[network][channel] = []
    user = xchat.strip(word[0])
    msg = xchat.strip(word[1])
    networks[network][channel].append([time(), user, msg])

def replace_arg(data, arg):
    """Highlights found instances of arg.

    arg is simply preceded by a fg/bg color combination, and followed by the
    default color escape code.

    """
    return data.replace(arg, "\00300,12%s\017" % arg)

def search(word, word_eol, userdata):
    """Searches whatever messages we have for any passed arguments.

    If userdata is equal to 'a', usernames and messages will be searched for
    matches.
    If userdata is equal to 'u', only usernames will be searched for matches.
    Finally, if userdata is equal to 'm', only messages will be searched for
    matches.

    Found matches are highlighted. The above rules are respected for
    highlighting matches.

    """
    channel = xchat.get_info("channel")
    network = xchat.get_info("network")
    if network not in networks:
        print("\00307Nothing to search in %s." % network)
        return
    if channel not in networks[network]:
        print("\00307Nothing to search in %s:%s." % (network, channel))
        return
    args = split(word_eol[1])
    msgs = []
    for msg in networks[network][channel]:
        # Convert the timestamp to H:M:S format, then get the nickname's color.
        timestamp = strftime("%H:%M:%S", localtime(msg[0]))
        ucolor = color(msg[1])
        found = False
        for arg in args:
            if userdata == 'a' and (arg in msg[1] or arg in msg[2]):
                found = True
                user = "%s%s%s" % (ucolor, replace_arg(msg[1], arg), ucolor)
                umsg = replace_arg(msg[2], arg)
            elif userdata == 'u' and arg in msg[1]:
                found = True
                user = "%s%s%s" % (ucolor, replace_arg(msg[1], arg), ucolor)
                umsg = msg[2]
            elif userdata == 'm' and arg in msg[2]:
                found = True
                user = ucolor
                umsg = replace_arg(msg[2], arg)
            if found:
                # Append result to msgs, which will be used later, and break
                # so the same match isn't counted multiple times if multiple
                # arguments are passed.
                msgs.append("%s\t%s\017: %s" % (timestamp, user, umsg))
                break
    if len(msgs) > 0:
        # Open a new dialog and print all found results in it.
        xchat.command("DIALOG Search")
        dialog = xchat.find_context(network, "Search")
        for msg in msgs:
            dialog.prnt(msg)
    else:
        print("\00307No results founds in %s:%s." % (network, channel))
    return xchat.EAT_ALL


xchat.hook_print("Your Message", new_msg)
xchat.hook_print("Your Action", new_msg)
xchat.hook_print("Channel Message", new_msg)
xchat.hook_print("Channel Msg Hilight", new_msg)
xchat.hook_print("Channel Action", new_msg)
xchat.hook_print("Channel Action Hilight", new_msg)

xchat.hook_command("SEARCH_ALL", search, 'a')
xchat.hook_command("SEARCH_USERS", search, 'u')
xchat.hook_command("SEARCH_MESSAGES", search, 'm')

print("\00304", __module_name__, "successfully loaded.\003")
