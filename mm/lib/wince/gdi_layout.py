__version__ = "$Id$"

# app constants
from appcon import *
from WMEVENTS import *

# windows
import winuser, wingdi, wincon
import winstruct

#
import base_window

class Region(base_window.Window):
	def __init__(self, parent, coordinates, transparent, z, units, bgcolor):
		base_window.Window.__init__(self)
		
		# create the window
		self.create(parent, coordinates, units, z, transparent, bgcolor)
		if self._topwindow:
			self._canvas = self._topwindow.LRtoDR(self._canvas, round = 1)
						
	def __repr__(self):
		return '<Region instance at %x>' % id(self)
		
	def newwindow(self, coordinates, pixmap = 0, transparent = 0, z = 0, units = None, bgcolor=None):
		return Region(self, coordinates, transparent, z, units, bgcolor)
	
	def close(self):
		if self._parent is None:
			return
		if self._transition:
			self._transition.endtransition()
		self._parent._subwindows.remove(self)
		self.updateMouseCursor()
		self._parent.update()
		self._parent = None
		for win in self._subwindows[:]:
			win.close()
		for dl in self._displists[:]:
			dl.close()
		del self._topwindow
		del self._convert_color
		del self._transition

	def update(self, rc = None):
		if self._topwindow and self._topwindow != self:
			if rc is None:
				rc = self.getwindowpos()
			self._topwindow.update(rc)
	
	def getDR(self):
		rc = self.getwindowpos()
		return self._topwindow.LRtoDR(rc, round = 1)

	def getClipDR(self, dc):
		# dc box
		ltrb1 = dc.GetClipBox()

		# clip to parent
		ltrb2a = winstruct.ltrb(self.getwindowpos())
		ltrb2b = winstruct.ltrb(self._parent.getwindowpos())
		ltrb2 = winstruct.rectAnd(ltrb2a, ltrb2b)
		if ltrb2 is None: return None
		ltrb2 = self._topwindow.LRtoDR(ltrb2, round = 1)

		# common box
		return winstruct.rectAnd(ltrb1, ltrb2)

	def _paintOnDC(self, dc):
		ltrb = self.getClipDR(dc)
		if ltrb is None:
			return
		if self._active_displist:
			entry = self._active_displist._list[0]
			bgcolor = None
			if entry[0] == 'clear' and entry[1]:
				bgcolor = entry[1]
			elif not self._transparent:
				bgcolor = self._bgcolor
			if bgcolor:
				brush = wingdi.CreateSolidBrush(bgcolor)
				old_brush = dc.SelectObject(brush)
				dc.Rectangle(ltrb)
				dc.SelectObject(old_brush)
				wingdi.DeleteObject(brush)
			self._active_displist._render(dc, ltrb, start=1)
			if self._showing:
				brush =  wingdi.CreateSolidBrush((255, 0, 0))
				dc.FrameRect(ltrb, brush)
				wingdi.DeleteObject(brush)

		elif self._transparent == 0 and self._bgcolor:
			brush = wingdi.CreateSolidBrush(self._bgcolor)
			old_brush = dc.SelectObject(brush)
			dc.Rectangle(ltrb)
			dc.SelectObject(old_brush)
			wingdi.DeleteObject(brush)

	# normal painting
	def _paint_0(self, dc):
		self._paintOnDC(dc)

		# then paint children bottom up
		L = self._subwindows[:]
		L.reverse()
		for w in L:
			w.paint(dc)

	def paint(self, dc):
		self._paint_0(dc)

#############################

class Viewport(Region):
	def __init__(self, context, coordinates, bgcolor):
		Region.__init__(self, None, coordinates, 0, 0, UNIT_PXL, bgcolor)
		
		# adjust some variables
		self._topwindow = self
		self._canvas = self.LRtoDR(self._canvas, round = 1)

		# viewport context (here an os window) 
		self._ctx = context
		
		# scaling
		self._device2logical = self._ctx._d2l
			
		self._bgbrush = wingdi.CreateSolidBrush(bgcolor)
			
		# init bmp 
		wd, hd = self.LPtoDP(coordinates[2:])
		self._backBuffer = self.createSurface(wd, hd, bgcolor)
			
	def __repr__(self):
		return '<Viewport instance at %x>' % id(self)

	def _convert_color(self, color):
		return color 

	def getwindowpos(self, rel=None):
		return self._rectb

	def pop(self, poptop = 1):
		pass

	def setcursor(self, strid):
		print 'Viewport.setcursor', strid

	def close(self):
		if self._ctx is None:
			return
		ctx = self._ctx
		self._ctx = None
		for win in self._subwindows[:]:
			win.close()
		for dl in self._displists[:]:
			dl.close()
		del self._topwindow
		ctx.update()

		#
		if self._bgbrush:
			wingdi.DeleteObject(self._bgbrush)
		self._bgbrush = 0


	def newwindow(self, coordinates, pixmap = 0, transparent = 0, z = 0, units = None, bgcolor=None):
		return Region(self, coordinates, transparent, z, units, bgcolor)
	newcmwindow = newwindow

	# 
	# Query section
	# 
	def is_closed(self):
		return self._ctx is None
		
	def getContext(self):
		return self._ctx

	# 
	# Painting section
	#
	def createSurface(self, w, h, bgcolor):
		if self.is_closed(): return
		wnd = self._ctx
		dc = wingdi.CreateDCFromHandle(wnd.GetDC())
		surf = wingdi.CreateDIBSurface(dc, w, h, bgcolor)
		wnd.ReleaseDC(dc.Detach())
		return surf
	
	def getBackBuffer(self):
		return self._backBuffer

	def update(self, rc=None):
		if self._ctx is None or self._backBuffer is None: 
			return
		if rc is None:
			rc = self._viewport.getwindowpos()
		self._ctx.update(rc)

	def paint(self, dc):
		ltrb = dc.GetClipBox()
		old_brush = dc.SelectObject(self._bgbrush)
		dc.Rectangle(ltrb)
		dc.SelectObject(old_brush)
		
		L = self._subwindows[:]
		L.reverse()
		for w in L:
			w.paint(dc)

	def paintSurfAt(self, dc, surf, pos):
		dcc = dc.CreateCompatibleDC()
		bmp = dcc.SelectObject(surf)
		dc.BitBlt(pos, surf.GetSize(), dcc, (0, 0), wincon.SRCCOPY)
		dcc.SelectObject(bmp)
		dcc.DeleteDC()
	
	# 
	# Mouse section
	# 
	def updateMouseCursor(self):
		pass

	def onMouseEvent(self, point, event, params=None):
		for w in self._subwindows:
			if w.inside(point):
				if event == Mouse0Press:
					w._onlbuttondown(point)
				elif event == Mouse0Release:
					w._onlbuttonup(point)
				break		
		return Region.onMouseEvent(self, point, event)

	def onMouseMove(self, point, params=None):
		# check subwindows first
		for w in self._subwindows:
			if w.inside(point):
				w._onmousemove(point)
				if w.setcursor_from_point(point):
					return

		# not in a subwindow, handle it ourselves
		if self._active_displist:
			x, y, w, h = self.getwindowpos()
			xp, yp = point
			point = xp-x, yp-y
			x, y = self._pxl2rel(point,self._canvas)
			for button in self._active_displist._buttons:
				if button._inside(x,y):
					self.setcursor('hand')
					return
		self.setcursor(self._cursor)


	