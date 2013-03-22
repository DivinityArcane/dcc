from extensions import base
import traceback

class extension(base):
    def __inst__(self, system):
        self.name = 'coreExtension'
        self.version = 1.0
        self.author = 'OrrinFox'
        self.descrip = 'core commands for the client.'
        
        self.man  = { 'chat':   '**********\nChat - Change active room to chat in.\n'+
                                '   Usage:\n'+
                                '       {trig}chat [ #channel ]\n\n'+
                                '   [ #channel ] = channel to change activity in.\n**********',
                      'clear':  '**********\nClear - Clear the screen.\n'+
                                '   Usage:\n'+
                                '       {trig}clear\n\n**********',
                      'join':   '**********\nJoin - Join another channel.\n'+
                                '   Usage:\n'+
                                '       {trig}join [ #channel ]\n\n'+
                                '   [ #channel ] = channel to join\n**********',
                      'part':   '**********\nPart - part active or seperate channel.\n'+
                                '   Usage:\n'+
                                '       {trig}part\n'+
                                '       {trig}part [ #channel ]\n\n'+
                                '   [ #channel ] = channel to part\n**********',
                      'exec':   '**********\nExec - execute python code.\n'+
                                '   Usage:\n'+
                                '       {trig}exec [ code ]\n\n'+
                                '   [ code ] = code to execute\n**********',
                                }

        
        
        # This is an example comman, used for testing, not needed anymore.
        #system.add_command('helloworld', self.cmd_test, 'Hello world command')
        
        system.add_command('chat', self.cmd_chat, self.man['chat'])
        system.add_command('join', self.cmd_join, self.man['join'])
        system.add_command('part', self.cmd_part, self.man['part'])
        system.add_command('clear', self.cmd_clear, self.man['clear'])
        system.add_command('exec', self.cmd_exec, self.man['exec'])
        
    # Example...
    def cmd_test(self, ns, args, system):
        system.client.log('TEST', 'Hello world!')

    def cmd_chat(self, ns, args, system):
        chatlist = [system.client.deform_ns(x).lower() for x in system.channel.keys()]
        if len(args) > 1:
            channel = system.client.deform_ns(args[1].lower())
            if channel in chatlist:
            # get index of lowered' list
                indexof = chatlist.index(channel)
                realns  = list(system.channel.keys())[indexof]
                system.client.active_ns = realns
                system.client.active_users = len(system.channel[realns]['members'].keys())
            else:
                system.client.log('ERROR', 'Not joined in {0}'.format(system.client.deform_ns(channel)))
        else:
            return False
            
    def cmd_join(self, ns, args, system):
        # I had to modify the system for joining rooms
        # just so this looks normal... herp
        if len(args) > 1:
            channel = system.client.format_ns(args[1])
            system.client.join(channel)
        else:
            return False
            
    def cmd_part(self, ns, args, system):
        if len(args) > 1:
            channel = system.client.format_ns(args[1])
            system.client.part(channel)
        else:
            if system.client.active_ns == 'System':
                return system.client.log('ERROR', 'Cannot part system namespace.')
            else:
                system.client.part(system.client.format_ns(system.client.active_ns))
                
    def cmd_clear(self, ns, args, system):
        # Not sure if theres a better way to do this but... :P
        system.client.log('SYSTEM', ('\n'*100)+'Screen cleared.')
        
    def cmd_exec(self, ns, args, system):
        if len(args) > 1:
            cmd = ' '.join(args[1:])
            try:
                exec(cmd)
            except:
                system.client.log('ERROR', '\n\n{0}'.format(traceback.format_exc()))
        else: return False
                
                
        
        
