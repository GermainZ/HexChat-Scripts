__module_name__ = 'Trivia'
__module_version__ = '1.0'
__module_description__ = 'Trivia'

import xchat
import re
import random
import os
import math
import pickle

counter = 0
answer = None
xchat_timer = None
actions = ("random", "stats", "skip")
users_loc = "/home/germain/.config/hexchat/addons/data/trivia.pkl"
try:
    users = pickle.load(open(users_loc, "rb"))
except IOError:
    users = {}


def send_message(channel, user, data):
    data = data % {'nick': user}
    xchat.command('msg ' + channel + ' \00307' + data)

def get_args(word):
    user = xchat.strip(word[0])
    try:
        action = xchat.strip(word[1].split(' ', 2)[1])
    except IndexError:
        action = None
    try:
        args = word[1].strip().split(' ', 2)[2].split('*')
        args = [xchat.strip(v) for v in args]
    except IndexError:
        args = None
    return user, action, args

def correct_answer(channel, user):
    global counter, answer
    score = (40 - counter)
    update_score(user, score)
    send_message(channel, user, ''.join(["%(nick)s gains ", str(score),
                                         " points! Answer(s): ", 
                                         ', '.join(answer)]))
    reset()
    pickle.dump(users, open(users_loc, "wb"))

def update_score(user, score):
    global users
    try:
        users[user] += score
    except KeyError:
        users[user] = score
def reset():
    global answer, counter
    xchat.unhook(xchat_timer)
    answer = None
    counter = 0

def handler(word, word_eol, userdata):
    global answer
    channel = xchat.get_info('channel')
    command = xchat.strip(word[1].split(' ', 1)[0])
    user, action, args = get_args(word)
    if answer:
        if (word[1].lower() in [x.lower() for x in answer]):
            correct_answer(channel, user)
        elif action == actions[2]: #skip
            update_score(user, -10)
            reset()
            send_message(channel, user, "SKIP: %(nick)s [-10 points]")
            getquestion(channel, user)
    elif command == "#trivia" or command == "#t":
            if not action:
                getquestion(channel, user)
            elif action in actions:
                if action == actions[0]: # random
                    getquestion(channel, user)
                elif action == actions[1]: # stats
                    send_message(channel, user, str(users))

def getquestion(channel, user):
    global answer, xchat_timer
    question, answer = getrandom()
    if question:
        send_message(channel, user, '\002' + question)
        if len(answer) == 1:
            mask = re.sub(r'[a-zA-Z0-9]', '-', answer[0])
            send_message(channel, user, "Answer: %s" % mask )
        else:
            send_message(channel, user, "Multiple answers available.")
        xchat_timer = xchat.hook_timer(10000, timer, (channel, user))

def hint_randomizer(answers, fraction):
    hint = ""
    for answer in answers:
        words = answer.split(' ')
        for word in words:
            divider = int(math.ceil(len(word) * fraction))
            if divider == len(word):
                divider -= 1
            show = word[:divider]
            blank = word[divider:]
            blank = re.sub('\w', '-', blank)
            hint = ''.join([hint, show, blank, " "])
        hint = ''.join([hint[:-1], ", "])
    return hint[:-2]

def timer(userdata):
    global counter, answer
    if not answer:
        return False
    channel, user = userdata
    counter += 10
    if counter == 10:
        hint = hint_randomizer(answer, 0.2)
    elif counter == 20:
        hint = hint_randomizer(answer, 0.4)
    elif counter == 30:
        hint = hint_randomizer(answer, 0.6)
    elif counter == 40:
        send_message(channel, user, ''.join(["Round over! Answer(s): ",
                                             ', '.join(answer)]))
        answer = None
        counter = 0
        return False
    hint_str = " seconds have passed. Hint %s: " % (counter/10)
    send_message(channel, user, ''.join([str(counter), hint_str, hint]))
    return True

def getrandom():
    tdir = "/home/germain/.config/hexchat/addons/data/trivia/"
    rand_file = tdir + random.choice(os.listdir(tdir))
    data = random.choice(list(open(rand_file))).rstrip()
    data1 = data.split('*', 1)[0]
    data2 = data.split('*', 1)[1].split('*')
    return data1, data2


xchat.hook_print('Channel Msg Hilight', handler)
xchat.hook_print('Channel Message', handler)
xchat.hook_print('Your Message', handler)

print("\00304", __module_name__, "successfully loaded.\003")
