__version__ = "$Id$"

# Get the prearm size and bandwidth of a node, in bits and bps.
# This module knows which channel types need special treatment.
# XXXX This is a quick-and-dirty solution. We assume that for dynamic
# media we do no preloading, and the whole media file is streamed to us
# at a continuous rate.

import MMAttrdefs
import os
from stat import ST_SIZE
import MMurl
from urlcache import urlcache
import string

Error="Bandwidth.Error"

# These rates are derived from the Real Producer SDK documentation.
# Later we may want to give the user the ability to change the bitrates.
TARGET_BITRATES = [
	20 * 1024,			# 28k8 modem
	34 * 1024,			# 56k modem
	45 * 1024,			# Single ISDN
	80 * 1024,			# Dual ISDN
	220 * 1024,			# Cable modem
	150 * 1024,			# LAN
	]

def get(node, target=0):
	ntype = node.GetType()
	if ntype not in ('ext', 'slide'):
		# Nodes that are not external consume no bandwidth
		return 0, 0
	if ntype == 'slide':
		raise Error, 'Cannot compute bandwidth for slide'
	
	context = node.GetContext()
	ctype = node.GetChannelType()

	if ntype == 'ext' and ctype == 'RealPix':
		# Get information from the attributes
		bitrate = MMAttrdefs.getattr(node, 'bitrate')
		return 0, bitrate
			
	url = MMAttrdefs.getattr(node, 'file')
	url = context.findurl(url)
	val = urlcache[url].get('bandwidth')
	if val is not None:
		return val

	# We skip bandwidth retrieval for nonlocal urls (too expensive)
	type, rest = MMurl.splittype(url)
	if type and type != 'file':
##		print "DBG: Bandwidth.get: skip nonlocal", url
		return None, None
	host, rest = MMurl.splithost(rest)
	if host and host != 'localhost':
##		print "DBG: Bandwidth.get: skip nonlocal", url
		return None, None

	if urlcache[url].has_key('mimetype'):
		maintype, subtype = urlcache[url]['mimetype']
	else:
		try:
			u = MMurl.urlopen(url)
		except IOError:
			raise Error, 'Media item does not exist'
		maintype = u.headers.getmaintype()
		subtype = u.headers.getsubtype()
		urlcache[url]['mimetype'] = maintype, subtype
		u.close()
		del u
	if string.find(subtype, 'real') >= 0:
		# For real channels we parse the header and such
		# XXXX If we want to do real-compatible calculations
		# we have to take preroll time and such into account.
		import realsupport
		info = realsupport.getinfo(url)
		prearm = 0
		bandwidth = 0
		if info.has_key('bitrate'):
			bandwidth = info['bitrate']
##		print "DBG: Bandwidth.get: real:", url, prearm, bandwidth
		urlcache[url]['bandwidth'] = prearm, bandwidth
		return prearm, bandwidth
	if maintype == 'audio' or maintype == 'video':
		targets = MMAttrdefs.getattr(node, 'project_targets')
		bitrate = TARGET_BITRATES[0] # default: 28k8 modem
		for i in range(len(TARGET_BITRATES)):
			if targets & (1 << i):
				bitrate = TARGET_BITRATES[i]
		# don't cache since the result depends on project_targets
		return 0, bitrate

	attrs = {'project_quality':MMAttrdefs.getattr(node, 'project_quality')}
	filesize = GetSize(url, target, attrs, MMAttrdefs.getattr(node, 'project_convert'))
	if filesize is None:
		return None, 0

##	print 'DBG: Bandwidth.get: discrete',filename, filesize, float(filesize)*8
	urlcache[url]['bandwidth'] = float(filesize)*8, 0
	return float(filesize)*8, 0

def GetSize(url, target=0, attrs = {}, convert = 1):
	val = urlcache[url].get('filesize')
	if val is not None:
		return val

	# We skip bandwidth retrieval for nonlocal urls (too expensive)
	type, rest = MMurl.splittype(url)
	if type and type != 'file':
##		print "DBG: Bandwidth.GetSize: skip nonlocal", url
		return None
	host, rest = MMurl.splithost(rest)
	if host and host != 'localhost':
##		print "DBG: Bandwidth.GetSize: skip nonlocal", url
		return None

	# Okay, get the filesize
	try:
		filename, hdrs = MMurl.urlretrieve(url)
	except IOError:
		raise Error, 'Media item does not exist'
	tmp = None
	if target and hdrs.maintype == 'image' and convert:
		import tempfile, realconvert
		tmp = tempfile.mktemp('.jpg')
		dir, file = os.path.split(tmp)
		try:
			cfile = realconvert.convertimagefile(None, url, dir, file, attrs)
		except:
			# XXXX Too many different errors can occur in convertimagefile:
			# I/O errors, image file errors, etc.
			cfile = None
		if cfile: file = cfile
		filename = tmp = os.path.join(dir, file)
	try:
		# XXXX Incorrect for mac (resource fork size)
		statb = os.stat(filename)
	except os.error:
##		print "DBG: Bandwidth.get: nonexisting", filename
		raise Error, 'Media item does not exist'
	if tmp:
		os.unlink(tmp)
	filesize = statb[ST_SIZE]
	urlcache[url]['filesize'] = filesize
	return filesize
