# Attribute editor using the FORMS library (fl, FL), based upon Dialog.


import gl
import fl
from FL import *

import MMExc
import MMAttrdefs
import MMParser
import MMWrite
from MMNode import alltypes, leaftypes, interiortypes

from ChannelMap import channelmap

from Dialog import Dialog


# There are two basic calls into this module (but see below for more):
# showattreditor(node) creates an attribute editor form for a node
# and hideattreditor(node) hides it again.  Since the editor may also
# hide itself, spurious hide calls are ignored; also, only one attribute
# editor is allowed per node, and extra show calls are also ignored
# (actually, this pops up the window, to draw the user's attention...).

def showattreditor(node):
	try:
		attreditor = node.attreditor
	except NameError:
		attreditor = AttrEditor().init(NodeWrapper().init(node))
		node.attreditor = attreditor
	except AttributeError: # new style exceptions
		attreditor = AttrEditor().init(NodeWrapper().init(node))
		node.attreditor = attreditor
	attreditor.open()


def hideattreditor(node):
	try:
		attreditor = node.attreditor
	except NameError:
		return # No attribute editor active
	except AttributeError:
		return # No attribute editor active (new style exceptions)
	attreditor.hide()


# An additional call to check whether the attribute editor is currently
# active for a node (so the caller can put up a warning "you are already
# editing this node's attributes" instead of just silence).

def hasattreditor(node):
	try:
		attreditor = node.attreditor
	except NameError:
		return 0 # No attribute editor active
	except AttributeError:
		return 0 # No attribute editor active (new style exceptions)
	return attreditor.is_showing()


# A similar interface for channels (note different arguments!).
# The administration is kept in context.channelattreditors,
# which is created here if necessary.

def showchannelattreditor(context, name):
	try:
		dict = context.channelattreditors
	except NameError:
		dict = context.channelattreditors = {}
	except AttributeError: # new style exceptions
		dict = context.channelattreditors = {}
	if dict.has_key(name):
		editor = dict[name]
		wrapper = editor.wrapper
		if wrapper.name <> name:
			editor.hide()
			del dict[name]
	if not dict.has_key(name):
		dict[name] = \
			AttrEditor().init(ChannelWrapper().init(context, name))
	dict[name].open()

def hidechannelattreditor(context, name):
	try:
		dict = context.channelattreditors
	except NameError:
		return
	except AttributeError: # new style exceptions
		return
	if not dict.has_key(name):
		return
	dict[name].hide()

def haschannelattreditor(context, name):
	try:
		dict = context.channelattreditors
	except NameError:
		return 0
	except AttributeError: # new style exceptions
		return 0
	if not dict.has_key(name):
		return 0
	return dict[name].is_showing()


# And again a similar interface for styles.
# The administration is kept in context.styleattreditors,
# which is created here if necessary.

def showstyleattreditor(context, name):
	try:
		dict = context.styleattreditors
	except NameError:
		dict = context.styleattreditors = {}
	except AttributeError: # new style exceptions
		dict = context.styleattreditors = {}
	if not dict.has_key(name):
		dict[name] = \
			AttrEditor().init(StyleWrapper().init(context, name))
	dict[name].open()

def hidestyleattreditor(context, name):
	try:
		dict = context.styleattreditors
	except NameError:
		return
	except AttributeError: # new style exceptions
		return
	if not dict.has_key(name):
		return
	dict[name].hide()

def hasstyleattreditor(context, name):
	try:
		dict = context.styleattreditors
	except NameError:
		return 0
	except AttributeError: # new style exceptions
		return 0
	if not dict.has_key(name):
		return 0
	return dict[name].is_showing()


# The "Wrapper" classes encapsulate the differences between attribute
# editors for nodes and channels.  If you want editors for other
# attribute collections (styles!) you may want to new wrappers.
# All wrappers should support the methods shown here; the init()
# method can have different arguments since it is only called from
# the show*() function.  (When introducing a style attr editor
# it should probably be merged with the class attr editor, using
# a common base class implementing most functions.)

class Wrapper: # Base class -- common operations
	def init(self):
		return self
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
	#
	def getdef(self, name):
		return MMAttrdefs.getdef(name)
	def valuerepr(self, (name, value)):
		return MMAttrdefs.valuerepr(name, value)
	def parsevalue(self, (name, string)):
		return MMAttrdefs.parsevalue(name, string, self.context)

class NodeWrapper(Wrapper):
	#
	def init(self, node):
		self.node = node
		self.context = node.GetContext()
		self.editmgr = self.context.geteditmgr()
		self.root = node.GetRoot()
		return Wrapper.init(self)
	#
	def stillvalid(self):
		return self.node.GetRoot() is self.root
	#
	def maketitle(self):
		name = MMAttrdefs.getattr(self.node, 'name')
		return 'Attributes for node: ' + name
	#
	def getattr(self, name): # Return the attribute or a default
		return MMAttrdefs.getattr(self.node, name)
	#
	def getvalue(self, name): # Return the raw attribute or None
		return self.node.GetRawAttrDef(name, None)
	#
	def getdefault(self, name): # Return the default or None
		return MMAttrdefs.getdefattr(self.node, name)
	#
	def setattr(self, (name, value)):
		self.editmgr.setnodeattr(self.node, name, value)
	#
	def delattr(self, name):
		self.editmgr.setnodeattr(self.node, name, None)
	#
	# Return a list of attribute names that make sense for this node,
	# in an order that makes sense to the user.
	#
	def attrnames(self):
		namelist = ['name', 'channel', 'closed', 'comment']
		if self.node.GetType() == 'bag':
			namelist.append('bag_index')
		try:
			# Get the channel class (should be a subroutine!)
			cname = MMAttrdefs.getattr(self.node, 'channel')
			cattrs = self.context.channeldict[cname]
			ctype = cattrs['type']
			cclass = channelmap[ctype]
			# Add the class's declaration of attributes
			namelist = namelist + cclass.node_attrs
			for name in cclass.chan_attrs:
				if name in namelist: continue
				if MMAttrdefs.getdef(name)[5] == 'channel':
					namelist.append(name)
			for name in cclass.node_attrs:
				if name in namelist: continue
				namelist.append(name)
		except: # XXX be more specific!
			pass # Ignore errors in the above
		# Merge in nonstandard attributes (except synctolist!)
		extras = []
		for name in self.node.GetAttrDict().keys():
			if name not in namelist and name <> 'synctolist':
				extras.append(name)
		extras.sort()
		return namelist + extras
	#


class ChannelWrapper(Wrapper):
	#
	def init(self, (context, name)):
		self.context = context
		self.editmgr = context.geteditmgr()
		self.name = name
		self.attrdict = self.context.channeldict[name]
		return Wrapper.init(self)
	#
	def stillvalid(self):
		return self.context.channeldict.has_key(self.name) and \
			self.context.channeldict[self.name] == self.attrdict
	#
	def maketitle(self):
		return 'Attributes for channel: ' + self.name
	#
	def getattr(self, name):
		if name == '.cname': return self.name
		if self.attrdict.has_key(name):
			return self.attrdict[name]
		else:
			return MMAttrdefs.getdef(name)[1]
	#
	def getvalue(self, name): # Return the raw attribute or None
		if name == '.cname': return self.name
		if self.attrdict.has_key(name):
			return self.attrdict[name]
		else:
			return None
	#
	def getdefault(self, name): # Return the default or None
		return MMAttrdefs.getdef(name)[1]
	#
	def setattr(self, (name, value)):
		if name == '.cname':
			self.editmgr.setchannelname(self.name, value)
			self.change_channel_name(self.editmgr.root, \
						self.name, value)
			# XXX Should also patch styles?
			self.name = value
		else:
			self.editmgr.setchannelattr(self.name, name, value)
	#
	def delattr(self, name):
		if name == '.cname':
			self.editmgr.setchannelname(self.name, 'none')
		else:
			self.editmgr.setchannelattr(self.name, name, None)
	#
	# Return a list of attribute names that make sense for this channel,
	# in an order that makes sense to the user.
	#
	def attrnames(self):
		namelist = ['.cname', 'type', 'comment']
		try:
			ctype = self.attrdict['type']
			cclass = channelmap[ctype]
			# Add the class's declaration of attributes
			namelist = namelist + cclass.chan_attrs
			for name in cclass.node_attrs:
				if name in namelist: continue
				if MMAttrdefs.getdef(name)[5] == 'channel':
					namelist.append(name)
		except: # XXX be more specific!
			pass # Ignore errors in the above
		# Merge in nonstandard attributes
		extras = []
		for name in self.attrdict.keys():
			if name not in namelist:
				extras.append(name)
		extras.sort()
		return namelist + extras
	#
	# Override three methods from Wrapper to fake channel name attribute
	#
	def getdef(self, name):
		if name == '.cname':
			# Channelname -- special case
			return (('name', ''), 'none', \
				'Channel name', 'default', \
				'Channel name (not a real attribute)', 'raw')
		return MMAttrdefs.getdef(name)
	#
	def valuerepr(self, (name, value)):
		if name == '.cname': name = 'name'
		return MMAttrdefs.valuerepr(name, value)
	#
	def parsevalue(self, (name, string)):
		if name == '.cname': name = 'name'
		return MMAttrdefs.parsevalue(name, string, self.context)
	#
	def change_channel_name(self, (node, oldname, newname)):
		try:
			cname = node.GetRawAttr('channel')
		except MMExc.NoSuchAttrError:
			cname = None
		if cname == oldname:
			self.editmgr.setnodeattr(node, 'channel', newname)
		if node.GetType() in interiortypes:
			for c in node.GetChildren():
				self.change_channel_name(c, oldname, newname)


class StyleWrapper(Wrapper):
	#
	def init(self, (context, name)):
		self.context = context
		self.editmgr = context.geteditmgr()
		self.name = name
		self.attrdict = self.context.styledict[name]
		return Wrapper.init(self)
	#
	def stillvalid(self):
		return self.context.styledict.has_key(self.name) and \
			self.context.styledict[self.name] == self.attrdict
	#
	def maketitle(self):
		return 'Attributes for style: ' + self.name
	#
	def getattr(self, name):
		if self.attrdict.has_key(name):
			return self.attrdict[name]
		else:
			return MMAttrdefs.getdef(name)[1]
	#
	def getvalue(self, name): # Return the raw attribute or None
		if self.attrdict.has_key(name):
			return self.attrdict[name]
		else:
			return None
	#
	def getdefault(self, name): # Return the default or None
		return MMAttrdefs.getdef(name)[1]
	#
	def setattr(self, (name, value)):
		self.editmgr.setstyleattr(self.name, name, value)
	#
	def delattr(self, name):
		self.editmgr.setstyleattr(self.name, name, None)
	#
	# Return a list of attribute names that make sense for this style,
	# in an order that makes sense to the user.
	#
	def attrnames(self):
		namelist = ['type', 'channel', 'comment']
		try:
			# Get the channel class (should be a subroutine!)
			ctype = self.attrdict['type']
			cclass = channelmap[ctype]
			# Add the class's declaration of attributes
			for name in cclass.node_attrs + cclass.chan_attrs:
				if MMAttrdefs.getdef(name)[5] <> 'raw':
					namelist.append(name)
		except: # XXX be more specific!
			pass # Ignore errors in the above
		# Merge in nonstandard attributes
		extras = []
		for name in self.attrdict.keys():
			if name not in namelist:
				extras.append(name)
		extras.sort()
		return namelist + extras
	#


# Attribute editor class.

class AttrEditor(Dialog):
	#
	def init(self, wrapper):
		#
		self.wrapper = wrapper
		self.namelist = wrapper.attrnames()
		#
		self.changed = -1 # Neither 0 not 1
		#
		itemwidth = 450
		itemheight = 25
		#
		formwidth = itemwidth
		formheight = len(self.namelist) * itemheight + 30
		#
		title = self.wrapper.maketitle()
		hint = '[Click on labels for help]'
		#
		return Dialog.init(self, formwidth, formheight, title, hint)
	#
	def make_form(self):
		#
		itemwidth = 450
		itemheight = 25
		#
		formwidth = itemwidth
		formheight = len(self.namelist) * itemheight + 30
		#
		self.width, self.height = formwidth, formheight
		Dialog.make_form(self)
		#
		itemw3 = 50
		itemw2 = itemwidth/2
		itemw1 = itemwidth - itemw2 - itemw3
		#
		itemx1 = 0
		itemx2 = itemx1 + itemw1
		itemx3 = itemx2 + itemw2
		#
		form = self.form
		#
		self.blist = []
		#
		for i in range(len(self.namelist)):
			itemy = formheight - (i+1)*itemheight
			name = self.namelist[i]
			b = ButtonRow().init(self, name)
			b.makelabeltext(itemx1, itemy, itemw1, itemheight)
			b.makehelpbutton(itemx1, itemy, itemw1, itemheight)
			b.makevalueinput(itemx2, itemy, itemw2, itemheight)
			b.makeresetbutton(itemx3, itemy, itemw3, itemheight)
			self.blist.append(b)
	#
	def transaction(self):
		return 1
	#
	def commit(self):
		if not self.wrapper.stillvalid():
			self.hide()
		else:
			namelist = self.wrapper.attrnames()
			if namelist <> self.namelist:
				# re-open with possibly different size
				if self.is_showing():
					self.hide()
					self.open()
			else:
				self.fixvalues()
				self.settitle(self.wrapper.maketitle())
	#
	def rollback(self):
		pass
	#
	def kill(self):
		self.destroy()
	#
	def open(self):
		self.show()
	#
	def show(self):
		if self.is_showing():
			self.pop()
		else:
			namelist = self.wrapper.attrnames()
			if namelist <> self.namelist:
				del self.form
				self.namelist = namelist
				self.make_form()
				if self.last_geometry <> None:
					x, y, w, h = self.last_geometry
					self.last_geometry = x, y, 0, 0
			self.title = self.wrapper.maketitle()
			self.getvalues()
			self.wrapper.register(self)
			Dialog.show(self)
	#
	def hide(self):
		if self.showing:
			self.wrapper.unregister(self)
			Dialog.hide(self)
	#
	def setchanged(self, changed):
		if self.changed <> changed:
			self.changed = changed
			self.activate_buttons(self.changed)
	#
	def getvalues(self):
		self.form.freeze_form()
		for b in self.blist: b.getvalue()
		self.setchanged(0)
		self.form.unfreeze_form()
	#
	def setvalues(self, keep_open):
		if not self.wrapper.transaction():
			return
		if not keep_open:
			self.hide()
		self.form.freeze_form()
		for b in self.blist:
			b.setvalue()
		self.setchanged(0)
		self.wrapper.commit()
		self.form.unfreeze_form()
	#
	def fixvalues(self):
		self.fixfocus()
		self.form.freeze_form()
		for b in self.blist:
			b.fixvalue()
		self.form.unfreeze_form()
	#
	def cancel_callback(self, dummy):
		self.hide()
	#
	def restore_callback(self, (obj, arg)):
		obj.set_button(1)
		self.getvalues()
		obj.set_button(0)
	#
	def apply_callback(self, (obj, arg)):
		obj.set_button(1)
		self.fixfocus()
		if self.changed:
			self.setvalues(1)
		obj.set_button(0)
	#
	def ok_callback(self, (obj, arg)):
		obj.set_button(1)
		self.fixfocus()
		if not self.changed:
			self.hide()
		else:
			self.setvalues(0)
		obj.set_button(0)
	#
	def fixfocus(self):
		for b in self.blist:
			if b.value.focus:
				b.valuecallback(b.value, None)
	#


# Class for one attribute definitition.

# XXX Still to do: use type-specific objects for common cases,
# e.g.: on/off buttons for booleans, sliders for numbers (?),
# and input fields without quotes for strings.
# XXX The class has the wrong type of interface to do that!

class ButtonRow:
	#
	def init(b, (attreditor, name)):
		b.attreditor = attreditor
		b.name = name
		b.wrapper = attreditor.wrapper
		b.form = attreditor.form
		return b
	#
	def makelabeltext(b, (x, y, w, h)):
		attrdef = b.wrapper.getdef(b.name)
		labeltext = attrdef[2]
		if labeltext == '': labeltext = b.name
		b.label = b.form.add_text(NORMAL_TEXT, x, y, w-1, h, labeltext)
	#
	def makehelpbutton(b, (x, y, w, h)):
		b.help = b.form.add_button(HIDDEN_BUTTON, x, y, w-1, h, '')
		b.help.set_call_back(b.helpcallback, None)
	#
	def makevalueinput(b, (x, y, w, h)):
		b.value = b.form.add_input(NORMAL_INPUT, x, y, w-1, h, '')
		b.value.lstyle = FIXED_STYLE
		b.value.set_call_back(b.valuecallback, None)
	#
	def makeresetbutton(b, (x, y, w, h)):
		b.reset = b.form.add_button(PUSH_BUTTON, x, y, w-1, h, 'reset')
		b.reset.set_call_back(b.resetcallback, None)
	#
	def getvalue(b):
		value = b.wrapper.getvalue(b.name)
		default = b.wrapper.getdefault(b.name)
		b.defaultvalue = default
		if value == None:
			b.currentvalue = default
			b.isdefault = 1
		else:
			b.currentvalue = value
			b.isdefault = 0
		b.lastvalue = b.currentvalue
		b.changed = 0
		b.update()
	#
	def setvalue(b):
		if b.changed:
			if b.isdefault:
				b.wrapper.delattr(b.name)
			else:
				b.wrapper.setattr(b.name, b.currentvalue)
		b.changed = 0
		# b.update() # Don't -- commit will do that
	#
	def fixvalue(b):
		if not b.changed:
			b.getvalue()
		elif b.isdefault:
			b.currentvalue = b.wrapper.getdefault(b.name)
			b.update()
	#
	def helpcallback(b, dummy):
		attrdef = b.wrapper.getdef(b.name)
		fl.show_message('attribute: ' + b.name, \
			'default: ' + b.valuerepr(b.defaultvalue), attrdef[4])
	#
	def valuecallback(b, dummy):
		newtext = b.value.get_input()[:INPUT_MAX-1]
		if newtext == b.currenttext[:INPUT_MAX-1]:
			return # No change
		try:
			value = b.parsevalue(newtext)
		except (EOFError, MMExc.SyntaxError, MMExc.TypeError), msg:
			if type(msg) <> type(''):
				found, expected = msg
				if expected == ')':
					expected = ') or EOF'
				msg = 'found ' + `found` + \
					', expected ' + expected
			msg2 = 'for attribute ' + b.name
			fl.show_message('Syntax error', msg2, msg)
			b.update()
			return
		b.currentvalue = value
		b.isdefault = 0
		b.changed = 1
		b.attreditor.setchanged(1)
		b.update()
	#
	def resetcallback(b, dummy):
		b.isdefault = b.reset.get_button()
		if b.isdefault:
			b.lastvalue = b.currentvalue
			b.currentvalue = b.defaultvalue
		else:
			b.currentvalue = b.lastvalue
		b.changed = 1
		b.attreditor.setchanged(1)
		b.update()
	#
	def update(b):
		b.currenttext = b.valuerepr(b.currentvalue)
		b.value.set_input(b.currenttext[:INPUT_MAX-1])
		b.reset.set_button(b.isdefault)
		if b.isdefault and not b.changed:
			b.reset.hide_object()
		else:
			b.reset.freeze_object()
			if b.changed:
				b.reset.boxtype = UP_BOX
			else:
				b.reset.boxtype = FRAME_BOX
			b.reset.show_object()
			b.reset.unfreeze_object()
	#
	def valuerepr(b, value):
		return b.wrapper.valuerepr(b.name, value)
	#
	def parsevalue(b, string):
		return b.wrapper.parsevalue(b.name, string)
	#


# Routine to hide all attribute editors in a tree and its context.

def hideall(root):
	hidenode(root)
	context = root.GetContext()
	for cname in root.GetContext().channeldict.keys():
		hidechannelattreditor(context, cname)
	for cname in root.GetContext().styledict.keys():
		hidestyleattreditor(context, cname)


# Recursively hide the attribute editors for this node and its subtree.

def hidenode(node):
	hideattreditor(node)
	if node.GetType() in interiortypes:
		for child in node.GetChildren():
			hidenode(child)


# Test program -- edit the attributes of the root node.

def test():
	import sys, MMTree
	if sys.argv[1:]:
		filename = sys.argv[1]
	else:
		filename = 'demo.cmif'
	#
	print 'parsing', filename, '...'
	root = MMTree.ReadFile(filename)
	#
	print 'quit button ...'
	quitform = fl.make_form(FLAT_BOX, 50, 50)
	quitbutton = quitform.add_button(NORMAL_BUTTON, 0, 0, 50, 50, 'Quit')
	quitform.set_form_position(600, 10)
	quitform.show_form(PLACE_POSITION, FALSE, 'QUIT')
	#
	print 'showattreditor ...'
	showattreditor(root)
	#
	print 'go ...'
	while 1:
		obj = fl.do_forms()
		if obj == quitbutton:
			hideattreditor(root)
			break
		print 'This object should have a callback!', `obj.label`
