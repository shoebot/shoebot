### CREDITS ##########################################################################################

# Copyright (c) 2007 Tom De Smedt.
# See LICENSE.txt for details.

__author__    = "Tom De Smedt"
__version__   = "1.9.1"
__copyright__ = "Copyright (c) 2007 Tom De Smedt"
__license__   = "MIT"

### NODEBOX BEZIER PATH EDITOR #######################################################################

# The NodeBox Bezier path editor offers an interactive way to construct paths in NodeBox.
# Some things are better done with the mouse than with code and creating smooth paths just the way
# you want is one of them. This straightforward editor allows you to create paths by adding and
# moving path points, dragging handles, drawing in freehand and organising points on a grid.
#
# Controls:
#
# 1) Pressing the mouse anywhere on the canvas adds a new point to the path. 
#    You can instantly drag its control handle to create a curve.
#    Clicking on the path inserts a point.
# 2) Select a point by clicking on it. You can drag its control handles, move the point
#    and delete it by clicking the button with a cross.
# 3) The last point in the path has an extra pause button. By clicking this you break the path,
#    the next point will start at a new location.
# 4) When dragging a point's handle, hold down "x" to break contuity: this half of the handle
#    will move independently from the other half.
# 5) Hit ESC to deselect the current selected point.
# 6) Hit TAB to activate or deactivate the magnetic grid. Points will snap to it when moved.
# 7) Hit BACKSPACE to delete the current selected point.
# 8) Press "f" to enter freehand mode. You can now draw freehand lines.
#    Press "f" again to exit freehand mode. When you delete the last point in a freehand path,
#    the whole freehand path will be removed.
# 9) Use the LEFT, RIGHT, UP and DOWN keys to move the path around on the canvas.
#
# The path you are creating is automatically stored in an SVG file for which you can 
# supply a name. The file is constantly updated with your changes.
# You can then import the file with the SVG library in other NodeBox projects to do all sorts
# of fun and programmatic things with your path. You can also import the SVG file in Illustrator
# or Inkscape to fine-tune it.

######################################################################################################

from nodebox.graphics import MOVETO, LINETO, CURVETO, CLOSE, CENTER, Point, PathElement, BezierPath
from math import sin, cos, atan, pi, degrees, radians, sqrt, pow

KEY_TAB = 48
KEY_ESC = 53

#### MAGNETIC GRID ###################################################################################

class MagneticGrid:
    
    def __init__(self, padding=10):
        
        self.padding = padding
        self.stroke = _ctx.color(0.8)
        self.strokewidth = 0.5
        
    def draw(self):
        
        _ctx.nofill()
        _ctx.stroke(self.stroke)
        _ctx.strokewidth(self.strokewidth)
        _ctx.autoclosepath(False)
        _ctx.beginpath(0,0)
        
        for x in range(_ctx.WIDTH):
            _ctx.moveto(x*self.padding, 0)
            _ctx.lineto(x*self.padding, _ctx.HEIGHT)
                
        for y in range(_ctx.HEIGHT/self.padding):
            _ctx.moveto(0, y*self.padding)
            _ctx.lineto(_ctx.WIDTH, y*self.padding)
        
        _ctx.endpath()
        
    def snap(self, x, y, treshold=0.4):
        
        l = x - (x%self.padding)
        t = y - (y%self.padding)
        r = l + self.padding
        b = t + self.padding
        
        treshold *= self.padding
        gx, gy = x, y
        if x-l < treshold and y-t < treshold: gx, gy = l, t # snap top left
        if r-x < treshold and y-t < treshold: gx, gy = r, t # snap top right
        if r-x < treshold and b-y < treshold: gx, gy = r, b # snap bottom right
        if x-l < treshold and b-y < treshold: gx, gy = l, b # snap bottom left
        
        return gx, gy

#### BEZIER PATH EDITOR ##############################################################################

class BezierPathEditor:
    
    def __init__(self, path=None, file="path", freehand=False):
        
        if path != None:
            self.path = path
            self._points = list(path)
            for pt in self._points:
                pt.freehand = False
                if pt.cmd == LINETO or pt.cmd == MOVETO:
                    pt.ctrl1 = Point(pt.x, pt.y)
                    pt.ctrl2 = Point(pt.x, pt.y)
        else:
            self.path = None
            self._points = []
        
        # These variables discern between different
        # modes of interaction.
        # In add-mode, new contains the last point added.
        # In edit-mode, edit contains the index of the point
        # in the path being edited.
        
        self.new = None
        self.edit = None
        self.editing = False
        self.insert = False
        self.inserting = False
        
        self.drag_point = False
        self.drag_handle1 = False
        self.drag_handle2 = False
        
        self.freehand = freehand
        self.freehand_move = True
        
        # Colors used to draw interface elements.
        
        self.strokewidth = 0.75
        self.path_color = _ctx.color(0.2)
        self.path_fill = _ctx.color(0,0,0,0)
        self.handle_color = _ctx.color(0.6)
        self.new_color = _ctx.color(0.8)
        
        # Checks whether the SVG export file
        # should be updated based on the user's edits.
        
        self._dirty = False
        self.file = file
        
        # Different states for button actions.
        # When delete contains a number,
        # delete that index from the path.
        # When moveto contains True,
        # do a MOVETO before adding the next new point.
        
        self.delete = None
        self.moveto = None
        self.last_moveto = None
        self.btn_r = 5
        self.btn_x = -5-1
        self.btn_y = -5*2
        
        # Magnetic grid to snap to when enabled.
        
        self.grid = MagneticGrid()
        self.show_grid = False
        
        # Keyboard keys pressed.
        
        self.last_key = None
        self.last_keycode = None
        
        # A message to flash on the screen.
        
        self.msg = ""
        self.msg_alpha = 1.0
        
    def overlap(self, x1, y1, x2, y2, r=5):
        
        """ Returns True when point 1 and point 2 overlap.
        
        There is an r treshold in which point 1 and point 2
        are considered to overlap.
        
        """
        
        if abs(x2-x1) < r and abs(y2-y1) < r:
            return True
        else:
            return False
    
    def reflect(self, x0, y0, x, y):
        
        """ Reflects the point x, y through origin x0, y0.
        """
                
        rx = x0 - (x-x0)
        ry = y0 - (y-y0)
        return rx, ry

    def angle(self, x0, y0, x1, y1):
        
        """ Calculates the angle between two points.
        """
    
        a = degrees( atan((y1-y0) / (x1-x0+0.00001)) ) + 360
        if x1-x0 < 0: a += 180
        return a

    def distance(self, x0, y0, x1, y1):
    
        """ Calculates the distance between two points.
        """
    
        return sqrt(pow(x1-x0, 2) + pow(y1-y0, 2))
        
    def coordinates(self, x0, y0, distance, angle):
        
        """ Calculates the coordinates of a point from the origin.
        """
        
        x = x0 + cos(radians(angle)) * distance
        y = y0 + sin(radians(angle)) * distance
        return Point(x, y)
    
    def contains_point(self, x, y, d=2):
        
        """ Returns true when x, y is on the path stroke outline.
        """
        
        if self.path != None and len(self.path) > 1 \
        and self.path.contains(x, y):
            # If all points around the mouse are also part of the path,
            # this means we are somewhere INSIDE the path.
            # Only points near the edge (i.e. on the outline stroke)
            # should propagate.
            if not self.path.contains(x+d, y) \
            or not self.path.contains(x, y+d) \
            or not self.path.contains(x-d, y) \
            or not self.path.contains(x, y-d) \
            or not self.path.contains(x+d, y+d) \
            or not self.path.contains(x-d, y-d) \
            or not self.path.contains(x+d, y-d) \
            or not self.path.contains(x-d, y+d):
                return True

        return False

    def insert_point(self, x, y):
        
        """ Inserts a point on the path at the mouse location.
        
        We first need to check if the mouse location is on the path.
        Inserting point is time intensive and experimental.
        
        """
        
        try: 
            bezier = _ctx.ximport("bezier")
        except:
            from nodebox.graphics import bezier
        
        # Do a number of checks distributed along the path.
        # Keep the one closest to the actual mouse location.
        # Ten checks works fast but leads to imprecision in sharp corners
        # and curves closely located next to each other.
        # I prefer the slower but more stable approach.
        n = 100
        closest = None
        dx0 = float("inf") 
        dy0 = float("inf")
        for i in range(n):
            t = float(i)/n
            pt = self.path.point(t)
            dx = abs(pt.x-x)
            dy = abs(pt.y-y)
            if dx+dy <= dx0+dy0:
                dx0 = dx
                dy0 = dy
                closest = t

        # Next, scan the area around the approximation.
        # If the closest point is located at 0.2 on the path,
        # we need to scan between 0.1 and 0.3 for a better
        # approximation. If 1.5 was the best guess, scan
        # 1.40, 1.41 ... 1.59 and so on.
        # Each decimal precision takes 20 iterations.                
        decimals = [3,4]
        for d in decimals:
            d = 1.0/pow(10,d)
            
            for i in range(20):
                t = closest-d + float(i)*d*0.1
                if t < 0.0: t = 1.0+t
                if t > 1.0: t = t-1.0
                pt = self.path.point(t)
                dx = abs(pt.x-x)
                dy = abs(pt.y-y)
                if dx <= dx0 and dy <= dy0:
                    dx0 = dx
                    dy0 = dy
                    closest_precise = t
            
            closest = closest_precise   

        # Update the points list with the inserted point.
        p = bezier.insert_point(self.path, closest_precise)
        i, t, pt = bezier._locate(self.path, closest_precise)
        i += 1
        pt = PathElement()
        pt.cmd = p[i].cmd
        pt.x = p[i].x
        pt.y = p[i].y
        pt.ctrl1 = Point(p[i].ctrl1.x, p[i].ctrl1.y)
        pt.ctrl2 = Point(p[i].ctrl2.x, p[i].ctrl2.y)
        pt.freehand = False
        self._points.insert(i, pt)
        self._points[i-1].ctrl1 = Point(p[i-1].ctrl1.x, p[i-1].ctrl1.y)
        self._points[i+1].ctrl1 = Point(p[i+1].ctrl1.x, p[i+1].ctrl1.y)
        self._points[i+1].ctrl2 = Point(p[i+1].ctrl2.x, p[i+1].ctrl2.y)
    
    def update(self):
        
        """ Update runs each frame to check for mouse interaction.
        
        Alters the path by allowing the user to add new points,
        drag point handles and move their location.
        Updates are automatically stored as SVG
        in the given filename.
        
        """
        
        x, y = mouse()
        if self.show_grid:
            x, y = self.grid.snap(x, y)
        
        if _ctx._ns["mousedown"] \
        and not self.freehand:
            
            self._dirty = True
            
            # Handle buttons first.
            # When pressing down on a button, all other action halts.
            # Buttons appear near a point being edited.
            # Once clicked, actions are resolved.
            if self.edit != None \
            and not self.drag_point \
            and not self.drag_handle1 \
            and not self.drag_handle2:
                pt = self._points[self.edit]
                dx = pt.x+self.btn_x
                dy = pt.y+self.btn_y
                # The delete button
                if self.overlap(dx, dy, x, y, r=self.btn_r):
                    self.delete = self.edit
                    return
                # The moveto button,
                # active on the last point in the path.
                dx += self.btn_r*2 + 2
                if self.edit == len(self._points) -1 and \
                   self.overlap(dx, dy, x, y, r=self.btn_r):
                    self.moveto = self.edit
                    return
                    
            if self.insert:
                self.inserting = True
                return
            
            # When not dragging a point or the handle of a point,
            # i.e. the mousebutton was released and then pressed again,
            # check to see if a point on the path is pressed.
            # When this point is not the last new point,
            # enter edit mode.
            if not self.drag_point and \
               not self.drag_handle1 and \
               not self.drag_handle2:
                self.editing = False
                indices = range(len(self._points))
                indices.reverse()
                for i in indices:
                    pt = self._points[i]
                    if pt != self.new \
                    and self.overlap(x, y, pt.x, pt.y) \
                    and self.new == None:
                        # Don't select a point if in fact
                        # it is at the same location of the first handle 
                        # of the point we are currently editing.
                        if self.edit == i+1 \
                        and self.overlap(self._points[i+1].ctrl1.x,
                                         self._points[i+1].ctrl1.y, x, y):
                            continue
                        else:
                            self.edit = i
                            self.editing = True
                            break
            
            # When the mouse button is down,
            # edit mode continues as long as
            # a point or handle is dragged.
            # Else, stop editing and switch to add-mode
            # (the user is clicking somewhere on the canvas).
            if not self.editing:
                if self.edit != None:
                    pt = self._points[self.edit]
                    if self.overlap(pt.ctrl1.x, pt.ctrl1.y, x, y) or \
                       self.overlap(pt.ctrl2.x, pt.ctrl2.y, x, y):
                        self.editing = True
                    else:
                        self.edit = None
                    
            # When not in edit mode, there are two options.
            # Either no new point is defined and the user is
            # clicking somewhere on the canvas (add a new point)
            # or the user is dragging the handle of the new point.
            # Adding a new point is a fluid click-to-locate and
            # drag-to-curve action.
            if self.edit == None:
                if self.new == None:
                    # A special case is when the used clicked
                    # the moveto button on the last point in the path.
                    # This indicates a gap (i.e. MOVETO) in the path.
                    self.new = PathElement()
                    if self.moveto == True \
                    or len(self._points) == 0:
                        cmd = MOVETO
                        self.moveto = None
                        self.last_moveto = self.new
                    else:
                        cmd = CURVETO
                    self.new.cmd = cmd
                    self.new.x = x
                    self.new.y = y
                    self.new.ctrl1 = Point(x, y)
                    self.new.ctrl2 = Point(x, y)
                    self.new.freehand = False
                    # Don't forget to map the point's ctrl1 handle
                    # to the ctrl2 handle of the previous point.
                    # This makes for smooth, continuous paths.
                    if len(self._points) > 0:
                        prev = self._points[-1]
                        rx, ry = self.reflect(prev.x, prev.y, prev.ctrl2.x, prev.ctrl2.y)
                        self.new.ctrl1 = Point(rx, ry)
                    self._points.append(self.new)
                else:
                    # Illustrator-like behavior:
                    # when the handle is dragged downwards,
                    # the path bulges upwards.
                    rx, ry = self.reflect(self.new.x, self.new.y, x, y)
                    self.new.ctrl2 = Point(rx, ry)
            
            # Edit mode
            elif self.new == None:
            
                pt = self._points[self.edit]
            
                # The user is pressing the mouse on a point,
                # enter drag-point mode.
                if self.overlap(pt.x, pt.y, x, y) \
                and not self.drag_handle1 \
                and not self.drag_handle2 \
                and not self.new != None:
                    self.drag_point = True
                    self.drag_handle1 = False
                    self.drag_handle2 = False

                # The user is pressing the mouse on a point's handle,
                # enter drag-handle mode.
                if self.overlap(pt.ctrl1.x, pt.ctrl1.y, x, y) \
                and pt.cmd == CURVETO \
                and not self.drag_point \
                and not self.drag_handle2:
                    self.drag_point = False
                    self.drag_handle1 = True
                    self.drag_handle2 = False
                if self.overlap(pt.ctrl2.x, pt.ctrl2.y, x, y) \
                and pt.cmd == CURVETO \
                and not self.drag_point \
                and not self.drag_handle1:
                    self.drag_point = False
                    self.drag_handle1 = False
                    self.drag_handle2 = True
                
                # In drag-point mode,
                # the point is located at the mouse coordinates.
                # The handles move relatively to the new location
                # (e.g. they are retained, the path does not distort).
                # Modify the ctrl1 handle of the next point as well.
                if self.drag_point == True:
                    dx = x - pt.x
                    dy = y - pt.y
                    pt.x = x
                    pt.y = y
                    pt.ctrl2.x += dx
                    pt.ctrl2.y += dy
                    if self.edit < len(self._points)-1:
                        rx, ry = self.reflect(pt.x, pt.y, x, y)
                        next = self._points[self.edit+1]
                        next.ctrl1.x += dx
                        next.ctrl1.y += dy

                # In drag-handle mode,
                # set the path's handle to the mouse location.
                # Rotate the handle of the next or previous point
                # to keep paths smooth - unless the user is pressing "x".
                if self.drag_handle1 == True:
                    pt.ctrl1 = Point(x, y)
                    if self.edit > 0 \
                    and self.last_key != "x":
                        prev = self._points[self.edit-1]
                        d = self.distance(prev.x, prev.y, prev.ctrl2.x, prev.ctrl2.y)
                        a = self.angle(prev.x, prev.y, pt.ctrl1.x, pt.ctrl1.y)
                        prev.ctrl2 = self.coordinates(prev.x, prev.y, d, a+180)                        
                if self.drag_handle2 == True:   
                    pt.ctrl2 = Point(x, y)
                    if self.edit < len(self._points)-1 \
                    and self.last_key != "x":
                        next = self._points[self.edit+1]
                        d = self.distance(pt.x, pt.y, next.ctrl1.x, next.ctrl1.y)
                        a = self.angle(pt.x, pt.y, pt.ctrl2.x, pt.ctrl2.y)
                        next.ctrl1 = self.coordinates(pt.x, pt.y, d, a+180)
        
        elif not self.freehand:
            
            # The mouse button is released
            # so we are not dragging anything around.
            self.new = None
            self.drag_point = False
            self.drag_handle1 = False
            self.drag_handle2 = False
            
            # The delete button for a point was clicked.
            if self.delete != None and len(self._points) > 0:
                i = self.delete
                cmd = self._points[i].cmd
                del self._points[i]
                if 0 < i < len(self._points):
                    prev = self._points[i-1]
                    rx, ry = self.reflect(prev.x, prev.y, prev.ctrl2.x, prev.ctrl2.y)
                    self._points[i].ctrl1 = Point(rx, ry)
                # Also delete all the freehand points
                # prior to this point.
                start_i = i
                while i > 1:
                    i -= 1
                    pt = self._points[i]
                    if pt.freehand:
                        del self._points[i]
                    elif i < start_i-1 and pt.freehand == False:
                        if pt.cmd == MOVETO:
                            del self._points[i]
                        break
                # When you delete a MOVETO point,
                # the last moveto (the one where the dashed line points to)
                # needs to be updated.
                if len(self._points) > 0 \
                and (cmd == MOVETO or i == 0):
                    self.last_moveto = self._points[0]
                    for pt in self._points:
                        if pt.cmd == MOVETO:
                            self.last_moveto = pt
                self.delete = None
                self.edit = None

            # The moveto button for the last point
            # in the path was clicked.
            elif isinstance(self.moveto, int):
                self.moveto = True
                self.edit = None
            
            # We are not editing a node and
            # the mouse is hovering over the path outline stroke:
            # it is possible to insert a point here.
            elif self.edit == None \
            and self.contains_point(x, y, d=2):
                self.insert = True
            else:
                self.insert = False
            
            # Commit insert of new point.
            if self.inserting \
            and self.contains_point(x, y, d=2): 
                self.insert_point(x, y)
                self.insert = False
            self.inserting = False
            
            # No modifications are being made right now
            # and the SVG file needs to be updated.
            if self._dirty == True:
                self.export_svg()
                self._dirty = False
        
        # Keyboard interaction.
        if _ctx._ns["keydown"]:
            self.last_key = _ctx._ns["key"]
            self.last_keycode = _ctx._ns["keycode"]
        if not _ctx._ns["keydown"] and self.last_key != None:
            # If the TAB-key is pressed,
            # switch the magnetic grid either on or off.
            if self.last_keycode == KEY_TAB:
                self.show_grid = not self.show_grid
            # When "f" is pressed, switch freehand mode.
            if self.last_key == "f":
                self.edit = None
                self.freehand = not self.freehand
                if self.freehand:
                    self.msg = "freehand"
                else:
                    self.msg = "curves"
            # When ESC is pressed exit edit mode.
            if self.last_keycode == KEY_ESC:
                self.edit = None
            # When BACKSPACE is pressed, delete current point.
            if self.last_keycode == _ctx.KEY_BACKSPACE \
            and self.edit != None:
                self.delete = self.edit
            self.last_key = None
            self.last_code = None
        
        # Using the keypad you can scroll the screen.
        if _ctx._ns["keydown"]:
            dx = 0
            dy = 0
            keycode = _ctx._ns["keycode"]
            if keycode == _ctx.KEY_LEFT:
                dx = -10
            elif keycode == _ctx.KEY_RIGHT:
                dx = 10
            if keycode == _ctx.KEY_UP:
                dy = -10
            elif keycode == _ctx.KEY_DOWN:
                dy = 10
            if dx != 0 or dy != 0:
                for pt in self._points:
                    pt.x += dx
                    pt.y += dy
                    pt.ctrl1.x += dx
                    pt.ctrl1.y += dy
                    pt.ctrl2.x += dx
                    pt.ctrl2.y += dy

    def draw(self):
        
        """ Draws the editable path and interface elements.
        """
                
        # Enable interaction.
        self.update()
        x, y = mouse()
        
        # Snap to grid when enabled.
        # The grid is enabled with the TAB key.
        if self.show_grid:
            self.grid.draw()
            x, y = self.grid.snap(x, y)
        
        _ctx.strokewidth(self.strokewidth)
        if self.freehand:
            self.draw_freehand()
        
        r = 4
        _ctx.nofill()
        if len(self._points) > 0:
            
            first = True            
            for i in range(len(self._points)):
                
                # Construct the path.
                pt = self._points[i]
                if first:
                    _ctx.beginpath(pt.x, pt.y)
                    first = False
                else:
                    if pt.cmd == CLOSE:
                        _ctx.closepath()
                    elif pt.cmd == MOVETO:
                        _ctx.moveto(pt.x, pt.y)
                    elif pt.cmd == LINETO:
                        _ctx.lineto(pt.x, pt.y)
                    elif pt.cmd == CURVETO:
                        _ctx.curveto(pt.ctrl1.x, pt.ctrl1.y, 
                                     pt.ctrl2.x, pt.ctrl2.y, 
                                     pt.x, pt.y)
                # In add- or edit-mode,
                # display the current point's handles.
                if ((i == self.edit and self.new == None) \
                or pt == self.new) \
                and pt.cmd == CURVETO \
                and not pt.freehand:
                    _ctx.stroke(self.handle_color)
                    _ctx.nofill()
                    _ctx.oval(pt.x-r, pt.y-r, r*2, r*2)
                    _ctx.stroke(self.handle_color)
                    _ctx.line(pt.ctrl2.x, pt.ctrl2.y, pt.x, pt.y)
                    _ctx.fill(self.handle_color)
                # Display the new point's handle being dragged.
                if pt == self.new \
                and not pt.freehand:
                    rx, ry = self.reflect(pt.x, pt.y, pt.ctrl2.x, pt.ctrl2.y)
                    _ctx.stroke(self.handle_color)
                    _ctx.line(rx, ry, pt.x, pt.y)
                    _ctx.nostroke()
                    _ctx.fill(self.handle_color)
                    _ctx.oval(rx-r/2, ry-r/2, r, r)
                # Display handles for point being edited.
                if i == self.edit \
                and self.new == None \
                and pt.cmd == CURVETO \
                and not pt.freehand:
                    _ctx.oval(pt.ctrl2.x-r/2, pt.ctrl2.y-r/2, r, r)
                    if i > 0:
                        prev = self._points[i-1]
                        _ctx.line(pt.ctrl1.x, pt.ctrl1.y, prev.x, prev.y)
                        _ctx.oval(pt.ctrl1.x-r/2, pt.ctrl1.y-r/2, r, r)
                    if i > 0 and self._points[i-1].cmd != MOVETO:
                        _ctx.line(prev.ctrl2.x, prev.ctrl2.y, prev.x, prev.y)
                    if i < len(self._points)-1:
                        next = self._points[i+1]
                        if next.cmd == CURVETO:
                            _ctx.line(next.ctrl1.x, next.ctrl1.y, pt.x, pt.y)
                
                # When hovering over a point,
                # highlight it.
                elif self.overlap(x, y, pt.x, pt.y) \
                and not pt.freehand:
                    self.insert = False # quit insert mode
                    _ctx.nofill()
                    _ctx.stroke(self.handle_color)
                    _ctx.oval(pt.x-r, pt.y-r, r*2, r*2)
                
                # Provide visual coordinates
                # for points being dragged, moved or hovered.
                _ctx.fontsize(9)
                _ctx.fill(self.handle_color)
                txt = " ("+str(int(pt.x))+", "+str(int(pt.y))+")"
                if (i == self.edit and self.new == None) \
                or pt == self.new \
                and not pt.freehand:
                    _ctx.text(txt, pt.x+r, pt.y+2)                                       
                elif self.overlap(x, y, pt.x, pt.y) \
                and not pt.freehand:
                    _ctx.text(txt, pt.x+r, pt.y+2)

                # Draw a circle for each point
                # in the path.
                if not pt.freehand:
                    if pt.cmd != MOVETO:
                        _ctx.fill(self.path_color)
                        _ctx.nostroke()
                    else:
                        _ctx.stroke(self.path_color)
                        _ctx.nofill()
                    _ctx.oval(pt.x-r/2, pt.y-r/2, r, r)
                
            # Draw the current path,
            # update the path property.
            _ctx.stroke(self.path_color)
            _ctx.fill(self.path_fill)
            _ctx.autoclosepath(False)    
            p = _ctx.endpath()
            self.path = p
            
            # Possible to insert a point here.
            if self.insert:
                _ctx.stroke(self.handle_color)
                _ctx.nofill()
                _ctx.oval(x-r*0.8, y-r*0.8, r*1.6, r*1.6)
                
            # When not editing a node,
            # prospect how the curve will continue
            # when adding a new point.
            if self.edit == None \
            and self.new == None \
            and self.moveto != True \
            and not self.freehand:
                _ctx.nofill()
                _ctx.stroke(self.new_color)
                rx, ry = self.reflect(pt.x, pt.y, pt.ctrl2.x, pt.ctrl2.y)
                _ctx.beginpath(pt.x, pt.y)
                _ctx.curveto(rx, ry, x, y, x, y)
                _ctx.endpath()

                # A dashed line indicates what
                # a CLOSETO would look like.
                if self.last_moveto != None:
                    start = self.last_moveto
                else:
                    start = self._points[0]
                p = _ctx.line(x, y, start.x, start.y, draw=False)
                try: p._nsBezierPath.setLineDash_count_phase_([2,4], 2, 50)
                except:
                    pass
                _ctx.drawpath(p)
        
            # When doing a MOVETO,
            # show the new point hovering at the mouse location.
            elif self.edit == None \
            and self.new == None \
            and self.moveto != None:
                _ctx.stroke(self.new_color)
                _ctx.nofill()
                _ctx.oval(x-r*0.8, y-r*0.8, r*1.6, r*1.6)
            
            # Draws button for a point being edited.
            # The first button deletes the point.
            # The second button, which appears only on the last point
            # in the path, tells the editor to perform a MOVETO
            # before adding a new point.
            if self.edit != None:
                pt = self._points[self.edit]
                x = pt.x + self.btn_x
                y = pt.y + self.btn_y
                r = self.btn_r
                _ctx.nostroke()
                _ctx.fill(0,0,0,0.2)
                _ctx.fill(self.handle_color)
                _ctx.oval(x-r, y-r, r*2, r*2)
                _ctx.fill(1)
                _ctx.rotate(45)
                _ctx.rect(x-r+2, y-0.625, r+1, 1.25)
                _ctx.rotate(-90)
                _ctx.rect(x-r+2, y-0.625, r+1, 1.25)
                _ctx.reset()
                if self.edit == len(self._points)-1:
                    _ctx.fill(self.handle_color)
                    _ctx.oval(x+r*2+2-r, y-r, r*2, r*2)
                    _ctx.fill(1)
                    _ctx.rect(x+r*2+2-2.25, y-r+3, 1.5, r-1)
                    _ctx.rect(x+r*2+2+0.75, y-r+3, 1.5, r-1)
        
        # Handle onscreen notifications.
        # Any text in msg is displayed in a box in the center
        # and slowly fades away, after which msg is cleared.    
        if self.msg != "":
            self.msg_alpha -= 0.1
            _ctx.nostroke()
            _ctx.fill(0,0,0, self.msg_alpha)
            _ctx.fontsize(18)
            _ctx.lineheight(1)
            w = _ctx.textwidth(self.msg)
            _ctx.rect(_ctx.WIDTH/2-w/2-9, _ctx.HEIGHT/2-27, w+18, 36, roundness=0.4)
            _ctx.fill(1,1,1, 0.8)
            _ctx.align(CENTER) 
            _ctx.text(self.msg, 0, _ctx.HEIGHT/2, width=_ctx.WIDTH)
        if self.msg_alpha <= 0.0:
            self.msg = ""
            self.msg_alpha = 1.0
    
    def draw_freehand(self):
        
        """ Freehand sketching.
        """
        
        if _ctx._ns["mousedown"]:
            
            x, y = mouse()
            if self.show_grid:
                x, y = self.grid.snap(x, y)
            
            if self.freehand_move == True:
                cmd = MOVETO
                self.freehand_move = False
            else:
                cmd = LINETO
            
            # Add a new LINETO to the path,
            # except when starting to draw,
            # then a MOVETO is added to the path.
            pt = PathElement()
            if cmd != MOVETO:
                pt.freehand = True # Used when mixed with curve drawing.
            else:
                pt.freehand = False
            pt.cmd = cmd
            pt.x = x
            pt.y = y
            pt.ctrl1 = Point(x,y)
            pt.ctrl2 = Point(x,y)
            self._points.append(pt)
            
            # Draw the current location of the cursor.
            r = 4
            _ctx.nofill()
            _ctx.stroke(self.handle_color)
            _ctx.oval(pt.x-r, pt.y-r, r*2, r*2)
            _ctx.fontsize(9)
            _ctx.fill(self.handle_color)
            _ctx.text(" ("+str(int(pt.x))+", "+str(int(pt.y))+")", pt.x+r, pt.y)
        
            self._dirty = True
        
        else:

            # Export the updated drawing,
            # remember to do a MOVETO on the next interaction.
            self.freehand_move = True
            if self._dirty:
                self._points[-1].freehand = False
                self.export_svg()
                self._dirty = False
                
    def export_svg(self):
        
        """ Exports the path as SVG.
        
        Uses the filename given when creating this object.
        The file is automatically updated to reflect
        changes to the path.
        
        """
        
        d = ""
        if len(self._points) > 0:
            d += "M "+str(self._points[0].x)+" "+str(self._points[0].y)+" "
            for pt in self._points:
                if pt.cmd == MOVETO:
                    d += "M "+str(pt.x)+" "+str(pt.y)+" "
                elif pt.cmd == LINETO:
                    d += "L "+str(pt.x)+" "+str(pt.y)+" "
                elif pt.cmd == CURVETO:
                    d += "C "
                    d += str(pt.ctrl1.x)+" "+str(pt.ctrl1.y)+" "
                    d += str(pt.ctrl2.x)+" "+str(pt.ctrl2.y)+" "
                    d += str(pt.x)+" "+str(pt.y)+" "
        
        c = "rgb("
        c += str(int(self.path_color.r*255)) + ","
        c += str(int(self.path_color.g*255)) + ","
        c += str(int(self.path_color.b*255)) + ")"
        
        s  = '<?xml version="1.0"?>\n'
        s += '<svg width="'+str(_ctx.WIDTH)+'pt" height="'+str(_ctx.HEIGHT)+'pt">\n'
        s += '<g>\n'
        s += '<path d="'+d+'" fill="none" stroke="'+c+'" stroke-width="'+str(self.strokewidth)+'" />\n'
        s += '</g>\n'
        s += '</svg>\n'
        
        f = open(self.file+".svg", "w")
        f.write(s)
        f.close()

######################################################################################################

def mouse():

    x = _ctx._ns["MOUSEX"]
    y = _ctx._ns["MOUSEY"]    
    return (x, y)

def start(path=None, filename="path", freehand=None):
    return BezierPathEditor(path, filename, freehand)
