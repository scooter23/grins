__version__ = "$Id$"

import imgformat
import struct

_bigendian = struct.pack('i', 1)[0] == '\0'

class reader:
	def __init__(self):
		self.width = 16
		self.height = 16
		format = imgformat.colormap
		self.format = format
		self.format_choices = (format,)
		import imgcolormap
		if _bigendian:
			self.colormap = imgcolormap.new('''\
\0\0\0\0\0\1\1\1\0\0\0\377\0\200\200\200\0\377\377\377\0\377\0\0\0\0\0\0\
\0\0\0\0''')
		else:
			self.colormap = imgcolormap.new('''\
\0\0\0\0\1\1\1\0\377\0\0\0\200\200\200\0\377\377\377\0\0\0\377\0\0\0\0\0\
\0\0\0\0''')
		self.transparent = 1
		self.top = 0
		self.left = 0
		self.aspect = 0

	def read(self):
		return '''\
\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\0\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\0\1\1\1\1\
\1\1\1\1\1\1\1\1\1\1\1\0\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\0\1\1\1\1\1\1\1\1\
\1\1\1\1\1\1\1\0\1\1\1\1\1\3\3\3\3\3\3\2\2\1\1\0\1\1\1\1\1\3\5\5\5\5\2\3\
\1\2\1\0\1\1\1\1\1\3\5\4\4\2\5\3\1\1\2\0\1\1\1\1\1\3\5\4\2\4\5\3\2\2\2\0\
\1\1\1\1\1\3\5\4\4\4\5\3\1\1\1\0\1\1\1\1\1\3\5\5\5\5\5\3\1\1\1\0\1\1\1\1\
\1\3\3\3\3\3\3\3\1\1\1\0\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\0\1\1\1\1\1\1\1\1\
\1\1\1\1\1\1\1\0\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\0\1\1\1\1\1\1\1\1\1\1\1\1\
\1\1\1\0'''
