import grins_app_core
resdll = None
embedded = 0

class PlayerApp(grins_app_core.GrinsApp):
	def BootGrins(self):
		import exec_cmif
		exec_cmif.Boot(0)

try:
	import grinspapi
except ImportError:
	grinspapi = None

runApp = 1

if grinspapi:
	import sys
	grinspapi.OleInitialize()
	for i in range(1, len(sys.argv)):
		arg = sys.argv[i]
		if arg[:1]=='/' or arg[:1]=='-':
			val = arg[1:]
			if val == 'UnregServer':
				grinspapi.UnregisterServer()
				runApp = 0
			elif val == 'RegServer':
				grinspapi.RegisterServer()
				runApp = 0
			elif val == 'Embedding':
				sys.argv = sys.argv[:1]
				global embedded
				embedded = 1
				runApp = 1

if not runApp:
	grinspapi.OleUninitialize()
else:
	if not embedded and grinspapi:
		grinspapi.commodule.Lock()
	grins_app_core.fix_argv()
	grins_app_core.BootApplication(PlayerApp)

