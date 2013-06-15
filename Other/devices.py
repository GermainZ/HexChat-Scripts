__module_name__ = 'Devices'
__module_version__ = '1.0'
__module_description__ = 'Keeps lists of user\'s devices'

import xchat
import pickle

data_loc = "/home/germain/.config/hexchat/addons/data/devices.pkl"
try:
    users = pickle.load(open(data_loc, "rb"))
except IOError:
    users = {}

class data:
    allowed_chans = ["#gingerdx", "#atest"]
    commands = ["add", "remove", "list", "search"]

def send_message(channel, msg):
    try:
        xchat.command('msg ' + channel + ' \00307' + msg)
    except TypeError:
        for message in msg:
            xchat.command('msg ' + channel + ' \00307' + message)

def get_args(word):
    user = xchat.strip(word[0])
    try:
        action = xchat.strip(word[1].split(' ', 2)[1])
    except IndexError:
        action = None
    try:
        arg = xchat.strip(word[1].strip().split(' ', 2)[2])
        #~ arg = args.split(' ', 1)
    except IndexError:
        arg = None
    return user, action, arg

def chan_command(word, word_eol, userdata):
    channel = xchat.get_info('channel')
    command = xchat.strip(word[1].split(' ', 1)[0])
    if channel.lower() in data.allowed_chans:
        user, action, arg = get_args(word)
        if command == "#d":
            if action in data.commands:
                if action == data.commands[0]:
                    if arg:
                        send_message(channel, add_device(user, arg))
                    else:
                        send_message(channel, "Usage: #d add <device>")
                elif action == data.commands[1]:
                    if arg:
                        send_message(channel, rem_device(user, arg))
                    else:
                        send_message(channel, "Usage: #d remomve <device_id>")
                elif action == data.commands[2]:
                    if arg:
                        send_message(channel, list_devices(arg))
                    else:
                        send_message(channel, "Usage: #d list <user>")
                elif action == data.commands[3]:
                    if arg:
                        send_message(channel, search_devices(arg))
                    else:
                        send_message(channel, "Usage: #d search <device>")
            elif action:
                arg = action
                send_message(channel, list_devices(arg))

def search_devices(query):
    msg = ["Results for %s:" % query]
    for user in users:
        for device in users[user]:
            if query.lower() in device.lower():
                msg.append("  %s: %s" % (user, device))
    if len(msg) == 1:
        msg = "No results found for %s." % query
    return msg

def add_device(user, device):
    global users
    try:
        users[user].append(device)
    except KeyError:
        users[user] = [device]
    if len(users[user]) > 10:
            return "%s, you can only have up to 10 devices at once." % (user)
    pickle.dump(users, open(data_loc, "wb"))
    return "Device %s added to %s's list." % (device, user)

def rem_device(user, device_id):
    global users
    try:
        users[user]
    except KeyError:
        return "User %s not found." % user
    try:
        device = users[user].pop(int(device_id) - 1)
    except ValueError:
        return "Usage: #d remove <device_id>"
    except IndexError:
        return "Device #%s does not exist." % device_id
    if len(users[user]) == 0:
        del users[user]
    pickle.dump(users, open(data_loc, "wb"))
    return "Device %s removed from %s's list." % (device, user)

def list_devices(user):
    global users
    try:
        users[user]
    except KeyError:
        return "User %s not found." % user
    msg = ["%s's devices:" % user]
    for i, device in enumerate(users[user]):
        msg.append("  %s: %s" % (i + 1, device))
    return msg


xchat.hook_print('Channel Msg Hilight', chan_command)
xchat.hook_print('Channel Message', chan_command)
xchat.hook_print('Your Message', chan_command)

print "\00304", __module_name__, "successfully loaded.\003"
