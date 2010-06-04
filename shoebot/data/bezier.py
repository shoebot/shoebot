import sys, locale, gettext
from shoebot.data import _copy_attrs
##from shoebot.data import Grob, ColorMixin, TransformMixin
from shoebot.data import Grob, ColorMixin
from shoebot.util import RecordingSurface
from shoebot import MOVETO, RMOVETO, LINETO, RLINETO, CURVETO, RCURVETO, ARC, ELLIPSE, CLOSE
from math import pi as _pi

import cairo

from grob import CENTER, CORNER

APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
#gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext


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
    def __init__(self, canvas, fillcolor=None, strokecolor=None, strokewidth=None, pathmode=CORNER):
        # Stores two lists, _elements and _render_funcs that are kept syncronized
        # _render_funcs contain functions that do the rendering
        # _elements contains either a PathElement or the arguments that need
        # to be passed to a PathElement when it's created.
        #
        # This way PathElements are not created unless they are used in the bot
        Grob.__init__(self, canvas = canvas)

        self._elements = []
        self._render_funcs = []
        self._fillcolor = fillcolor
        self._strokecolor = strokecolor
        self._strokewidth = strokewidth
        self._pathmode = pathmode
        self.closed = False

        self._drawn = False
        self._bounds = None
        self._center = None

    def _append_element(self, render_func, pe):
        '''
        Append a render function and the parameters to pass
        an equivilent PathElement, or the PathElement itself.
        '''
        self._render_funcs.append(render_func)
        self._elements.append(pe)

    def append(self, *args):
        if len(args) is 2:
            ## TODO, check this against nodebox
            self.moveto(*args)
        else:
            if pe.cmd == MOVETO:
                self._append_element(self._canvas.moveto_closure(p.x, p.y), pe)
            elif pe.cmd == LINETO:
                self._append_element(self._canvas.lineto_closure(p.x, p.y), pe)
            elif pe.cmd == CURVETO:
                self._append_element(self._canvas.curveto_closure(p.x, p.y, p.c1x, p.c1y, p.c2x, p.c2y), pe)

    def addpoint(self, *args):
        self.append(*args)

    def copy(self):
        path =BezierPath(self._canvas, self._fillcolor, self._strokecolor, self._strokewidth, self._pathmode)
        path.closed = self.closed
        path._center = self._center
        path._elements = list(self._elements)
        return path

    def moveto(self, x, y):
        self._append_element(self._canvas.moveto_closure(x, y), (MOVETO, x, y))

    def lineto(self, x, y):
        self._append_element(self._canvas.lineto_closure(x, y), (LINETO, x, y))

    def curveto(self, x1, y1, x2, y2, x3, y3):
        self._append_element(self._canvas.curveto_closure(x1, y1, x2, y2, x3, y3), (CURVETO, x1, y1, x2, y2, x3, y3))

    def closepath(self):
        self._append_element(self._canvas.closepath_closure(), (CLOSE,))
        self.closed = True

    def ellipse(self, x, y, w, h):
        self._append_element(self._canvas.ellipse_closure(x, y, w, h), (ELLIPSE, x, y, w, h)) 
        self.closed = True


    def rellineto(self, x, y):
        self._append_element(self._canvas.rellineto_closure(x, y), (RLINETO, x, y))

    def rect(self, x, y, w, h, roundness=0.0, rectmode=CORNER):
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

    def _get_bounds(self):
        '''
        Return cached bounds of this Grob.
        If bounds are not cached, render to a meta surface, and
        keep the meta surface and bounds cached.
        '''
        if self._bounds:
            return self._bounds

        record_surface = RecordingSurface(0, 0)
        dummy_ctx = cairo.Context(record_surface)
        self._traverse(dummy_ctx)
        
        self._bounds = dummy_ctx.path_extents()        
        return self._bounds

    def _get_dimensions(self):
        bounds = (x1,y1,x2,y2) = self._get_bounds()
        return x1, y1

    def _get_center(self):
        '''
        Return cached bounds of this Grob.
        If bounds are not cached, render to a meta surface, and
        keep the meta surface and bounds cached.
        '''
        if self._center:
            return self._center

       
        # get the center point
        (x1,y1,x2,y2) = self._get_bounds()
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2

        center = self._center = x, y
        ### TODO Cache function that draws using the RecordingSurface
        ### Save the context or surface (without the bounding box strokecolor)
        ### to optimise drawing
        return center

    def _render_closure(self):
        '''Use a closure so that draw attributes can be saved'''
        fillcolor = self._get_fillcolor()
        strokecolor = self._get_strokecolor()
        strokewidth = self._get_strokewidth()

        def _render(cairo_ctx):
            '''
            At the moment this is based on cairo.

            TODO: Need to work out how to move the cairo specific
                  bits somewhere else.
            '''
            # Go to initial point (CORNER or CENTER):
            transform = self._call_transform_mode(self._transform)

            # Change the origin if nessacary
            if self._get_pathmode() == CENTER:
                xc, yc = self._get_center()
                transform.translate(-xc, -yc)


            cairo_ctx.transform(transform)
            # Run the path commands on the cairo context:
            self._traverse(cairo_ctx)
            ## Matrix affects stroke, so we need to reset it:
            cairo_ctx.set_matrix(cairo.Matrix())

            if fillcolor is not None and strokecolor is not None:
                # Draw onto intermediate surface so that stroke
                # does not overlay fill
                cairo_ctx.push_group()

                cairo_ctx.set_source_rgba(*fillcolor)
                cairo_ctx.fill_preserve()

                cairo_ctx.set_source_rgba(*strokecolor)
                cairo_ctx.set_operator(cairo.OPERATOR_SOURCE)
                cairo_ctx.set_line_width(strokewidth)
                cairo_ctx.stroke()
            
                cairo_ctx.pop_group_to_source ()
                cairo_ctx.paint ()
            elif fillcolor is not None:
                cairo_ctx.set_source_rgba(*fillcolor)
                cairo_ctx.fill()
            elif strokecolor is not None:
                cairo_ctx.set_source_rgba(*strokecolor)
                cairo_ctx.set_line_width(strokewidth)
                cairo_ctx.stroke()


        return _render

    def draw(self):
        self._deferred_render(self._render_closure())

    def _get_contours(self):
        """ 
        Returns a list of contours in the path, as BezierPath objects.
        A contour is a sequence of lines and curves separated from the next contour by a MOVETO.
        For example, the glyph "o" has two contours: the inner circle and the outer circle.

        From nodebox
        """
        contours = []
        current_contour = None
        empty = True
        for i, el in enumerate(self._get_elements()):
            if el.cmd == MOVETO:
                if not empty:
                    contours.append(current_contour)
                current_contour = BezierPath(self._canvas)
                current_contour.moveto(el.x, el.y)
                empty = True
            elif el.cmd == LINETO:
                empty = False
                current_contour.lineto(el.x, el.y)
            elif el.cmd == CURVETO:
                empty = False
                current_contour.curveto(el.c1x, el.c1y, el.c2x, el.c2y, el.x, el.y)
            elif el.cmd == CLOSE:
                current_contour.closepath()
        if not empty:
            contours.append(current_contour)
        return contours

    def _get_elements(self):
        '''
        Yields all elements as PathElements
        '''
        for index, el in enumerate(self._elements):
            if isinstance(el, tuple):
                el = PathElement(*el)
                self._elements[index] = el
            yield el


    def __getitem__(self, index):
        '''
        el is either a PathElement or the parameters to pass
        to one.
        If el is a PathElement return it
        If el is parameters, create a PathElement and return it
        '''
        el = self._elements[index]
        if isinstance(el, tuple):
            el = PathElement(*el)
            self._elements[index] = el
        return el

    def __iter__(self):
        for index in xrange(len(self._elements)):
            yield self.__getitem__(index)

    def __len__(self):
        return len(self._elements)

    contours = property(_get_contours)


class ClippingPath(BezierPath):
    
    # stateAttributes = ('_fillcolorcolor', '_strokecolorcolor', '_strokewidth')
    # kwargs = ('fillcolor', 'strokecolor', 'strokewidth')    
    
    def __init__(self, canvas, path=None, **kwargs):
        BezierPath.__init__(self, canvas, path, **kwargs)

class EndClip(Grob):
    def __init__(self, canvas, **kwargs):
        Grob.__init__(self, canvas = canvas)

    def _render(self, ctx):
        pass

class PathElement(object):
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

