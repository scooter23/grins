__version__ = "$Id$"

#
# Mac CMIF editor wrapper
#

# First, immedeately disable the console window
import sys
DEBUG=1
if DEBUG:
	print '** Verbose **'
	quietconsole=None
elif len(sys.argv) > 1 and sys.argv[1] == '-v':
	del sys.argv[1]
	print '** Verbose **'
	quietconsole=None
else:
	import quietconsole
	quietconsole.install()

ID_SPLASH_DIALOG=513
# XXXX Debugging code: assure the resource file is available
import Res
try:
	Res.GetResource('DLOG', ID_SPLASH_DIALOG)
except:
	Res.OpenResFile(':maccmifed.rsrc')
Res.GetResource('DLOG', ID_SPLASH_DIALOG)

# Next, show the splash screen
import splash
splash.splash('loadprog')

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
	
#
# Mangle sys.path. Here are the directives for macfreeze:
#
# macfreeze: path :
# macfreeze: path ::editor:mac
# macfreeze: path ::editor
# macfreeze: path ::common
# macfreeze: path ::lib:mac
# macfreeze: path ::lib
# macfreeze: path ::pylib
# macfreeze: path ::pylib:audio
#
# and some modules we don't want:
# macfreeze: exclude X_window
# macfreeze: exclude X_windowbase
# macfreeze: exclude GL_window
# macfreeze: exclude GL_windowbase
# macfreeze: exclude WIN32_window
# macfreeze: exclude WIN32_windowbase
# macfreeze: exclude fastimp
# macfreeze: exclude fm
# macfreeze: exclude gl
# macfreeze: exclude Xlib
# macfreeze: exclude Xt
# macfreeze: exclude Xm
# macfreeze: exclude Xtdefs
# macfreeze: exclude glXconst
# macfreeze: exclude mv
# macfreeze: exclude SOCKS
# macfreeze: exclude signal
# macfreeze: exclude mm
# macfreeze: exclude thread
# macfreeze: exclude SUNAUDIODEV
# macfreeze: exclude Xcursorfont
# macfreeze: exclude FCNTL
# macfreeze: exclude sunaudiodev
# macfreeze: exclude X
# macfreeze: exclude newdir
# macfreeze: exclude glX
# macfreeze: exclude dummy_window
# macfreeze: exclude mpegex
# macfreeze: exclude al
# macfreeze: exclude imageex
# macfreeze: exclude Xmd
# macfreeze: exclude VFile
# macfreeze: exclude NTVideoDuration
# macfreeze: exclude MpegDuration
# macfreeze: exclude fcntl
# macfreeze: exclude MovieChannel
# macfreeze: exclude MpegChannel
# macfreeze: exclude MidiChannel
# macfreeze: exclude VcrChannel
# macfreeze: exclude NTVideoChannel
# macfreeze: exclude MPEGVideoChannel
# macfreeze: exclude audiohcom
# macfreeze: exclude audio8svx
# macfreeze: exclude audiosdnr
# macfreeze: exclude audiosndt
# macfreeze: exclude audiosndr
# macfreeze: exclude audiovoc
# macfreeze: exclude imgpng


#
# And here's the code for non-standalone version of the editor:

if not STANDALONE:
	# For now:
	progdir=os.path.split(sys.argv[0])[0]
	CMIFDIR=os.path.split(progdir)[0]
	
	CMIFPATH = [
		CMIFDIR+":mac",
		CMIFDIR+":editor:mac",
		CMIFDIR+":editor",
		CMIFDIR+":common",
		CMIFDIR+":lib:mac",
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

##if len(sys.argv) < 2:
##	MacOS.splash()
##	fss, ok = macfs.PromptGetFile('CMIF/SMIL file (cancel for URL)', 'TEXT')
##	if ok:
##		sys.argv = ["macgrins", fss.as_pathname()]
##	else:
##		import EasyDialogs
##		url = EasyDialogs.AskString("CMIF/SMIL URL")
##		if url is None:
##			sys.exit(0)
##		sys.argv = ["maccmifed", url]
		
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
##		if DEBUG:
##			import pdb
##			pdb.post_mortem(sys.exc_info()[2])
##		elif quietconsole:
##			quietconsole.revert()
##			print 'Type return to exit-',
##			sys.stdin.readline()
	
