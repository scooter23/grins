#
# XXXX This is a placeholder for the coming HTML channel. It is just
# an ordinary text channel, but it's anchors have arguments.
#
from Channel import ChannelWindow
from AnchorDefs import *
from debug import debug
import string
from urllib import urlopen

class HtmlChannel(ChannelWindow):
	node_attrs = ChannelWindow.node_attrs + ['fgcolor', 'font', \
		  'pointsize']

	def init(self, name, attrdict, scheduler, ui):
		return ChannelWindow.init(self, name, attrdict, scheduler, ui)

	def __repr__(self):
		return '<HtmlChannel instance, name=' + `self._name` + '>'

	def updatefixedanchors(self, node):
		str = self.getstring(node)
		parlist = extract_paragraphs(str)
		taglist = extract_taglist(parlist)
		fix_anchorlist(node, taglist)
		return 1
		
	def do_arm(self, node):
		str = self.getstring(node)
		parlist = extract_paragraphs(str)
		taglist = extract_taglist(parlist)
		fix_anchorlist(node, taglist)
##			if taglist: print `taglist`
		fontspec = getfont(node)
		fontname, pointsize = mapfont(fontspec)
		ps = getpointsize(node)
		if ps != 0:
			pointsize = ps
		baseline, fontheight, pointsize = \
			  self.armed_display.setfont(\
			  fontname, pointsize)
		margin = self.armed_display.strsize('m')[0] / 2
		width = 1.0 - 2 * margin
		curlines, partoline, linetopar = calclines(parlist, \
			  self.armed_display.strsize, width)
		self.armed_display.setpos(margin, baseline)
		buttons = []
		# write the text on the window.
		# The loop is executed once for each anchor defined
		# in the text.  pline and pchar specify how far we got
		# with printing.
		pline, pchar = 0, 0
		for (par0, chr0, par1, chr1, name, type) in taglist:
			# first convert paragraph # and character #
			# to line and character.
			line0, char0 = map_parpos_to_linepos(par0, \
				  chr0, 0, curlines, partoline)
			line1, char1 = map_parpos_to_linepos(par1, \
				  chr1, 1, curlines, partoline)
			if (line0, char0) > (line1, char1):
				print 'Anchor without screenspace:', name
				continue
			# write everything before the anchor
			for line in range(pline, line0):
				dummy = self.armed_display.writestr(curlines[line][pchar:] + '\n')
				pchar = 0
			dummy = self.armed_display.writestr(curlines[line0][pchar:char0])
			pline, pchar = line0, char0
			# write the anchor text and remember its
			# position (note: the anchor may span several
			# lines)
			for line in range(pline, line1):
				box = self.armed_display.writestr(curlines[line][pchar:])
				buttons.append((name, box, type))
				dummy = self.armed_display.writestr('\n')
				pchar = 0
			box = self.armed_display.writestr(curlines[line1][pchar:char1])
			buttons.append((name, box, type))
			# update loop invariants
			pline, pchar = line1, char1
		# write text after last button
		for line in range(pline, len(curlines)):
			dummy = self.armed_display.writestr(curlines[line][pchar:] + '\n')
			pchar = 0
##			print 'buttons:',`buttons`
		self.armed_display.fgcolor(self.gethicolor(node))
		for (name, box, type) in buttons:
			button = self.armed_display.newbutton(box)
			button.hiwidth(3)
##			button.hicolor(self.getfgcolor(node))
			self.setanchor(name, type, button)
##			dummy = self.armed_display.writestr(string.joinfields(curlines, '\n'))
		return 1

	def getstring(self, node):
		if node.type == 'imm':
			return string.joinfields(node.GetValues(), '\n')
		elif node.type == 'ext':
			filename = self.getfilename(node)
			try:
				fp = urlopen(filename)
			except IOError:
				print 'Cannot open text file', `filename`
				return ''
			text = fp.read()
			fp.close()
			if text[-1:] == '\n':
				text = text[:-1]
			return text
		else:
			raise CheckError, \
				'gettext on wrong node type: ' +`node.type`

	def defanchor(self, node, anchor):
		# Anchors don't get edited in the HtmlChannel.  You
		# have to edit the text to change the anchor.  We
		# don't want a message, though, so we provide our own
		# defanchor() method.
		return anchor

# Convert an anchor to a set of boxes.
def map_parpos_to_linepos(parno, charno, last, curlines, partoline):
	# This works only if parno and charno are valid
	sublist = partoline[parno]
	for lineno, char0, char1 in sublist:
		if charno <= char1:
			i = max(0, charno-char0)
			if last:
				return lineno, i
			curline = curlines[lineno]
			n = len(curline)
			while i < n and curline[i] == ' ': i = i+1
			if i < n:
				return lineno, charno-char0
			charno = char1

def getfont(node):
	import MMAttrdefs
	return MMAttrdefs.getattr(node, 'font')

def getpointsize(node):
	import MMAttrdefs
	return MMAttrdefs.getattr(node, 'pointsize')

# Turn a text string into a list of strings, each representing a paragraph.
# Tabs are expanded to spaces (since the font mgr doesn't handle tabs),
# but this only works well at the start of a line or in a monospaced font.
# Blank lines and lines starting with whitespace separate paragraphs.

def extract_paragraphs(text):
	lines = string.splitfields(text, '\n')
	parlist = []
	par = []
	for line in lines:
		if '\t' in line: line = string.expandtabs(line, 8)
		i = len(line) - 1
		while i >= 0 and line[i] == ' ': i = i-1
		line = line[:i+1]
		if not line or line[0] in ' \t':
			parlist.append(string.join(par))
			par = []
		if line:
			par.append(line)
	if par: parlist.append(string.join(par))
	return parlist


# Extract anchor tags from a list of paragraphs.
#
# An anchor starts with "<A NAME=...>" and ends with "</A>".
# Alternatively, for compatability with the HTML channel, anchors can
# be formatted as <A HREF="cmif:...">.
# These tags are case independent; whitespace is significant.
# Anchors may span paragraphs but an anchor tag must be contained in
# one paragraph.  Other occurrences of < are left in the text.
#
# The list of paragraps is modified in place (the tags are removed).
# The return value is a list giving the start and end position
# of each anchor and its name.  Start and end positions are given as
# paragraph_number, character_offset.

def extract_taglist(parlist):
	import regex
	# (1) Extract the raw tags, removing them from the text
	pat = regex.compile('<[Aa] +[Nn][Aa][Mm][Ee]=\([a-zA-Z0-9_]+\)>\|'+
		  '<[Aa] +[Hh][Rr][Ee][Ff]="[Cc][Mm][Ii][Ff]:\([a-zA-Z0-9_]+\)">\|</[Aa]>')
	rawtaglist = []
	for i in range(len(parlist)):
		par = parlist[i]
		j = 0
		while pat.search(par, j) >= 0:
			regs = pat.regs
			a, b = regs[0]
			tag = par[a:b]
			par = par[:a] + par[b:]
			j = a
			if tag[:2] != '</':
				a, b = regs[1]
				if a == b:
					a, b = regs[2]
				name = tag[a-j:b-j]
			else:
				name = None
			rawtaglist.append((i, j, name))
		parlist[i] = par
	# (2) Parse the raw taglist, picking up the valid patterns
	# (a begin tag immediately followed by an end tag)
	taglist = []
	last = None
	for item in rawtaglist:
		if item[2] is not None:
			last = item
		elif last:
			taglist.append(last[:2] + item[:2] + last[2:3])
			last = None
	return taglist

# XXX THIS IS A HACK
# When we have extracted the anchors from a node's paragraph list,
# add them to the node's anchor list.
# This should be done differently, and doesn't even use the edit mgr,
# but as a compatibility hack it's probably OK...

def fix_anchorlist(node, taglist):
	if not taglist:
		return
	import MMAttrdefs
	names_in_anchors = []
	names_in_taglist = []
	anchor_types = {}
	for item in taglist:
		names_in_anchors.append(item[4])
	oldanchors = MMAttrdefs.getattr(node, 'anchorlist')
	modanchorlist(oldanchors)
	anchors = oldanchors[:]
	i = 0
	while i < len(anchors):
		aid, atype, args = a = anchors[i]
		if atype in [ATYPE_WHOLE, ATYPE_AUTO, ATYPE_COMP]:
			pass
		elif aid not in names_in_anchors:
			print 'Dont remove html anchor from anchorlist:', a
		else:
			names_in_taglist.append(aid)
			anchor_types[aid] = atype
		i = i + 1
	for i in range(len(taglist)):
		item = taglist[i]
		name = item[4]
		if not anchor_types.has_key(name):
			print 'Add html anchor to anchorlist:', name
			anchors.append(name, ATYPE_NORMAL, [])
			anchor_types[name] = ATYPE_NORMAL
		taglist[i] = taglist[i] + (anchor_types[name],)
	if anchors <> oldanchors:
		print 'New anchors:', anchors
		node.SetAttr('anchorlist', anchors)
		MMAttrdefs.flushcache(node)

# Calculate a set of lines from a set of paragraphs, given a font and
# a maximum line width.  Also return mappings between paragraphs and
# line numbers and back: (1) a list containing for each paragraph a
# list of triples (lineno, start, end) where start and end are the
# offset into the paragraph, and (2) a list containing for each line a
# triple (parno, start, end)

def calclines(parlist, sizefunc, limit):
	partoline = []
	linetopar = []
	curlines = []
	for parno in range(len(parlist)):
		par = parlist[parno]
		sublist = []
		partoline.append(sublist) # It will grow while in there
		start = 0
		while 1:
			i = fitwords(par, sizefunc, limit)
			n = len(par)
			while i < n and par[i] == ' ': i = i+1
			sublist.append(len(curlines), start, start+i)
			curlines.append(par[:i])
			linetopar.append((parno, start, start+i))
			par = par[i:]
			start = start + i
			if not par: break
	return curlines, partoline, linetopar


# Find last occurence of space in string such that the size (according
# to some size calculating function) of the initial substring is
# smaller than a given number.  If there is no such substrings the
# first space in the string is returned (if any) otherwise the length
# of the string. Assume sizefunc() is additive:
# sizefunc(s + t) == sizefunc(s) + sizefunc(t)

def fitwords(s, sizefunc, limit):
	words = string.splitfields(s, ' ')
	spw = sizefunc(' ')[0]
	okcount = -1
	totsize = 0
	totcount = 0
	for w in words:
		if w:
			addsize = sizefunc(w)[0]
			if totsize > 0 and totsize + addsize > limit:
				break
			totsize = totsize + addsize
			totcount = totcount + len(w)
			okcount = totcount
		# The space after the word
		totsize = totsize + spw
		totcount = totcount + 1
	if okcount < 0:
		return totcount
	else:
		return okcount

# Map a possibly symbolic font name to a real font name and default point size

fontmap = { \
	'':		('Times-Roman', 12), \
	'default':	('Times-Roman', 12), \
	'plain':	('Times-Roman', 12), \
	'italic':	('Times-Italic', 12), \
	'bold':		('Times-Bold', 12), \
	'courier':	('Courier', 12), \
	'bigbold':	('Times-Bold', 14), \
	'title':	('Times-Bold', 24), \
	  }

def mapfont(fontname):
	if fontmap.has_key(fontname):
		return fontmap[fontname]
	else:
		return fontname, 12
