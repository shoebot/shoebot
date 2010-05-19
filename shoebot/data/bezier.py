import sys, locale, gettext
from shoebot.data import _copy_attrs
from shoebot.data import Grob, ColorMixin, TransformMixin
from shoebot.util import RecordingSurface
from math import pi as _pi

import cairo

APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
#gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext


MOVETO = "moveto"
RMOVETO = "rmoveto"
LINETO = "lineto"
RLINETO = "rlineto"
CURVETO = "curveto"
RCURVETO = "rcurveto"
ARC = 'arc'
ELLIPSE = 'ellipse'
CLOSE = "close"

class BezierPath(Grob):
    '''
    Represents a Bezier path as a list of PathElements.

    Shoebot implementation of Nodebox's BezierPath wrapper.
    While Nodebox relies on Cocoa/QT for its data structures,
    this is more of an "agnostic" implementation that won't
    require any other back-ends to do some simple work with paths.

    (this last sentence is not so correct: we use a bit of Cairo
    for getting path dimensions)
    '''
    def __init__(self, canvas, fillcolor=None, strokecolor=None, strokewidth=None, pathmode='corner'):
        # Internally stores two lists
        #
        # _render_funcs  References to functions to render each PathElement
        # _elements      Items start as tuples, but if a PathElement is
        #                requested then it is stored there.
        Grob.__init__(self, canvas = canvas)

        self._render_funcs = []
        self._elements = []
        self._fillcolor = fillcolor or canvas.fillcolor
        self._strokecolor = strokecolor or canvas.strokecolor
        self._strokewidth = strokewidth or canvas.strokewidth
        self._pathmode = pathmode or canvas.pathmode
        self.closed = False

        self._drawn = False
        self._center = None

    def _append_element(self, render_func, element):
        '''
        Append a render function and the parameters to pass
        an equivilent PathElement, or the PathElement itself.
        '''
        self._render_funcs.append(render_func)
        self._elements.append(element)

    def moveto(self, x, y):
        self._append_element(self._canvas.moveto_closure(x, y), (MOVETO, x, y))

    def lineto(self, x, y):
        self._append_element(self._canvas.lineto_closure(x, y), (LINETO, x, y))

    def curveto(self, x1, y1, x2, y2, x3, y3):
        self._append_element(self._canvas.curveto_closure(x1, y1, x2, y2, x3, y3), (CURVETO, x1, y1, x2, y2, x3, y3))

    def closepath(self):
        self._append_element(self._canvas.closepath_closure(), (CLOSE))
        self.closed = True

    def ellipse(self, x, y, w, h):
        self._append_element(self._canvas.ellipse_closure(x, y, w, h), (ELLIPSE, x, y, w, h)) 
        self.closed = True


    def rellineto(self, x, y):
        self._append_element(self._canvas.rellineto_closure(x, y), (RLINETO, x, y))

    def rect(self, x, y, w, h, roundness=0.0, rectmode='corner'):
        if not roundness:
            self.moveto(x, y)
            self.rellineto(w, 0)
            self.rellineto(0, h)
            self.rellineto(-w, 0)
            self.closepath()
        else:
            curve = min(w*roundness, h*roundness)
            self.moveto(x, y+curve)
            self.curveto(x, y, x, y, x+curve, y)
            self.lineto(x+w-curve, y)
            self.curveto(x+w, y, x+w, y, x+w, y+curve)
            self.lineto(x+w, y+h-curve)
            self.curveto(x+w, y+h, x+w, y+h, x+w-curve, y+h)
            self.lineto(x+curve, y+h)
            self.curveto(x, y+h, x, y+h, x, y+h-curve)
            self.closepath()
    
    def _traverse(self, cairo_ctx):
        '''
        Traverse this path
        '''
        for render_func in self._render_funcs:
            render_func(cairo_ctx)

    def _get_center(self):
        '''
        Return cached bounds of this Grob.
        If bounds are not cached, render to a meta surface, and
        keep the meta surface and bounds cached.
        '''
        if self._center:
            return self._center

        record_surface = RecordingSurface(*self._canvas.size)
        dummy_ctx = cairo.Context(record_surface)
        self._traverse(dummy_ctx)
        
        bounds = dummy_ctx.path_extents()
        
        # get the center point
        (x1,y1,x2,y2) = bounds
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2

        center = self._center = x, y
        ### TODO Cache function that draws using the RecordingSurface
        ### Save the context or surface (without the bounding box strokecolor)
        ### to optimise drawing
        return center

    def _render(self, cairo_ctx):
        '''
        At the moment this is based on cairo.

        TODO: Need to work out how to move the cairo specific
              bits somewhere else.
        '''
        # Go to initial point (CORNER or CENTER):
        transform = self._call_transform_mode(self._transform)

        # Change the origin if nessacary
        if self._pathmode == 'center':
            xc, yc = self._get_center()
            transform.translate(-xc, -yc)

        cairo_ctx.set_matrix(transform)

        # Change the origin if nessacary
        if self._pathmode == 'center':
            xc, yc = self._get_center()
            cairo_ctx.move_to(-xc, -yc)

        # Run the path commands on the cairo context:
        self._traverse(cairo_ctx)
        ## Matrix affects stroke, so we need to reset it:
        cairo_ctx.set_matrix(cairo.Matrix())

        if self._fillcolor:
            cairo_ctx.set_source_rgba(*self._fillcolor)
            if self._strokecolor:
                cairo_ctx.fill_preserve()
            else:
                cairo_ctx.fill()
        if self._strokecolor:
            cairo_ctx.set_line_width(self._strokewidth)
            cairo_ctx.set_source_rgba(*self._strokecolor)
            cairo_ctx.stroke()

    def draw(self):
        '''
        Save the current fillcolor, strokecolor and transform
        then add the render function to the draw queue
        '''
        self._fillcolor = self._fillcolor or self._canvas.fillcolor
        self._strokecolor = self._strokecolor or self._canvas.strokecolor
        self._strokewidth = self._canvas.strokewidth
        self._deferred_render()

    def _path_element(self, el):
        '''
        el is either a PathElement or the parameters to pass
        to one.
        If el is a PathElement return it
        If el is parameters, create a PathElement and return it
        '''
        if isinstance(el, tuple):
            el = PathElement(el[1], el[1:])
            self._elements[index] = el
        return el

    def __getitem__(self, index):
        el = self._elements[index]
        return self._path_element(el)

    def __iter__(self):
        for el in self._elements():
            yield self._path_element(el)

    def __len__(self):
        return len(self._elements)


class ClippingPath(BezierPath):
    
    # stateAttributes = ('_fillcolorcolor', '_strokecolorcolor', '_strokewidth')
    # kwargs = ('fillcolor', 'strokecolor', 'strokewidth')    
    
    def __init__(self, bot, path=None, **kwargs):
        BezierPath.__init__(self, bot, path, **kwargs)

class EndClip(Grob):
    def __init__(self, bot, **kwargs):
        self._bot = bot

class PathElement:
    '''
    Represents a single element in a Bezier path.

    The first argument should be a command string,
    following the proper values according to which element we want.

    Possible input:
        ('moveto', x, y)
        ('lineto', x, y)
        ('rlineto', x, y)
        ('curveto', c1x, c1y, c2x, c2y, x, y)
        ('rcurveto', c1x, c1y, c2x, c2y, x, y)
        ('arc', x, y, radius, angle1, angle2)
        ('ellipse', x, y, w, h)
        ('close',)

        Mind the trailing comma in the 'close' example, since it just needs
        an argument. The trailing comma is a way to tell python this really is
        supposed to be a tuple.
    '''

    def __init__(self, cmd, *args):
        self.cmd = cmd
        self.values = args

        if cmd == MOVETO or cmd == RMOVETO:
            self.x, self.y = self.values
            self.c1x = self.c1y = self.c2x = self.c2y = None
        elif cmd == LINETO or cmd == RLINETO:
            self.x, self.y = self.values
        elif cmd == CURVETO or cmd == RCURVETO:
            self.c1x, self.c1y, self.c2x, self.c2y, self.x, self.y = self.values
        elif cmd == CLOSE:
            self.x = self.y = self.c1x = self.c1y = self.c2x = self.c2y = None
        elif cmd == ARC:
            self.x, self.y, self.radius, self.angle1, self.angle2 = self.values
        elif cmd == ELLIPSE:
            # it doesn't feel right having an "ellipse" element, but we need
            # some cairo specific functions to draw it in draw_cairo()
            self.x, self.y, self.w, self.h = self.values
        else:
            raise ValueError(_('Wrong initialiser for PathElement (got "%s")') % (cmd))

    def __getitem__(self, key):
        data = list(self.values)
        data.insert(0, self.cmd)
        return data[key]

    def __repr__(self):
        data = list(self. values)
        data.insert(0, self.cmd)
        return "PathElement" + str(tuple(data))

    def __eq__(self, other):
        if other is None: return False
        if self.cmd != other.cmd: return False
        if self.values != other.values: return False
        return True
    
    def __ne__(self, other):
        return not self.__eq__(other)

