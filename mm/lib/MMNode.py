__version__ = "$Id$"

import MMAttrdefs
from MMTypes import *
from MMExc import *
from SR import *
from AnchorDefs import *
import Duration
from Hlinks import Hlinks
import MMurl
import settings
from HDTL import HD, TL
import string

class MMNodeContext:
	def __init__(self, nodeclass):
		self.nodeclass = nodeclass
		self.uidmap = {}
		self.channelnames = []
		self.channels = []
		self.channeldict = {}
		self.hyperlinks = Hlinks()
		self.layouts = {}
		self.usergroups = {}
		self.baseurl = None
		self.nextuid = 1
		self.editmgr = None
		self.armedmode = None
		self.getchannelbynode = None
		self.title = None
		self.attributes = {}	# unrecognized SMIL meta values
		self.__registers = []

	def __repr__(self):
		return '<MMNodeContext instance, channelnames=' \
			+ `self.channelnames` + '>'

	def settitle(self, title):
		self.title = title

	def gettitle(self):
		return self.title

	def setbaseurl(self, baseurl):
		if baseurl:
			# delete everything after last slash
			i = string.rfind(baseurl, '/')
			if i >= 0:
				baseurl = baseurl[:i+1]
		self.baseurl = baseurl

	def findurl(self, url):
		"Locate a file given by url-style filename."
		if self.baseurl:
			url = MMurl.basejoin(self.baseurl, url)
		return url

	def relativeurl(self, url):
		"Convert a URL to something that is relative to baseurl."
		url = MMurl.canonURL(url)
		baseurl = MMurl.canonURL(self.baseurl or '')
		if url[:len(baseurl)] == baseurl:
			url = url[len(baseurl):]
		return url

	def newnode(self, type):
		return self.newnodeuid(type, self.newuid())

	def newnodeuid(self, type, uid):
		node = self.nodeclass(type, self, uid)
		self.knownode(uid, node)
		return node

	def newuid(self):
		while 1:
			uid = `self.nextuid`
			self.nextuid = self.nextuid + 1
			if not self.uidmap.has_key(uid):
				return uid

	def mapuid(self, uid):
		if not self.uidmap.has_key(uid):
			raise NoSuchUIDError, 'in mapuid()'
		return self.uidmap[uid]

	def knownode(self, uid, node):
		if self.uidmap.has_key(uid):
			raise DuplicateUIDError, 'in knownode()'
		self.uidmap[uid] = node

	def forgetnode(self, uid):
		del self.uidmap[uid]

	#
	# Channel administration
	#
	def compatchannels(self, url = None, chtype = None):
		# return a list of channels compatible with the given URL
		if url:
			# ignore chtype if url is set
			import mimetypes, ChannelMime
			mtype = mimetypes.guess_type(url)[0]
			if not mtype:
				return []
			if mtype == 'application/vnd.rn-realmedia':
				# for RealMedia look inside the file
				import realsupport
				info = realsupport.getinfo(self.findurl(url))
				if info and not info.has_key('width'):
					mtype = 'audio/vnd.rn-realaudio'
				else:
					mtype = 'video/vnd.rn-realvideo'
			chtypes = ChannelMime.MimeChannel.get(mtype, [])
		elif chtype:
			chtypes = [chtype]
		else:
			# no URL and no channel type given
			return []
		chlist = []
		for ch in self.channels:
			if ch['type'] in chtypes:
				chlist.append(ch.name)
		chlist.sort()
		return chlist

	def addchannels(self, list):
		for name, dict in list:
			c = MMChannel(self, name)
##			for key, val in dict.items():
##				c[key] = val
			c.attrdict = dict # we know the internals...
			self.channeldict[name] = c
			self.channelnames.append(name)
			self.channels.append(c)

	def getchannel(self, name):
		try:
			return self.channeldict[name]
		except KeyError:
			return None

	def addchannel(self, name, i, type):
		import ChannelMap
		if name in self.channelnames:
			raise CheckError, 'addchannel: existing name'
		if not 0 <= i <= len(self.channelnames):
			raise CheckError, 'addchannel: invalid position'
		c = MMChannel(self, name)
		c['type'] = type
		if ChannelMap.isvisiblechannel(type):
			if not settings.get('cmif'):
				# some defaults for SMIL mode differ from CMIF defaults
				from windowinterface import UNIT_PXL
				c['units'] = UNIT_PXL
				c['transparent'] = 1
				c['center'] = 0
				c['drawbox'] = 0
				c['scale'] = 1
			if settings.get('compatibility') == settings.G2:
				# specialized settings for G2-compatibility
				from windowinterface import UNIT_PXL
				c['units'] = UNIT_PXL
				c['transparent'] = -1
				c['center'] = 0
				c['drawbox'] = 0
				if type in ('image', 'video'):
					c['scale'] = 1
				if type in ('text', 'RealText'):
					c['bgcolor'] = 255,255,255
				else:
					c['bgcolor'] = 0,0,0
		self.channeldict[name] = c
		self.channelnames.insert(i, name)
		self.channels.insert(i, c)

	def copychannel(self, name, i, orig):
		if name in self.channelnames:
			raise CheckError, 'copychannel: existing name'
		if not 0 <= i <= len(self.channelnames):
			raise CheckError, 'copychannel: invalid position'
		if not orig in self.channelnames:
			raise CheckError, 'copychannel: non-existing original'
		c = MMChannel(self, name)
		orig_i = self.channelnames.index(orig)
		orig_ch = self.channels[orig_i]
		for attr in orig_ch.keys():
		    c[attr] = eval(repr(orig_ch[attr]))
		self.channeldict[name] = c
		self.channelnames.insert(i, name)
		self.channels.insert(i, c)

	def movechannel(self, name, i):
		if not name in self.channelnames:
			raise CheckError, 'movechannel: non-existing name'
		if not 0 <= i <= len(self.channelnames):
			raise CheckError, 'movechannel: invalid position'
		old_i = self.channelnames.index(name)
		if old_i == i:
		    return
		self.channels.insert(i, self.channels[old_i])
		self.channelnames.insert(i, name)
		if old_i < i:
		    del self.channelnames[old_i]
		    del self.channels[old_i]
		else:
		    del self.channelnames[old_i+1]
		    del self.channels[old_i+1]

	def delchannel(self, name):
		if name not in self.channelnames:
			raise CheckError, 'delchannel: non-existing name'
		i = self.channelnames.index(name)
		c = self.channels[i]
		for channels in self.layouts.values():
			for j in range(len(channels)):
				if c is channels[j]:
					del channels[j]
					break
		del self.channels[i]
		del self.channelnames[i]
		del self.channeldict[name]
		c._destroy()

	def setchannelname(self, oldname, newname):
		if newname == oldname: return # No change
		if newname in self.channelnames:
			raise CheckError, 'setchannelname: duplicate name'
		i = self.channelnames.index(oldname)
		c = self.channeldict[oldname]
		self.channeldict[newname] = c
		c._setname(newname)
		self.channelnames[i] = newname
		del self.channeldict[oldname]
		# Patch references to this channel in nodes
		for uid in self.uidmap.keys():
			n = self.uidmap[uid]
			if n.GetRawAttrDef('channel', None) == oldname:
				n.SetAttr('channel', newname)
		# Patch references to this channel in other channels
		for ch in self.channels:
			if ch.get('base_window') == oldname:
				ch['base_window'] = newname

	def registergetchannelbynode(self, func):
		self.getchannelbynode = func
	#
	# Hyperlink administration
	#
	def addhyperlinks(self, list):
		self.hyperlinks.addlinks(list)

	def addhyperlink(self, link):
		self.hyperlinks.addlink(link)

	def sanitize_hyperlinks(self, roots):
		"""Remove all hyperlinks that aren't contained in the given trees
		   (note that the argument is a *list* of root nodes)"""
		self._roots = roots
		badlinks = self.hyperlinks.selectlinks(self._isbadlink)
		del self._roots
		for link in badlinks:
			self.hyperlinks.dellink(link)

	def get_hyperlinks(self, root):
		"""Return all hyperlinks pertaining to the given tree
		   (note that the argument is a *single* root node)"""
		self._roots = [root]
		links = self.hyperlinks.selectlinks(self._isgoodlink)
		del self._roots
		return links

	#
	# Layout administration
	#
	def addlayouts(self, list):
		for name, channels in list:
			chans = []
			for channame in channels:
				chan = self.channeldict.get(channame)
				if chan is None:
					print 'channel %s in layout %s does not exist' % (channame, name)
				else:
					chans.append(chan)
			self.layouts[name] = chans

	def addlayout(self, name):
		if self.layouts.has_key(name):
			raise CheckError, 'addlayout: existing name'
		self.layouts[name] = []

	def dellayout(self, name):
		if not self.layouts.has_key(name):
			raise CheckError, 'dellayout: non-existing name'
		del self.layouts[name]

	def setlayoutname(self, oldname, newname):
		if newname == oldname: return # No change
		if self.layouts.has_key(newname):
			raise CheckError, 'setlayoutname: duplicate name'
		layout = self.layouts.get(oldname)
		if layout is None:
			raise CheckError, 'setlayoutname: unknown layout'
		del self.layouts[oldname]
		self.layouts[newname] = layout
		# Patch references to this layout in nodes
		for uid in self.uidmap.keys():
			n = self.uidmap[uid]
			if n.GetRawAttrDef('layout', None) == oldname:
				n.SetAttr('layout', newname)

	def addlayoutchannel(self, name, channel):
		channels = self.layouts.get(name)
		if channels is None:
			raise CheckError, 'addlayoutchannel: non-existing name'
		for ch in channels:
			if ch is channel:
				raise CheckError, 'addlayoutchannel: channel already in layout'
		channels.append(channel)

	def dellayoutchannel(self, name, channel):
		channels = self.layouts.get(name)
		if channels is None:
			raise CheckError, 'dellayoutchannel: non-existing name'
		for i in range(len(channels)):
			if channels[i] is channel:
				del channels[i]
				return
		raise CheckError, 'dellayoutchannel: channel not in layout'

	#
	# User group administration
	#
	def addusergroups(self, list):
		for name, value in list:
			title, rendered, allowed = value
			rendered = ['NOT RENDERED', 'RENDERED'][rendered]
			allowed = ['not allowed', 'allowed'][allowed]
			self.usergroups[name] = title, rendered, allowed

	def addusergroup(self, name, value):
		if self.usergroups.has_key(name):
			raise CheckError, 'addusergroup: existing name'
		self.usergroups[name] = value

	def delusergroup(self, name):
		if not self.usergroups.has_key(name):
			raise CheckError, 'delusergroup: non-existing name'
		del self.usergroups[name]

	def setusergroupname(self, oldname, newname):
		if newname == oldname: return # No change
		if self.usergroups.has_key(newname):
			raise CheckError, 'setusergroup: existing name'
		if not self.usergroups.has_key(oldname):
			raise CheckError, 'setusergroup: non-existing name'
		self.usergroups[newname] = self.usergroups[oldname]
		del self.usergroups[oldname]
		# Patch references to this usergroup in nodes
		for uid in self.uidmap.keys():
			n = self.uidmap[uid]
			if n.GetRawAttrDef('usergroup', None) == oldname:
				n.SetAttr('usergroup', newname)

	# Internal: predicates to select nodes pertaining to self._roots
	def _isbadlink(self, link):
		return not self._isgoodlink(link)

	def _isgoodlink(self, link):
		a1, a2, dir, ltype = link
		if type(a1) is type(()):
			uid1, aid1 = a1
			srcok = (self.uidmap.has_key(uid1) and
				 self.uidmap[uid1].GetRoot() in self._roots)
		else:
			srcok = 0
		if type(a2) is type(()):
			uid2, aid2 = a2
			dstok = (('/' in uid2) or
				 (self.uidmap.has_key(uid2) and
				  self.uidmap[uid2].GetRoot() in self._roots))
		else:
			dstok = 1
		return (srcok and dstok)

	#
	# Editmanager
	#
	def seteditmgr(self, editmgr):
		self.editmgr = editmgr
		for x in self.__registers:
			editmgr.registerfirst(x)
		self.__registers = []

	def geteditmgr(self):
		return self.editmgr

	def register(self, x):
		if self.editmgr:
			self.editmgr.registerfirst(x)
		else:
			self.__registers.append(x)

class MMChannel:
	def __init__(self, context, name):
		self.context = context
		self.name = name
		self.attrdict = {}

	def __repr__(self):
		return '<MMChannel instance, name=' + `self.name` + '>'

	def _setname(self, name): # Only called from context.setchannelname()
		self.name = name

	def _destroy(self):
		self.context = None

	def stillvalid(self):
		return self.context is not None

	def _getdict(self): # Only called from MMWrite.fixroot()
		return self.attrdict

	#
	# Emulate the dictionary interface
	#
	def __getitem__(self, key):
		if self.attrdict.has_key(key):
			return self.attrdict[key]
		else:
			# special case for background color
			if key == 'bgcolor' and \
			   self.attrdict.has_key('base_window') and \
			   self.attrdict.get('transparent', 0) <= 0:
				pname = self.attrdict['base_window']
				pchan = self.context.channeldict[pname]
				return pchan['bgcolor']
			raise KeyError, key

	def __setitem__(self, key, value):
		self.attrdict[key] = value

	def __delitem__(self, key):
		del self.attrdict[key]

	def has_key(self, key):
		return self.attrdict.has_key(key)

	def keys(self):
		return self.attrdict.keys()

	def items(self):
		return self.attrdict.items()

	def get(self, key, default = None):
		if self.attrdict.has_key(key):
			return self.attrdict[key]
		if key == 'bgcolor' and \
		   self.attrdict.has_key('base_window') and \
		   self.attrdict.get('transparent', 0) <= 0:
			pname = self.attrdict['base_window']
			pchan = self.context.channeldict.get(pname)
			if pchan:
				return pchan.get('bgcolor', default)
		return default

# The Sync Arc class
#
# XXX This isn't used yet
#
class MMSyncArc:

	def __init__(self, context):
		self.context = context
		self.src = None
		self.dst = None
		self.delay = 0.0

	def __repr__(self):
		return '<MMSyncArc instance, from ' + \
			  `self.src` + ' to ' + `self.dst` + \
			  ', delay ' + `self.delay` + '>'

	def setsrc(self, srcnode, srcend):
		self.src = (srcnode, srcend)

	def setdst(self, dstnode, dstend):
		self.dst = (dstnode, dstend)

	def setdelay(self, delay):
		self.delay = delay


class MMNode_body:
	"""Helper for looping nodes"""
	helpertype = "looping"
	
	def __init__(self, parent):
		self.parent = parent

	def __repr__(self):
		return "<%s body of %s>"%(self.helpertype, self.parent.__repr__())

	def __getattr__(self, name):
		if name == 'attrcache':
			raise AttributeError, 'Not allowed'
		return getattr(self.parent, name)

	def GetUID(self):
		return '%s-%s-%d'%(self.parent.GetUID(), self.helpertype, id(self))

	def stoplooping(self):
		pass
	
class MMNode_pseudopar_body(MMNode_body):
	"""Helper for RealPix nodes with captions, common part"""

	def _is_realpix_with_captions(self):
		return 0
	
class MMNode_realpix_body(MMNode_pseudopar_body):
	"""Helper for RealPix nodes with captions, realpix part"""
	helpertype = "realpix"
	
class MMNode_caption_body(MMNode_pseudopar_body):
	"""Helper for RealPix nodes with captions, caption part"""
	helpertype = "caption"

	def GetAttrDict(self):
		raise 'Unimplemented'

	def GetRawAttr(self, name):
		if name == 'channel': name = 'captionchannel'
		return self.parent.GetRawAttr(name)

	def GetRawAttrDef(self, name, default):
		if name == 'channel': name = 'captionchannel'
		return self.parent.GetRawAttrDef(name, default)

	def GetAttr(self, name):
		if name == 'channel': name = 'captionchannel'
		return self.parent.GetAttr(name)

	def GetAttrDef(self, name, default):
		if name == 'channel': name = 'captionchannel'
		return self.parent.GetAttrDef(name, default)

	def GetInherAttr(self, name):
		if name == 'channel': name = 'captionchannel'
		return self.parent.GetInherAttr(name)

	def GetDefInherAttr(self, name):
		if name == 'channel': name = 'captionchannel'
		return self.parent.GetDefInherAttr(name)

	def GetInherAttrDef(self, name, default):
		if name == 'channel': name = 'captionchannel'
		return self.parent.GetInherAttrDef(name, default)
		
class MMNode:
	def __init__(self, type, context, uid):
		# ASSERT type in alltypes
		self.type = type
		self.context = context
		self.uid = uid
		self.attrdict = {}
		self.values = []
		self.willplay = None
		self.shouldplay = None
		self.canplay = None
		self.parent = None
		self.children = []
##		self.summaries = {}
		self.setgensr()
##		self.isloopnode = 0
##		self.isinfiniteloopnode = 0
		self.looping_body_self = None
		self.realpix_body = None
		self.caption_body = None
		self.curloopcount = 0
		self.infoicon = ''
		self.errormessage = None

	#
	# Return string representation of self
	#
	def __repr__(self):
		try:
			import MMAttrdefs
			name = MMAttrdefs.getattr(self, 'name')
		except:
			name = ''
		return '<MMNode instance, type=%s, uid=%s, name=%s>' % \
		       (`self.type`, `self.uid`, `name`)

	#
	# Private methods to build a tree
	#
	def _addchild(self, child):
		# ASSERT self.type in interiortypes
		child.parent = self
		self.children.append(child)

	def _addvalue(self, value):
		# ASSERT self.type = 'imm'
		self.values.append(value)

	def _setattr(self, name, value):
		# ASSERT not self.attrdict.has_key(name)
		self.attrdict[name] = value
		MMAttrdefs.flushcache(self)

	#
	# Public methods for read-only access
	#
	def GetType(self):
		return self.type

	def GetContext(self):
		return self.context

	def GetUID(self):
		return self.uid

	def MapUID(self, uid):
		return self.context.mapuid(uid)

	def GetParent(self):
		return self.parent

	def GetRoot(self):
		root = None
		x = self
		while x is not None:
			root = x
			x = x.parent
		return root

	def GetPath(self):
		path = []
		x = self
		while x is not None:
			path.append(x)
			x = x.parent
		path.reverse()
		return path

	def IsAncestorOf(self, x):
		while x is not None:
			if self is x: return 1
			x = x.parent
		return 0

	def CommonAncestor(self, x):
		p1 = self.GetPath()
		p2 = x.GetPath()
		n = min(len(p1), len(p2))
		i = 0
		while i < n and p1[i] == p2[i]: i = i+1
		if i == 0: return None
		else: return p1[i-1]

	def GetChildren(self):
		return self.children

	def GetChild(self, i):
		return self.children[i]

	def GetValues(self):
		return self.values

	def GetValue(self, i):
		return self.values[i]

	def GetAttrDict(self):
		return self.attrdict

	def GetRawAttr(self, name):
		if self.attrdict.has_key(name):
			return self.attrdict[name]
		raise NoSuchAttrError, 'in GetRawAttr()'

	def GetRawAttrDef(self, name, default):
		return self.attrdict.get(name, default)

	def GetAttr(self, name):
		if self.attrdict.has_key(name):
			return self.attrdict[name]
		raise NoSuchAttrError, 'in GetAttr'

	def GetAttrDef(self, name, default):
		return self.attrdict.get(name, default)

	def GetInherAttr(self, name):
		x = self
		while x is not None:
			if x.attrdict and x.attrdict.has_key(name):
				return x.attrdict[name]
			x = x.parent
		raise NoSuchAttrError, 'in GetInherAttr()'

	def GetDefInherAttr(self, name):
		x = self.parent
		while x is not None:
			if x.attrdict and x.attrdict.has_key(name):
				return x.attrdict[name]
			x = x.parent
		raise NoSuchAttrError, 'in GetInherDefAttr()'

	def GetInherAttrDef(self, name, default):
##		try:
##			return self.GetInherAttr(name)
##		except NoSuchAttrError:
##			return default
		x = self
		while x is not None:
			if x.attrdict and x.attrdict.has_key(name):
				return x.attrdict[name]
			x = x.parent
		return default

##	def GetSummary(self, name):
##		if not self.summaries.has_key(name):
##			self.summaries[name] = self._summarize(name)
##		return self.summaries[name]

	def Dump(self):
		print '*** Dump of', self.type, 'node', self, '***'
		attrnames = self.attrdict.keys()
		attrnames.sort()
		for name in attrnames:
			print 'Attr', name + ':', `self.attrdict[name]`
##		summnames = self.summaries.keys()
##		if summnames:
##			summnames.sort()
##			print 'Has summaries for attrs:',
##			for name in summnames:
##				print name,
##			print
		if self.type == 'imm' or self.values:
			print 'Values:',
			for value in self.values: print value,
			print
		if self.type in interiortypes or self.children:
			print 'Children:',
			for child in self.children: print child.GetType(),
			print

	#
	# Channel management
	#
	def GetChannel(self, attrname='channel'):
		cname = self.GetInherAttrDef(attrname, None)
		if not cname:		# cname == '' or cname == None
			return None
		return self.context.channeldict.get(cname)

	def GetChannelName(self):
		c = self.GetChannel()
		if c: return c.name
		else: return 'undefined'

	def GetChannelType(self):
		c = self.GetChannel()
		if c and c.has_key('type'):
			return c['type']
		else:
			return ''

	def SetChannel(self, c):
		if c is None:
			try:
				self.DelAttr('channel')
			except NoSuchAttrError:
				pass
		else:
			self.SetAttr('channel', c.name)

	#
	# GetAllChannels - Get a list of all channels used in a tree.
	# If there is overlap between parnode children the node in error
	# is returned.
	def GetAllChannels(self):
		if self.type in bagtypes:
			return [], None
		if self.type in leaftypes:
			list = [MMAttrdefs.getattr(self, 'channel')]
			captionchannel = MMAttrdefs.getattr(self, 'captionchannel')
			if captionchannel and captionchannel != 'undefined':
				list.append(captionchannel)
			return list, None
		errnode = None
		overlap = []
		list = []
		for ch in self.children:
			chlist, cherrnode = ch.GetAllChannels()
			if cherrnode:
				errnode = cherrnode
			list, choverlap = MergeLists(list, chlist)
			if choverlap:
				overlap = overlap + choverlap
		if overlap and self.type == 'par':
			errnode = (self, overlap)
		return list, errnode

	#
	# Make a "deep copy" of a subtree
	#
	def DeepCopy(self):
		uidremap = {}
		copy = self._deepcopy(uidremap, self.context)
		copy._fixuidrefs(uidremap)
		_copyoutgoinghyperlinks(self.context.hyperlinks, uidremap)
		return copy
	#
	# Copy a subtree (deeply) into a new context
	#
	def CopyIntoContext(self, context):
		uidremap = {}
		copy = self._deepcopy(uidremap, context)
		copy._fixuidrefs(uidremap)
		_copyinternalhyperlinks(self.context.hyperlinks,
					copy.context.hyperlinks, uidremap)
		return copy
	#
	# Private methods for DeepCopy
	#
	def _deepcopy(self, uidremap, context):
		nodeclass = context.nodeclass
		context.nodeclass = self.__class__
		copy = context.newnode(self.type)
		context.nodeclass = nodeclass
		uidremap[self.uid] = copy.uid
		copy.attrdict = _valuedeepcopy(self.attrdict)
		copy.values = _valuedeepcopy(self.values)
		children = self.children
		if self.type == 'ext' and self.GetChannelType() == 'RealPix':
			if not hasattr(self, 'slideshow'):
				print 'MMNode._deepcopy: creating SlideShow'
				import realnode
				self.slideshow = realnode.SlideShow(self)
			self.slideshow.copy(copy)
			if copy.attrdict.has_key('file'):
				del copy.attrdict['file']
			# don't copy children since node collapsed
			children = []
		for child in children:
			copy._addchild(child._deepcopy(uidremap, context))
		return copy

	def _fixuidrefs(self, uidremap):
		# XXX Are there any other attributes that reference uids?
		self._fixsyncarcs(uidremap)
		for child in self.children:
			child._fixuidrefs(uidremap)

	def _fixsyncarcs(self, uidremap):
		# XXX Exception-wise, this function knows about the
		# semantics and syntax of an attribute...
		try:
			arcs = self.GetRawAttr('synctolist')
		except NoSuchAttrError:
			return
		if not arcs:
			self.DelAttr('synctolist')
			return
		newarcs = []
		for xuid, xside, delay, yside in arcs:
			if uidremap.has_key(xuid):
				xuid = uidremap[xuid]
			if yside == HD:
				if self.parent.type == 'seq' and xside == TL:
					prev = None
					for n in self.parent.children:
						if n is self:
							break
						prev = n
					if prev is not None and prev.uid == xuid:
						self.SetAttr('begin', delay)
						continue
				elif xside == HD and self.parent.uid == xuid:
					self.SetAttr('begin', delay)
					continue
			newarcs.append((xuid, xside, delay, yside))
		if newarcs <> arcs:
			if not newarcs:
				self.DelAttr('synctolist')
			else:
				self.SetAttr('synctolist', newarcs)

	#
	# Public methods for modifying a tree
	#
	def SetType(self, type):
		if type not in alltypes:
			raise CheckError, 'SetType() bad type'
		if type == self.type:
			return
		if self.type in interiortypes and type in interiortypes:
			self.type = type
			self.setgensr()
			return
		if self.children <> []: # TEMP! or self.values <> []:
			raise CheckError, 'SetType() on non-empty node'
		self.type = type
		self.setgensr()

	def SetValues(self, values):
		if self.type <> 'imm':
			raise CheckError, 'SetValues() bad node type'
		self.values = values

	def SetAttr(self, name, value):
		self.attrdict[name] = value
		MMAttrdefs.flushcache(self)
##		self._updsummaries([name])

	def DelAttr(self, name):
		if not self.attrdict.has_key(name):
			raise NoSuchAttrError, 'in DelAttr()'
		del self.attrdict[name]
		MMAttrdefs.flushcache(self)
##		self._updsummaries([name])

	def Destroy(self):
		if self.parent is not None:
			raise CheckError, 'Destroy() non-root node'

		if hasattr(self, 'slideshow'):
			self.slideshow.destroy()
			del self.slideshow
		# delete hyperlinks referring to anchors here
		alist = MMAttrdefs.getattr(self, 'anchorlist')
		hlinks = self.context.hyperlinks
		for a in alist:
			aid = (self.uid, a[A_ID])
			for link in hlinks.findalllinks(aid, None):
				hlinks.dellink(link)

		self.context.forgetnode(self.uid)
		for child in self.children:
			child.parent = None
			child.Destroy()
		self.type = None
		self.context = None
		self.uid = None
		self.attrdict = None
		self.parent = None
		self.children = None
		self.values = None
		self.sync_from = None
		self.sync_to = None
		self.wtd_children = None
##		self.summaries = None
		self.looping_body_self = None
		self.realpix_body = None
		self.caption_body = None

	def Extract(self):
		if self.parent is None: raise CheckError, 'Extract() root node'
		parent = self.parent
		self.parent = None
		parent.children.remove(self)
		name = MMAttrdefs.getattr(self, 'name')
		if name and MMAttrdefs.getattr(parent, 'terminator') == name:
			parent.DelAttr('terminator')
##		parent._fixsummaries(self.summaries)

	def AddToTree(self, parent, i):
		if self.parent is not None:
			raise CheckError, 'AddToTree() non-root node'
		if self.context is not parent.context:
			# XXX Decide how to handle this later
			raise CheckError, 'AddToTree() requires same context'
		if i == -1:
			parent.children.append(self)
		else:
			parent.children.insert(i, self)
		self.parent = parent
##		parent._fixsummaries(self.summaries)
##		parent._rmsummaries(self.summaries.keys())

	#
	# Methods for mini-document management
	#
	# Check whether a node is the top of a mini-document
	def IsMiniDocument(self):
		if self.type in bagtypes:
			return 0
		parent = self.parent
		return parent is None or parent.type in bagtypes

	# Find the first mini-document in a tree
	def FirstMiniDocument(self):
		if self.IsMiniDocument():
			return self
		for child in self.children:
			mini = child.FirstMiniDocument()
			if mini is not None:
				return mini
		return None

	# Find the last mini-document in a tree
	def LastMiniDocument(self):
		if self.IsMiniDocument():
			return self
		res = None
		for child in self.children:
			mini = child.LastMiniDocument()
			if mini is not None:
				res = mini
		return res

	# Find the next mini-document in a tree after the given one
	# Return None if this is the last one
	def NextMiniDocument(self):
		node = self
		while 1:
			parent = node.parent
			if parent is None:
				break
			siblings = parent.children
			index = siblings.index(node) # Cannot fail
			while index+1 < len(siblings):
				index = index+1
				mini = siblings[index].FirstMiniDocument()
				if mini is not None:
					return mini
			node = parent
		return None

	# Find the previous mini-document in a tree after the given one
	# Return None if this is the first one
	def PrevMiniDocument(self):
		node = self
		while 1:
			parent = node.parent
			if parent is None:
				break
			siblings = parent.children
			index = siblings.index(node) # Cannot fail
			while index > 0:
				index = index-1
				mini = siblings[index].LastMiniDocument()
				if mini is not None:
					return mini
			node = parent
		return None

	# Find the root of a node's mini-document
	def FindMiniDocument(self):
		node = self
		parent = node.parent
		while parent is not None and parent.type not in bagtypes:
			node = parent
			parent = node.parent
		return node

	# Find the nearest bag given a minidocument
	def FindMiniBag(self):
		bag = self.parent
		if bag is not None and bag.type not in bagtypes:
			raise CheckError, 'FindMiniBag: minidoc not rooted in a choice node!'
		return bag

##	#
##	# Private methods for summary management
##	#
##	def _rmsummaries(self, keep):
##		x = self
##		while x is not None:
##			changed = 0
##			for key in x.summaries.keys():
##				if key not in keep:
##					del x.summaries[key]
##					changed = 1
##			if not changed:
##				break
##			x = x.parent

##	def _fixsummaries(self, summaries):
##		tofix = summaries.keys()
##		for key in tofix[:]:
##			if summaries[key] == []:
##				tofix.remove(key)
##		self._updsummaries(tofix)

##	def _updsummaries(self, tofix):
##		x = self
##		while x is not None and tofix:
##			for key in tofix[:]:
##				if not x.summaries.has_key(key):
##					tofix.remove(key)
##				else:
##					s = x._summarize(key)
##					if s == x.summaries[key]:
##						tofix.remove(key)
##					else:
##						x.summaries[key] = s
##			x = x.parent

##	def _summarize(self, name):
##		try:
##			summary = [self.GetAttr(name)]
##		except NoSuchAttrError:
##			summary = []
##		for child in self.children:
##			list = child.GetSummary(name)
##			for item in list:
##				if item not in summary:
##					summary.append(item)
##		summary.sort()
##		return summary

	#
	# Set the correct method for generating scheduler records.
	def setgensr(self):
		type = self.type
		if type in ('imm', 'ext'):
			self.gensr = self.gensr_leaf
		elif type == 'bag':
			self.gensr = self.gensr_bag
		elif type == 'alt':
			self.gensr = self.gensr_alt
		elif type in ('seq', 'par'):
			self.gensr = self.gensr_interior
		else:
			raise CheckError, 'MMNode: unknown type %s' % self.type
	#
	# Methods for building scheduler records. The interface is as follows:
	# - PruneTree() is called first, with a parameter that specifies the
	#   node to seek to (where we want to start playing). None means 'play
	#   everything'. PruneTree() sets the scope of all the next calls and
	#   initializes a few data structures in the tree nodes.
	# - Next GetArcList() should be called to obtain a list of all sync
	#   arcs with destinations in the current tree.
	# - Next FilterArcList() is called to filter out the sync arcs with
	#   a source outside the current tree.
	# - Finally gensr() is called in a loop to obtain a complete list of
	#   scheduler records. (There was a very good reason for the funny
	#   calling sequence of gensr(). I cannot seem to remember it at
	#   the moment, though).
	# - Call EndPruneTree() to clear the garbage.
	# Alternatively, call GenAllSR(), and then call EndPruneTree() to clear
	# the garbage.
	def PruneTree(self, seeknode):
		if seeknode is None or seeknode is self:
			self._FastPruneTree()
			return
		if seeknode is not None and not self.IsAncestorOf(seeknode):
			raise CheckError, 'Seeknode not in tree!'
		self.sync_from = ([],[])
		self.sync_to = ([],[])
		self.looping_body_self = None
		self.realpix_body = None
		self.caption_body = None
		if self.type in playabletypes:
			return
		self.wtd_children = []
		if self.type == 'seq':
			for c in self.children:
				if seeknode is not None and \
				   c.IsAncestorOf(seeknode):
					self.wtd_children.append(c)
					c.PruneTree(seeknode)
					seeknode = None
				elif seeknode is None:
					self.wtd_children.append(c)
					c._FastPruneTree()
		elif self.type == 'par':
			self.wtd_children = self.children[:]
			for c in self.children:
				if c.IsAncestorOf(seeknode):
					c.PruneTree(seeknode)
				else:
					c._FastPruneTree()
		else:
			raise CheckError, 'Cannot PruneTree() on nodes of this type %s' % self.type
	#
	# PruneTree - The fast lane. Just copy children->wtd_children and
	# create sync_from and sync_to.
	def _FastPruneTree(self):
		self.sync_from = ([],[])
		self.sync_to = ([],[])
		self.looping_body_self = None
		self.realpix_body = None
		self.caption_body = None
		self.wtd_children = self.children[:]
		for c in self.children:
			c._FastPruneTree()


	def EndPruneTree(self):
		pass
##		del self.sync_from
##		del self.sync_to
##		if self.type in ('seq', 'par'):
##			for c in self.wtd_children:
##				c.EndPruneTree()
##			del self.wtd_children

#	def gensr(self):
#		if self.type in ('imm', 'ext'):
#			return self.gensr_leaf(), []
#		elif self.type == 'bag':
#			return self.gensr_bag(), []
#		elif self.type == 'seq':
#			rv = self.gensr_seq(), self.wtd_children
#			return rv
#		elif self.type == 'par':
#			rv = self.gensr_par(), self.wtd_children
#			return rv
#		raise 'Cannot gensr() for nodes of this type', self.type

	#
	# Generate schedrecords for leaf nodes.
	# The looping parmeter is only for pseudo-par-nodes implementing RealPix with
	# captions.
	#
	def gensr_leaf(self, looping=0, overrideself=None):
		if overrideself:
			# overrideself is passed for the interior
			self = overrideself
		elif self._is_realpix_with_captions():
			self.realpix_body = MMNode_realpix_body(self)
			self.caption_body = MMNode_caption_body(self)
			return self.gensr_interior(looping)
		# Clean up realpix stuff: the node may have been a realpix node in the past
		self.realpix_body = None
		self.caption_body = None
		in0, in1 = self.sync_from
		out0, out1 = self.sync_to
		arg = self
		result = [([(SCHED, arg), (ARM_DONE, arg)] + in0,
			   [(PLAY, arg)] + out0)]
		if not Duration.get(self):
			# there is no (intrinsic or explicit) duration
			# PLAY_DONE comes immediately, so in effect
			# only wait for sync arcs
			result.append(
				([(PLAY_DONE, arg)] + in1,
				 [(SCHED_DONE,arg)] + out1))
			result.append(([(SCHED_STOP, arg)],
				       [(PLAY_STOP, arg)]))
		elif not MMAttrdefs.getattr(self, 'duration'):
			# there is an intrinsic but no explicit duration
			# keep active until told to stop
			# terminate on sync arcs
			for ev in in1:
				result.append(([ev], [(TERMINATE, self)]))
			result.append(
				([(PLAY_DONE, arg)],
				 [(SCHED_DONE,arg)] + out1))
			result.append(([(SCHED_STOP, arg)],
				       [(PLAY_STOP, arg)]))
		else:
			# there is an explicit duration
			# stop when done playing
			# terminate on sync arc
			for ev in in1:
				result.append(([ev], [(TERMINATE, self)]))
			result.append(
				([(PLAY_DONE, arg)],
				 [(SCHED_DONE,arg), (PLAY_STOP, arg)] + out1))
			result.append(([(SCHED_STOP, arg)], []))
		return result

	def gensr_empty(self):
		# generate SR list for empty interior node, taking
		# sync arcs to the end and duration into account
		in0, in1 = self.sync_from
		out0, out1 = self.sync_to
		duration = MMAttrdefs.getattr(self, 'duration')
		actions = out0[:]
		final = [(SCHED_DONE, self)] + out1
		srlist = [([(SCHED, self)] + in0, actions),
			  ([(SCHED_STOP, self)], []),
			  ([(TERMINATE, self)], [])]
		if in1:
			# wait for sync arcs
			srlist.append((in1, final))
		elif duration > 0:
			# wait for duration
			actions.append((SYNC, (duration, self)))
			srlist.append(([(SYNC_DONE, self)], final))
		else:
			# don't wait
			actions[len(actions):] = final
		return srlist

	# XXXX temporary hack to do at least something on ALT nodes
	def gensr_alt(self):
		if not self.wtd_children:
			return self.gensr_empty()
		selected_child = None
		selected_child = self.ChosenSwitchChild(self.wtd_children)
		if selected_child:
			self.wtd_children = [selected_child]
		else:
			self.wtd_children = []
			return self.gensr_empty()
		in0, in1 = self.sync_from
		out0, out1 = self.sync_to
		srlist = []
		duration = MMAttrdefs.getattr(self, 'duration')
		if duration > 0:
			# if duration set, we must trigger a timeout
			# and we must catch the timeout to terminate
			# the node
			out0 = out0 + [(SYNC, (duration, self))]
			srlist.append(([(SYNC_DONE, self)],
					[(TERMINATE, self)]))
		prereqs = [(SCHED, self)] + in0
		actions = out0[:]
		tlist = []
		actions.append((SCHED, selected_child))
		srlist.append((prereqs, actions))
		prereqs = [(SCHED_DONE, selected_child)]
		actions = [(SCHED_STOP, selected_child)]
		tlist.append((TERMINATE, selected_child))
		last_actions = actions
		actions = [(SCHED_DONE, self)]
		srlist.append((prereqs, actions))
		srlist.append(([(SCHED_STOP, self)],
			       last_actions + out1))
##		tlist.append((SCHED_DONE, self))
		srlist.append(([(TERMINATE, self)], tlist))
		for ev in in1:
			srlist.append(([ev], [(TERMINATE, self)]))
		return srlist + selected_child.gensr()

	def gensr_bag(self):
		if not self.wtd_children:
			return self.gensr_empty()
		in0, in1 = self.sync_from
		out0, out1 = self.sync_to
		result = [([(SCHED, self)] + in0,  [(BAG_START, self)] + out0),
			  ([(BAG_DONE, self)],     [(SCHED_DONE,self)] + out1),
			  ([(SCHED_STOP, self)],   [(BAG_STOP, self)]),
			  ([(TERMINATE, self)],    [])]
		for ev in in1:
			result.append(([ev], [(TERMINATE, self)]))
		return result

	#
	# There's a lot of common code for par and seq nodes.
	# We attempt to factor that out with a few helper routines.
	# All the helper routines accept at least two arguments
	# - the actions to be taken when the node is "starting"
	# - the actions to be taken when the node is "finished"
	# (or, colloquially, the outgoing head-syncarcs and the SCHED_DONE
	# event) and return 4 items:
	# - actions to be taken upon node starting (SCHED)
	# - actions to be taken upon SCHED_STOP
	# - actions to be taken upon TERMINATE or incoming tail-syncarcs
	# - a list of all (event, action) tuples to be generated
	#
	def gensr_interior(self, looping=0):
		#
		# If the node is empty there is very little to do.
		#
		if not self.wtd_children:
			return self.gensr_empty()
		is_realpix = 0
		if self.type == 'par':
			gensr_body = self.gensr_body_par
		elif self._is_realpix_with_captions():
			gensr_body = self.gensr_body_realpix
			is_realpix = 1
		else:
			gensr_body = self.gensr_body_seq

		#
		# Select the  generator for the outer code: either non-looping
		# or, for looping nodes, the first or subsequent times through
		# the loop.
		#
		loopcount = MMAttrdefs.getattr(self, 'loop')
		if loopcount == 1:
			gensr_envelope = self.gensr_envelope_nonloop
		elif looping == 0:
			# First time loop generation
			gensr_envelope = self.gensr_envelope_firstloop
		else:
			gensr_envelope = self.gensr_envelope_laterloop

		#
		# If the node has a duration we add a syncarc from head
		# to tail. This will terminate the node when needed.
		#
		in0, in1 = self.sync_from
		out0, out1 = self.sync_to
		
		if is_realpix:
			duration = 0
		else:
			duration = MMAttrdefs.getattr(self, 'duration')
		if duration > 0:
			# Implement duration by adding a syncarc from
			# head to tail.
			out0 = out0[:] + [(SYNC, (duration, self))]
			in1 = in1[:] + [(SYNC_DONE, self)]
		elif duration < 0:
			# Infinite duration, simulate with SYNC_DONE event
			# for which there is no SYNC action
			in1 = in1[:] + [(SYNC_DONE, self)]

		#
		# We are started when we get our SCHED and all our
		# incoming head-syncarcs.
		#
		sched_events = [(SCHED, self)] + in0
		#
		# Once we are started we should fire our outgoing head
		# syncarcs
		#
		sched_actions_arg = out0[:]
		#
		# When we're done we should signal SCHED_DONE to our parent
		# and fire our outgoing tail syncarcs.
		#
		scheddone_actions_arg = [(SCHED_DONE, self)]+out1
		#
		# And when the parent is really done with us we get a
		# SCHED_STOP
		#
		schedstop_events = [(SCHED_STOP, self)]

		#
		# And we also tell generating routines about all terminating
		# events.
		terminate_events_arg = in1

		sched_actions, schedstop_actions,  \
			       srlist = gensr_envelope(gensr_body, loopcount,
						       sched_actions_arg,
						       scheddone_actions_arg,
						       terminate_events_arg)
		if not looping:
			#
			# Tie our start-events to the envelope/body
			# start-actions
			#
			srlist.append( (sched_events, sched_actions) )
			#
			# Tie the envelope/body done events to our done actions
			#
			srlist.append( (schedstop_events, schedstop_actions) )
			#
			# And, for our incoming tail syncarcs and a
			# TERMINATE for ourselves we abort everything.
			#
##		if self._is_realpix_with_captions():	#DBG
##			print 'NODE', self # DBG
##			for i in srlist: print i #DBG
##			print 'NODE END' #DBG
		
		return srlist

	def gensr_envelope_nonloop(self, gensr_body, loopcount, sched_actions,
				   scheddone_actions, terminate_events):
		if loopcount != 1:
			raise 'Looping nonlooping node!'
		self.curloopcount = 0

		sched_actions, schedstop_actions, srlist = \
			       gensr_body(sched_actions, scheddone_actions,
					  terminate_events)
##		for event in in1+[(TERMINATE, self)]:
##			srlist.append( ([event], terminate_actions) )
		return sched_actions, schedstop_actions, srlist

	def gensr_envelope_firstloop(self, gensr_body, loopcount,
				     sched_actions, scheddone_actions,
				     terminate_events):
		srlist = []
		terminate_actions = []
		#
		# Remember the loopcount.
		#
		if loopcount == 0:
			self.curloopcount = -1
		else:
			self.curloopcount = loopcount

		#
		# We create a helper node, to differentiate between terminates
		# from the inside and the outside (needed for par nodes with
		# endsync, which can generate terminates internally that should
		# not stop the whole loop).
		#
		self.looping_body_self = MMNode_body(self)

		#
		# When we start we do our syncarc stuff, and also LOOPSTART
		# XXXX Note this is incorrect: we should check which of the
		# syncarcs refer to children
		#
		# XXXX We should also do our SCHED_DONE here if we are
		# looping indefinitely.
		#
		sched_actions.append( (LOOPSTART, self) )
		body_sched_actions = []
		body_scheddone_actions = [(SCHED_DONE, self.looping_body_self)]
		body_terminate_events = []

		body_sched_actions, body_schedstop_actions, srlist = \
				    gensr_body(body_sched_actions,
					       body_scheddone_actions,
					       body_terminate_events,
					       self.looping_body_self)

		# When the loop has started we start the body
		srlist.append( ([(LOOPSTART_DONE, self)], body_sched_actions) )

		# Terminating the body doesn't terminate the loop,
		# but the other way around it does
##		srlist.append( ([(TERMINATE, self.looping_body_self)],
##				body_terminate_actions) )
		terminate_actions = [(TERMINATE, self.looping_body_self)]

		# When the body is done we stop it, and we end/restart the loop
		srlist.append( ([(SCHED_DONE, self.looping_body_self)],
				[(LOOPEND, self),
				 (SCHED_STOP, self.looping_body_self)]) )
		srlist.append( ([(SCHED_STOP, self.looping_body_self)],
				body_schedstop_actions) )

		#
		# Three cases for signalling the parent we're done:
		# 1. Incoming tail sync arcs or an explicit duration:
		#	When these fire we signal SCHED_DONE and TERMINATE
		#	ourselves. No special action on end-of-loop
		# 2. We loop indefinite:
		#	Immedeately tell our parents we are done. No special
		#	actions on end-of-loop.
		# 3. Other cases (fixed loopcount and no duration/tailsync):
		#	End-of-loop signals SCHED_DONE.
		# In all cases a SCHED_STOP is translated to a terminate of
		# ourselves.
		#
		if terminate_events:
			srlist.append(terminate_events, scheddone_actions +
				      [(TERMINATE, self)])
			terminate_actions.append( (TERMINATE, self) )
			srlist.append( ([(LOOPEND_DONE, self)], []) )
		elif self.curloopcount < 0:
			sched_actions = sched_actions + scheddone_actions
			#terminate_actions.append( (TERMINATE, self) )
			srlist.append( ([(LOOPEND_DONE, self)], []) )
		else:
			srlist.append( ([(LOOPEND_DONE, self)],
					scheddone_actions) )
##		for ev in terminate_events + [(TERMINATE, self)]:
##			srlist.append( [ev], terminate_actions )
		srlist.append([(TERMINATE, self)], terminate_actions)

		return sched_actions, terminate_actions, srlist


	def gensr_envelope_laterloop(self, gensr_body, loopcount,
				     sched_actions, scheddone_actions,
				     terminate_events):
		srlist = []

		body_sched_actions = []
		body_scheddone_actions = [(SCHED_DONE, self.looping_body_self)]
		body_terminate_events = []

		body_sched_actions, body_schedstop_actions, srlist = \
				    gensr_body(body_sched_actions,
					       body_scheddone_actions,
					       body_terminate_events,
					       self.looping_body_self)

		# When the loop has started we start the body
		srlist.append( ([(LOOPSTART_DONE, self)], body_sched_actions) )

		# Terminating the body doesn't terminate the loop,
		# but the other way around it does
##		srlist.append( ([(TERMINATE, self.looping_body_self)],
##				body_terminate_actions) )

		# When the body is done we stop it, and we end/restart the loop
		srlist.append( ([(SCHED_DONE, self.looping_body_self)],
				[(LOOPEND, self),
				 (SCHED_STOP, self.looping_body_self)]) )
		srlist.append( ([(SCHED_STOP, self.looping_body_self)],
				body_schedstop_actions) )

		return [], [], srlist

	def gensr_body_par(self, sched_actions, scheddone_actions,
			   terminate_events, self_body=None):
		srlist = []
		schedstop_actions = []
		terminate_actions = []
		scheddone_events = []
		if self_body == None:
			self_body = self

		termtype = MMAttrdefs.getattr(self, 'terminator')
		if termtype == 'FIRST':
			terminating_children = self.wtd_children[:]
		elif termtype == 'LAST':
			terminating_children = []
		else:
			terminating_children = []
			for child in self.wtd_children:
				if MMAttrdefs.getattr(child, 'name') \
				   == termtype:
					terminating_children.append(child)

		for child in self.wtd_children:
			srlist = srlist + child.gensr()

			sched_actions.append( (SCHED, child) )
			schedstop_actions.append( (SCHED_STOP, child) )
			terminate_actions.append( (TERMINATE, child) )

			if child in terminating_children:
				srlist.append( ([(SCHED_DONE, child)],
						[(TERMINATE, self_body)]))
			else:
				scheddone_events.append( (SCHED_DONE, child) )

		#
		# Trickery to handle dur and end correctly:
		#
		if scheddone_events and \
		   (terminate_events or terminating_children):
			# Terminate_events means we have a specified
			# duration. We obey this, and ignore scheddone
			# events from our children.
			# Terminating_children means we have a
			# terminator attribute that points to a child.
			# We obey this also and ignore scheddone
			# events from our other children.
			srlist.append( (scheddone_events, []) )
			scheddone_events = []

		if scheddone_events:
			srlist.append((scheddone_events,
				       scheddone_actions))
		else:
			terminate_actions = terminate_actions + \
					    scheddone_actions

		for ev in terminate_events+[(TERMINATE, self_body)]:
			srlist.append( [ev], terminate_actions )
		return sched_actions, schedstop_actions, srlist

	def gensr_body_seq(self, sched_actions, scheddone_actions,
			   terminate_events, self_body=None):
		srlist = []
		schedstop_actions = []
		terminate_actions = []
		if self_body == None:
			self_body = self

		previous_done_events = []
		previous_stop_actions = []
		for ch in self.wtd_children:
			# Link previous child to this one
			if previous_done_events:
				srlist.append(
					(previous_done_events,
					 [(SCHED, ch)]+previous_stop_actions) )
			else:
				sched_actions.append((SCHED, ch))

			# Setup events/actions for next child to link to
			previous_done_events = [(SCHED_DONE, ch)]
			previous_stop_actions = [(SCHED_STOP, ch)]

			# And setup terminate actions
			terminate_actions.append( (TERMINATE, ch) )

			# And child's own events/actions
			srlist = srlist + ch.gensr()

		# Link the events/actions for the last child to the parent,
		# iff we don't have a explicit duration or end.
		if terminate_events:
			terminate_actions = terminate_actions + \
					    scheddone_actions
			srlist.append( (previous_done_events, []) )
		else:
			srlist.append( (previous_done_events,
					scheddone_actions) )
##		append SCHED_DONE to terminate_actions??
		schedstop_actions = previous_stop_actions

		for ev in terminate_events+[(TERMINATE, self_body)]:
			srlist.append( [ev], terminate_actions )

		return sched_actions, schedstop_actions, srlist

	def gensr_body_realpix(self, sched_actions, scheddone_actions,
			   terminate_events, self_body=None):
		srlist = []
		schedstop_actions = []
		terminate_actions = []
		scheddone_events = []
		if self_body == None:
			self_body = self

		for child in (self.realpix_body, self.caption_body):
##			print 'gensr for', child
##			print 'func is', child._is_realpix_with_captions(), child._is_realpix_with_captions

			srlist = srlist + child.gensr(overrideself=child)

			sched_actions.append( (SCHED, child) )
			schedstop_actions.append( (SCHED_STOP, child) )
			terminate_actions.append( (TERMINATE, child) )

			scheddone_events.append( (SCHED_DONE, child) )

		#
		# Trickery to handle dur and end correctly:
		# XXX isn't the dur passed on in the files? Check.
		if terminate_events:
			# Terminate_events means we have a specified
			# duration. We obey this, and ignore scheddone
			# events from our children.
			# Terminating_children means we have a
			# terminator attribute that points to a child.
			# We obey this also and ignore scheddone
			# events from our other children.
			srlist.append( (scheddone_events, []) )
			scheddone_events = []

		if scheddone_events:
			srlist.append((scheddone_events,
				       scheddone_actions))
		else:
			terminate_actions = terminate_actions + \
					    scheddone_actions

		for ev in terminate_events+[(TERMINATE, self_body)]:
			srlist.append( [ev], terminate_actions )
		return sched_actions, schedstop_actions, srlist
		
	def _is_realpix_with_captions(self):
		if self.type == 'ext' and self.GetChannelType() == 'RealPix':
			# It is a realpix node. Check whether it has captions
			captionchannel = MMAttrdefs.getattr(self, 'captionchannel')
			if captionchannel and captionchannel != 'undefined':
				return 1
		return 0

	def GenAllSR(self, seeknode):
##		self.SetPlayability()
		if not seeknode:
			seeknode = self
## Commented out for now: this cache messes up Scheduler.GenAllPrearms()
##		if hasattr(seeknode, 'sractions'):
##			sractions = seeknode.sractions[:]
##			srevents = {}
##			for key, val in seeknode.srevents.items():
##				srevents[key] = val
##			return sractions, srevents
		#
		# First generate arcs
		#
		self.PruneTree(seeknode)
		arcs = self.GetArcList()
		arcs = self.FilterArcList(arcs)
		for i in range(len(arcs)):
			n1, s1, n2, s2, delay = arcs[i]
			n1.SetArcSrc(s1, delay, i)
			n2.SetArcDst(s2, i)
		#
		# Now run through the tree
		#
		srlist = self.gensr()
		srlist.append(([(SCHED_DONE, self)], [(SCHED_STOP, self)]))

		sractions, srevents = self.splitsrlist(srlist)

		seeknode.sractions = sractions[:]
		seeknode.srevents = {}
		for key, val in srevents.items():
			seeknode.srevents[key] = val
		if self.context.editmgr:
			self.context.editmgr.register(seeknode)
		return sractions, srevents

	def splitsrlist(self, srlist, offset=0):
		sractions = [None]*len(srlist)
		srevents = {}
		for actionpos in range(len(srlist)):
			# Replace eventlist by count, and store events in dict
			events = srlist[actionpos][0]
			nevents = len(events)
			sractions[actionpos] = (nevents,) + \
					       srlist[actionpos][1:]
			for ev in events:
				if srevents.has_key(ev):
					raise CheckError, 'Scheduler: Duplicate event: %s' % ev2string(ev)
				srevents[ev] = actionpos+offset
		return sractions, srevents
	#
	# Re-generate SR actions/events for a loop. Called for the
	# second and subsequent times through the loop.
	#
	def GenLoopSR(self, offset):
		# XXXX Try by Jack:
		self.PruneTree(None)
		srlist = self.gensr(looping=1)
		sractions, srevents = self.splitsrlist(srlist, offset)
		return sractions, srevents
	#
	# Check whether the current loop has reached completion.
	#
	def moreloops(self, decrement=0):
		rv = self.curloopcount
		if decrement and self.curloopcount > 0:
			self.curloopcount = self.curloopcount - 1
		return (rv != 0)

	def stoplooping(self):
		self.curloopcount = 0

	# eidtmanager stuff
	def transaction(self):
		return 1

	def rollback(self):
		pass

	def commit(self):
##		print 'MMNode: deleting cached values'
		try:
			del self.sractions
		except AttributeError:
			pass
		try:
			del self.srevents
		except AttributeError:
			pass
		try:
			del self.prearmlists
		except AttributeError:
			pass
		self.context.editmgr.unregister(self)

	def kill(self):
		pass

	#
	# Methods to handle sync arcs.
	#
	# The GetArcList method recursively gets a list of sync arcs
	# The sync arcs are returned as (n1, s1, n2, s2, delay) tuples.
	# Unused sync arcs are not filtered out of the list yet.
	#
	def GetArcList(self):
##		if not self.GetSummary('synctolist'):
##			return []
		synctolist = []
		delay = self.GetAttrDef('begin', 0.0)
		if delay > 0:
			if self.parent.type == 'seq':
				xnode = None
				xside = TL
				for n in self.parent.children:
					if n is self:
						break
					xnode = n
				else:
					# first child in seq
					xnode = self.parent
					xside = HD
			else:
				xnode = self.parent
				xside = HD
			synctolist.append((xnode, xside, self, HD, delay))
		arcs = self.GetAttrDef('synctolist', [])
		for arc in arcs:
			n1uid, s1, delay, s2 = arc
			try:
				n1 = self.MapUID(n1uid)
			except NoSuchUIDError:
				print 'GetArcList: skipping syncarc with deleted source'
				continue
			synctolist.append((n1, s1, self, s2, delay))
		if self.GetType() in ('seq', 'par'):
			for c in self.wtd_children:
				synctolist = synctolist + c.GetArcList()
		elif self.GetType() == 'alt':
			for c in self.wtd_children:
				if c.WillPlay():
					synctolist = synctolist + \
						     c.GetArcList()
					break
		return synctolist
	#
	# FilterArcList removes all arcs if they are not part of the
	# subtree rooted at this node.
	#
	def FilterArcList(self, arclist):
		newlist = []
		for arc in arclist:
			n1, s1, n2, s2, delay = arc
			if self.IsWtdAncestorOf(n1) and \
				  self.IsWtdAncestorOf(n2):
				newlist.append(arc)
		return newlist
	#
	def IsWtdAncestorOf(self, x):
		while x is not None:
			if self is x: return 1
			xnew = x.parent
			if xnew is None:
				return 0
			try:
				if not x in xnew.wtd_children:
					return 0
			except AttributeError:
				return 0
			x = xnew
		return 0

	def GetWtdChildren(self):
		return self.wtd_children

	def IsWanted(self):
		# This is not very efficient...
		if self.parent == None:
			return 1
		parent = self.parent
		if not hasattr(parent, 'wtd_children'):
			return 1
		return self in parent.wtd_children and parent.IsWanted()

	#
	# SetArcSrc sets the source of a sync arc.
	#
	def SetArcSrc(self, side, delay, aid):
		self.sync_to[side].append((SYNC, (delay, aid)))

	#
	# SetArcDst sets the destination of a sync arc.
	#
	def SetArcDst(self, side, aid):
		self.sync_from[side].append((SYNC_DONE, aid))

	#
	# method for maintaining armed status when the ChannelView is
	# not active
	#
	def set_armedmode(self, mode):
		self.armedmode = mode
		
	#
	# method for maintaining node's info-icon state when the HierarchyView is
	# not active
	#
	def set_infoicon(self, icon, msg=None):
		self.infoicon = icon
		self.errormessage = msg
		
	def clear_infoicon(self):
		self.infoicon = ''
		self.errormessage = None
		for ch in self.children:
			ch.clear_infoicon()

	#
	# Playability depending on system/environment parameters
	# and various other things. There are three concepts:
	# ShouldPlay() - A decision based only on node attributes
	#                and preference settings.
	# _CanPlay()   - Depends on ShouldPlay() and whether the channel
	#                actually can play the node.
	# WillPlay()   - Based on ShouldPlay() and switch items.
	#
	def _CanPlay(self):
		if not self.canplay is None:
			return self.canplay
		self.canplay = self.ShouldPlay()
		if not self.canplay:
			return 0
		# Check that we really can
		getchannelfunc = self.context.getchannelbynode
		if self.type in leaftypes and getchannelfunc:
			# For media nodes check that the channel likes
			# the node
			chan = getchannelfunc(self)
			if not chan or not chan.getaltvalue(self):
				self.canplay = 0
		return self.canplay

	def ShouldPlay(self):
		if not self.shouldplay is None:
			return self.shouldplay
		self.shouldplay = 0
		# If any of the system test attributes don't match
		# we should not play
		all = settings.getsettings()
		for setting in all:
			if self.attrdict.has_key(setting):
				ok = settings.match(setting,
						    self.attrdict[setting])
				if not ok:
					return 0
		# And if our user group doesn't match we shouldn't
		# play either
		u_group = self.GetAttrDef('u_group', 'undefined')
		if u_group != 'undefined':
			val = self.context.usergroups.get(u_group)
			if val is not None and val[1] != 'RENDERED':
				return 0
		# Else we should
		self.shouldplay = 1
		return 1

	def WillPlay(self):
		if not self.willplay is None:
			return self.willplay
		parent = self.parent
		# If our parent won't play we won't play
		if parent and not parent.WillPlay():
			self.willplay = 0
			return 0
		# And if we shouldn't play we won't play either
		if not self.ShouldPlay():
			self.willplay = 0
			return 0
		# And if our parent is a switch we have to check whether
		# we're the Chosen One
		if parent and parent.type == 'alt' and \
		   not parent.ChosenSwitchChild() is self:
			self.willplay = 0
			return 0
		self.willplay = 1
		return 1

	def ChosenSwitchChild(self, childrentopickfrom=None):
		"""For alt nodes, return the child that will be played"""
		if childrentopickfrom is None:
			childrentopickfrom = self.children
		for ch in childrentopickfrom:
			if ch._CanPlay():
				return ch
		return None

	def ResetPlayability(self):
		self.canplay = self.willplay = self.shouldplay = None
		for child in self.children:
			child.ResetPlayability()

# Make a "deep copy" of an arbitrary value
#
def _valuedeepcopy(value):
	if type(value) is type({}):
		copy = {}
		for key in value.keys():
			copy[key] = _valuedeepcopy(value[key])
		return copy
	if type(value) is type([]):
		copy = value[:]
		for i in range(len(copy)):
			copy[i] = _valuedeepcopy(copy[i])
		return copy
	# XXX Assume everything else is immutable.  Not quite true...
	return value
# When a subtree is copied, certain hyperlinks must be copied as well.
# - When copying into another context, all hyperlinks within the copied
#   subtree must be copied.
# - When copying within the same context, all outgoing hyperlinks
#   must be copied as well as all hyperlinks within the copied subtree.
#
# XXX This code knows perhaps more than is good for it about the
# representation of hyperlinks.  However it knows more about anchors
# than would be good for code placed in module Hlinks...
#
def _copyinternalhyperlinks(src_hyperlinks, dst_hyperlinks, uidremap):
	links = src_hyperlinks.getall()
	newlinks = []
	for a1, a2, dir, ltype in links:
		if type(a1) is not type(()) or type(a2) is not type(()):
			continue
		uid1, aid1 = a1
		uid2, aid2 = a2
		if uidremap.has_key(uid1) and uidremap.has_key(uid2):
			uid1 = uidremap[uid1]
			uid2 = uidremap[uid2]
			a1 = uid1, aid1
			a2 = uid2, aid2
			link = a1, a2, dir, ltype
			newlinks.append(link)
	if newlinks:
		dst_hyperlinks.addlinks(newlinks)

def _copyoutgoinghyperlinks(hyperlinks, uidremap):
	from Hlinks import DIR_1TO2, DIR_2TO1, DIR_2WAY
	links = hyperlinks.getall()
	newlinks = []
	for a1, a2, dir, ltype in links:
		changed = 0
		if type(a1) is type(()):
			uid1, aid1 = a1
			if uidremap.has_key(uid1) and \
			   dir in (DIR_1TO2, DIR_2WAY):
				uid1 = uidremap[uid1]
				a1 = uid1, aid1
				changed = 1
		if type(a2) is type(()):
			uid2, aid2 = a2
			if uidremap.has_key(uid2) and \
			   dir in (DIR_2TO1, DIR_2WAY):
				uid2 = uidremap[uid2]
				a2 = uid2, aid2
				changed = 1
		if changed:
			link = a1, a2, dir, ltype
			newlinks.append(link)
##		uid1, aid1 = a1
##		uid2, aid2 = a2
##		if uidremap.has_key(uid1) and dir in (DIR_1TO2, DIR_2WAY) or \
##			uidremap.has_key(uid2) and dir in (DIR_2TO1, DIR_2WAY):
##			if uidremap.has_key(uid1):
##				uid1 = uidremap[uid1]
##				a1 = uid1, aid1
##			if uidremap.has_key(uid2):
##				uid2 = uidremap[uid2]
##				a2 = uid2, aid2
##			link = a1, a2, dir, ltype
##			newlinks.append(link)
	if newlinks:
		hyperlinks.addlinks(newlinks)

#
# MergeList merges two lists. It also returns a status value to indicate
# whether there was an overlap between the lists.
#
def MergeLists(l1, l2):
	overlap = []
	for i in l2:
		if i in l1:
			overlap.append(i)
		else:
			l1.append(i)
	return l1, overlap
