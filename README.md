dcc
===


DCC - dAmn Curses Client

HOWTO: setup.

Make a storage folder and add/setup the configuration files:

$ mkdir storage


$ echo username > storage/user.txt

$ echo auth_token > storage/auth.txt

$ echo autojoin > storage/autojoin.txt

     -- Note: autojoin is a list of rooms seperated by ':'
          
          For instance: #Botdom:#Deviousdevelopment:#Room1:#etc


-OPTIONAL- setup a debug file.

$ echo True >  storage/debug.txt


Finally, start the client. 

$ python main.py
