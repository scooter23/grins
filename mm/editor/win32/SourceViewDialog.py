__version__ = "$Id$"

import windowinterface, usercmd
from usercmd import *

class SourceViewDialog:
	def __init__(self):
		self.__textwindow = None
		self.__setCommonCommandList()

		self._findReplaceDlg = None
		self._findText = ''
		self._replaceText = None
		self._findOptions = (0,0)
		self.__selChanged = 1
		self.__replacing = 0
		
	def __setCommonCommandList(self):
		self._commonCommandList = [SELECTNODE_FROM_SOURCE(callback = (self.onRetrieveNode, ())),
								   FIND(callback = (self.onFind, ())),
								   FINDNEXT(callback = (self.onFindNext, ())),
								   REPLACE(callback = (self.onReplace, ())),
								   ]
		
	def destroy(self):
		self.__textwindow = None
		
	def show(self):
		if not self.__textwindow:
			self.window = self.__textwindow = self.toplevel.window.textwindow("", readonly=0)
			self.__textwindow.set_mother(self)
		else:
			# Pop it up
			pass
		self.__updateCommandList()
		self.__textwindow.setListener(self)

	def pop(self):
		if self.__textwindow != None:
			self.__textwindow.pop()
			
	def __updateCommandList(self):
		commandList = []

		# undo
		if self.__textwindow.canUndo():
			commandList.append(UNDO(callback = (self.onUndo, ())))

		# copy/paste/cut			
		if self.__textwindow.isSelected():
			if self.__textwindow.isClipboardEmpty():
				commandList.append(COPY(callback = (self.onCopy, ())))
				commandList.append(CUT(callback = (self.onCut, ())))
			else:
				commandList.append(COPY(callback = (self.onCopy, ())))
				commandList.append(CUT(callback = (self.onCut, ())))
				commandList.append(PASTE(callback = (self.onPaste, ())))
		elif not self.__textwindow.isClipboardEmpty():
			commandList.append(PASTE(callback = (self.onPaste, ())))

		# other operations all the time actived
		commandList = commandList+self._commonCommandList
		
		self.setcommandlist(commandList)
		
	def is_showing(self):
		if self.__textwindow:
			return 1
		else:
			return 0

	def hide(self):
		if self.__textwindow:
			self.__textwindow.removeListener()
			self.__textwindow.close()
			self.__textwindow = None

		if self._findReplaceDlg:
			self._findReplaceDlg.hide()
			self._findReplaceDlg = None
			
	def setcommandlist(self, commandlist):
		if self.__textwindow:
			self.__textwindow.set_commandlist(commandlist)

	def get_text(self):
		if self.__textwindow:
			return self.__textwindow.gettext()
		else:
			print "ERROR (get_text): No text window."

	def set_text(self, text):
		if self.__textwindow:
			return self.__textwindow.settext(text)
		else:
			print "ERROR (set text): No text window"

	def is_changed(self):
		if self.__textwindow:
			return self.__textwindow.isChanged()

	def select_chars(self, s, e):
		if self.__textwindow:
			self.__textwindow.select_chars(s,e)

	def select_lines(self, sLine, eLine):
		if self.__textwindow:
			self.__textwindow.select_line(sLine)

	# return the current line pointed by the carret
	def getCurrentCharIndex(self):
		if self.__textwindow:
			return self.__textwindow.getCurrentCharIndex()
		return -1

	# return the line number
	def getLineNumber(self):
		if self.__textwindow:
			return self.__textwindow.getLineNumber()
		return 0
	
	#
	# text window listener interface
	#
	
	# this call back is called when the selection change
	def onSelChanged(self):
		self.__updateCommandList()
		self.__selChanged = 1
		if not self.__replacing and self._findReplaceDlg != None:
			self._findReplaceDlg.enableReplace(0)
					
	# this call back is called when the content of the clipboard change (or may have changed)
	def onClipboardChanged(self):
		self.__updateCommandList()
			
	#
	# command listener interface
	#
	
	# note: these copy, paste and cut operation don't use the GRiNS clipboard
	def onCopy(self):
		self.__textwindow.Copy()

	def onCut(self):
		self.__textwindow.Cut()

	def onPaste(self):
		self.__textwindow.Paste()

	def onUndo(self):
		self.__textwindow.Undo()


	#
	# find/replace support
	#

	def onFind(self):
		# if another dlg was showed, we hide it
		if self._findReplaceDlg != None:
			self._findReplaceDlg.hide()
			self._findReplaceDlg = None

		import win32dialog
		self._findReplaceDlg = win32dialog.FindDialog(self.doFindNext, self._findText, self._findOptions, self.window)
		self._findReplaceDlg.show()
	
	def onFindNext(self):
		if self._findText != None:
			self.doFindNext(self._findText, self._findOptions)

	def onReplace(self):
		# if another dlg was showed, we hide it
		if self._findReplaceDlg != None:
			self._findReplaceDlg.hide()
			self._findReplaceDlg = None

		import win32dialog
		self._findReplaceDlg = win32dialog.ReplaceDialog(self.doFindNext, self.doReplace, self.doReplaceAll, \
														self._findText, self._replaceText, self._findOptions, self.window)
		self._findReplaceDlg.show()
		if not self.__selChanged:
			self._findReplaceDlg.enableReplace(1)
		
	def doFindNext(self, text, options):
		if not self.__textwindow:
			return

		# save the text and options for the next time
		self._findText = text
		self._findOptions = options

		found = 0
		# first search from the current position
		begin = self.getCurrentCharIndex()
		if self.__textwindow.findNext(begin, text, options) == None:
			# not found, search from the begining
			ret = self.__textwindow.findNext(0, text, options)
			if ret == None:
				windowinterface.showmessage("GRiNS has finished searching the document", mtype = 'error')
			else:
				found = 1
		else:
			found = 1

		if self._findReplaceDlg != None:
			self._findReplaceDlg.enableReplace(found)
		# raz the flag whitch allows to know if a replace if directly possible.
		self.__selChanged = 0
					
	def doReplace(self, text, options, replaceText):
		if not self.__textwindow:
			return

		# save the text and options for the next time
		self._findOptions = options
		
		if self._findText != text:
			# the findwhat value has changed since the last find
			# in this special case, we jump to the next value without automatic replace
			self._findText = text
			self.onFindNext()
			return
		
		self.__replacing = 1
		# save the text and options for the next time
		self._findText = text

		# save the text for the next time
		self._replaceText = replaceText
		if self.__textwindow:
			self.__textwindow.replaceSel(replaceText)
			# seek on the next occurrence found			
			self.onFindNext()

		self.__replacing = 0

	def doReplaceAll(self, text, options, replaceText):
		if not self.__textwindow:
			return

		self.__replacing = 1
		
		# save the text and options for the next time
		self._findText = text
		self._findOptions = options
			
		begin = 0
		nocc = 0
		lastPos = None
		pos = self.__textwindow.findNext(begin, self._findText, self._findOptions)
		while pos != None and lastPos != pos:
			lastPos = pos
			self.__textwindow.replaceSel(replaceText)
			begin = self.getCurrentCharIndex()
			nocc = nocc + 1
			pos = self.__textwindow.findNext(begin, self._findText, self._findOptions)

		self.__replacing = 0

		windowinterface.showmessage("Replaced "+`nocc`+' occurrences')
		
	