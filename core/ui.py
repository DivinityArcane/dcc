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
		self.version  = '0.01 Beta'
		self.title    = ' > dAmn Curses Client - dcc v' + self.version
		self.actbar   = ' > [un] in [ns] - ([c] user[s])'
		self.lines    = []
		self.buffer   = ''
		self.running  = True


	def start(self, bot):
		self.core     = bot
		self.stdscr   = curses.wrapper(self.mainloop)


	def mainloop(self, screen):
		self.scr = screen
		curses.noecho()
		curses.cbreak()
		self.rows, self.cols = screen.getmaxyx()

		# Make the UI display
		self.add_line('')

		self.cthread = Thread(None, self.core.mainloop, args=[])
		self.cthread.start()

		while self.running:
			(i, o, e) = select.select([sys.stdin], [], [])
			
			if sys.stdin in i:
				key = screen.getkey()
				if key == curses.KEY_BACKSPACE or key == 'KEY_BACKSPACE':
					self.buffer = self.buffer[:-1]
				elif key == '\n' or key == '\r':
					self.add_line(self.buffer)
					self.buffer = ''
				elif key == chr(033): 
					break
				else:
					self.buffer += key
				
				self.refresh_screen(screen)

		self.core.quit("quit")
		sys.exit()



	def refresh_screen(self, screen):
		
		# Output the action bar (shows name, channel, ..)

		actbar = self.actbar

		# [un] = username
		# [ns] = channel
		# [c]  = user count
		# [d]  = s if user count != 1, else empty

		actbar = actbar.replace('[un]', 'TestUser')
		actbar = actbar.replace('[ns]', '#Botdom')
		actbar = actbar.replace('[c]',  '0')
		actbar = actbar.replace('[s]',  's') 
	
		
		# Clear the screen

		screen.clear()
		screen.border(0)
		screen.addstr(0, 1, self.title)
		screen.addstr(self.rows - 4, 1, actbar)


		# Output lines

		i = 0
		l = len(self.lines) - 1

		while i < self.rows - 7 and l >= 0:
			screen.addstr(self.rows - (7 + i), 1, self.lines[l])
			i += 1
			l -= 1


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


	def add_line(self, line):
		line = line.rstrip()
		
		lines = line.split('\n') if '\n' in line else [line]

		for msg in lines:
			for wrapped in self.wrap_line(msg, self.cols - 2):
				self.lines.append(wrapped)

		self.refresh_screen(self.scr)


UI = Interface()
