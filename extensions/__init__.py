import extensions
import os, sys, traceback, imp, time
import core
from threading import Thread as thread

# Primary extensions' system
#   by OrrinFox
#
#

class main:
    def __init__(self, client):
        self.client = client
        
        self.trigger    = '/'
        self.extensions = {}
        self.commands   = {}
        self.help       = {}
        self.events     = {'conmsg': {},
                          }

    def loopevents(self, event, args):
        if event not in self.events:
            # We can add an event here, or we can simply let it go, in this case...
            return # lettin' it go :P
        for each in self.events[event]:
            try:
                tread(None, target=self.event[event][each], args=(self, args)).start()
            except:
                self.onerror(traceback.format_exc())
                # Above is used to handle errors in the extensions' system.
        

    def command(self, data):
        # Was going to make this both a bot and client but... no that would be too much wtfery
        message = data['message']
        ns      = data['ns']
        if message.startswith(self.trigger):
            message = message[len(self.trigger):]
            
            args    = message.split(' ')
            command = args[0]
            if self.client.debug:
                self.client.log('DEBUG', '\nCOMMAND:{0}\nARGS:{1}\nNS:{2}'.format(command, str(args), ns))
            
            if command in self.commands:
                try:
                    if ''.join(args).endswith('--?') and message.strip() == self.trigger+command+' --?':
                        if command in self.help.keys():
                            self.client.log('', self.help[command].format(trig=self.trigger), shown=False)
                        else:
                            self.client.log('HELP', 'No help topic for {0}'.format(command))
                    else:
                        x = thread(None, self.commands[command], args=(ns, args, self)).start()
                        if x == False:
                            if command in self.help.keys():
                                self.client.log('', self.help[command].format(trig=self.trigger), shown=False)
                            else:
                                self.client.log('HELP', 'No help topic for {0}'.format(command))
                except:
                    self.onerror(traceback.format_exc())
            else:
                self.client.log('', 'Command {0} doesn\'t exist'.format(command), shown=False)
        else:
            self.client.say(ns, message)

    def onerror(self, error):
        pass
        # Again, we can do anything we want here. maybe display the error, save to debug file?
        # Etc... ~ OrrinFox

