__version__ = "$Id$"

import win32ui, win32con, win32api
Sdk=win32ui.GetWin32Sdk()
Afx=win32ui.GetAfx()

import GenWnd
import usercmd, usercmdui	
from WMEVENTS import *
	
WM_USER_OPEN = win32con.WM_USER+1
WM_USER_CLOSE = win32con.WM_USER+2
WM_USER_PLAY = win32con.WM_USER+3
WM_USER_STOP = win32con.WM_USER+4
WM_USER_PAUSE = win32con.WM_USER+5
WM_USER_GETSTATUS = win32con.WM_USER+6
WM_USER_SETHWND = win32con.WM_USER+7
WM_USER_UPDATE = win32con.WM_USER+8
WM_USER_MOUSE_CLICKED  = win32con.WM_USER+9
WM_USER_MOUSE_MOVED  = win32con.WM_USER+10

STOPPED, PAUSING, PLAYING = range(3)
UNKNOWN = -1

class ListenerWnd(GenWnd.GenWnd):
	def __init__(self, toplevel):
		GenWnd.GenWnd.__init__(self)
		self._toplevel = toplevel
		self.create()
		self._docmap = {}
		self.HookMessage(self.OnOpen, WM_USER_OPEN)
		self.HookMessage(self.OnClose, WM_USER_CLOSE)
		self.HookMessage(self.OnPlay, WM_USER_PLAY)
		self.HookMessage(self.OnStop, WM_USER_STOP)
		self.HookMessage(self.OnPause, WM_USER_PAUSE)
		self.HookMessage(self.OnGetStatus, WM_USER_GETSTATUS)
		self.HookMessage(self.OnSetWindow, WM_USER_SETHWND)
		self.HookMessage(self.OnUpdate, WM_USER_UPDATE)
		self.HookMessage(self.OnMouseClicked, WM_USER_MOUSE_CLICKED)
		self.HookMessage(self.OnMouseMoved, WM_USER_MOUSE_MOVED)

	def OnOpen(self, params):
		# lParam (params[3]) is a pointer to a c-string
		filename = Sdk.GetWMString(params[3])
		event = 'OnOpen'
		try:
			func, arg = self._toplevel.get_embedded(event)
			func(arg, self, event, filename)
			self._docmap[params[2]] = self._toplevel.get_most_recent_docframe()
		except:
			pass

	def OnClose(self, params):
		wnd = self._docmap.get(params[2])
		if wnd: wnd.PostMessage(win32con.WM_COMMAND,usercmdui.class2ui[usercmd.CLOSE].id)

	def OnPlay(self, params):
		wnd = self._docmap.get(params[2])
		if wnd: wnd.PostMessage(win32con.WM_COMMAND,usercmdui.class2ui[usercmd.PLAY].id)

	def OnStop(self, params):
		wnd = self._docmap.get(params[2])
		if wnd: wnd.PostMessage(win32con.WM_COMMAND,usercmdui.class2ui[usercmd.STOP].id)

	def OnPause(self, params):
		wnd = self._docmap.get(params[2])
		if wnd: wnd.PostMessage(win32con.WM_COMMAND,usercmdui.class2ui[usercmd.PAUSE].id)

	def OnGetStatus(self, params):
		print 'OnGetStatus'

	def OnSetWindow(self, params):
		self._toplevel.set_embedded_hwnd(params[2], params[3])

	def OnUpdate(self, params):
		wnd = self._toplevel.get_embedded_wnd(params[2])
		if wnd: wnd.update()

	def OnMouseClicked(self, params):
		wnd = self._toplevel.get_embedded_wnd(params[2])
		x, y = win32api.LOWORD(params[3]),win32api.HIWORD(params[3])
		wnd.onMouseEvent((x,y),Mouse0Press)
		wnd.onMouseEvent((x,y),Mouse0Release)

	def OnMouseMoved(self, params):
		wnd = self._toplevel.get_embedded_wnd(params[2])
		x, y = win32api.LOWORD(params[3]),win32api.HIWORD(params[3])
		wnd.onMouseMoveEvent((x,y))

############################
import win32window
import ddraw
from pywinlib.mfc import window
from appcon import *
import win32mu
import grinsRC

class EmbeddedWnd(win32window.DDWndLayer):
	def __init__(self, wnd, w, h, units, bgcolor, hwnd=0, title='', id=0):
		self._cmdframe = wnd
		self._peerwnd = wnd
		self._smildoc = wnd.getgrinsdoc()
		self._peerid = id
		self._bgcolor = bgcolor

		self._viewport = win32window.Viewport(self, 0, 0, w, h, bgcolor)
		self._rect = 0, 0, w, h

		win32window.DDWndLayer.__init__(self, self, bgcolor)
		if hwnd:
			self._peerwnd = window.Wnd(win32ui.CreateWindowFromHandle(hwnd))
			self.createDDLayer(w, h, hwnd)
		else:
			self.createBackDDLayer(w, h, wnd.GetSafeHwnd())
		self.settitle(title)

		try:
			from __main__ import commodule
			commodule.AdviceSetSize(self._peerid, w, h)
		except:
			pass

	def attach(self, hwnd):
		self.destroyDDLayer()
		self._peerwnd = window.Wnd(win32ui.CreateWindowFromHandle(hwnd))
		x, y, w, h = self._rect
		self.createDDLayer(w, h, hwnd)

	def settitle(self,title):
		import urllib
		title=urllib.unquote(title)
		self._title=title
		if self._peerwnd:
			parent = self._peerwnd.GetParent()
			if parent:
				parent.SetWindowText(title)
	#
	# Playback query support
	#
	def getTime(self):
		player = self._smildoc.player
		if not player: return UNKNOWN
		scheduler = player.scheduler
		return scheduler.timefunc()

	def getDuration(self):
		return -1

	def getState(self):
		player = self._smildoc.player
		if not player: return UNKNOWN
		return player.getstate()


	#
	# paint
	#
	def update(self, rc=None, exclwnd=None):
		if not self._ddraw or not self._frontBuffer or not self._backBuffer:
			return
		if self._frontBuffer.IsLost():
			if not self._frontBuffer.Restore():
				# we can't do anything for this
				# system is busy with video memory
				#self.InvalidateRect(self.GetClientRect())
				return
		if self._backBuffer.IsLost():
			if not self._backBuffer.Restore():
				# and for this either
				# system should be out of memory
				#self.InvalidateRect(self.GetClientRect())
				return
		
		# do we have anything to update?
		if rc and (rc[2]==0 or rc[3]==0): 
			return 

		self.paint(rc, exclwnd)
		
		if rc is None:
			x, y, w, h = self._viewport._rect
			rcBack = x, y, x+w, y+h
		else:
			rc = self.rectAnd(rc, self._viewport._rect)
			rcBack = rc[0], rc[1], rc[0]+rc[2], rc[1]+rc[3]
		
		rcFront = self.getContextOsWnd().ClientToScreen(rcBack)
		try:
			self._frontBuffer.Blt(rcFront, self._backBuffer, rcBack)
		except ddraw.error, arg:
			print 'EmbeddedWnd.update', arg

	def paint(self, rc=None, exclwnd=None):
		if rc is None:
			x, y, w, h = self._viewport._rect
			rcPaint = x, y, x+w, y+h
		else:
			rc = self.rectAnd(rc, self._viewport._rect)
			rcPaint = rc[0], rc[1], rc[0]+rc[2], rc[1]+rc[3] 

		try:
			self._backBuffer.BltFill(rcPaint, self._ddbgcolor)
		except ddraw.error, arg:
			print 'EmbeddedWnd.paint',arg
			return

		if self._viewport:
			self._viewport.paint(rc, exclwnd)


	def getRGBBitCount(self):
		return self._pxlfmt[0]

	def getPixelFormat(self):
		returnself._pxlfmt

	def getDirectDraw(self):
		return self._ddraw

	def getContextOsWnd(self):
		return self._peerwnd

	def pop(self, poptop=1):
		pass

	def getwindowpos(self):
		return self._viewport._rect

	def closeViewport(self, viewport):
		del viewport
		self.destroyDDLayer()

	def getDrawBuffer(self):
		return self._backBuffer

	def updateMouseCursor(self):
		pass

	def imgAddDocRef(self, file):
		self._cmdframe.imgAddDocRef(file)

	def CreateSurface(self, w, h):
		ddsd = ddraw.CreateDDSURFACEDESC()
		ddsd.SetFlags(ddraw.DDSD_WIDTH | ddraw.DDSD_HEIGHT | ddraw.DDSD_CAPS)
		ddsd.SetCaps(ddraw.DDSCAPS_OFFSCREENPLAIN)
		ddsd.SetSize(w,h)
		dds = self._ddraw.CreateSurface(ddsd)
		dds.BltFill((0, 0, w, h), self._ddbgcolor)
		return dds

	def ltrb(self, xywh):
		x,y,w,h = xywh
		return x, y, x+w, y+h

	def xywh(self, ltrb):
		l,t,r,b = ltrb
		return l, t, r-l, b-t

	def rectAnd(self, rc1, rc2):
		# until we make calcs
		import win32ui
		rc, ans= win32ui.GetWin32Sdk().IntersectRect(self.ltrb(rc1),self.ltrb(rc2))
		if ans:
			return self.xywh(rc)
		return 0, 0, 0, 0

	#
	# Mouse input
	#
	def onMouseEvent(self, point, ev):
		return  self._viewport.onMouseEvent(point, ev)

	def onMouseMoveEvent(self, point):
		return  self._viewport.onMouseMove(0, point)

	def setcursor(self, strid):
		try:
			from __main__ import commodule
			commodule.AdviceSetCursor(self._peerid, strid)
		except:
			pass

	#
	# OS windows 
	#
	def setClientRect(self, w, h):
		l1, t1, r1, b1 = self.GetWindowRect()
		l2, t2, r2, b2 = self.GetClientRect()
		dxe = dye = 0
		#if (self._exstyle & WS_EX_CLIENTEDGE):
		#	dxe = 2*win32api.GetSystemMetrics(win32con.SM_CXEDGE)
		#	dye = 2*win32api.GetSystemMetrics(win32con.SM_CYEDGE)
		wi = (r1-l1) - (r2-l2)
		wp = w + wi + dxe
		hi = (b1-t1) - (b2-t2)
		hp = h + hi + dye
		flags=win32con.SWP_NOMOVE | win32con.SWP_NOZORDER 		
		self.SetWindowPos(0, (0,0,wp,hp), flags)

	def createOsWnd(self, rect, color, title='Viewport'):
		brush=Sdk.CreateBrush(win32con.BS_SOLID,win32mu.RGB(color),0)
		cursor=Afx.GetApp().LoadStandardCursor(win32con.IDC_ARROW)
		icon=Afx.GetApp().LoadIcon(grinsRC.IDR_GRINSED)
		clstyle=win32con.CS_DBLCLKS
		style=win32con.WS_OVERLAPPEDWINDOW | win32con.WS_CLIPCHILDREN
		exstyle = 0
		strclass=Afx.RegisterWndClass(clstyle,cursor,brush,icon)
		self.CreateWindowEx(exstyle,strclass,title,style,
			self.ltrb(rect), None, 0)		
		self.ShowWindow(win32con.SW_SHOW)

class showmessage:
	def __init__(self, text, mtype = 'message', grab = 1, callback = None,
		     cancelCallback = None, name = 'message',
		     title = 'GRiNS', parent = None, identity = None):
		self._res = win32con.IDOK
		if callback and self._res==win32con.IDOK:
			apply(apply,callback)
		elif cancelCallback and self._res==win32con.IDCANCEL:
			apply(apply,cancelCallback)








