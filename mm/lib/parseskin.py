__version__ = "$Id$"

error = 'parseskin.error'

# The syntax for a GRiNS skin description file is very simple:
#
# Comments start with the character # and extend to the end of the
# line; empty lines are ignored.
#
# Lines consist of a keyword and parameters, separated from each other
# by white space.  The available keywords and their parameters are:
#
# "image"	URL of image file (relative to skin definition file)
# "display"	4 numbers giving x, y, width, height
# "key"		key shape coordinates
# command	shape coordinates
# component	URI
# profile	profile name
# SmilBaseSet	"SMIL-3GPP-R4" or "SMIL-3GPP-R5"
# SmilModules	list of SMIL module names
#
# The key is a single, possibly quoted, character.  If either ", ', or
# a space character needs to be specified, it must be surrounded with
# quotes, otherwise quotes are optional.  Use ' to quote " and v.v.
# Some special characters can also be specified: Use \t for TAB, \r
# for ENTER, \b for BACKSPACE, and \n for LINEFEED.
#
# The possible commands are:
# "open", "play", "pause", "stop", "exit", "tab".
#
# The possible shapes and coordinates are:
# "rect" with 4 numbers giving x, y, width, and height;
# "circle" with 3 numbers giving x, y, and radius;
# "poly" with an even number of numbers, each pair describing the x
# and y coordinates of a point.
#
# A special shape is "rocker".  The possible 'coordinates' for the
# "rocker" shape are "left", "right", "up", "down", "center".
#
# The component command may be repeated and all components are
# returned as a single list
#
# The profile can be one of (without the quotes):
#	"SMIL 2.0 Language Profile" (default)
#	"3GPP PSS5 Profile"
#	"3GPP PSS4 Profile"
#	"SMIL 2.0 Basic Language Profile"
#	"SMIL MMS Profile"
#
# In addition to the above commands, you can also have lines to set
# system attributes.  These lines are single Python assignments and
# start with "system_".  E.g.
#	system_bitrate = 33600
#
# Example skin definition file:
#	image Classic.gif
#	display 0 0 240 268
#	play rect 12 272 18 18			# Play Icon
#	pause rect 32 272 18 18			# Pause Icon
#	stop rect 54 272 18 18			# Stop
#	exit rect 143 275 18 18			# Exit Button
#	open rect 86 272 18 18			# Open File Button
#	skin rect 110 272 18 18
#	tab rocker right			# right side of rocker panel
#	activate rocker center			# center of rocker panel
#	profile 3GPP PSS5 Profile		# use 3GPP PSS5 profile

import string				# for whitespace
import re
import settings

# we cheat: we're not nearly so fuzzy as we claim to be
mms = re.compile(r'\bmms\b', re.IGNORECASE)
pss4 = re.compile(r'\bpss4\b', re.IGNORECASE)
pss5 = re.compile(r'\bpss4\b', re.IGNORECASE)
basic = re.compile(r'\bbasic\b', re.IGNORECASE)

def parsegskin(file):
	dict = {}
	lineno = 0
	profile = settings.SMIL_20_MODULES
	modules = []
	prefs = {}
	while 1:
		line = file.readline()
		if not line:
			break
		lineno = lineno + 1

		# ignore comments and empty lines
		# and strip off white space
		i = line.find('#')
		if i >= 0:
			line = line[:i]
		line = line.strip()
		if not line:
			continue

		if line[:7] == 'system_':
			exec(line, prefs)
			continue

		# first part is GRiNS command
		line = line.split(None, 1)
		if len(line) == 1:
			raise error, 'syntax error in skin on line %d' % lineno
		cmd, rest = line
		if cmd =='image':
			if dict.has_key(cmd):
				# only one image allowed
				raise error, 'syntax error in skin on line %d' % lineno
			dict[cmd] = rest.strip()
			continue
		if cmd == 'component':
			v = rest.strip()
			if dict.has_key('component'):
				dict['component'].append(v)
			else:
				dict['component'] = [v]
			continue
		if cmd == 'profile':
			if mms.search(rest) is not None:
				profile = settings.SMIL_MMS_MODULES
			elif pss4.search(rest) is not None:
				profile = settings.SMIL_PSS4_MODULES
			elif pss5.search(rest) is not None:
				profile = settings.SMIL_PSS5_MODULES
			elif basic.search(rest) is not None:
				profile = settings.SMIL_BASIC_MODULES
			else:
				profile = settings.SMIL_20_MODULES
			continue
		if cmd == 'SmilBaseSet':
			if rest == 'SMIL-3GPP-R4':
				profile = settings.SMIL_PSS4_MODULES
			elif rest == 'SMIL-3GPP-R5':
				profile = settings.SMIL_PSS5_MODULES
			continue
		if cmd == 'SmilModules':
			modules.extend(rest.split())
			continue
		if cmd == 'key':
			quote = None
			backslash = 0
			key = None
			rest = list(rest) # easier to manipiulate list
			while rest:
				c = rest[0]
				del rest[0]
				if quote is not None:
					if c == quote:
						quote = None
					elif backslash:
						if key is None:
							if c == '\\':
								key = '\\'
							elif c == 'r':
								key = '\r'
							elif c == 't':
								key = '\t'
							elif c == 'n':
								key = '\n'
							elif c == 'b':
								key = '\b'
							else:
								key = c
						else:
							raise error, 'syntax error in skin on line %d: only single character allowed for key' % lineno
						backslash = 0
					elif c == '\\':
						backslash = 1
					elif key is None:
						key = c
					else:
						raise error, 'syntax error in skin on line %d: only single character allowed for key' % lineno
				elif c == '"' or c == "'":
					quote = c
				elif c in string.whitespace:
					if key is not None:
						break
				elif backslash:
					if key is None:
						if c == '\\':
							key = '\\'
						elif c == 'r':
							key = '\r'
						elif c == 't':
							key = '\t'
						elif c == 'n':
							key = '\n'
						elif c == 'b':
							key = '\b'
						else:
							key = c
					else:
						raise error, 'syntax error in skin on line %d: only single character allowed for key' % lineno
					backslash = 0
				elif c == '\\':
					backslash = 1
				elif key is None:
					key = c
				else:
					raise error, 'syntax error in skin on line %d: only single character allowed for key' % lineno
			if key is None:
				raise error, 'syntax error in skin on line %d: no key specified' % lineno
			rest = ''.join(rest) # reassemble string
		coords = rest.split()
		if cmd == 'display':
			# display area is always rectangular
			shape = 'rect'
		else:
			shape = coords[0]
			del coords[0]
		if shape == 'rocker':
			if len(coords) != 1:
				raise error, 'syntas error in skin on line %d' % lineno
			coords = coords[0]
			if coords == 'centre': # undocumented alternative spelling
				coords = 'center'
			if coords not in ('left','right','up','down','center'):
				raise error, 'syntas error in skin on line %d' % lineno
		else:
			try:
				coords = map(lambda v: int(v, 0), coords)
			except ValueError:
				raise error, 'syntax error in skin on line %d' % lineno
			if shape == 'poly' and coords[:2] == coords[-2:]:
				del coords[-2:]
			if (shape != 'rect' or len(coords) != 4) and \
			   (shape != 'circle' or len(coords) != 3) and \
			   (shape != 'poly' or len(coords) < 6 or len(coords) % 2 != 0):
				raise error, 'syntax error in skin on line %d' % lineno
		if cmd == 'display':
			if dict.has_key(cmd):
				# only one display allowed
				raise error, 'syntax error in skin on line %d' % lineno
			dict[cmd] = shape, coords
		elif cmd == 'key':
			if dict.has_key(cmd):
				dict[cmd].append((shape, coords, key))
			else:
				dict[cmd] = [(shape, coords, key)]
		else:
			if dict.has_key(cmd):
				dict[cmd].append((shape, coords))
			else:
				dict[cmd] = [(shape, coords)]
	if dict.has_key('image') and not dict.has_key('display'):
		raise error, 'display region missing from skin description file'
	settings.switch_profile(profile + modules)
	for key, val in prefs.items():
		if key[:1] != '_':
			settings.set(key, val)
	return dict
