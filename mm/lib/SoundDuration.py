# Cache info about sound files

# Used to get full info
def getfullinfo(filename):
	import audiofile
	from urllib import urlretrieve
	filename = urlretrieve(filename)[0]
	try:
		a = audiofile.open(filename, 'r')
	except (audiofile.Error, IOError), msg:
		print 'error in sound file', filename, ':', msg
		return f, 1, 0, 1, 8000, 'error', []
	dummy = a.readframes(0)		# sets file pointer to start of data
	if a.getcomptype() != 'NONE':
		print 'cannot read compressed audio files for now', filename
		return f, 1, 0, 1, 8000, 'error', []
	return a.getfp(), a.getnchannels(), a.getnframes(), \
	       a.getsampwidth(), a.getframerate(), 'AIFF', \
	       a.getmarkers()

# Used for compatibility (can't use cache, must open the file)
def getinfo(filename):
	return getfullinfo(filename)[:6]

# Used to get all info except open file
def getallinfo(filename):
	f, nchannels, nsampframes, sampwidth, samprate, format, markers = \
		  getfullinfo(filename)
	f.close()
	if format not in ('AIFF', 'AIFC'):
		raise IOError, (0, 'bad sound file')
	return nchannels, nsampframes, sampwidth, samprate, format, markers

import FileCache
allinfo_cache = FileCache.FileCache(getallinfo)

def get(filename):
	nchannels, nsampframes, sampwidth, samprate, format, markers = \
		  allinfo_cache.get(filename)
	duration = float(nsampframes) / samprate
	return duration

def getmarkers(filename):
	nchannels, nsampframes, sampwidth, samprate, format, markers = \
		  allinfo_cache.get(filename)
	if not markers:
		return []
	xmarkers = []
	invrate = 1.0 / samprate
	for id, pos, name in markers:
		xmarkers.append((id, pos*invrate, name))
	return xmarkers
