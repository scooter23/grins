__version__ = "$Id$"


import win32ui, win32con, win32api
Afx=win32ui.GetAfx()
Sdk=win32ui.GetWin32Sdk()
import os

from types import *
from WMEVENTS import *
from appcon import *
from sysmetrics import *
import grinsRC


import win32mu
import usercmd,wndusercmd,usercmdui
from components import *

import win32menu, MenuTemplate
import __main__
 
###########################################################
# import window core stuff
from pywin.mfc import window,object,docview,dialog
import afxres,commctrl
import cmifwnd	
import afxexttb # part of generated afxext.py


##################################
from FormServer import FormServer
from ViewServer import ViewServer,appview

##########
class GRiNSToolbar(window.Wnd):
	def __init__(self, parent):
		style = win32con.WS_CHILD |\
			win32con.WS_VISIBLE |\
			afxres.CBRS_TOP |\
			afxres.CBRS_TOOLTIPS|\
			afxres.CBRS_FLYBY|\
			afxres.CBRS_SIZE_DYNAMIC
		wndToolBar = win32ui.CreateToolBar(parent,style,afxres.AFX_IDW_TOOLBAR)
		wndToolBar.LoadToolBar(grinsRC.IDR_GRINSED)
		wndToolBar.EnableDocking(afxres.CBRS_ALIGN_ANY)
		wndToolBar.SetWindowText(AppDispName)
		wndToolBar.ModifyStyle(0, commctrl.TBSTYLE_FLAT)
		window.Wnd.__init__(self,wndToolBar)

class GRiNSDlgBar(window.Wnd):
	def __init__(self, parent):
		AFX_IDW_DIALOGBAR=0xE805
		wndDlgBar = win32ui.CreateDialogBar()
		window.Wnd.__init__(self,wndDlgBar)
		wndDlgBar.CreateWindow(parent,grinsRC.IDD_GRINSEDBAR,
			afxres.CBRS_ALIGN_BOTTOM,AFX_IDW_DIALOGBAR)
		import components
		self._tab=components.TabCtrl(self,grinsRC.IDC_TAB_GRINSVIEWS)
		self._tab.attach_to_parent()
		for viewno in range(len(appview.keys())):
			self._tab.insertitem(viewno,appview[viewno]['title'])
		rc=win32mu.Rect(parent.GetClientRect())
		self.sizeto(rc.width(),rc.height())

	def getid(self):
		return grinsRC.IDD_GRINSEDBAR
	def sizeto(self,w,h):
		rc=win32mu.Rect(self._tab.getwindowrect())
		self._tab.setwindowpos(0,(0,0,w,rc.height()),
			win32con.SWP_NOMOVE|win32con.SWP_NOZORDER)
	def postcmd(self,wnd,viewno):
		if viewno==0: return
		cmdcl=appview[viewno]['cmd']
		usercmd_ui = usercmdui.class2ui[cmdcl]
		wnd.PostMessage(win32con.WM_COMMAND,usercmd_ui.id)
	def settab(self,ix):
		self._tab.setcursel(ix)

####################################
		
class MDIFrameWnd(window.MDIFrameWnd,cmifwnd._CmifWnd,ViewServer):
	wndpos=None
	wndsize=None
	def __init__(self):
		window.MDIFrameWnd.__init__(self)
		cmifwnd._CmifWnd.__init__(self)
		ViewServer.__init__(self,self)
		self._do_init(__main__.toplevel)
		self._formServer=FormServer(self)
		
	def create(self,title):
		strclass=self.registerwndclass()		
		self._obj_.Create(strclass,title)

		# toolbar
		self.EnableDocking(afxres.CBRS_ALIGN_ANY)
		self._wndToolBar=GRiNSToolbar(self)
		self.DockControlBar(self._wndToolBar)
		if IsPlayer:
			self.setPlayerToolbar()
		else:
			self.setEditorFrameToolbar()

	def registerwndclass(self):
		# register top frame class
		clstyle=win32con.CS_DBLCLKS
		exstyle=0
		icon=Afx.GetApp().LoadIcon(grinsRC.IDI_GRINS_ED)
		cursor=Afx.GetApp().LoadStandardCursor(win32con.IDC_ARROW)
		brush=0 #Sdk.CreateBrush(win32con.BS_SOLID,win32mu.RGB(self._bgcolor),0)
		return Afx.RegisterWndClass(clstyle,cursor,brush,icon)


	def PreCreateWindow(self, csd):
		csd=self._obj_.PreCreateWindow(csd)
		cs=win32mu.CreateStruct(csd)

		# sizes
		if not MDIFrameWnd.wndsize:
			MDIFrameWnd.wndsize=win32mu.Point(((3*scr_width_pxl/4),(3*scr_height_pxl/4)))
		cs.cx,cs.cy=MDIFrameWnd.wndsize.tuple()

		if not MDIFrameWnd.wndpos:
			MDIFrameWnd.wndpos=win32mu.Point((scr_width_pxl/8,scr_height_pxl/8))
		cs.x,cs.y=MDIFrameWnd.wndpos.tuple()

		# menu from MenuTemplate
		# hold instance for dunamic menus
		self._mainmenu=win32menu.Menu()
		self._mainmenu.create_from_menubar_spec_list(MenuTemplate.MENUBAR,self.get_cmdclass_id)
		cs.hMenu=self._mainmenu.GetHandle()

		return cs.to_csd()
	
	def get_cmdclass_id(self,cmdcl):
		if cmdcl in usercmdui.class2ui.keys():
			return usercmdui.class2ui[cmdcl].id
		else: 
			print 'CmdClass not found',cmdcl
			return -1

	# this is called after CWnd::OnCreate 
	def OnCreate(self, createStruct):
		self.HookMessage(self.onSize,win32con.WM_SIZE)
		self.HookMessage(self.onMove,win32con.WM_MOVE)
		self.HookMessage(self.onInitMenu,win32con.WM_INITMENU)
		# the view is responsible for user input
		# so do not hook other messages

		# direct all cmds to self.OnUserCmd but dissable them
		for cmdcl in usercmdui.class2ui.keys():
			id=usercmdui.class2ui[cmdcl].id
			self.HookCommand(self.OnUserCmd,id)
			self.HookCommandUpdate(self.OnUpdateCmdDissable,id)
		self.HookCommand(self.OnWndUserCmd,afxres.ID_WINDOW_CASCADE)
		self.HookCommand(self.OnWndUserCmd,afxres.ID_WINDOW_TILE_VERT)
		self.HookCommand(self.OnWndUserCmd,afxres.ID_WINDOW_TILE_HORZ)
		id=usercmdui.class2ui[wndusercmd.CLOSE_ACTIVE_WINDOW].id
		self.HookCommand(self.OnCloseActiveWindow,id)

		id=usercmdui.class2ui[wndusercmd.ABOUT_GRINS].id
		self.HookCommand(self.OnAbout,id)
		self.HookCommandUpdate(self.OnUpdateCmdEnable,id)

		id=usercmdui.class2ui[wndusercmd.SELECT_CHARSET].id
		self.HookCommand(self.OnCharset,id)
		self.HookCommandUpdate(self.OnUpdateCmdEnable,id)

		client=self.GetMDIClient()
		client.HookMessage(self.OnMdiRefreshMenu,win32con.WM_MDIREFRESHMENU)
		self._active_child=None
		# hook tab sel change
		TCN_FIRST =-550;TCN_SELCHANGE  = TCN_FIRST - 1
		self.HookNotify(self.OnNotifyTcnSelChange,TCN_SELCHANGE)

		return 0

	# protect player from modal menus
	def onInitMenu(self,params):
		return # for dev
		if self.is_playing():
			self.SendMessage(win32con.WM_COMMAND,usercmdui.class2ui[usercmd.PAUSE].id)
			__main__.toplevel.settimer(0.001,(self.autostart,()))
	def autostart(self):
		self.SendMessage(win32con.WM_COMMAND,usercmdui.class2ui[usercmd.PAUSE].id)
	def is_playing(self):
		return self._cmifdoc and self._cmifdoc.player and self._cmifdoc.player.playing
	def is_pausing(self):
		return self._cmifdoc and self._cmifdoc.player and self._cmifdoc.player.pausing
	def kick_timer(self):
		if self.is_playing():self._cmifdoc.timer_callback()
		
	
	# mirror mdi window-menu to tab bar (not impl)
	# do ... on new activate	
	def OnMdiRefreshMenu(self,params):
		msg=win32mu.Win32Msg(params)
		id=usercmdui.class2ui[wndusercmd.CLOSE_ACTIVE_WINDOW].id
		#print 'OnMdiRefreshMenu',msg._wParam,msg._lParam
		t=self.MDIGetActive()
		if not t:
			self._active_child=None
			self.HookCommandUpdate(self.OnUpdateCmdDissable,id)
			self.HookCommandUpdate(self.OnUpdateCmdDissable,afxres.ID_WINDOW_CASCADE)
			self.HookCommandUpdate(self.OnUpdateCmdDissable,afxres.ID_WINDOW_TILE_VERT)
			self.HookCommandUpdate(self.OnUpdateCmdDissable,afxres.ID_WINDOW_TILE_HORZ)
			return
		f,ismax=t
		if not self._active_child or self._active_child!=f:	
			if hasattr(f,'_view'):
				self._active_child=f
				v=f._view
				self.set_commandlist(v._commandlist,v._strid)
			else:
				self._active_child=None 
		self.HookCommandUpdate(self.OnUpdateCmdEnable,id)
		self.HookCommandUpdate(self.OnUpdateCmdEnable,afxres.ID_WINDOW_CASCADE)
		self.HookCommandUpdate(self.OnUpdateCmdEnable,afxres.ID_WINDOW_TILE_VERT)
		self.HookCommandUpdate(self.OnUpdateCmdEnable,afxres.ID_WINDOW_TILE_HORZ)

					
	def OnNotifyTcnSelChange(self, nm, nmrest=(0,)):
		self.ActivateFrame()
		hwndFrom,idFrom,code=nm
		if idFrom==grinsRC.IDC_TAB_GRINSVIEWS:
			viewno=self._wndDlgBar._tab.getcursel()
			if appview[viewno]['obj']:
				self.MDIActivate(appview[viewno]['obj'])
			return 1
		return 0

	def OnAbout(self,id,code):
		from version import version
		dlg=AboutDlg(arg=0,version = 'GRiNS ' + version,parent=self)
		dlg.DoModal()

	def OnCharset(self,id,code):
		import Font
		prompt = 'Select Charset:'
		list = []
		for name in Font.win32_charsets_list:
			list.append(name, (Font.set_win32_charset, (name,)))
		Dialog(list, title = 'Select Charset', prompt = prompt, grab = 1, vertical = 1, parent = self)

	def OnWndUserCmd(self,id,code):
		client=self.GetMDIClient()
		if id==afxres.ID_WINDOW_TILE_HORZ:
			client.SendMessage(win32con.WM_MDITILE,win32con.MDITILE_HORIZONTAL)			
		elif id==afxres.ID_WINDOW_TILE_VERT:
			client.SendMessage(win32con.WM_MDITILE,win32con.MDITILE_VERTICAL)			
		elif id==afxres.ID_WINDOW_CASCADE:
			client.SendMessage(win32con.WM_MDICASCADE)			
	
	def OnCloseActiveWindow(self,id,code):
		t=self.MDIGetActive()
		if not t: return
		f,ismax=t
		f.PostMessage(win32con.WM_CLOSE)
				
	def init_cmif(self, x, y, w, h, title,units = UNIT_MM,
		      adornments = None,commandlist = None):	
		if not w or w==0:
			w=(3*scr_width_mm/4)
		if not h or h==0:
			h=(3*scr_height_mm/4)
		if not x: x=scr_width_mm/8
		if not y: y=scr_height_mm/8

		self.newcmwindow=self.newwindow #alias
		self._canscroll = 0
		self._title = AppDisplayName # ignore title		
		self._topwindow = self
		self._window_type = SINGLE # actualy not applicable
		self._sizes = 0, 0, 1, 1
		# we must check since we reuse
		if self not in __main__.toplevel._subwindows:
			self._parent._subwindows.insert(0, self)
		xp,yp,wp,hp = to_pixels(x,y,w,h,units)
		self._rectb= xp,yp,wp,hp
		self._sizes = (float(xp)/scr_width_pxl,float(yp)/scr_height_pxl,float(wp)/scr_width_pxl,float(hp)/scr_height_pxl)
		self._depth = __main__.toplevel.getscreendepth()
		
		# all, are historic alias but useful to markup externals
		# the symbol self._obj_ reresents the os-mfc window object
		self._wnd=self._obj_ 
		self._hWnd=self.GetSafeHwnd()

		# set adorments and cmdlist
		self._cmifdoc=None
		self._qtitle={'frame':self._title,'document':None,'view':None}
		self._activecmds={'frame':{},'document':{},'view':{}}
		self._dynamiclists={}
		self._dyncmds={}
		self.set_commandlist(commandlist,'frame')

		l,t,r,b=self.GetClientRect()
		self._canvas=self._rect=(l,t,r-l,b-t)
		if hasattr(self,'_wndDlgBar'):
			self._wndDlgBar.sizeto(r-l,b-t)
	

	def newdocument(self,cmifdoc,adornments,commandlist):
		if not self._cmifdoc:
			self.setdocument(cmifdoc,adornments,commandlist)
			return self
		else:
			frame = MDIFrameWnd()
			frame.create(self._qtitle['frame'])
			frame.init_cmif(None, None, 0, 0,self._qtitle['frame'],
				UNIT_MM,None,self.get_commandlist('frame'))
			frame.setdocument(cmifdoc,adornments,commandlist)
			return frame

	def setdocument(self,cmifdoc,adornments,commandlist):
		self._cmifdoc=cmifdoc
		self.settitle(cmifdoc.basename,'document')
		self.set_commandlist(commandlist,'document')
		if not IsPlayer:
			self.setEditorDocumentToolbar()
			#self._wndDlgBar=GRiNSDlgBar(self)
			self.RecalcLayout()			
		self.ActivateFrame()

	def newwindow(self, x, y, w, h, title, visible_channel = TRUE,
		      type_channel = SINGLE, pixmap = 0, units = UNIT_MM,
		      adornments = None, canvassize = None,
		      commandlist = None, resizable = 1):
		if 'view' in adornments.keys():strid=adornments['view']
		else: strid='cmifview_'
		return self.newview(x, y, w, h, title, units, adornments,canvassize, commandlist,strid)

	def getdoc(self):
		if self.countMDIChildWnds()==0:
			self._doc=docview.Document(docview.DocTemplate())
		return self._doc

	def textwindow(self,text):
		sv=self.newviewobj('sview_')
		sv.settext(text)
		self.showview(sv,'sview_')
		return sv

	def getformserver(self):
		return self._formServer

	def newChildFrame(self,view,decor=None):
		return ChildFrame(view,decor)
	def Activate(self,view):
		self.MDIActivate(view)
	def getPrefRect(self):
		rc= win32mu.Rect(self.GetClientRect())
		return rc.width()/8,rc.height()/8,7*rc.width()/8,7*rc.height()/8

	# simulate user	closing
	def close_all_views(self):
		currentChild=None
		count=0
		l=[]
		while 1:
			currentChild=self.getNextMDIChildWnd(currentChild)
			if currentChild:l.append(currentChild)
			else: break
		for w in l:
			w.SendMessage(win32con.WM_CLOSE)

	def setviewtab(self,viewno):
		if hasattr(self,'_wndDlgBar'):
			self._wndDlgBar.settab(viewno)

	def setwaiting(self):
		#self.BeginWaitCursor();
		pass
		
	def setready(self):
		self.EndWaitCursor();
		self.ActivateFrame()


	def close(self):
		# 1. first close all views
		self.close_all_views()
		self._mainmenu.clear_cascade_menus()

		# 2. then the document
		self._cmifdoc=None
		self.set_commandlist(None,'document')
		self.settitle(None,'document')
		if not IsPlayer and len(__main__.toplevel._subwindows)==1:
			self.setEditorFrameToolbar()
		if hasattr(self,'_wndDlgBar'):
			self._wndDlgBar.DestroyWindow()
			self.RecalcLayout()

		# 3. if there is another top-level frame
		# we should close self frame
		if len(__main__.toplevel._subwindows)>1:
			self.DestroyWindow()	
			
	def onSize(self,params):
		self.RecalcLayout()
		msg=win32mu.Win32Msg(params)
		if msg.minimized(): return
		self._rect=self._canvas=0,0,msg.width(),msg.height()
		if hasattr(self,'_wndDlgBar'):
			self._wndDlgBar.sizeto(msg.width(),msg.height())
		rc=self.GetWindowRect()
		MDIFrameWnd.wndsize=win32mu.Point((rc[2]-rc[0],rc[3]-rc[1]))

	def onMove(self,params):
		rc=self.GetWindowRect()
		MDIFrameWnd.wndpos=win32mu.Point((rc[0],rc[1]))


	def setcoords(self,coords,units=UNIT_MM):
		x, y, w, h = coords
		x,y,w,h=to_pixels(x,y,w,h,units)
		rc=(x,y,x+w,y+h)
		l,t,r,b=self.CalcWindowRect(rc,0)
		w=r-l+2*cxframe+4
		h=b-t+3*cycaption+16+4
		flags=win32con.SWP_NOZORDER|win32con.SWP_NOACTIVATE |win32con.SWP_NOMOVE
		self.SetWindowPos(0,(0,0,w,h),flags)

	def maximize(self,child):
		client=self.GetMDIClient()
		client.SendMessage(win32con.WM_MDIMAXIMIZE,child.GetSafeHwnd())

	def set_commandlist(self,commandlist,context='view'):
		if context not in self._activecmds.keys():
			self._activecmds[context]={}
		contextcmds=self._activecmds[context]
		otherids=self.othercmdids(context)
		menu=self.GetMenu()
		for id in contextcmds.keys():
			if id not in otherids.keys():
				self.HookCommandUpdate(self.OnUpdateCmdDissable,id)
		contextcmds.clear()
		if not commandlist: return
		for cmd in commandlist:
			usercmd_ui = usercmdui.class2ui[cmd.__class__]
			id=usercmd_ui.id
			self.HookCommandUpdate(self.OnUpdateCmdEnable,id)
			contextcmds[id]=cmd

	def othercmdids(self,except_context):
		d={}
		for context in self._activecmds.keys():
			if context==except_context:continue
			contextcmds=self._activecmds[context]
			for id in contextcmds.keys():d[id]=1
		return d

	def get_commandlist(self,context='view'):
		return self._activecmds[context].values()
	def enable_commandlist(self,context,enable):
		contextcmds=self._activecmds[context]
		commandlist=contextcmds.values()
		if enable:
			for cmd in commandlist:
				usercmd_ui = usercmdui.class2ui[cmd.__class__]
				self.HookCommandUpdate(self.OnUpdateCmdEnable,usercmd_ui.id)
		else:
			menu=self.GetMenu()
			for cmd in commandlist:
				usercmd_ui = usercmdui.class2ui[cmd.__class__]
				self.HookCommandUpdate(self.OnUpdateCmdDissable,usercmd_ui.id)
				menu.CheckMenuItem(usercmd_ui.id,win32con.MF_BYCOMMAND | win32con.MF_UNCHECKED)
			
	def set_toggle(self, cmdcl, onoff):
		id=usercmdui.class2ui[cmdcl].id
		flags = win32con.MF_BYCOMMAND
		if onoff==0:flags = flags | win32con.MF_UNCHECKED
		else:flags = flags | win32con.MF_CHECKED
		(self.GetMenu()).CheckMenuItem(id,flags)

	####=========dynamic menu
	#	('fond', (<method Player.channel_callback of Player instance at 1c68510>, ('fond',)), 't', 1)
	#	('smiley', (<method Player.channel_callback of Player instance at 1c68510>, ('smiley',)), 't', 1)
	#	('text', (<method Player.channel_callback of Player instance at 1c68510>, ('text',)), 't', 1)
	def set_dynamiclist(self, command, list):
		self._dynamiclists[command]=list
		submenu=self._mainmenu.get_cascade_menu(command)
		idstart = usercmdui.class2ui[command].id+1
		cmd = self.GetUserCmd(command)
		if cmd is None:
			# dissable submenu cmds?
			# they are always active?
			return
		if not cmd.dynamiccascade:
			raise error, 'non-dynamic command in set_dynamiclist'

		callback = cmd.callback
		menuspec = []
		if command not in self._dyncmds.keys():
			self._dyncmds[command]={}
		else:
			self._dyncmds[command].clear()
		for entry in list:
			entry = (entry[0], (callback, entry[1])) + entry[2:]
			menuspec.append(entry)			
		if submenu:
			self._mainmenu.clear_cascade(command)
			win32menu._create_menu(submenu,menuspec,idstart,self._dyncmds[command])
			self.set_dyncbd(self._dyncmds[command],submenu)

	def get_cascade_menu(self,id):
		cl=usercmdui.get_cascade(id)
		return self._mainmenu.get_cascade_menu(cl)
		
	def OnUserDynCmd(self,id,code):
		for cbd in self._dyncmds.values():
			if cbd.has_key(id):
				if not cbd[id]:return
				apply(apply,cbd[id])
				submenu=self.get_cascade_menu(id)
				if id not in submenu._toggles.keys():return
				state=submenu.GetMenuState(id,win32con.MF_BYCOMMAND)
				if state & win32con.MF_CHECKED:
					submenu.CheckMenuItem(id,win32con.MF_BYCOMMAND | win32con.MF_UNCHECKED)
				else:
					submenu.CheckMenuItem(id,win32con.MF_BYCOMMAND | win32con.MF_CHECKED)
				return

	def set_dyncbd(self,cbd,menu):
		for id in cbd.keys():
			self.HookCommand(self.OnUserDynCmd,id)
			self.HookCommandUpdate(self.OnUpdateCmdEnable,id)
		
	def EnableDynCmds(self,cmdcl):
		for cbd in self._dyncmds.values():
			if cbd.has_key(id):
				if cbd[id]:apply(apply,cbd[id])
				return

	def OnUpdateCmdEnable(self,cmdui):
		cmdui.Enable(1)

	def OnUpdateCmdDissable(self,cmdui):
		cmdui.Enable(0)

	def OnUserCmd(self,id,code):
		cmd=None
		
		# look first self._active_child cmds
		if self._active_child and self._active_child._view._strid in self._activecmds.keys():
			contextcmds=self._activecmds[self._active_child._view._strid]
			if contextcmds.has_key(id):
				cmd=contextcmds[id]
				if cmd is not None and cmd.callback is not None:
					self.check_menu_item(id)
					apply(apply,cmd.callback)
				return

		# the command does not belong to self._active_child
		# look to others (including dynamic menus)
		for context in self._activecmds.keys():
			contextcmds=self._activecmds[context]
			if contextcmds.has_key(id):
				cmd=contextcmds[id]
				if cmd is not None and cmd.callback is not None:
					self.check_menu_item(id)
					apply(apply,cmd.callback)
				return

	def check_menu_item(self,id):
		if id not in self._mainmenu._toggles.keys(): return
		state=self._mainmenu.GetMenuState(id,win32con.MF_BYCOMMAND)
		if state & win32con.MF_CHECKED:
			self._mainmenu.CheckMenuItem(id,win32con.MF_BYCOMMAND | win32con.MF_UNCHECKED)
		else:
			self._mainmenu.CheckMenuItem(id,win32con.MF_BYCOMMAND | win32con.MF_CHECKED)

	def GetUserCmdId(self,cmdcl):
		return usercmdui.class2ui[cmdcl].id

	def GetUserCmd(self,cmdcl):
		id=usercmdui.class2ui[cmdcl].id
		cmd=None
		for context in self._activecmds.keys():
			contextcmds=self._activecmds[context]
			if contextcmds.has_key(id):
				cmd=contextcmds[id]
		return cmd

	def fire_cmd(self,cmdcl):
		id=usercmdui.class2ui[cmdcl].id
		self.OnUserCmd(id,0)
		
	def settitle(self,title,context='view'):
		self._qtitle[context]=title
		qtitle=''
		if self._qtitle['document']:
			qtitle= qtitle + self._qtitle['document'] + ' - '
		elif self._qtitle['view']:
				qtitle=qtitle + self._qtitle['view'] + ' - '
		qtitle=qtitle + self._qtitle['frame']
		self.SetWindowText(qtitle)

	def set_adornments(self, adornments):
		pass			

	def OnClose(self):
		if len(__main__.toplevel._subwindows)>1:
			self.PostMessage(win32con.WM_COMMAND,usercmdui.CLOSE_UI.id)
		else:
			self.PostMessage(win32con.WM_COMMAND,usercmdui.EXIT_UI.id)

	def pop(self):
		self.BringWindowToTop()

	def push(self):
		pass


	def OnDestroy(self, msg):
		if self in __main__.toplevel._subwindows:
			__main__.toplevel._subwindows.remove(self)
		window.MDIFrameWnd.OnDestroy(self, msg)

	# should be set from adornments
	# but for now...
	def setEditorFrameToolbar(self):
		self._wndToolBar.AllocateButtons(4)

		id=usercmdui.class2ui[usercmd.NEW_DOCUMENT].id
		self._wndToolBar.SetButtonInfo(0,id,afxexttb.TBBS_BUTTON,0)

		self._wndToolBar.SetButtonInfo(1,afxexttb.ID_SEPARATOR,afxexttb.TBBS_SEPARATOR,6);

		id=usercmdui.class2ui[usercmd.OPEN].id
		self._wndToolBar.SetButtonInfo(2,id,afxexttb.TBBS_BUTTON, 1)

		id=usercmdui.class2ui[usercmd.SAVE].id
		self._wndToolBar.SetButtonInfo(3,id,afxexttb.TBBS_BUTTON, 2)
				
		self.ShowControlBar(self._wndToolBar,1,0)

	# should be set from from adornments
	# but for now...
	def setEditorDocumentToolbar(self):
		self._wndToolBar.AllocateButtons(15)

		id=usercmdui.class2ui[usercmd.NEW_DOCUMENT].id
		self._wndToolBar.SetButtonInfo(0,id,afxexttb.TBBS_BUTTON,0)

		self._wndToolBar.SetButtonInfo(1,afxexttb.ID_SEPARATOR,afxexttb.TBBS_SEPARATOR,6);

		id=usercmdui.class2ui[usercmd.OPEN].id
		self._wndToolBar.SetButtonInfo(2,id,afxexttb.TBBS_BUTTON, 1)

		id=usercmdui.class2ui[usercmd.SAVE].id
		self._wndToolBar.SetButtonInfo(3,id,afxexttb.TBBS_BUTTON, 2)
	
		# Play Toolbar
		self._wndToolBar.SetButtonInfo(4,afxexttb.ID_SEPARATOR,afxexttb.TBBS_SEPARATOR,6);

		id=usercmdui.class2ui[usercmd.RESTORE].id
		self._wndToolBar.SetButtonInfo(5,id,afxexttb.TBBS_BUTTON, 6)

		id=usercmdui.class2ui[usercmd.CLOSE].id
		self._wndToolBar.SetButtonInfo(6,id,afxexttb.TBBS_BUTTON, 7)

		self._wndToolBar.SetButtonInfo(7,afxexttb.ID_SEPARATOR,afxexttb.TBBS_SEPARATOR,6);

		id=usercmdui.class2ui[usercmd.PLAY].id
		self._wndToolBar.SetButtonInfo(8,id,afxexttb.TBBS_BUTTON, 9)

		id=usercmdui.class2ui[usercmd.PAUSE].id
		self._wndToolBar.SetButtonInfo(9,id,afxexttb.TBBS_BUTTON, 10)

		id=usercmdui.class2ui[usercmd.STOP].id
		self._wndToolBar.SetButtonInfo(10,id,afxexttb.TBBS_BUTTON, 11)

		self._wndToolBar.SetButtonInfo(11,afxexttb.ID_SEPARATOR,afxexttb.TBBS_SEPARATOR,12);
	
		id=usercmdui.class2ui[wndusercmd.CLOSE_ACTIVE_WINDOW].id
		self._wndToolBar.SetButtonInfo(12,id,afxexttb.TBBS_BUTTON, 14)

		self._wndToolBar.SetButtonInfo(13,afxexttb.ID_SEPARATOR,afxexttb.TBBS_SEPARATOR,12);

		id=usercmdui.class2ui[usercmd.HELP].id
		self._wndToolBar.SetButtonInfo(14,id,afxexttb.TBBS_BUTTON, 12)

		self.ShowControlBar(self._wndToolBar,1,0)


	# should be set from from adornments
	# but for now...
	def setPlayerToolbar(self):
		self._wndToolBar.AllocateButtons(9)

		id=usercmdui.class2ui[usercmd.OPEN].id
		self._wndToolBar.SetButtonInfo(0,id,afxexttb.TBBS_BUTTON, 1)

		# Play Toolbar
		self._wndToolBar.SetButtonInfo(1,afxexttb.ID_SEPARATOR,afxexttb.TBBS_SEPARATOR,6);

		id=usercmdui.class2ui[usercmd.CLOSE].id
		self._wndToolBar.SetButtonInfo(2,id,afxexttb.TBBS_BUTTON, 7)

		self._wndToolBar.SetButtonInfo(3,afxexttb.ID_SEPARATOR,afxexttb.TBBS_SEPARATOR,6);

		id=usercmdui.class2ui[usercmd.PLAY].id
		self._wndToolBar.SetButtonInfo(4,id,afxexttb.TBBS_BUTTON, 9)

		id=usercmdui.class2ui[usercmd.PAUSE].id
		self._wndToolBar.SetButtonInfo(5,id,afxexttb.TBBS_BUTTON, 10)

		id=usercmdui.class2ui[usercmd.STOP].id
		self._wndToolBar.SetButtonInfo(6,id,afxexttb.TBBS_BUTTON, 11)
	
		self._wndToolBar.SetButtonInfo(7,afxexttb.ID_SEPARATOR,afxexttb.TBBS_SEPARATOR,6);

		id=usercmdui.class2ui[usercmd.HELP].id
		self._wndToolBar.SetButtonInfo(8,id,afxexttb.TBBS_BUTTON, 12)
	
		self.ShowControlBar(self._wndToolBar,1,0)

	def countMDIChildWnds(self):
		currentChild=None
		count=0
		while 1:
			currentChild=self.getNextMDIChildWnd(currentChild)
			if currentChild:count=count+1
			else: break
		return count

	def getNextMDIChildWnd(self,currentChild=None):
		client=self.GetMDIClient()
		if not currentChild:
			# Get the first child window.
			currentChild=client.GetWindow(win32con.GW_CHILD)
		else:
			# Get the next child window in the list.
			currentChild=currentChild.GetWindow(win32con.GW_HWNDNEXT)
		if not currentChild:
			# No child windows exist in the MDIClient,
			# or we are at the end of the list. This check
			# will terminate any recursion.
			return None
		# Check the kind of window
		owner=currentChild.GetWindow(win32con.GW_OWNER)
		if not owner:
			if currentChild.IsKindOfMDIChildWnd():
	            # MDIChildWnd or a derived class.
				return currentChild
			else:
				# Window is foreign to the MFC framework.
				# Check the next window in the list recursively.
				return self.GetNextMDIChildWnd(currentChild)
		else:
			# Title window associated with an iconized child window.
			# Recurse over the window manager's list of windows.
			return self.GetNextMDIChildWnd(currentChild)	

