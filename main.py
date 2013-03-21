import sys, io, os

#from threading  import Thread, Lock
from core.ui    import Interface
from core.vixen import bot


# TODO make a more... user friendly system, ill be adding a menu soon,
#  but we'll save that for later.
#	~ OrrinFox
user = open('storage/user.txt', 'r').read().rstrip()
pk   = open('storage/auth.txt', 'r').read().rstrip()
autojoin = open('storage/autojoin.txt', 'r').read().rstrip().split(':')
debug = open('storage/debug.txt', 'r').read().rstrip() if 'debug.txt' in os.listdir('storage') else 'False'

if debug in ['true', 'True']:
    _debug = True
else:
    _debug = False

UI   = Interface()
bot  = bot(UI, user, pk, debug=_debug, autojoin=autojoin)

UI.start(bot)
