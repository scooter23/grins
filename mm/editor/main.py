# Main program for the CMIF editor

import sys
import getopt
import os

def main():
	playnow = 0
	stats = 0
	#
	opts, args = getopt.getopt(sys.argv[1:], 'psnh:')
	#
	if args:
		if len(args) > 1:
			sys.stderr.write('Warning: only one filename used\n')
		filename = args[0]
	else:
		filename = 'demo.cmif'
	#
	try:
		# Make sure the file exists first...
		f = open(filename, 'r')
		f.close()
	except IOError:
		sys.stderr.write(filename + ': cannot open\n')
		sys.exit(2)
	#
	# patch the module search path
	# so we are less dependent on where we are called
	#
	if os.environ.has_key('CMIF'):
		CMIF = os.environ['CMIF']
	else:
		CMIF = '/ufs/guido/mm/demo'
	sys.path.append(os.join(CMIF, 'mm4'))
	sys.path.append(os.join(CMIF, 'lib'))
	#
	import MMExc
	import TopLevel
	import SoundChannel
	import Channel
	#
	for opt, arg in opts:
		if opt == '-p':
			playnow = 1
		elif opt == '-s':
			stats = 1
		elif opt == '-n':
			Channel.disable_prearm()
		elif opt == '-h':
			TopLevel.sethelpdir(arg)
	#
	top = TopLevel.TopLevel().init(filename)
	#
	top.show()
	#
	try:
		try:
			if playnow:
				top.player.playsubtree(top.root)
			top.run()
			top.destroy()
		except KeyboardInterrupt:
			print 'Interrupt.'
	finally:
		try:
			SoundChannel.restore()
		finally:
			pass
		#
		if stats:
			import MMNode
			MMNode._prstats()

main()
