# Initial stab at Windows Media Player export

import windowinterface

class Exporter:
	def __init__(self, filename, player):
		self.filename = filename
		self.player = player
		self.aborted = 0
		self.topwindow = None
		windowinterface.settimevirtual(1)
		self.starttime = windowinterface.getcurtime()
		print 'starttime=', self.starttime
		self.player.exportplay(self)
		
	def _cleanup(self):
		self.player = None
		self.topwindow = None
		
	def changed(self, topchannel, window, event, timestamp):
		"""Callback from the player: the bits in the window have changed"""
##		if topwindow:
##			if self.topwindow and self.topwindow != topwindow:
##				windowinterface.showmessage("Cannot export multiple topwindows")
##				self.cancel_callback() # XXX Or schedule with timer? We're in a callback...
##			self.topwindow = topwindow
##		windowinterface.showmessage("Changed, timestamp=%d"%timestamp)
		print "CHANGED", timestamp-self.starttime, topchannel, window
		
	def audiofragment(self):
		"""XXXX This needs work"""
		pass
		
	def finished(self, aborted):
		if aborted:
			self.aborted = 1
		stoptime = windowinterface.getcurtime()
		windowinterface.settimevirtual(0)
		windowinterface.showmessage("Finished, aborted=%d"%self.aborted)
		
	def cancel_callback(self):
		self.aborted = 1
		self.player.stop()
		self._cleanup()
