__version__ = "$Id$"

# Status: all code not run yet. Just written. Bug-free. Yea, right.

# The Interactive class provides a framework for having multiple editable
# objects ('widgets', if you must) on the screen. Event handling, selection,
# drawing and so forth will be done on a per-object basis.
# -mjvdg 13-oct-2000

# ----------------------------------------------------------------------------
# Email sent:
# At 15:37 12/10/2000 +0200, you wrote: This is an idea that I have; I
# just want to see what people think. I've discussed this with Sjoerd so
# far, and I'll probably try to start implementing it (pending
# management approval) after Snap! is ready.

# Basically, every interactive widget on the screen is it's own object
# (unlike the way the Hierarchy view is now...).

# Coupled with this idea is the document/view (or Model/view/controller)
# paradigm where there is a conceptual object being edited by multiple
# views (widgets) - that is, if you select one view, all other views get
# selected. If you edit one view, the changes percolate to all the other
# views as it does at the moment using the Edit manager. If you select
# an object in the structure view, it also gets selected in the timeline
# (channel??) view.

# We can define a window (as in window with title bar, frame etc) to be
# a container for widgets. The widgets have a z-order and event
# management. There is only ever one selected conceptual object, which
# when selected will make all of it's views (widgets) appear to be
# selected.

# When drawing, the window calls, iteratively, the draw() method on each
# of it's widget. If the widget is recursive and holds instances of more
# widgets, then it calls the draw() routine on each of it's children
# recursively. Sjoerd thinks that each object would ideally have it's
# own window (as in, screen real-estate) but I see no reason why it
# cannot just return a display list which it's parent concatenates to
# it's siblings.

# When selected, it sends a message to the object that it is a view of,
# and draws a frame around itself. We could use handles for resizing and
# so forth - this could be discussed more.

# When right-clicked, each object is itself responsible for showing it's
# own context menu, and feeds change requests to it's associated object.


# Using this paradigm, user interface ideas could be implemented a bit
# easier and tidier. The structure view could be composed of many nested
# widgets. The layout view that Alain is working on could consist of
# image widgets with a z-order and resizing handles, so that images
# could be resized; and so forth for the other views available. We could
# have entire widgets glued to the pointer when we drag-and-drop.

# Just an idea... personally I would just like to see simple lighting
# effects on the widgets (it's doable!) - the selected object is always
# brighter than the rest, the distant widgets are progressively dimmer
# and there are vague shadows to distinguish the z-order.

# Following on from this, an inheritance heirachy of widgets would be
# dead useful - the drawing code becomes much simpler. Having a
# different class for the various structure node and media types would
# make the drawing code and click-handling code much cleaner.
# ----------------------------------------------------------------------------

# The scope of this class is limited to drawing, selecting and handling events for
# an object. No "scope specific" or system dependant code will be here.

import windowinterface, WMEVENTS
from AppDefaults import *

# Appendability: (used in Interactive.appended_to_loc to determine where this is appended
# to another Interactive).
LEFT, RIGHT, TOP, BOTTOM, LEFTBOTTOM, RIGHTBOTTOM, LEFTTOP, RIGHTTOP = range(8);

##############################################################################

#                  ABSTRACT BASE CLASS INTERACTIVE

##############################################################################

class Interactive:

    # Functionality:
    # * draw
    # * click, double-click, right-click
    # * select, unselect
    # * move, drag, resize, append (to another Interactive, relative pos)
    # * create, copy, cut, delete
    # * show, hide (why hide???) - discuss further.

    # Positions are either absolute (pixels ~ integers) or relative (floating point 0.0 <= n <= 1.0)
    # and are always tuples of (left, top, right, bottom).
    # At some stage, a better drawing scheme could be developed which prevents drawing out of an
    # Interactive's area and only has relative coordinates, perhaps by having each Interactive in
    # it's own window.

    def __init__(self, root):
        # Root is the Hierarchy view window.
        assert root != None;
        self.root = root;

        # Mutable attributes
        self.pos_rel = (0.0, 0.0, 1.0, 1.0); # relative position (0.0 <= n <= 1.0);
        self.pos_z = 0;                 # Z value - order on screen. 
        self.minsize = (0.0, 0.0);      # Minimum size that this is likely to be.
        self.maxsize = (1.0, 1.0);      # Maximum size that this is likely to be.
        # The relative window size is always (1.0, 1.0, 1.0, 1.0).

        self.selected = 0;              # TRUE or FALSE

        # The next block of functionality will probably never be implemented.
        self.visable = 1;               # TRUE or FALSE, I'm not sure about the usefullness of this..
        self.appended_to = None;        # Object that this will be appended to.
        self.appended_to_loc = None;    # The manner which it is appended to another object.
        self.appended_to_pos = (0.0, 0.0, 0.0, 0,0) # Relative coordinates from the certain position on the appended thingy.
        
        # pseudo-immutable attributes
        self.clickable = 1;             # whether this will accept events
        self.movable = 1;               # whether this can be moved or resized.
        self.drag_dropable = 1;         # whether this does the D&D thing.
        self.context_menu = None;       # Pops up when right-clicked.

        self.parent = None;             # Sometimes nodes have parents.

    def draw(self, displist):
        # For the base Interactive, nothing will be drawn.
        self.recalc();

        if self.pos_rel == (0,0,0,0):
            print "Warning! Interactive drawn with null coords.";
            return 0;

        l, t, r, b = self.pos_rel;
        width = r-l;
        height = b-t;

        # Check that this widget is on the screen.
        if l<0.0 or t<0.0 or r>1.0 or b>1.0:
            print "Warning! Widget drawn off window.";
            return 0;

        print "DEBUG: drawing a grey box.";
        # DEBUG: draw a grey, outlined box.
        print l, t, width, height
        if self.selected:
            displist.drawfbox(BGCOLOR, (l, t, width, height) );
        else:
            displist.drawfbox(LEAFCOLOR, (l, t, width, height) );
        displist.drawbox((l, t, width, height));
        return 1;
    
    def recalc(self):
        # Calculate the position if this is relative to another widget.
        pass;

    def highlight(self, color):
        # Make the color a bit brighter
        # This could be used to highlight a selected node.
        # TODO: should this be a global function?
        r, g, b = color
        return min(float(r)*1.25, 255), min(float(g)*1.25, 255), min(float(b)*1.25, 255);

    def dim_to_z_index(self):
        # Adjust the color depending on the distance from the user
        # and the maximum z-index used.
        assert 0;

    def get_pos_abs(self):
        x, y = self.root.get_window_size_abs();
        lr, tr, rr, br = self.pos_rel;
        l = float(lr) * x;
        t = float(tr) * y;
        r = float(rr) * x;
        b = float(br) * y;
        return (l,t,r,b);

    def click(self, pos):
        self.select();

    def double_click(self, pos):
        print "TODO: Interactive.double_click()";

    def right_click(self, pos):
        print "TODO: Interactive.right_click()";

    def moveto(self, newpos):
        # Also handles resizing - new size is in newpos as well.
        l,t,r,b = newpos;
#        print "DEBUG: moveto Received sizes: ", l, t, r, b
#        print "DEBUG: moveto self.get_minsize is: ", self.get_minsize();
#        print "DEBUG: moveto self.get_maxsize is: ", self.get_maxsize();

# TODO: put this back.
#        lw, lh = self.get_minsize();
#        mw, mh = self.get_maxsize();
#        assert (r-l) > lw and (b-t) > lh;
#        assert (r-l) < mw and (b-t) < mh;

        if r < l:
            print "Interactive: Error: box is right-to-left";
        if t > b:
            print "Interactive: Error: box is upside down.";

        assert r <= 1.0 and r >= 0.0 and l <= 1.0 and l >= 0.0
        assert t >= 0.0 and t <= 1.0 and b >= 0.0 and b <= 1.0;
        self.pos_rel = newpos;

    def set_append(self, otherobject, position):
        # Used to make the position of this object relative to another.
        # Warning! Don't start doing traversals using this!
        # Make a container that inherits from EditWindow instead.
        print "TODO: Interactive.append()";

    def select(self):
        self.selected = 1;
        self.root.redraw();

    def unselect(self):
        self.selected = 0;
        self.root.redraw();

    def get_minsize(self):
        # Return the least size that this widget is likely to be.
        return self.minsize;

    def get_maxsize(self):
        # Return the maximum size that this widget is likely to be. 
        return self.maxsize;

    # TODO: def deepcopy?? And other methods here.

    def get_box(self):
        l,t,r,b = self.pos_rel;
        return l,t,r-l,b-t;

    def get_relx(self, xvalue):
        return float(xvalue)/ self.root.get_window_size_abs()[0];

    def get_rely(self, yvalue):
        return float(yvalue) / self.root.get_window_size_abs()[1];

    def is_hit(self, (x, y)):
        l,t,r,b = self.pos_rel;
        if l < x <= r and t < y < b:
            return 1;
        else:
            return 0;

##############################################################################

#                    ABSTRACT BASE CLASS EDITWINDOW

##############################################################################
    
class EditWindow(Interactive):
    # An EditWindow is a container for Interactive objects.
    # This is a nestable container, so you can add and remove objects from it.

    # This object behaves like a collection - you can add and remove Interactives from
    # it. 

    def __init__(self, root):
        Interactive.__init__(self, root);
        self.widgets = [];
        
    def draw(self, displist):
        # Draw widgets, starting with the furthest (z-index = 0)
        for i in self.widgets:
            i.draw(displist);            

    def click(self, pos):
        # Find the closest widget (z-index is greatest)
        # if it is one of my sub-children:
        for i in range(len(self.widgets)-1, -1, -1):
            if self.widgets[i].is_hit(pos):
                self.widgets[i].click(pos)
                return
        # else: 
        self.select();
        

    def double_click(self, pos):
        # Find the closest widget (z-index is greatest)
        for i in range(len(self.widgets)-1, -1, -1):
            if self.widgets[i].is_hit(pos):
                self.widgets[i].double_click(pos)
                return

    def right_click(self, pos):
        # Find the closest widget (z-index is greatest)
        for i in range(len(self.widgets)-1, -1, -1):
            if self.widgets[i].is_hit(pos):
                self.widgets[i].right_click(pos)
                return

    ## List handling functions
    
    def __len__(self):
        return len(self.widgets);

    def __getitem__(self, key):
        return self.widgets[key];

    def __setitem__(self, key, value):
        self.insert(value);

    def __delitem__(self, key): # incorrect arguments
        del self.widgets[key];

    def __add__(self):                  # incorrect arguments.
        assert 0; # not useful.

    def append(self, node):
        assert isinstance(node, Interactive);
        node.parent = self;
        node.pos_z = self.pos_z + 1;
        self.insert(node);

    def count(self):
        assert 0; # not useful.


    ## Maintaining the z-index:

    def insert(self, intact):
        # Keep the Interactives ordered by z-index.
        # intact is the Interactive widget to insert by z-index.
        self.widgets.append(intact);
        self.resort();

    # alternatively (untested):
#     def insert(self, intact):
#         element = 0;
#         for i in range(len(self.widgets)):
#             if self.widgets[i].pos_z = intact.pos_z:
#                 element = i;
#                 break;
#         head = self.widgets[:i];
#         tail = self.widgets[i:];
#         self.widgets = head + intact + tail;

    def resort(self):
        # Ensure that the list is sorted by z-index.
        # Using the python built-in sort function..
        # Sjoerd reckons this is faster..
        tuple_list = [];
        for i in self.widgets:
            tuple_list.append((i.pos_z, i));
        tuple_list.sort();
        
        new_widgetlist = [];
        for k,v in tuple_list:
            new_widgetlist.append(v);

        self.widgets = new_widgetlist;
    
#    def get_minsize(self):
#        # The minimum size of a container is the sum of all of it's children.
#        print "TODO";

#    def get_maxsize(self):
#        # the maximum size of a container is the sum of all of it's children.
 #       print "TODO";
