import sys
import select
import curses
from threading import Thread, Lock

# dcc
# Client Interface
#
# - DivinityArcane (Justin Eittreim)

class Interface:

    def __init__(self):
        self.name     = 'dcc'
        self.version  = '0.06 Beta'
        self.title    = 'dAmn Curses Client - dcc v ' + self.version
        self.actbar   = '-[ [un] in [ns] - [c] user[s] joined ]'
        self.joinedbar= '-[Channels: {0}'
        self.lines    = {}
        self.buffer   = ''
        self.running  = True
        self.l_offset = 0
        
        # 1 = Chat, 2 = Channels, 3 = Users, 4 = Title, 5 = Topic
        self.dsp_mode = 1


    def start(self, bot):
        self.core     = bot
        self.stdscr   = curses.wrapper(self.mainloop)

    def mainloop(self, screen):
        self.scr = screen
        curses.noecho()
        curses.cbreak()
        self.rows, self.cols = screen.getmaxyx()
        # Make the UI display
        self.add_line('System', '')
        self.cthread = Thread(None, self.core.mainloop, args=[])
        self.cthread.start()
        while self.running:
            (i, o, e) = select.select([sys.stdin], [], [])
            if sys.stdin in i:
                key = screen.getkey()
                if key == curses.KEY_BACKSPACE or key == 'KEY_BACKSPACE':
                    self.buffer = self.buffer[:-1]
                elif key == '\n' or key == '\r':
                    self.core.onevent('conmsg', [self.buffer])
                    self.buffer = ''
                elif key == 'KEY_PPAGE':
                    self.l_offset += 1
                elif key == 'KEY_NPAGE':
                    self.l_offset = self.l_offset - 1 if self.l_offset > 0 else 0
                elif key == 'KEY_UP':
                    pass # scroll through msg history
                elif key == 'KEY_DOWN':
                    pass # scroll through msg history
                elif key == 'KEY_END':
                    self.dsp_mode = 2 if self.dsp_mode == 1 else 1
                elif key == 'KEY_HOME':
                    self.dsp_mode = 3 if self.dsp_mode == 1 else 1
                elif key == chr(9):
                    pass # tab username
                elif key == chr(033):
                    break #quit
                else:
                    self.buffer += key
                self.refresh_screen(screen)
        self.core.quit("quit")
        sys.exit()

    def refresh_screen(self, screen):
        # Output the action bar (shows name, channel, ..)
        actbar = self.actbar
        if self.core.active_ns != 'System':
            ns = self.core.deform_ns(self.core.active_ns)
        else:
            ns = 'System'
        # [un] = username
        # [ns] = channel
        # [c]  = user count
        # [d]  = s if user count != 1, else empty
        actbar = actbar.replace('[un]', self.core.username)
        actbar = actbar.replace('[ns]', ns)
        actbar = actbar.replace('[c]',  str(self.core.active_users))
        actbar = actbar.replace('[s]',  's' if self.core.active_users != 1 else '')
        # Clear the screen
        screen.clear()
        screen.border(0)
        screen.addstr(0, 1, self.title)
        screen.addstr(self.rows - 4, 1, actbar)
        # Output lines
        if self.dsp_mode == 1:
            i = 0
            l = len(self.lines[ns]) - 1
            l -= self.l_offset
            while i < self.rows - 6 and l >= 0:
                screen.addstr(self.rows - (6 + i), 1, self.lines[ns][l])
                i += 1
                l -= 1
        elif self.dsp_mode == 2:
            chanlist = [self.core.deform_ns(each) for each in self.core.channel.keys()]
            chanlist.append('System')
            chanlist.sort()
            i = 4
            l = len(chanlist) - 1
            screen.addstr(2, 1, '%s channel%s joined - to switch to a tab, type /chat channel' % (l + 1, 's' if l + 1 != 1 else ''))
            while l >= 0 and l < self.rows - 6:
                screen.addstr(i, 1, chanlist[l])
                l -= 1
                i += 1
        # Output input
        i = 0
        iplines = self.wrap_line(self.buffer, self.cols - 2, 0)
        for each in iplines:
            screen.addstr(self.rows - (3 - i), 1, each)
            i += 1
        # Refresh the screen
        screen.refresh()
        screen.move(self.rows - 3, 1)


    def wrap_line(self, line, max_width, indent=4):
        if len(line) <= max_width:
            return [line]
        lines   = []
        tlwidth = len(line)
        tabs    = "".join([' ' for x in range(0, indent)])
        while len(line) > max_width:
            lines.append(line[0:max_width])
            line    = tabs + line[max_width:]
            tlwidth = len(line) + indent
        lines.append(line)
        return lines

    def refresh(self):
        self.refresh_screen(self.scr)

    def add_line(self, ns, line):
        line = line.rstrip()
        if ns != 'System' and not ns.startswith('#'):
            ns = self.core.deform_ns(ns)
        if ns not in self.lines:
            self.lines[ns] = []
        lines = line.split('\n') if '\n' in line else [line]
        for msg in lines:
            for wrapped in self.wrap_line(msg, self.cols - 2):
                self.lines[ns].append(wrapped)
        self.refresh_screen(self.scr)


UI = Interface()
