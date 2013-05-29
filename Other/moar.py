__module_name__ = 'Moar'
__module_version__ = '1.0'
__module_description__ = 'Moar'

import xchat
import random
import re

# Quickly adapted from supybot

def aol(text):
    """<text>

    Returns <text> as if an AOLuser had said it.
    """
    text = text.replace(' you ', ' u ')
    text = text.replace(' are ', ' r ')
    text = text.replace(' love ', ' <3 ')
    text = text.replace(' luv ', ' <3 ')
    text = text.replace(' too ', ' 2 ')
    text = text.replace(' to ', ' 2 ')
    text = text.replace(' two ', ' 2 ')
    text = text.replace('fore', '4')
    text = text.replace(' for ', ' 4 ')
    text = text.replace('be', 'b')
    text = text.replace('four', ' 4 ')
    text = text.replace(' their ', ' there ')
    text = text.replace(', ', ' ')
    text = text.replace(',', ' ')
    text = text.replace("'", '')
    text = text.replace('one', '1')
    smiley = random.choice(['<3', ':)', ':-)', ':D', ':-D'])
    text += ' '.join(['', smiley, smiley, smiley])
    return text

def jeffk(text):
    """<text>

    Returns <text> as if JeffK had said it himself.
    """
    def randomlyPick(L):
        return random.choice(L)
    def quoteOrNothing(m):
        return randomlyPick(['"', '']).join(m.groups())
    def randomlyReplace(s, probability=0.5):
        def f(m):
            if random.random() < probability:
                return m.expand(s)
            else:
                return m.group(0)
        return f
    def randomExclaims(m):
        if random.random() < 0.85:
            return ('!' * random.randrange(1, 5)) + m.group(1)
        else:
            return '.' + m.group(1)
    def randomlyShuffle(m):
        L = list(m.groups())
        random.shuffle(L)
        return ''.join(L)
    def lessRandomlyShuffle(m):
        L = list(m.groups())
        if random.random() < .4:
            random.shuffle(L)
        return ''.join(L)
    def randomlyLaugh(text, probability=.3):
        if random.random() < probability:
            if random.random() < .5:
                insult = random.choice([' fagot1', ' fagorts',
                                            ' jerks', 'fagot' ' jerk',
                                            'dumbshoes', ' dumbshoe'])
            else:
                insult = ''
            laugh1 = random.choice(['ha', 'hah', 'lol', 'l0l', 'ahh'])
            laugh2 = random.choice(['ha', 'hah', 'lol', 'l0l', 'ahh'])
            laugh1 = laugh1 * random.randrange(1, 5)
            laugh2 = laugh2 * random.randrange(1, 5)
            exclaim = random.choice(['!', '~', '!~', '~!!~~',
                                         '!!~', '~~~!'])
            exclaim += random.choice(['!', '~', '!~', '~!!~~',
                                          '!!~', '~~~!'])
            if random.random() < 0.5:
                exclaim += random.choice(['!', '~', '!~', '~!!~~',
                                              '!!~', '~~~!'])
            laugh = ''.join([' ', laugh1, laugh2, insult, exclaim])
            text += laugh
        return text
    if random.random() < .03:
        return randomlyLaugh('NO YUO', probability=1)
    alwaysInsertions = {
        r'er\b': 'ar',
        r'\bthe\b': 'teh',
        r'\byou\b': 'yuo',
        r'\bis\b': 'si',
        r'\blike\b': 'liek',
        r'[^e]ing\b': 'eing',
        }
    for (r, s) in alwaysInsertions.iteritems():
        text = re.sub(r, s, text)
    randomInsertions = {
        r'i': 'ui',
        r'le\b': 'al',
        r'i': 'io',
        r'l': 'll',
        r'to': 'too',
        r'that': 'taht',
        r'[^s]c([ei])': r'sci\1',
        r'ed\b': r'e',
        r'\band\b': 'adn',
        r'\bhere\b': 'hear',
        r'\bthey\'re': 'their',
        r'\bthere\b': 'they\'re',
        r'\btheir\b': 'there',
        r'[^e]y': 'ey',
        }
    for (r, s) in randomInsertions.iteritems():
        text = re.sub(r, randomlyReplace(s), text)
    text = re.sub(r'(\w)\'(\w)', quoteOrNothing, text)
    text = re.sub(r'\.(\s+|$)', randomExclaims, text)
    text = re.sub(r'([aeiou])([aeiou])', randomlyShuffle, text)
    text = re.sub(r'([bcdfghkjlmnpqrstvwxyz])([bcdfghkjlmnpqrstvwxyz])',
                  lessRandomlyShuffle, text)
    text = randomlyLaugh(text)
    if random.random() < .4:
        text = text.upper()
    return text

def send_message(channel, data):
    xchat.command('msg ' + channel + ' \00307' + data)

def moar(word, word_eol, userdata):
    channel = xchat.get_info('channel')
    command = xchat.strip(word[1].split(' ', 1)[0])
    if command == "#moar":
        text = xchat.strip(word[1].split(' ', 1)[1])
        send_message(channel, jeffk(aol("moaarrr %s!!! MMMOOOOOAAAAAARRRRRRRR!!!" % text)))

xchat.hook_print('Channel Msg Hilight', moar)
xchat.hook_print('Channel Message', moar)
xchat.hook_print('Your Message', moar)
