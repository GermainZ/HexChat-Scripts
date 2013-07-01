__module_name__ = 'Screenshooter'
__module_version__ = '1.0'
__module_description__ = 'Takes and uploads screenshot'

import xchat


def screenshot(word, word_eol, userdata):
    if word[1].startswith('#screenshot'):
        bashCommand = 'scrot /tmp/screenshot.png; printf "::Screenshot captured: "; ~/bin/imgur-cli upload /tmp/screenshot.png | grep "original:" | cut -d " " -f 9'
        xchat.command('exec -o ' + bashCommand)
        return xchat.EAT_NONE


xchat.hook_print('Your Message', screenshot)

print("\00304", __module_name__, "successfully loaded.\003")
