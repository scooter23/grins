__version__ = "$Id$"


#
#	Export interface 
# 
def WriteFileAsXhtmlSmil(root, filename, cleanSMIL = 0, grinsExt = 1, copyFiles = 0, evallicense = 0, progress = None, convertURLs = 0):
	fp = IndentedFile(open(filename, 'w'))
	try:
		writer = SMILXhtmlSmilWriter(root, fp, filename, cleanSMIL, grinsExt, copyFiles, evallicense, progress = progress, convertURLs = convertURLs)
	except Error, msg:
		from windowinterface import showmessage
		showmessage(msg, mtype = 'error')
		return
	writer.writeAsXhtmlSmil()


not_xhtml_smil_elements = ('prefetch', )

not_xhtml_smil_attrs = ('min', 'max',  'customTest', 'fillDefault', 
	'restartDefault', 'syncBehaviorDefault','syncToleranceDefault', 'repeat',
	#'regPoint', 'regAlign', # we take them into account indirectly
	'close', 'open', 'pauseDisplay',
	'showBackground',
	)

#
#	XHTML+SMIL DTD 
# 
class XHTML_SMIL:

	__Core = {'class':None,
		'id':None,
	}

	__basicTiming = {'begin':None,
		'dur':None,
		'end':None,
		'repeatCount':None,
		'repeatDur':None,
	}

	__Timing = {'restart':None,
		'syncBehavior':None,
		'syncMaster':None,
		'syncTolerance':None,
		'timeAction':'visibility'
	}
	__Timing.update(__basicTiming)


	__TimeManipulators = {'speed':None,
		    'accelerate':None,
		    'decelerate':None,
		    'autoReverse':None,
	}

	__Media = {'abstract':'',
		'author':'',
		'copyright':'',
		'title': '',
		'clipBegin':None,
		'clipEnd':None,
		'fill':None,
		'src':None,
		'type':None,
		'player':None,
		'mute':'false',
		'volume':'1.0',
	}

	__animate_attrs_core = {'attributeName':None,
				'attributeType':None,
				'autoReverse':'false',
				'fill':None,
				'targetElement': None,
				'to':None,
				}

	__animate_attrs_extra = {'accumulate':'none',
				 'additive':'replace',
				 'by':None,
				 'calcMode':'linear',
				 'from':None,
				 'keySplines':None,
				 'keyTimes':None,
				 'values':None,
				 }

	# Elements

	__media_object = ['audio', 'video', 'img', 'animation', 'media', 'ref']

	__animate_elements = ['animate', 'animateMotion', 'animateColor', 'set']

	__containers = ['par', 'seq', 'switch', 'excl''priorityClass', ]



	#
	__allElements = __media_object + __animate_elements + __containers


	def hasElement(self, element):
		return element in __allElements


#
#	SMILXhtmlSmilWriter
# 
from SMILTreeWrite import *

# imported by SMILTreeWrite:
# import string 
# from fmtfloat import fmtfloat 
# from nameencode import nameencode
from fmtfloat import round
import math
import Animators

class SMILXhtmlSmilWriter(SMIL):
	def __init__(self, node, fp, filename, cleanSMIL = 0, grinsExt = 1, copyFiles = 0,
		     evallicense = 0, tmpcopy = 0, progress = None,
		     convertURLs = 0):
		self.smilboston = 1
		self.prune = 0
		self.cleanSMIL = 1

		# some abbreviations
		self.context = ctx = node.GetContext()
		self.hyperlinks = ctx.hyperlinks

		self.root = node
		self.fp = fp
		self.__title = ctx.gettitle()
		self.__animateContext = Animators.AnimateContext(node=node)
		self.copydir = self.copydirurl = self.copydirname = None
		if convertURLs:
			url = MMurl.canonURL(MMurl.pathname2url(filename))
			i = string.rfind(url, '/')
			if i >= 0: url = url[:i+1]
			else: url = ''
			self.convertURLs = url
		else:
			self.convertURLs = None

		self.ids_used = {}

		self.ugr2name = {}
		self.calcugrnames(node)

		self.layout2name = {}
		self.calclayoutnames(node)
		
		self.transition2name = {}
		self.name2transition = {}
		self.calctransitionnames(node)

		# remove next as soon as getRegionFromName becomes obsolete
		self.chnamedict = {} 

		self.ch2name = {}
		self.top_levels = []
		self.calcchnames1(node)

		self.uid2name = {}
		self.calcnames1(node)

		# second pass
		self.calcnames2(node)
		self.calcchnames2(node)

		self.syncidscheck(node)

		self.sensitivityList = []
		self.buildSensitivityList(self.root, self.sensitivityList)

		self.links_target2src = {}
		self.buildAnchorTargets(node)

		self.freezeSyncDict = {}

		self.currLayout = []

		self.__isopen = 0
		self.__stack = []

		self.ids_written = {}
	
		self.__warnings = {}

	def showunsupported(self, key):
		from windowinterface import showmessage
		if not self.__warnings.has_key(key):
			msg = 'Not supported by XHTML+SMIL: %s' % key
			showmessage(msg, mtype = 'warning')
			self.__warnings[key]=1

	def writeAsXhtmlSmil(self):
		write = self.fp.write
		ctx = self.root.GetContext()
		import version
		write('<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\">\n')
		if ctx.comment:
			write('<!--%s-->\n' % ctx.comment)
		self.writetag('html')
		self.push()

		# head
		self.writetag('head')
		self.push()
		
		# head contents
		self.writetag('meta', [('http-equiv', 'content-type'), 
			('content', 'text/html; charset=ISO-8859-1')])
		if self.__title:
			self.writetag('meta', [('name', 'title'),
					       ('content', self.__title)])
		self.writetag('meta', [('name', 'generator'),
				       ('content','GRiNS %s'%version.version)])

		#
		self.writetag('XML:namespace', [('prefix','t'),])

		# style
		self.writetag('style', [('type', 'text/css'),])
		self.push()

		# style contents

		# Internet explorer style conventions for XHTML+SMIL support
		write('.time {behavior: url(#default#time2); }\n')
		write('t\:*  {behavior: url(#default#time2); }\n') # or part 2 below
		
		self.pop() # style

		self.pop() # head

		# body
		self.writetag('body')
		self.push()
		
		# body contents
		self.writeToplayout()
		self.writenode(self.root, root = 1)
		self.close()

	def push(self):
		if self.__isopen:
			self.fp.write('>\n')
			self.__isopen = 0
		self.fp.push()

	def pop(self):
		fp = self.fp
		if self.__isopen:
			fp.write('/>\n')
			self.__isopen = 0
			del self.__stack[-1]
		fp.pop()
		fp.write('</%s>\n' % self.__stack[-1])
		del self.__stack[-1]

	def close(self):
		fp = self.fp
		if self.__isopen:
			fp.write('/>\n')
			self.__isopen = 0
			del self.__stack[-1]
		while self.__stack:
			self.pop()
		fp.close()

	def writecomment(self, x):
		write = self.fp.write
		if self.__isopen:
			write('/>\n')
			self.__isopen = 0
			del self.__stack[-1]
		write('<!--%s-->\n' % string.join(x.values, '\n'))

	def writetag(self, tag, attrs = None):
		if attrs is None:
			attrs = []
		write = self.fp.write
		if self.__isopen:
			write('/>\n')
			self.__isopen = 0
			del self.__stack[-1]
		write('<' + tag)
		for attr, val in attrs:
			write(' %s=%s' % (attr, nameencode(val)))
		self.__isopen = 1
		self.__stack.append(tag)

	def closehtmltag(self, expl=1):
		write = self.fp.write
		if self.__isopen:
			if expl:
				write('></%s>\n' % self.__stack[-1])
			else:
				write('>\n')
			self.__isopen = 0
			del self.__stack[-1]

	def pushviewport(self, viewport):
		style = self.getViewportStyle(viewport)
		name = self.ch2name[viewport]
		self.writetag('div', [('id',name), ('style', style),])
		self.push()
		self.currLayout = [viewport]
				
	def popviewport(self):
		self.pop()
		self.currLayout = []

	def writeToplayout(self):
		hasSingleTopLayout  = (len(self.top_levels) == 1)
		style = self.getLayoutStyle()
		self.writetag('div', [('id','xhtml_smil_export'), ('style', style),])
		self.push()
		if hasSingleTopLayout:
			self.pushviewport(self.top_levels[0])
		else:
			for v in self.top_levels:
				self.pushviewport(v)
				self.popviewport()

	def issensitive(self, node):
		return node in self.sensitivityList

	def writenode(self, x, root = 0):
		type = x.GetType()

		if type == 'comment':
			self.writecomment(x)
			return

		if type == 'animate':
			self.writeanimatenode(x, root)
			return

		####
		attrlist = []
		interior = (type in interiortypes)
		if interior:
			if type == 'prio':
				xtype = mtype = 'priorityClass'
			elif type == 'foreign':
				tag = x.GetRawAttrDef('tag', None)
				if ' ' in tag:
					ns, tag = string.split(tag, ' ', 1)
					xtype = mtype = 'foreign:%s' % tag
					attrlist.append(('xmlns:foreign', ns))
				else:
					ns = ''
					xtype = mtype = tag
			else:
				xtype = mtype = type
		else:
			chtype = x.GetChannelType()
			if not chtype:
				chtype = 'unknown'
			mtype, xtype = mediatype(x)
		
		# if node used as destination, make sure it's id is written
		uid = x.GetUID()
		name = self.uid2name[uid]
		if not self.ids_used[name] and self.hyperlinks.finddstlinks(x):
			self.ids_used[name] = 1

		####
		attributes = self.attributes.get(xtype, {})
		if type == 'prio':
			attrs = prio_attrs
		elif type == 'foreign':
			attrs = []
			extensions = {ns: 'foreign'}
			for attr, val in x.attrdict.items():
				if attr == 'tag':
					continue
				if ' ' in attr:
					ans, attr = string.split(attr, ' ', 1)
					if not extensions.has_key(ans):
						extensions[ans] = 'x%s' % len(extensions)
						attrlist.append(('xmlns:%s' % extensions[ans], ans))
					attr = '%s:%s' % (extensions[ans], attr)
				attrlist.append((attr, val))
		else:
			attrs = smil_attrs
			# special case for systemRequired
			sysreq = x.GetRawAttrDef('system_required', [])
			for i in range(len(sysreq)):
				attrlist.append(('ext%d' % i, sysreq[i]))

		####
		regionName = None
		nodeid = None
		transIn = None
		transOut = None
		fill = None
		hasfill = 0
		for name, func, keyToCheck in attrs:
			if keyToCheck is not None and not x.attrdict.has_key(keyToCheck):
				continue
			value = func(self, x)
			if value and attributes.has_key(name) and value != attributes[name]:				

				if name == 'fill':
					hasfill = 1
					fill = value

				# endsync translation
				if name == 'endsync' and value not in ('first' , 'last'):
					name = 'end'
					value = value + '.end'

				# activateEvent exception
				elif name == 'end' and value == 'activateEvent':
					name = 'onClick'
					value = 'endElement();'

				elif name == 'src' and value[:8] == 'file:///' and value[9:10] == '|':
					value = 'file:///' + value[8] + ':' + value[10:]
						
				# for the rest
				else:
					# convert event refs
					if value: 
						value = event2xhtml(value)
						value = replacePrevShortcut(value, x)
					 
				if interior:
					if name == 'fillDefault':
						pass
					elif name == 'id':
						attrlist.append((name, value))
						self.ids_written[value] = 1
						nodeid = value
					else:
						attrlist.append((name, value))
				else:	
					if name == 'region': 
						regionName = value
					elif name == 'id':
						self.ids_written[value] = 1
						nodeid = value
					elif name == 'transIn':
						transIn = value
					elif name == 'transOut':
						transOut = value
					elif name == 'backgroundColor':
						pass
					elif name == 'fill':
						pass
					elif name == 'fit':
						pass
					elif name in ('regPoint', 'regAlign'):
						pass # taken into account indirectly
					elif not name in ('top','left','width','height','right','bottom'):
						attrlist.append((name, value))

		if not hasfill:
			# no fill attr, be explicit about fillDefault value
			fillDefault = MMAttrdefs.getattr(x, 'fillDefault')
			if fillDefault != 'inherit':
				hasfill = 1
				if interior:
					attrlist.append(('fill', fillDefault))
				else:
					fill = fillDefault

		if not nodeid:
			nodeid = 'm' + x.GetUID()
			if interior:
				attrlist.append(('id', nodeid))

		if self.links_target2src.has_key(x):
			self.fixBeginList(x, attrlist)

		####
		if interior:
			if mtype in not_xhtml_smil_elements:
				pass # self.showunsupported(mtype)

			if ':' in mtype:
				self.writetag(mtype, attrlist)
			else:
				# IE hack first please!
				# set fill = 'freeze' if last visible child has it
				if mtype == 'seq' and not hasfill:
					self.applyFillHint(x, attrlist)
				# normal
				self.writetag('t:' + mtype, attrlist)
			self.push()
			for child in x.GetChildren():
				self.writenode(child)
			if self.freezeSyncDict.has_key(x):
				transOut, trnodeid, trregionid = self.freezeSyncDict[x]
				self.writeTransition(None, transOut, trnodeid, nodeid)
			self.pop()

		elif type in ('imm', 'ext', 'brush'):
			if mtype in not_xhtml_smil_elements:
				self.showunsupported(mtype)
			self.writemedianode(x, nodeid, attrlist, mtype, regionName, transIn, transOut, fill)

		elif type != 'animpar':
			raise CheckError, 'bad node type in writenode'

	def writemedianode(self, node, nodeid, attrlist, mtype, regionName, transIn, transOut, fill):
		pushed, inpar, pardur, regionid = 0, 0, None, ''
		
		# write media node layout
		pushed, inpar, pardur, regionid  = \
			self.writeMediaNodeLayout(node, nodeid, attrlist, mtype, regionName, transIn, transOut, fill)

		# apply subregion's style
		self.applySubregionStyle(node, nodeid, attrlist, mtype)

		# write anchors
		hasAnchors = self.writeAnchors(node, nodeid)
		if hasAnchors:
			attrlist.append(('usemap', '#'+nodeid+'map'))

		# extent conditionally the node to a time container
		if self.hasTimeChildren(node) and not inpar:
			attrlist.append(('timeContainer', 'par'))

		# write media node
		sensitive = self.issensitive(node)
		if mtype == 'brush':
			if sensitive:
				self.writetag('a', [('href', '#')])
				self.push()
				self.writetag('div', attrlist)
				self.closehtmltag()
				self.pop()
			elif hasAnchors:
				self.writetag('div', attrlist)
				self.closehtmltag()
			else:
				attrlist.append( ('class','time') )
				self.writetag('div', attrlist)
				self.closehtmltag()

		elif mtype == 'img':
			if sensitive:
				self.writetag('a', [('href', '#')])
				self.push()
				self.writetag(mtype, attrlist)
				self.pop()
			elif hasAnchors:
				self.writetag(mtype, attrlist)
			else:
				self.writetag('t:'+mtype, attrlist)

		elif mtype == 'text' and node.GetType() == 'imm':
			self.removeAttr(attrlist, 'src')
			self.writetag('div', attrlist)
			self.push()
			self.fp.write('<p>')
			text = string.join(node.GetValues(), '\n')
			if text:
				text = nameencode(text)
				self.fp.write(text[1:-1])
			self.fp.write('</p>')
			self.pop()

		else:
			self.writetag('t:'+mtype, attrlist)
		
		# write not anchors children (animations, etc)
		self.writeChildren(node)

		# write transition(s)
		if transIn or transOut:
			if not regionid:
				regionid = nodeid
			if transIn and not transOut:
				self.writeTransition(transIn, None, nodeid, regionid)
			elif transOut and not transIn:
				self.writeTransition(None, transOut, nodeid, regionid)
			else:
				self.writeTransition(transIn, None, nodeid, regionid)
				freezeSync = None
				if fill == 'freeze':
					freezeSync = self.locateFreezeSyncNode(node)
				if freezeSync is None:
					self.writeTransition(None, transOut, nodeid, regionid)
				else:
					self.freezeSyncDict[freezeSync] = transOut, nodeid, regionid

		# restore stack
		while pushed:
			self.pop()
			pushed = pushed - 1

	def writeMediaNodeLayout(self, node, nodeid, attrlist, mtype, regionName, transIn, transOut, fill):
		pushed, inpar, pardur, regionid = 0, 0, None, ''
		
		# optional: ignore smil layout for audio
		if mtype == 'audio':
			return pushed, inpar, pardur, regionid

		lch = node.GetChannel().GetLayoutChannel()
		path = self.getRegionPath(lch)
		if not path:
			print 'error: failed to get region path for', regionName
			return pushed, inpar, pardur, regionid

		# region (div) attr list
		divlist = []

		currViewport, currRegion = path[0], path[len(path)-1]
		prevViewport, prevRegion = None, None
		if self.currLayout:
			n = len(self.currLayout)
			prevViewport = self.currLayout[0]
			prevRegion = self.currLayout[n-1]

		# find/compose/set region id
		name = self.ch2name[currRegion]
		if self.ids_written.get(name):
			self.ids_written[name] = self.ids_written[name] + 1
			regionid = name + '%d' % self.ids_written[name]
		else:
			self.ids_written[name] = 1
			regionid = name
		divlist.append(('id', regionid))

		# apply region style and fill attribute
		prevRegion = None
		if self.currLayout:
			n = len(self.currLayout)
			prevRegion = self.currLayout[n-1]
		forceTransparent = (prevRegion == currRegion or mtype == 'audio')
		regstyle = self.getRegionStyle(lch, node, forceTransparent)
		if regstyle is not None:
			divlist.append(('style', regstyle))
		divlist.append(('class', 'time'))
		if fill:
			divlist.append(('fill', fill))
				
		# transfer timing from media to div
		# the composite is the item for xhtml+smil
		timing_spec = 0 				
		i = 0
		while i < len(attrlist):
			attr, val = attrlist[i]
			if attr in ('begin', 'dur', 'end'):
				timing_spec = timing_spec + 1
				divlist.append((attr, val))
				del attrlist[i]
				if attr == 'dur':
					pardur = val
			else:
				i = i + 1

		# Duration hint for IE scheduler when dur attr has 
		# not been given and not both begin and end.
		# Possibly temporary until we find a way to make it needless			
		if pardur is None and timing_spec < 2 and not (timing_spec == 0 and mtype == 'img'):
			val = self.getDurHint(node)
			if val > 0:
				pardur = fmtfloat(val, prec = 2)
				divlist.append(('dur', pardur))
				timing_spec = timing_spec + 1
		
		# when div has timing extent it to a time container
		if timing_spec > 0 or self.hasTimeChildren(node):
			divlist.append( ('timeContainer', 'par'))
			inpar = 1
			
		# finally write div
		self.writetag('div', divlist)
		self.push()
		pushed = 1
		self.currLayout = path
		return pushed, inpar, pardur, regionid


	def applySubregionStyle(self, node, nodeid, attrlist, mtype):
		subRegGeom, mediaGeom = None, None
		try:
			geoms = node.getPxGeomMedia()
		except:
			geoms = None
		if geoms and mtype != 'audio':
			subRegGeom, mediaGeom = geoms
			x, y, w, h = subRegGeom
			xm, ym, wm, hm = mediaGeom
			mediarc = x, y, wm, hm
		else:
			mediarc = None
		if mediarc:
			if nodeid:
				attrlist.insert(0,('id', nodeid))
			style = self.rc2style(mediarc)
			if mtype == 'brush':
				color = self.removeAttr(attrlist, 'color')
				if color is not None:
					style = style + 'background-color:%s;' % color
			attrlist.append( ('style', style) )


	def rc2style(self, rc):
		x, y, w, h = rc
		return 'position:absolute;overflow:hidden;left:%d;top:%d;width:%d;height:%d;' % (x, y, w, h)

	def getNodeMediaRect(self, node):
		subRegGeom, mediaGeom = None, None
		try:
			geoms = node.getPxGeomMedia()
		except:
			return 0, 0, 100, 100
		else:
			subRegGeom, mediaGeom = geoms
			x, y, w, h = subRegGeom
			xm, ym, wm, hm = mediaGeom
			return 0, 0, wm, hm

	def writeTransition(self, transIn, transOut, nodeid, regionid):
		transitions = self.root.GetContext().transitions
		quotedname = transIn or transOut
		name = self.name2transition[quotedname]
		td = transitions.get(name)
		if not td:
			trtype = 'barWipe'
			subtype = None
			dur = 1
			direction = None
		else:
			trtype = td.get('trtype')
			subtype = td.get('subtype')
			dur = td.get('dur')
			direction = td.get('direction')
		if not dur: dur = 1
		elif dur<=0: dur = 0.1
		trattrlist = []
		trattrlist.append( ('type', trtype) )
		if subtype is not None:
			trattrlist.append( ('subtype',subtype) )
		trattrlist.append( ('targetElement',nodeid) )
		trattrlist.append( ('dur','%.1f' % dur) )
		if transIn:
			trattrlist.append( ('begin', regionid + '.begin') )
			trattrlist.append( ('mode', 'in') )
		elif transOut:
			trattrlist.append( ('begin', regionid + '.end-%.1f' % dur) )
			trattrlist.append( ('mode', 'out') )
		if direction == 'reverse':
			trattrlist.append( ('from','1') )
			trattrlist.append( ('to','0') )
		else:
			trattrlist.append( ('from','0') )
			trattrlist.append( ('to','1') )
		self.writetag('t:transitionFilter', trattrlist)

	def writeChildren(self, node):
		pushed = 0
		for child in node.GetChildren():
			type = child.GetType()
			if type != 'anchor':
				if not pushed:
					self.push()
					pushed = 1
				self.writenode(child)
		if pushed:
			self.pop()

	def hasTimeChildren(self, node):
		for child in node.GetChildren():
			type = child.GetType()
			if type != 'anchor':
				return 1
		return 0

	def removeAttr(self, attrlist, attrname):
		val = None
		i = 0
		while i < len(attrlist):
			a, v = attrlist[i]
			if a == attrname:
				val = v
				del attrlist[i]
				break
			i = i + 1
		return val

	def replaceAttrVal(self, attrlist, attrname, attrval):
		val = None
		i = 0
		while i < len(attrlist):
			a, v = attrlist[i]
			if a == attrname:
				attrlist[i] = a, attrval
				val = v
				break
			i = i + 1
		if val is None:
			attrlist.append((attrname, attrval))	
		return val

	# set fill = 'freeze' if last visible child has it
	def applyFillHint(self, x, attrlist):
		if x.GetChildren():
			children = x.GetChildren()[:]
			children.reverse()
			for i in range(len(children)):
				last = children[i]
				if last.GetType() != 'audio':
					lastfill = MMAttrdefs.getattr(last, 'fill')
					if lastfill == 'freeze':
						attrlist.append( ('fill', 'freeze') )
					break

	def locateFreezeSyncNode(self, node):
		fill = MMAttrdefs.getattr(node, 'fill')
		if fill != 'freeze':
			return None
		# XXX: find freeze sync
		parent = node.GetParent()
		if parent.GetType() == 'seq':
			return parent.GetParent()

	# XXX: needs to be implemented correctly
	# or find a way to make needless
	def getDurHint(self, node):
		try:
			t0, t1, t2, downloadlag, begindelay = node.GetTimes()
			val = t1 - t0
		except: 
			val = 2.0
		return val

	def fixBeginList(self, node, attrlist):
		srcid = self.links_target2src.get(node)
		if srcid is None:
			return
		bl = self.removeAttr(attrlist, 'begin')
		if bl is None:
			parent = node.GetParent()
			if parent.GetType() == 'par':
				bl = '0;%s.click' % srcid
				attrlist.append(('begin', bl))
			elif parent.GetType() == 'seq':
				prev = self.getPreviousSibling(node)
				if prev is not None:
					previd = identify(self.getNodeId(prev))
					bl = '%s.end;%s.click' % (previd, srcid)
				else:
					bl = '0;%s.click' % srcid
				attrlist.append(('begin', bl))
		else:
			if bl[-1] != ';':
				bl = bl + ';'
			bl = bl = '%s.click' % srcid
			attrlist.append(('begin', bl))


	def toPxStr(self, c, d):
		if type(c) is type(0):
			# pixel coordinates
			return '%d' % c
		else:
			# relative coordinates
			return '%d' % round(c*d)

	def toPixelCoordsStrs(self, ashape, acoords, width, height):
		relative = 0
		coords = []
		for c in acoords:
			if type(c) is type(0):
				coords.append('%d' % c)
			else:
				relative = 1
				break
		if not relative:
			return coords
		toPxStr = self.toPxStr
		if ashape == 'rect' or ashape == 'rectangle':
			l, t, r, b = acoords
			coords = [toPxStr(l, width), toPxStr(t, height), toPxStr(r, width), toPxStr(b, height)]
		elif ashape == 'circ' or ashape == 'circle':
			xc, yc, r = acoords
			coords = [toPxStr(xc, width), toPxStr(yc, height), toPxStr(r, (width+height)/2)]
		else: # elif ashape == 'poly':
			i = 0
			while i < len(acoords)-1:
				x, y = toPxStr(acoords[i], width), toPxStr(acoords[i+1], height)
				coords.append(x)
				coords.append(y)
				i = i + 2
		return coords

	def writeAnchors(self, node, name):
		hassrc = 0
		x, y, w, h = 0, 0, 1, 1
		for anchor in node.GetChildren():
			if anchor.GetType() != 'anchor':
				continue
			links = self.hyperlinks.findsrclinks(anchor)
			if not links:
				continue
			if len(links) > 1:
				print '** Multiple links on anchor', \
				      anchor.GetRawAttrDef('name', '<unnamed>'), \
				      anchor.GetUID()
			if not hassrc:
				hassrc = 1
				x, y, w, h = self.getNodeMediaRect(node)
				self.writetag('map', [('id', name+'map')])
				self.push()
			a1, a2, dir, ltype, stype, dtype = links[0]
			attrlist = []
			id = getid(self, anchor)
			if id is None:
				id = 'a' + node.GetUID()
			attrlist.append(('id', id))
			attrlist.extend(self.linkattrs(a2, ltype, stype, dtype))
			fragment = MMAttrdefs.getattr(anchor, 'fragment')
			if fragment:
				attrlist.append(('fragment', fragment))

			shape = MMAttrdefs.getattr(anchor, 'ashape')
			attrlist.append(('shape', shape))

			acoords =  MMAttrdefs.getattr(anchor, 'acoords')
			if not acoords:
				acoords = [x, y, x+w, y+h]
			coords = self.toPixelCoordsStrs(shape, acoords, w, h)
			if coords:
				attrlist.append(('coords', ','.join(coords)))

			begin = getsyncarc(self, anchor, 0)
			if begin is not None:
				attrlist.append(('begin', begin))
			end = getsyncarc(self, anchor, 1)
			if end is not None:
				attrlist.append(('end', end))

			actuate = MMAttrdefs.getattr(anchor, 'actuate')
			if actuate != 'onRequest':
				attrlist.append(('actuate', actuate))

			accesskey = anchor.GetAttrDef('accesskey', None)
			if accesskey is not None:
				attrs.append(('accesskey', accesskey))

			self.writetag('area', attrlist)
			self.closehtmltag(0)

		if hassrc:
			self.pop()
		return hassrc
				
	def writeEmptyRegion(self, region):
		if region is None:
			return
		path = self.getRegionPath(region)
		if not path:
			print 'failed to get region path for', region
			return

		# region (div) attr list
		divlist = []

		# find/compose/set region id
		lch = path[len(path)-1]
		name = self.ch2name[lch]
		if self.ids_written.get(name):
			self.ids_written[name] = self.ids_written[name] + 1
			regionid = name + '%d' % self.ids_written[name]
		else:
			self.ids_written[name] = 1
			regionid = name
		divlist.append(('id', regionid))

		# apply region style and fill attribute
		regstyle = self.getRegionStyle(lch)
		if regstyle is not None:
			divlist.append(('style', regstyle))
		divlist.append(('class', 'time'))
							
		# finally write div
		self.writetag('div', divlist)
		self.closehtmltag()

	def writeanimatenode(self, node, root, targetElement=None):
		attrlist = []
		if targetElement is not None:
			attrlist.append(('targetElement', targetElement))
		tag = node.GetAttrDict().get('atag')

		if tag == 'animateMotion':
			from Animators import AnimateElementParser
			aparser = AnimateElementParser(node, self.__animateContext)
			isAdditive = aparser.isAdditive()
			fromxy = aparser.toDOMOriginPosAttr('from')
			toxy = aparser.toDOMOriginPosAttr('to')
			values = aparser.toDOMOriginPosValues()
			path = aparser.toDOMOriginPath()

		hasid = 0
		attributes = self.attributes.get(tag, {})
		for name, func, gname in smil_attrs:
			if attributes.has_key(name):
				if name == 'type':
					value = node.GetRawAttrDef("trtype", None)
				else:
					value = func(self, node)
				if targetElement is None and name == 'targetElement':
					targetElement = value
					value = value
				if tag == 'animateMotion' and not isAdditive:
					if name == 'from':value = fromxy
					elif name == 'to':value = toxy
					elif name == 'values':value = values
					elif name == 'path': value = path
				if name == 'id':
					hasid = 1
				if value and value != attributes[name]:
					if name in ('begin', 'end'):
						value = event2xhtml(value)
						value = replacePrevShortcut(value, node)
					attrlist.append((name, value))
		if not hasid:
			id = 'm' + node.GetUID()
			attrlist.append( ('id', id))
		if not self.ids_written.has_key(targetElement):
			region = self.getRegionFromName(targetElement)
			self.writeEmptyRegion(region)
		self.writetag('t:'+tag, attrlist)
	
	def getLayoutStyle(self):
		x, y = 20, 20
		xmargin, ymargin = 20, 20
		v = self.top_levels[0]
		tw, th = v.getPxGeom()
		for v in self.top_levels[1:]:
			tw = tw + xmargin
			w, h = v.getPxGeom()
			tw = tw + w
		style = 'position:absolute;overflow:hidden;left:%d;top:%d;width:%d;height:%d;' % (x, y, tw, th)
		return style
			
	def getViewportOffset(self, viewport):
		x, y = 0, 0
		xmargin, ymargin = 20, 20
		viewports = self.top_levels
		try:
			index = viewports.index(viewport)
		except:
			index = 0
		for i in range(index):
			v = viewports[i]
			w, h = v.getPxGeom()
			x = x + w + xmargin
		return x, y

	def getViewportStyle(self, viewport, forcetransparent = 0):
		x, y = self.getViewportOffset(viewport)
		w, h = viewport.getPxGeom()
		style = 'position:absolute;overflow:hidden;left:%d;top:%d;width:%d;height:%d;' % (x, y, w, h)
		if not forcetransparent:
			if viewport.has_key('bgcolor'):
				bgcolor = viewport['bgcolor']
			else:
				bgcolor = 255,255,255
			if colors.rcolors.has_key(bgcolor):
				bgcolor = colors.rcolors[bgcolor]
			else:
				bgcolor = '#%02x%02x%02x' % bgcolor
			style = style + 'background-color:%s;' % bgcolor
		return style

	def getRegionStyle(self, region, node = None, forcetransparent = 0):
		if region in self.top_levels:
			return self.getViewportStyle(region, forcetransparent)
		path = self.getRegionPath(region)
		if not path: 
			return None
		ch = path[len(path)-1]
		x, y, w, h = ch.getPxGeom()
		dx, dy = 0, 0
		if len(self.top_levels) > 1:
			dx, dy = self.getViewportOffset(path[0])
		if node:
			fit = MMAttrdefs.getattr(node, 'fit')
		else:
			fit = 'hidden'
		overflow = self.getoverflow(fit)
		style = 'position:absolute;overflow:%s;left:%d;top:%d;width:%d;height:%d;' % (overflow, dx+x, dy+y, w, h)
		transparent = ch.get('transparent', None)
		bgcolor = ch.get('bgcolor', None)
		if bgcolor and transparent==0 and not forcetransparent:
			if colors.rcolors.has_key(bgcolor):
				bgcolor = colors.rcolors[bgcolor]
			else:
				bgcolor = '#%02x%02x%02x' % bgcolor
			style = style + 'background-color:%s;' % bgcolor
		z = ch.get('z', 0)
		if z > 0:
			style = style + 'z-index:%d;' % z
		return style

	def getoverflow(self, fit):
		# overflow in ('visible', 'scroll', 'hidden', 'auto')
		# valid for us are: 'hidden', 'auto'
		overflow = 'hidden'
		if fit == 'fill':
			overflow = 'hidden'
		elif fit == 'hidden':
			overflow = 'hidden'
		elif fit == 'meet':
			overflow = 'hidden'
		elif fit == 'scroll':
			overflow = 'auto'
		elif fit == 'slice':
			overflow = 'hidden'
		return overflow

	def getRegionPath(self, lch):
		path = []
		while lch:
			if lch.get('type') == 'layout':
				path.insert(0, lch)
			lch = lch.GetParent()
		return path
		
	# temporal for writing empty regions 
	# XXX: should be avoided 
	def getRegionFromName(self, regionName):
		lch = self.context.getchannel(regionName)
		if lch is None:
			regionName = self.chnamedict.get(regionName)
			lch = self.context.getchannel(regionName)
		return lch

	def getPreviousSibling(self, node):
		parent = node.GetParent()
		prev = None
		for child in parent.GetChildren():
			if child == node:
				break
			prev = child
		return prev

	def getNodeId(self, node):
		id = node.GetRawAttrDef('name', None)
		if not id:
			id = 'm' + node.GetUID()
		return id

	def linkattrs(self, a2, ltype, stype, dtype):
		attrs = []
		if ltype == Hlinks.TYPE_JUMP:
			# default value, so we don't need to write it
			pass
		elif ltype == Hlinks.TYPE_FORK:
			attrs.append(('show', 'new'))
			if stype == Hlinks.A_SRC_PLAY:
				# default sourcePlaystate value
				pass
			elif stype == Hlinks.A_SRC_PAUSE:
				attrs.append(('sourcePlaystate', 'pause'))			
			elif stype == Hlinks.A_SRC_STOP:
				attrs.append(('sourcePlaystate', 'stop'))
		
		if dtype == Hlinks.A_DEST_PLAY:
			# default value, so we don't need to write it
			pass
		elif dtype == Hlinks.A_DEST_PAUSE:
			attrs.append(('destinationPlaystate', 'pause'))
							
		# else show="replace" (default)
		if type(a2) is type(''):
			attrs.append(('href', a2))
		else:
			target =  self.uid2name[a2.GetUID()]
			attrs.append(('href', '#%s' % target))
			# attrs.append(('onclick', '%s.beginElement();' % target))
		return attrs

	#
	#
	#
	def buildSensitivityList(self, parent, sensitivityList):
		import MMTypes
		for node in parent.children:
			ntype = node.GetType()
			for arc in node.attrdict.get('beginlist', []) + node.attrdict.get('endlist', []):
				if arc.event == 'activateEvent':
					sensitivityList.append(arc.srcnode)
			self.buildSensitivityList(node, sensitivityList)

	def buildAnchorTargets(self, node):
		ntype = node.GetType()
		interior = (ntype in interiortypes)
		if interior:
			for child in node.GetChildren():
				self.buildAnchorTargets(child)
		elif ntype in ('imm', 'ext', 'brush'):
			for anchor in node.GetChildren():
				if anchor.GetType() != 'anchor':
					continue
				links = self.hyperlinks.findsrclinks(anchor)
				if not links:
					continue
				a1, a2, dir, ltype, stype, dtype = links[0]
				id = getid(self, anchor)
				if id is None:
					id = 'a' + node.GetUID()
				if type(a2) is not type(''):
					self.links_target2src[a2] = id
					 
	def calcugrnames(self, node):
		# Calculate unique names for usergroups
		usergroups = node.GetContext().usergroups
		if not usergroups:
			return
		for ugroup in usergroups.keys():
			name = identify(ugroup, html = 1)
			if self.ids_used.has_key(name):
				i = 0
				nn = '%s_%d' % (name, i)
				while self.ids_used.has_key(nn):
					i = i+1
					nn = '%s_%d' % (name, i)
				name = nn
			self.ids_used[name] = 1
			self.ugr2name[ugroup] = name

	def calclayoutnames(self, node):
		# Calculate unique names for layouts
		layouts = node.GetContext().layouts
		if not layouts:
			return
		self.uses_grins_namespaces = 1
		for layout in layouts.keys():
			name = identify(layout, html = 1)
			if self.ids_used.has_key(name):
				i = 0
				nn = '%s_%d' % (name, i)
				while self.ids_used.has_key(nn):
					i = i+1
					nn = '%s_%d' % (name, i)
				name = nn
			self.ids_used[name] = 1
			self.layout2name[layout] = name

	def calctransitionnames(self, node):
		# Calculate unique names for transitions
		transitions = node.GetContext().transitions
		if not transitions:
			return
		for transition in transitions.keys():
			name = identify(transition, html = 1)
			if self.ids_used.has_key(name):
				i = 0
				nn = '%s_%d' % (name, i)
				while self.ids_used.has_key(nn):
					i = i+1
					nn = '%s_%d' % (name, i)
				name = nn
			self.ids_used[name] = 1
			self.transition2name[transition] = name
			self.name2transition[name] = transition

	def calcnames1(self, node):
		# Calculate unique names for nodes; first pass
		uid = node.GetUID()
		name = node.GetRawAttrDef('name', '')
		if name:
			name = identify(name, html = 1)
			if not self.ids_used.has_key(name):
				self.ids_used[name] = 1
				self.uid2name[uid] = name
		ntype = node.GetType()
		if ntype in interiortypes:
			for child in node.children:
				self.calcnames1(child)
				for c in child.children:
					self.calcnames1(c)

	def calcnames2(self, node):
		# Calculate unique names for nodes; second pass
		uid = node.GetUID()
		name = node.GetRawAttrDef('name', '')
		if not self.uid2name.has_key(uid):
			isused = name != ''
			if isused:
				name = identify(name, html = 1)
			else:
				name = 'node'
			# find a unique name by adding a number to the name
			i = 0
			nn = '%s_%d' % (name, i)
			while self.ids_used.has_key(nn):
				i = i+1
				nn = '%s_%d' % (name, i)
			name = nn
			self.ids_used[name] = isused
			self.uid2name[uid] = name
		if node.GetType() in interiortypes:
			for child in node.children:
				self.calcnames2(child)
				for c in child.children:
					self.calcnames2(c)

	def calcchnames1(self, node):
		# Calculate unique names for channels; first pass
		context = node.GetContext()
		channels = context.channels
		for ch in channels:
			name = identify(ch.name, html = 1)
			if not self.ids_used.has_key(name):
				self.ids_used[name] = 0
				self.ch2name[ch] = name
				self.chnamedict[name] = ch.name
			if ch.GetParent() is None and \
			   ChannelMap.isvisiblechannel(ch['type']):
				# top-level channel with window
				self.top_levels.append(ch)
				if not self.__title:
					self.__title = ch.name
		if not self.__title and channels:
			# no channels with windows, so take very first channel
			self.__title = channels[0].name

	def calcchnames2(self, node):
		# Calculate unique names for channels; second pass
		context = node.GetContext()
		channels = context.channels
		for ch in context.getviewports():
			if ChannelMap.isvisiblechannel(ch['type']):
				# first top-level channel
				top0 = ch.name
				break
		else:
			top0 = None
		for ch in channels:
			if not self.ch2name.has_key(ch):
				name = identify(ch.name, html = 1)
				i = 0
				nn = '%s_%d' % (name, i)
				while self.ids_used.has_key(nn):
					i = i+1
					nn = '%s_%d' % (name, i)
				name = nn
				self.ids_used[name] = 0
				self.ch2name[ch] = name
				self.chnamedict[name] = ch.name

	# copied from SMILTreeWrite.py
	def syncidscheck(self, node):
		# make sure all nodes referred to in sync arcs get their ID written
		for arc in node.GetRawAttrDef('beginlist', []) + node.GetRawAttrDef('endlist', []):
			# see also getsyncarc() for similar code
			if arc.srcnode is None and arc.event is None and arc.marker is None and arc.wallclock is None and arc.accesskey is None:
				pass
			elif arc.wallclock is not None:
				pass
			elif arc.accesskey is not None:
				pass
			elif arc.marker is None:
				srcnode = arc.srcnode
				if type(srcnode) is type('') and srcnode not in ('prev', 'syncbase'):
					srcnode = arc.refnode()
					if srcnode is None:
						continue
				if arc.channel is not None:
					pass
				elif srcnode in ('syncbase', 'prev'):
					pass
				elif srcnode is not node:
					self.ids_used[self.uid2name[srcnode.GetUID()]] = 1
			else:
				self.ids_used[self.uid2name[arc.srcnode.GetUID()]] = 1
		for child in node.children:
			self.syncidscheck(child)


#
#   Util
#
smil20event2xhtml = {'.activateEvent':'.click', '.beginEvent':'.begin', '.endEvent':'.end'}
def event2xhtml(value):
	if not value: 
		return value
	for ev in smil20event2xhtml.keys():	
		l = string.split(value, ev)
		if len(l)==2:
			return l[0]+smil20event2xhtml[ev] + l[1]
	return value

def replacePrevShortcut(value, node):
	if value.find('prev.') != 0:
		return value
	parent = node.GetParent()
	prev = parent
	for child in parent.GetChildren():
		if child == node:
			break
		prev = child
	id = prev.GetRawAttrDef('name', None)
	if not id:
		id = 'm' + prev.GetUID()
	return id + value[4:]
	
	

