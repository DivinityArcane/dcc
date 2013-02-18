import urwid

class interface:
	def __init__(self):
		self.window = urwid.Padding(self.config_menu(), left=3, right=3)
		self.shade = urwid.Overlay(self.window, urwid.SolidFill('\N{MEDIUM SHADE}'), align='center', width=('relative', 50), valign='middle', height=('relative', 50), min_width=50, min_height=10)

	def config_menu(self):
		content = [urwid.Text('Config'), urwid.Divider()]

		for opt in ['Username', 'Password', 'Channels', 'Etc']:
			button = urwid.Button(opt)
			urwid.connect_signal(button, 'click', self.on_config_click, opt)
			content.append(urwid.AttrMap(button, None))

		return urwid.ListBox(urwid.SimpleFocusListWalker(content))

	def on_config_click(self, button, option):
		resp = urwid.Text(['You clicked ', option, '!\n'])
		exit = urwid.Button('Exit')
		urwid.connect_signal(exit, 'click', self.close)
		self.window.original_widget = urwid.Filler(urwid.Pile([resp, urwid.AttrMap(exit, None)]))

	def start(self):
		urwid.MainLoop(self.shade, palette=[('reversed', 'standout', '')]).run()

	def check_input(self):
		pass
		
	def close(self, button):
		raise urwid.ExitMainLoop()
