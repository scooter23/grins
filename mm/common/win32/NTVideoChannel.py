__version__ = "$Id$"

#
# WIN32 Video channel.
#

from Channel import *

# node attributes
import MMAttrdefs

# url parsing
import os, ntpath, urllib, MMurl

# std win32 libs 
import win32ui,win32con

# DirectShow support
DirectShowSdk=win32ui.GetDS()

# private graph notification message
WM_GRPAPHNOTIFY=win32con.WM_USER+101

# channel types
[SINGLE, HTM, TEXT, MPEG] = range(4)

class VideoChannel(ChannelWindow):
	node_attrs = ChannelWindow.node_attrs + \
		     ['bucolor', 'hicolor', 'scale', 'center',
		      'clipbegin', 'clipend']
	_window_type = MPEG
	def __init__(self, name, attrdict, scheduler, ui):
		ChannelWindow.__init__(self, name, attrdict, scheduler, ui)
		
		# DirectShow Graph builders
		self._builders={}

		# active builder from self._builders
		self._playBuilder=None

		# scheduler notification mechanism
		self.__qid=None

	def __repr__(self):
		return '<VideoChannel instance, name=' + `self._name` + '>'

	def do_show(self, pchan):
		if not ChannelWindow.do_show(self, pchan):
			return 0
		for b in self._builders.values():
			b.SetVisible(1)
		return 1

	def do_hide(self):
		for b in self._builders.values():
			b.SetVisible(0)
		if self.played_display:
			self.played.display.close()
		ChannelWindow.do_hide(self)

	def destroy(self):
		if self._playBuilder:
			self._playBuilder.Stop()
		for b in self._builders.values():
			b.SetVisible(0)
		del self._builders
		ChannelWindow.destroy(self)

	def do_arm(self, node, same=0):
		if debug:print 'VideoChannel.do_arm('+`self`+','+`node`+'same'+')'
		if node in self._builders.keys():
			return 1
		if node.type != 'ext':
			self.errormsg(node, 'Node must be external')
			return 1
		fn = self.getfileurl(node)
		fn = MMurl.urlretrieve(fn)[0]
		fn = self.toabs(fn)
		builder=DirectShowSdk.CreateGraphBuilder()
		if builder:
			builder.RenderFile(fn)
			self._builders[node]=builder
		else:
			print 'Failed to create GraphBuilder'

		drawbox = MMAttrdefs.getattr(node, 'drawbox')
		if drawbox:
			self.armed_display.fgcolor(self.getbucolor(node))
		else:
			self.armed_display.fgcolor(self.getbgcolor(node))
		hicolor = self.gethicolor(node)
		for a in node.GetRawAttrDef('anchorlist', []):
			atype = a[A_TYPE]
			if atype not in SourceAnchors or atype == ATYPE_AUTO:
				continue
			b = self.armed_display.newbutton((0,0,1,1))
			b.hiwidth(3)
			if drawbox:
				b.hicolor(hicolor)
			self.setanchor(a[A_ID], a[A_TYPE], b)
		return 1

	# Async Channel play
	def play(self, node):
		if debug:print 'VideoChannel.play('+`self`+','+`node`+')'
		self.play_0(node)
		if not self._is_shown or not node.IsPlayable() \
		   or self.syncplay:
			self.play_1()
			return
		if not self.nopop:
			self.window.pop()
		if self._is_shown:
			self.do_play(node)
		self.armdone()

	def do_play(self, node):
		if debug:print 'VideoChannel.do_play('+`self`+','+`node`+')'
		if node not in self._builders.keys():
			print 'node not armed'
			self.playdone(0)
			return

		self.play_loop = self.getloop(node)

		# get duration in secs (float)
		duration = MMAttrdefs.getattr(node, 'duration')
		if duration > 0:
			self._scheduler.enter(duration, 0, self._stopplay, ())
	
		if not self.armed_display.is_closed():
			self.armed_display.render()
		if self.played_display:
			self.played.display.close()
		self.played_display = self.armed_display
		self.armed_display = None
		self.played_display.render()

		self._playBuilder=self._builders[node]
		self._playBuilder.SetPosition(0)
		if self.window and self.window.IsWindow():
			self._playBuilder.SetWindow(self.window,WM_GRPAPHNOTIFY)
			self.window.HookMessage(self.OnGraphNotify,WM_GRPAPHNOTIFY)
		self._playBuilder.Run()
		self._playBuilder.SetVisible(1)

		if self.play_loop == 0 and duration == 0:
			self.playdone(0)

	# scheduler callback, at end of duration
	def _stopplay(self):
		self.__qid = None
		if self._playBuilder:
			self._playBuilder.Stop()
			self._playBuilder.SetVisible(0)
			self._playBuilder=None
		self.playdone(0)

	# part of stop sequence
	def stopplay(self, node):
		if self.__qid is not None:
			self._scheduler.cancel(self.__qid)
			self.__qid = None
		if self._playBuilder:
			self._playBuilder.Stop()
			self._playBuilder.SetVisible(0)
			self._playBuilder=None
		ChannelWindow.stopplay(self, node)

	# toggles between pause and run
	def setpaused(self, paused):
		self._paused = paused
		if self._playBuilder:
			if self._paused:
				self._playBuilder.Pause()
			else:
				self._playBuilder.Run()

	# capture end of media
	def OnGraphNotify(self,params):
		if self._playBuilder:
			duration=self._playBuilder.GetDuration()
			t_msec=self._playBuilder.GetPosition()
			if t_msec>=duration:self.OnMediaEnd()

	def OnMediaEnd(self):
		if debug: print 'VideoChannel: OnMediaEnd',`self`
		if not self._playBuilder:
			return		
		if self.play_loop:
			self.play_loop = self.play_loop - 1
			if self.play_loop: # more loops
				self._playBuilder.SetPosition(0)
				self._playBuilder.Run()
				return
			# no more loops
			self._playBuilder.Stop()
			self._playBuilder.SetVisible(0)
			self._playBuilder=None
			# if event wait scheduler
			if self.__qid is not None:return
			# else end
			self.playdone(0)
			return
		# play_loop is 0 so play until duration if set
		self._playBuilder.SetPosition(0)
		self._playBuilder.Run()


	def defanchor(self, node, anchor, cb):
		import windowinterface
		windowinterface.showmessage('The whole window will be hot.')
		cb((anchor[0], anchor[1], [0,0,1,1]))

	def islocal(self,url):
		utype, url = MMurl.splittype(url)
		host, url = MMurl.splithost(url)
		return not utype and not host

	def toabs(self,url):
		if not self.islocal(url):
			return url
		filename=MMurl.url2pathname(MMurl.splithost(url)[1])
		if os.path.isfile(filename):
			if not os.path.isabs(filename):
				filename=os.path.join(os.getcwd(),filename)
				filename=ntpath.normpath(filename)	
		return filename

