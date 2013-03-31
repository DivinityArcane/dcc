#!/usr/bin/python3
import socket, time, os, sys, traceback, re, select
import extensions

class bot:
    def __init__(self, ui, username, authtoken, debugfile='debug.log', debug=False, agent='dAmn.vixen', server='chat.deviantart.com', port=3900, encoding='latin-1', clientver='0.3', client='dAmnClient', autojoin=['#Botdom']):
        self.m_name        = 'vixen'
        self.m_version     = 5.0
        self.m_author      = 'OrrinFox'
        
        self.active_ns     = 'System'
        self.active_users  = 0
        self.buffer_ns     = ''
        # Buffer_ns is what we claim on join
        # then when we grab the members for the buffer_ns
        # set it to active_ns, ( reason: if we join before members gotten it shows
        # the members to the previous ns before the one we joined.. i know its hacky
        # But i dont really see a better way )
        
        self.username      = username
        self.auth          = authtoken
        self.autojoin      = autojoin
        self.UI            = ui
        self.ext           = extensions.main(self)
        
        self.server        = server
        self.port          = port
        self.encoding      = encoding
        self.clientver     = clientver
        self.client        = client
        self.agent         = agent
        self.buff          = ''
        self.pkts_recv     = 0
        self.pkts_sent     = 0
        self.pkts          = []
        self.connected     = False
        self.sock          = None
        self.authenticated = False
        
        self.channel       = {}
        
        self.started       = time.time()
        self.pyver         = sys.version_info[0]    
        
        self.debug         = debug
        if self.debug:
            self.debugfile = open(debugfile, 'a+')
        
        
        self.conmsg = { 'error': 'ERROR:\n\n{0}\n\n',
                        'start1': 'Starting {0} [ver {1}] by {2}',
                        'start2': 'Debug mode: {0}',
                        'start3': 'Login info: {0} [ AU: {1} ]',
                        'connecting': 'Connecting to {0} @ port {1}...',
                        'connected': 'Connected!',
                        'connecterror': 'Unable to connect to server:\n\n{0}\n',
                        'mainloopstrt': 'Initiating mainloop...',
                        'debugsrvsnt': 'Sending packet:\n\n{0}\n\n',
                        'socksnterr': 'Failed to send packet to server!\n\n{0}\n',
                        'sendagent': 'Sending agent {2} on base of {0}/{1}',
                        'gotdataserv': 'Got data from server of length [{0}]',
                        'confirmedconnect': 'Got connection confirmation from server.',
                        'sendlogin': 'Sending login packet...',
                        'loginfail': 'Failed to login as {0} [{1}]',
                        'loggedin': 'Logged in as {0} [{1}]',
                        'shutdown': 'Shutting down... [{0}]',
                        'onjoin': 'Joined {0} [{1}]',
                        'joinfailed': 'Could not join {0} [{1}]',
                        'parted': 'Parted {0} [{1}]',
                        'disconnect': 'Disconnected! [{0}]',
                        'kicked': 'Kicked by {0} {1}',
                        'pong': 'Received ping... sent Pong!',
                        'msgrecv': '[{0}] {1}',
                        'actionrecv': '*{0} {1}',
                        'usrjoin': '{0} has joined.',
                        'recvpart': '{0} has left.',
                        'recvpart1': '{0} has left. [{1}]',
                        'usrkicked': '{0} has been kicked by {1} {2}',
                        'adminrename': 'Privclass {0} has been renamed to {1} by {2}',
                        'grabtopic': 'Got topic for {0}',
                        'grabtitle': 'Got title for {0}',
                        'grabpriv': 'Got privclasses for {0}',
                        'grabmember': 'Got members for {0}',
                       }
        
        self.subs = [
            (re.compile("&avatar\t([a-zA-Z0-9-]+)\t([0-9]+)\t"), ":icon\\1:"),
            (re.compile("&dev\t(.)\t([a-zA-Z0-9-]+)\t"), ":dev\\2:"),
            (re.compile("&emote\t([^\t]+)\t([0-9]+)\t([0-9]+)\t(.*?)\t([a-z0-9./=-]+)\t"), "\\1"),
            (re.compile("&a\t([^\t]+)\t([^\t]*)\t"), "<a href=\"\\1\" title=\"\\2\">"),
            (re.compile("&link\t([^\t]+)\t&\t"), "\\1"),
            (re.compile("&link\t([^\t]+)\t([^\t]+)\t&\t"), "\\1 (\\2)"),
            (re.compile("&acro\t([^\t]+)\t"), "<acronym title=\"\\1\">"),
            (re.compile("&abbr\t([^\t]+)\t"), "<abbr title=\"\\1\">"),
            (re.compile("&thumb\t([0-9]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t"), ":thumb\\1:"),
            (re.compile("&img\t([^\t]+)\t([^\t]*)\t([^\t]*)\t"), "<img src=\"\\1\" alt=\"\\2\" title=\"\\3\" />"),
            (re.compile("&iframe\t([^\t]+)\t([0-9%]*)\t([0-9%]*)\t&\/iframe\t"), "<iframe src=\"\\1\" width=\"\\2\" height=\"\\3\" />"),
            (re.compile("<([^>]+) (width|height|title|alt)=\"\"([^>]*?)>"), "<\\1\\3>"),
            (re.compile(' <abbr title=\"colors\:([0-9A-F]{6})\:([0-9A-F]{6})\"\><\/abbr\>'), ''),
            (re.compile('(&gt;)'), '>'),
            (re.compile('(&lt;)'), '<'),
        ]
        
        self.replace = [
            ("&b\t", "<b>"),
            ("&/b\t", "</b>"),
            ("&i\t", "<i>"),
            ("&/i\t", "</i>"),
            ("&u\t", "<u>"),
            ("&/u\t", "</u>"),
            ("&s\t", "<s>"),
            ("&/s\t", "</s>"),
            ("&sup\t", "<sup>"),
            ("&/sup\t", "</sup>"),
            ("&sub\t", "<sub>"),
            ("&/sub\t", "</sub>"),
            ("&code\t", "<code>"),
            ("&/code\t", "</code>"),
            ("&p\t", "<p>"),
            ("&/p\t", "</p>"),
            ("&ul\t", "<ul>"),
            ("&/ul\t", "</ul>"),
            ("&ol\t", "<ol>"),
            ("&/ol\t", "</ol>"),
            ("&li\t", "<li>"),
            ("&/li\t", "</li>"),
            ("&bcode\t", "<bcode>"),
            ("&/bcode\t", "</bcode>"),
            ("&br\t", "\n"),
            ("&/a\t", "</a>"),
            ("&/acro\t", "</acronym>"),
            ("&/abbr\t", "</abbr>"),
        ]
        
        
    def log(self, ns, message, shown=True):
        ts = time.strftime('[%I:%M:%S%p]')
        try:   
            ns = '['+ns+']'
            if shown:
                # Added boolean "shown" for printing regular text in the console.
                msg = ts+ns+message
            else:
                msg=message
        
            self.UI.add_line(msg)
            
        except:
            
            msg = ts+'[ERROR]'+self.conmsg['error'].format(traceback.format_exc())
            self.UI.add_line(self.conmsg['error'].format(msg))
        
        if self.debug:
            self.debugfile.write(msg+'\n')
    
    def quit(self, reason):
        if self.connected:
            if self.authenticated:
            # Bot has been authenticated, its running.
                self.disconnect()
            else:
                self.connected = False
        self.log('SYSTEM', self.conmsg['shutdown'].format(reason))
        
      
    def connect(self):
        self.log('SERVER', self.conmsg['connecting'].format(self.server, str(self.port)))
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setblocking(0)
            self.sock.settimeout(180)
            self.sock.connect((self.server, self.port))
            self.connected = True
            self.log('SERVER', self.conmsg['connected'])
        except:
            self.log('ERROR', self.conmsg['connecterror'].format(traceback.format_exc()))
    
    def disconnect(self):
        self.connected = False
        self.send('disconnect')
    
    #
    # Server stuff.
    #
    
    def join(self, ns):
        self.buffer_ns = ns
        self.send('join {0}'.format(ns))
    
    def say(self, ns, message):
        self.send('send {0}\n\nmsg main\n\n{1}'.format(self.format_ns(ns), message))
    
    def part(self, ns):
        self.send('part {0}'.format(ns))
    
    #
    # End of server stuff.
    #
    
    
    def send(self, data):
        try:
            if self.debug:
                # We dont need this for now...
                #self.log('DEBUG', self.conmsg['debugsrvsnt'].format(data.replace('\n', '\\n')+'\\n\\0'))
                pass
            self.sock.send(data+'\n\0'.encode( self.encoding))
        except:
            self.log('ERROR', self.conmsg['socksnterr'].format(traceback.format_exc()))
    
    def listen(self):
	try:
	    ok   = select.select([self.sock], [], [], 1)
	    if ok[0]:
	        data = self.sock.recv(1).decode(self.encoding, 'ignore')
            else:
	        data = None
	except:
            data = None
        return data
    
            
    def mainloop(self):
        ns = 'SYSTEM'
        self.log(ns, self.conmsg['start1'].format(self.m_name, self.m_version, self.m_author))
        self.log(ns, self.conmsg['start2'].format(str(self.debug)))
        self.log(ns, self.conmsg['start3'].format(self.username, self.auth))
        self.ext.activate_extensions()
        self.connect()
        if self.connected:
        ### connected! ###
            self.log(ns, self.conmsg['mainloopstrt'])
            self.sendagent()
            while self.connected and self.UI.running:
                try:
                    data = self.listen()
                    if data == None:
                        continue
                    if data != '\0':
                        self.buff = self.buff + data
                    else:
                        self.chkdata(self.buff)
                        self.buff = ''
                except KeyboardInterrupt:
                    sys.stdout.write('\n')
                    time.sleep(.1)
                    self.quit('^C Keyboard interrupt.')
            
       
    def sendagent(self):
        self.log('SERVER', self.conmsg['sendagent'].format(self.client, self.clientver, self.agent))
        self.send('{0} {1}\nagent={2}'.format(self.client, self.clientver, self.agent))  
    
    def sendlogin(self):
        self.send('login {0}\npk={1}'.format(self.username, self.auth))
    
    def parsehtml(self, data):
        msg=''
        t=True
        for c in data:
            if c == '<':
                t=False
                continue
            elif c == '>':
                t=True
                continue
            if t:
                msg+=c
        return msg
        

    
    
    def chkdata(self, data):
        data = self.parse(data)
        _data = self.formatdata(data)
        
        
        data    = _data['raw']
        command = _data['command']
        param   = _data['param']
        args    = _data['args']
        body    = _data['body']
        if command.lower() == 'damnserver':
            if param == self.clientver:
                self.onevent('damnserverconfirm', [])
        elif command.lower() == 'login':
            if args['e'] == 'ok':
                self.onevent('loggedin', [args['e']])
            else:
                self.onevent('loginfail', [args['e']])       
        elif command.lower() == 'join':
            ns     = param
            joined = args['e']
            if joined == 'ok':
                self.onevent('joined', [ns, joined])
            else:
                self.onevent('joinfailed', [ns, joined])
        elif command.lower() == 'part':
            if not 'r' in args.keys():
                ns = param
                parted = args['e']
                if parted == 'ok':
                    self.onevent('parted', [ns, parted])
                else:
                    self.onevent('partfailed', [ns, parted])
            else:
                exited = args['r']
                self.onevent('disconnected', [exited])
        elif command.lower() == 'kicked':
            ns = param
            msg = '\n\n'.join(data.split('\n\n')[1:])
            by = args['by']
            self.onevent('kicked', [ns, msg, by])
        elif command == 'ping':
            self.onevent('ping', [])
        elif command == 'recv':
            ns = param
            typ = body.split('\n')[0]
            if typ == 'msg main':
                msg = '\n\n'.join(body.split('\n\n')[1:])
                user = body.split('\n\n')[0].split('\n')[1].split('from=')[1]
                self.onevent('msgrecv', [ns, user, msg])
           
            elif typ == 'action main':
                msg = '\n\n'.join(body.split('\n\n')[1:])
                user = body.split('\n\n')[0].split('\n')[1].split('from=')[1]
                self.onevent('actionrecv', [ns, user, msg])
            elif typ.startswith('join'):
                user = typ.split(' ')[1].split('\n')[0]
                x = ''.join(body.split('\n\n')[1:])
                lines = x.split('\n')
                data = {}
                for each in lines:
                    if '=' in each:
                        mk = each.find('=')
                        data[each[:mk]] = each[1+mk:]
                self.onevent('usrjoin', [ns, user, data])
            
            elif typ.startswith('part'):
                user = typ.split(' ')[1].split('\n')[0]                
                x = ','.join(body.split('\n')[1:])
                data = {}
                lines = x.split(',')
                for each in lines:
                    if '=' in each:
                        mk = each.find('=')
                        data[each[:mk]] = each[1+mk:]
                if 'r' in data.keys():
                    reason = data['r']
                else:
                    reason = False
                self.onevent('usrparted', [ns, user, reason, data])
            elif typ.startswith('kicked'):
                user = typ.split(' ')[1].split('\n')[0]
                x = ','.join(body.split('\n')[1:])
                data = {}
                lines = x.split(',')
                for each in lines:
                    if '=' in each:
                        mk = each.find('=')
                        data[each[:mk]] = each[1+mk:]
                reason = '\n\n'.join(body.split('\n\n')[1:])
                self.onevent('usrkicked', [ns, user, data, reason])
            elif typ.startswith('admin'):
                data = body.split('\n')
                if data[0].split(' ')[1] == 'rename':
                    data.remove(data[0])
                    temp = data
                    data = {}
                    for each in temp:
                        if each != '':
                            mk = each.find('=')
                            data[each[:mk]] = each[1+mk:]
                    self.onevent('adminrename', [ns, data])
        elif command == 'property':
            ns = param
            if args['p'] == 'topic':
                by = args['by']
                ts = args['ts']
                content = body
                self.onevent('proptopic', [by, ts, content, ns])
            elif args['p'] == 'title':
                by = args['by']
                ts = args['ts']
                content = body
                self.onevent('proptitle', [by, ts, content, ns])   
            elif args['p'] == 'privclasses':
                dat = body.strip('\n\n').split('\n')
                self.onevent('proppriv', [dat, ns])
            elif args['p'] == 'members':
                pk1 = body.split('\n\n')                
                self.onevent('propmembers', [pk1, ns])
            

    def format_ns(self, data):
        if data.startswith('chat:'):
            return data
        else: return 'chat:'+data.strip('#')
        
    def deform_ns(self, data):
        if data.startswith('chat:'):
            return '#'+data.split(':')[1]
        elif data.startswith('#'):
            return data
        else:
            return '#'+data
        
    
    def parse(self, data):
        try:
            for found, replace in self.replace:
                data = data.replace(found, replace)
            for exp, replace in self.subs:
                data = exp.sub(replace, data)
        except:
                return False
        return data

    def formatdata(self, data):
        dat     = {}
        command = None
        param   = None
        args    = {}
        body    = None
        raw     = data
        sep     = '='
        if not bool(data): return
        if data.find('\n\n') != -1:
            body = data[data.find('\n\n')+2:]
            data = data[:data.find('\n\n')]
        breaks = data.split('\n')
        if not bool(breaks): return
        if len(breaks) >= 1 and not sep in breaks[0]:
            head = breaks.pop(0).split(' ')
            command = head[0] or None
            param = None if len(head) < 2 else head[1]
        for line in breaks:
            if line.find(sep) == -1: continue
            args[line[:line.find(sep)]] = line[line.find(sep)+len(sep):]
        dat['raw']      = raw
        dat['command']  = command
        dat['param']    = param
        dat['args']     = args
        dat['body']     = body
        return dat    
       
            
    def onevent(self, typ, args):
        if typ == 'damnserverconfirm':
            
            self.log('SERVER', self.conmsg['confirmedconnect'])
            self.log('SERVER', self.conmsg['sendlogin'])
            self.sendlogin()
            
        elif typ == 'loggedin':
            e=args[0]
            self.log('SERVER', self.conmsg['loggedin'].format(self.username, e))
            for each in self.autojoin:
                if len(each) > 0:
                    self.join(self.format_ns(each))
        elif typ == 'loginfail':
            e=args[0]
            self.authenticated = False
            self.log('SERVER', self.conmsg['loginfail'].format(self.username, e))
            self.quit('Login False')
        elif typ == 'joined':
            self.joining = False
            ns = args[0]
            r  = args[1]
            self.buffer_ns = ns
            # see above for information on buffer_ns
            self.log('SERVER', self.conmsg['onjoin'].format(self.deform_ns(ns), r))
            self.channel[ns] = {'topic': {}, 'title': {}, 'privclasses': {}, 'members': {}}
            data = {'ns': ns, 'r': r}
            
        elif typ == 'joinfailed':
            ns = args[0]
            r  = args[1]
            self.log('SERVER', self.conmsg['joinfailed'].format(self.deform_ns(ns), r))
        elif typ == 'parted':
            ns = args[0]
            r = args[1]
            
            del self.channel[ns]
            if self.active_ns == ns:
                self.change_ns()
                
            data = {'ns': ns, 'r': r}
            self.log('SERVER', self.conmsg['parted'].format(self.deform_ns(ns), r))
            
        elif typ == 'partfailed':
            ns = args[0]
            r  = args[1]
            self.log('SERVER', self.conmsg['partfailed'].format(self.deform_ns(ns), reason))
        elif typ == 'disconnected':
            r = args[0]
            self.log('SERVER', self.conmsg['disconnect'].format(r))
        elif typ == 'kicked':
            ns = args[0]
            reason = args[1]
            by = args[2]
            del self.channel[ns]
            if self.active_ns == ns:
                self.change_ns()
            data = {'ns': ns, 'r': reason, 'by': by }
            self.log(ns=self.deform_ns(ns), message=self.conmsg['kicked'].format(by, '['+reason+']' if len(reason) > 0 else ''))
        elif typ == 'ping':
            self.send('pong')
            if self.debug:
                self.log('SERVER', self.conmsg['pong'])
        elif typ == 'msgrecv':
            ns = args[0]
            user = args[1]
            message = args[2]
            self.log(self.deform_ns(ns), self.conmsg['msgrecv'].format(user, self.parsehtml(message)))
        elif typ == 'actionrecv':
            ns = args[0]
            user = args[1]
            message = args[2]
            self.log(self.deform_ns(ns), self.conmsg['actionrecv'].format(user, self.parsehtml(message)))
        elif typ == 'usrjoin':
            ns = args[0]
            user = args[1]
            data = args[2]
            self.channel[ns]['members'][user] = data
            if ns == self.active_ns:
                # update information on active ns
                self.active_users = len(self.channel[self.active_ns]['members'].keys())
            self.log(self.deform_ns(ns), self.conmsg['usrjoin'].format(user))
        elif typ == 'usrparted':
            ns      = args[0]
            user    = args[1]
            reason  = args[2]
            data    = args[3]
            if user in self.channel[ns]['members'].keys():
                del self.channel[ns]['members'][user]
            if ns == self.active_ns:
                self.active_users = len(self.channel[self.active_ns]['members'].keys())
            if not reason:
                self.log(self.deform_ns(ns), self.conmsg['recvpart'].format(user))
            else:
                self.log(self.deform_ns(ns), self.conmsg['recvpart1'].format(user, reason))
        elif typ == 'usrkicked':
            ns      = args[0]
            user    = args[1]
            reason  = args[3]
            by      = args[2]['by']
            if user in self.channel[ns]['members'].keys():
                del self.channel[ns]['members'][user]
            if ns == self.active_ns:
                self.active_users = len(self.channel[self.active_ns]['members'].keys())
            self.log(self.deform_ns(ns), self.conmsg['usrkicked'].format(user, by, '['+reason+']' if len(reason) > 0 else ''))
            data = {'ns': ns, 'user': user, 'r': reason, 'by': by}
        elif typ == 'adminrename':
            ns      = args[0]      #namespace
            data    = args[1]      #data dictionary
            prop    = data['p']    #original property
            prev    = data['prev'] #previous privclass name
            by      = data['by']   #who renamed privclasses
            newname = data['name'] #new privclass name
            self.log(self.deform_ns(ns), self.conmsg['adminrename'].format(prev, newname, by))
        elif typ == 'proptopic':
            by      = args[0]
            ts      = args[1]
            content = args[2]
            room    = args[3]
            self.channel[room]['topic']['by'] = by
            self.channel[room]['topic']['ts'] = ts
            self.channel[room]['topic']['content'] = content
            if self.debug:
                self.log('SERVER', self.conmsg['grabtopic'].format(self.deform_ns(room)))
        elif typ == 'proptitle':
            by      = args[0]
            ts      = args[1]
            content = args[2]
            room    = args[3]
            self.channel[room]['title']['by'] = by
            self.channel[room]['title']['ts'] = ts
            self.channel[room]['title']['content'] = content
            if self.debug:
                self.log('SERVER', self.conmsg['grabtitle'].format(self.deform_ns(room)))
        elif typ == 'proppriv':
            _data = {}
            ns = args[1]
            for each in args[0]:
                level, name = each.split(':')
                self.channel[ns]['privclasses'][name] = level
                _data[name] = level
            if self.debug:    
                self.log('SERVER', self.conmsg['grabpriv'].format(self.deform_ns(ns)))
            _data['type'] = 'privclasses'
        elif typ == 'propmembers':
            ns = args[1]
            _data = {}
            for each in args[0]:    
                if not each == '':
                    x = each.split('\n')
                    name        = x[0].split(' ')[1]
                    pc          = x[1][x[1].find('=')+1:]
                    usericon    = x[2][x[2].find('=')+1:] 
                    symbol      = x[3][x[3].find('=')+1:]
                    realname    = x[4][x[4].find('=')+1:]
                    typename    = x[5][x[5].find('=')+1:]
                    gpc         = x[6][x[6].find('=')+1:]
                    self.channel[ns]['members'][name] = {   'pc': pc, 
                                                            'usericon': usericon,
                                                            'symbol': symbol,
                                                            'realname': realname,
                                                            'typename': typename,
                                                            'gpc': gpc}
                    _data[name] = {'pc': pc, 'usericon': usericon, 'symbol': symbol, 'realname': realname, 'gpc': gpc}
            _data['type'] = 'members'
            if ns == self.buffer_ns:
                #again, see above for information about this
                # theres a method to my madness. :P
                self.active_ns    = self.buffer_ns
                self.active_users = len(self.channel[ns]['members'].keys())
            # Well make it log this so it will post how many users are in the current room :P
            self.log('SERVER', self.conmsg['grabmember'].format(self.deform_ns(ns)))
            
        elif typ == 'conmsg':
            # This is where console input should be handled.
            message = args[0]
            ns      = self.active_ns
            if self.debug:
                self.log('DEBUG', 'USER_INPUT: '+message.strip())
            # Now to make a command system / extension loader.
            data = {'message': message, 'ns': ns}
            self.ext.command(data)
            
    def change_ns(self):
        if len(self.channel) < 1: 
            self.active_ns = 'System'
            self.active_users = 0
            return True
        self.active_ns = list(self.channel.keys())[0]
        self.active_users = len(self.channel[self.active_ns]['members'].keys())
