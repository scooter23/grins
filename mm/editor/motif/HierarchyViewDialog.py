# HierarchyView dialog - Version for standard windowinterface
# XXXX Note: the separation isn't correct: there are still things in HierarchyView
# that really belong here...

from ViewDialog import ViewDialog
import windowinterface
import WMEVENTS
from usercmd import *

class HierarchyViewDialog(ViewDialog):
	adornments = {
		'shortcuts': {'d': DELETE,
			      'x': CUT,
			      'c': COPY,
			      'p': PLAYNODE,
			      'G': PLAYFROM,
			      'i': INFO,
			      'a': ATTRIBUTES,
			      'e': CONTENT,
			      't': ANCHORS,
			      'T': CREATEANCHOR,
			      'L': FINISH_LINK,
			      'f': PUSHFOCUS,
			      'z': ZOOMOUT,
			      '.': ZOOMHERE,
			      'Z': ZOOMIN,
			      },
		'menubar': [
			('Close', [
				('Close', CLOSE_WINDOW),
				]),
			('Edit', [
				('Cut', CUT),
				('Copy', COPY),
				('Paste', [
					('Before', PASTE_BEFORE),
					('After', PASTE_AFTER),
					('Within', PASTE_UNDER),
					]),
				('Delete', DELETE),
				None,
				('New node', [
					('Before', NEW_BEFORE),
					('After', NEW_AFTER),
					('Within', NEW_UNDER),
					None,
					('Seq parent', NEW_SEQ),
					('Par parent', NEW_PAR),
					('Switch parent', NEW_ALT),
					('Choice parent', NEW_CHOICE),
					]),
				]),
			('Play', [
				('Play node', PLAYNODE),
				('Play from node', PLAYFROM),
				None,
				]),
			('Tools', [
				('Info...', INFO),
				('Properties...', ATTRIBUTES),
				('Anchors...', ANCHORS),
				('Edit content...', CONTENT),
				None,
				('Create simple anchor', CREATEANCHOR),
				('Finish hyperlink', FINISH_LINK)
				]),
			('Navigate', [
				('Zoom in', ZOOMIN),
				('Zoom out', ZOOMOUT),
				('Zoom to focus', ZOOMHERE),
				('Level of detail', [
					('More vertical detail', CANVAS_HEIGHT),
					('More horizontal detail', CANVAS_WIDTH),
					('Fit in window', CANVAS_RESET),
					]),
				None,
				('Send focus to other views', PUSHFOCUS),
				(('Show thumbnails', 'Hide thumbnails'),
				 THUMBNAIL, 't'),
				]),
			('Help', [
				('Help...', HELP),
				]),
			],
		'toolbar': None, # no images yet...
		'close': [ CLOSE_WINDOW, ],
		}

	interior_popupmenu = (
		('New node Before', NEW_BEFORE),
		('New node After', NEW_AFTER),
		('New within', NEW_UNDER),
		None,
		('Cut', CUT),
		('Copy', COPY),
		('Delete', DELETE),
		None,
		('Paste Before', PASTE_BEFORE),
		('Paste After', PASTE_AFTER),
		('Paste Within', PASTE_UNDER),
		None,
		('Play node', PLAYNODE),
		('Play from node', PLAYFROM),
		None,
		('Zoom in', ZOOMIN),
		('Zoom out', ZOOMOUT),
		('Zoom to focus', ZOOMHERE),
		None,
		('Info...', INFO),
		('Properties...', ATTRIBUTES),
		('Anchors...', ANCHORS),
		)

	leaf_popupmenu = (
		('New node Before', NEW_BEFORE),
		('New node After', NEW_AFTER),
		None,
		('Cut', CUT),
		('Copy', COPY),
		('Delete', DELETE),
		None,
		('Paste Before', PASTE_BEFORE),
		('Paste After', PASTE_AFTER),
		None,
		('Play node', PLAYNODE),
		('Play from node', PLAYFROM),
		None,
		('Zoom in', ZOOMIN),
		('Zoom out', ZOOMOUT),
		None,
		('Create simple anchor', CREATEANCHOR),
		('Finish hyperlink', FINISH_LINK),
		None,
		('Info...', INFO),
		('Properties...', ATTRIBUTES),
		('Edit content...', CONTENT),
		('Anchors...', ANCHORS),
		)

	def __init__(self):
		ViewDialog.__init__(self, 'hview_')

	# transf from HierarchyView
	def helpcall(self):
		import Help
		Help.givehelp(self.window._hWnd,'Hierarchy_view')

	def show(self):
		if self.is_showing():
			return
		self.toplevel.showstate(self, 1)
		title = 'Structure View (%s)' % self.toplevel.basename
		self.load_geometry()
		x, y, w, h = self.last_geometry
		self.window = windowinterface.newcmwindow(x, y, w, h, title,
				pixmap = 1, adornments = self.adornments,
				canvassize = (w, h),
				commandlist = self.commands)
		self.window.set_toggle(THUMBNAIL, self.thumbnails)
		self.window.register(WMEVENTS.Mouse0Press, self.mouse, None)
		self.window.register(WMEVENTS.ResizeWindow, self.redraw, None)

	def hide(self, *rest):
		self.save_geometry()
		self.window.close()
		self.window = None
		self.displist = None
		self.new_displist = None

	def fixtitle(self):
		if self.is_showing():
			title = 'Structure View (' + self.toplevel.basename + ')'
			self.window.settitle(title)

	def settoggle(self, command, onoff):
		self.window.set_toggle(command, onoff)

	def setcommands(self, commandlist):
		self.window.set_commandlist(commandlist)

	def setpopup(self, template):
		self.window.setpopupmenu(template)
