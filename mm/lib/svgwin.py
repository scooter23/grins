__version__ = "$Id$"

#
#	Windows SVG module
#

import svggraphics
import svgtypes

import wingdi

import win32con

import math


class SVGWinGraphics(svggraphics.SVGGraphics):
	#
	#  platform toolkit interface
	#
	# called to intialize platform toolkit before rendering
	def tkStartup(self, params):
		hdc = params
		self.hdc = hdc

		# context vars
		self.tk = Tk()
		self.tk.saveid = wingdi.SaveDC(hdc)
		self._tkstack = []

		wingdi.SetGraphicsMode(hdc, win32con.GM_ADVANCED)
		wingdi.SetBkMode(hdc, win32con.TRANSPARENT)
		wingdi.SetTextAlign(hdc, win32con.TA_BASELINE)

	# called to dispose platform toolkit objects after rendering
	def tkShutdown(self):
		wingdi.SetGraphicsMode(self.hdc, win32con.GM_COMPATIBLE)
		wingdi.SetMapMode(self.hdc, win32con.MM_TEXT) 
		wingdi.RestoreDC(self.hdc, self.tk.saveid)

	# we start rendering
	def tkOnBeginRendering(self, size, viewbox):
		cx, cy = size
		wingdi.SetMapMode(self.hdc, win32con.MM_ISOTROPIC)
		vcx, vcy = wingdi.GetViewportExtEx(self.hdc)
		if vcy<0: vcy = -vcy
		wingdi.SetWindowExtEx(self.hdc, (vcx, vcy))
		wingdi.SetViewportExtEx(self.hdc, (vcx, vcy))
		wingdi.SetViewportOrgEx(self.hdc, (0, 0))
		wingdi.Rectangle(self.hdc, (0, 0, cx, cy))

	# we finished rendering
	def tkOnEndRendering(self):
		pass

	# new graphics context
	# self state reflects this new context
	def tkOnBeginContext(self):
		# push current tkctx
		self.saveTk()

		# save dc and hold its id for restore
		self.tk.saveid = wingdi.SaveDC(self.hdc)
		
		# establish tk pen
		stroke = self.getStyleAttr('stroke')
		strokeWidth = self.getStyleAttr('stroke-width')
		if stroke is not None and stroke!='none':
			self.tk.pen = wingdi.ExtCreatePen(strokeWidth, stroke)
			wingdi.SelectObject(self.hdc, self.tk.pen)

		# establish tk brush
		fill = self.getStyleAttr('fill')
		if fill is not None and fill != 'none':
			self.tk.brush = wingdi.CreateSolidBrush(fill)
			wingdi.SelectObject(self.hdc, self.tk.brush)

		# establish tk font
		fontFamily = self.getStyleAttr('font-family')
		fontSize = self.getStyleAttr('font-size')
		if fontFamily is not None:
			self.tk.font = wingdi.CreateFontIndirect({'name': fontFamily, 'height':fontSize,  'outprecision':win32con.OUT_OUTLINE_PRECIS, })
			wingdi.SelectObject(self.hdc, self.tk.font)

		# establish tk transform
		wingdi.SetWorldTransform(self.hdc, self.ctm.getElements())

	# end of context
	# self state reflects the restored context
	def tkOnEndContext(self):
		# restore dc to its previous state before deleting objects
		wingdi.RestoreDC(self.hdc, self.tk.saveid)

		if self.tk.pen:
			wingdi.DeleteObject(self.tk.pen)
	
		if self.tk.brush:
			wingdi.DeleteObject(self.tk.brush)

		if self.tk.font:
			wingdi.DeleteObject(self.tk.font)

		# restore previous tk
		self.restoreTk()

		# establish tk transform
		wingdi.SetWorldTransform(self.hdc, self.ctm.getElements())

	# init toolkit objects for 'other' 
	def tkInitInstance(self, other):
		other.hdc = self.hdc
		other.tk = self.tk
		other._tkstack = self._tkstack
	#
	#  platform line art interface
	#
	def beginDraw(self, style, tflist):
		if tflist:
			tm = self.ctm.copy()
			tm.applyTfList(tflist)
			wingdi.SetWorldTransform(self.hdc, tm.getElements())
		wingdi.BeginPath(self.hdc)

	def endDraw(self, style, tflist):
		wingdi.EndPath(self.hdc)
		#print 'number of path points', wingdi.GetPath(self.hdc)

		# fill should be painted first, then the stroke, and then the marker symbols
		fill = self.getStyleAttr('fill', style)
		stroke = self.getStyleAttr('stroke', style)

		# fill attrs
		needsfill = 0
		brush = None
		rop = None
		if fill is not None and fill != 'none':
			contextFill = self.getStyleAttr('fill')
			if contextFill != fill:
				brush = wingdi.CreateSolidBrush(fill)
				brush = wingdi.SelectObject(self.hdc, brush)
			try:
				if stroke and stroke != 'none':
					# keep path for stroke
					dcid = wingdi.SaveDC(self.hdc)
					wingdi.FillPath(self.hdc)
					wingdi.RestoreDC(self.hdc, dcid)
				else:
					wingdi.FillPath(self.hdc)
			except wingdi.error, arg:
				print arg,  style, tflist
			if brush:
				wingdi.DeleteObject(wingdi.SelectObject(self.hdc, brush))
			
		# stroke attrs
		needsstroke = 0
		pen = None
		strokeWidth = self.getStyleAttr('stroke-width', style)
		if stroke is not None and stroke!='none':
			contextStroke = self.getStyleAttr('stroke')
			contextStrokeWidth = self.getStyleAttr('stroke-width')
			if contextStroke != stroke or contextStrokeWidth != strokeWidth:
				pen = wingdi.ExtCreatePen(strokeWidth, stroke)
				pen = wingdi.SelectObject(self.hdc, pen)
			try:
				wingdi.StrokePath(self.hdc)
			except wingdi.error, arg:
				print arg,  style, tflist
			if pen:
				wingdi.DeleteObject(wingdi.SelectObject(self.hdc, pen))

		if tflist:
			wingdi.SetWorldTransform(self.hdc, self.ctm.getElements())
						
	def drawRect(self, pos, size, rxy, style, tflist):
		self.beginDraw(style, tflist)
		ltrb = pos[0], pos[1], pos[0]+size[0], pos[1]+size[1]
		rx, ry = rxy
		if rx is None or ry is None:
			wingdi.Rectangle(self.hdc, ltrb)
		else:
			wingdi.RoundRect(self.hdc, ltrb, rxy)
			
		self.endDraw(style, tflist)

	def drawCircle(self, center, r, style, tflist):
		self.beginDraw(style, tflist)
		ltrb = center[0]-r, center[1]-r, center[0]+r, center[1]+r
		wingdi.Ellipse(self.hdc, ltrb)
		self.endDraw(style, tflist)

	def drawEllipse(self, center, rxy, style, tflist):
		self.beginDraw(style, tflist)
		ltrb = center[0]-rxy[0], center[1]-rxy[1], center[0]+rxy[0], center[1]+rxy[1]
		wingdi.Ellipse(self.hdc, ltrb)
		self.endDraw(style, tflist)

	def drawLine(self, pt1, pt2, style, tflist):
		self.beginDraw(style, tflist)
		wingdi.MoveToEx(self.hdc, pt1)
		wingdi.LineTo(self.hdc, pt2)
		self.endDraw(style, tflist)

	def drawPolyline(self, points, style, tflist):
		self.beginDraw(style, tflist)
		wingdi.Polyline(self.hdc, points)
		self.endDraw(style, tflist)

	def drawPolygon(self, points, style, tflist):
		self.beginDraw(style, tflist)
		wingdi.Polygon(self.hdc, points)
		self.endDraw(style, tflist)

	def drawPath(self, path, style, tflist):
		self.beginDraw(style, tflist)
		self.drawPathSegList(path._pathSegList)
		self.endDraw(style, tflist)

	def drawText(self, text, pos, style, tflist):
		font = None
		fontFamily = self.getStyleAttr('font-family', style)
		fontSize = self.getStyleAttr('font-size', style)
		if fontFamily is not None:
			contextFontfamily = self.getStyleAttr('font-family')
			contextFontSize = self.getStyleAttr('font-size')
			if contextFontfamily != fontFamily or contextFontSize != fontSize:
				font = wingdi.CreateFontIndirect({'name': fontFamily, 'height':fontSize, 'outprecision':win32con.OUT_OUTLINE_PRECIS})
				wingdi.SelectObject(self.hdc, font)
		if tflist:
			tm = self.ctm.copy()
			tm.applyTfList(tflist)
			wingdi.SetWorldTransform(self.hdc, tm.getElements())

		fill = self.getStyleAttr('fill', style)
		stroke = self.getStyleAttr('stroke', style)

		# whats the default?
		if (fill is None or fill == 'none') and (stroke is None or stroke == 'none'):
			# text will be invisible
			# make it visible as black
			fill = 0, 0, 0

		if fill is not None and fill != 'none':
			oldcolor = wingdi.SetTextColor(self.hdc, fill)
			wingdi.TextOut(self.hdc, pos, text)
			wingdi.SetTextColor(self.hdc, oldcolor)

		pen = None
		strokeWidth = self.getStyleAttr('stroke-width', style)
		if stroke is not None and stroke!='none':
			# create path
			wingdi.BeginPath(self.hdc)
			wingdi.TextOut(self.hdc, pos, text)
			wingdi.EndPath(self.hdc)
			
			# stroke path
			contextStroke = self.getStyleAttr('stroke')
			contextStrokeWidth = self.getStyleAttr('stroke-width')
			if contextStroke != stroke or contextStrokeWidth != strokeWidth:
				pen = wingdi.ExtCreatePen(strokeWidth, stroke)
				pen = wingdi.SelectObject(self.hdc, pen)
			wingdi.StrokePath(self.hdc)
			if pen:
				wingdi.DeleteObject(wingdi.SelectObject(self.hdc, pen))

		if font:
			wingdi.DeleteObject(wingdi.SelectObject(self.hdc, font))
		if tflist:
			wingdi.SetWorldTransform(self.hdc, self.ctm.getElements())

	def computeArcCenter(self, x1, y1, rx, ry, a, x2, y2, fa, fs):
		cos = math.cos(a)
		sin = math.sin(a)
		x1p, y1p = 0.5*(x1-x2)*cos + 0.5*(y1-y2)*sin, -0.5*sin*(x1-x2)+0.5*cos*(y1-y2)
		
		rx2, ry2 = rx*rx, ry*ry
		x1p2, y1p2 = x1p*x1p, y1p*y1p
		r2 = x1p2/float(rx2) + y1p2/float(ry2)
		if r2>1:
			rx, ry = math.sqrt(r2)*rx, math.sqrt(r2)*ry
			rx2, ry2 = rx*rx, ry*ry
		sq2 = (rx2*ry2 - rx2*y1p2 -ry2*x1p2)/(rx2*y1p2+ry2*x1p2)
		if sq2 < 0: sq2 = 0.0
		sq = math.sqrt(sq2)
		if fa == fs: sq = -sq
		cxp, cyp = sq*rx*y1p/float(ry), -sq*ry*x1p/float(rx)
		cx, cy = cxp*cos - cyp*sin + 0.5*(x1+x2), cxp*sin + cyp*cos + 0.5*(y1+y2)
		return int(cx+0.5), int(cy+0.5)
		
	def saveTk(self):
		assert self.tk.saveid != 0, 'invalid tk'
		self._tkstack.append(self.tk.getHandles())
		self.tk.reset()

	def restoreTk(self):
		assert len(self._tkstack)>0, 'unpaired save/restore tk'
		self.tk.setHandles(self._tkstack.pop())

	# XXX: use PolyDraw to speed up
	def drawPathSegList(self, pathSegList):
		PathSeg = svgtypes.PathSeg
		lastX = 0
		lastY = 0
		lastC = None
		startP = None
		isstart = 1
		for seg in pathSegList:
			seg.topxl()
			if isstart:
				badCmds = 'HhVvZz'
				if badCmds.find(seg.getTypeAsLetter())>=0:
					print 'ignoring cmd ', seg.getTypeAsLetter()
					continue
				if badCmds.find(seg.getTypeAsLetter())<0:
					if seg._type != PathSeg.SVG_PATHSEG_MOVETO_ABS and \
						seg._type != PathSeg.SVG_PATHSEG_MOVETO_REL:
						print 'assuming abs moveto'
					if seg._type == PathSeg.SVG_PATHSEG_MOVETO_REL:
						lastX, lastY = lastX + seg._x, lastY + seg._y
						startP = lastX, lastY
						wingdi.MoveToEx(self.hdc, startP)
					else:
						lastX, lastY = seg._x, seg._y
						startP = (lastX, lastY)
						wingdi.MoveToEx(self.hdc, startP)
				isstart = 0
			else:
				if seg._type == PathSeg.SVG_PATHSEG_CLOSEPATH:
					if startP:
						lastX, lastY = startP
						wingdi.CloseFigure(self.hdc)
						startP = None
					lastC = None
					isstart = 1

				elif seg._type == PathSeg.SVG_PATHSEG_MOVETO_ABS:
					lastX, lastY = seg._x, seg._y
					lastC = None
					wingdi.MoveToEx(self.hdc, (lastX, lastY))

				elif seg._type == PathSeg.SVG_PATHSEG_MOVETO_REL:
					if seg._x != 0 or seg._y != 0:
						lastX, lastY = lastX + seg._x, lastY + seg._y
						lastC = None
						wingdi.MoveToEx(self.hdc, (lastX, lastY))

				elif seg._type == PathSeg.SVG_PATHSEG_LINETO_ABS:
					if seg._x != lastX or seg._y != lastY:
						lastX, lastY = seg._x, seg._y
						lastC = None
						wingdi.LineTo(self.hdc, (seg._x, seg._y))

				elif seg._type == PathSeg.SVG_PATHSEG_LINETO_REL:
					lastX, lastY = lastX + seg._x, lastY + seg._y
					lastC = None
					wingdi.LineTo(self.hdc, (lastX, lastY))

				elif seg._type == PathSeg.SVG_PATHSEG_LINETO_HORIZONTAL_ABS:
					lastX = seg._x
					lastC = None
					wingdi.LineTo(self.hdc, (lastX, lastY))

				elif seg._type == PathSeg.SVG_PATHSEG_LINETO_HORIZONTAL_REL:
					lastX = lastX + seg._x
					lastC = None
					wingdi.LineTo(self.hdc, (lastX, lastY))

				elif seg._type == PathSeg.SVG_PATHSEG_LINETO_VERTICAL_ABS:
					lastY = seg._y
					lastC = None
					wingdi.LineTo(self.hdc, (lastX, lastY))

				elif seg._type == PathSeg.SVG_PATHSEG_LINETO_VERTICAL_REL:
					lastY = lastY + seg._y
					lastC = None
					wingdi.LineTo(self.hdc, (lastX, lastY))

				elif seg._type == PathSeg.SVG_PATHSEG_CURVETO_CUBIC_ABS:
					x1, y1, x2, y2, x, y = seg._x1, seg._y1, seg._x2, seg._y2, seg._x, seg._y
					bl = [(x1,y1), (x2,y2), (x,y)]
					wingdi.PolyBezierTo(self.hdc, bl)
					lastC = seg._x2,seg._y2
					lastX, lastY = seg._x, seg._y

				elif seg._type == PathSeg.SVG_PATHSEG_CURVETO_CUBIC_REL:
					x1, y1, x2, y2, x, y = lastX + seg._x1, lastY + seg._y1, lastX + seg._x2, lastY + seg._y2, lastX + seg._x, lastY + seg._y
					bl = [(x1,y1), (x2,y2), (x,y)]
					wingdi.PolyBezierTo(self.hdc, bl)
					lastC = lastX + seg._x2,lastY + seg._y2
					lastX, lastY = lastX + seg._x,lastY + seg._y

				elif seg._type == PathSeg.SVG_PATHSEG_CURVETO_CUBIC_SMOOTH_ABS:
					if lastC is None:
						lastC = lastX, lastY
					x1, y1 = 2*lastX - lastC[0], 2*lastY - lastC[1]
					bl = [(x1, y1),(seg._x2, seg._y2),(seg._x, seg._y)]
					wingdi.PolyBezierTo(self.hdc, bl)
					lastC = seg._x2, seg._y2
					lastX, lastY = seg._x, seg._y

				elif seg._type == PathSeg.SVG_PATHSEG_CURVETO_CUBIC_SMOOTH_REL:
					if lastC is None:
						lastC = lastX, lastY
					x1, y1 = 2*lastX - lastC[0], 2*lastY - lastC[1]
					bl = [(x1, y1),(lastX + seg._x2, lastY + seg._y2),(lastX + seg._x, lastY + seg._y)]
					wingdi.PolyBezierTo(self.hdc, bl)
					lastC = lastX + seg._x2, lastY + seg._y2
					lastX, lastY = lastX + seg._x, lastY + seg._y

				elif seg._type == PathSeg.SVG_PATHSEG_CURVETO_QUADRATIC_ABS:
					bl = [(lastX, lastY),(seg._x1, seg._y1),(seg._x, seg._y)]
					wingdi.PolyBezierTo(self.hdc, bl)
					lastC = seg._x1, seg._y1
					lastX, lastY = seg._x, seg._y

				elif seg._type == PathSeg.SVG_PATHSEG_CURVETO_QUADRATIC_REL:
					bl = [(lastX, lastY),(lastX + seg._x1, lastY + seg._y1),(lastX + seg._x, lastY + seg._y)]
					wingdi.PolyBezierTo(self.hdc, bl)
					lastC = lastX + seg._x1, lastY + seg._y1
					lastX, lastY = lastX + seg._x, lastY + seg._y

				elif seg._type == PathSeg.SVG_PATHSEG_CURVETO_QUADRATIC_SMOOTH_ABS:
					if lastC is None:
						lastC = lastX, lastY
					nextC = 2*lastX - lastC[0], 2*lastY - lastC[1]
					bl = [(lastX, lastY),nextC,(seg._x, seg._y)]
					wingdi.PolyBezierTo(self.hdc, bl)
					lastC = nextC
					lastX, lastY = seg._x, seg._y

				elif seg._type == PathSeg.SVG_PATHSEG_CURVETO_QUADRATIC_SMOOTH_REL:
					if lastC is None:
						lastC = lastX, lastY
					nextC = 2*lastX - lastC[0], 2*lastY - lastC[1]
					bl = [(lastX, lastY),nextC,(lastX+seg._x, lastY+seg._y)]
					wingdi.PolyBezierTo(self.hdc, bl)
					lastC = nextC
					lastX, lastY = lastX+seg._x, lastY+seg._y

				elif seg._type == PathSeg.SVG_PATHSEG_ARC_ABS:
					angle = int(seg._angle)/360
					angle = (angle/180.0)*math.pi
					fa = seg._largeArcFlag
					fs = seg._sweepFlag
					r1, r2 = seg._r1, seg._r2
					if r1<0: r1 = -r1
					if r2<0: r2 = -r2
					if r1 == 0 or r2 == 0:
						wingdi.LineTo(self.hdc, (seg._x, seg._y))
					else:
						if fs:
							olddir = wingdi.SetArcDirection(self.hdc, win32con.AD_CLOCKWISE)
						else:
							olddir = wingdi.SetArcDirection(self.hdc, win32con.AD_COUNTERCLOCKWISE)
						cx, cy = self.computeArcCenter(lastX, lastY, r1, r2, angle, seg._x, seg._y, fa, fs)
						if angle:
							tm = svgtypes.TM()
							tm.translate([cx, cy])
							tm.rotate([angle])
							tm.inverse()
							x1, y1 = tm.UPtoVP((lastX, lastY))
							x2, y2 = tm.UPtoVP((seg._x, seg._y))

							oldtf = wingdi.GetWorldTransform(self.hdc)
							tm = self.ctm.copy()
							tm.applyTfList([('translate',[cx, cy]), ('rotate',[angle,]),])
							wingdi.SetWorldTransform(self.hdc, tm.getElements())
							rc = -r1, -r2, r1, r2
							wingdi.Arc(self.hdc, rc, (x1, y1), (x2, y2))
							wingdi.SetWorldTransform(self.hdc, oldtf)
							wingdi.MoveToEx(self.hdc, (seg._x, seg._y))
						else:
							rc = cx-r1, cy-r2, cx+r1, cy+r2
							x1, y1 = lastX, lastY
							x2, y2 = seg._x, seg._y
							wingdi.ArcTo(self.hdc, rc, (x1, y1), (x2, y2))
						wingdi.SetArcDirection(self.hdc, olddir)	
					lastC = None
					lastX, lastY = seg._x, seg._y

				elif seg._type == PathSeg.SVG_PATHSEG_ARC_REL:
					angle = int(seg._angle)%360
					angle = (angle/180.0)*math.pi
					fa = seg._largeArcFlag
					fs = seg._sweepFlag
					r1, r2 = seg._r1, seg._r2
					if r1<0: r1 = -r1
					if r2<0: r2 = -r2
					if r1 == 0 or r2 == 0:
						wingdi.LineTo(self.hdc, (lastX + seg._x, lastY + seg._y))
					else:
						if fs:
							olddir = wingdi.SetArcDirection(self.hdc, win32con.AD_CLOCKWISE)
						else:
							olddir = wingdi.SetArcDirection(self.hdc, win32con.AD_COUNTERCLOCKWISE)
						cx, cy = self.computeArcCenter(lastX, lastY, r1, r2, angle, lastX + seg._x, lastY + seg._y, fa, fs)	
						if angle:
							tm = svgtypes.TM()
							tm.translate([cx, cy])
							tm.rotate([angle])
							tm.inverse()
							x1, y1 = tm.UPtoVP((lastX, lastY))
							x2, y2 = tm.UPtoVP((lastX + seg._x, lastY + seg._y))

							oldtf = wingdi.GetWorldTransform(self.hdc)
							tm = self.ctm.copy()
							tm.applyTfList([('translate',[cx, cy]), ('rotate',[angle,]),])
							wingdi.SetWorldTransform(self.hdc, tm.getElements())
							rc = -r1, -r2, r1, r2
							wingdi.Arc(self.hdc, rc, (x1, y1), (x2, y2))
							wingdi.SetWorldTransform(self.hdc, oldtf)
							wingdi.MoveToEx(self.hdc, (lastX + seg._x, lastY + seg._y))
						else:
							rc = cx-r1, cy-r2, cx+r1, cy+r2
							x1, y1 = lastX, lastY
							x2, y2 = lastX + seg._x, lastY + seg._y
							wingdi.ArcTo(self.hdc, rc, (x1, y1), (x2, y2))
						wingdi.SetArcDirection(self.hdc, olddir)
					lastC = None
					lastX, lastY = lastX + seg._x, lastY + seg._y
		

######################
class Tk:
	def __init__(self):
		self.pen = 0
		self.brush = 0
		self.font = 0
		self.saveid = 0 # previous SaveDC id

	def setDefaults(self):
		self.pen = wingdi.GetStockObject(win32con.BLACK_PEN)
		self.brush = wingdi.GetStockObject(win32con.WHITE_BRUSH)
		self.font = wingdi.GetStockObject(win32con.SYSTEM_FONT)
	
	def reset(self):
		self.pen, self.brush, self.font, self.saveid = 0, 0, 0, 0
		
	def getHandles(self):
		return self.pen, self.brush, self.font, self.saveid

	def setHandles(self, ht):
		self.pen, self.brush, self.font, self.saveid = ht

