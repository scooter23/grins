__version__ = "$Id$"

from RealWindowChannel import RealWindowChannel

class RealPixChannel(RealWindowChannel):
	node_attrs = RealWindowChannel.node_attrs + \
		     ['size', 'aspect', 'bitrate', 'maxfps', 'preroll', 'href']

	def getfileurl(self, node):
		if hasattr(node, 'tmpfile'):
			import MMurl, realsupport
			realsupport.writeRP(node.tmpfile, node.slideshow.rp, node)
			return MMurl.pathname2url(node.tmpfile)
		return RealWindowChannel.getfileurl(self, node)
