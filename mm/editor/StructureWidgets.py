# $Id$
# This file contains a list of standard widgets used in the
# HierarchyView. I tried to keep them view-independant, but
# I can't promise anything!!

import Widgets
import MMurl, MMAttrdefs, MMmimetypes, MMNode
import features
import os, windowinterface
import settings
from AppDefaults import *

TIMELINE_AT_TOP = 1
TIMELINE_IN_FOCUS = 1

ICONSIZE = windowinterface.ICONSIZE_PXL
ARROWCOLOR = (0,255,0)

######################################################################
# Create new widgets

def create_MMNode_widget(node, mother):
	assert mother != None
	ntype = node.GetType()
	if mother.usetimestripview:
		# We handle toplevel, second-level and third-level nodes differently
		# in snap
		if node.parent == None and ntype == 'seq':
			# Don't show toplevel root (actually the <body> in SMIL)
 			return UnseenVerticalWidget(node, mother)
		if node.parent and node.parent.parent == None and ntype == 'par':
			# Don't show second-level par either
			return UnseenVerticalWidget(node, mother)
		if node.parent and node.parent.parent and node.parent.parent.parent == None and ntype == 'seq':
			# And show secondlevel seq as a timestrip
			return TimeStripSeqWidget(node, mother)
	if ntype == 'seq':
		return SeqWidget(node, mother)
	elif ntype == 'par':
		return ParWidget(node, mother)
	elif ntype == 'switch':
		return SwitchWidget(node, mother)
	elif ntype == 'ext':
		return MediaWidget(node, mother)
	elif ntype == 'imm':
		return MediaWidget(node, mother)
	elif ntype == 'excl':
		return ExclWidget(node, mother)
	elif ntype == 'prio':
		return PrioWidget(node, mother)
	elif ntype == 'brush':
		return MediaWidget(node, mother)
	elif ntype == 'animate':
		return MediaWidget(node, mother)
	elif ntype == 'prefetch':
		return MediaWidget(node, mother)
	else:
		raise "Unknown node type", ntype
		return None



##############################################################################
# Abstract Base classes
##############################################################################

#
# The MMNodeWidget represents any widget which is representing an MMNode
# It also handles callbacks from the window interface.
#
class MMNodeWidget(Widgets.Widget):  # Aka the old 'HierarchyView.Object', and the base class for a MMNode view.
	# View of every MMNode within the Hierarchy view
	def __init__(self, node, mother):
		Widgets.Widget.__init__(self, mother)
		self.node = node			   # : MMNode
		assert isinstance(node, MMNode.MMNode)
		self.name = MMAttrdefs.getattr(self.node, 'name')
		self.node.set_infoicon = self.set_infoicon
		# self.node.views['struct_view'] is initialized in the subclasses,
		# because not all inheritors of this class should set it
		assert self.mother is not None
		self.is_timed = 0
		self.old_pos = None	# used for recalc optimisations.

		# Holds little icons..
		self.iconbox = IconBox(self, self.mother)
		self.iconbox.setup()
		self.has_event_icons = 0
		self.cause_event_icon = None

	def __repr__(self):
		return '<%s instance, name="%s", id=%X>' % (self.__class__.__name__, self.name, id(self))

	def get_node(self):
		return self.node

	def add_event_icons(self):
		if self.has_event_icons: # calls this once only.
			return
		self.has_event_icons = 1
		beginevents = MMAttrdefs.getattr(self.node, 'beginlist')
		endevents = MMAttrdefs.getattr(self.node, 'endlist')

		self.__add_events_helper(beginevents, 'beginevent')
		self.__add_events_helper(endevents, 'endevent')

	def __add_events_helper(self, events, iconname):
		icon = None
		for b in events:
			othernode = b.refnode()
			if othernode:
				# Known bug: TODO: I'm not worrying if the node is collapsed.
				# TODO: Add end events also.
				otherwidget = othernode.views['struct_view'].get_cause_event_icon()
				if icon is None:
					icon = self.iconbox.add_icon(iconname, arrowto = otherwidget).set_properties(arrowable=1).set_contextmenu(self.mother.event_popupmenu_dest)
				else:
					icon.add_arrow(otherwidget)
				otherwidget.add_arrow(icon)

	def collapse_levels(self, level):
		# Place holder for a recursive function.
		return

	def uncollapse_all(self):
		# Placeholder for a recursive function.
		return					  
	def collapse_all(self):		  # Is this doable using a higher-order function?
		return

	def destroy(self):
		# Prevent cyclic dependancies.
		Widgets.Widget.destroy(self)
		if self.node:
			del self.node.views['struct_view']
			del self.node.set_infoicon
			self.node = None
		self.set_infoicon = None

	def adddependencies(self):
		self.is_timed = 1
		t0, t1, t2, download, begindelay = self.node.GetTimes('bandwidth')
		w, h = self.get_minsize()
		if t0 != t1:
			self.mother.timemapper.adddependency(t0, t1, w)
		if t2 != t1 and t0 != t2:
			self.mother.timemapper.adddependency(t0, t2, w)
		
	def addcollisions(self, mastert0, mastertend):
		self.is_timed = 1
		edge = sizes_notime.HEDGSIZE
		t0, t1, t2, download, begindelay = self.node.GetTimes('bandwidth')
		tend = t2
		if download+begindelay:
			# Slightly special case. We register a collision on t0, and then continue
			# computing with t0 minus the delays
			self.mother.timemapper.addcollision(t0, edge)
			t0 = t0 - (download+begindelay)
		ledge = redge = edge
		if t0 == tend:
			w, h = self.get_minsize()
			if t0 == mastert0:
				ledge = ledge + w
			elif t0 == mastertend:
				redge = redge + w
			else:
				self.mother.timemapper.addcollision(t0, w+2*edge)
		if t0 != mastert0:
			self.mother.timemapper.addcollision(t0, ledge)
			ledge = 0
		if tend != mastertend:
			self.mother.timemapper.addcollision(tend, redge)
			redge = 0
		return ledge, redge
		
	def removedependencies(self):
		self.is_timed = 0
		
	def get_minpos(self):
		# Returns the leftmost position where this node can be placed
		pnode = self.node.parent
		if not pnode: return 0
		pwidget = pnode.views['struct_view']
		return pwidget.get_minpos() + pwidget.get_child_relminpos(self)

	def moveto(self, newpos):
		self.old_pos = self.pos_abs
		Widgets.Widget.moveto(self, newpos)
	#   
	# These a fillers to make this behave like the old 'Object' class.
	#
	def select(self):
		self.dont_draw_children = 1 # I'm selected.
		Widgets.Widget.select(self)

	def deselect(self):
		self.dont_draw_children = 1 # I'm deselected.
		self.unselect()

	def ishit(self, pos):
		return self.is_hit(pos)

	def cleanup(self):
		self.destroy()

	def set_infoicon(self, icon, msg=None):
		# Sets the information icon to this icon.
		# icon is a string, msg is a string.
		self.node.infoicon = icon
		self.node.errormessage = msg
		self.iconbox.add_icon(icon, callback = self.show_mesg)

	def get_cause_event_icon(self):
		# Returns the start position of an event arrow.
		if not self.cause_event_icon:
			self.cause_event_icon = self.iconbox.add_icon('causeevent').set_properties(arrowable = 1, arrowdirection=1).set_contextmenu(self.mother.event_popupmenu_source)
		return self.cause_event_icon

	def getlinkicon(self):
		# Returns the icon to show for incoming and outgiong hyperlinks.
		links = self.node.context.hyperlinks
		is_src, is_dst = links.findnodelinks(self.node)
		if is_src:
			if is_dst:
				return 'linksrcdst'
			else:
				return 'linksrc'
		else:
			if is_dst:
				return 'linkdst'
			else:
				return ''

	def get_nearest_node_index(a):
		# This is only for seqs and verticals.
		return -1

	def expandcall(self):
		# 'Expand' the view of this node.
		# Also, if this node is expanded, collapse it!
		# Doesn't appear to be called.
		if isinstance(self, StructureObjWidget):
			if self.iscollapsed():
				self.uncollapse()
			else:
				self.collapse()
			self.mother.need_redraw = 1

	def expandallcall(self, expand):
		# Expand the view of this node and all kids.
		# if expand is 1, expand. Else, collapse.
		if isinstance(self, StructureObjWidget):
			if expand:
				self.uncollapse_all()
			else:
				self.collapse_all()
			self.mother.need_redraw = 1

	def playcall(self):
		top = self.mother.toplevel
		top.setwaiting()
		top.player.playsubtree(self.node)

	def playfromcall(self):
		top = self.mother.toplevel
		top.setwaiting()
		top.player.playfrom(self.node)

	def attrcall(self):
		self.mother.toplevel.setwaiting()
		import AttrEdit
		AttrEdit.showattreditor(self.mother.toplevel, self.node)

	def editcall(self):
		self.mother.toplevel.setwaiting()
		import NodeEdit
		NodeEdit.showeditor(self.node)
	def _editcall(self):
		self.mother.toplevel.setwaiting()
		import NodeEdit
		NodeEdit._showeditor(self.node)
	def _opencall(self):
		self.mother.toplevel.setwaiting()
		import NodeEdit
		NodeEdit._showviewer(self.node)

	def anchorcall(self):
		self.mother.toplevel.setwaiting()
		import AnchorEdit
		AnchorEdit.showanchoreditor(self.mother.toplevel, self.node)

	def createanchorcall(self):
		self.mother.toplevel.links.wholenodeanchor(self.node)

	def hyperlinkcall(self):
		self.mother.toplevel.links.finish_link(self.node)

	def rpconvertcall(self):
		import rpconvert
		rpconvert.rpconvert(self.node)

	def deletecall(self):
		self.mother.deletefocus(0)

	def cutcall(self):
		self.mother.deletefocus(1)

	def copycall(self):
		mother = self.mother
		mother.toplevel.setwaiting()
		mother.copyfocus()

	def createbeforecall(self, chtype=None):
		self.mother.create(-1, chtype=chtype)

	def createbeforeintcall(self, ntype):
		self.mother.create(-1, ntype=ntype)

	def createaftercall(self, chtype=None):
		self.mother.create(1, chtype=chtype)

	def createafterintcall(self, ntype):
		self.mother.create(1, ntype=ntype)

	def createundercall(self, chtype=None):
		self.mother.create(0, chtype=chtype)

	def createunderintcall(self, ntype):
		self.mother.create(0, ntype=ntype)

	def createseqcall(self):
		self.mother.insertparent('seq')

	def createparcall(self):
		self.mother.insertparent('par')

	def createaltcall(self):
		self.mother.insertparent('switch')

	def pastebeforecall(self):
		self.mother.paste(-1)

	def pasteaftercall(self):
		self.mother.paste(1)

	def pasteundercall(self):
		self.mother.paste(0)

#
# An MMWidgetDecoration is a decoration on a widget - and has no particular
# binding to an MMNode, but rather to a parent MMWidget.
#
class MMWidgetDecoration(Widgets.Widget):
	# This is a base class for anything that an MMNodeWidget has on it, but which isn't
	# actually the MMWidget.
	def __init__(self, mmwidget, mother):
		assert isinstance(mmwidget, MMNodeWidget)
		
		self.mmwidget = mmwidget
		Widgets.Widget.__init__(self, mother)
	def destroy(self):
		self.mmwidget = None
		Widgets.Widget.destroy(self)
	def get_mmwidget(self):
		return self.mmwidget
	def get_node(self):
		return self.mmwidget.get_node()


#
# The StructureObjWidget represents any node which has children,
# and is thus collapsable.
#
class StructureObjWidget(MMNodeWidget):
	# A view of a seq, par, excl or any internal structure node.
	HAS_COLLAPSE_BUTTON = 1
	def __init__(self, node, mother):
		MMNodeWidget.__init__(self, node, mother)
		assert self is not None
		# Create more nodes under me if there are any.
		self.children = []
		if self.HAS_COLLAPSE_BUTTON and not self.mother.usetimestripview:
			if self.node.collapsed:
				icon = 'closed'
			else:
				icon = 'open'
			self.collapsebutton = Icon(self, self.mother)
			self.collapsebutton.setup()
			self.collapsebutton.set_properties(callbackable=1, selectable=0)
			self.collapsebutton.set_icon(icon)
			self.collapsebutton.set_callback(self.toggle_collapsed)
		else:
			self.collapsebutton = None
		self.parent_widget = None # This is the parent node. Used for recalcing optimisations.
		for i in self.node.children:
			bob = create_MMNode_widget(i, mother)
			if bob == None:
				pass
			else:
				bob.parent_widget = self
				self.children.append(bob)
		self.node.views['struct_view'] = self 
		if mother.timescale == 'global' and not node.parent:
			# If we are showing timescale globally we do it on the root
			self.timeline = TimelineWidget(self, mother)
		else:
			self.timeline = None
		self.need_recalc = 1	# used to determine if this node or any of it's children need recalculating.
		self.dont_draw_children = 0

#	def __repr__(self):
#		return "Abstract class StructureObjWidget, name = " + self.name

	def destroy(self):
		if self.children:
			for i in self.children:
				i.destroy()
		self.children = None
		if self.collapsebutton: self.collapsebutton.destroy()
		self.collapsebutton = None
		if self.parent_widget: self.parent_widget = None
		if self.timeline: self.timeline.destroy()
		self.timeline = None
		MMNodeWidget.destroy(self)

	def select(self):
		if self.mother.timescale in ('focus', 'cfocus'):
			self.timeline = TimelineWidget(self, self.mother)
		MMNodeWidget.select(self)
		
	def unselect(self):
		if self.mother.timescale in ('focus', 'cfocus') and self.timeline:
			self.timeline.destroy()
			self.timeline = None
		MMNodeWidget.unselect(self)
		
	def collapse_levels(self, levels):
		if levels < 1:
			self.collapse()
		for i in self.children:
			i.collapse_levels(levels-1)
		self.mother.need_redraw = 1

	def collapse(self):
		self.node.collapsed = 1
		if self.collapsebutton:
			self.collapsebutton.icon = 'closed'
		self.mother.need_redraw = 1
		self.mother.need_resize = 1
		self.set_need_resize()

	def uncollapse(self):
		self.node.collapsed = 0
		if self.collapsebutton:
			self.collapsebutton.icon = 'open'
		self.mother.need_redraw = 1
		self.mother.need_resize = 1
		self.set_need_resize()

	def toggle_collapsed(self):
		if self.iscollapsed():
			self.uncollapse()
		else:
			self.collapse()
			
	def iscollapsed(self):
		return self.node.collapsed

	def uncollapse_all(self):
		self.uncollapse()
		for i in self.children:
			i.uncollapse_all()

	def collapse_all(self):
		self.collapse()
		for i in self.children:
			i.collapse_all()

	def get_obj_at(self, pos):
		# Return the MMNode widget at position x,y
		# Oh, how I love recursive methods :-). Nice. -mjvdg.
		#if self.collapsebutton and self.collapsebutton.is_hit(pos):
		#	return self.collapsebutton
		
		if self.is_hit(pos):
			if self.iscollapsed():
				return self
			for i in self.children:
				ob = i.get_obj_at(pos)
				if ob != None:
					return ob
			return self
		else:
			return None

	def get_clicked_obj_at(self, pos):
		# Returns an object which reacts to a click() event.
		# This is duplicated code, so it's getting a bit hacky again.
		if self.collapsebutton and self.collapsebutton.is_hit(pos):
			return self.collapsebutton
		if self.is_hit(pos):
			if self.iconbox.is_hit(pos):
				return self.iconbox.get_clicked_obj_at(pos)
			elif self.iscollapsed():
				return self
			for i in self.children:
				ob = i.get_clicked_obj_at(pos)
				if ob != None:
					return ob
			return self
		else:
			return None

	def get_collapse_icon(self):
		return self.collapsebutton

	def recalc(self):
		# One optimisation that could be done is to have a dirty flag
		# for recalculating the relative sizes of all the nodes.
		# If the node sizes don't need to be changed, then don't
		# change them.
		# For the meanwhile, this is too difficult. 
		self.add_event_icons()
		if self.collapsebutton:
			l,t,r,b = self.pos_abs
			#l = l + self.get_relx(1)
			#t = t + self.get_rely(2)
			self.collapsebutton.moveto((l+1,t+2,0,0))
		self.need_resize = 0

	def set_need_resize(self):
		# Sets the need_recalc attribute.
		p = self
		while(p is not None):
			p.need_resize = 1
			p = p.parent_widget

	def draw_selected(self, displist):
		# Called from self.draw or from the mother when selection is changed.
		displist.draw3dbox(FOCUSRIGHT, FOCUSBOTTOM, FOCUSLEFT, FOCUSTOP, self.get_box())

	def draw_unselected(self, displist):
		# Called from self.draw or from the mother when selection is changed.
		displist.draw3dbox(FOCUSLEFT, FOCUSTOP, FOCUSRIGHT, FOCUSBOTTOM, self.get_box())

	def draw_box(self, displist):
		displist.draw3dbox(DROPCOLOR, DROPCOLOR, DROPCOLOR, DROPCOLOR, self.get_box())

	def draw(self, displist):
		# This is a base class for other classes.. this code only gets
		# called once the aggregating node has been called.
		# Draw only the children.
		if not self.iscollapsed():
			for i in self.children:
				i.draw(displist)

		# Draw the title.
		displist.fgcolor(CTEXTCOLOR)
		displist.usefont(f_title)
		l,t,r,b = self.pos_abs
		b = t + sizes_notime.TITLESIZE + sizes_notime.VEDGSIZE
		l = l + 16	# move it past the icon.

		if self.iconbox:
			self.iconbox.moveto((l,t+2,r,b))
			self.iconbox.draw(displist)
			l = l + self.iconbox.get_minsize()[0]
		
		displist.centerstring(l,t,r,b, self.name)
		if self.collapsebutton:
			self.collapsebutton.draw(displist)
		if self.timeline:
			self.timeline.draw(displist)
			
		displist.draw3dbox(FOCUSLEFT, FOCUSTOP, FOCUSRIGHT, FOCUSBOTTOM, self.get_box())			

	def adddependencies(self):
		MMNodeWidget.adddependencies(self)
		for ch in self.children:
			ch.adddependencies()

	def addcollisions(self, mastert0, mastertend):
		for ch in self.children:
			ch.addcollisions(None, None)
		return 0, 0

	def removedependencies(self):
		MMNodeWidget.removedependencies(self)
		for ch in self.children:
			ch.removedependencies()


#
# The HorizontalWidget is any sideways-drawn StructureObjWidget.
#
class HorizontalWidget(StructureObjWidget):
	# All widgets drawn horizontally; e.g. sequences.
	def draw(self, displist):
		# Draw those funny vertical lines.
		if self.iscollapsed():
			l,t,r,b = self.pos_abs
			i = l + sizes_notime.HEDGSIZE
			t = t + sizes_notime.VEDGSIZE + sizes_notime.TITLESIZE
			b = b - sizes_notime.VEDGSIZE
			step = 8
			if r > l:
				while i < r:
					displist.drawline(TEXTCOLOR, [(i, t),(i, b)])
					i = i + step
		StructureObjWidget.draw(self, displist)

	def get_nearest_node_index(self, pos):
		# Return the index of the node at the specific drop position.

		if self.iscollapsed():
			return -1

		assert self.is_hit(pos)
		x,y = pos
		# Working from left to right:
		for i in range(len(self.children)):
			l,t,w,h = self.children[i].get_box()
			if x <= l+(w/2.0):
				return i
		return -1

	def get_minsize(self, ignoreboxes=0):
		# Everything here calculated in pixels.
		if self.iscollapsed():
			boxsize = sizes_notime.MINSIZE + 2*sizes_notime.HEDGSIZE
			return boxsize, boxsize
		
		xgap = sizes_notime.GAPSIZE
		
		if not self.children and not self.channelbox:
			boxsize = sizes_notime.MINSIZE + 2*sizes_notime.HEDGSIZE
			min_width, min_height = boxsize, boxsize
			if self.dropbox and not ignoreboxes:
				min_width = min_width  + xgap + self.dropbox.get_minsize()[0]
			return min_width, min_height
		
		mw=0
		mh=0
		if self.channelbox and not ignoreboxes:
			mw, mh = self.channelbox.get_minsize()
			mw = mw + sizes_notime.GAPSIZE
			
		for i in self.children:
			pushover = 0
			w,h = i.get_minsize()
			if h > mh: mh=h
			mw = mw + w + pushover
			
		mw = mw + sizes_notime.GAPSIZE*(len(self.children)-1) + 2*sizes_notime.HEDGSIZE
		
		if self.dropbox and not ignoreboxes:
			mw = mw + self.dropbox.get_minsize()[0] + sizes_notime.GAPSIZE
			
		mh = mh + 2*sizes_notime.VEDGSIZE
		# Add the title box.
		mh = mh + sizes_notime.TITLESIZE
		if self.timeline:
			w, h = self.timeline.get_minsize()
			if w > mw:
				mw = w
			mh = mh + h
		return mw, mh
		
	def get_child_relminpos(self, child):
		minpos = sizes_notime.HEDGSIZE
		for ch in self.children:
			if ch == child:
				return minpos
			minpos = minpos + ch.get_minsize()[0] + sizes_notime.GAPSIZE
		raise 'Unknown child node'

	def recalc(self):
		# Recalculate the position of all the contained boxes.
		# Algorithm: Iterate through each of the MMNodes children's views and find their minsizes.
		# Apportion free space equally, based on the size of self.
		# TODO: This does not test for maxheight()
		
		if self.iscollapsed():
			StructureObjWidget.recalc(self)
			return

		l, t, r, b = self.pos_abs
		if self.timeline and not TIMELINE_AT_TOP:
			tl_w, tl_h = self.timeline.get_minsize()
			b = b - tl_h
		min_width, min_height = self.get_minsize()
		
		free_width = ((r-l) - min_width)
		
		# Add the title	 free
		
		t = t + sizes_notime.TITLESIZE
		min_height = min_height - sizes_notime.TITLESIZE
		
		# Add the timeline, if it is at the top
		if self.timeline and TIMELINE_AT_TOP:
			tl_w, tl_h = self.timeline.get_minsize()
			self.timeline.moveto((l, t, r, t+tl_h))
			t = t + tl_h
			min_height = min_height - tl_h
			
		# Always set free_width to zero. No way we can do this if a node halfway can
		# suddenly be timed and therefore take up lots of space.
		free_width = 0
		
		# Umm.. Jack.. the free width for each child isn't proportional to their size doing this..
		freewidth_per_child = free_width / max(1, len(self.children))
		
		l = l + sizes_notime.HEDGSIZE
		t = t + sizes_notime.VEDGSIZE
		b = b - sizes_notime.VEDGSIZE
		
		if self.channelbox:
			w, h = self.channelbox.get_minsize()
			self.channelbox.moveto((l, t, l+w, b))
			l = l + w + sizes_notime.GAPSIZE
		for chindex in range(len(self.children)):
			medianode = self.children[chindex]
			# Compute rightmost position we may draw
			if chindex == len(self.children)-1:
				max_r = self.pos_abs[2] - sizes_notime.VEDGSIZE
			elif not self.is_timed:
				# XXXX Should do this more intelligently
				max_r = self.pos_abs[2] - sizes_notime.VEDGSIZE
			else:
				nextmedianode = self.children[chindex+1]
				nt0, nt1, nt2, dummy, dummy = nextmedianode.node.GetTimes('bandwidth')
				max_r = self.mother.timemapper.time2pixel(nt0)
			w,h = medianode.get_minsize()
			thisnode_free_width = freewidth_per_child
			# First compute pushback bar position
			if medianode.is_timed:
				t0, t1, t2, download, begindelay = medianode.node.GetTimes('bandwidth')
				tend = t2
				lmin = self.mother.timemapper.time2pixel(t0)
				if l < lmin:
					l = lmin
			r = l + w + thisnode_free_width
			if medianode.is_timed:
				rmin = self.mother.timemapper.time2pixel(tend)
				# tend may be t2, the fill-time, so for fill=hold it may extend past
				# the begin of the next child. We have to truncate in that
				# case.
				if chindex < len(self.children)-1:
					nextch = self.children[chindex+1]
					rminmax = self.mother.timemapper.time2pixel(nextch.node.GetTimes('bandwidth')[0])
					if rmin > rminmax:
						rmin = rminmax
				if r < rmin:
					r = rmin
			else:
				if chindex == len(self.children)-1:
					# The last child is extended the whole way to the end
					r = max_r
			if r > max_r:
				r = max_r
			if l > r:
				l = r
			medianode.moveto((l,t,r,b))
			medianode.recalc()
			l = r + sizes_notime.GAPSIZE

		if self.dropbox:
			w,h = self.dropbox.get_minsize()
			# The dropbox takes up the rest of the free width.
			r = self.pos_abs[2]-sizes_notime.HEDGSIZE
			
			self.dropbox.moveto((l,t,r,b))
		
		if self.timeline and not TIMELINE_AT_TOP:
			l, t, r, b = self.pos_abs
			tl_w, tl_h = self.timeline.get_minsize()
			self.timeline.moveto((l, b-tl_h, r, b))

		StructureObjWidget.recalc(self)

#
# The Verticalwidget is any vertically-drawn StructureObjWidget.
#
class VerticalWidget(StructureObjWidget):
	# Any node which is drawn vertically

##	def __repr__(self):
##		return "VerticalWidget, name is: " + self.name

	def get_minsize(self):
		mw=0
		mh=0
		
		if len(self.children) == 0 or self.iscollapsed():
			boxsize = sizes_notime.MINSIZE + 2*sizes_notime.HEDGSIZE
			return boxsize, boxsize

		for i in self.children:
			w,h = i.get_minsize()
			if w > mw: mw=w
			mh=mh+h
		mh = mh + sizes_notime.GAPSIZE*(len(self.children)-1) + 2*sizes_notime.VEDGSIZE
		# Add the titleheight

		mh = mh + sizes_notime.TITLESIZE
		mw = mw + 2*sizes_notime.HEDGSIZE
		if self.timeline:
			w, h = self.timeline.get_minsize()
			if w > mw:
				mw = w
			mh = mh + h
		return mw, mh

	def get_child_relminpos(self, child):
		return sizes_notime.HEDGSIZE
		
	def get_nearest_node_index(self, pos):
		# Return the index of the node at the specific drop position.
		if self.iscollapsed():
			return -1
		
		assert self.is_hit(pos)
		x,y = pos
		# Working from left to right:
		for i in range(len(self.children)):
			l,t,w,h = self.children[i].get_box()
			if y <= t+(h/2.0):
				return i
		return -1

	def recalc(self):
		# Untested.
		# Recalculate the position of all the contained boxes.
		# Algorithm: Iterate through each of the MMNodes children's views and find their minsizes.
		# Apportion free space equally, based on the size of self.
		# TODO: This does not test for maxheight()
		
		if self.iscollapsed():
			StructureObjWidget.recalc(self)
			return
		
		l, t, r, b = self.pos_abs
		# Add the titlesize
		t = t + sizes_notime.TITLESIZE

		# Add the timeline, if it is at the top
		if self.timeline and TIMELINE_AT_TOP:
			tl_w, tl_h = self.timeline.get_minsize()
			self.timeline.moveto((l, t, r, t+tl_h))
			t = t + tl_h

		min_width, min_height = self.get_minsize()
		min_height = min_height - sizes_notime.TITLESIZE
		
		overhead_height = 2*sizes_notime.VEDGSIZE + len(self.children)-1*sizes_notime.GAPSIZE
		free_height = (b-t) - min_height
		
		if free_height < 0: #or free_height > 1.0:
			free_height = 0
		
		l_par = float(l) + sizes_notime.HEDGSIZE
		r = float(r) - sizes_notime.HEDGSIZE
		t = float(t) + sizes_notime.VEDGSIZE
		
		
		for medianode in self.children: # for each MMNode:
			w,h = medianode.get_minsize()
			l = l_par
			if h > (b-t):			  # If the node needs to be bigger than the available space...
				pass				   # TODO!!!!!
			# Take a portion of the free available width, fairly.
			if free_height == 0:
				thisnode_free_height = 0
			else:
				thisnode_free_height = h/(min_height-overhead_height) * free_height
			# Give the node the free width.
			b = t + h + thisnode_free_height
			this_l = l
			this_r = r
			if medianode.is_timed:
				t0, t1, t2, download, begindelay = medianode.node.GetTimes('bandwidth')
				tend = t2
				lmin = self.mother.timemapper.time2pixel(t0)
				if this_l < lmin:
					this_l = lmin
##				rmin = self.mother.timemapper.time2pixel(tend)
##				if this_r < rmin:
##					this_r = rmin
##				else:
				rmax = self.mother.timemapper.time2pixel(tend, align='right')
				if this_r > rmax:
					this_r = rmax
				if this_l > this_r:
					this_l = this_r
			
			medianode.moveto((this_l,t,this_r,b))
			medianode.recalc()
			t = b + sizes_notime.GAPSIZE
		if self.timeline and not TIMELINE_AT_TOP:
			l, t, r, b = self.pos_abs
			tl_w, tl_h = self.timeline.get_minsize()
			self.timeline.moveto((l, b-tl_h, r, b))

		StructureObjWidget.recalc(self)

	def draw(self, displist):
		if self.iscollapsed():
			l,t,r,b = self.pos_abs
			i = t + sizes_notime.VEDGSIZE + sizes_notime.TITLESIZE
			l = l + sizes_notime.HEDGSIZE
			r = r - sizes_notime.HEDGSIZE
			step = 8
			if r > l:
				while i < b:
					displist.drawline(TEXTCOLOR, [(l, i),(r, i)])
					i = i + step
		StructureObjWidget.draw(self, displist)

	def addcollisions(self, mastert0, mastertend):
		self.is_timed = 1
		t0, t1, t2, download, begindelay = self.node.GetTimes('bandwidth')
		tend = t1
		maxneededpixel0 = 0
		maxneededpixel1 = 0
		for ch in self.children:
			neededpixel0, neededpixel1 = ch.addcollisions(t0, tend)
			if neededpixel0 > maxneededpixel0:
				maxneededpixel0 = neededpixel0
			if neededpixel1 > maxneededpixel1:
				maxneededpixel1 = neededpixel1
		maxneededpixel0 = maxneededpixel0 + sizes_notime.HEDGSIZE
		maxneededpixel1 = maxneededpixel1 + sizes_notime.HEDGSIZE
		if t0 != mastert0:
			self.mother.timemapper.addcollision(t0, maxneededpixel0)
			maxneededpixel0 = 0
		if tend != mastertend:
			self.mother.timemapper.addcollision(tend, maxneededpixel1)
			maxneededpixel1 = 0
		return maxneededpixel0, maxneededpixel1


######################################################################
# Concrete widget classes.
######################################################################


######################################################################
# Structure widgets

#
# The SeqWidget represents a sequence node.
#
class SeqWidget(HorizontalWidget):
	# Any sequence node.
	HAS_CHANNEL_BOX = 0
	def __init__(self, node, mother):
		HorizontalWidget.__init__(self, node, mother)
		has_drop_box = not MMAttrdefs.getattr(node, 'project_readonly')
		if mother.usetimestripview and has_drop_box:
			self.dropbox = DropBoxWidget(node, mother)
		else:
			self.dropbox = None
		if self.HAS_CHANNEL_BOX:
			self.channelbox = ChannelBoxWidget(self, node, mother)
		else:
			self.channelbox = None

#	def __repr__(self):
#		return "Seq, name = " + self.name

	def destroy(self):
		HorizontalWidget.destroy(self)
		if self.dropbox: self.dropbox.destroy()
		self.dropbox = None
		if self.channelbox: self.channelbox.destroy()
		self.channelbox = None

	def get_obj_at(self, pos):
		if self.channelbox is not None and self.channelbox.is_hit(pos):
			return self.channelbox
		return HorizontalWidget.get_obj_at(self, pos)

	def draw(self, displist):
		willplay = not self.mother.showplayability or self.node.WillPlay()
		if willplay:
			color = SEQCOLOR
		else:
			color = SEQCOLOR_NOPLAY

		displist.drawfbox(color, self.get_box())

		if self.channelbox and not self.iscollapsed():
			self.channelbox.draw(displist)

		# Uncomment to redraw pushback bars.
		#for i in self.children:
		#	if isinstance(i, MediaWidget) and i.pushbackbar:
		#		i.pushbackbar.draw(displist)

		if self.dropbox and not self.iscollapsed():
			self.dropbox.draw(displist)
		HorizontalWidget.draw(self, displist)

	def adddependencies(self):
		# Sequence widgets need a special adddependencies, because we want to calculate the
		# time->pixel mapping without the channelbox and dropbox
		self.is_timed = 1
		t0, t1, t2, download, begindelay = self.node.GetTimes('bandwidth')
		w, h = self.get_minsize(ignoreboxes=1)
		if t0 != t1:
			self.mother.timemapper.adddependency(t0, t1, w)
		if t2 != t1 and t0 != t2:
			self.mother.timemapper.adddependency(t0, t2, w)
		for ch in self.children:
			ch.adddependencies()
		
	def addcollisions(self, mastert0, mastertend):
		self.is_timed = 1
		t0, t1, t2, download, begindelay = self.node.GetTimes('bandwidth')
		tend = t1
		maxneededpixel0 = sizes_notime.HEDGSIZE
		maxneededpixel1 = sizes_notime.HEDGSIZE
		if self.channelbox:
			mw, mh = self.channelbox.get_minsize()
			maxneededpixel0 = maxneededpixel0 + mw + sizes_notime.GAPSIZE
		if self.dropbox:
			mw, mw =self.dropbox.get_minsize()
			maxneededpixel1 = maxneededpixel1 + mw + sizes_notime.GAPSIZE
		time_to_collision = {t0: maxneededpixel0}
		time_to_collision[tend] = time_to_collision.get(tend, 0) + maxneededpixel1
		prevneededpixel = 0
		for ch in self.children:
			thist0, thist1, thist2, dummy, dummy = self.node.GetTimes('bandwidth')
			thistend = thist1
			neededpixel0, neededpixel1 = ch.addcollisions(thist0, thistend)
			time_to_collision[thist0] = time_to_collision.get(thist0, 0) + neededpixel0
			time_to_collision[thistend] = time_to_collision.get(thistend, 0) + neededpixel1
		maxneededpixel0 = time_to_collision[t0]
		del time_to_collision[t0]
		if time_to_collision.has_key(tend):
			maxneededpixel1 = time_to_collision[tend]
			del time_to_collision[tend]
		else:
			maxneededpixel1 = 0
		for time, pixel in time_to_collision.items():
			if pixel:
				self.mother.timemapper.addcollision(time, pixel)
		if t0 != mastert0:
			self.mother.timemapper.addcollision(t0, maxneededpixel0)
			maxneededpixel0 = 0
		if tend != mastertend:
			self.mother.timemapper.addcollision(tend, maxneededpixel1)
			maxneededpixel1 = 0
		return maxneededpixel0, maxneededpixel1

#
# The UnseenVerticalWidget is only ever a single top-level widget
#
class UnseenVerticalWidget(StructureObjWidget):
	# The top level par that doesn't get drawn.
	HAS_COLLAPSE_BUTTON = 0

#	def __init__(self, node, mother):
#		StructureObjWidget.__init__(self, node, mother)
			
##	def __repr__(self):
##		return "UnseenVerticalWidget, name = "+self.name

	def get_minsize(self):
		mw=0
		mh=0
		
		if len(self.children) == 0 or self.iscollapsed():
			return sizes_notime.MINSIZE, sizes_notime.MINSIZE+sizes_notime.TITLESIZE
		
		for i in self.children:
			w,h = i.get_minsize()
			if w > mw: mw=w
			mh=mh+h
		if self.timeline:
			w, h = self.timeline.get_minsize()
			if w > mw:
				mw = w
			mh = mh + h
		return mw, mh

	def get_child_relminpos(self, child):
		return 0

	def get_nearest_node_index(self, pos):
		# Return the index of the node at the specific drop position.
		if self.iscollapsed():
			return -1
		
		assert self.is_hit(pos)
		x,y = pos
		# Working from left to right:
		for i in range(len(self.children)):
			l,t,w,h = self.children[i].get_box()
			if y <= t+(h/2.0):
				return i
		return -1

	def recalc(self):
		# Recalculate the position of all the contained boxes.
		# Algorithm: Iterate through each of the MMNodes children's views and find their minsizes.
		# Apportion free space equally, based on the size of self.
		# TODO: This does not test for maxheight()
		
		if self.iscollapsed():
			StructureObjWidget.recalc(self)
			return
		
		l, t, r, b = self.pos_abs
		my_b = b
		# Add the titlesize;
		min_width, min_height = self.get_minsize()
		
		overhead_height = 0
		free_height = (b-t) - min_height
			
		if self.timeline and not TIMELINE_AT_TOP:
			tl_w, tl_h = self.timeline.get_minsize()
			self.timeline.moveto((l, t, r, t+tl_h))
			t = t + tl_h
			free_height = free_height - tl_h

		if free_height < 0:
			free_height = 0.0
		
		for medianode in self.children: # for each MMNode:
			w,h = medianode.get_minsize()
			if h > (b-t):			  # If the node needs to be bigger than the available space...
				pass				   # TODO!!!!!
			# Take a portion of the free available width, fairly.
			if free_height == 0.0:
				thisnode_free_height = 0.0
			else:
				thisnode_free_height = (float(h)/(min_height-overhead_height)) * free_height
			# Give the node the free width.
			b = t + h + thisnode_free_height 
			# r = l + w # Wrap the node to it's minimum size.
			this_l = l
			this_r = r
			if medianode.is_timed:
				t0, t1, t2, download, begindelay = medianode.node.GetTimes('bandwidth')
				tend = t2
				lmin = self.mother.timemapper.time2pixel(t0)
				if this_l < lmin:
					this_l = lmin
##				rmin = self.mother.timemapper.time2pixel(tend)
##				if this_r < rmin:
##					this_r = rmin
##				else:
				rmax = self.mother.timemapper.time2pixel(tend, align='right')
				if this_r > rmax:
					this_r = rmax
				if this_l > this_r:
					this_l = this_r
			medianode.moveto((this_l,t,this_r,b))
			medianode.recalc()
			t = b #  + self.get_rely(sizes_notime.GAPSIZE)
		if self.timeline and not TIMELINE_AT_TOP:
			self.timeline.moveto((l, t, r, my_b))
		StructureObjWidget.recalc(self)

	def draw(self, displist):
		# We want to draw this even if pushback bars are disabled.
		for i in self.children:
			#if isinstance(i, MediaWidget):
			#	i.pushbackbar.draw(displist)
			i.draw(displist)
		if self.timeline:
			self.timeline.draw(displist)

	def adddependencies(self):
		for ch in self.children:
			ch.adddependencies()
		
	def addcollisions(self, mastert0, mastertend):
		for ch in self.children:
			ch.addcollisions(None, None)

#
# A ParWidget represents a Par node.
#
class ParWidget(VerticalWidget):
	# Parallel node
	def draw(self, displist):
		willplay = not self.mother.showplayability or self.node.WillPlay()
		if willplay:
			color = PARCOLOR
		else:
			color = PARCOLOR_NOPLAY
		displist.drawfbox(color, self.get_box())
		VerticalWidget.draw(self, displist)

# and so forth..
class ExclWidget(SeqWidget):
	# Exclusive node.
	def draw(self, displist):
		willplay = not self.mother.showplayability or self.node.WillPlay()
		if willplay:
			color = EXCLCOLOR
		else:
			color = EXCLCOLOR_NOPLAY
		displist.drawfbox(color, self.get_box())
		StructureObjWidget.draw(self, displist)


class PrioWidget(SeqWidget):
	# Prio node (?!) - I don't know what they are, but here is the code I wrote! :-)
	def draw(self, displist):
		willplay = not self.mother.showplayability or self.node.WillPlay()
		if willplay:
			color = PRIOCOLOR
		else:
			color = PRIOCOLOR_NOPLAY
		displist.drawfbox(color, self.get_box())
##		if self.selected:
##			#displist.drawfbox(self.highlight(color), self.get_box())
##			displist.draw3dbox(FOCUSRIGHT, FOCUSBOTTOM, FOCUSLEFT, FOCUSTOP, self.get_box())
##		else:
##			#displist.drawfbox(color, self.get_box())
##			displist.draw3dbox(FOCUSLEFT, FOCUSTOP, FOCUSRIGHT, FOCUSBOTTOM, self.get_box())
		StructureObjWidget.draw(self, displist)


class SwitchWidget(VerticalWidget):
	# Switch Node
	def draw(self, displist):
		willplay = not self.mother.showplayability or self.node.WillPlay()
		if willplay:
			color = ALTCOLOR
		else:
			color = ALTCOLOR_NOPLAY
		displist.drawfbox(color, self.get_box())
##		if self.selected:
##			#displist.drawfbox(self.highlight(color), self.get_box())
##			displist.draw3dbox(FOCUSRIGHT, FOCUSBOTTOM, FOCUSLEFT, FOCUSTOP, self.get_box())
##		else:
##			#displist.drawfbox(color, self.get_box())
##			displist.draw3dbox(FOCUSLEFT, FOCUSTOP, FOCUSRIGHT, FOCUSBOTTOM, self.get_box())
		VerticalWidget.draw(self, displist)


##############################################################################
# The Media objects (images, videos etc) in the Structure view.
##############################################################################

#
# A MediaWidget represents most leaf nodes.
# This should really be an abstract base class, but that isn't necessary until
# the implementation changes.
#
class MediaWidget(MMNodeWidget):
	# A view of an object which is a playable media type.
	# NOT the structure nodes.

	# TODO: this has some common code with the two functions above - should they
	# have a common ancester?

	# TODO: This class can be broken down into various different node types (img, video)
	# if the drawing code is different enough to warrent this.
	
	def __init__(self, node, mother):
		MMNodeWidget.__init__(self, node, mother)
		self.transition_in = TransitionWidget(self, mother, 'in')
		self.transition_out = TransitionWidget(self, mother, 'out')

		if 0 and mother.timescale: # Disable for now, conflicts with single-node time display
			self.pushbackbar = PushBackBarWidget(self, mother)
		else:
			self.pushbackbar = None
		self.downloadtime = 0.0		# not used??
		self.downloadtime_lag = 0.0	# Distance to push this node to the right - relative coords. Not pixels.
		self.downloadtime_lag_errorfraction = 1.0
		#self.infoicon = Icon(None, self, self.node, self.mother)
		#self.infoicon.set_callback(self.show_mesg)

		# DEBUG:
		#i1 = self.iconbox.add_icon('linksrc').set_properties(arrowable = 1,selectable=1)
		#self.iconbox.add_icon('linksrcdst').add_arrow(i1).set_properties(arrowable = 1,selectable=1)
		#(self.iconbox.add_icon('transout')).add_arrow(self.mother.debug_arrow).set_properties(arrowable=1,selectable=1)
		#self.mother.debug_arrow = i1

		self.node.views['struct_view'] = self

##	def __repr__(self):
##		return "MediaWidget, name: " + self.name

	def destroy(self):
		# Remove myself from the MMNode view{} dict.
		MMNodeWidget.destroy(self)
		if self.iconbox: self.iconbox.destroy()
		self.iconbox = None
		if self.transition_in: self.transition_in.destroy()
		self.transistion_in = None
		if self.transition_out: self.transition_out.destroy()
		self.transition_out = None

	def is_hit(self, pos):
		hit = self.transition_in.is_hit(pos) or \
				self.transition_out.is_hit(pos) or \
				(self.pushbackbar and self.pushbackbar.is_hit(pos)) or \
				MMNodeWidget.is_hit(self, pos)
		return hit
		

	def show_mesg(self):
		if self.node.errormessage:
			windowinterface.showmessage(self.node.errormessage, parent=self.mother.window)

	def recalc(self):
		l,t,r,b = self.pos_abs

		self.add_event_icons()
		self.iconbox.moveto((l+1, t+2,0,0))
		# First compute pushback bar position
		if self.pushbackbar:
			if not self.is_timed:
				raise "Should not happen"
			t0, t1, t2, download, begindelay = self.node.GetTimes('bandwidth')
			if download + begindelay == 0:
				self.downloadtime_lag_errorfraction = 0
			else:
				self.downloadtime_lag_errorfraction = download / (download + begindelay)
			pbb_left = self.mother.timemapper.time2pixel(t0-(download+begindelay), align='right')
			self.pushbackbar.moveto((pbb_left, t, l, t+12))

		t = t + sizes_notime.TITLESIZE
		pix16x = 16
		pix16y = 16
		self.transition_in.moveto((l,b-pix16y,l+pix16x, b))
		self.transition_out.moveto((r-pix16x,b-pix16y,r, b))

		MMNodeWidget.recalc(self) # This is probably not necessary.

	def get_minsize(self):
		# return the minimum size of this node, in pixels.
		# Calld to work out the size of the canvas.
		xsize = sizes_notime.MINSIZE + self.iconbox.get_minsize()[0]
		ysize = sizes_notime.MINSIZE# + sizes_notime.TITLESIZE
		return (xsize, ysize)

	def get_maxsize(self):
		return sizes_notime.MAXSIZE, sizes_notime.MAXSIZE

	def draw_selected(self, displist):
		displist.drawfbox((255,255,255), self.get_box())
		displist.draw3dbox(FOCUSRIGHT, FOCUSBOTTOM, FOCUSLEFT, FOCUSTOP, self.get_box())
		self.__draw(displist)

	def draw_unselected(self, displist):
		self.draw(displist)

	def draw_box(self, displist):
		displist.draw3dbox(DROPCOLOR, DROPCOLOR, DROPCOLOR, DROPCOLOR, self.get_box())

	def draw(self, displist):
		# Only draw unselected.
		willplay = not self.mother.showplayability or self.node.WillPlay()
		if willplay:
			color = LEAFCOLOR
		else:
			color = LEAFCOLOR_NOPLAY
		displist.drawfbox(color, self.get_box())
		displist.draw3dbox(FOCUSLEFT, FOCUSTOP, FOCUSRIGHT, FOCUSBOTTOM, self.get_box())
		self.__draw(displist)

	def __draw(self, displist):
		x,y,w,h = self.get_box()	 
		y = y + sizes_notime.TITLESIZE
		h = h - sizes_notime.TITLESIZE
		
		ntype = self.node.GetType()

		# Draw the image.
		if self.node.GetChannelType() == 'brush':
			displist.drawfbox(MMAttrdefs.getattr(self.node, 'fgcolor'), (x+w/12, y+h/6, 5*(w/6), 4*(h/6)))
			displist.fgcolor(TEXTCOLOR)
			displist.drawbox((x+w/12, y+h/6, 5*(w/6), 4*(h/6)))
		else:
			image_filename = self.__get_image_filename()
			if image_filename != None and w > 0 and h > 0:
				try:
					box = displist.display_image_from_file(
						image_filename,
						center = 1,
						# The coordinates should all be floating point numbers.
						coordinates = (x+w/12, y+h/6, 5*(w/6), 4*(h/6)),
						scale = -2
						)
				except windowinterface.error:
					pass					# Shouldn't I use another icon or something?
				else:
					displist.fgcolor(TEXTCOLOR)
					displist.drawbox(box)

		# Draw the name
		iconsizex = ICONSIZE
		iconsizey = ICONSIZE
		displist.fgcolor(CTEXTCOLOR)
		displist.usefont(f_title)
		l,t,r,b = self.pos_abs
		b = t+sizes_notime.TITLESIZE + sizes_notime.VEDGSIZE
		#if self.node.infoicon:
		#	l = l + iconsizex	  # Maybe have an icon there soon.
		l = l + self.iconbox.get_minsize()[0]
		displist.centerstring(l,t,r,b,self.name)

		# Draw the icon before the name.
		#self.infoicon.icon = self.node.infoicon
		#self.infoicon.draw(displist)

		# Draw the icon box.
		self.iconbox.draw(displist)

		# Draw the silly transitions.
		if self.mother.transboxes:
			self.transition_in.draw(displist)
			self.transition_out.draw(displist)

	def __get_image_filename(self):
		# I just copied this.. I don't know what it does. -mjvdg.
		f = None
		
		url = self.node.GetAttrDef('file', None)
		if url:
			media_type = MMmimetypes.guess_type(url)[0]
		else:
			return None
		
		channel_type = self.node.GetChannelType()
		if url and self.mother.thumbnails and channel_type == 'image':
			url = self.node.context.findurl(url)
			try:
				f = MMurl.urlretrieve(url)[0]
			except IOError, arg:
				self.set_infoicon('error', 'Cannot load image: %s'%`arg`)
		else:
			f = os.path.join(self.mother.datadir, '%s.tiff'%channel_type)
		return f

	def get_obj_at(self, pos):
		# Returns an MMWidget at pos. Compare get_clicked_obj_at()
		if self.is_hit(pos):
			return self
		else:
			return None

	def get_clicked_obj_at(self, pos):
		# Returns any object which can be clicked(). 
		if self.is_hit(pos):
			if self.transition_in.is_hit(pos):
				return self.transition_in
			elif self.transition_out.is_hit(pos):
				return self.transition_out
			elif self.iconbox.is_hit(pos):
				return self.iconbox.get_clicked_obj_at(pos)
			elif self.pushbackbar and self.pushbackbar.is_hit(pos):
				return self.pushbackbar
			else:
				return self
		else:
			return None


class TransitionWidget(MMWidgetDecoration):
	# This is a box at the bottom of a node that represents the in or out transition.
	def __init__(self, parent, mother, inorout):
		MMWidgetDecoration.__init__(self, parent, mother)
		self.in_or_out = inorout
		self.parent = parent

	def destroy(self):
		self.parent = None
		MMWidgetDecoration.destroy(self)

	def select(self):
		# XXXX Note: this code assumes the select() is done on mousedown, and
		# that we can still post a menu at this time.
		self.parent.select()
		self.mother.need_redraw = 1

	def unselect(self):
		self.parent.unselect()

	def draw(self, displist):
		if self.in_or_out is 'in':
			displist.drawicon(self.get_box(), 'transin')
		else:
			displist.drawicon(self.get_box(), 'transout')

	def attrcall(self):
		self.mother.toplevel.setwaiting()
		import AttrEdit
		if self.in_or_out == 'in':
			AttrEdit.showattreditor(self.mother.toplevel, self.node, 'transIn')
		else:
			AttrEdit.showattreditor(self.mother.toplevel, self.node, 'transOut')

	def posttransitionmenu(self):
		transitionnames = self.node.context.transitions.keys()
		transitionnames.sort()
		transitionnames.insert(0, 'No transition')
		if self.in_or_out == 'in':
			which = 'transIn'
		else:
			which = 'transOut'
		curtransition = MMAttrdefs.getattr(self.node, which)
		if not curtransition:
			curtransition = 'No transition'
		if curtransition in transitionnames:
			transitionnames.remove(curtransition)
		transitionnames.insert(0, curtransition)
		return which, transitionnames

	def transition_callback(self, which, new):
		curtransition = MMAttrdefs.getattr(self.node, which)
		if not curtransition:
			curtransition = 'No transition'
		if new == curtransition:
			return
		if new == 'No transition':
			new = ''
		editmgr = self.mother.editmgr
		if not editmgr.transaction():
			return # Not possible at this time
		editmgr.setnodeattr(self.node, which, new)
		editmgr.commit()


######################################################################
# Widget decorations.
######################################################################

class PushBackBarWidget(MMWidgetDecoration):
	# This is a push-back bar between nodes.
	def __init__(self, parent, mother):
		MMWidgetDecoration.__init__(self, parent, mother)
		self.node = parent.node
		self.parent = parent

	def draw(self, displist):
		# TODO: draw color based on something??
		redfraction = self.parent.downloadtime_lag_errorfraction
		x, y, w, h = self.get_box()
		displist.fgcolor(TEXTCOLOR)
		displist.drawfbox(COLCOLOR, (x, y, w*redfraction, h))
		displist.drawfbox(LEAFCOLOR, (x+w*redfraction, y, w*(1-redfraction), h))
		displist.draw3dbox(FOCUSLEFT, FOCUSTOP, COLCOLOR, FOCUSBOTTOM, self.get_box())

	def draw_selected(self, displist):
		redfraction = self.parent.downloadtime_lag_errorfraction
		x, y, w, h = self.get_box()
		displist.fgcolor(TEXTCOLOR)
		displist.drawfbox(COLCOLOR, (x, y, w*redfraction, h))
		displist.drawfbox(LEAFCOLOR, (x+redfraction, y, w*(1-redfraction), h))
		displist.drawbox(self.get_box())

	def draw_unselected(self, displist):
		self.draw(displist)

	def draw_box(self, displist):
		self.parent.draw_box(displist)

	def select(self):
		self.parent.select()

	def unselect(self):
		self.parent.unselect()

	def ishit(self, pos):
		return self.is_hit(pos)

	def attrcall(self):
		self.mother.toplevel.setwaiting()
		import AttrEdit
		AttrEdit.showattreditor(self.mother.toplevel, self.node, '.begin1')


class TimelineWidget(MMWidgetDecoration):
	# A widget showing the timeline
##	def __repr__(self):
##		return "TimelineWidget"
	
	def get_minsize(self):
		return f_timescale.strsizePXL(' 000:00 000:00 000:00 ')[0], 2*sizes_notime.TITLESIZE
		
	def moveto(self, coords):
		MMWidgetDecoration.moveto(self, coords)
		t0, t1, t2, download, begindelay = self.get_mmwidget().node.GetTimes('bandwidth')
		self.time_segments = self.mother.timemapper.gettimesegments(range=(t0, t2))
		starttime, dummy, oldright = self.time_segments[0]
		stoptime, dummy, dummy = self.time_segments[-1]
		self.ticks = [(starttime, self.mother.timemapper.time2pixel(starttime, align='right'))]
		for time in range(int(starttime+1), int(stoptime)+1):
			tick_x = self.mother.timemapper.interptime2pixel(time)
			self.ticks.append((time, tick_x))
		
	def draw(self, displist):
		x, y, w, h = self.get_box()
		if TIMELINE_AT_TOP:
			line_y = y + (h/2)
			tick_top = line_y
			tick_bot = y+h-(h/3)
			longtick_top = line_y
			longtick_bot = y + h - (h/6)
			endtick_top = line_y - (h/3)
			endtick_bot = longtick_bot
			label_top = y 
			label_bot = y + (h/2)
		else:
			line_y = y + (h/2)
			tick_top = y + (h/3)
			tick_bot = line_y
			longtick_top = y + (h/6)
			longtick_bot = line_y
			endtick_top = longtick_top
			endtick_bot = line_y + (h/6)
			label_top = y + (h/2)
			label_bot = y + h
		starttime, dummy, oldright = self.time_segments[0]
		stoptime, dummy, dummy = self.time_segments[-1]
		for time, left, right in self.time_segments[1:]:
			displist.drawline(TEXTCOLOR, [(oldright, line_y), (left, line_y)])
			if time != stoptime:
				displist.drawline(COLCOLOR, [(left, line_y), (right, line_y)])
			oldright = right
		halflabelwidth = displist.strsize('000:00 ')[0]/2
		lastlabelpos = x
		displist.usefont(f_timescale)
		for time, tick_x in self.ticks:
			# Check whether it is time for a tick
			if int(time) % 10 in (0, 5) and tick_x > lastlabelpos + halflabelwidth:
				lastlabelpos = tick_x + halflabelwidth
				cur_tick_top = longtick_top
				cur_tick_bot = longtick_bot
				displist.centerstring(tick_x-halflabelwidth, label_top,
					tick_x+halflabelwidth, label_bot, '%02d:%02.2d'%(int(time)/60, int(time)%60))
			else:
				cur_tick_top = tick_top
				cur_tick_bot = tick_bot
			displist.drawline(TEXTCOLOR, [(tick_x, cur_tick_top), (tick_x, cur_tick_bot)])			
	draw_selected = draw

# A box with icons in it.
# Comes before the node's name.
class IconBox(MMWidgetDecoration):
	def setup(self):
		self._icons = {}
		self.iconlist = []	# a list of icon names, the order is kept.
		self.remember_click = (0,0)
		self.selected_iconname = None

	def destroy(self):
		for iconname in self.iconlist:
			self._icons[iconname].destroy()
		self._icons = None
		MMWidgetDecoration.destroy(self)

	def add_icon(self, iconname, callback=None, contextmenu=None, arrowto=None):
		# iconname - name of an icon, decides which icon to use.
		# callback - function to call when icon is clicked on.
		# contextmenu - pop-up menu to use.
		# arrowto - Draw an arrow to another icon on the screen.
		i = Icon(self.mmwidget, self.mother)
		i.setup()
		i.set_icon(iconname)
		if callback:
			i.set_callback(callback)
		if contextmenu:
			i.set_contextmenu(contextmenu)
		if arrowto:
			i.add_arrow(arrowto)
		self._icons[iconname] = i
		if iconname not in self.iconlist:
			self.iconlist.append(iconname)
		return i

	def get_icon(self, iconname):
		if self._icons.has_key(iconname):
			return self._icons[iconname]
		else:
			return None

	def del_icon(self, iconname):
		del self._icons[iconname]
		del self.iconlist[iconname]

	def get_minsize(self):
		# Always the number of icons.
		return ((len(self._icons) * ICONSIZE), ICONSIZE)

	def get_clicked_obj_at(self, coords):
		x,y = coords
		return self.__get_icon(x)

	def is_hit(self, pos):
		l,t,a,b = self.pos_abs
		x,y = pos
		if l < x < l+(len(self._icons)*ICONSIZE) and t < y < t+ICONSIZE:
			return 1
		else:
			return 0

	def draw(self, displist):
		l,t,r,b = self.pos_abs
		for iconname in self.iconlist:
			i = self._icons[iconname]
			i.moveto((l,t,r,b))
			i.draw(displist)
			l = l + ICONSIZE
	draw_selected = draw

	def __get_icon_name(self, x):
		l,t,r,b = self.pos_abs
		if len(self.iconlist) > 0:
			index = int((x-l)/ICONSIZE)
			if index >= 0 and index < len(self.iconlist):
				return self.iconlist[index]
		else:
			return None

	def __get_icon(self, x):
		return self._icons[self.__get_icon_name(x)]

	def mouse0release(self, coords):
		x,y = coords
		l,t,r,b = self.pos_abs
		icon = self.__get_icon(x)
		if icon:
			icon.mouse0release(coords)
		else:
			return
		
		#if self.callback:
		#	apply(apply, self.callback)


class Icon(MMWidgetDecoration):
	# Display an icon which can be clicked on. This can be used for
	# any icon on screen.

	def setup(self):
		self.callback = None
		self.arrowto = []	# a list of other MMWidgets.
		self.icon = ""
		self.contextmenu = None
		
		self.set_properties()

	def destroy(self):
		MMWidgetDecoration.destroy(self)
		self.callback = None
		self.arrowto = None

	def set_icon(self, iconname):
		self.icon = iconname
		return self

	def set_properties(self, selectable=1, callbackable=1, arrowable=0, arrowdirection=0):
		self.selectable = selectable
		self.callbackable = callbackable
		self.arrowable = arrowable
		self.arrowdirection = arrowdirection
		return self

	def select(self):
		if self.selectable:
			MMWidgetDecoration.select(self)
	def unselect(self):
		if self.selectable:
			MMWidgetDecoration.unselect(self)

	def set_callback(self, callback, args=()):
		self.callback = callback, args
		return self

	def mouse0release(self, coords):
		if self.callback and self.icon:
			apply(apply, self.callback)

	def moveto(self, pos):
		l,t,r,b = pos
		iconsizex = sizes_notime.ERRSIZE
		iconsizey = sizes_notime.ERRSIZE
		MMWidgetDecoration.moveto(self, (l, t, l+iconsizex, t+iconsizey))
		return self

	def draw_selected(self, displist):
		if not self.selectable:
			self.draw(displist)
			return
		displist.drawfbox((0,0,0),self.get_box())
		self.draw(displist)
		if self.arrowable:	# The arrows get drawn by the Hierarchyview at a later stage.
			for arrow in self.arrowto:
				p = arrow.get_node().GetCollapsedParent()
				if p:
					l,t,r,b = p.views['struct_view'].get_collapse_icon().pos_abs
				else:
					l,t,r,b = arrow.pos_abs
				if l == 0:
					return
				xd = (l+r)/2
				yd = (t+b)/2
				l,t,r,b = self.pos_abs
				xs = (l+r)/2
				ys = (t+b)/2
				if self.arrowdirection:
					self.mother.add_arrow(ARROWCOLOR, (xs,ys),(xd,yd))
				else:
					self.mother.add_arrow(ARROWCOLOR, (xd,yd),(xs,ys))

	def draw_unselected(self, displist):
		self.draw(displist)

	def draw(self, displist):
		if self.icon is not None:
			displist.drawicon(self.get_box(), self.icon)

	def set_contextmenu(self, foobar):
		self.contextmenu = foobar			# TODO.
		return self
	def get_contextmenu(self):
		return self.contextmenu

	def add_arrow(self, dest):
		# dest can be any MMWidget.
		if dest and dest not in self.arrowto:
			self.arrowto.append(dest)
		return self

	def is_selectable(self):
		return self.selectable


# Maybe one day.
##class CollapseIcon(Icon):
##	# For collapsing and uncollapsing nodes
##	def setup(self):
##		Icon.setup(self)
##		self.selectable = 0
##		self.callbackable = 1
##		self.arrowable = 0
##		self.contextmenu = None

##class EventSourceIcon(Icon):
##	# Is the source of an event
##	def setup(self):
##		Icon.setup(self)
##		self.selectable = 1
##		self.callbackable = 1
##		self.arrowable = 1
##		self.arrowdirection = 1
##		self.contextmenu = None

##class EventIcon(Icon):
##	# Is the actual event.
##	pass




##############################################################################
			# Crap at the end of the file.

class BrushWidget(MMNodeWidget):
	def __init__(self):
		print "TODO: BrushWidget"

#class TimeStripSeqWidget(SeqWidget):
#	# A sequence that has a channel widget at the start of it.
#	# This only exists at the second level from the root, assuming the root is a
#	# par.
#	# Wow. I like this sort of code. If only the rest of the classes were this easy. -mjvdg
#	HAS_COLLAPSE_BUTTON = 0
#	HAS_CHANNEL_BOX = 1
##	def __repr__(self):
##		return "TimeStripSeqWidget"

class ImageBoxWidget(MMWidgetDecoration):
	# Common baseclass for dropbox and channelbox
	# This is only for images shown as part of the sequence views; This
	# is not used for any image on screen.
##	def __repr__(self):
##		return "ImageBoxWidget"
	
	def get_minsize(self):
		return sizes_notime.MINSIZE, sizes_notime.MINSIZE

	def draw(self, displist):
		x,y,w,h = self.get_box()	 
		
		# Draw the image.
		image_filename = self._get_image_filename()
		if image_filename != None:
			try:
				sx = sizes_notime.DROPAREASIZE
				sy = sx
				cx = x + w/2 # center 
				cy = y + h/2
				box = displist.display_image_from_file(
					image_filename,
					center = 1,
					# The coordinates should all be floating point numbers.
					# Wrong - now they are pixels -mjvdg.
					#coordinates = (float(x+w)/12, float(y+h)/6, 5*(float(w)/6), 4*(float(h)/6)),
					coordinates = (cx - sx/2, cy - sy/2, sx, sy),
					scale = -2
					)
#				print "TODO: fix those 32x32 hard-coded sizes."
			except windowinterface.error:
				pass
			else:
				displist.fgcolor(TEXTCOLOR)
				displist.drawbox(box)


class DropBoxWidget(ImageBoxWidget):
	# This is the stupid drop-box at the end of a sequence. Looks like a
	# MediaWidget, acts like a MediaWidget, but isn't a MediaWidget.

##	def __repr__(self):
##		return "DropBoxWidget"

	def _get_image_filename(self):
		f = os.path.join(self.mother.datadir, 'dropbox.tiff')
		return f


class ChannelBoxWidget(ImageBoxWidget):
	# This is the box at the start of a Sequence which represents which channel it 'owns'
	def __init__(self, parent, node, mother):
		Widgets.Widget.__init__(self, mother) 
		self.node = node
		self.parent = parent

##	def __repr__(self):
##		return "ChannelBoxWidget"

	def draw(self, displist):
		ImageBoxWidget.draw(self, displist)
		x, y, w, h = self.get_box()
		texth = sizes_notime.TITLESIZE
		texty = y + h - texth
		availbw  = settings.get('system_bitrate')
		bwfraction = MMAttrdefs.getattr(self.node, 'project_bandwidth_fraction')
		if bwfraction <= 0:
			return
		bandwidth = availbw * bwfraction
		if bandwidth < 1000:
			label = '%d bps'%int(bandwidth)
		elif bandwidth < 10000:
			label = '%3.1f Kbps'%(bandwidth / 1000.0)
		elif bandwidth < 1000000:
			label = '%3d Kbps' % int(bandwidth / 1000)
		elif bandwidth < 10000000:
			label = '%3.1f Mbps'%(bandwidth / 1000000.0)
		else:
			label = '%d Mbps'%int(bandwidth / 1000000)
		displist.fgcolor(CTEXTCOLOR)
		displist.usefont(f_title)
		displist.centerstring(x, texty, x+w, texty+texth, label)
	
	def get_minsize(self):
		return sizes_notime.MINSIZE, sizes_notime.MINSIZE + sizes_notime.TITLESIZE

	def _get_image_filename(self):
		channel_type = MMAttrdefs.getattr(self.node, 'project_default_type')
		if not channel_type:
			channel_type = 'null'
		f = os.path.join(self.mother.datadir, '%s.tiff'%channel_type)
		if not os.path.exists(f):
			f = os.path.join(self.mother.datadir, 'null.tiff')
		return f

	def select(self):
		self.parent.select()

	def unselect(self):
		self.parent.unselect()

	def ishit(self, pos):
		return self.is_hit(pos)

	def attrcall(self):
		self.mother.toplevel.setwaiting()
		chname = MMAttrdefs.getattr(self.node, 'project_default_region')
		if not chname:
			self.parent.attrcall()
		channel = self.mother.toplevel.context.getchannel(chname)
		if not channel:
			self.parent.attrcall()
		import AttrEdit
		AttrEdit.showchannelattreditor(self.mother.toplevel, channel)

