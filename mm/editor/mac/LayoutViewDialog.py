__version__ = "$Id$"

import windowinterface
from usercmd import *

ID_DIALOG_LAYOUT=526

ITEM_LAYOUT_LIST=4
ITEM_LAYOUT_NEW=5
ITEM_LAYOUT_RENAME=6
ITEM_LAYOUT_DELETE=7

ITEM_CHANNEL_LIST=8
ITEM_CHANNEL_NEW=9
ITEM_CHANNEL_REMOVE=10
ITEM_CHANNEL_ATTRS=11

ITEM_OCHANNEL_LIST=12
ITEM_OCHANNEL_ADD=13

ITEM_TO_COMMAND={
	ITEM_LAYOUT_NEW: NEW_LAYOUT,
	ITEM_LAYOUT_RENAME: RENAME,
	ITEM_LAYOUT_DELETE: DELETE,
	ITEM_CHANNEL_NEW: NEW_CHANNEL,
	ITEM_CHANNEL_REMOVE: REMOVE_CHANNEL,
	ITEM_CHANNEL_ATTRS: ATTRIBUTES,
	ITEM_OCHANNEL_ADD: ADD_CHANNEL,
}

class LayoutViewDialog(windowinterface.MACDialog):
	item_to_command = ITEM_TO_COMMAND
	
	def __init__(self):
##		w = windowinterface.Window('LayoutDialog', resizable = 1,
##					   deleteCallback = [CLOSE_WINDOW])
##		self.__window = w
		windowinterface.MACDialog.__init__(self, title, ID_DIALOG_LAYOUT,
				ITEMLIST_ALL)
##		w1 = w.SubWindow(left = None, top = None, bottom = None, right = 0.33)
##		w2 = w.SubWindow(left = w1, top = None, bottom = None, right = 0.67)
##		w3 = w.SubWindow(left = w2, top = None, bottom = None, right = None)
##		b1 = w1.ButtonRow([('New...', NEW_LAYOUT),
##				   ('Rename...', RENAME),
##				   ('Delete', DELETE),
##				   ],
##				  vertical = 0,
##				  left = None, right = None, bottom = None)
##		l1 = w1.List('Layouts', [], (self.__layoutcb, ()),
##			     top = None, left = None, right = None, bottom = b1)
##		self.__layoutlist = l1
		self.__layoutlist = self._window.ListWidget(ITEM_LAYOUT_LIST)
##		b2 = w2.ButtonRow([('New...', NEW_CHANNEL),
##				   ('Remove', REMOVE_CHANNEL),
##				   ('Attrs...', ATTRIBUTES),
##				   ],
##				  vertical = 0,
##				  left = None, right = None, bottom = None)
##		l2 = w2.List('Layout channels', [], (self.__channelcb, ()),
#### 			     tooltip = 'List of channels in current layout',
##			     top = None, left = None, right = None, bottom = b2)
##		self.__channellist = l2
		self.__channellist = self._window.ListWidget(ITEM_CHANNEL_LIST)
##		b3 = w3.ButtonRow([('Add', ADD_CHANNEL),
##				   ],
##				  vertical = 0,
##				  left = None, right = None, bottom = None)
##		l3 = w3.List('Other channels', [], (self.__othercb, ()),
#### 			     tooltip = 'List of channels not in current layout',
##			     top = None, left = None, right = None, bottom = b3)
##		self.__otherlist = l3
		self.__otherlist = self._window.ListWidget(ITEM_OCHANNEL_LIST)

	def destroy(self):
		if self.__window is None:
			return
		self.__window.close()
		self.__window = None
		del self.__layoutlist
		del self.__channellist
		del self.__otherlist

	def show(self):
		self.__window.show()

	def is_showing(self):
		if self.__window is None:
			return 0
		return self.__window.is_showing()

	def hide(self):
		if self.__window is not None:
			self.__window.hide()

	def setlayoutlist(self, layouts, cur):
		if layouts != self.__layoutlist.getlist():
			self.__layoutlist.delalllistitems()
			self.__layoutlist.addlistitems(layouts, 0)
		if cur is not None:
			self.__layoutlist.selectitem(layouts.index(cur))
		else:
			self.__layoutlist.selectitem(None)

	def setchannellist(self, channels, cur):
		if channels != self.__channellist.getlist():
			self.__channellist.delalllistitems()
			self.__channellist.addlistitems(channels, 0)
		if cur is not None:
			self.__channellist.selectitem(channels.index(cur))
		else:
			self.__channellist.selectitem(None)

	def setotherlist(self, channels, cur):
		if channels != self.__otherlist.getlist():
			self.__otherlist.delalllistitems()
			self.__otherlist.addlistitems(channels, 0)
		if cur is not None:
			self.__otherlist.selectitem(channels.index(cur))

	def layoutname(self):
		return self.__layoutlist.getselection()

	def __layoutcb(self):
		sel = self.__layoutlist.getselected()
		if sel is None:
			self.curlayout = None
		else:
			self.curlayout = self.__layoutlist.getlistitem(sel)
		self.fill()

	def __channelcb(self):
		sel = self.__channellist.getselected()
		if sel is None:
			self.curchannel = None
		else:
			self.curchannel = self.__channellist.getlistitem(sel)
		self.fill()

	def __othercb(self):
		sel = self.__otherlist.getselected()
		if sel is None:
			self.curother = None
		else:
			self.curother = self.__otherlist.getlistitem(sel)
		self.fill()

	def setwaiting(self):
		self.__window.setcursor('watch')

	def setready(self):
		self.__window.setcursor('')

	def setcommandlist(self, commandlist):
		self.__window.set_commandlist(commandlist)

	def asklayoutname(self, default):
		windowinterface.InputDialog('Name for layout',
					    default,
					    self.newlayout_callback,
					    cancelCallback = (self.newlayout_callback, ()),
					    parent = self.__window)

	def askchannelnameandtype(self, default, types):
		w = windowinterface.Window('newchanneldialog', grab = 1,
					   parent = self.__window)
		self.__chanwin = w
		t = w.TextInput('Name for channel', default, None, None, left = None, right = None, top = None)
		self.__chantext = t
		o = w.OptionMenu('Choose type', types, 0, None, top = t, left = None, right = None)
		self.__chantype = o
		b = w.ButtonRow([('Cancel', (self.__okchannel, (0,))),
				 ('OK', (self.__okchannel, (1,)))],
				vertical = 0,
				top = o, left = None, right = None, bottom = None)
		w.show()

	def __okchannel(self, ok = 0):
		if ok:
			name = self.__chantext.gettext()
			type = self.__chantype.getvalue()
		else:
			name = type = None
		self.__chanwin.close()
		del self.__chantext
		del self.__chantype
		del self.__chanwin
		# We can't call this directly since we're still in
		# grab mode.  We must first return from this callback
		# before we're out of that mode, so we must schedule a
		# callback in the very near future.
		windowinterface.settimer(0.00001, (self.newchannel_callback, (name, type)))
