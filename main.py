from ui import interface

class Client:
	def __init__(self):
		self.ui = interface()
		self.ui.start()
		self.running = True
		self.loop()

	def loop(self):
		#while self.running:
		#	self.ui.check_input()
		pass


cli = Client()
