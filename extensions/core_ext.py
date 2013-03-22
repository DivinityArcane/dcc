from extensions import base

class extension(base):
    def __inst__(self, system):
        self.name = 'coreExtension'
        self.version = 1.0
        self.author = 'OrrinFox'
        self.descrip = 'core commands for the client.'
        
        # This is an example comman, used for testing, not needed anymore.
        #system.add_command('helloworld', self.cmd_test, 'Hello world command')
        
        system.add_command('chat', self.cmd_chat, 'change active channel')
        system.add_command('join', self.cmd_join, 'join a room.')
        system.add_command('part', self.cmd_part, 'part a room.')
        
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
                
        
        
