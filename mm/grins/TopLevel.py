__version__ = "$Id$"

import os, posixpath
import windowinterface
import MMExc, MMAttrdefs, MMTree, MMurl
import Timing
from Hlinks import TYPE_JUMP, TYPE_CALL, TYPE_FORK

# an empty document
EMPTY = "(seq '1' ((channellist) (hyperlinks)))"

# List of currently open toplevel windows
opentops = []

class TopLevel:
	def __init__(self, main, filename):
		self._tracing = 0
		self.waiting = 0
		self.showing = 0
		self.select_fdlist = []
		self.select_dict = {}
		self._last_timer_id = None
		self.main = main
		# convert filename to URL
		type, url = MMurl.splittype(filename)
		if not type or type not in ('http', 'file', 'ftp', 'rtsp'):
			# assume filename using local convention
			type = None
			url = MMurl.pathname2url(filename)
			type, url = MMurl.splittype(url)
		host, url = MMurl.splithost(url)
		dir, base = posixpath.split(url)
		if not type and not host:
			# local file
			self.dirname = dir
		else:
			# remote file
			self.dirname = ''
		if base[-5:] == '.cmif':
			self.basename = base[:-5]
		elif base[-4:] == '.smi':
			self.basename = base[:-4]
		elif base[-5:] == '.smil':
			self.basename = base[:-5]
		else:
			self.basename = base
		if host:
			url = '//%s%s' % (host, url)
		if type:
			url = '%s:%s' % (type, url)
		self.filename = url
		self.read_it()
		self.makeplayer()
		self.window = None
		opentops.append(self)

	def __repr__(self):
		return '<TopLevel instance, url=' + `self.filename` + '>'

	def show(self):
		if self.showing:
			return
		self.load_geometry()
		self.window = windowinterface.Window(self.basename,
				deleteCallback = (self.close_callback, ()))
		self.buttons = self.window.ButtonRow(
			[('Open...', (self.open_callback, ())),
			 ('Close', (self.close_callback, ())),
			 None,
			 ('Debug', (self.debug_callback, ())),
			 ('Trace', (self.trace_callback, ()), 't')],
			top = None, bottom = None, left = None, right = None,
			vertical = 1)
		self.window.show()
		self.showing = 1

	def load_geometry(self):
		name = 'toplevel_'
		h, v = MMAttrdefs.getattr(self.root, name + 'winpos')
		width, height = MMAttrdefs.getattr(self.root, name + 'winsize')
		self.last_geometry = h, v, width, height

	def destroy(self):
		self.destroyplayer()
		if self.window:
			self.window.close()
			self.window = None
		self.showing = 0
		self.root.Destroy()
		self.player.toplevel = None
		if self in opentops:
			opentops.remove(self)

	def timer_callback(self):
		self._last_timer_id = None
		self.player.timer_callback()

	def set_timer(self, delay):
		if self._last_timer_id is not None:
			windowinterface.canceltimer(self._last_timer_id)
			self._last_timer_id = None
		if delay:
			self._last_timer_id = windowinterface.settimer(delay,
				  (self.timer_callback, ()))

	#
	# View manipulation.
	#
	def makeplayer(self):
		import Player
		self.player = Player.Player(self)

	def destroyplayer(self):
		self.player.destroy()

	#
	# Callbacks.
	#
	def open_okcallback(self, filename):
		if os.path.isabs(filename):
			cwd = self.dirname
			if cwd:
				cwd = MMurl.url2pathname(cwd)
				if not os.path.isabs(cwd):
					cwd = os.path.join(os.getcwd(), cwd)
			else:
				cwd = os.getcwd()
			if os.path.isdir(filename):
				dir, file = filename, os.curdir
			else:
				dir, file = os.path.split(filename)
			# XXXX maybe should check that dir gets shorter!
			while len(dir) > len(cwd):
				dir, f = os.path.split(dir)
				file = os.path.join(f, file)
			if dir == cwd:
				filename = file
		try:
			top = TopLevel(self.main, MMurl.pathname2url(filename))
		except:
			msg = sys.exc_value
			if type(msg) is type(self):
				if hasattr(msg, 'strerror'):
					msg = msg.strerror
				else:
					msg = msg.args[0]
			windowinterface.showmessage('Open operation failed.\n'+
						    'File: '+filename+'\n'+
						    'Error: '+`msg`)
			return
		top.show()
		top.player.show()
		top.player.playsubtree(top.root)
		top.setready()

	def open_callback(self):
		cwd = self.dirname
		if cwd:
			cwd = MMurl.url2pathname(cwd)
			if not os.path.isabs(cwd):
				cwd = os.path.join(os.getcwd(), cwd)
		else:
			cwd = os.getcwd()
		windowinterface.FileDialog('Open CMIF file:', cwd, '*.cmif',
					   '', self.open_okcallback, None)

	def read_it(self):
		import time
		self.changed = 0
		print 'parsing', self.filename, '...'
		t0 = time.time()
		if self.filename[-4:] == '.smi' or \
		   self.filename[-5:] == '.smil':
			import SMILTree
			self.root = SMILTree.ReadFile(self.filename)
		else:
			self.root = MMTree.ReadFile(self.filename)
		t1 = time.time()
		print 'done in', round(t1-t0, 3), 'sec.'
		Timing.changedtimes(self.root)
		self.context = self.root.GetContext()

	def close_callback(self):
		self.setwaiting()
		self.close()
		self.setready()

	def close(self):
		self.destroy()
		if len(opentops) == 0:
			raise SystemExit, 0

	def debug_callback(self):
		import pdb
		pdb.set_trace()

	def trace_callback(self):
		import trace
		if self._tracing:
			trace.unset_trace()
			self._tracing = 0
		else:
			self._tracing = 1
			trace.set_trace()

	def setwaiting(self):
		if self.waiting: return
		self.waiting = 1
		windowinterface.setcursor('watch')
		self.player.setwaiting()

	def setready(self):
		if not self.waiting: return
		self.waiting = 0
		self.player.setready()
		windowinterface.setcursor('')

	#
	# Global hyperjump interface
	#
	def jumptoexternal(self, uid, aid, type):
		# XXXX Should check that document isn't active already,
		# XXXX and, if so, should jump that instance of the
		# XXXX document.
		import MMurl
		if '/' not in uid:
			url = self.filename
		elif uid[-2:] == '/1':
			url = uid[:-2]
		else:
			url = uid
		type, url = MMurl.splittype(url)
		host, url = MMurl.splithost(url)
		if not type and not host:
			filename = MMurl.url2pathname(url)
			if not os.path.isabs(filename) and self.dirname:
				filename = os.path.join(self.dirname, filename)
			url = MMurl.pathname2url(filename)
		if host:
			url = '//%s%s' % (host, url)
		if type:
			url = '%s:%s' % (type, url)
		for top in opentops:
			if top is not self and top.is_document(url):
				break
		else:
			try:
				top = TopLevel(self.main, url)
			except:
				msg = sys.exc_value
				if type(msg) is type(self):
					if hasattr(msg, 'strerror'):
						msg = msg.strerror
					else:
						msg = msg.args[0]
				windowinterface.showmessage(
					'Open operation failed.\n'+
					'File: '+url+'\n'+
					'Error: '+`msg`)
				return 0
		top.show()
		node = top.root
		if '/' not in uid:
			try:
				node = top.root.context.mapuid(uid)
			except NoSuchUIDError:
				print 'uid not found in document'
		top.player.show((top.player.playfromanchor, (node, aid)))
		if type == TYPE_CALL:
			self.player.pause(1)
		elif type == TYPE_JUMP:
			self.close()
		return 1

	def is_document(self, url):
		return self.filename == url
## 		import posix

## 		try:
## 			fn = self.filename
## 			if self.dirname:
## 				fn = os.path.join(self.dirname, self.filename)
## 			ourdata = posix.stat(fn)
## 			hisdata = posix.stat(filename)
## 		except posix.error:
## 			return 0
## 		return (ourdata == hisdata)

	def _getlocalexternalanchors(self):
		fn = self.filename
		if not '/' in fn:
			fn = './' + fn
		rv = []
		alist = MMAttrdefs.getattr(self.root, 'anchorlist')
		for i, t, v in alist:
			rv.append((fn, i))
		return rv

	def getallexternalanchors(self):
		rv = []
		for top in opentops:
			if top is not self:
				rv = rv + top._getlocalexternalanchors()
		return rv
