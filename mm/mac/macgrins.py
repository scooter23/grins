__version__ = "$Id$"

#
# Mac GRiNS Player wrapper
#

# First, immedeately disable the console window
import sys
if len(sys.argv) > 1 and sys.argv[1] == '-v':
	del sys.argv[1]
	print '** Verbose **'
else:
	import quietconsole
	quietconsole.install()
	
# Next, show the splash screen
import MacOS
MacOS.splash(513)

# Now time for real work.
import os
import string
import macfs

#
# Set variable for standalone cmif:
#
try:
	import MMNode
except ImportError:
	STANDALONE=0
else:
	STANDALONE=1

if not STANDALONE:
	# For now:
	progdir=os.path.split(sys.argv[0])[0]
	CMIFDIR=os.path.split(progdir)[0]
	
	CMIFPATH = [
		CMIFDIR+":mac",
		CMIFDIR+":grins:mac",
		CMIFDIR+":grins",
		CMIFDIR+":common",
		CMIFDIR+":lib",
	# Overrides for Python distribution
		CMIFDIR+":pylib",
		CMIFDIR+":pylib:audio"
	]
	sys.path[0:0] = CMIFPATH
	
	os.environ["CMIF"] = CMIFDIR
	#os.environ["CHANNELDEBUG"] = "1"
	
if len(sys.argv) > 1 and sys.argv[1] == '-p':
	profile = 1
	del sys.argv[1]
	print '** Profile **'
else:
	profile = 0


##import trace
##trace.set_trace()

if len(sys.argv) < 2:
	MacOS.splash()
	fss, ok = macfs.PromptGetFile('SMIL file (cancel for URL)', 'TEXT')
	if ok:
		sys.argv = ["macgrins", fss.as_pathname()]
	else:
		import EasyDialogs
		url = EasyDialogs.AskString("SMIL URL")
		if url is None:
			sys.exit(0)
		sys.argv = ["macgrins", url]
		
	

if profile:
	import profile
	fss, ok = macfs.StandardPutFile("Profile output:")
	if not ok: sys.exit(1)
	profile.run("import main", fss.as_pathname())
else:
	import main
