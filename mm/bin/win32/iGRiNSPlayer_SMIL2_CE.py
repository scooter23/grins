# Win32 CMIF script to run cmif applications interactively
# Executed from "Pythonwin.exe"
# cmd: Pythonwin /run iGRiNS.py

[PLAYER,EDITOR,SUBSYSTEM]=range(3)


##################### Settings

WHAT=PLAYER  # <-- What to run
what=WHAT

# if WHAT is SUBSYSTEM specify subsystemModuleName
subsystemModuleName='dslab'


# Global Application Object
toplevel=None

##################### Main Script
import os
import sys
	
CMIFDIR=r'\cmif'

# TEMP TEST FOLDER

if what==PLAYER:
	specificPath = "grins"
	os.environ['GRiNSApp']='GRiNS'
else:
	specificPath = "editor"
	os.environ['GRiNSApp']='GRiNSed'


CMIFPATH = [
	os.path.join(CMIFDIR, 'bin\\win32'),
	os.path.join(CMIFDIR, '%s\\smil20\\win32' % specificPath),
	os.path.join(CMIFDIR, '%s\\smil20' % specificPath),
	os.path.join(CMIFDIR, '%s\\win32' % specificPath),
##	os.path.join(CMIFDIR, 'mmextensions\\real\\win32'),
	os.path.join(CMIFDIR, 'common\\win32'),
	os.path.join(CMIFDIR, 'lib\\win32'),
	os.path.join(CMIFDIR, '%s' % specificPath),
	os.path.join(CMIFDIR, 'common'),
	os.path.join(CMIFDIR, 'lib'),
	os.path.join(CMIFDIR, 'pylib'),
##	os.path.join(CMIFDIR, 'pylib\\audio'),
	os.path.join(CMIFDIR, 'win32\\src\\Build'),
	os.path.join(os.path.split(CMIFDIR)[0], 'python\\Lib')
]
sys.path[0:0] = CMIFPATH

os.environ["CMIF"] = CMIFDIR
os.environ["CMIF_USE_WIN32"] = "ON"
if not os.environ.has_key('HOME'):
	os.environ['HOME']=CMIFDIR

# Turn pathnames into their full NT version
import longpath
for i in range(1, len(sys.argv)):
	if os.path.exists(sys.argv[i]):
		sys.argv[i] = longpath.short2longpath(sys.argv[i])

import string
import win32api
from win32con import *
import win32ui
import traceback

from version import registryname, registrykey
win32ui.SetAppName(registryname)
win32ui.SetRegistryKey(registrykey)

def SafeCallbackCaller(fn, args):
	try:
		return apply(fn, args)
	except SystemExit, rc:
		# We trap a system exit, and translate it to the "official" way to bring down a GUI.
		try:
			rc = int(rc[0])
		except (ValueError, TypeError):
			rc = 0
		# use afx to unload com/ole lib
		#(win32ui.GetAfx()).PostQuitMessage(rc)
		win32ui.GetMainFrame().PostMessage(WM_CLOSE)
	except:
		# We trap all other errors, ensure the main window is shown, then
		# print the traceback.
		try:
			win32ui.GetMainFrame().ShowWindow(SW_SHOW)
		except win32ui.error:
			print "Cant show the main frame!"
		traceback.print_exc()
		return


win32ui.InstallCallbackCaller(SafeCallbackCaller)

def Boot(what = 0):
	# Locate the GRiNSRes.dll file.  This is presumably in the same directory as
	# the extensionmodules, or if frozen, in the main directory
	# This call allows Pythonwin to automatically find resources in it.
	import win32ui
	dllPath = os.path.split(win32ui.__file__)[0]
	try:
		global resdll
		resdll = win32ui.LoadLibrary(os.path.join(dllPath, "GRiNSRes.dll"))
		resdll.AttachToMFC()
	except win32ui.error:
		win32ui.MessageBox("The application resource DLL 'GRiNSRes.dll' can not be located\r\n\r\nPlease correct this problem, and restart the application")
		# For now just continue!?!?!
	# run the given cmif file
	try:
		if what==PLAYER:
			import grins
		elif what==SUBSYSTEM:
			exec 'import %s\n' % subsystemModuleName
		else:
			import cmifed
	except SystemExit, rc:
		win32ui.GetMainFrame().PostMessage(WM_CLOSE)


def GuessCMIFRoot():
	selfDir = win32api.GetFullPathName(os.path.join(os.path.split(sys.argv[0])[0], "." ))
	l=string.split(selfDir,'\\')
	found=0;dir=''
	for s in l:
		dir=dir+s
		if s=='cmif':
			found=1
			break
		dir=dir+'\\'
	if found:return dir
	return r'd:\ufs\mm\cmif'

Boot(WHAT)