__version__ = "$Id$"

from Channel import ChannelWindow, error
from TextChannel import mapfont, extract_taglist, fix_anchorlist
from AnchorDefs import *
import string
import MMurl
import MMAttrdefs
import os

class LabelChannel(ChannelWindow):
	node_attrs = ChannelWindow.node_attrs + \
		     ['bucolor', 'hicolor', 'fgcolor',
		      'font', 'pointsize', 'textalign',
		      'scale', 'center', 'crop', 'noanchors']

	def updatefixedanchors(self, node):
		try:
			str = self.getstring(node)
		except error, arg:
			print arg
			str = ''
		parlist = extract_paragraphs(str)
		taglist = extract_taglist(parlist)
		fix_anchorlist(node, taglist)
		return 1

	def do_arm(self, node, same = 0):
		if same and self.armed_display:
			return 1
		fgcolor = self.getfgcolor(node)
		bucolor = self.getbucolor(node)
		drawbox = MMAttrdefs.getattr(node, 'drawbox')
		try:
			str = self.getstring(node)
		except error, arg:
			print arg
			str = ''
		parlist = extract_paragraphs(str)
		if MMAttrdefs.getattr(node, 'noanchors'):
			taglist = []
		else:
			taglist = extract_taglist(parlist)
		fix_anchorlist(node, taglist)
		buttons = []
		if len(taglist) == 1:
			line0, char0, line1, char1, name, type, times = taglist[0]
			if line0 == 0 and char0 == 0 and \
			   line1 == len(parlist)-1 and \
			   char1 == len(parlist[-1]):
				taglist = []
				buttons.append((name, [0.0,0.0,1.0,1.0], type, times))
				if not drawbox:
					self.armed_display.fgcolor(bucolor)
		fontspec = MMAttrdefs.getattr(node, 'font')
		fontname, pointsize = mapfont(fontspec)
		ps = MMAttrdefs.getattr(node, 'pointsize')
		if ps != 0:
			pointsize = ps
		baseline, fontheight, pointsize = \
			  self.armed_display.setfont(fontname, pointsize)
		width, height = self.armed_display.strsize(
			string.joinfields(parlist, '\n'))
		align = MMAttrdefs.getattr(node, 'textalign')
		if align == 'center':
			y = (1.0 - height) / 2.0 + baseline
			left = right = 0
			block = 1
		else:
			if string.find(align, 'top') >= 0:
				y = baseline
			elif string.find(align, 'bottom') >= 0:
				y = 1.0 - height + baseline
			else:
				y = (1.0 - height) / 2.0 + baseline
			left = string.find(align, 'left') >= 0
			right = string.find(align, 'right') >= 0
			if left and right:
				left = right = 0
			block = string.find(align, 'block') >= 0
			if left: block = 1
		if block:
			if left:
				x = 0.0
			elif right:
				x = 1.0 - width
			else:
				x = (1.0 - width) / 2.0
			self.armed_display.setpos(x, y)
		pline = pchar = 0
		# for each anchor...
		for line0, char0, line1, char1, name, type, times in taglist:
			if (line0, char0) >= (line1, char1):
				print 'Anchor without screenspace:', name
				continue
			# display lines before the anchor
			for line in range(pline, line0):
				if not block and pchar == 0:
					self.position(y, parlist[line], right)
				dummy = self.armed_display.writestr(
					parlist[line][pchar:] + '\n')
				pchar = 0
				y = y + fontheight
			# display text before the anchor
			if not block and pchar == 0:
				self.position(y, parlist[line0], right)
			dummy = self.armed_display.writestr(
				parlist[line0][pchar:char0])
			# display text in the anchor (if on multiple lines)
			pline, pchar = line0, char0
			if not drawbox:
				self.armed_display.fgcolor(bucolor)
			for line in range(pline, line1):
				if not block and pchar == 0:
					self.position(y, parlist[line], right)
				box = self.armed_display.writestr(parlist[line][pchar:])
				buttons.append((name, box, type, times))
				dummy = self.armed_display.writestr('\n')
				pchar = 0
				y = y + fontheight
			# display text in anchor on last line of anchor
			if not block and pchar == 0:
				self.position(y, parlist[line1], right)
			box = self.armed_display.writestr(parlist[line1][pchar:char1])
			buttons.append((name, box, type, times))
			pline, pchar = line1, char1
			self.armed_display.fgcolor(fgcolor)
		# display text after last anchor
		for line in range(pline, len(parlist)):
			if not block and pchar == 0:
				self.position(y, parlist[line], right)
			dummy = self.armed_display.writestr(
				parlist[line][pchar:] + '\n')
			pchar = 0
			y = y + fontheight
		# draw boxes for the anchors
		if drawbox:
			self.armed_display.fgcolor(bucolor)
		else:
			self.armed_display.fgcolor(self.getbgcolor(node))
		hicolor = self.gethicolor(node)
		for name, box, type, times in buttons:
			# for now, keep the compatibility
			button = self.armed_display.newbutton([A_SHAPETYPE_RECT,]+box, times = times)
			button.hicolor(hicolor)
			button.hiwidth(3)
			self.setanchor(name, type, button, times)
		return 1

	def position(self, y, line, right):
		w, h = self.armed_display.strsize(line)
		if right:
			x = 1.0 - w
		else:
			x = (1.0 - w) / 2.0
		self.armed_display.setpos(x, y)

def extract_paragraphs(text):
	lines = string.splitfields(text, '\n')
	for lineno in range(len(lines)):
		line = lines[lineno]
		if '\t' in line: line = string.expandtabs(line, 8)
		i = len(line) - 1
		while i >= 0 and line[i] == ' ': i = i - 1
		line = line[:i+1]
		lines[lineno] = line
	return lines
