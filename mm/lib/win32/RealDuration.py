__version__ = "$Id$"

import rma

import MMurl, urllib

import win32ui, win32api

class RMDuration:
	def __init__(self, url):
		self.dur = 0
		url = MMurl.canonURL(url)
		url = urllib.unquote(url)
		self._engine = rma.CreateEngine()
		self._player = self._engine.CreatePlayer(-1,((-1,-1), (-1,-1)), 1)
		self._player.SetStatusListener(self)
		self._player.OpenURL(url)

	def calcDur(self):
		self._player.Begin()
		while not self.dur:
			win32ui.PumpWaitingMessages(0,0)
			win32api.Sleep(50)
		self._player.Stop()

	def OnPosLength(self, pos, len):
		self.dur = len/1000.0

	def getDur(self):
		return self.dur 
	
def get(url):
	rmadur = RMDuration(url)
	rmadur.calcDur()
	return rmadur.getDur()

