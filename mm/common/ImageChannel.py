# Image channel

import MMExc
import MMAttrdefs

import gl
import GL
import DEVICE
import fl

from Channel import Channel
from ChannelWindow import ChannelWindow

from AnchorEdit import A_ID, A_TYPE, A_ARGS, ATYPE_NORMAL, ATYPE_PAUSE, \
	ATYPE_AUTO

import FileCache


def between(v, x0, x1):
	return ((x0 <= v and v <= x1) or (x1 <= v and v <= x0))

class ImageWindow(ChannelWindow):
	#
	# Initialization function.
	#
	def init(self, (name, attrdict, channel)):
		self = ChannelWindow.init(self, name, attrdict, channel)
		self.clear()
		self.player = channel.player
		return self
	#
	def show(self):
		if self.is_showing():
			self.pop()
			return
		ChannelWindow.show(self)
		fl.qdevice(DEVICE.LEFTMOUSE)
		self.render()
	#
	def redraw(self):
		if not self.is_showing():
			return
		gl.reshapeviewport()
		winwidth, winheight = gl.getsize()
		self.xcorner = int(winwidth - self.xsize*self.effscale) / 2
		self.ycorner = int(winheight - self.ysize*self.effscale) / 2
		gl.ortho2(-0.5, winwidth-0.5, -0.5, winheight-0.5)
		self.render()
	#
	def clear(self):
		self.node = None
		self.parray = None
		self.error = None
		self.anchors = []
		self.newanchor = None
		self.xsize = self.ysize = 0
		self.xcorner = self.ycorner = 0
		self.effscale = 1.0
		self.mousescale = 1.0
		self.setcolors()
		if self.is_showing():
			self.setwin()
			gl.RGBcolor(self.bgcolor)
			gl.clear()
	#
	def setcolors(self):
		if self.node:
			self.bgcolor = MMAttrdefs.getattr(self.node, 'bgcolor')
			self.fgcolor = MMAttrdefs.getattr(self.node, 'fgcolor')
			self.hicolor = MMAttrdefs.getattr(self.node, 'hicolor')
			return
		if self.attrdict.has_key('bgcolor'):
			self.bgcolor = self.attrdict['bgcolor']
		else:
			self.bgcolor = 255, 255, 255
		if self.attrdict.has_key('fgcolor'):
			self.fgcolor = self.attrdict['fgcolor']
		else:
			self.fgcolor = 0, 0, 0
		if self.attrdict.has_key('hicolor'):
			self.hicolor = self.attrdict['hicolor']
		else:
			self.hicolor = 255, 0, 0
	#
	def getmouse(self):
		mx, my = fl.get_mouse()
		mx = int((mx - self.xcorner) / self.mousescale)
		my = int((my - self.ycorner) / self.mousescale)
		return mx, my
	#
	def mouse(self, (dev, val)):
		if dev == DEVICE.RIGHTMOUSE:
			ChannelWindow.mouse(self, (dev, val))
			return
		if not self.node:
			gl.ringbell()
			return
		mx, my = self.getmouse()
		if self.newanchor:
			# We're not playing, we're defining anchors
			if dev <> DEVICE.LEFTMOUSE:
				gl.ringbell()
				return
			if val == 1:
				self.pm = (mx, my)
				fl.qdevice(DEVICE.MOUSEX)
				fl.qdevice(DEVICE.MOUSEY)
			else:
				fl.unqdevice(DEVICE.MOUSEX)
				fl.unqdevice(DEVICE.MOUSEY)
				a = self.newanchor
				self.newanchor = (a[0], a[1], \
					  [self.pm[0], self.pm[1], mx, my])
				self.drawnewanchor()
			return
		if (dev, val) <> (DEVICE.LEFTMOUSE, 1):
			return
		if not self.anchors:
			print 'mouse: no anchors on this node'
		al2 = []
		for a in self.anchors:
			args = a[A_ARGS]
			if not args:
				al2.append(a)
				continue
			x0, y0, x1, y1 = args[0], args[1], args[2], args[3]
			if between(mx, x0, x1) and between(my, y0, y1):
				al2.append(a)
		if not al2:
			print 'Mouse: No anchor selected'
			gl.ringbell()
			return
		rv = self.player.anchorfired(self.node, al2)
		# If this was a paused anchor and it didn't fire
		# stop showing the node
		if rv == 0 and len(al2) == 1 and al2[0][A_TYPE] == ATYPE_PAUSE:
			self.channel.haspauseanchor = 0
			self.channel.done(0)
	#
	def mousex(self, val):
		if not self.newanchor:
			print '*** Huh? MOUSEX but not defining anchors ***'
			return
		self.newxy()
	#
	def mousey(self, val):
		if not self.newanchor:
			print '*** Huh? MOUSEY but not defining anchors ***'
			return
		self.newxy()
	#
	def newxy(self):
		mx, my = self.getmouse()
		a = self.newanchor
		self.newanchor = (a[0], a[1], [self.pm[0], self.pm[1], mx, my])
		self.drawnewanchor()
	#
	def armimage(self, (filename_arg, node)):
		# (Import imgfile here so if it doesn't exist we can
		# still play documents that don't contain images...)
		import imgfile
		filename = rgbcache.get(filename_arg)
		self.node = node
		self.setcolors()
		self.parray = None
		self.effscale = 1.0 # Scale for lrectwrite
		self.mousescale = 1.0 # Scale for mouse and anchors
		self.xcorner = 0
		self.ycorner = 0
		self.error = None
		try:
			self.xsize, self.ysize, dummy = \
				imgfile.getsizes(filename)
		except imgfile.error, msg:
			print 'Cannot get size of image file', filename_arg, \
				  ':', msg
			self.error = 'Bad or missing file ' + `filename_arg`
			return
		if self.is_showing():
			self.setwin()
			winwidth, winheight = gl.getsize()
		else:
			winwidth, winheight = 0, 0
		self.effscale = MMAttrdefs.getattr(node, 'scale')
		if self.effscale <= 0.0:
			if not self.is_showing():
				self.effscale = 1.0
			else:
				self.effscale = \
					min(float(winwidth)/self.xsize, \
					    float(winheight)/self.ysize)
		self.mousescale = self.effscale
		try:
			if self.effscale == int(self.effscale):
				self.parray = imgfile.read(filename)
			else:
				width = int(self.xsize * self.effscale)
				height = int(self.ysize * self.effscale)
				self.parray = imgfile.readscaled(filename, \
					                         width, height)
				self.effscale = 1.0
				self.xsize, self.ysize = width, height
		except imgfile.error, msg:
			print 'Cannot read image file', filename_arg, ':', msg
			self.error = 'Cannot read file ' + `filename_arg`
		self.xcorner = int(winwidth - self.xsize*self.effscale) / 2
		self.ycorner = int(winheight - self.ysize*self.effscale) / 2
	#
	def showimage(self):
		if self.is_showing():
			self.pop() # Implies gl.winset()
			self.render()
	#
	def setanchors(self, anchors):
		self.anchors = anchors
		# NB: this routine must be called before showimage
	#
	# Start defining an anchor
	def setdefanchor(self, anchor):
		if anchor in self.anchors:
			self.saveanchor = anchor
			self.anchors.remove(anchor)
		else:
			self.saveanchor = None
		self.newanchor = anchor
		self.redraw()
	#
	# Stop defining an anchor
	def getdefanchor(self):
		res = self.newanchor
		self.anchors.append(res)
		self.saveanchor = None
		self.newanchor = None
		self.redraw()
		return res
	#
	# Abort defining an anchor
	def enddefanchor(self, anchor):
		if self.saveanchor <> None:
			self.anchors.append(self.saveanchor)
			self.saveanchor = None
		self.newanchor = None
		self.redraw()
	#
	def render(self):
		gl.RGBcolor(self.bgcolor)
		gl.clear()
		width, height = gl.getsize()
		if self.parray:
			gl.rectzoom(self.effscale, self.effscale)
			gl.lrectwrite(self.xcorner, self.ycorner, \
				self.xcorner+self.xsize-1, \
				self.ycorner+self.ysize-1, \
				self.parray)
		else:
			if self.error:
				gl.RGBcolor(self.fgcolor)
				width, height = gl.getsize()
				x, y = width/2, height/2
				sw = gl.strwidth(self.error)
				sh = gl.getheight()
				x = max(0, x - sw/2)
				y = y + sh/2
				gl.cmov2(x, y)
				gl.charstr(self.error)
		# Draw anchors even if the image can't be drawn
		if self.anchors:
			gl.RGBcolor(self.hicolor)
			for dummy, tp, a in self.anchors:
				self.drawanchor(a)
		self.drawnewanchor()
	#
	# Subroutine to render just the new anchor in the pop-up planes.
	# In all cases the pop-up planes are first cleared.
	#
	def drawnewanchor(self):
		# XXX I'm using PUPDRAW because it's the only
		# mode that works on a basic Indigo; on the
		# other hand SGI says that pop-up planes are
		# maintained for compatibility only...
		gl.drawmode(GL.PUPDRAW)
		gl.color(0)
		gl.clear()
		if self.newanchor:
			gl.mapcolor((1,) + self.fgcolor)
			gl.color(1)
			self.drawanchor(self.newanchor[2])
		gl.drawmode(GL.NORMALDRAW)
	#
	# Subroutine to draw an anchor
	#
	def drawanchor(self, a):
		if len(a) <> 4:
			return
		x0, y0, x1, y1 = a[0], a[1], a[2], a[3]
		x0 = int(x0 * self.mousescale + self.xcorner)
		x1 = int(x1 * self.mousescale + self.xcorner)
		y0 = int(y0 * self.mousescale + self.ycorner)
		y1 = int(y1 * self.mousescale + self.ycorner)
		gl.bgnclosedline()
		gl.v2i(x0, y0)
		gl.v2i(x0, y1)
		gl.v2i(x1, y1)
		gl.v2i(x1, y0)
		gl.endclosedline()


# XXX Make the image channel class a derived class from ImageWindow?!

class ImageChannel(Channel):
	#
	# Declaration of attributes that are relevant to this channel,
	# respectively to nodes belonging to this channel.
	#
	chan_attrs = ['winsize', 'winpos', 'visible']
	node_attrs = ['file', 'duration', 'scale', 'arm_duration', \
		 'bgcolor', 'fgcolor', 'hicolor']
	#
	def init(self, (name, attrdict, player)):
		self = Channel.init(self, name, attrdict, player)
		self.window = ImageWindow().init(name, attrdict, self)
		self.armed_node = 0
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
	def getduration(self, node):
		return Channel.getduration(self, node)
	#
	# clear is called by Channel.clearnode() to clear remains of
	# previous node.
	def clear(self):
		self.window.clear()
	#
	def play(self, (node, callback, arg)):
		if not self.is_showing():
			callback(arg)
			return
	        if node <> self.armed_node:
		    print 'ImageChannel: node not armed'
		    self.arm(node)
		self.armed_node = None
		self.showanchors(node)
		self.window.showimage()
		Channel.play(self, node, callback, arg)
	#
	def defanchor(self, node, anchor):
		self.arm(node)
		self.showanchors(node)
		self.window.setdefanchor(anchor)
		self.window.showimage()

		import AdefDialog
		try:
			rv = AdefDialog.run('Select reactive area with mouse')
			a = self.window.getdefanchor()
			if rv == 0:
				a = (a[0], a[1], [])
			return a
		except AdefDialog.cancel:
			self.window.enddefanchor(anchor)
			return None
	#
	def showanchors(self, node):
		try:
			alist = node.GetRawAttr('anchorlist')
		except MMExc.NoSuchAttrError:
			self.window.setanchors([])
			return
		al2 = []
		self.autoanchor = None
		self.haspauseanchor = 0
		for a in alist:
			if a[A_TYPE] == ATYPE_AUTO:
				self.autoanchor = a
			if a[A_TYPE] == ATYPE_PAUSE:
				self.haspauseanchor = 1
			if a[A_TYPE] not in (ATYPE_NORMAL, ATYPE_PAUSE):
				continue
			if len(a[A_ARGS]) not in (0,4):
				print 'ImageChannel: funny-sized anchor'
			else:
				al2.append(a)
		self.window.setanchors(al2)
	#
	def reset(self):
		self.window.clear()
	#
	def arm(self, node):
		if not self.is_showing():
			return
		self.window.armimage(self.getfilename(node), node)
		self.armed_node = node
	#
	def getfilename(self, node):
		return MMAttrdefs.getattr(node, 'file')
	#


temps = []

def makergbfile(filename):
	import imghdr
	import os
	uncompressed = None
	if filename[-2:] == '.Z':
		filename = uncompressed = conv('zcat <$1 >$2', filename)
	try:
		type = imghdr.what(filename)
	except IOError:
		type = None
	if type == 'pnm':
		res = conv('fromppm $1 $2', filename)
	elif type == 'gif':
		res = conv('fromgif $1 $2', filename)
	elif type == 'tiff':
		tempname = conv('tifftopnm <$1 >$2', filename)
		res = conv('fromppm $1 $2', tempname)
		os.unlink(tempname)
		temps.remove(tempname)
	elif type == 'rast':
		res = conv('fromsun $1 $2', filename)
	else:
		res = filename
	if None <> uncompressed <> res:
		os.unlink(uncompressed)
		temps.remove(uncompressed)
	return res

def conv(cmd, filename):
	import os
	import tempfile
	tempname = tempfile.mktemp()
	temps.append(tempname)
	cmd = 'set ' + filename + ' ' + tempname + '; ' + cmd
	print 'Executing:', cmd
	sts = os.system(cmd)
	if sts:
		print cmd
		print  'Exit status:', sts
	return tempname

def cleanup():
	import os
	rgbcache.flushall()
	for tempname in temps:
		try:
			os.unlink(tempname)
		except (os.error, IOError):
			pass
	temps[:] = []

rgbcache = FileCache.FileCache().init(makergbfile)
