__version__ = "$Id$"

#
# Mac CMIF editor wrapper
#

# First, immedeately disable the console window
import sys
#if len(sys.argv) > 1 and sys.argv[1] == '-v':
#	del sys.argv[1]
#	print '** Verbose **'
#	quietconsole=None
#else:
#	import quietconsole
#	quietconsole.install()
quietconsole=None


ID_SPLASH_DIALOG=513
# XXXX Debugging code: assure the resource file is available
import Res
try:
	Res.GetResource('DLOG', ID_SPLASH_DIALOG)
except:
	Res.OpenResFile(':maccmifed.rsrc')
Res.GetResource('DLOG', ID_SPLASH_DIALOG)

# Next, show the splash screen
import MacOS
MacOS.splash(ID_SPLASH_DIALOG)

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
		CMIFDIR+":editor:mac",
		CMIFDIR+":editor",
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
	fss, ok = macfs.PromptGetFile('CMIF/SMIL file (cancel for URL)', 'TEXT')
	if ok:
		sys.argv = ["macgrins", fss.as_pathname()]
	else:
		import EasyDialogs
		url = EasyDialogs.AskString("CMIF/SMIL URL")
		if url is None:
			sys.exit(0)
		sys.argv = ["maccmifed", url]
		
no_exception=0
try:
	try:
		if profile:
			import profile
			fss, ok = macfs.StandardPutFile("Profile output:")
			if not ok: sys.exit(1)
			profile.run("import grins", fss.as_pathname())
		else:
			import cmifed
		no_exception=1
	except SystemExit:
		no_exception=1
finally:
	if not no_exception:
		if quietconsole:
			quietconsole.revert()
		print 'Type return to exit-',
		sys.stdin.readline()
	
