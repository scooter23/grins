__version__ = "$Id$"

import windowinterface, WMEVENTS
from usercmd import *

""" @win32doc|TopLevelDialog
There is one to one corespondance between a TopLevelDialog
instance and a document, and a TopLevelDialog
instance with an MDIFrameWnd. The document level commands
are enabled. This class has acces to the document and
can display its various views and its source
"""

class TopLevelDialog:
	adornments = {}

	def __init__(self):
		pass

	def show(self):
		if self.window is not None:
			return
		self.window = windowinterface.newdocument(self, 
			adornments = self.adornments,commandlist = self.commandlist)

	def hide(self):
		if self.window is None:
			return
		self.window.close()
		self.window = None

	def setbuttonstate(self, command, showing):
		self.window.set_toggle(command, showing)

	def showsource(self, source = None, optional=0):
		if source is None:
			if self.source is not None:
				self.source.close()
				self.source = None
		else:
			if self.source is not None:
				self.source.settext(source)
			else:
				self.source = self.window.textwindow(source)

	def mayclose(self):
		prompt = 'You haven\'t saved your changes yet;\n' + \
			 'do you want to save them before closing?'
		return windowinterface.GetYesNoCancel(prompt,self.window)

	# doesn't seem to work
	# kk: you must pass a context string as a second arg
	def setcommands(self, commandlist):
		self.window.set_commandlist(commandlist,'document')

	def do_edit(self, tmp):
		import os

		# use only notepad for now
		editor='Notepad'
		stat1 = os.stat(tmp)
		import win32api,win32con
		try:
			win32api.WinExec('%s %s' % (editor, tmp),win32con.SW_SHOW)
		except:	
			# no editor found
			self.edit_finished_callback()

		stat2 = os.stat(tmp)
		from stat import ST_INO, ST_DEV, ST_MTIME, ST_SIZE
		if stat1[ST_INO] == stat2[ST_INO] and \
		   stat1[ST_DEV] == stat2[ST_DEV] and \
		   stat1[ST_MTIME] == stat2[ST_MTIME] and \
		   stat1[ST_SIZE] == stat2[ST_SIZE]:
			# nothing changed
			self.edit_finished_callback()
			return
		self.edit_finished_callback(tmp)
