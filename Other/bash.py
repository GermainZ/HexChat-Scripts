__module_name__ = 'Bash'
__module_version__ = '1.0'
__module_description__ = 'Executes bash commands'

import os
import xchat


def exec_command(word, word_eol, userdata):
    if word[1].startswith('#exec'):
        bashCommand = ''.join(word_eol[1].split(' ', 1)[1])
        user = os.popen("whoami").read().strip()
        host = os.popen("hostname").read().strip()
        xchat.command('say ' + user + '@' + host + ':~$ ' + bashCommand)
        xchat.command('exec -o ' + bashCommand)
        return xchat.EAT_NONE
    elif word[1].startswith('#summem'):
        arg = ''.join(word_eol[1].split(' ', 1)[1])
        arg_ = "[" + arg[:1] + "]" + arg[1:]
        command = 'mem=`ps aux | grep ' + arg_ + ' | while IFS=" " read -ra line; do echo ${line[5]}; done | paste -sd+ | bc`; echo Memory usage of ' + arg + ': $mem KB'
        xchat.command('exec -o ' + command)

xchat.hook_print('Your Message', exec_command)

print "\00304", __module_name__, "successfully loaded.\003"
