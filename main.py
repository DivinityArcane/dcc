#!/usr/bin/python
import sys, io, os, cookielib, urllib, urllib2, json, time, traceback, re
from core.ui    import Interface
from core.vixen import bot

'''
This is where we handle everything before the client starts.
This includes the username, the password. all that stuff.

   - orrinfox
'''

class main:
    def __init__(self):
        self.username  = None
        self.authtoken = None
        self.debug     = False
        self.autojoin  = None
        self.loginurls = ['https://www.deviantart.com/users/login',
                          'http://chat.deviantart.com/chat/Botdom',
                         ]

    def init_client(self):
        UI    = Interface()
        vixen = bot(UI, self.username, self.authtoken, debug=self.debug, autojoin=self.autojoin)
        UI.start(vixen)

    def prompt(self, message):
        return raw_input(message).strip()
        
    def log(self, message):
        return sys.stdout.write(message + '\n')

    def start(self):
        self.clear()
        self.log(' *** DCC Client launcher version 1.0 starting ...')
        configurations = self.load_json_file('storage/config.json')
        if configurations == None:
            self.log("WARNING: Couldnt load a configuration file! Loading setup system.")
            self.get_login_details()
        else:
            self.log("Got configuration! Setting up ...")
            self.username  = configurations['username']
            self.authtoken = configurations['authtoken']
            self.autojoin  = configurations['autojoin']
            self.log("Everything is set up! Initialize!")
            self.init_client()
            
        
    def load_json_file(self, filename, default=None, strict=False):
        try:
            file = open(filename, 'r')
            data = json.loads(file.read())
            file.close()
            return data
        except:
            if strict:
                self.log('ERROR', '\nAn Error was encountered while loading {0}\n\n{1}'.format(filename, traceback.format_exc()))
            return default
    
    def save_json_file(self, filename, obj):
        try:
            file = open(filename, 'w')
            file.write(json.dumps(obj))
            file.close()
            return True
        except:
            self.log('ERROR', '\nAn Error was encountered while saving {0}\n\n{1}'.format(filename, traceback.format_exc()))
            
    def grab_cookie_2(self, client='dAmn.vixen authtoken grabber [python2]'):        
        url = self.loginurls[0]
        extras = {'remember_me': '1', 'username': self.username, 'password': self.password}
        self.jar = cookielib.CookieJar()
        opener   = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.jar))
        req      = urllib2.Request(
            url,
            urllib.urlencode(extras),
            {'User-Agent': client},
        )
        try:
            response = opener.open(req)
            return response
        except IOError as error:
            raise Exception("Something super weird happened! D: TRACEBACK: \nERROR.REASON: {0}\nERROR: STRERROR: {1}\n\n{2}".format(error.reason, error.strerror, traceback.format_exc()))

    def fetch_token_2(self, client='dAmn.vixen authtoken grabber [python2]'):
        url    = self.loginurls[1]
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.jar))
        req    = urllib2.Request(
            url,
            urllib.urlencode({}),
            {'User-Agent': client},
        )
        try:
            resp     = opener.open(url)
            response = resp.read().decode('latin-1')
            return response
        except IOError as error:
            raise Exception("Something super weird happened! D: TRACEBACK: \nERROR.REASON: {0}\nERROR.STRERROR: {1}\n\n{2}".format(error.reason, error.strerror, traceback.format_exc()))

    def scrape_token_page(self, page):
        match = re.search('"'+self.username+'", "([0-9a-f]{32})"', page, re.IGNORECASE)
        if match is None or match.group(1) is None:
            raise Exception("Could not match the authtoken in the token page! Exiting!")
        authtoken = match.group(1)
        return authtoken
    
    def clear(self):
        sys.stdout.write('[H[J')
        sys.stdout.flush()
        
    def get_login_details(self):
        self.log(" *** Welcome to DCC Token grabber, this will give a token that will Allow\n"+
                 "   You to join dAmn using this client! Just follow the prompt below ...\n\n")
        self.prompt("Press enter to begin.")
        self.setup = True
        while self.setup:
            self.clear()
            self.username = self.prompt("What is your username:\n ")
            self.password = self.prompt("What is your password:\n ")
            self.log(" *** Okay. lets try and grab an authtoken...")
            req = self.grab_cookie_2()
            if "wrong-password?" in req:
                self.log("Could not grab authentication with dA! BAD PASSWD\nResponse: {0}".format(req))
            elif "verify.deviantart.com" in req:
                self.log("Could not grab authentication with dA! VERIFICATION REQUIRED\nResponse: {0}".format(req))
            else:
                self.log("Fetched authentication cookies! Time to grab an authtoken...")
                token = self.scrape_token_page( self.fetch_token_2() )
                self.log("Fetched an authtoken! {0}".format(token))
                self.log(" *** OK, time to get the autojoin!")
                autojoin = self.prompt("What channels do you want to join? Seperate by spaces:\n ").split(' ')
                while len(autojoin) < 1:
                    self.log("Please enter the channels...")
                    autojoin = self.prompt("What channels do you want to join? Seperate by spaces:\n ").split(' ')
                self.log(" *** Alright! Lets save our settings. then we restart.")
                data = {'username': self.username, 'authtoken': token, 'autojoin': autojoin}
                if not os.path.exists('storage'):
                    os.mkdir('storage')
                    self.save_json_file('storage/config.json', data)
                else:
                    if not os.path.isdir('storage'):
                        os.remove('storage')
                        os.mkdir('storage')
                        self.save_json_file('storage/config.json', data)
                    else:
                        self.save_json_file('storage/config.json', data)
                self.log("File saved and authentication ready! Lets do this.")
                self.log(" *** Restarting the client, and joining channels, initialize!")
                time.sleep(1)
                self.setup = False
                self.restart()
        
    def restart(self):
        file = open('.restart', 'w')
        file.write("Restarting ...")
        file.close()
        return True


if __name__ == '__main__':
    main().start()
    while '.restart' in os.listdir('.'):
        os.remove('.restart')
        main().start()
    
    
