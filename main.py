import sys
import io

#from threading  import Thread, Lock
from core.ui    import Interface
from core.vixen import bot


# TODO make a more... user friendly system, ill be adding a menu soon,
#  but we'll save that for later.
#	~ OrrinFox
user = open('user.txt', 'r').read().rstrip()
pk   = open('auth.txt', 'r').read().rstrip()

UI   = Interface()
bot  = bot(UI, user, pk, debug=True)

UI.start(bot)
