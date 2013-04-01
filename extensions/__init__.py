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
        self.deform_ns = client.deform_ns
        self.format_ns = client.format_ns
        self.username  = client.username
        
        self.trigger    = '/'
        self.extensions = {}
        self.commands   = {}
        self.help       = {}
        self.events     = { 'conmsg': {},
                            'msg': {},
                          }

    def loopevents(self, event, args):
        if self.client.debug:
            self.client.log('DEBUG', 'Received event: {0}'.format(event))
        if event not in self.events:
            # We can add an event here, or we can simply let it go, in this case...
            return # lettin' it go :P
        for each in self.events[event]:
            try:
                if self.client.debug:
                    self.client.log('DEBUG', "Processing event {0}".format(self.events[event][each]))
                self.events[event][each](self, args)
            except:
                self.onerror(traceback.format_exc())
                # Above is used to handle errors in the extensions' system.
        

    def command(self, data):
        # Was going to make this both a bot and client but... no that would be too much wtfery
        self.channel = self.client.channel
        message = data['message']
        ns      = data['ns']
        if message.startswith(self.trigger):
            message = message[len(self.trigger):]
            
            args    = message.split(' ')
            command = args[0]
            if self.client.debug:
                self.client.log(self.deform_ns(ns), '\nCOMMAND:{0}\nARGS:{1}\nNS:{2}'.format(command, str(args), ns))
            
            if command in self.commands:
                try:
                    #x = thread(None, self.commands[command], args=(ns, args, self)).start()
                    x = self.commands[command](ns, args, self)
                    if x == False:
                        if command in self.help.keys():
                            self.client.log(self.deform_ns(ns), self.help[command].format(trig=self.trigger), False)
                        else:
                            self.client.log(self.deform_ns(ns), 'No help topic for {0}'.format(command), False)
                except:
                    self.onerror(traceback.format_exc())
            else:
                self.client.log(self.deform_ns(ns), 'Command {0} doesn\'t exist'.format(command), False)
        else:
            if len(message) < 1: return self.onerror('Nothing to send to {0}...'.format(self.client.deform_ns(ns)))
            
            self.client.say(ns, message)

    def onerror(self, error):
        pass
        # Again, we can do anything we want here. maybe display the error, save to debug file?
        # Etc... ~ OrrinFox
        
    def load_extensions(self):
        self.client.log('SYSTEM', 'Loading Extensions...')
        try:
            for each in sys.modules:
                if each.startswith('extensions.'):
                    try:
                        imp.reload(eval(each))
                    except:
                        pass
        except:
            pass
        mods = {}
        failed = []
        for f in os.listdir('extensions'):
            if f in ['__init__.py', '__init__.pyc']: continue
            modname, ext = os.path.splitext(f)
            if not ext in '.pyc' or not ext: continue
            if not modname in mods.keys():
                try:
                    mod = __import__('extensions', fromlist=[modname])
                    if hasattr(mod, modname):
                        mods[modname.capitalize()] = getattr(mod, modname)
                except:
                    failed.append([f, traceback.format_exc()])
        for each in mods:
            try:
                x = mods[each].extension(self)
                self.extensions[x.name.capitalize()] = x
            except:
                failed.append([each, traceback.format_exc()])
        return failed
        
    def activate_extensions(self):
        failed = self.load_extensions()
        activated = []
        for ext in self.extensions:
            ext = ext.capitalize()
            try:
                name = self.extensions[ext].name
                activated.append(name)
            except:
                failed.append([ext, traceback.format_exc()])
        for each in failed:
            self.client.log('SYSTEM', 'Failed to load extension {0}!\n{1}'.format(each[0], each[1]))
        #for each in activated:
        #    self.bot.logger('System', "Loaded Extension [{0}]".format(each))
        self.client.log('SYSTEM', 'Loaded Extensions.')
        return failed

    def reload_extensions(self):
        for each in sys.modules:
            if each.startswith('extensions.'):
                try:
                    imp.reload(eval(each))
                except:
                    pass
        self.extensions = {}
        for each in self.events:
            self.events[each] = {}
        self.commands = {}
        failed = self.activate_extensions()
        return failed
        
    def add_event(self, type, callback):
        
        if type not in self.events: self.events[type] = {}
        x = list(self.events[type].keys())
        x.sort()
        if len(x) == 0: id = 1
        else:           id = x[-1] + 1
        self.events[type][id] = callback
        return id
        
    def add_command(self, name, ext, help=''):
        name = name.lower()
        if name in self.commands:
            self.client.log('SYSTEM', "Command {0} defined, so object {1} is null".format(name, ext))
        else:
            self.commands[name] = ext
            if len(help) > 0: self.help[name] = help
        return True

class base:
    def __init__(self, system):
        self.name   = 'No Name'
        self.author = 'No Author'
        self.version= 1.0
        self.descrip= 'No description'
        self.doc    = {}
        self.__inst__(system)
        self.name = self.name.replace(' ', '')
