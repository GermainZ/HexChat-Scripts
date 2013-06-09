__module_name__ = 'Factoids'
__module_version__ = '1.0'
__module_description__ = 'Factoids'

import xchat
import sqlite3

conn = sqlite3.connect('/home/germain/.config/hexchat/addons/data/facts.db')
c = conn.cursor()

try:
    c.execute('''CREATE TABLE facts(title text, content text)''')
except Exception,e:
    pass

class data:
    allowed_chans = ["#gingerdx", "#atest"]
    commands = ["add", "remove", "list"]

def send_message(channel, msg):
    msg = msg
    xchat.command('msg ' + channel + ' ' + msg)

def get_args(word):
    user = xchat.strip(word[0])
    try:
        action = xchat.strip(word[1].split(' ', 2)[1])
    except IndexError:
        action = None
    try:
        args = xchat.strip(word[1].strip().split(' ', 2)[2])
        args = args.split(' ', 1)
    except IndexError:
        args = None
    if args:
        try:
            arg1 = args[0]
        except IndexError:
            arg1 = None
        try:
            arg2 = args[1]
        except IndexError:
            arg2 = None
    else:
        arg1 = None
        arg2 = None
    return user, action, arg1, arg2

def chan_command(word, word_eol, userdata):
    channel = xchat.get_info('channel')
    command = xchat.strip(word[1].split(' ', 1)[0])
    if channel.lower() in data.allowed_chans:
        user, action, title, content = get_args(word)
        if command == "#f":
            if action in data.commands:
                if action == data.commands[0]:
                    if title and content:
                        c.execute("DELETE FROM facts WHERE title=?", (title,))
                        c.execute("INSERT INTO facts VALUES (?, ?)", (title, content,))
                        conn.commit()
                    else:
                        send_message(channel, "Error inserting fact into database - specified title/content?")
                elif action == data.commands[1]:
                    if title:
                        c.execute("DELETE FROM facts WHERE title=?", (title,))
                        conn.commit()
                    else:
                        send_message(channel, "Error removing fact from database - specified title?")
                elif action == data.commands[2]:
                    c.execute("SELECT * FROM facts")
                    msg = "::\00306"
                    for row in c.fetchall():
                        msg = ''.join([msg, '\003: \00302"'.join(row), '"\003, \00306'])
                    send_message(channel, msg[:-6])
        elif command == "#give":
            fact = getfact(title)
            if fact:
                send_message(channel, "::%s: %s" % (action, fact))
        elif command.startswith("#"):
            title = command[1:]
            fact = getfact(title)
            if fact:
                send_message(channel, '::\00307' + fact)

def getfact(title):
        c.execute("SELECT * FROM facts WHERE title=?", (title,))
        try:
            fact = c.fetchone()[1]
            if fact.startswith("<reply>"):
                fact = fact.split("<reply>", 1)[1].strip()
            else:
                fact = "%s: %s" % (title, fact)
            return "%s" % fact
        except TypeError:
            return None
            raise


xchat.hook_print('Channel Msg Hilight', chan_command)
xchat.hook_print('Channel Message', chan_command)
xchat.hook_print('Your Message', chan_command)

print "\00304", __module_name__, "successfully loaded.\003"
