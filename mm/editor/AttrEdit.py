__version__ = "$Id$"

import windowinterface
import MMAttrdefs
import ChannelMap
from MMExc import *			# exceptions
import MMNode
from MMTypes import *
from AnchorDefs import *		# ATYPE_*
from Hlinks import DIR_1TO2, TYPE_JUMP
import string

# There are two basic calls into this module (but see below for more):
# showattreditor(node) creates an attribute editor form for a node
# and hideattreditor(node) hides it again.  Since the editor may also
# hide itself, spurious hide calls are ignored; also, only one attribute
# editor is allowed per node, and extra show calls are also ignored
# (actually, this pops up the window, to draw the user's attention...).

def showattreditor(toplevel, node):
	try:
		attreditor = node.attreditor
	except AttributeError:
		if node.__class__ is MMNode.MMNode:
			wrapperclass = NodeWrapper
			if node.GetType() == 'ext' and \
			   node.GetChannelType() == 'RealPix' and \
			   not hasattr(node, 'slideshow'):
				import realnode
				node.slideshow = realnode.SlideShow(node)
		else:
			wrapperclass = SlideWrapper
		attreditor = AttrEditor(wrapperclass(toplevel, node))
		node.attreditor = attreditor
	else:
		attreditor.pop()

# An additional call to check whether the attribute editor is currently
# active for a node (so the caller can put up a warning "you are already
# editing this node's attributes" instead of just silence).

def hasattreditor(node):
	try:
		attreditor = node.attreditor
	except AttributeError:
		return 0		# No attribute editor active
	return 1


# A similar interface for channels (note different arguments!).
# The administration is kept in channel.attreditor,
# which is created here if necessary.

def showchannelattreditor(toplevel, channel, new = 0):
	try:
		attreditor = channel.attreditor
	except AttributeError:
		attreditor = AttrEditor(ChannelWrapper(toplevel, channel), new)
		channel.attreditor = attreditor
	else:
		attreditor.pop()

def haschannelattreditor(channel):
	try:
		attreditor = channel.attreditor
	except AttributeError:
		return 0
	return 1

# A similar interface for documents (note different arguments!).
# The administration is kept in toplevel.attreditor,
# which is created here if necessary.

def showdocumentattreditor(toplevel):
	try:
		attreditor = toplevel.attreditor
	except AttributeError:
		attreditor = AttrEditor(DocumentWrapper(toplevel))
		toplevel.attreditor = attreditor
	else:
		attreditor.pop()

def hasdocumentattreditor(toplevel):
	try:
		attreditor = toplevel.attreditor
	except AttributeError:
		return 0
	return 1

# This routine checks whether we are in CMIF or SMIL mode, and
# whether the given attribute should be shown in the editor.
def cmifmode():
	import settings
	return settings.get('cmif')

# The "Wrapper" classes encapsulate the differences between attribute
# editors for nodes and channels.  If you want editors for other
# attribute collections (styles!) you may want to new wrappers.
# All wrappers should support the methods shown here; the __init__()
# method can have different arguments since it is only called from
# the show*() function.  (When introducing a style attr editor
# it should probably be merged with the class attr editor, using
# a common base class implementing most functions.)

class Wrapper: # Base class -- common operations
	def __init__(self, toplevel, context):
		self.toplevel = toplevel
		self.context = context
		self.editmgr = context.geteditmgr()
	def __repr__(self):
		return '<Wrapper instance>'
	def close(self):
		del self.context
		del self.editmgr
		del self.toplevel
	def getcontext(self):
		return self.context
	def register(self, object):
		self.editmgr.register(object)
	def unregister(self, object):
		self.editmgr.unregister(object)
	def transaction(self):
		return self.editmgr.transaction()
	def commit(self):
		self.editmgr.commit()
	def rollback(self):
		self.editmgr.rollback()

	def getdef(self, name):
		return MMAttrdefs.getdef(name)
	def valuerepr(self, name, value):
		return MMAttrdefs.valuerepr(name, value)
	def parsevalue(self, name, str):
		return MMAttrdefs.parsevalue(name, str, self.context)

class NodeWrapper(Wrapper):
	def __init__(self, toplevel, node):
		self.node = node
		self.root = node.GetRoot()
		Wrapper.__init__(self, toplevel, node.GetContext())

	def __repr__(self):
		return '<NodeWrapper instance, node=' + `self.node` + '>'

	def close(self):
		del self.node.attreditor
		del self.node
		del self.root
		Wrapper.close(self)

	def stillvalid(self):
		return self.node.GetRoot() is self.root

	def maketitle(self):
		name = MMAttrdefs.getattr(self.node, 'name')
		return 'Properties of node ' + name

	def __findlink(self, new = None):
		# if new == None, just return a link, if any
		# if new == '', remove any existing link
		# otherwise, remove old and set new link
		srcanchor = self.toplevel.links.wholenodeanchor(self.node, notransaction = 1, create = new)
		if not srcanchor:
			# no whole node anchor, and we didn't have to create one
			return None
		links = self.context.hyperlinks.findsrclinks(srcanchor)
		if links and new is not None:
			# there is a link, and we want to replace or delete it
			self.editmgr.dellink(links[0])
			links = []
		if not links:
			if not new:
				# remove the anchor since it isn't used
				alist = MMAttrdefs.getattr(self.node, 'anchorlist')[:]
				for i in range(len(alist)):
					if alist[i][A_TYPE] == ATYPE_WHOLE:
						del alist[i]
						break
				self.editmgr.setnodeattr(self.node, 'anchorlist', alist)
				return None
			link = srcanchor, new, DIR_1TO2, TYPE_JUMP
			self.editmgr.addlink(link)
		else:
			link = links[0]
		dstanchor = link[1]
		if type(dstanchor) == type(''):
			# external link
			return dstanchor
		return '<Hyperlink within document>'	# place holder for internal link

	def getattr(self, name): # Return the attribute or a default
		if name == '.hyperlink':
			return self.__findlink() or ''
		if name == '.type':
			return self.node.GetType()
		if name == '.values':
			return self.node.GetValues()
		return MMAttrdefs.getattr(self.node, name)

	def getvalue(self, name): # Return the raw attribute or None
		if name == '.hyperlink':
			return self.__findlink()
		if name == '.type':
			return self.node.GetType()
		if name == '.values':
			return self.node.GetValues() or None
		return self.node.GetRawAttrDef(name, None)

	def getdefault(self, name): # Return the default or None
		if name == '.hyperlink':
			return None
		if name == '.type':
			return None
		if name == '.values':
			return None
		return MMAttrdefs.getdefattr(self.node, name)

	def setattr(self, name, value):
		if name == '.hyperlink':
			self.__findlink(value)
			return
		if name == '.type':
			if self.node.GetType() == 'imm' and value != 'imm':
				self.editmgr.setnodevalues(self.node, [])
			self.editmgr.setnodetype(self.node, value)
			return
		if name == '.values':
			self.editmgr.setnodevalues(self.node, value)
			return
		self.editmgr.setnodeattr(self.node, name, value)

	def delattr(self, name):
		if name == '.hyperlink':
			self.__findlink('')
			return
		if name == '.values':
			self.editmgr.setnodevalues(self.node, [])
			return
		self.editmgr.setnodeattr(self.node, name, None)

	def delete(self):
		editmgr = self.editmgr
		if not editmgr.transaction():
			return # Not possible at this time
		editmgr.delnode(self.node)
		editmgr.commit()

	#
	# Return a list of attribute names that make sense for this node,
	# in an order that makes sense to the user.
	#
	def attrnames(self):
		import settings
		# Tuples are optional names and will be removed if they
		# aren't set
		namelist = [
			'name', ('file',),	# From nodeinfo window
			'.type',
			('terminator',),
			'begin', ('duration',), 'loop',	# Time stuff
			('clipbegin',), ('clipend',),	# More time stuff
			'title', 'abstract', ('alt',), ('longdesc',), 'author',
			'copyright', 'comment',
			'layout', ('u_group',),
			('mimetype',),	# XXXX Or should this be with file?
			'system_bitrate', 'system_captions',
			'system_language', 'system_overdub_or_caption',
			'system_required', 'system_screen_size',
			'system_screen_depth',
			]
		ntype = self.node.GetType()
		ctype = self.node.GetChannelType()
		if ntype in ('ext', 'imm') or not settings.get('lightweight'):
			namelist[1:1] = ['channel']
		if ntype == 'bag':
			namelist.append('bag_index')
		if ntype == 'par':
			namelist.append('terminator')
		if ntype in ('par', 'seq'):
			namelist.append('duration')
		if ntype in ('ext', 'imm'):
			namelist.append('alt')
			namelist.append('longdesc')
			if ChannelMap.isvisiblechannel(ctype):
				namelist.append('.hyperlink')
		if ntype == 'imm':
			namelist.append('.values')
		# Get the channel class (should be a subroutine!)
		if ChannelMap.channelmap.has_key(ctype):
			cclass = ChannelMap.channelmap[ctype]
			# Add the class's declaration of attributes
			namelist = namelist + cclass.node_attrs
			if cmifmode():
				for name in cclass.chan_attrs:
					if name in namelist: continue
					defn = MMAttrdefs.getdef(name)
					if defn[5] == 'channel':
						namelist.append(name)
		# Merge in nonstandard attributes (except synctolist!)
		extras = []
		for name in self.node.GetAttrDict().keys():
			if name not in namelist and \
				     MMAttrdefs.getdef(name)[3] <> 'hidden':
				extras.append(name)
		extras.sort()
		namelist = namelist + extras
		retlist = []
		for name in namelist:
			if name in retlist:
				continue
			if type(name) == type(()):
				if name[0] in namelist:
					# It is in the list, insert it here
					retlist.append(name[0])
				else:
					# Not in the list for this node, skip
					pass
			else:
				retlist.append(name)
		return retlist

	def getdef(self, name):
		if name == '.hyperlink':
			# Channelname -- special case
			return (('string', None), '',
				'Hyperlink', 'default',
				'Hyperlink', 'raw', 'light')
		if name == '.type':
			return (('string', None), '',
				'Node type', 'nodetype',
				'Node type', 'raw', 'light')
		if name == '.values':
			return (('string', None), '',
				'Content', 'text',
				'Data for node', 'raw', 'light')
		return MMAttrdefs.getdef(name)

class SlideWrapper(NodeWrapper):
	def attrnames(self):
		import realsupport
		tag = self.node.GetAttrDict()['tag']
		if tag == 'fill':
			namelist = ['color', 'displayfull', 'subregionxy',
				    'subregionwh', 'subregionanchor', 'start']
		elif tag in ('fadein', 'crossfade', 'wipe'):
			namelist = ['file', 'caption', 'fullimage', 'imgcropxy',
				    'imgcropwh', 'imgcropanchor', 'aspect',
				    'displayfull', 'subregionxy',
				    'subregionwh', 'subregionanchor', 'start',
				    'duration', 'maxfps', 'href',
				    'project_quality']
			if tag == 'wipe':
				namelist.append('direction')
				namelist.append('wipetype')
			if tag == 'fadein':
				namelist = namelist + \
					   ['fadeout', 'fadeouttime',
					    'fadeoutcolor', 'fadeoutduration']
		elif tag == 'fadeout':
			namelist = ['color', 'subregionxy', 'displayfull',
				    'subregionwh', 'subregionanchor', 'start',
				    'duration', 'maxfps']
		elif tag == 'viewchange':
			namelist = ['fullimage', 'imgcropxy', 'imgcropwh',
				    'imgcropanchor', 'displayfull',
				    'subregionxy', 'subregionwh',
				    'subregionanchor', 'start', 'duration',
				    'maxfps']
		else:
			namelist = []
		namelist.insert(0, 'tag')
		return namelist

	def getdefault(self, name): # Return the default or None
		if name == 'color':
			return MMAttrdefs.getattr(self.node.GetParent(), 'bgcolor')
		else:
			return NodeWrapper.getdefault(self, name)

	def commit(self):
		node = self.node
		attrdict = node.GetAttrDict()
		if (attrdict.get('displayfull', 1) or
		    attrdict.get('fullimage', 1)) and \
		   attrdict['tag'] in ('fadein', 'crossfade', 'wipe') and \
		   attrdict.get('file'):
			import MMurl, Sizes
			url = attrdict['file']
			url = node.GetContext().findurl(url)
			w,h = Sizes.GetSize(url)
			if w != 0 and h != 0:
				if attrdict.get('displayfull', 1):
					attrdict['subregionwh'] = w, h
				if attrdict.get('fullimage', 1):
					attrdict['imgcropwh'] = w, h
		NodeWrapper.commit(self)


class ChannelWrapper(Wrapper):
	def __init__(self, toplevel, channel):
		self.channel = channel
		Wrapper.__init__(self, toplevel, channel.context)

	def __repr__(self):
		return '<ChannelWrapper, name=' + `self.channel.name` + '>'

	def close(self):
		del self.channel.attreditor
		del self.channel
		Wrapper.close(self)

	def stillvalid(self):
		return self.channel.stillvalid()

	def maketitle(self):
		return 'Properties of channel ' + self.channel.name

	def getattr(self, name):
		if name == '.cname': return self.channel.name
		if self.channel.has_key(name):
			return self.channel[name]
		else:
			return MMAttrdefs.getdef(name)[1]

	def getvalue(self, name): # Return the raw attribute or None
		if name == '.cname': return self.channel.name
		if self.channel.has_key(name):
			return self.channel[name]
		else:
			return None

	def getdefault(self, name): # Return the default or None
		if name == '.cname': return ''
		if name == 'bgcolor' and self.channel.has_key('base_window'):
			# special case code for background color
			ch = self.channel
			pname = ch['base_window']
			pchan = ch.context.channeldict[pname]
			try:
				return pchan['bgcolor']
			except KeyError:
				pass
		return MMAttrdefs.getdef(name)[1]

	def setattr(self, name, value):
		if name == '.cname':
			if self.channel.name != value and \
			   self.editmgr.context.getchannel(value):
			    windowinterface.showmessage('Duplicate channel name (not changed)')
			    return
			self.editmgr.setchannelname(self.channel.name, value)
		else:
			self.editmgr.setchannelattr( \
				  self.channel.name, name, value)

	def delattr(self, name):
		if name == '.cname':
			pass
			# Don't do this:
			# self.editmgr.setchannelname(self.channel.name, '')
		else:
			self.editmgr.setchannelattr( \
				  self.channel.name, name, None)

	def delete(self):
		editmgr = self.editmgr
		if not editmgr.transaction():
			return # Not possible at this time
		editmgr.delchannel(self.channel.name)
		editmgr.commit()
	#
	# Return a list of attribute names that make sense for this channel,
	# in an order that makes sense to the user.
	#
	def attrnames(self):
		namelist = ['.cname', 'type', 'title', 'comment']
		ctype = self.channel.get('type', 'unknown')
		if ChannelMap.channelmap.has_key(ctype):
			cclass = ChannelMap.channelmap[ctype]
			# Add the class's declaration of attributes
			namelist = namelist + cclass.chan_attrs
			# And, for CMIF, add attributes that nodes inherit
			# from channel
			if cmifmode():
				for name in cclass.node_attrs:
					if name in namelist: continue
					defn = MMAttrdefs.getdef(name)
					if defn[5] == 'channel':
						namelist.append(name)
##			else:
##				# XXXX hack to get bgcolor included
##				namelist.append('bgcolor')
		# Merge in nonstandard attributes
		extras = []
		for name in self.channel.keys():
			if name not in namelist and \
				    MMAttrdefs.getdef(name)[3] <> 'hidden':
				extras.append(name)
		extras.sort()
		rv = namelist + extras
		# Remove some attributes if we are a base window, or if
		# we're in SMIL mode.
		base = self.channel.get('base_window')
		if base is None:
			if 'z' in rv: rv.remove('z')
			if 'base_winoff' in rv: rv.remove('base_winoff')
			if 'units' in rv: rv.remove('units')
			if 'transparent' in rv: rv.remove('transparent')
##		if not cmifmode():
##			if 'file' in rv: rv.remove('file')
##			if 'scale' in rv: rv.remove('scale')
		if ctype == 'layout' and not cmifmode():
			rv.remove('type')
		return rv
	#
	# Override three methods from Wrapper to fake channel name attribute
	#
	def getdef(self, name):
		if name == '.cname':
			# Channelname -- special case
			return (('name', ''), 'none',
				'Channel name', 'default',
				'Channel name', 'raw', 'light')
		return MMAttrdefs.getdef(name)

	def valuerepr(self, name, value):
		if name == '.cname': name = 'name'
		return MMAttrdefs.valuerepr(name, value)

	def parsevalue(self, name, str):
		if name == '.cname': name = 'name'
		return MMAttrdefs.parsevalue(name, str, self.context)



class DocumentWrapper(Wrapper):
	__stdnames = ['title', 'author', 'copyright', 'base', 
			'project_ftp_host', 'project_ftp_user', 'project_ftp_dir',
			'project_ftp_host_media', 'project_ftp_user_media', 'project_ftp_dir_media',
			'project_html_page', 'project_smil_url']

	def __init__(self, toplevel):
		Wrapper.__init__(self, toplevel, toplevel.context)

	def __repr__(self):
		return '<DocumentWrapper instance, file=%s>' % self.toplevel.filename

	def close(self):
		del self.toplevel.attreditor
		Wrapper.close(self)

	def stillvalid(self):
		return self.toplevel in self.toplevel.main.tops

	def maketitle(self):
		import MMurl
		basename = MMurl.unquote(self.toplevel.basename)
		return 'Properties of document %s' % basename

	def getattr(self, name):	# Return the attribute or a default
		return self.getvalue() or ''

	def getvalue(self, name):	# Return the raw attribute or None
		if name == 'title':
			return self.context.title or None
		if name == 'base':
			return self.context.baseurl or None
		if self.context.attributes.has_key(name):
			return self.context.attributes[name]
		return None		# unrecognized

	def getdefault(self, name):
		return ''

	def setattr(self, name, value):
		if name == 'title':
			self.context.title = value
		elif name == 'base':
			self.context.setbaseurl(value)
		else:
			self.context.attributes[name] = value

	def delattr(self, name):
		if name == 'title':
			self.context.title = None
		elif name == 'base':
			self.context.setbaseurl(None)
		elif self.context.attributes.has_key(name):
			del self.context.attributes[name]

	def delete(self):
		# shouldn't be called...
		pass

	def attrnames(self):
		attrs = self.context.attributes
		names = attrs.keys()
		for name in self.__stdnames:
			if attrs.has_key(name):
				names.remove(name)
		names.sort()
		return self.__stdnames + names

	def valuerepr(self, name, value):
		if name in ('title', 'base'):
			return MMAttrdefs.valuerepr(name, value)
		else:
			return value

	def parsevalue(self, name, str):
		if name in ('title', 'base'):
			return MMAttrdefs.parsevalue(name, str, self.context)
		else:
			return str


# Attribute editor class.

from AttrEditDialog import AttrEditorDialog, AttrEditorDialogField

class AttrEditor(AttrEditorDialog):
	def __init__(self, wrapper, new = 0):
		self.__new = new
		self.wrapper = wrapper
		wrapper.register(self)
		self.__open_dialog()

	def __open_dialog(self):
		import settings
		wrapper = self.wrapper
		list = []
		allnamelist = wrapper.attrnames()
		namelist = []
		lightweight = settings.get('lightweight')
		if not lightweight:
			cmif = settings.get('cmif')
		else:
			cmif = 0
		for name in allnamelist:
			flags = wrapper.getdef(name)[6]
			if flags != 'light':
				if lightweight or \
				   (not cmif and flags == 'cmif'):
					continue
			namelist.append(name)
		self.__namelist = namelist
		for i in range(len(namelist)):
			name = namelist[i]
			typedef, defaultvalue, labeltext, displayername, \
				 helptext, inheritance, flags = \
				 wrapper.getdef(name)
			type = typedef[0]
			if displayername == 'file':
				C = FileAttrEditorField
			elif displayername == 'font':
				C = FontAttrEditorField
			elif displayername == 'color':
				C = ColorAttrEditorField
			elif displayername == 'layoutname':
				C = LayoutnameAttrEditorField
			elif displayername == 'channelname':
				C = ChannelnameAttrEditorField
			elif displayername == 'captionchannelname':
				C = CaptionChannelnameAttrEditorField
			elif displayername == 'basechannelname':
				C = BaseChannelnameAttrEditorField
			elif displayername == 'childnodename':
				C = ChildnodenameAttrEditorField
			elif displayername == 'channeltype':
				C = ChanneltypeAttrEditorField
			elif displayername == 'units':
				C = UnitsAttrEditorField
			elif displayername == 'termnodename':
				C = TermnodenameAttrEditorField
			elif displayername == 'transparency':
				C = TransparencyAttrEditorField
			elif displayername == 'usergroup':
				C = UsergroupAttrEditorField
			elif displayername == 'transition':
				C = TransitionAttrEditorField
			elif displayername == 'direction':
				C = WipeDirectionAttrEditorField
			elif displayername == 'wipetype':
				C = WipeTypeAttrEditorField
			elif displayername == 'subregionanchor':
				C = AnchorTypeAttrEditorField
			elif displayername == 'targets':
				C = RMTargetsAttrEditorField
			elif displayername == 'audiotype':
				C = RMAudioAttrEditorField
			elif displayername == 'videotype':
				C = RMVideoAttrEditorField
			elif displayername == 'nodetype':
				C = NodeTypeAttrEditorField
			elif displayername == 'text':
				C = TextAttrEditorField
			elif displayername == 'bool3':
				C = Bool3AttrEditorField
			elif type == 'bool':
				C = BoolAttrEditorField
			elif type == 'name':
				C = NameAttrEditorField
			elif type == 'string':
				C = StringAttrEditorField
			elif type == 'int':
				C = IntAttrEditorField
			elif type == 'float':
				C = FloatAttrEditorField
			elif type == 'tuple':
				C = TupleAttrEditorField
			else:
				C = AttrEditorField
			b = C(self, name, labeltext or name)
			list.append(b)
		self.attrlist = list
		AttrEditorDialog.__init__(self, wrapper.maketitle(), list)

	def resetall(self):
		for b in self.attrlist:
			b.reset_callback()

	def restore_callback(self):
		for b in self.attrlist:
			b.setvalue(b.valuerepr(None))

	def close(self):
		AttrEditorDialog.close(self)
		for b in self.attrlist:
			b.close()
		self.wrapper.unregister(self)
		if self.__new:
			self.wrapper.delete()
		self.wrapper.close()
		del self.attrlist
		del self.wrapper

	def cancel_callback(self):
		self.close()

	def ok_callback(self):
		if not self.apply_callback():
			self.close()

	def apply_callback(self):
		self.__new = 0
		# first collect all changes
		dict = {}
		for b in self.attrlist:
			name = b.getname()
			str = b.getvalue()
			if str != b.getcurrent():
				try:
					value = b.parsevalue(str)
				except:
					typedef = self.wrapper.getdef(name)[0]
					exp = typedef[0]
					if exp == 'tuple':
						exp = 'tuple of'
						for e in typedef[1]:
							exp = exp + ' ' + e[0]
					if exp[0] in 'aeiou':
						n = 'n'
					else:
						n = ''
					if name == 'duration' or name == 'loop':
						exp = exp + " or `indefinite'"
					self.showmessage('%s: value should be a%s %s' % (b.getlabel(), n, exp), mtype = 'error')
					return 1
				dict[name] = value
		if not dict:
			# nothing to change
			return
		if not self.wrapper.transaction():
			# can't do a transaction
			return 1
		# this may take a while...
		self.wrapper.toplevel.setwaiting()
		for name, value in dict.items():
			self.wrapper.delattr(name)
			if value is not None:
				self.wrapper.setattr(name, value)
		self.wrapper.commit()

	#
	# EditMgr interface
	#
	def transaction(self):
		return 1

	def commit(self):
		if not self.wrapper.stillvalid():
			self.close()
		else:
			namelist = self.wrapper.attrnames()
			if namelist != self.__namelist:
				# re-open with possibly different size
				AttrEditorDialog.close(self)
				for b in self.attrlist:
					b.close()
				del self.attrlist
				self.__open_dialog()
			else:
##				self.fixvalues()
				self.resetall()
				self.settitle(self.wrapper.maketitle())

	def rollback(self):
		pass

	def kill(self):
		self.close()

class AttrEditorField(AttrEditorDialogField):
	type = 'string'

	def __init__(self, attreditor, name, label):
		self.__name = name
		self.label = label
		self.attreditor = attreditor
		self.wrapper = attreditor.wrapper
		self.__attrdef = self.wrapper.getdef(name)

	def __repr__(self):
		return '<%s instance, name=%s>' % (self.__class__.__name__,
						   self.__name)

	def close(self):
		AttrEditorDialogField.close(self)
		del self.attreditor
		del self.wrapper
		del self.__attrdef

	def getname(self):
		return self.__name

	def gettype(self):
		return self.type

	def getlabel(self):
		return self.label

	def gethelptext(self):
		return '%s\ndefault: %s' % (self.__attrdef[4], self.getdefault())
##		return 'atribute: %s\n' \
##		       'default: %s\n' \
##		       '%s' % (self.__name, self.getdefault(),
##			       self.__attrdef[4])

	def gethelpdata(self):
		return self.__name, self.getdefault(), self.__attrdef[4]

	def getcurrent(self):
		return self.valuerepr(self.wrapper.getvalue(self.__name))

	def getdefault(self):
		return self.valuerepr(self.wrapper.getdefault(self.__name))

	def valuerepr(self, value):
		"""Return string representation of value."""
		if value is None:
			return ''
		return self.wrapper.valuerepr(self.__name, value)

	def parsevalue(self, str):
		"""Return internal representation of string."""
		if str == '':
			return None
		return self.wrapper.parsevalue(self.__name, str)

	def reset_callback(self):
		self.setvalue(self.getcurrent())

	def help_callback(self):
		windowinterface.showmessage(self.gethelptext())

class IntAttrEditorField(AttrEditorField):
	type = 'int'

	def valuerepr(self, value):
		if value == 0 and self.getname() == 'loop':
			return 'indefinite'
		return AttrEditorField.valuerepr(self, value)

	def parsevalue(self, str):
		if str == 'indefinite' and self.getname() == 'loop':
			return 0
		return AttrEditorField.parsevalue(self, str)

class FloatAttrEditorField(AttrEditorField):
	type = 'float'

	def valuerepr(self, value):
		if value == -1 and self.getname() == 'duration':
			return 'indefinite'
		return AttrEditorField.valuerepr(self, value)

	def parsevalue(self, str):
		if str == 'indefinite' and self.getname() == 'duration':
			return -1.0
		return AttrEditorField.parsevalue(self, str)

class StringAttrEditorField(AttrEditorField):
	def valuerepr(self, value):
		"""Return string representation of value."""
		if value is None:
			return ''
		return value

	def parsevalue(self, str):
		"""Return internal representation of string."""
		if str == '':
			return None
		return str

class NameAttrEditorField(StringAttrEditorField):
	pass

class FileAttrEditorField(StringAttrEditorField):
	type = 'file'

	def browser_callback(self):
		import os, MMurl, urlparse
		cwd = self.wrapper.toplevel.dirname
		if cwd:
			cwd = MMurl.url2pathname(cwd)
			if not os.path.isabs(cwd):
				cwd = os.path.join(os.getcwd(), cwd)
		else:
			cwd = os.getcwd()
		url = self.getvalue()
		if url == '' or url == '/dev/null':
			dir, file = cwd, ''
		else:
			node = self.wrapper.node
			url = node.GetContext().findurl(url)
			utype, host, path, params, query, fragment = urlparse.urlparse(url)
			if (utype and utype != 'file') or \
			   (host and host != 'localhost'):
				dir, file = cwd, ''
			else:
				file = MMurl.url2pathname(path)
				file = os.path.join(cwd, file)
				if os.path.isdir(file):
					dir, file = file, ''
				else:
					dir, file = os.path.split(file)
		windowinterface.FileDialog('Choose File for ' + self.label,
					   dir, '*', file, self.__ok_cb, None,
					   existing=1)

	def __ok_cb(self, pathname):
		import MMurl, os
		if os.path.isabs(pathname):
			cwd = self.wrapper.toplevel.dirname
			if cwd:
				cwd = MMurl.url2pathname(cwd)
				if not os.path.isabs(cwd):
					cwd = os.path.join(os.getcwd(), cwd)
			else:
				cwd = os.getcwd()
			if os.path.isdir(pathname):
				dir, file = pathname, os.curdir
			else:
				dir, file = os.path.split(pathname)
			# XXXX maybe should check that dir gets shorter!
			while len(dir) > len(cwd):
				dir, f = os.path.split(dir)
				file = os.path.join(f, file)
			if dir == cwd:
				pathname = file
		url = MMurl.pathname2url(pathname)
		self.setvalue(url)
		if self.wrapper.__class__ is SlideWrapper and url:
			import HierarchyView
			node = self.wrapper.node
			pnode = node.GetParent()
			start, minstart = HierarchyView.slidestart(pnode, url, pnode.children.index(node))
			for b in self.attreditor.attrlist:
				if b.getname() == 'start':
					str = b.getvalue()
					try:
						value = b.parsevalue(str) or 0
					except:
						value = 0
					if minstart - start > value:
						b.setvalue(b.valuerepr(minstart-start))
					break

class TextAttrEditorField(AttrEditorField):
	type = 'text'

	def valuerepr(self, value):
		"""Return string representation of value."""
		if value is None:
			return ''
		return string.join(value, '\n')

	def parsevalue(self, str):
		"""Return internal representation of string."""
		if str == '':
			return None
		return string.split(str, '\n')

class TupleAttrEditorField(AttrEditorField):
	type = 'tuple'

	def valuerepr(self, value):
		if type(value) is type(''):
			return value
		return AttrEditorField.valuerepr(self, value)

from colors import colors
class ColorAttrEditorField(TupleAttrEditorField):
	type = 'color'
	def parsevalue(self, str):
		str = string.lower(string.strip(str))
		if colors.has_key(str):
			return colors[str]
		if str[:1] == '#':
			rgb = []
			if len(str) == 4:
				for i in range(1, 4):
					rgb.append(string.atoi(str[i], 16) * 16)
			elif len(str) == 7:
				for i in range(1, 7, 2):
					rgb.append(string.atoi(str[i:i+2], 16))
			elif len(str) == 13:
				for i in range(1, 13, 4):
					rgb.append(string.atoi(str[i:i+4], 16)/256)
			else:
				raise RuntimeError, 'Bad color specification'
			str = ''
			for c in rgb:
				str = str + ' ' + `c`
		return TupleAttrEditorField.parsevalue(self, str)

	def valuerepr(self, value):
		for name, rgb in colors.items():
			if value == rgb:
				return name
		return TupleAttrEditorField.valuerepr(self, value)

class PopupAttrEditorField(AttrEditorField):
	# A choice menu choosing from a list -- base class only
	type = 'option'

	def getoptions(self):
		# derived class overrides this to defince the choices
		return ['Default']

	def parsevalue(self, str):
		if str == 'Default':
			return None
		return str

	def valuerepr(self, value):
		if value is None:
			return 'Default'
		return value

class PopupAttrEditorFieldWithUndefined(PopupAttrEditorField):
	# This class differs from the one above in that when a value
	# does not occur in the list of options, valuerepr will return
	# 'undefined'.

	def getoptions(self):
		# derived class overrides this to defince the choices
		return ['Default', 'undefined']

	def valuerepr(self, value):
		if value is None:
			return 'Default'
		options = self.getoptions()
		if value not in options:
			return 'undefined'
		return value

	def reset_callback(self):
		self.recalcoptions()

class BoolAttrEditorField(PopupAttrEditorField):
	__offon = ['off', 'on']

	def parsevalue(self, str):
		return self.__offon.index(str)

	def valuerepr(self, value):
		return self.__offon[value]

	def getoptions(self):
		return self.__offon

	def getcurrent(self):
		val = self.wrapper.getvalue(self.getname())
		if val is None:
			return self.getdefault()
		return self.valuerepr(val)

class Bool3AttrEditorField(PopupAttrEditorField):
	__offon = ['off', 'on']

	def parsevalue(self, str):
		if str == 'Not set':
			return None
		return self.__offon.index(str)

	def valuerepr(self, value):
		if value is None:
			return 'Not set'
		return self.__offon[value]

	def getoptions(self):
		return ['Not set'] + self.__offon

class UnitsAttrEditorField(PopupAttrEditorField):
	__values = ['mm', 'relative', 'pixels']
	__valuesmap = [windowinterface.UNIT_MM, windowinterface.UNIT_SCREEN,
		       windowinterface.UNIT_PXL]

	# Choose from a list of unit types
	def getoptions(self):
		return ['Default'] + self.__values

	def parsevalue(self, str):
		if str == 'Default':
			return None
		return self.__valuesmap[self.__values.index(str)]

	def valuerepr(self, value):
		if value is None:
			return 'Default'
		return self.__values[self.__valuesmap.index(value)]

class TransitionAttrEditorField(PopupAttrEditorField):
	__values = ['fill', 'fadein', 'fadeout', 'crossfade', 'wipe', 'viewchange']

	def getoptions(self):
		return ['Default'] + self.__values

class WipeDirectionAttrEditorField(PopupAttrEditorField):
	__values = ['left', 'right', 'up', 'down']

	def getoptions(self):
		return ['Default'] + self.__values

class WipeTypeAttrEditorField(PopupAttrEditorField):
	__values = ['normal', 'push']

	def getoptions(self):
		return ['Default'] + self.__values

class AnchorTypeAttrEditorField(PopupAttrEditorField):
	__values = ['top-left', 'top-center', 'top-right',
		    'center-left', 'center', 'center-right',
		    'bottom-left', 'bottom-center', 'bottom-right']

	def getoptions(self):
		return ['Default'] + self.__values

class TransparencyAttrEditorField(PopupAttrEditorField):
	__values = ['never', 'when empty', 'always']
	__valuesmap = [0, -1, 1]

	# Choose from a list of unit types
	def getoptions(self):
		return ['Default'] + self.__values

	def parsevalue(self, str):
		if str == 'Default':
			return None
		return self.__valuesmap[self.__values.index(str)]

	def valuerepr(self, value):
		if value is None:
			return 'Default'
		return self.__values[self.__valuesmap.index(value)]

class RMTargetsAttrEditorField(PopupAttrEditorField):
	# Note: these values come from the producer module, but we don't want to import
	# that here
	__values = ['28k8 modem', '56k modem', 
		'Single ISDN', 'Double ISDN', 'Cable modem', 'LAN']

	# Choose from a list of unit types
	def getoptions(self):
##		return ['Default'] + self.__values
		return self.__values

	def parsevalue(self, str):
		if str == 'Default':
			str = '28k8 modem,56k modem'
		strs = string.split(str, ',')
		rv = 0
		for str in strs:
			rv = rv | (1 << self.__values.index(str))
		return rv

	def valuerepr(self, value):
		if value is None:
			value = 3	# '28k8 modem,56k modem'
		str = self.__values[0]	# XXX use lowest as default
		# XXX just the last one for now
		strs = []
		for i in range(len(self.__values)):
			if value & (1 << i):
				strs.append(self.__values[i])
		str = string.join(strs, ',')
		return str

class RMAudioAttrEditorField(PopupAttrEditorField):
	__values = ['Voice', 'Voice and background music', 'Music (mono)', 'Music (stereo)']
	__valuesmap = [0, 1, 2, 3]

	# Choose from a list of unit types
	def getoptions(self):
##		return ['Default'] + self.__values
		return self.__values

	def parsevalue(self, str):
		if str == 'Default':
			return None
		return self.__valuesmap[self.__values.index(str)]

	def valuerepr(self, value):
		if value is None:
			return 'Default'
		return self.__values[self.__valuesmap.index(value)]

class RMVideoAttrEditorField(PopupAttrEditorField):
	__values = ['Normal quality', 'Smoother motion', 'Sharper pictures', 'Slideshow']
	__valuesmap = [0, 1, 2, 3]

	# Choose from a list of unit types
	def getoptions(self):
##		return ['Default'] + self.__values
		return self.__values

	def parsevalue(self, str):
		if str == 'Default':
			return None
		return self.__valuesmap[self.__values.index(str)]

	def valuerepr(self, value):
		if value is None:
			return 'Default'
		return self.__values[self.__valuesmap.index(value)]

class LayoutnameAttrEditorField(PopupAttrEditorFieldWithUndefined):
	# Choose from the current layout names
	def getoptions(self):
		list = self.wrapper.context.layouts.keys()
		list.sort()
		return ['Default', 'undefined'] + list

class ChannelnameAttrEditorField(PopupAttrEditorFieldWithUndefined):
	# Choose from the current channel names
	def getoptions(self):
		import settings
		list = []
		ctx = self.wrapper.context
		if settings.get('lightweight'):
			ch = self.wrapper.node.GetContext().getchannel(self.wrapper.getvalue(self.getname()))
			if ch is not None:
				chtype = ch.get('type')
			else:
				chtype = None
			chlist = ctx.compatchannels(None, chtype)
			chlist.sort()
			if not chlist and not chtype:
				chlist = ctx.channelnames[:]
				chlist.sort()
				chlist = ['undefined', None] + chlist
			return chlist or ['undefined']
		for name in ctx.channelnames:
			if ctx.channeldict[name].attrdict['type'] != 'layout':
				list.append(name)
		list.sort()
		return ['Default', 'undefined'] + list

	def channelprops(self):
		ch = self.wrapper.context.getchannel(self.getvalue())
		if ch is not None:
			showchannelattreditor(self.wrapper.toplevel, ch)

class CaptionChannelnameAttrEditorField(PopupAttrEditorFieldWithUndefined):
	# Choose from the current RealText channel names
	__nocaptions = 'No captions'

	def getoptions(self):
		import settings
		list = []
		ctx = self.wrapper.context
		chlist = ctx.compatchannels(None, 'RealText')
		chlist.sort()
		return [self.__nocaptions] + chlist

	def parsevalue(self, str):
		if str == self.__nocaptions:
			return None
		return str

	def valuerepr(self, value):
		if value is None:
			return self.__nocaptions
		return value

class BaseChannelnameAttrEditorField(ChannelnameAttrEditorField):
	# Choose from the current channel names
	def getoptions(self):
		list = []
		ctx = self.wrapper.context
		chname = self.wrapper.channel.name
		for name in ctx.channelnames:
			if name == chname:
				continue
			ch = ctx.channeldict[name]
##			if ch.attrdict['type'] == 'layout':
			list.append(name)
		list.sort()
		return ['Default', 'undefined'] + list

class UsergroupAttrEditorField(PopupAttrEditorFieldWithUndefined):
	def getoptions(self):
		list = self.wrapper.context.usergroups.keys()
		list.sort()
		return ['Default', 'undefined'] + list

class ChildnodenameAttrEditorField(PopupAttrEditorFieldWithUndefined):
	# Choose from the node's children
	def getoptions(self):
		list = []
		for child in self.wrapper.node.GetChildren():
			try:
				list.append(child.GetAttr('name'))
			except NoSuchAttrError:
				pass
		list.sort()
		return ['Default', 'undefined'] + list

class TermnodenameAttrEditorField(PopupAttrEditorFieldWithUndefined):
	# Choose from the node's children or the values LAST or FIRST
	def getoptions(self):
		list = []
		for child in self.wrapper.node.GetChildren():
			try:
				list.append(child.GetAttr('name'))
			except NoSuchAttrError:
				pass
		list.sort()
		return ['Default', 'LAST', 'FIRST'] + list

class ChanneltypeAttrEditorField(PopupAttrEditorField):
	# Choose from the standard channel types
	def getoptions(self):
		return ['Default'] + ChannelMap.getvalidchanneltypes()

class FontAttrEditorField(PopupAttrEditorField):
	# Choose from all possible font names
	def getoptions(self):
		fonts = windowinterface.fonts[:]
		fonts.sort()
		return ['Default'] + fonts

Alltypes = alltypes[:]
Alltypes[Alltypes.index('bag')] = 'choice'
Alltypes[Alltypes.index('alt')] = 'switch'
class NodeTypeAttrEditorField(PopupAttrEditorField):
	def getoptions(self):
		if cmifmode():
			options = Alltypes[:]
		else:
			options = Alltypes[:]
			options.remove('choice')
		ntype = self.wrapper.node.GetType()
		if ntype in interiortypes:
			if self.wrapper.node.GetChildren():
				options.remove('imm')
				options.remove('ext')
		elif ntype == 'imm' and self.wrapper.node.GetValues():
			options = ['imm']
		return options

	def parsevalue(self, str):
		if str == 'choice':
			return 'bag'
		if str == 'switch':
			return 'alt'
		return str

	def valuerepr(self, value):
		if value is 'bag':
			return 'choice'
		if value is 'alt':
			return 'switch'
		return value
