# Top level menu.
# Read the file and create a menu that accesses the basic functions.

import os

import gl, DEVICE
import fl
from FL import *

import glwindow
from Dialog import BasicDialog
from ViewDialog import ViewDialog

import MMExc
import MMAttrdefs
import MMTree

from EditMgr import EditMgr

import Timing


# Parametrizations
BHEIGHT = 30				# Button height
HELPDIR = None

def sethelpdir(helpdir):
	global HELPDIR
	HELPDIR = helpdir

class TopLevel(ViewDialog, BasicDialog):
	#
	# Initialization.
	#
	def init(self, filename):
		self = ViewDialog.init(self, 'toplevel_')
		self.filename = filename
		self.dirname, self.basename = os.path.split(self.filename)
		MMAttrdefs.toplevel = self # For hack in MMAttrdefs.getattr()
		self.read_it()
		width, height = \
			MMAttrdefs.getattr(self.root, 'toplevel_winsize')
		self = BasicDialog.init(self, width, height, 'CMIF')
		self.makeviews()	# References the form just made
		return self
	#
	def __repr__(self):
		return '<TopLevel instance, filename=' + `self.filename` + '>'
	#
	# Interface to prefix relative filenames with the CMIF file's
	# directory, if the resulting filename exists.
	#
	def findfile(self, filename):
		if os.path.isabs(filename):
			return filename
		altfilename = os.path.join(self.dirname, filename)
		if os.path.exists(altfilename):
			return altfilename
		# As a last resort, search along the $CMIFPATH
		import cmif
		return cmif.findfile(filename)
	#
	# Extend inherited show/hide/destroy interface.
	#
	def show(self):
		if self.showing: return
		BasicDialog.show(self)
		fl.qdevice(DEVICE.WINQUIT)
	#
	def hide(self):
		BasicDialog.hide(self)
		self.hideviews()
	#
	def destroy(self):
		self.hide()
		self.destroyviews()
		self.root.Destroy()
		import Clipboard
		type, data = Clipboard.getclip()
		if type == 'node' and data <> None:
			Clipboard.setclip('', None)
			data.Destroy()
		for v in self.views: v.toplevel = None
		self.views = []
		BasicDialog.destroy(self)
	#
	# Main interface.
	#
	def run(self):
		return fl.do_forms()
	#
	# EditMgr interface (as dependent client).
	# This is the first registered client; hence its commit routine
	# will be called first, so it can fix the timing for the others.
	# It also flushes the attribute cache maintained by MMAttrdefs.
	#
	def transaction(self):
		# Always allow transactions
		return 1
	#
	def commit(self):
		# Fix the timing -- views may depend on this.
		self.changed = 1
		MMAttrdefs.flushcache(self.root)
		Timing.changedtimes(self.root)
	#
	def rollback(self):
		# Nothing has happened.
		pass
	#
	def kill(self):
		print 'TopLevel.kill() should not be called!'
	#
	# Make the menu form (called from BasicDialog.init).
	#
	def make_form(self):
		width, height = self.width, self.height
		bheight = height/11
		self.form = form = fl.make_form(FLAT_BOX, width, height)
		#
		# The topmost button is a shortcut to start playing.
		#
		# The next four buttons in the menu open/close views.
		# They show a light which indicates whether the view
		# is open or closed.
		# The fifth button opens/closes the Help window,
		# which is almost, but not quite, completely like a view.
		#
		# Their callbacks are set later, in makeviews.
		#
		x, y, w, h = 0, height, width, bheight
		#
		y = y - h
		self.playbutton = \
			form.add_button(INOUT_BUTTON,x,y,w,h, 'Play')
		#
		y = y - h
		self.pvbutton = \
			form.add_lightbutton(PUSH_BUTTON,x,y,w,h, 'Player')
		#
		y = y - h
		self.bvbutton = \
			form.add_lightbutton(PUSH_BUTTON,x,y,w,h, 'Hierarchy')
		#
		y = y - h
		self.cvbutton = \
			form.add_lightbutton(PUSH_BUTTON,x,y,w,h, 'Time chart')
		#
		y = y - h
		self.svbutton = \
		    form.add_lightbutton(PUSH_BUTTON,x,y,w,h, 'Style sheet')
		#
		y = y - h
		self.lvbutton = \
		    form.add_lightbutton(PUSH_BUTTON,x,y,w,h, 'Hyperlinks')
		#
		y = y - h
		self.helpbutton = \
			form.add_lightbutton(PUSH_BUTTON,x,y,w,h, 'Help')
		#
		# The bottom three buttons are document-related commands.
		# They remain pressed while the command is executing.
		#
		y = 3*bheight
		#
		y = y - h
		self.savebutton = \
			form.add_button(INOUT_BUTTON,x,y,w,h, 'Save')
		self.savebutton.set_call_back(self.save_callback, None)
		#
		y = y - h
		self.restorebutton = \
			form.add_button(INOUT_BUTTON,x,y,w,h, 'Restore')
		self.restorebutton.set_call_back(self.restore_callback, None)
		#
		y = y - h
		self.quitbutton = \
			form.add_button(INOUT_BUTTON,x,y,w,h, 'Quit')
		self.quitbutton.set_call_back(self.quit_callback, None)
		#
	#
	# View manipulation.
	#
	def makeviews(self):
		import BlockView
		self.blockview = BlockView.BlockView().init(self)
		#
		import ChannelView
		self.channelview = \
			ChannelView.ChannelView().init(self)
		#
		import Player
		self.player = Player.Player().init(self)
		#
		import StyleSheet
		self.styleview = StyleSheet.StyleSheet().init(self)
		#
		import Help
		helpdir = HELPDIR
		if helpdir == None:
			import cmif
			helpdir = cmif.findfile('help')
		self.help = Help.HelpWindow().init(helpdir, self)
		#
		import LinkEdit
		self.links = LinkEdit.LinkEdit().init(self)
		#
		# Views that are destroyed by restore (currently all)
		self.views = [self.blockview, self.channelview, self.player, \
			  self.styleview, self.links, self.help]
		#
		self.bvbutton.set_call_back(self.view_callback, self.blockview)
		self.cvbutton.set_call_back(self.view_callback, \
						self.channelview)
		self.pvbutton.set_call_back(self.view_callback, self.player)
		self.playbutton.set_call_back(self.play_callback, None)
		self.svbutton.set_call_back(self.view_callback, self.styleview)
		self.lvbutton.set_call_back(self.view_callback, self.links)
		self.helpbutton.set_call_back(self.view_callback, self.help)
	#
	def hideviews(self):
		for v in self.views: v.hide()
	#
	def checkviews(self):
		# Check that the button states are still correct
		self.bvbutton.set_button(self.blockview.is_showing())
		self.cvbutton.set_button(self.channelview.is_showing())
		self.pvbutton.set_button(self.player.is_showing())
		self.svbutton.set_button(self.styleview.is_showing())
		self.lvbutton.set_button(self.links.is_showing())
		self.helpbutton.set_button(self.help.is_showing())
	#
	def destroyviews(self):
		self.hideviews()
		for v in self.views: v.destroy()
	#
	# Callbacks.
	#
	def play_callback(self, (obj, arg)):
		if obj.get_button():
			self.player.show()
			self.player.playsubtree(self.root)
	#
	def view_callback(self, (obj, view)):
		if obj.get_button():
			view.show()
		else:
			view.hide()
	#
	def save_callback(self, (obj, arg)):
		if not obj.pushed: return
		# Get rid of hyperlinks outside the current tree and clipboard
		# (XXX We shouldn't *save* the links to/from the clipboard,
		# but we don't want to throw them away either...)
		roots = [self.root]
		import Clipboard
		type, data = Clipboard.getclip()
		if type == 'node' and data != None:
			roots.append(data)
		self.context.sanitize_hyperlinks(roots)
		# Get all windows to save their current geometry.
		self.get_geometry()
		self.save_geometry()
		for v in self.views:
			v.get_geometry()
			v.save_geometry()
		# The help window too!
		if self.help <> None:
			self.help.save_geometry()
		# Make a back-up of the original file...
		try:
			os.rename(self.filename, self.filename + '~')
		except os.error:
			pass
		print 'saving to', self.filename, '...'
		MMTree.WriteFile(self.root, self.filename)
		print 'done saving.'
		self.changed = 0
		obj.set_button(0)
	#
	def restore_callback(self, (obj, arg)):
		if not obj.pushed:
			return
		if not self.editmgr.transaction():
			obj.set_button(0)
			return
		self.editmgr.rollback()
		if self.changed:
			l1 = 'Are you sure you want to re-read the file?'
			l2 = '(This will destroy the changes you have made)'
			l3 = 'Click Yes to restore, No to keep your changes'
			reply = fl.show_question(l1, l2, l3)
			if not reply:
				obj.set_button(0)
				return
		self.editmgr.unregister(self)
		self.editmgr.destroy() # kills subscribed views
		self.help.destroy() # XXX Needed because help's a view now...
		self.context.seteditmgr(None)
		self.root.Destroy()
		self.read_it()
		#
		# Move the menu window to where it's supposed to be
		#
		self.get_geometry() # From window
		old_geometry = self.last_geometry
		self.load_geometry() # From document
		new_geometry = self.last_geometry
		if new_geometry[:2]<>(-1,-1) and new_geometry <> old_geometry:
			self.hide()
			# Undo unwanted save_geometry()
			self.last_geometry = new_geometry
			self.save_geometry()
			self.show()
		#
		self.makeviews()
		obj.set_button(0)
	#
	def read_it(self):
		import time
		self.changed = 0
		print 'parsing', self.filename, '...'
		t0 = time.millitimer()
		self.root = MMTree.ReadFile(self.filename)
		t1 = time.millitimer()
		print 'done in', (t1-t0) * 0.001, 'sec.'
		Timing.changedtimes(self.root)
		self.context = self.root.GetContext()
		self.editmgr = EditMgr().init(self.root)
		self.context.seteditmgr(self.editmgr)
		self.editmgr.register(self)
	#
	def quit_callback(self, (obj, arg)):
		ok = self.quit_ok()
		obj.set_button(0)
		if ok:
			raise SystemExit, 0

	def quit_ok(self):
		if self.changed:
			l1 = 'You haven\'t saved your changes yet;'
			l2 = 'do you want to save them before quitting?'
			l3 = ''
			b1 = 'Save'
			b2 = 'Don\'t save'
			b3 = 'Cancel'
			reply = fl.show_choice(l1, l2, l3, b1, b2, b3)
			if reply == 3:
				return 0
			if reply == 1:
				self.save_callback(obj, arg)
		return 1
	#
	# GL event callback for WINSHUT and WINQUIT (called from glwindow)
	#
	def winshut(self):
		self.quit_callback(self.quitbutton, 0)
