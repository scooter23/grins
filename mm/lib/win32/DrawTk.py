__version__ = "$Id$"

""" @win32doc|DrawTk
The basic classes defined in this module are the DrawTool and the DrawObj.
The SelectTool and the RectTool are extensions to the DrawTool
The DrawRect is an extension to the DrawObj
The DrawTk is a utility class 
The DrawLayer is a mixin class for windows
"""

# Win32 Drawing Toolkit

import win32ui,win32con
Sdk=win32ui.GetWin32Sdk()
Afx=win32ui.GetAfx()

import win32mu
from win32mu import Point,Size,Rect # shorcuts
from appcon import UNIT_MM, UNIT_SCREEN, UNIT_PXL


################################# DrawTool
# base class for drawing tools
class DrawTool:
	def __init__(self,toolType):
		self._toolType=toolType
		self._client_units = 0

	def setunits(self, units):
		self._client_units = units

	def onLButtonDown(self,view,flags,point):
		tk=view.drawTk
		tk.SetCapture(view)
		tk.down_flags = flags
		tk.down = point
		tk.last = point

	def onLButtonDblClk(self,view,flags,point):
		pass

	def onLButtonUp(self,view,flags,point):
		tk=view.drawTk
		tk.ReleaseCapture(view)
		if point.iseq(tk.down):
			tk.currentToolType = tk.TOOL_SELECT

	def onMouseMove(self,view,flags,point):
		tk=view.drawTk
		tk.last = point
		cursor=Sdk.LoadStandardCursor(win32con.IDC_ARROW)
		tk.SetCursor(view,cursor)

	# Cancel drawing
	def onCancel(self,view):
		view.drawTk.currentToolType = view.drawTk.TOOL_SELECT



################################# SelectTool

class SelectTool(DrawTool):
	def __init__(self):
		DrawTool.__init__(self,DrawTk.TOOL_SELECT)

	def onLButtonDown(self,view,flags,point):
		local = view.ClientToCanvas(point)
		drawObj=None
		tk=view.drawTk
		tk.selectMode = DrawTk.SM_NONE

		# Check for resizing (only allowed on single selections)
		if len(view._selection) == 1:
			drawObj = view._selection[0]
			tk.ixDragHandle = drawObj.hitTest(local,view,1)
			if tk.ixDragHandle != 0:
				tk.selectMode = DrawTk.SM_SIZE
				# for smoother behavior set cursor here
				tk.SetCursor(view,drawObj.getHandleCursor(tk.ixDragHandle))

		# See if the click was on an object, select and start move if so
		if tk.selectMode == DrawTk.SM_NONE:
			drawObj = view.ObjectAt(local);
			if drawObj:
				tk.selectMode = DrawTk.SM_MOVE
				if not view.IsSelected(drawObj):
					view.Select(drawObj, (flags & win32con.MK_SHIFT))
				# Ctrl+Click clones the selection...
				if (flags & win32con.MK_CONTROL) != 0:
					view.CloneSelection()


		# Click on background, start a net-selection
		if tk.selectMode == DrawTk.SM_NONE:
			if (flags & win32con.MK_SHIFT) == 0:
				view.Select(None)

			tk.selectMode = DrawTk.SM_NET

			dc=view.GetDC()
			rect=Rect((point.x, point.y, point.x, point.y))
			rect.normalizeRect()
			dc.DrawFocusRect(rect.tuple())
			view.ReleaseDC(dc)

		tk.lastPoint = local
		DrawTool.onLButtonDown(self,view,flags, point)

	def onLButtonDblClk(self,view,flags,point):
		if (flags & win32con.MK_SHIFT) != 0:
			# Shift+DblClk deselects object...
			local=view.ClientToCanvas(point);
			drawObj = view.ObjectAt(local)
			if drawObj:
				view.Deselect(drawObj)
		else:
			# Normal DblClk opens properties
			if len(view._selection)==1:
				view._selection[0].onOpen(view)
		DrawTool.onLButtonDblClk(self,view,flags,point)


	def onLButtonUp(self,view,flags,point):
		tk=view.drawTk
		if tk.MouseCaptured(view):
			if tk.selectMode == DrawTk.SM_NET:
				dc=view.GetDC()
				rect=Rect((tk.down.x, tk.down.y, tk.last.x, tk.last.y))
				rect.normalizeRect();
				dc.DrawFocusRect(rect.tuple())
				view.ReleaseDC(dc)
				view.SelectWithinRect(rect,1)
			elif tk.selectMode != DrawTk.SM_NONE:
				dc=view.GetDC()
				view.InvalidateRect()
				view.ReleaseDC(dc)
		DrawTool.onLButtonUp(self,view,flags,point)

	def onMouseMove(self,view,flags,point):
		tk=view.drawTk
		if not tk.MouseCaptured(view):
			if tk.currentToolType == tk.TOOL_SELECT and len(view._selection) == 1:
				drawObj = view._selection[0]
				local=view.ClientToCanvas(point)
				nHandle = drawObj.hitTest(local,view, 1)
				if nHandle != 0:
					tk.SetCursor(view,drawObj.getHandleCursor(nHandle))
					return # bypass DrawTool
			if tk.currentToolType == tk.TOOL_SELECT:
				DrawTool.onMouseMove(self,view,flags,point)
			return

		if tk.selectMode == DrawTk.SM_NET:
			dc=view.GetDC()
			rect=Rect((tk.down.x, tk.down.y, tk.last.x, tk.last.y))
			rect.normalizeRect()
			dc.DrawFocusRect(rect.tuple())
			rect.setRect(tk.down.x, tk.down.y, point.x, point.y)
			rect.normalizeRect()
			dc.DrawFocusRect(rect.tuple())
			view.ReleaseDC(dc)
			DrawTool.onMouseMove(self,view,flags,point)
			return

		local=view.ClientToCanvas(point)
		delta = Point.subtr(local,tk.lastPoint)
		for drawObj in view._selection:
			position = Rect(drawObj._position.tuple())
			if tk.selectMode == DrawTk.SM_MOVE:
				position.moveByPt(delta)
				drawObj.moveTo(position,view)
				if delta.x+delta.y:view.SetDrawObjDirty(1)
			elif tk.ixDragHandle != 0:
				drawObj.moveHandleTo(tk.ixDragHandle,local,view)
				view.SetDrawObjDirty(1)

		tk.lastPoint = local

		if tk.selectMode == DrawTk.SM_SIZE and tk.currentToolType == tk.TOOL_SELECT:
			tk.last = point
			cursor=view._selection[0].getHandleCursor(tk.ixDragHandle)
			tk.SetCursor(view,cursor)
			return # bypass DrawTool

		tk.last = point

		if tk.currentToolType == DrawTk.TOOL_SELECT:
			DrawTool.onMouseMove(self,view,flags,point)


class RectTool(DrawTool):
	def __init__(self):
		DrawTool.__init__(self,DrawTk.TOOL_RECT)

	def onLButtonDown(self,view,flags,point):
		tk=view.drawTk
		DrawTool.onLButtonDown(self,view,flags,point)
		local=view.ClientToCanvas(point)
		drawObj = DrawRect(Rect((local.x,local.y,local.x,local.y)), units = self._client_units)
		view.Add(drawObj)
		view.Select(drawObj)

		tk.selectMode = DrawTk.SM_SIZE
		tk.ixDragHandle = 5
		tk.lastPoint = local

	def onLButtonDblClk(self,view,flags,point):
		DrawTool.onLButtonDblClk(self,view,flags,point)

	def onLButtonUp(self,view,flags,point):
		tk=view.drawTk
		if point.iseq(tk.down):
			# don't create empty objects...
			if len(view._selection):
				drawObj = view._selection[len(view._selection)-1]
				view.Remove(drawObj);
				del drawObj
			tk.selectTool.onLButtonDown(view,flags,point) # try a select!
		tk.selectTool.onLButtonUp(view,flags,point)
		tk.OnNewRect(view)		

	def onMouseMove(self,view,flags,point):
		tk=view.drawTk
		if not tk.InDrawArea(point):
			cursor=Sdk.LoadStandardCursor(win32con.IDC_ARROW)
			tk.SetCursor(view,cursor)
			return
		cursor=Sdk.LoadStandardCursor(win32con.IDC_CROSS)
		tk.SetCursor(view,cursor)
		tk.selectTool.onMouseMove(view,flags,point)

#################################			
class DrawObj:
	def __init__(self,rc,units=None):
		self._position=Rect(rc.tuple())
		self._shape=0
		self._pen = win32mu.Pen(win32con.PS_INSIDEFRAME,Size((1,1)),(0,0,0))
		self._brush=win32mu.Brush(win32con.BS_SOLID,(192, 192, 192),win32con.HS_HORIZONTAL)
		self._client_units = units

	def setunits(self, units):
		self._client_units = units

	def __del__(self):
		# release resources
		pass
	# Return the number if handles 
	def getHandleCount(self):
		return 8

	# Return the bounding box
	def getbbox(self):
		return self._position.tuple()

	# Return the handle at index
	def getHandle(self,ix):
		"""returns logical coords of center of handle"""
	
		# this gets the center regardless of left/right and top/bottom ordering
		xCenter = self._position.left + self._position.width() / 2
		yCenter = self._position.top + self._position.height() / 2

		if ix== 1:
			x = self._position.left
			y = self._position.top
		elif ix== 2:
			x = xCenter;
			y = self._position.top
		elif ix== 3:
			x = self._position.right;
			y = self._position.top;
		elif ix== 4:
			x = self._position.right;
			y = yCenter;
		elif ix== 5:
			x = self._position.right;
			y = self._position.bottom;
		elif ix== 6:
			x = xCenter;
			y = self._position.bottom;
		elif ix== 7:
			x = self._position.left;
			y = self._position.bottom;
		elif ix== 8:
			x = self._position.left;
			y = yCenter;
		else:
			raise error, 'invalid handle'
		return Point((x, y))

	# Return handle's rectangle
	def getHandleRect(self,ix,view):
		"""return rectange of handle in logical coords"""
		if not view: return
		# get the center of the handle in logical coords
		point = self.getHandle(ix)
		# convert to device coords 
		# (not needed if logical coordinates in MM_TEXT )
		point=view.CanvasToClient(point)
		# return Rect of handle in device coords
		rect=Rect((point.x-3, point.y-3, point.x+3, point.y+3))
		return view.ClientToCanvasRect(rect)

	# Return the appropriate for the handle cursor
	def getHandleCursor(self,ix):
		if   ix==1 or ix==5:id = win32con.IDC_SIZENWSE
		elif ix==2 or ix==6:id = win32con.IDC_SIZENS
		elif ix==3 or ix==7:id = win32con.IDC_SIZENESW
		elif ix==4 or ix==8:id = win32con.IDC_SIZEWE
		else:raise error, 'invalid handle'
		return Sdk.LoadStandardCursor(id)

	def setLineColor(self,color):
		self._pen._color=color
		self.invalidate()
	def setFillColor(self,color):
		self._brush._color=color
		self.invalidate()

	# operations
	def draw(self,dc):
		# will be overwritten
		pass

	# Draw a small trag rect for each handle
	def drawTracker(self,dc,trackerState):
		if trackerState==DrawObj.normal:
			pass
		elif trackerState==DrawObj.selected or trackerState==DrawObj.active:
			nHandleCount = self.getHandleCount()		
			for nHandle in range(1,nHandleCount+1):
				handlept=self.getHandle(nHandle)
				dc.PatBlt((handlept.x - 3, handlept.y - 3), (7, 7), win32con.DSTINVERT);

	def moveTo(self,position,view):
		tk=view.drawTk
		if position.iseq(self._position):
			return
		if not tk.InDrawAreaRc(position):
			return
		if not view:
			self.invalidate()
			self._position.setToRect(position)
			self.invalidate();
		else:
			view.InvalObj(self)
			self._position.setToRect(position)
			view.InvalObj(self)

	# Returns true if the point is within the object
	def hitTest(self,point,view,is_selected):
		"""
		Note: if is selected, hit-codes start at one for the top-left
		and increment clockwise, 0 means no hit.
		If not selected, 0 = no hit, 1 = hit (anywhere)
		point is in logical coordinates
		"""
		assert(view)

		if is_selected:
			nHandleCount = self.getHandleCount()
			for nHandle in range(1,nHandleCount+1):
				# GetHandleRect returns in logical coords
				rc = self.getHandleRect(nHandle,view)
				if rc.isPtInRect(point): 
					return nHandle
		else:
			if self._position.isPtInRect(point):return 1
		return 0

	# Returns true if the rect intersects the object
	def intersects(self,rect):
		"""rect must be in logical coordinates"""
		rect.normalizeRect()
		self._position.normalizeRect()
		return Rect.intersect(rect,self._position)

	def moveHandleTo(self,ixHandle,point,view = None):
		"""point must be in logical coordinates"""
		position = Rect(self._position.tuple())
		if	ixHandle== 1:
			position.left = point.x
			position.top = point.y
		elif ixHandle== 2:
			position.top = point.y
		elif ixHandle== 3:
			position.right = point.x
			position.top = point.y
		elif ixHandle== 4:
			position.right = point.x
		elif ixHandle== 5:
			position.right = point.x
			position.bottom = point.y
		elif ixHandle== 6:
			position.bottom = point.y
		elif ixHandle== 7:
			position.left = point.x
			position.bottom = point.y
		elif ixHandle== 8:
			position.left = point.x
		else:
			raise error, 'invalid handle'
		position.normalizeRect()
		self.moveTo(position,view)

	def invalidate(self):
		self.UpdateObj(DrawTk.HINT_UPDATE_DRAWOBJ,self)

	def clone(self,context=None):
		clone = DrawObj(self._position)
		clone._pen = self._pen
		clone._brush = self._brush
		clone._client_units= self._client_units
		if context:
			context.Add(clone);
		return clone

	# class attributes
	[normal, selected, active]=range(3)

# A rectangle drawing tool

class DrawRect(DrawObj):
	def __init__(self,pos,units=None):
		DrawObj.__init__(self,pos,units)
	def getHandleCount(self):
		return DrawObj.getHandleCount(self)
	def getHandle(self,ix):
		return DrawObj.getHandle(self,ix)
	def getHandleCursor(self,ixHandle):
		return DrawObj.getHandleCursor(self,ixHandle)
	def moveHandleTo(self,ixHandle,point,view = None):
		return DrawObj.moveHandleTo(self,ixHandle,point,view)
	def intersects(self,rect):
		return DrawObj.intersects(self,rect)
	def clone(self,context=None):
		return DrawObj.clone(self,context)

	# fill with clr the dc outsite self._position
	def crcfill(self,dc,tk,clr=(0,0,0)):
		cr = win32mu.RGB(clr)
		l,t,r,b = tk._crect.tuple()
		li,ti,ri,bi = self._position.tuple()
		dc.FillSolidRect((l,t,li,b),cr)
		dc.FillSolidRect((l,t,r,ti),cr)
		dc.FillSolidRect((ri,t,r,b),cr)
		dc.FillSolidRect((l,bi,r,b),cr)

	# invert the dc outsite self._position
	def crcinvert(self,dc,tk):
		l,t,r,b = tk._crect.tuple()
		li,ti,ri,bi = self._position.tuple()
		dc.PatBlt((l,t),(r-l,b-t), win32con.DSTINVERT);
		dc.PatBlt((li,ti),(ri-li,bi-ti), win32con.DSTINVERT);
		
	def draw(self,dc,view):
		tk=view.drawTk
		# create pen and brush and select them in dc
		pen=Sdk.CreatePen(win32con.PS_SOLID,0,win32mu.RGB((255,0,0)))
		oldpen=dc.SelectObjectFromHandle(pen)

		if not tk.InLayoutMode():
			if tk._bkimg<0:
				clr=(0xC0, 0xC0, 0xC0)
				dc.FillSolidRect(self._position.tuple(),win32mu.RGB(clr))
			else:
				#self.crcfill(dc,tk,(0,0,0))
				self.crcinvert(dc,tk)

		win32mu.FrameRect(dc,self._position.tuple(),(255,0,0))
		
		if not tk.InLayoutMode() and tk._bkimg>=0:
			dc.SelectObjectFromHandle(oldpen)
			Sdk.DeleteObject(pen)
			return

		# write dimensions
		s=''
		str_units=''
		scale = tk.GetScale()
		if scale:
			s,str_units=scale.orgrect_str(self._position,self._client_units)
		else:
			if self._client_units == UNIT_PXL:				
				s='(%d,%d,%d,%d)' % self._position.tuple_ps()
			elif self._client_units == UNIT_SCREEN and tk._ref_wnd:
				s='(%.2f,%.2f,%.2f,%.2f)' % tk._ref_wnd.inverse_coordinates(self._position.tuple_ps(),units=self._client_units)
			else:
				str_units='mm'
				s='(%.1f,%.1f,%.1f,%.1f)' % tk._ref_wnd.inverse_coordinates(self._position.tuple_ps(),units=self._client_units)
		if s:
			tk.SetSmallFont(dc)
			dc.SetBkMode(win32con.TRANSPARENT)
			dc.DrawText(s,self._position.tuple(),win32con.DT_SINGLELINE|win32con.DT_CENTER|win32con.DT_VCENTER)
			if str_units:
				rc=Rect(self._position.tuple())
				rc.moveByPt(Point((0,9)))
				dc.DrawText(str_units,rc.tuple(),win32con.DT_SINGLELINE|win32con.DT_CENTER|win32con.DT_VCENTER)
				
		# restore dc by selecting old pen and brush
		tk.RestoreFont(dc)
		dc.SelectObjectFromHandle(oldpen)
		Sdk.DeleteObject(pen)


# Context class for draw toolkit
import sysmetrics

class DrawTk:
	# supported tools
	[TOOL_SELECT,TOOL_RECT] = range(2)

	# Hints for OnUpdate
	[	HINT_UPDATE_WINDOW,
		HINT_UPDATE_DRAWOBJ,
		HINT_UPDATE_SELECTION,
		HINT_DELETE_SELECTION,
	] = range(4)

	# select modes
	[	SM_NONE,
		SM_NET,
		SM_MOVE,
		SM_SIZE
	]=range(4)

	def __init__(self):
		self.tool={
			DrawTk.TOOL_SELECT:SelectTool(),
			DrawTk.TOOL_RECT:RectTool()}
		self.down=Point((0,0))
		self.down_flags=0
		self.last=Point((0,0))
		self.currentToolType=DrawTk.TOOL_RECT
		self.selectTool=self.tool[DrawTk.TOOL_SELECT]
		self.rectTool=self.tool[DrawTk.TOOL_RECT]
		self.selectMode = DrawTk.SM_NONE
		self.ixDragHandle=0
		self.lastPoint=Point()
		self._hsmallfont=0
		self._hfont_org=0
		self._limit_rect=1 # number of rect allowed
		self._capture=None
	
		# layout page support
		self._layoutmode=1
		self._brect=None
		self._crect=None
		self._scale=None
		self._bkimg=-1

	def __del__(self):
		if self._hsmallfont:
			Sdk.DeleteObject(self._hsmallfont)
			self._hsmallfont = 0

	def release(self):
		if self._hsmallfont:
			Sdk.DeleteObject(self._hsmallfont)
			self._hsmallfont = 0
		
	def SetCursor(self,view,cursor):
		if cursor!=Sdk.GetCursor():
			#Sdk.SetCursor(cursor)
			Sdk.SetClassLong(view.GetSafeHwnd(),win32con.GCL_HCURSOR,cursor)
			
	def SetCapture(self,wnd):
		self._capture=wnd
	def ReleaseCapture(self,view):
		self._capture=None
	def MouseCaptured(self,wnd):
		return (self._capture==wnd)

	def GetCurrentTool(self):
		return self.tool.get(self.currentToolType)

	def SelectTool(self,tool='select', units = 0):
		if tool=='select':
			self.currentToolType=DrawTk.TOOL_SELECT
		elif tool=='rect':
			self.currentToolType=DrawTk.TOOL_RECT
		else:
			self.currentToolType=DrawTk.TOOL_SELECT
		self.selectTool.setunits(units)
		self.rectTool.setunits(units)

	def LimitRects(self,num):
		self._limit_rect=num
	def OnNewRect(self,view):
		if hasattr(self,'_limit_rect'):
			if len(view._objects)>=self._limit_rect:
				self.currentToolType=DrawTk.TOOL_SELECT	
					
	def SetSmallFont(self,dc):
		if not self._hsmallfont:
			fd={'name':'Arial','height':10,'weight':700}
			self._hsmallfont=Sdk.CreateFontIndirect(fd)		
		self._hfont_org=dc.SelectObjectFromHandle(self._hsmallfont)
	def RestoreFont(self,dc):
		if self._hfont_org:
			dc.SelectObjectFromHandle(self._hfont_org)

	def SetRelCoordRef(self,wnd):
		self._ref_wnd=wnd
	
	
	######################
	# layout page support
	def SetLayoutMode(self,v):
		self._layoutmode=v

	def InLayoutMode(self):
		return self._layoutmode

	def	SetScale(self,scale):
		self._scale=scale

	def GetScale(self):
		if self.InLayoutMode():
			return None
		return self._scale

	def	SetBRect(self,rc):
		self._brect=Rect(rc)
	def	SetCRect(self,rc):
		self._crect=Rect(rc)
	def SetBkImg(self,img):
		self._bkimg=img

	def InDrawArea(self,point):
		if self.InLayoutMode():
			if point.x<0 or point.y<0:
				return 0
			else:
				return 1
		return self._brect.isPtInRectEq(point)

	def InDrawAreaRc(self,rc):
		if self.InLayoutMode():
			return 1
		return self._brect.isRectIn(rc)

	def SetUnits(self,units):
		self.selectTool.setunits(units)
		self.rectTool.setunits(units)
		objs=self._ref_wnd._objects
		if len(objs):objs[0].setunits(units)
		self._ref_wnd._rb_units=units

	def	RestoreState(self):
		self._scale=None
		self._layoutmode=1
		self._has_scale=0
		self._bkimg=-1


#########################	
# MFC View or Layer for other views
	
class DrawLayer:
	def __init__(self):
		self._dragPoint=Point() # current position
		self._dragSize=Size()   # size of dragged object
		self._dragOffset=Point()# offset between pt and drag object corner
		self._objects=[]
		self._selection=[]
		self._grid=1
		self._gridColor=(0, 0, 128)
		self._active=1
		self._drawObjIsDirty=0

	# std view stuff
	def OnUpdate(self,viewSender,hint=None,hintObj=None):
		if hint==DrawTk.HINT_UPDATE_WINDOW:   # redraw entire window
			self.InvalidateRect()
		elif hint==DrawTk.HINT_UPDATE_DRAWOBJ:   # a single object has changed
			self.InvalObj(hintObj)
		elif hint==DrawTk.HINT_UPDATE_SELECTION: # an entire selection list has changed
			if not hintObj:hintObj=self._selection
			for obj in hintObj:
				self.InvalObj(obj)
		elif hint==DrawTk.HINT_DELETE_SELECTION: # an entire selection has been removed
			if hintObj:
				for obj in hintObj:
					self.InvalObj(obj)
					self.Remove(obj)
		else:
			self.InvalidateRect()

	# Convert coordinates CanvasToClient
	def CanvasToClient(self,point):
		dc=self.GetDC()
		#self.OnPrepareDC(dc)
		point=dc.LPtoDP(point.tuple())
		self.ReleaseDC(dc)
		return Point(point)

	# Convert coordinates CanvasToClient Rect
	def CanvasToClientRect(self,rect):
		dc=self.GetDC()
		#self.OnPrepareDC(dc)
		pos=dc.LPtoDP(rect.pos())
		rb_pos=dc.LPtoDP(rect.rb_pos())
		self.ReleaseDC(dc)
		return Rect((pos[0],pos[1],rb_pos[0],rb_pos[1]))


	# Convert coordinates ClientToCanvas
	def ClientToCanvas(self,point):
		dc=self.GetDC()
		#self.OnPrepareDC(dc)
		point=dc.DPtoLP(point.tuple());
		self.ReleaseDC(dc)
		return Point(point)

	# Convert coordinates ClientToCanvas rect
	def ClientToCanvasRect(self,rect):
		dc=self.GetDC()
		#self.OnPrepareDC(dc)
		pos=dc.DPtoLP(rect.pos())
		rb_pos=dc.DPtoLP(rect.rb_pos())
		self.ReleaseDC(dc)
		return Rect((pos[0],pos[1],rb_pos[0],rb_pos[1]))

	# Select the object
	def Select(self,drawObj,add = 0):
		if not add:
			self.OnUpdate(None,DrawTk.HINT_UPDATE_SELECTION,None)
			del self._selection
			self._selection=[]
		if not drawObj or self.IsSelected(drawObj):
			return
		self._selection.append(drawObj)
		#drawObj.select(1)
		self.InvalObj(drawObj)

	# Select objects within rect
	def SelectWithinRect(self,rect,add = 0):
		"""rect is in device coordinates"""
		if not add:
			self.Select(None)
		rect=self.ClientToCanvasRect(rect)
		objList = self._objects
		for obj in objList:
			if obj.intersects(rect):
				self.Select(obj,1)
				

	def Deselect(self,drawObj):
		for obj in self._selection:
			if obj==drawObj:
				self.InvalObj(drawObj)
				self._selection.remove(drawObj)
				break


	def CloneSelection(self):
		for ix in range(len(self._selection)):
			drawObj=self._selection[ix]
			drawObj.clone(drawObj._context)

	def InvalObj(self,drawObj):
		rect = Rect(drawObj._position.tuple())
		rect=self.CanvasToClientRect(rect);
		if self._active and self.IsSelected(drawObj):
			rect.left =rect.left-4;
			rect.top = rect.top-5;
			rect.right = rect.right+5;
			rect.bottom = rect.bottom+4;
		rect.inflateRect(1,1) 
		self.InvalidateRect(rect.tuple(),0)

	def Remove(self,drawObj):
		for obj in self._selection:
			if obj==drawObj:
				self._selection.remove(drawObj)
				break
	def IsSelected(self,drawObj):
		for obj in self._selection:
			if obj==drawObj:return 1
		return 0

	def onCancelEdit(self):
		"""
		The following command handler provides the standard keyboard
		user interface to cancel an in-place editing session.
		"""
		self.ReleaseCapture();

		drawTool = self.drawTk.GetCurrentTool()
		if drawTool:
			drawTool.onCancel(self)
		self.drawTk.currentToolType = self.drawTk.TOOL_SELECT

	def onEditClear(self):
		# update all the views before the selection goes away
		self.UpdateObj(DrawTk.HINT_DELETE_SELECTION,self._selection)
		self.OnUpdate(None,DrawTk.HINT_UPDATE_SELECTION,None)

		# now remove the selection from the document
		for obj in self._selection:
			self.Remove(obj)
			del obj
		del self._selection
		self._selection=[]

	def OnInitialUpdate(self):
		self.drawTk.currentToolType = self.drawTk.TOOL_SELECT


	def onLButtonDown(self, params):
		msg=win32mu.Win32Msg(params)
		point=Point(msg.pos());flags=msg._wParam
		drawTool = self.drawTk.GetCurrentTool()
		if drawTool:
			drawTool.onLButtonDown(self,flags,point);

	def onLButtonUp(self, params):
		msg=win32mu.Win32Msg(params)
		point=Point(msg.pos());flags=msg._wParam
		drawTool = self.drawTk.GetCurrentTool()
		if drawTool:
			drawTool.onLButtonUp(self,flags,point);

	def onLButtonDblClk(self, params):
		msg=win32mu.Win32Msg(params)
		point=Point(msg.pos());flags=msg._wParam
		point_dp=self.ClientToCanvas(point)
		drawObj=self.ObjectAt(point_dp)
		if drawObj:
			s='rect: (%d,%d,%d,%d)' % drawObj._position.tuple()
			win32ui.MessageBox(s)
			return
		drawTool = self.drawTk.GetCurrentTool()
		if drawTool:
			drawTool.onLButtonDblClk(self,flags,point);

	def onMouseMove(self, params):
		msg=win32mu.Win32Msg(params)
		point=Point(msg.pos());flags=msg._wParam
		drawTool = self.drawTk.GetCurrentTool()
		if drawTool:
			drawTool.onMouseMove(self,flags,point)

	# Called when the activation changes
	def OnActivateView(self,activate,activeView,deactiveView):
		self._obj_.OnActivateView(activate,activeView,deactiveView)
		if self._active != activate:
			if activate:
				self._active = activate
		if	len(self._selection):
			self.OnUpdate(None, DrawTk.HINT_UPDATE_SELECTION, None);
		self._active = activate

	def onSize(self,params):
		pass

	# An optimized Drawing function while using the toolkit
	def DrawObjLayer(self,dc):
		# only paint the rect that needs repainting
		rect=self.CanvasToClientRect(Rect(dc.GetClipBox()))
		
		# draw to offscreen bitmap for fast looking repaints
		#dcc=win32ui.CreateDC()
		dcc=dc.CreateCompatibleDC()

		bmp=win32ui.CreateBitmap()
		bmp.CreateCompatibleBitmap(dc,rect.width(),rect.height())
		
		#self.OnPrepareDC(dcc)
		
		# offset origin more because bitmap is just piece of the whole drawing
		dcc.OffsetViewportOrg((-rect.left, -rect.top))
		oldBitmap = dcc.SelectObject(bmp)
		dcc.SetBrushOrg((rect.left % 8, rect.top % 8))
		dcc.IntersectClipRect(rect.tuple())

		# background decoration on dcc
		#dcc.FillSolidRect(rect.tuple(),win32mu.RGB((228,255,228)))
		dcc.FillSolidRect(rect.tuple(),win32mu.RGB(self._active_displist._bgcolor))

		# show draw area
		if not self.drawTk.InLayoutMode():
			l,t,w,h=self._canvas
			if self.drawTk._bkimg<0:
				dcc.FillSolidRect((l,t,l+w,t+h),win32mu.RGB((0,0,0)))
				dcc.FillSolidRect(self.drawTk._crect.tuple(),win32mu.RGB((200,200,0)))
				dcc.FillSolidRect(self.drawTk._brect.tuple(),win32mu.RGB((255,255,255)))
				win32mu.FrameRect(dcc,self.drawTk._crect.tuple(),(0,0,0))
				win32mu.FrameRect(dcc,self.drawTk._brect.tuple(),(0,0,0))
			else:
				#ig = win32ui.Getig()
				import gear32sd
				ig = gear32sd
				img = self.drawTk._bkimg
				ig.device_rect_set(img,(0,0,w,h))
				ig.display_desktop_pattern_set(img,0)
				ig.display_image(img,dcc.GetSafeHdc())

		# draw objects on dcc
		if self._active_displist:
			self._active_displist._render(dcc,rect.tuple())
		self.DrawObjectsOn(dcc)

		
		# copy bitmap
		dc.SetViewportOrg((0, 0))
		dc.SetWindowOrg((0,0))
		dc.SetMapMode(win32con.MM_TEXT)
		dcc.SetViewportOrg((0, 0))
		dcc.SetWindowOrg((0,0))
		dcc.SetMapMode(win32con.MM_TEXT)
		dc.BitBlt(rect.pos(),rect.size(),dcc,(0, 0), win32con.SRCCOPY)

		# clean up (revisit this)
		dcc.SelectObject(oldBitmap)
		dcc.DeleteDC() # needed?
		del bmp



	# Context behaviour
	def UpdateObj(self,hint=None,hintObj=None):
		self.OnUpdate(sender,hint,hintObj)

	# draw support
	def ObjectAt(self,point):
		"""point is in logical coordinates"""
		rect=Rect((point.x,point.y,point.x+1,point.y+1))
		l=self._objects[:]
		l.reverse()
		for obj in l:
			if obj.intersects(rect):
				return obj
		return None

	def DrawObjectsOn(self,dc):
		for obj in self._objects:
			obj.draw(dc,self)
			if self.IsSelected(obj):
				obj.drawTracker(dc,DrawObj.selected)

	def Add(self,drawObj):
		self._objects.append(drawObj)

	def Remove(self,drawObj):
		for obj in self._objects:
			if obj==drawObj:	
				self._objects.remove(drawObj)
				break

	def DeleteContents(self):
		self._objects=[]

	def SetDrawObjDirty(self,f):
		self._drawObjIsDirty=f

	def IsDrawObjDirty(self):
		return self._drawObjIsDirty