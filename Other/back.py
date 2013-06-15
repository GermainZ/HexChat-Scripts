__module_name__ = 'Back message'
__module_version__ = '1.0'
__module_description__ = 'Customized back messages in current tab'
 
import xchat
from time import time


away_time = 0
away_reason = None

def away(word, word_eol, userdata):
    global away_time, away_reason
    away_time = time()
    away_reason = word[1]

def back(word, word_eol, userdata):
    away_duration = time() - away_time
    m, s = divmod(away_duration, 60)
    h, m = divmod(m, 60)
    away_duration = "%d:%02d:%02d" % (h, m, s)
    print "You are no longer marked as being away ('%s' for %s)" % (away_reason, away_duration)

xchat.hook_command("AWAY", away)
xchat.hook_command("BACK", back)

print "\00304", __module_name__, "successfully loaded.\003"
