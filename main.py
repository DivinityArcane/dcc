import sys
import io

#from threading  import Thread, Lock
from core.ui    import Interface
from core.vixen import bot

user = open('user.txt', 'r').read().rstrip()
pk   = open('auth.txt', 'r').read().rstrip()

UI   = Interface()
bot  = bot(UI, user, pk)

UI.start(bot)
