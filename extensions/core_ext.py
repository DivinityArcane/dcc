from extensions import base

class extension(base):
    def __inst__(self, system):
        self.name = 'coreExtension'
        self.version = 1.0
        self.author = 'OrrinFox'
        self.descrip = 'core commands for the client.'
        system.add_command('helloworld', self.cmd_test, 'Hello world command')
        system.add_command('chat', self.cmd_chat, 'change active channel')
        
        
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
            else:
                system.client.log('ERROR', 'Not joined in {0}'.format(system.client.deform_ns(channel)))
        else:
            return False
            
                
        
        
