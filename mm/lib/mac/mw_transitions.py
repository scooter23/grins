import time
import Qd
import QuickDraw
import mw_globals

class TransitionClass:
	def __init__(self, engine, dict):
		self.ltrb = (0, 0, 0, 0)
		self.dict = dict
##		self.initial_update = 1
		
	def move_resize(self, ltrb):
		self.ltrb = ltrb
##		self.initial_update = 1
		
	def computeparameters(self, value, oldparameters):
		pass
		
	def updatebitmap(self, parameters, src1, src2, tmp, dst, dstrgn):
##		self.initial_update = 0
		pass
		
	def needtmpbitmap(self):
		return 0
		
class NullTransition(TransitionClass):
	UNIMPLEMENTED=0
	
	def updatebitmap(self, parameters, src1, src2, tmp, dst, dstrgn):
		Qd.CopyBits(src1, dst, self.ltrb, self.ltrb, QuickDraw.srcCopy, dstrgn)
		if self.UNIMPLEMENTED:
			x0, y0, x1, y1 = self.ltrb
			Qd.MoveTo(x0, y0)
			Qd.LineTo(x1, y1)
			Qd.MoveTo(x0, y1)
			Qd.LineTo(x1, y0)
		
class EdgeWipeTransition(TransitionClass):
	# Wipes. Parameters are two ltrb tuples
	def computeparameters(self, value, oldparameters):
		x0, y0, x1, y1 = self.ltrb
		# Assume left-to-right
		xpixels = int(value*(x1-x0)+0.5)
		xcur = x0+xpixels
		return ((x0, y0, xcur, y1), (xcur, y0, x1, y1), )
		
	def updatebitmap(self, parameters, src1, src2, tmp, dst, dstrgn):
		rect1, rect2 = parameters
		Qd.CopyBits(src2, dst, rect2, rect2, QuickDraw.srcCopy, dstrgn)
		Qd.CopyBits(src1, dst, rect1, rect1, QuickDraw.srcCopy, dstrgn)
			
class IrisWipeTransition(TransitionClass):
	def computeparameters(self, value, oldparameters):
		x0, y0, x1, y1 = self.ltrb
		xmid = int((x0+x1+0.5)/2)
		ymid = int((y0+y1+0.5)/2)
		xc0 = int((x0+(1-value)*(xmid-x0))+0.5)
		yc0 = int((y0+(1-value)*(ymid-y0))+0.5)
		xc1 = int((xmid+value*(x1-xmid))+0.5)
		yc1 = int((ymid+value*(y1-ymid))+0.5)
		return ((xc0, yc0, xc1, yc1), (x0, y0, x1, y1))

	def updatebitmap(self, parameters, src1, src2, tmp, dst, dstrgn):
		rect1, rect2 = parameters
		Qd.CopyBits(src2, tmp, rect2, rect2, QuickDraw.srcCopy, dstrgn)
		Qd.CopyBits(src1, tmp, rect1, rect1, QuickDraw.srcCopy, dstrgn)
		Qd.CopyBits(tmp, dst, self.ltrb, self.ltrb, QuickDraw.srcCopy, dstrgn)
			
	def needtmpbitmap(self):
		return 1
		
class RadialWipeTransition(NullTransition):
	UNIMPLEMENTED=1
	
class MatrixWipeTransition(TransitionClass):
	def __init__(self, engine, dict):
		TransitionClass.__init__(self, engine, dict)
		x0, y0, x1, y1 = self.ltrb
		hr = dict.get('horzRepeat', 0)+1
		vr = dict.get('vertRepeat', 0)+1
		self.hsteps = hr
		self.vsteps = vr
		self._recomputeboundaries()
		
	def _recomputeboundaries(self):
		x0, y0, x1, y1 = self.ltrb
		self.hboundaries = []
		self.vboundaries = []
		hr = self.hsteps
		vr = self.vsteps
		for i in range(hr+1):
			self.hboundaries.append(x0+int((x1-x0)*float(i)/(hr+1)+0.5))
		for i in range(vr+1):
			self.vboundaries.append(y0+int((y1-y0)*float(i)/(vr+1)+0.5))
		
	def move_resize(self, ltrb):
		TransitionClass.move_resize(self, ltrb)
		self._recomputeboundaries()
		
	def computeparameters(self, value, oldparameters):
		index = int(value*self.hsteps*self.vsteps)
		hindex = index % self.hsteps
		vindex = index / self.hsteps
		return (hindex, vindex)
		
	def updatebitmap(self, parameters, src1, src2, tmp, dst, dstrgn):
		hindex, vindex = parameters
		Qd.CopyBits(src2, tmp, self.ltrb, self.ltrb, QuickDraw.srcCopy, None)
		x0, y0, x1, y1 = self.ltrb
		rgn = Qd.NewRgn()
		for i in range(vindex):
			rgn2 = Qd.NewRgn()
			rect = (x0, self.vboundaries[i], x1, self.vboundaries[i+1])
			Qd.RectRgn(rgn2, rect)
			Qd.UnionRgn(rgn, rgn2, rgn)
			Qd.DisposeRgn(rgn2)
		ylasttop = self.vboundaries[vindex]
		ylastbottom = self.vboundaries[vindex+1]
		for i in range(hindex):
			rgn2 = Qd.NewRgn()
			rect = (self.hboundaries[i], ylasttop, self.hboundaries[i+1], ylastbottom)
			Qd.RectRgn(rgn2, rect)
			Qd.UnionRgn(rgn, rgn2, rgn)
			Qd.DisposeRgn(rgn2)
		Qd.CopyBits(src1, tmp, self.ltrb, self.ltrb, QuickDraw.srcCopy, rgn)
		Qd.DisposeRgn(rgn)
		Qd.CopyBits(tmp, dst, self.ltrb, self.ltrb, QuickDraw.srcCopy, dstrgn)
		
	def needtmpbitmap(self):
		return 1
				
class PushWipeTransition(TransitionClass):
	# Parameters are src1-ltrb, dst1-ltrb, src2-ltrb, dst2-ltrb
	def computeparameters(self, value, oldparameters):
		x0, y0, x1, y1 = self.ltrb
		# Assume left-to-right
		xpixels = int(value*(x1-x0)+0.5)
		return ((x1-xpixels, y0, x1, y1), (x0, y0, x0+xpixels, y1),
				(x0, y0, x1-xpixels, y1), (x0+xpixels, y0, x1, y1) )

	def updatebitmap(self, parameters, src1, src2, tmp, dst, dstrgn):
		srcrect1, dstrect1, srcrect2, dstrect2 = parameters
		Qd.CopyBits(src2, dst, srcrect2, dstrect2, QuickDraw.srcCopy, dstrgn)
		Qd.CopyBits(src1, dst, srcrect1, dstrect1, QuickDraw.srcCopy, dstrgn)
			
class SlideWipeTransition(TransitionClass):
	# Parameters are src1-ltrb, dst1-ltrb, 2-ltrb
	def computeparameters(self, value, oldparameters):
		x0, y0, x1, y1 = self.ltrb
		# Assume left-to-right
		xpixels = int(value*(x1-x0)+0.5)
		return ((x1-xpixels, y0, x1, y1), (x0, y0, x0+xpixels, y1), (x0+xpixels, y0, x1, y1), )

	def updatebitmap(self, parameters, src1, src2, tmp, dst, dstrgn):
		srcrect1, dstrect1, rect2 = parameters
		Qd.CopyBits(src2, dst, rect2, rect2, QuickDraw.srcCopy, dstrgn)
		Qd.CopyBits(src1, dst, srcrect1, dstrect1, QuickDraw.srcCopy, dstrgn)
		
class FadeTransition(TransitionClass):
	def computeparameters(self, value, oldparameters):
		return int(value*0xffff), int(value*0xffff), int(value*0xffff)
		
	def updatebitmap(self, parameters, src1, src2, tmp, dst, dstrgn):
		Qd.OpColor(parameters)
		Qd.CopyBits(src2, tmp, self.ltrb, self.ltrb, QuickDraw.srcCopy, dstrgn)
		Qd.CopyBits(src1, tmp, self.ltrb, self.ltrb, QuickDraw.blend, dstrgn)
		Qd.CopyBits(tmp, dst, self.ltrb, self.ltrb, QuickDraw.srcCopy, dstrgn)
		
	def needtmpbitmap(self):
		return 1
	
TRANSITIONDICT = {
	"edgeWipe" : EdgeWipeTransition,
	"irisWipe" : IrisWipeTransition,
	"radialWipe" : RadialWipeTransition,
	"matrixWipe" : MatrixWipeTransition,
	"pushWipe" : PushWipeTransition,
	"slideWipe" : SlideWipeTransition,
	"fade" : FadeTransition,
}

def TransitionFactory(trtype, subtype):
	"""Return the class that implements this transition. Incomplete, only looks
	at type right now"""
	if TRANSITIONDICT.has_key(trtype):
		return TRANSITIONDICT[trtype]
	return NullTransition

class TransitionEngine:
	def __init__(self, window, inout, runit, dict):
		dur = dict.get('dur', 1)
		self.windows = [window]
		self.starttime = time.time()	# Correct?
		self.duration = dur
		self.running = runit
		self.value = 0
		trtype = dict['trtype']
		subtype = dict.get('subtype')
		klass = TransitionFactory(trtype, subtype)
		self.transitiontype = klass(self, dict)
		self.dstrgn = None
		self.move_resize()
		self.currentparameters = None
		# xxx startpercent/endpercent
		# xxx transition type, etc
		mw_globals.toplevel.setidleproc(self._idleproc)
		
	def join(self, window):
		"""Join this (sub or super) window to an existing transition"""
		self.windows.append(window)
		self.move_resize()
		
	def endtransition(self):
		"""Called by upper layer (window) to tear down the transition"""
		if self.windows != None:
			mw_globals.toplevel.cancelidleproc(self._idleproc)
			self.windows = None
			self.transitiontype = None
		
	def need_tmp_wid(self):
		return self.transitiontype.needtmpbitmap()
		
	def move_resize(self):
		"""Internal: recompute the region and rect on which this transition operates"""
		if self.dstrgn:
			Qd.DisposeRgn(self.dstrgn)
		x0, y0, x1, y1 = self.windows[0].qdrect()
		self.dstrgn = Qd.NewRgn()
		for w in self.windows:
			rect = w.qdrect()
			newrgn = Qd.NewRgn()
			Qd.RectRgn(newrgn, rect)
			Qd.UnionRgn(self.dstrgn, newrgn, self.dstrgn)
			Qd.DisposeRgn(newrgn)
			nx0, ny0, nx1, ny1 = rect
			if nx0 < x0: x0 = nx0
			if ny0 < y0: y0 = ny0
			if nx1 > x1: x1 = nx1
			if ny1 > y1: y1 = ny1
		self.transitiontype.move_resize((x0, y0, x1, y1))
			
		
	def _idleproc(self):
		"""Called in the event loop to optionally do a recompute"""
		self.changed(0)
		
	def changed(self, mustredraw=1):
		"""Called by upper layer when it wants the destination bitmap recalculated. If
		mustredraw is true we should do the recalc even if the transition hasn't advanced."""
		if self.running:
			self.value = float(time.time() - self.starttime) / self.duration
			if self.value >= 0.5:
				pass # DBG
			if self.value >= 1.0:
				self._cleanup()
				return
		self._doredraw(mustredraw)
		
	def settransitionvalue(self, value):
		"""Called by uppoer layer when it has a new percentage value"""
		self.value = value / 100.0
		self._doredraw()
		
	def _cleanup(self):
		"""Internal function called when our time is up. Ask the upper layer (window)
		to tear us down"""
		wcopy = self.windows[:]
		for w in wcopy:
			w.endtransition()
		
	def _doredraw(self, mustredraw):
		"""Internal: do the actual computation, iff anything has changed since last time"""
		oldparameters = self.currentparameters
		self.currentparameters = self.transitiontype.computeparameters(self.value, oldparameters)
		if self.currentparameters == oldparameters and not mustredraw:
			return
		# All windows in the transition share their bitmaps, so we can pick any of them
		w = self.windows[0]
		dst = w._mac_getoswindowpixmap(mw_globals.BM_ONSCREEN)
		src_active = w._mac_getoswindowpixmap(mw_globals.BM_DRAWING)
		src_passive = w._mac_getoswindowpixmap(mw_globals.BM_PASSIVE)
		tmp = w._mac_getoswindowpixmap(mw_globals.BM_TEMP)
		w._mac_setwin(mw_globals.BM_ONSCREEN)
		Qd.RGBBackColor((0xffff, 0xffff, 0xffff))
		Qd.RGBForeColor((0, 0, 0))
		self.transitiontype.updatebitmap(self.currentparameters, src_active, src_passive, tmp, dst, 
			self.dstrgn)
