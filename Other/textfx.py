__module_name__ = 'TextFX'
__module_version__ = '1.0'
__module_description__ = 'Changes the text\'s style and colors'
 
import xchat, math

rainbow_desc = "Colorizes the text using the colors of the rainbow"
color_desc = "Colorizes the text"
colors = {'white': "\00300", 'black': "\00301", 'blue': "\00302",
        'green': "\00303", 'lred': "\00304", 'brown': "\00305",
        'purple': "\00306", 'orange':"\00307", 'yellow': "\00308",
        'lgreen': "\00309", 'cyan': "\00310", 'lcyan': "\00311",
        'lblue': "\00312", 'pink': "\00313", 'grey': "\00314",
        'lgrey': "\00315", 'bold': "\002", 'nobold': "\002",
        'nocolor': "\003"}


def rainbow_trigger(word, word_eol, userdata):
    channel = xchat.get_info('channel')
    try:
        xchat.command("msg %s %s" % (channel, rainbow(word_eol[1])))
    except IndexError:
        xchat.prnt("/RAINBOW <message> %s" % (rainbow_desc))
    return xchat.EAT_ALL

def rainbow(word):
    rainbow_colors = ["\00306", "\00313", "\00302", "\00303",
            "\00308", "\00307", "\00304"]
    output = []
    i = 0
    index = 7
    for char in word:
        output.append(rainbow_colors[index - 1])
        output.append(char)
        index = int(math.ceil(7 * (len(word) - i) / float(len(word))))
        i += 1
    return ''.join(output)

def color(word, word_eol, userdata):
    try:
        channel = xchat.get_info('channel')
        xchat.command("msg %s %s" % (channel,
                                     colors[word[1]] + word_eol[2]))
    except KeyError:
        supported_colors = "Supported colors: "
        for key in colors.keys():
            supported_colors += colors[key] + key + ' '
        xchat.prnt("Syntax: /COLOR <color> <message>")
        xchat.prnt(supported_colors)
    except IndexError:
        xchat.prnt("/COLOR <color> <message> %s" % (color_desc))
    return xchat.EAT_ALL

xchat.hook_command("RAINBOW", rainbow_trigger, help="/RAINBOW <message> %s" % (rainbow_desc))
xchat.hook_command("COLOR", color, help="/COLOR <color> <message> %s" % (color_desc))

print "\00304", __module_name__, "successfully loaded.\003"
