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
\0\0\0\0\0\0\231\0\0\1\1\1\0\0f\0\0\4\4\4\0\0\0\0\0\0\0\0\0\0\0\0''')
		else:
			self.colormap = imgcolormap.new('''\
\0\0\0\0\0\231\0\0\1\1\1\0\0f\0\0\4\4\4\0\0\0\0\0\0\0\0\0\0\0\0\0''')
		self.transparent = 2
		self.top = 0
		self.left = 0
		self.aspect = 0

	def read(self):
		return '''\
\2\2\2\2\2\2\2\2\2\2\2\2\2\2\2\0\2\2\2\2\2\2\2\2\2\2\2\2\2\2\2\0\2\2\2\2\
\2\2\2\2\2\2\2\2\2\2\2\0\2\2\2\2\2\2\2\2\2\2\2\2\2\2\2\0\2\2\2\2\2\2\2\2\
\2\2\2\2\2\2\2\0\2\2\2\2\2\2\4\4\4\4\4\2\2\2\2\0\2\2\2\2\2\4\3\1\3\1\3\4\
\2\2\2\0\2\2\2\2\2\4\1\3\1\3\1\4\2\2\2\0\2\2\2\2\2\4\3\1\3\1\3\4\2\2\2\0\
\2\2\2\2\2\4\1\3\1\3\1\4\2\2\2\0\2\2\2\2\2\4\3\1\3\1\3\4\2\2\2\0\2\2\2\2\
\2\2\4\4\4\4\4\2\2\2\2\0\2\2\2\2\2\2\2\2\2\2\2\2\2\2\2\0\2\2\2\2\2\2\2\2\
\2\2\2\2\2\2\2\0\2\2\2\2\2\2\2\2\2\2\2\2\2\2\2\0\2\2\2\2\2\2\2\2\2\2\2\2\
\2\2\2\0'''
