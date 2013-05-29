__module_name__ = 'Russian Roulette'
__module_version__ = '1.0'
__module_description__ = 'Russian Roulette'

import xchat
from random import choice, randint

guns = {}
actions = ("challenge", "challenge_reset", "help")
start_messages = ("%(nick)s spins the barrel...",)
wait_messages = ("%(nick)s, you can't fire twice in a row.",)
fire_messages = ("%(nick)s pulls the trigger.",)
life_messages = ("The gun clicks.", "Silence.", "The gun jams.",
                 "%(nick)s lives to see another day.",
                 "The chamber is empty.",)
death_messages = ("BANG!", "The bullet rips through %(nick)s's skull.",
                 "%(nick)s's body hits the ground with a heavy thud.",
                 "A blinding light is the last thing %(nick)s sees.",
                 "Blood splatters everywhere.",)
help_messages = ("Usage:  * Help: #roulette help",
                 "        * FreeForAll Game: #roulette",
                 ("        * Start Challenge: #roulette challenge <nick>"
                 " [nick] ..."),
                 "        * Continue Challenge: #roulette challenge",
                 "        * Reset Challenge: #roulette challenge_reset")


class Gun:
    def __init__(self, channel, challenger=None, challenged=None):
        self.bullets_max = 6
        self.bullets = self.bullets_max
        self.last_user = None
        self.channel = channel
        self.challenger = challenger
        self.challenged = challenged
        if challenger:
            self.append_text = "".join(["[", challenger, " vs ",
                                        ' vs '.join(challenged), "]"])
        else:
            self.append_text = "[FreeForAll - %s]" % self.channel

    def trigger(self, user):
        msg = ""
        msg = ''.join([self.append_text, " - "])
        if not self.last_user:
            msg = ''.join([msg, choice(start_messages), " "])
        if user != self.last_user:
            self.last_user = user
            msg = ''.join([msg, choice(fire_messages), " "])
            send_message(self.channel, user, msg)
            if randint(1, self.bullets) == 1:
                msg = ''.join(["\00304", choice(death_messages)])
                send_message(self.channel, user, msg)
                return True
            else:
                msg = ''.join(["\00302", choice(life_messages)])
                send_message(self.channel, user, msg)
            self.bullets -= 1
        else:
            send_message(self.channel, user, choice(wait_messages))
        return False


def send_message(channel, user, data):
    data = data % {'nick': user}
    xchat.command('msg ' + channel + ' \00307' + data)

def challenge(channel, user, args):
    if args and user in guns:
        send_message(channel, user, ("You're already in a challenge,"
                                    " %(nick)s. To pull the trigger,"
                                    " type '#roulette challenge'."))
    elif args:
        guns[user] = Gun(channel, user, args)
        for challenged in args:
            guns[challenged] = user
        send_message(channel, user, ''.join([("%(nick)s started a new"
                                              " challenge with... "),
                                              ', '.join(args), "!",
                                              (" '#roulette challenge'"
                                              " pulls the trigger!")]))
    else:
        if user in guns:
            if isinstance(guns[user], basestring):
                if guns[guns[user]].trigger(user):
                    clean_guns(guns[user])
                    send_message(channel, user, ("Challenge over!"))
            else:
                if guns[user].trigger(user):
                    clean_guns(user)
                    send_message(channel, user, ("Challenge over!"))
        else:
            send_message(channel, user, ("You're not in any challenge,"
                                         " %(nick)s. To challenge"
                                         " someone, type '#roulette"
                                         " challenge <nick> [nick]"
                                         " ...'"))

def challenge_reset(user):
    if user in guns:
        clean_guns(user)
        return "Challenge reset, %(nick)s,"
    else:
        return "You're not challenging anyone, %(nick)s."

def ffa(user, channel):
    if not 'global' in guns:
        guns['global'] = Gun(channel)
    if guns['global'].trigger(user):
        del guns['global']

def get_args(word):
    user = xchat.strip(word[0])
    try:
        action = xchat.strip(word[1].split(' ', 2)[1])
    except IndexError:
        action = None
    try:
        args = word[1].strip().split(' ', 2)[2].split(' ')
        args = [xchat.strip(v) for v in args]
    except IndexError:
        args = None
    return user, action, args

def handler(word, word_eol, userdata):
    channel = xchat.get_info('channel')
    command = xchat.strip(word[1].split(' ', 1)[0])
    if command == "#roulette":
        user, action, args = get_args(word)
        if not action:
            ffa(user, channel)
        elif action in actions:
            if action == "challenge":
                challenge(channel, user, args)
            elif action == "challenge_reset":
                send_message(channel, user, challenge_reset(user))
            elif action == "help":
                for msg in help_messages:
                    send_message(channel, user, msg)

def clean_guns(user):
    del guns[user]
    for key in guns.keys():
        if isinstance(guns[key], basestring) and guns[key] == user:
            del guns[key]


xchat.hook_print('Channel Msg Hilight', handler)
xchat.hook_print('Channel Message', handler)
xchat.hook_print('Your Message', handler)

print "\00304", __module_name__, "successfully loaded.\003"
