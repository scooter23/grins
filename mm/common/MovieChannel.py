# Movie channel

# For now, this play only movies recorded by Jack's "camcorder" program.
# The format is the following:
#	first line: "CMIF video 1.0"
#	second line: "(width, height, packfactor)"
#	each image:
#		one line: "(time, datasize)"
#		datasize bytes of binary data
# For compatibility with some old movies the header line, pack factor and
# data size are optional.  Default pack factor is 2; default data size is
# (width/2) * (height/2) if pack factor is nonzero, or width*height*4
# if it is zero (indicating a color movie).
# An EOF indicates the end of the file; 

import sys
sys.path.append('/ufs/guido/src/video')	# For VFile

import os
from stat import *

import MMExc
import MMAttrdefs

import gl
import GL

import VFile

# Errors that VFile operations may raise
VerrorList = VFile.Error, os.error, IOError, RuntimeError, EOFError

from Channel import Channel
from ChannelWindow import ChannelWindow

class MovieWindow(ChannelWindow):
	#
	# Initialization function.
	#
	def init(self, (title, attrdict)):
		self = ChannelWindow.init(self, title, attrdict)
		self.clear()
		return self
	#
	def show(self):
		if self.wid <> 0:
			self.setwin()
			return
		ChannelWindow.show(self)
		self.clear()
	#
	def redraw(self):
		if self.wid == 0: return
		gl.reshapeviewport()
		self.erase()
	#
	def clear(self):
		self.node = self.vfile = self.lookahead = None
		if self.wid <> 0:
			gl.winset(self.wid)
			gl.RGBmode()
			gl.gconfig()
			self.rgbmode = 1
			self.erase()
	#
	def erase(self):
		if self.node <> None:
			r, g, b = MMAttrdefs.getattr(self.node, 'bgcolor')
		elif self.attrdict.has_key('bgcolor'):
			r, g, b = self.attrdict['bgcolor']
		else:
			r, g, b = 255, 255, 255
		#
		if self.rgbmode:
			gl.RGBcolor(r, g, b)
		else:
			INDEX = 255
			gl.mapcolor(INDEX, r, g, b)
			gl.color(INDEX)
		#
		gl.clear()
		#
		if self.vfile <> None:
			self.centerimage()
	#
	def setfile(self, (filename, node)):
		#self.clear()
		try:
			self.vfile = VFile.VinFile().init(filename)
			self.vfile.warmcache()
		except EOFError:
			print 'Empty movie file', `filename`
			return
		except VerrorList, msg:
			print 'Cannot open movie file', `filename`, ':', msg
			return
		self.node = node
		self.vfile.magnify = MMAttrdefs.getattr(self.node, 'scale')
		dummy = self.peekaboo()
		if self.lookahead <> None and self.wid <> 0:
			self.pop()
			gl.winset(self.wid)
			#self.erase()
			self.vfile.initcolormap()
			self.rgbmode = (self.vfile.format == 'rgb')
			self.centerimage()
	#
	def centerimage(self):
		w, h = self.vfile.width, self.vfile.height
		w, h = int(w*self.vfile.magnify), int(h*self.vfile.magnify)
		W, H = gl.getsize()
		self.vfile.xorigin, self.vfile.yorigin = (W-w)/2, (H-h)/2
	#
	def peekaboo(self):
		try:
			self.lookahead = self.vfile.getnextframeheader()
			return self.lookahead[0] * 0.001
		except VerrorList:
			self.lookahead = None
			return 0.0
	#
	def done(self):
		return self.lookahead == None
	#
	def nextframe(self, skip):
		if self.lookahead == None:
			return 0.0
		time, size, chromsize = self.lookahead
		if self.wid == 0 or skip:
			try:
				self.vfile.skipnextframedata(size, chromsize)
			except VerrorList:
				return 0.0
		else:
			gl.winset(self.wid)
			try:
				data, chromdata = \
				  self.vfile.getnextframedata(size, chromsize)
				self.vfile.showframe(data, chromdata)
			except VerrorList:
				return 0.0
		return self.peekaboo()


# XXX Make the movie channel class a derived class from MovieWindow?!

class MovieChannel(Channel):
	#
	# Declaration of attributes that are relevant to this channel,
	# respectively to nodes belonging to this channel.
	#
	chan_attrs = ['winsize', 'winpos', 'visible']
	node_attrs = ['file', 'scale', 'bgcolor', 'arm_duration']
	#
	def init(self, (name, attrdict, player)):
		self = Channel.init(self, name, attrdict, player)
		self.window = MovieWindow().init(name, attrdict)
		self.armed_node = None
		return self
	#
	def show(self):
		if self.may_show():
			self.window.show()
	#
	def hide(self):
		self.window.hide()
	#
	def is_showing(self):
		return self.window.is_showing()
	#
	def destroy(self):
		self.window.destroy()
	#
	def save_geometry(self):
		self.window.save_geometry()
	#
	
	def arm(self, node):
		if not self.is_showing():
			return
		filename = self.getfilename(node)
		self.window.setfile(filename, node)
		self.armed_node = node
	def play(self, (node, callback, arg)):
		if not self.is_showing():
			self.player.enter(node.t1-node.t0, 0, callback, arg)
			return
	        if node <> self.armed_node:
		    print 'MovieChannel: node not armed'
		    self.arm(node)
		self.armed_node = None
		self.starttime = self.player.timefunc()
		self.played = self.skipped = 0
		self.poll(callback, arg) # Put on the first image right now
	#
	def poll(self, cb_arg):
		self.qid = None
		if self.window.done(): # Last frame
			if self.played:
				print 'Played ', self.played*100/ \
					  (self.played+self.skipped), \
					  '% of the frames'
			callback, arg = cb_arg
			callback(arg)
			return
		else:
			t = self.window.nextframe(0)
			self.played = self.played + 1
			now = self.player.timefunc()
			while t and self.starttime + t <= now:
				t = self.window.nextframe(1)
				self.skipped = self.skipped + 1
			self.qid = self.player.enterabs(self.starttime + t, \
				1, self.poll, cb_arg)
	#
	def reset(self):
		self.window.clear()
	#
	def getduration(self, node):
		# To estimate the duration: read the header and the first
		# image; use stat to get the total file size; use this
		# to estimate the number of images; multiply this with
		# the time listed for the first image...
		filename = self.getfilename(node)
		return duration_cache.get(filename)
	#
	def getfilename(self, node):
		return MMAttrdefs.getattr(node, 'file')
	#


def getfilesize(filename):
	from stat import ST_SIZE
	try:
		st = os.stat(filename)
		return st[ST_SIZE]
	except os.error:
		return -1


# Cache durations

def getduration(filename):
	totalsize = getfilesize(filename)
	try:
		vfile = VFile.VinFile().init(filename)
	except VerrorList:
		print 'Cannot open movie file',
		print `filename`, 'to get duration'
		return 0.0
	pos1 = vfile.fp.tell()
	try:
		time = vfile.skipnextframe()
	except EOFError:
		return 0.0
	pos2 = vfile.fp.tell()
	imagesize = pos2 - pos1
	imagecount = (totalsize - pos1) / imagesize
	return 0.001 * time * imagecount

import FileCache
duration_cache = FileCache.FileCache().init(getduration)
