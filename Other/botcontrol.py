__module_name__ = 'Bot Control'
__module_version__ = '1.0'
__module_description__ = 'Starts and restarts supybot'


import xchat


def botcontrol(word, word_eol, userdata):
    channel = xchat.get_info('channel')
    if word[1].startswith('#startbot'):
        xchat.command('exec ' + "supybot -d /home/germain/.config/supybot/ParanoidMarvin.conf")
        xchat.command("me calls ParanoidMarvin to get his robotic ass here!")
    elif word[1].startswith('#restartbot'):
        xchat.command('exec ' + "kill -s 15 $(pidof -sx supybot); supybot -d /home/germain/.config/supybot/ParanoidMarvin.conf")
        xchat.command("me orders ParanoidMarvin to come back after taking a robotic nap.")
    return xchat.EAT_NONE


xchat.hook_print('Your Message', botcontrol)

print "\00304", __module_name__, "successfully loaded.\003"
