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
                      'me':     '**********\nMe - Perform a dAmn action.\n'+
                                '   Usage:\n'+
                                '       {trig}me message\n\n**********',
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
                      'exec':   '**********\nExec/Eval - execute or eval python code.\n'+
                                '   Usage:\n'+
                                '       {trig}[exec, eval] [ code ]\n\n'+
                                '   [ code ] = code to execute\n**********',
                      'reload': '**********\nReload - Reload extensions.\n'+
                                '   Usage:\n'+
                                '       {trig}reload\n**********',
                      'commands': '**********\nCommands - get the commands available.\n'+
                                '   Usage:\n'+
                                '       {trig}commands\n**********',
                      'channels': '**********\nChannels - get the list of currently joined\n'+
                                  ' channels.\n**********',
                       'members': '**********\nMembers - get currently joined members in the channel\n'+
                                  '**********',
                                }
        system.add_command('chat', self.cmd_chat, self.man['chat'])
        system.add_command('me', self.cmd_me, self.man['me'])
        system.add_command('join', self.cmd_join, self.man['join'])
        system.add_command('part', self.cmd_part, self.man['part'])
        system.add_command('clear', self.cmd_clear, self.man['clear'])
        system.add_command('exec', self.cmd_exec, self.man['exec'])
        system.add_command('eval', self.cmd_eval, self.man['exec'])
        system.add_command('reload', self.cmd_reload, self.man['reload'])
        system.add_command('commands', self.cmd_commands, self.man['commands'])
        system.add_command('channels', self.cmd_channels, self.man['channels'])
        system.add_command('members', self.cmd_members, self.man['members'])
        system.add_event('msg', self.on_msg)
    
    def cmd_members(self, ns, args, system):
        '''
        Member roster:
           
        '''
        data = {}
        for each in system.channel[ns]['members']:
            privclass = system.channel[ns]['members'][each]['pc']
            name      = each
            symbol    = system.channel[ns]['members'][each]['symbol']
            if not privclass in data.keys():
                data[privclass] = [ symbol + name ]
            else:
                data[privclass].append( symbol + name ) 
            
        out = ''
        for each in data.keys():
            out += '[{0}]\n'.format(each)
            for user in data[each]:
                out += '    {0}\n'.format(user)
        system.client.log(system.deform_ns(ns), out, False)
            
    
    def cmd_channels(self, ns, args, system):
        system.client.log(system.deform_ns(ns), "*** Current joined channels:\n{0}\n***".format(system.client.human_list([system.deform_ns(x) for x in system.channel.keys()])), False)
    
    def cmd_commands(self, ns, args, system):
        system.client.log(system.deform_ns(ns), "***\nActive commands loaded...\n"+
                                                "   {0}\n***".format(", ".join(list(system.commands.keys()))), False)
    def cmd_reload(self, ns, args, system):
        if system.client.active_ns.lower() != 'system':
            system.client.log(system.deform_ns(ns), "Reloading Extensions...", False)
        system.reload_extensions()
        if system.client.active_ns.lower() != 'system':
            system.client.log(system.deform_ns(ns), "Reloaded Extensions!", False)
        
    def cmd_chat(self, ns, args, system):
        chatlist = [system.deform_ns(x).lower() for x in system.channel.keys()]
        if len(args) > 1:
            if args[1].lower() == 'system':
                system.client.active_ns    = 'System'
                system.client.active_users = 0
                system.client.UI.refresh()
            else:                
                channel = system.deform_ns(args[1].lower())
                if channel in chatlist:
                # get index of lowered' list
                    indexof = chatlist.index(channel)
                    realns  = list(system.channel.keys())[indexof]
                    system.client.active_ns = realns
                    system.client.active_users = len(system.channel[realns]['members'].keys())
                    system.client.UI.refresh()
                else:
                    system.client.log(system.deform_ns(ns), 'Not joined in {0}'.format(system.client.deform_ns(channel)))

        else:
            return False

    def cmd_me(self, ns, args, system):
        if len(args) > 1:
            msg = ' '.join(args[1:])
            system.client.act(ns, msg)
            
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
                return system.client.log('System', 'Cannot part system namespace.')
            else:
                system.client.part(system.client.format_ns(system.client.active_ns))
                
    def cmd_clear(self, ns, args, system):
        # Not sure if theres a better way to do this but... :P
        system.client.log(system.deform_ns(ns), ('\n'*100)+'Screen cleared.')
        
    def cmd_exec(self, ns, args, system):
        if len(args) > 1:
            cmd = ' '.join(args[1:])
            try:
                exec(cmd)
            except:
                system.client.log(system.deform_ns(ns), '\n\n{0}'.format(traceback.format_exc()))
        else: return False
        
    def cmd_eval(self, ns, args, system):
        if len(args) > 1:
            cmd = ' '.join(args[1:])
            try:
                system.client.log(system.deform_ns(ns), str(eval(cmd)))
            except:
                system.client.log(system.deform_ns(ns), '\n\n{0}'.format(traceback.format_exc()))
        else: return False
                
    def on_msg(self, system, data):
        if system.username.lower() in data['message'].lower() and data['ns'].lower() != system.client.active_ns.lower():
            system.client.log(system.deform_ns(system.client.active_ns), "NOTIFY: You were tabbed in {0} by {1}!".format(system.deform_ns(data['ns']),
                data['user']), False)
        
        
        
