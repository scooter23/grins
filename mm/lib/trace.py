__version__ = "$Id$"

import sys
import pprint
import time

class Trace:
	def __init__(self):
		self.dispatch = {
			'call': self.trace_dispatch_call,
			'return': self.trace_dispatch_return,
			'exception': self.trace_dispatch_exception,
			}
		self.curframe = None
		self.depth = 0
		self.__printargs = 1

	def run(self, cmd, globals = None, locals = None):
		if globals is None:
			import __main__
			globals = __main__.__dict__
		if locals is None:
			locals = globals
		sys.setprofile(self.trace_dispatch)
		try:
			exec cmd in globals, locals
		finally:
			sys.setprofile(None)

	def runcall(self, func, *args):
		sys.setprofile(self.trace_dispatch)
		try:
			apply(func, args)
		finally:
			sys.setprofile(None)

	def trace_dispatch(self, frame, event, arg, None = None):
		curframe = self.curframe
		if curframe is not frame:
			if frame.f_back is curframe:
				self.depth = self.depth + 1
			elif curframe is not None and curframe.f_back is frame:
				self.depth = self.depth - 1
##			elif curframe is not None and curframe.f_back is frame.f_back:
##				pass
		self.curframe = frame
		self.dispatch[event](frame, arg)

	def trace_dispatch_call(self, frame, arg, None = None, time = time.time):
		pframe = frame.f_back
		code = frame.f_code
		funcname = code.co_name
		if not funcname:
			funcname = '<lambda>'
		filename = code.co_filename
		lineno = frame.f_lineno
		if lineno == -1:
			code = code.co_code
			if code[0] == '\177': # SET_LINENO
				lineno = ord(code[1]) | ord(code[2]) << 8
		if self.__printargs:
			args = self.__args(frame)
		else:
			args = ''
		if pframe is not None:
			plineno = ' (%d)' % pframe.f_lineno
		else:
			plineno = ''
		print '%s> %s:%d %s(%s)%s' % (' '*self.depth,filename,lineno,funcname,args,plineno)
		frame.f_locals['__start_time'] = time()

	def trace_dispatch_return(self, frame, arg, time = time.time):
		t = frame.f_locals.get('__start_time', '')
		if t != '':
			t = ' [%.4f]' % (time() - t)
		code = frame.f_code
		funcname = code.co_name
		if not funcname:
			funcname = '<lambda>'
		filename = code.co_filename
		print '%s< %s:%d %s%s' % (' '*self.depth,filename,frame.f_lineno,funcname,t)
		self.curframe = frame.f_back
		self.depth = self.depth - 1

	def trace_dispatch_exception(self, frame, arg, time = time.time):
		t = frame.f_locals.get('__start_time', '')
		if t != '':
			t = ' [%.4f]' % (time() - t)
		code = frame.f_code
		funcname = code.co_name
		if not funcname:
			funcname = '<lambda>'
		filename = code.co_filename
		print '%sE %s:%d %s%s' % (' '*self.depth,filename,frame.f_lineno,funcname,t)

	def set_trace(self):
		try:
			raise 'xyzzy'
		except:
			frame = sys.exc_traceback.tb_frame
		while frame.f_code.co_name != 'set_trace':
			frame = frame.f_back
		d = 0
		self.curframe = frame
		while frame:
			d = d + 1
			frame = frame.f_back
		self.depth = d
		sys.setprofile(self.trace_dispatch)

	def __args(self, frame, repr = pprint.saferepr, range = range):
		code = frame.f_code
		dict = frame.f_locals
		isinit = dict.has_key
		n = code.co_argcount
		flags = code.co_flags
		if flags & 4:
			n = n + 1
		if flags & 8:
			n = n + 1
		str = ''
		sep = ''
		varnames = code.co_varnames
		for i in range(n):
			name = varnames[i]
			if isinit(name):
				try:
					val = repr(dict[name])
				except:
					val = '*** not repr-able ***'
			else:
				val = '*** undefined ***'
			str = str + sep + name + '=' + val
			sep = ','
		return str

def run(cmd, globals = None, locals = None):
	Trace().run(cmd, globals, locals)

def runcall(*func_args):
	apply(Trace().runcall, funcargs)

def set_trace():
	Trace().set_trace()

def unset_trace():
	sys.setprofile(None)
