__version__ = "$Id$"

from ChannelThread import ChannelWindowThread
import MMurl

class MovieChannel(ChannelWindowThread):
	def threadstart(self):
		import moviechannel
		return moviechannel.init()

	def getaltvalue(self, node):
		import string
		url = self.getfileurl(node)
		i = string.rfind(url, '.')
		if i > 0 and url[i:] == '.v':
			return 1
		return 0

	def do_arm(self, node, same=0):
		if node.type != 'ext':
			self.errormsg(node, 'Node must be external')
			return 1
		import MMAttrdefs, GLLock, VFile
		url = self.getfileurl(node)
		try:
			filename = MMurl.urlretrieve(url)[0]
			vfile = VFile.RandomVinFile(filename)
		except (EOFError, IOError, VFile.Error), msg:
			if type(msg) is type(self):
				if hasattr(msg, 'strerror'):
					msg = msg.strerror
				else:
					msg = msg.args[0]
			elif type(msg) is type(()):
				msg = msg[1]
			self.errormsg(node, url + ':\n' + msg)
			return 1
		try:
			vfile.readcache()
		except VFile.Error:
			print `url` + ': no cached index'
		arminfo = {'width': vfile.width,
			   'height': vfile.height,
			   'format': vfile.format,
			   'index': vfile.index,
			   'c0bits': vfile.c0bits,
			   'c1bits': vfile.c1bits,
			   'c2bits': vfile.c2bits,
			   'offset': vfile.offset,
			   'scale': MMAttrdefs.getattr(node, 'scale'),
			   'bgcolor': self.getbgcolor(node)}
		if vfile.format == 'compress':
			arminfo['compressheader'] = vfile.compressheader
		try:
			self.threads.arm(vfile.fp, 0, 0, arminfo, None,
				  self.syncarm)
		except RuntimeError, msg:
			if type(msg) is type(self):
				msg = msg.args[0]
			print 'Bad movie file', `url`, msg
			return 1
		return self.syncarm