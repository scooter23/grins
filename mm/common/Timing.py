# Interface to calculate the timing of a (sub)tree

import sched
import MMAttrdefs
from MMExc import *
from MMNode import alltypes, leaftypes, interiortypes
from HDTL import HD, TL


# Subroutine to check whether a node is a mini-document.
# This is true if either it is the root or its parent is a bag node.
# XXX Shouldn't this be defined as a node method?

def isminidoc(node):
	parent = node.GetParent()
	return parent == None or parent.GetType() == 'bag'


# The routine 'changedtimes' signifies that the timing might have changed
# (but is not needed at the moment), and the routine 'needtimes' signifies
# that somebody needs correct timing (possibly resulting in a recalc).
# Finally, 'do_times' does the actual calculation.
# As an option, 'hastimes' can be used to check whether the timings
# are correct (this is used to set the 'calculate times' button).

def changedtimes(node):
	try:
		del node.initial_arms
	except (KeyError, AttributeError): # initial_arms does not exist
		pass
	if node.GetType() == 'bag':
		for child in node.GetChildren():
			changedtimes(child)

def hastimes(node):
	try:
		if node.initial_arms <> None:
			return 1
	except AttributeError: # initial_arms does not exist
		pass
	return 0

def needtimes(node):
	try:
		if node.initial_arms <> None:
			return # The cached value is valid
	except AttributeError: # initial_arms does not exist
		pass
	do_times(node)


# Calculate the nominal times for each node in the given subtree.
# When the function is done, each node has two instance variables
# 't0' and 't1' that give the begin and end time of the node.
# By definition, 't0' for the given root is zero; its 't1' value
# gives the total duration.
#
# This takes sync arcs within the subtree into account, but ignores
# sync arcs with one end outside the given subtree.
#
# Any circularities in the sync arcs are detected and "reported"
# as exceptions.

def do_times(node):
	import time
	t0 = time.millitimer()
	print 'do_times...'
	
	# These globals are used only while in do_times();
	# they are changed by decrememt()
	
	global getd_times # Used to calculate time spent in getduration()
	getd_times = 0
	
	global last_node # Keeps track of the last node played per channel
	last_node = {}
	
	global initial_arms # Keeps track of the first node played per channel
	initial_arms = []

	node.t1 = 0
	del node.t1
	
	prepare(node)
	_do_times_work(node)
	try:
		void = node.t1
	except AttributeError:
		import fl
		fl.show_message('WARNING: circular timing dependencies.', \
			  '(ignoring sync arcs and trying again)', '')
		prep1(node)
		_do_times_work(node)
	t1 = time.millitimer()
	propdown(node, node.t1)
	t2 = time.millitimer()

	node.initial_arms = initial_arms

	print 'done in', (t2-t0) * 0.001, 'sec.'
	print '(of which', getd_times*0.001, 'sec. in getduration()',
	print 'and', (t2-t1)*0.001, 'sec. in propdown)'

def _do_times_work(node):
	pt = pseudotime().init(0.0)
	q = sched.scheduler().init(pt.timefunc, pt.delayfunc)
	node.counter[HD] = 1
	decrement(q, (0, node, HD))
	q.run()

# Interface to get the "initial arms" nodes of a tree.
# Call only after needtimes has calculated them.

def getinitial(node):
	return node.initial_arms # AttributeError here if called at wrong time


# Interface to the prep1() and prep2() functions; these are also used
# by the player (which uses a different version of decrement()).
# This adds instance variables 'counter' and 'deps' to each node,
# with meanings that can be deduced from the code below. :-) :-) :-)
#
def prepare(node):
	import time
	print '\tprepare...'
	t0 = time.millitimer()
	prep1(node)
	t1 = time.millitimer()
	prep2(node, node)
	t2 = time.millitimer()
	print '\tdone in', (t1-t0) * 0.001, '+', (t2-t1) * 0.001,
	print '=', (t2-t0) * 0.001, 'sec'
	if node.counter[HD] <> 0:
		raise CheckError, 'head of node has dependencies!?!'


# Interface to clean up the mess left behind by prepare().
#
# Calling this can never really hurt,
# ***however***, if you repeatedly call changedtimes(),
# it is faster not to call cleanup() in between!
#
# It does *not* remove t0 and t1, by the way...
#
def cleanup(node):
	node.counter = node.deps = None
	del node.counter
	del node.deps
	type = node.GetType()
	if type in interiortypes:
		for c in node.GetChildren():
			cleanup(c)


# Return a node's nominal duration, in seconds, as a floating point value.
# Should only be applied to leaf nodes.
#
def getduration(node):
	if node.GetType() in interiortypes:
		raise CheckError, 'Timing.getduration() on non-leaf'
	from ChannelMap import channelmap
	try:
		cname = MMAttrdefs.getattr(node, 'channel')
		cattrs = node.context.channeldict[cname]
		ctype = cattrs['type']
		cclass = channelmap[ctype]
	except: # XXX be more specific!
		# Fallback if the channel doesn't exists, etc.
		return MMAttrdefs.getattr(node, 'duration')
	# Get here only if the 'try' succeeded
	instance = cclass()		# XXX Not initialized!
					# Walking on thin ice here...
	return instance.getduration(node)


###########################################################
# The rest of the routines here are for internal use only #
###########################################################


def prep1(node):
	node.counter = [0, 0]
	node.deps = [], []
	type = node.GetType()
	if type in ('seq', 'bag'): # XXX not right!
		xnode, xside = node, HD
		for c in node.GetChildren():
			prep1(c)
			adddep(xnode, xside, 0, c, HD)
			xnode, xside = c, TL
		adddep(xnode, xside, 0, node, TL)
	elif type == 'par':
		for c in node.GetChildren():
			prep1(c)
			adddep(node, HD, 0, c, HD)
			adddep(c, TL, 0, node, TL)
		# Make sure there is *some* path from head to tail
		adddep(node, HD, 0, node, TL)
	else:
		# Special case -- delay -1 means execute leaf node
		# of leaf node when playing
		try:
			del node.prearm_event
		except:
			pass
		adddep(node, HD, -1, node, TL)


def prep2(node, root):
	if not node.GetSummary('synctolist'): return
	arcs = MMAttrdefs.getattr(node, 'synctolist')
	for arc in arcs:
		xuid, xside, delay, yside = arc
		xnode = node.MapUID(xuid)
		if root.IsAncestorOf(xnode):
			adddep(xnode, xside, delay, node, yside)
	#
	if node.GetType() in interiortypes:
		for c in node.GetChildren(): prep2(c, root)


# propdown - propagate timing down the tree again
def propdown(node, stoptime):
	tp = node.GetType()
	if not node.t0t1_inherited:
		stoptime = node.t1
	if tp == 'par':
		for c in node.GetChildren():
			propdown(c, stoptime)
	elif tp in ('seq', 'bag'): # XXX not right!
		children = node.GetChildren()
		if not children:
			return
		lastchild = children[-1]
		children = children[:-1]
		for c in children:
			propdown(c, c.t1)
		propdown(lastchild, stoptime)
	elif node.t0t1_inherited:
		node.t1 = stoptime


def adddep(xnode, xside, delay, ynode, yside):
	ynode.counter[yside] = ynode.counter[yside] + 1
	if delay >= 0:
		xnode.deps[xside].append(delay, ynode, yside)


def decrement(q, (delay, node, side)):
	if delay > 0:
		id = q.enter(delay, 0, decrement, (q, (0, node, side)))
		return
	x = node.counter[side] - 1
	node.counter[side] = x
	if x > 0:
		return
	if x < 0:
		raise CheckError, 'counter below zero!?!?'
	if side == HD:
		node.t0 = q.timefunc()
	elif side == TL:
		node.t1 = q.timefunc()
	node.node_to_arm = None
	if node.GetType() in interiortypes:
		node.t0t1_inherited = 1
	elif side == HD:
		import time
		t0 = time.millitimer()
		dt = getduration(node)
		node.t0t1_inherited = (dt == 0 and len(node.deps[TL]) <= 1)
			# Don't mess if it has timing deps
		t1 = time.millitimer()
		global getd_times
		getd_times = getd_times + (t1-t0)
		id = q.enter(dt, 0, decrement, (q, (0, node, TL)))
		cname = None
		try:
			cname = MMAttrdefs.getattr(node, 'channel')
		except NoSuchAttrError:
			cname = None
		if cname <> None:
			if node.GetRawAttrDef('arm_duration', -1) >= 0:
				if last_node.has_key(cname):
					ln = last_node[cname]
					ln.node_to_arm = node
				else:
					global initial_arms
					initial_arms.append(node)
			last_node[cname] = node
	for arg in node.deps[side]:
		decrement(q, arg)


class pseudotime:
	def init(self, t):
		self.t = t
		return self
	def timefunc(self):
		return self.t
	def delayfunc(self, delay):
		self.t = self.t + delay
