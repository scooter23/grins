__version__ = "$Id$"

#
# WIN32 Sound Channel
#

# the core
import Channel

# common component
import MediaChannel
import RealChannel

# node attributes
import MMAttrdefs

debug=0

class SoundChannel(Channel.ChannelAsync):
	node_attrs = Channel.ChannelAsync.node_attrs + [
		'duration', 'clipbegin', 'clipend',
		'project_audiotype', 'project_targets',
		'project_perfect', 'project_mobile']

	def __init__(self, name, attrdict, scheduler, ui):
		self.__mc = None
		self.__rc = None
		Channel.ChannelAsync.__init__(self, name, attrdict, scheduler, ui)

	def __repr__(self):
		return '<SoundChannel instance, name=' + `self._name` + '>'

	def do_show(self, pchan):
		if not Channel.ChannelAsync.do_show(self, pchan):
			return 0
		return 1

	def do_hide(self):
		self.__stopplayer()
		Channel.ChannelAsync.do_hide(self)

	def do_arm(self, node, same=0):
		self.__ready = 0
		node.__type = ''
		self.__maxsoundlevel = 1.0
		if node.type != 'ext':
			self.errormsg(node, 'Node must be external')
			return 1
		url = self.getfileurl(node)
		if not url:
			self.errormsg(node, 'No URL set on node')
			return 1
		import MMmimetypes, string
		mtype = MMmimetypes.guess_type(url)[0]			
		if mtype and string.find(mtype, 'real') >= 0:
			node.__type = 'real'
			if self.__rc is None:
				try:
					self.__rc = RealChannel.RealChannel(self)
				except RealChannel.error, msg:
					# can't do RealAudio
##					self.__rc = 0 # don't try again
					self.errormsg(node, msg)
			if self.__rc:
				if self.__rc.prepare_player(node):
					self.__ready = 1
		else:
			if self.needsSoundLevelCaps(node):
				self.__maxsoundlevel = self.getMaxSoundLevel(node)
				if mtype and string.find(mtype, 'x-wav')>=0:
					if not self.__mc:
						self.__mc = MediaChannel.DSPlayer(self)
					lc = self._attrdict.GetLayoutChannel()
					soundlevel = lc.get('soundLevel', 1.0)
					self.__mc.setsoundlevel(soundlevel, self.__maxsoundlevel)
			if not self.__mc:
				self.__mc = MediaChannel.MediaChannel(self)
			try:
				self.__mc.prepare_player(node)
				self.__ready = 1
			except MediaChannel.error, msg:
				self.errormsg(node, msg)
		return 1

	def do_play(self, node):
		self.__type = node.__type
		start_time = node.get_start_time()
		if not self.__ready:
			# arming failed, so don't even try playing
			self.playdone(0, start_time)
			return
		if node.__type == 'real':
			if not self.__rc:
				self.playdone(0, start_time)
			elif not self.__rc.playit(node, start_time=start_time):
				import windowinterface, MMAttrdefs
				name = MMAttrdefs.getattr(node, 'name')
				if not name:
					name = '<unnamed node>'
				chtype = self.__class__.__name__[:-7] # minus "Channel"
				windowinterface.showmessage('No playback support for %s on this system\n'
							    'node %s on channel %s' % (chtype, name, self._name), mtype = 'warning')
				self.playdone(0, start_time)
		elif not self.__mc.playit(node, start_time=start_time):
			self.errormsg(node,'Can not play')
			self.playdone(0, start_time)

	def playstop(self):
		self.__stopplayer()
		self.playdone(1)		
				
	def __stopplayer(self):
		if self.__mc:
			self.__mc.stopit()
			self.__mc.destroy()
			self.__mc = None
		if self.__rc:
			self.__rc.stopit()
			self.__rc.destroy()
			self.__rc = None

	def endoftime(self):
		self.__stopplayer()
		self.playdone(0)

	# toggles between pause and run
	def setpaused(self, paused):
		if self.__rc:
			self.__rc.pauseit(paused)
		if self.__mc is not None:
			self.__mc.pauseit(paused)
		Channel.ChannelAsync.setpaused(self, paused)


	def stopplay(self, node):
		self.__stopplayer()
		Channel.ChannelAsync.stopplay(self, node)

	def needsSoundLevelCaps(self, node):
		d = node.GetContext()._soundlevelinfo
		maxval = d.get('max', 1.0)
		minval = d.get('min', 1.0)
		hasanim = d.get('anim', 0)
		return maxval!=1.0 or minval!=1.0 or hasanim

	def getMaxSoundLevel(self, node):
		return node.GetContext()._soundlevelinfo.get('max', 1)

	def updatesoundlevel(self, val):
		if self.__mc:
			self.__mc.updatesoundlevel(val, self.__maxsoundlevel)
		if self.__rc:
			pass


		
