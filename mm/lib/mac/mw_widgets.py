import Win
import Qd
import QuickDraw
import List
import Lists
import Ctl
import Controls
import ControlAccessor
import App
import Evt
import Dlg

import img
import imgformat
import mac_image

#
# Stuff needed from other mw_ modules
#
import mw_globals
import mw_menucmd

class _Widget:
	def __init__(self, wid, item):
		tp, h, rect = wid.GetDialogItem(item) # XXXX To be fixed
		wid.SetDialogItem(item, tp,
		      mw_globals.toplevel._dialog_user_item_handler, rect)
		      
	def close(self):
		pass
		
class _ControlWidget:
	def close(self):
		pass	

	def _activate(self, onoff):
		pass # Handled by dialog mgr
		
	def _redraw(self, rgn):
		pass # Handled by dialog mgr
				
class _ImageMixin:

	def _loadimagefromfile(self, image, scale=None):
		if not image:
			return
		format = imgformat.macrgb16
		try:
			rdr = img.reader(format, image)
			bits = rdr.read()
		except (img.error, IOError):
			return
		
		pixmap = mac_image.mkpixmap(rdr.width, rdr.height, format, bits)
		return (rdr.width, rdr.height, (pixmap, bits))

	def _redrawimage(self, rect, image_data):
		w, h, (pixmap, dataref) = image_data
		dl, dt, dr, db = rect
		#
		# If there is enough room center the image
		#
		if dr-dl > w:
			dl = dl + ((dr-dl)-w)/2
			dr = dl + w
		if db-dt > h:
			dt = dt + ((db-dt)-h)/2
			db = dt + h
			
		srcrect = 0, 0, w, h
		dstrect = dl, dt, dr, db
		fgcolor = self.wid.GetWindowPort().rgbFgColor
		bgcolor = self.wid.GetWindowPort().rgbBkColor
		Qd.RGBBackColor((0xffff, 0xffff, 0xffff))
		Qd.RGBForeColor((0, 0, 0))
		Qd.CopyBits(pixmap,
		      self.wid.GetWindowPort().portBits,
		      srcrect, dstrect,
		      QuickDraw.srcCopy+QuickDraw.ditherCopy,
		      None)
		Qd.RGBBackColor(bgcolor)
		Qd.RGBForeColor(fgcolor)

class _ListWidget(_ControlWidget):
	def __init__(self, wid, item, content=[], multi=0):
		self.control = wid.GetDialogItemAsControl(item)
##		d1, d2, self.rect = wid.GetDialogItem(item)
		self.rect = (0, 0, 1000, 1000) # DBG
		h = self.control.GetControlDataHandle(Controls.kControlListBoxPart, 
			Controls.kControlListBoxListHandleTag)
		self.list = List.as_List(h)
		self.list.LAddRow(len(content), 0)
##?		self.list.LSetDrawingMode(0)
##		# wid is the window (dialog) where our list is going to be in
##		# rect is it's item rectangle (as in dialog item)
##		self.rect = rect
##		rect2 = rect[0]+1, rect[1]+1, rect[2]-16, rect[3]-1
##		self.list = List.LNew(rect2, (0, 0, 1, len(content)),
##					 (0,0), 0, wid,	0, 0, 0, 1)
		if not multi:
			self.list.selFlags = Lists.lOnlyOne
		self._data = []
		self._setcontent(0, len(content), content)
		self.wid = wid
##?		self.list.LSetDrawingMode(1)
##		Win.InvalRect(self.rect)
##		self._redraw() # DBG
	
	def close(self):
##		print 'DBG: close', self
		del self.list  # XXXX Or should we DisposeList it?
		del self.wid
		del self._data
		del self.control
		pass

##	def __del__(self):
##		print 'del', self
		
	def _setcontent(self, fr, to, content):
		for y in range(fr, to):
			item = content[y-fr]
			self.list.LSetCell(item, (0, y))
		self._data[fr:to] = content
		
	def _delete(self, fr=None, count=1):
		if fr is None:
			self.list.LDelRow(0,0)
			self._data = []
		else:
			self.list.LDelRow(count, fr)
			del self._data[fr:fr+count]
			
	def _insert(self, where=-1, count=1):
		if where == -1:
			where = 32766
			self._data = self._data + [None]*count
		else:
			self._data[where:where] = [None]*count
		return self.list.LAddRow(count, where)
		
	def delete(self, fr=None, count=1):
		self._delete(fr, count)
		Qd.SetPort(self.wid)
		Win.InvalRect(self.rect)
		
	def setitems(self, content=[], select=None):
		self._delete()
		self._insert(count=len(content))
		self._setcontent(0, len(content), content)
		self.select(select)
		Qd.SetPort(self.wid)
		Win.InvalRect(self.rect)
		
	def get(self):
		return self._data
		
	def getitem(self, item):
		return self._data[item]
		
	def insert(self, where=-1, content=[]):
		where = self._insert(where, len(content))
		self._setcontent(where, where+len(content), content)
		Qd.SetPort(self.wid)
		Win.InvalRect(self.rect)
		
	def replace(self, where, what):
		self._setcontent(where, where+1, [what])
		Qd.SetPort(self.wid)
		Win.InvalRect(self.rect)
		
	def _deselectall(self):
		while 1:
			ok, pt = self.list.LGetSelect(1, (0,0))
			if not ok: return
			self.list.LSetSelect(0, pt)
			
	def select(self, num, autoscroll=0):
		self._deselectall()
		if num in self._data:
			num = self._data.index(num)
		if num is None or num < 0:
			return
		self.list.LSetSelect(1, (0, num))
		if autoscroll:
			self.list.LAutoScroll()
		
	def getselect(self):
		ok, (x, y) = self.list.LGetSelect(1, (0,0))
		if not ok:
			return None
		return y
		
	def getselectvalue(self):
		num = self.getselect()
		if num is None:
			return None
		return self._data[num]
		
	def setkeyboardfocus(self):
		Ctl.SetKeyboardFocus(self.wid, self.control, Controls.kControlListBoxPart)

class _AreaWidget(_ControlWidget, _ImageMixin):
	def __init__(self, wid, item, callback=None, scaleitem=None):
		self.wid = wid
		self.scaleitem = scaleitem
		self.control = wid.GetDialogItemAsControl(item)
		self.rect = self.control.GetControlRect()
		self.control.SetControlDataCallback(0, Controls.kControlUserPaneDrawProcTag, self.redraw)
		self.control.SetControlDataCallback(0, Controls.kControlUserPaneHitTestProcTag, self.hittest)
##		self.control.SetControlDataCallback(0, Controls.kControlUserPaneTrackingProcTag, self.tracking)
		self.image = None
		self.outerrect = (0, 0, 1, 1)
		self.otherrects = []
		self.ourrect = (0, 0, 1, 1)
		self.recalc()
		self.callback = callback
		self._background_image = None
		
	def close(self):
		del self.wid
		del self.control
		del self.callback
		del self._background_image
		
	def redraw(self, ctl, part):
		try:
			Qd.SetPort(self.wid)
			Qd.RGBBackColor((0xffff, 0xffff, 0xffff))
			if self._background_image:
				self._redrawimage(self.rect, self._background_image)
			else:
				Qd.EraseRect(self.rect)
			Qd.RGBForeColor((0x7fff, 0x7fff, 0x7fff))
			Qd.FrameRect(self.rect)
			for r in self.otherrects:
				Qd.RGBForeColor((0x0, 0x7fff, 0x7fff))
				Qd.FrameRect(r)
			self.drawourrect()
		except:
			import traceback, sys
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_exception(exc_type, exc_value, None)
			traceback.print_tb(exc_traceback)

	def drawourrect(self):
		port = self.wid.GetWindowPort()
		Qd.RGBForeColor((0x0, 0, 0))
		oldmode = port.pnMode
		Qd.PenMode(QuickDraw.srcXor)
		Qd.FrameRect(self.ourrect)
		for l in self.lurven:
			Qd.PaintRect(l)
		Qd.PenMode(oldmode)
	
	def hittest(self, ctl, (x, y)):
		try:
##			print "hittest", ctl, x, y
			for i in range(len(self.lurven)-1, -1, -1):
				lx0, ly0, lx1, ly1 = self.lurven[i]
				if lx0 <= x <= lx1 and ly0 <= y <= ly1:
					# track
					if Evt.StillDown():
						self.tracklurf(i, (x, y))
					if self.callback:
						self.callback()
					return 1
			return 0
		except:
			import traceback, sys
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_exception(exc_type, exc_value, None)
			traceback.print_tb(exc_traceback)
			
	def tracklurf(self, lurf, (x, y)):
		x0, y0, x1, y1 = self.rect
		if lurf == 4:
			# Adapt pinning rectangle for middle lurf
			rx0, ry0, rx1, ry1 = self.ourrect
			w = (rx1-rx0)/2
			h = (ry1-ry0)/2
			x0 = x0 + w
			x1 = x1 - w
			y0 = y0 + h
			y1 = y1 - h
		while Evt.WaitMouseUp():
			newx, newy = Evt.GetMouse()
			# Pin the mouse to our rectangle
			if newx < x0: newx = x0
			if newx > x1: newx = x1
			if newy < y0: newy = y0
			if newy > y1: newy = y1
			deltax = newx-x
			deltay = newy-y
			x = newx
			y = newy
			if deltax or deltay:
				# Something has changed. Recompute and redraw
				self.drawourrect()
				rx0, ry0, rx1, ry1 = self.ourrect
				if lurf in (0, 3, 4, 6):
					rx0 = rx0 + deltax
					if rx0 > rx1: rx0 = rx1
				if lurf in (0, 1, 2, 4):
					ry0 = ry0 + deltay
					if ry0 > ry1: ry0 = ry1
				if lurf in (2, 4, 5, 8):
					rx1 = rx1 + deltax
					if rx1 < rx0: rx1 = rx0
				if lurf in (4, 6, 7, 8):
					ry1 = ry1 + deltay
					if ry1 < ry0: ry1 = ry0
				self.ourrect = rx0, ry0, rx1, ry1
				self.recalclurven()
				self.drawourrect()
		
##	def tracking(self, *args):
##		print "tracking", args
##		return 0
##		
		
	def setinfo(self, outerrect, image=None, otherrects=[]):
		self.outerrect = outerrect
		self.image = image
		self.otherrects = []
		for r in otherrects:
			self.oterrects.append(self.rect2screen(r))
		self.recalc()
		self._background_image = self._loadimagefromfile(image, self.scale)
		
	def recalc(self):
		scale = 1
		x, y, w, h = self.outerrect
		fullrect = self.control.GetControlRect()
		x0, y0, x1, y1 = fullrect
##		print 'outer', x, y, w, h
##		print 'ctl', x0, y0, x1, y1
		if x0 >= x1 or y0 >= y1:
			return
		while scale*(x1-x0) < w:
			scale = scale*2
		while scale*(y1-y0) < h:
			scale = scale*2
		w_extra = (x1-x0) - w/scale
		h_extra = (y1-y0) - h/scale
		self.rect = (x0+w_extra/2, y0+h_extra/2, x1-w_extra/2, y1-h_extra/2)
		self.scale = scale
##		print 'self.rect', self.rect
##		print 'scale', self.scale
		Qd.SetPort(self.wid)
		Win.InvalRect(fullrect)
		if self.scaleitem != None:
			if self.scale == 1:
				text = ''
			else:
				text = '(scale 1:%d, %dx%d)'%(self.scale, w, h)
			h = self.wid.GetDialogItemAsControl(self.scaleitem)
			Dlg.SetDialogItemText(h, text)

	def recalclurven(self):
##		print 'ourrect', self.ourrect
		x0, y0, x1, y1 = self.ourrect
		self.lurven = []
		for y in (y0, (y0+y1)/2, y1):
			for x in (x0, (x0+x1)/2, x1):
				self.lurven.append((x-2, y-2, x+2, y+2))
##		print 'lurven', self.lurven
		
	def set(self, rect):
		self.ourrect = self.rect2screen(rect)
		self.recalclurven()
		fullrect = self.control.GetControlRect()
		Qd.SetPort(self.wid)
		Win.InvalRect(fullrect)
		
	def get(self):
		return self.screen2rect(self.ourrect)
		
	def rect2screen(self, (x, y, w, h)):
		x0, y0, x1, y1 = self.rect
		return x0+x/self.scale, y0+y/self.scale, x0+(x+w)/self.scale, y0+(y+h)/self.scale
		
	def screen2rect(self, (rx0, ry0, rx1, ry1)):
		x0, y0, x1, y1 = self.rect
		w = rx1-rx0
		h = ry1-ry0
		return (rx0-x0)*self.scale, (ry0-y0)*self.scale, w*self.scale, h*self.scale
					
class _ImageWidget(_Widget, _ImageMixin):
	def __init__(self, wid, item, image=None):
		_Widget.__init__(self, wid, item)
		tp, h, rect = wid.GetDialogItem(item)
		# wid is the window (dialog) where our image is going to be in
		# rect is it's item rectangle (as in dialog item)
		self.rect = rect
		self.image = image
		self.wid = wid
		Win.InvalRect(self.rect)
		
	def close(self):
##		print 'DBG: close', self
		del self.image
		del self.wid
		self.image_data = None
		del self.image_data
			
	def setfromfile(self, image):
		Qd.SetPort(self.wid)
		Win.InvalRect(self.rect)
		self.image_data = self._loadimagefromfile(image)
				
	def _redraw(self, rgn=None):
##		if rgn == None:
##			rgn = self.wid.GetWindowPort().visRgn
		Qd.SetPort(self.wid)
		if not self.image_data:
			Qd.EraseRect(self.rect)
		else:
			self._redrawimage(self.rect, self.image_data)
		Qd.FrameRect(self.rect)

	def _activate(self, onoff):
		pass
				
class _SelectWidget(_ControlWidget):
	def __init__(self, wid, ctlid, items=[], default=None, callback=None):
		self.wid = wid
		self.itemnum = ctlid
		self.menu = None
##		self.choice = None
		self.control = self.wid.GetDialogItemAsControl(self.itemnum)
		self.setitems(items, default)
		if callback:
			raise 'Menu-callbacks not supported anymore'
		
	def close(self):
##		print 'DBG: close', self
		del self.wid
##		self.control.SetControlDataHandle(Controls.kControlMenuPart,
##				Controls.kControlPopupButtonMenuHandleTag, self.orig_menu)
		del self.control
##		self.menu.delete()
		del self.menu
		pass
		
##	def __del__(self):
##		print 'del', self
		
	def delete(self):
##		print 'DBG: delete (obsolete)', self
		pass
		
	def setitems(self, items=[], default=None):
		items = items[:]
		if not items:
			items.append('')
##		self.choice = None
		self.data = items
		oldmenu = self.menu
		self.menu = mw_menucmd.SelectPopupMenu(items)
		mhandle, mid = self.menu.getpopupinfo()
##		self.orig_menu = self.control.GetControlDataHandle(Controls.kControlMenuPart,
##				Controls.kControlPopupButtonMenuHandleTag)
		self.control.SetControlDataHandle(Controls.kControlMenuPart,
				Controls.kControlPopupButtonMenuHandleTag, mhandle)
##		ControlAccessor.SetControlData(self.control, Controls.kControlMenuPart,
##				Controls.kControlPopupButtonMenuIDTag, mid)
		self.control.SetControlMinimum(1)
		self.control.SetControlMaximum(len(items)+1)
		if default != None:
			self.select(default)
		if oldmenu:
			oldmenu.delete()
		
	def select(self, item):
		if item in self.data:
			item = self.data.index(item)
		elif type(item) != type(0):
			print "SelectWidget: select impossible value:", item #DBG
			item = 0
		self.control.SetControlValue(item+1)
		
##	def click(self, event=None):
##		self.usercallback()
		
	def getselectvalue(self):
		item = self.control.GetControlValue()-1
		if 0 <= item < len(self.data):
			return self.data[item]
		return None
		
	def getselect(self):
		return self.control.GetControlValue()-1

	def setkeyboardfocus(self):
		pass		# Not useful for menus
