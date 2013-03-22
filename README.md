dcc
===
  * * * * * * * * * * * * * * * * * *
  *       _ _ _                     *
  *      |_|_|_|    _ _ _   _ _ _   *
  *     |_|   |_|  |_|_|_| |_|_|_|  *
  *    |_|    _|  |_|     |_|       *
  *   |_|_ _|_|  |_|_ _  |_|_ _     *
  *  |_|_|_|    |_|_|_| |_|_|_|     *
  *                                 *
  * * * * * * * * * * * * * * * * * * 

HOWTO: setup.

Make a storage folder and add/setup the configuration files:

$ mkdir storage

 -- Note: autojoin is a list of rooms seperated by ':'
          For instance: #Botdom:#Deviousdevelopment:#Room1:#etc

$ echo username > storage/user.txt
$ echo auth_token > storage/auth.txt
$ echo autojoin > storage/autojoin.txt

-OPTIONAL- setup a debug file.
$ echo True >  storage/debug.txt


Finally, start the client. 

$ python main.py
