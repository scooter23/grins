__version__ = "$Id$"

import MMNodeBase
import MMAttrdefs
from MMTypes import *
from MMExc import *
from SR import *
from AnchorDefs import *
import Duration

class MMNodeContext(MMNodeBase.MMNodeContext):
	def __init__(self, nodeclass):
		MMNodeBase.MMNodeContext.__init__(self, nodeclass)
		self.nextuid = 1
		self.armedmode = None

	def newnode(self, type):
		return self.newnodeuid(type, self.newuid())

	def newuid(self):
		while 1:
			uid = `self.nextuid`
			self.nextuid = self.nextuid + 1
			if not self.uidmap.has_key(uid):
				return uid

	def forgetnode(self, uid):
		del self.uidmap[uid]

	#
	# Channel administration
	#
	def addchannel(self, name, i, type):
		if name in self.channelnames:
			raise CheckError, 'addchannel: existing name'
		if not 0 <= i <= len(self.channelnames):
			raise CheckError, 'addchannel: invalid position'
		c = MMChannel(self, name)
		c['type'] = type
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
			try:
				if n.GetRawAttr('channel') == oldname:
					n.SetAttr('channel', newname)
			except NoSuchAttrError:
				pass

	#
	# Hyperlink administration
	#
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

	# Internal: predicates to select nodes pertaining to self._roots
	def _isbadlink(self, link):
		return not self._isgoodlink(link)

	def _isgoodlink(self, link):
		(uid1, aid1), (uid2, aid2), dir, type = link
		srcok = (self.uidmap.has_key(uid1) \
		   and self.uidmap[uid1].GetRoot() in self._roots)
		dstok = (('/' in uid2) or (self.uidmap.has_key(uid2) \
		   and self.uidmap[uid2].GetRoot() in self._roots))
		return (srcok and dstok)

class MMChannel(MMNodeBase.MMChannel):
	def _setname(self, name): # Only called from context.setchannelname()
		self.name = name

	def _destroy(self):
		self.context = None

	def stillvalid(self):
		return self.context is not None

	def _getdict(self): # Only called from MMWrite.fixroot()
		return self.attrdict

	def __delitem__(self, key):
		del self.attrdict[key]

MMSyncArc = MMNodeBase.MMSyncArc

class MMNode(MMNodeBase.MMNode):
	def __init__(self, type, context, uid):
		MMNodeBase.MMNode.__init__(self, type, context, uid)
		self.parent = None
		self.children = []
##		self.summaries = {}
		self.setgensr()
		self.isloopnode = 0

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

	def GetParent(self):
		return self.parent

	def GetRoot(self):
		root = None
		x = self
		while x:
			root = x
			x = x.parent
		return root

	def GetPath(self):
		path = []
		x = self
		while x:
			path.append(x)
			x = x.parent
		path.reverse()
		return path

	def IsAncestorOf(self, x):
		while x is not None:
			if self == x: return 1
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

	def GetInherAttr(self, name):
		x = self
		while x:
			if x.attrdict:
				try:
					return x.GetAttr(name)
				except NoSuchAttrError:
					pass
			x = x.parent
		raise NoSuchAttrError, 'in GetInherAttr()'

	def GetDefInherAttr(self, name):
		x = self.parent
		while x:
			if x.attrdict:
				try:
					return x.GetAttr(name)
				except NoSuchAttrError:
					pass
			x = x.parent
		raise NoSuchAttrError, 'in GetInherDefAttr()'

## 	def GetSummary(self, name):
## 		if not self.summaries.has_key(name):
## 			self.summaries[name] = self._summarize(name)
## 		return self.summaries[name]

	def Dump(self):
		print '*** Dump of', self.type, 'node', self, '***'
		attrnames = self.attrdict.keys()
		attrnames.sort()
		for name in attrnames:
			print 'Attr', name + ':', `self.attrdict[name]`
## 		summnames = self.summaries.keys()
## 		if summnames:
## 			summnames.sort()
## 			print 'Has summaries for attrs:',
## 			for name in summnames:
## 				print name,
## 			print
		if self.type == 'imm' or self.values:
			print 'Values:',
			for value in self.values: print value,
			print
		if self.type in interiortypes or self.children:
			print 'Children:',
			for child in self.children: print child.GetType(),
			print

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
			return [MMAttrdefs.getattr(self, 'channel')], None
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
		copy = context.newnode(self.type)
		uidremap[self.uid] = copy.uid
		copy.attrdict = _valuedeepcopy(self.attrdict)
		copy.values = _valuedeepcopy(self.values)
		for child in self.children:
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
		newarcs = []
		for xuid, xsize, delay, yside in arcs:
			if uidremap.has_key(xuid):
				xuid = uidremap[xuid]
			newarcs.append(xuid, xsize, delay, yside)
		if newarcs <> arcs:
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
##		self._updsummaries([name])

	def DelAttr(self, name):
		if not self.attrdict.has_key(name):
			raise NoSuchAttrError, 'in DelAttr()'
		del self.attrdict[name]
##		self._updsummaries([name])

	def Destroy(self):
		if self.parent: raise CheckError, 'Destroy() non-root node'

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

	def Extract(self):
		if not self.parent: raise CheckError, 'Extract() root node'
		parent = self.parent
		self.parent = None
		parent.children.remove(self)
		name = MMAttrdefs.getattr(self, 'name')
		if name and MMAttrdefs.getattr(parent, 'terminator') == name:
			parent.DelAttr('terminator')
##		parent._fixsummaries(self.summaries)

	def AddToTree(self, parent, i):
		if self.parent: raise CheckError, 'AddToTree() non-root node'
		if self.context is not parent.context:
			# XXX Decide how to handle this later
			raise CheckError, 'AddToTree() requires same context'
		if i == -1:
			parent.children.append(self)
		else:
			parent.children.insert(i, self)
		self.parent = parent
## 		parent._fixsummaries(self.summaries)
## 		parent._rmsummaries(self.summaries.keys())

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
			if not parent:
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
			if not parent:
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
		if bag and bag.type not in bagtypes:
			raise CheckError, 'FindMiniBag: minidoc not rooted in a choice node!'
		return bag

## 	#
## 	# Private methods for summary management
## 	#
## 	def _rmsummaries(self, keep):
## 		x = self
## 		while x:
## 			changed = 0
## 			for key in x.summaries.keys():
## 				if key not in keep:
## 					del x.summaries[key]
## 					changed = 1
## 			if not changed:
## 				break
## 			x = x.parent

## 	def _fixsummaries(self, summaries):
## 		tofix = summaries.keys()
## 		for key in tofix[:]:
## 			if summaries[key] == []:
## 				tofix.remove(key)
## 		self._updsummaries(tofix)

## 	def _updsummaries(self, tofix):
## 		x = self
## 		while x and tofix:
## 			for key in tofix[:]:
## 				if not x.summaries.has_key(key):
## 					tofix.remove(key)
## 				else:
## 					s = x._summarize(key)
## 					if s == x.summaries[key]:
## 						tofix.remove(key)
## 					else:
## 						x.summaries[key] = s
## 			x = x.parent

## 	def _summarize(self, name):
## 		try:
## 			summary = [self.GetAttr(name)]
## 		except NoSuchAttrError:
## 			summary = []
## 		for child in self.children:
## 			list = child.GetSummary(name)
## 			for item in list:
## 				if item not in summary:
## 					summary.append(item)
## 		summary.sort()
## 		return summary

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
		elif type == 'seq':
			self.gensr = self.gensr_seq
		elif type == 'par':
			self.gensr = self.gensr_par
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
		if not seeknode or seeknode is self:
			self._FastPruneTree()
			return
		if seeknode and not self.IsAncestorOf(seeknode):
			raise CheckError, 'Seeknode not in tree!'
		self.sync_from = ([],[])
		self.sync_to = ([],[])
		if self.type in playabletypes:
			return
		self.wtd_children = []
		if self.type == 'seq':
			for c in self.children:
				if seeknode and c.IsAncestorOf(seeknode):
					self.wtd_children.append(c)
					c.PruneTree(seeknode)
					seeknode = None
				elif not seeknode:
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
		self.wtd_children = self.children[:]
		for c in self.children:
			c._FastPruneTree()


	def EndPruneTree(self):
		pass
## 		del self.sync_from
## 		del self.sync_to
## 		if self.type in ('seq', 'par'):
## 			for c in self.wtd_children:
## 				c.EndPruneTree()
## 			del self.wtd_children

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
	#
	def gensr_leaf(self):
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
		actions.append((SCHED, self.wtd_children[0]))
		srlist.append((prereqs, actions))
		prereqs = [(SCHED_DONE, self.wtd_children[0])]
		actions = [(SCHED_STOP, self.wtd_children[0])]
		tlist.append((TERMINATE, self.wtd_children[0]))
		last_actions = actions
		actions = [(SCHED_DONE, self)]
		srlist.append((prereqs, actions))
		srlist.append(([(SCHED_STOP, self)],
			       last_actions + out1))
		tlist.append((SCHED_DONE, self))
		srlist.append(([(TERMINATE, self)], tlist))
		for ev in in1:
			srlist.append(([ev], [(TERMINATE, self)]))
		return srlist + self.wtd_children[0].gensr()

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
	# gensr_headactions returns a list of srrecords and a list of
	# events that start an interior node. Incoming syncarcs and looping
	# are handled here.
	#
	def gensr_headactions(self, looping):
		if looping:
			# This is not the first time we're generating
			# events, it is yet another time through the loop
			return [], [(LOOPSTART_DONE, self)]
		in0 = self.sync_from[0]		# incoming syncarcs to head
		prereq = [(SCHED, self)] + in0	# all events needed to start
		sr_list = []
		loopcount = MMAttrdefs.getattr(self, 'loop')
		self.isloopnode = (loopcount != 1)
		if self.isloopnode:
			# Looping node. Our SCHEDSTART (plus syncarcs) gives
			# a LOOPSTART, and the LOOPSTART_DONE starts playing
			# the node.
			# First decrement of loopcount will be done
			# during LOOPSTART.
			if loopcount == 0:
				self.curloopcount = -1
			else:
				self.curloopcount = loopcount
			sr_list = [
				(
					prereq,
					[(LOOPSTART, self)]
				)
			]
			prereq = [(LOOPSTART_DONE, self)]
		else:
			# Non-looping node, so our SCHEDSTART (and arcs) just
			# starts playing the node.
			# There is no LOOPSTART, so we decrement the count
			# here.
			self.curloopcount = loopcount-1
		return sr_list, prereq
	#
	# gensr_tailactions gets the list of events that should all have
	# occurred before a node finishes. It returns the srrecords list
	# that make the world continue revolving. This may include a loop
	# end construct, or may be an immedeate SCHED_DONE and outgoing
	# tail syncarc list
	#
	def gensr_tailactions(self, events, looping):
		if looping:
			# Second (or later) pass through the loop.
			# Only regenerate records for the LOOPEND.
			return [(events, [(LOOPEND, self)])]
		out1 = self.sync_to[1]	# outgoing syncarcs from tail
		if self.isloopnode:
			# all children done -> LOOPEND
			# LOOPEND_DONE -> SCHED_DONE, syncarcs
			srlist = [(
				    events,
				    [(LOOPEND, self)]
				  ) , (
				    [(LOOPEND_DONE, self)],
				    [(SCHED_DONE, self)]+out1
				  )]
		else:
			# all children done -> SCHED_DONE, syncarcs
			srlist = [(
				    events,
				    [(SCHED_DONE, self)]+out1
				 )]
		return srlist
		
			
			
	#
	# Generate schedrecords for a sequential node
	def gensr_seq(self, looping=0):
		if not self.wtd_children:
			self.curloopcount = 0
			return self.gensr_empty()
		in0, in1 = self.sync_from
		out0, out1 = self.sync_to
		n_sr = len(self.wtd_children)+1
		sr_list, trigger_events = self.gensr_headactions(looping)
		last_actions = []
		t_list = []
		duration = MMAttrdefs.getattr(self, 'duration')
		if duration > 0:
			# if duration set, we must trigger a timeout
			# and we must catch the timeout to terminate
			# the node
			out0 = out0 + [(SYNC, (duration, self))]
			sr_list.append(([(SYNC_DONE, self)],
					[(TERMINATE, self)]))
		for i in range(n_sr):
			if i == 0:
				prereq = trigger_events
				actions = out0[:]
			else:
				arg = self.wtd_children[i-1]
				sr_list = sr_list + arg.gensr()
				prereq = [(SCHED_DONE, arg)]
				actions = [(SCHED_STOP, arg)]
			if i == n_sr-1:
				last_actions = actions
				tail_srlist = self.gensr_tailactions(prereq,
						    looping)
				sr_list[len(sr_list):] = tail_srlist
			else:
				actions.append((SCHED, self.wtd_children[i]))
				sr_list.append((prereq, actions))
			if i < n_sr-1:
				t_list.append((TERMINATE,
					       self.wtd_children[i]))
		sr_list.append( ([(SCHED_STOP, self)], last_actions) )
		for ev in in1:
			sr_list.append(([ev], [(TERMINATE, self)]))
## 		t_list.append((SCHED_DONE, self))
		sr_list.append(([(TERMINATE, self)], t_list))
		return sr_list

	def gensr_par(self, looping=0):
		if not self.wtd_children:
			self.curloopcount = 0
			return self.gensr_empty()
		in0, in1 = self.sync_from
		out0, out1 = self.sync_to
		duration = MMAttrdefs.getattr(self, 'duration')
		termtype = MMAttrdefs.getattr(self, 'terminator')
		alist = out0[:]		# actions on SCHED of self
		plist = []		# events needed before we stop
		slist = []		# actions on SCHED_STOP of self
		tlist = []		# actions on TERMINATE of self

		result, trigger_events = self.gensr_headactions(looping)

		result.append((trigger_events, alist))
		result.append(([(SCHED_STOP, self)], slist))
		result.append(([(TERMINATE, self)], tlist))

		for ev in in1:
			result.append(([ev], [(TERMINATE, self)]))
		added_entry = 0
		for arg in self.wtd_children:
			alist.append((SCHED, arg))
			slist.append((SCHED_STOP, arg))
			tlist.append((TERMINATE, arg))
			result = result + arg.gensr()
			if termtype == 'FIRST':
				added_entry = 1
				result.append(([(SCHED_DONE, arg)],
					       [(TERMINATE, self)]))
			elif termtype != 'FIRST' and \
			     termtype != 'LAST' and \
			     MMAttrdefs.getattr(arg, 'name') == termtype:
				added_entry = 1
				result.append(([(SCHED_DONE, arg)],
					       [(TERMINATE, self)]))
			else:
				plist.append((SCHED_DONE, arg))
		if plist:
			# come here only when there were children, and
			# termtype != 'FIRST' and (if termtype refers to
			# a node) there were other children as well
			if not added_entry:
				# termtype=='LAST' or termtype refers to
				# non-existent child
				added_entry = 1
				tail_srlist = self.gensr_tailactions(plist,
								     looping)
				result[len(result):] = tail_srlist
			else:
				# termtype refers to child, basically
				# ignore the other children
				result.append((plist, []))
		if termtype != 'LAST' and added_entry:
			# XXXX Comment by Jack: I _think_ this is also
			# correct for looping nodes, but I'm not 100% sure.
			tlist[len(tlist):] = [(SCHED_DONE, self)] + out1
		if duration > 0:
			# if duration set, we must trigger a timeout
			# and we must catch the timeout to terminate
			# the node
			alist.append((SYNC, (duration, self)))
			if not added_entry:
				tail_srlist = self.gensr_tailactions(
					[(SYNC_DONE, self)], looping)
				result[len(result):] = tail_srlist
			else:
				result.append(([(SYNC_DONE, self)],
					       [(TERMINATE, self)]))
		return result
# 	#
#	# gensr_arcs returns 4 lists of sync arc events: incoming head,
#	# outgoing head, incoming tail, outgoing tail.
#	#
#	def gensr_arcs(self):
#		in0 = []
#		out0 = []
#		in1 = []
#		out1 = []
#		for i in self.sync_from[0]:
#			in0.append((SYNC_DONE, i))
#		for i in self.sync_from[1]:
#			in1.append((SYNC_DONE, i))
#		for i in self.sync_to[0]:
#			out0.append((SYNC, i))
#		for i in self.sync_to[1]:
#			out1.append((SYNC, i))
#		return in0, out0, in1, out1
			
	def GenAllSR(self, seeknode):
		if not seeknode:
			seeknode = self
## Commented out for now: this cache messes up Scheduler.GenAllPrearms()
## 		if hasattr(seeknode, 'sractions'):
## 			sractions = seeknode.sractions[:]
## 			srevents = {}
## 			for key, val in seeknode.srevents.items():
## 				srevents[key] = val
## 			return sractions, srevents
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
		# XXXX Should we prunetree() here?
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

	def transaction(self):
		return 1

	def rollback(self):
		pass

	def commit(self):
## 		print 'MMNode: deleting cached values'
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
## 		if not self.GetSummary('synctolist'):
## 			return []
		synctolist = []
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
			if not xnew:
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
	for a1, a2, dir, type in links:
		uid1, aid1 = a1
		uid2, aid2 = a2
		if uidremap.has_key(uid1) and uidremap.has_key(uid2):
			uid1 = uidremap[uid1]
			uid2 = uidremap[uid2]
			a1 = uid1, aid1
			a2 = uid2, aid2
			link = a1, a2, dir, type
			newlinks.append(link)
	if newlinks:
		dst_hyperlinks.addlinks(newlinks)

def _copyoutgoinghyperlinks(hyperlinks, uidremap):
	from Hlinks import DIR_1TO2, DIR_2TO1, DIR_2WAY
	links = hyperlinks.getall()
	newlinks = []
	for a1, a2, dir, type in links:
		uid1, aid1 = a1
		uid2, aid2 = a2
		if uidremap.has_key(uid1) and dir in (DIR_1TO2, DIR_2WAY) or \
			uidremap.has_key(uid2) and dir in (DIR_2TO1, DIR_2WAY):
			if uidremap.has_key(uid1):
				uid1 = uidremap[uid1]
				a1 = uid1, aid1
			if uidremap.has_key(uid2):
				uid2 = uidremap[uid2]
				a2 = uid2, aid2
			link = a1, a2, dir, type
			newlinks.append(link)
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
