# TODO - Attempt to remove all mention of 'canvas' and 'bot' from here,
#        making it useable outside Shoebot
#
# TODO - Remove the whole 'packed elements' thing, it overcomplicates
#        the implementation.
#
import sys
import locale
import gettext
from shoebot.data import _copy_attrs
# from shoebot.data import Grob, ColorMixin, TransformMixin
from shoebot.core.backend import cairo
from grob import Grob
from itertools import chain
from basecolor import ColorMixin
from math import pi as _pi, sqrt

import geometry

CENTER = 'center'
CORNER = 'corner'
CORNERS = "corners"

APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
# gettext.bindtextdomain(APP)
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


class BezierPath(Grob, ColorMixin):
    '''
    Represents a Bezier path as a list of PathElements.

    Shoebot implementation of Nodebox's BezierPath wrapper.
    While Nodebox relies on Cocoa/QT for its data structures,
    this is more of an "agnostic" implementation that won't
    require any other back-ends to do some simple work with paths.

    (this last sentence is not so correct: we use a bit of Cairo
    for getting path dimensions)
    '''

    _state_attributes = {'fillcolor', 'strokecolor', 'strokewidth', 'transform'}

    def __init__(self, bot, path=None, fill=None, stroke=None, strokewidth=None, pathmode=CORNER, packed_elements=None):
        # Stores two lists, _elements and _render_funcs that are kept syncronized
        # _render_funcs contain functions that do the rendering
        # _elements contains either a PathElement or the arguments that need
        # to be passed to a PathElement when it's created.
        #
        # This way PathElements are not created unless they are used in the bot
        Grob.__init__(self, bot)
        ColorMixin.__init__(self, fill=fill, stroke=stroke, strokewidth=strokewidth)

        if packed_elements is not None:
            self._elements, self._render_funcs = packed_elements
        else:
            self._elements = []
            self._render_funcs = []

        self._pathmode = pathmode
        self.closed = False

        self._drawn = False
        self._bounds = None
        self._center = None
        self._segments = None

        if isinstance(path, (tuple, list)):
            # list of path elements
            for element in path:
                self.append(element)
        elif isinstance(path, BezierPath):
            self._elements = list(path._elements)
            self._render_funcs = list(path._render_funcs)
            self.closed = path.closed

    def _append_element(self, render_func, pe):
        '''
        Append a render function and the parameters to pass
        an equivilent PathElement, or the PathElement itself.
        '''
        self._render_funcs.append(render_func)
        self._elements.append(pe)

    def append(self, *args):
        if len(args) is 2:
            # TODO, check this against nodebox
            self.moveto(*args)
        elif isinstance(args[0], PathElement):
            p = args[0]
            if p.cmd == MOVETO:
                self._append_element(self._canvas.moveto_closure(p.x, p.y), p)
            elif p.cmd == LINETO:
                self._append_element(self._canvas.lineto_closure(p.x, p.y), p)
            elif p.cmd == CURVETO:
                self._append_element(self._canvas.curveto_closure(p.x, p.y, p.c1x, p.c1y, p.c2x, p.c2y), p)

    def addpoint(self, *args):
        self.append(*args)

    def copy(self):
        path = BezierPath(self._bot, None, self._fillcolor, self._strokecolor, self._strokewidth, self._pathmode, packed_elements=(self._elements[:], self._render_funcs[:]))
        path.closed = self.closed
        path._center = self._center
        return path

    def moveto(self, x, y):
        self._append_element(self._canvas.moveto_closure(x, y), (MOVETO, x, y))

    def lineto(self, x, y):
        self._append_element(self._canvas.lineto_closure(x, y), (LINETO, x, y))

    def line(self, x1, y1, x2, y2):
        self.moveto(x1, y1)
        self.lineto(x2, y2)

    def curveto(self, x1, y1, x2, y2, x3, y3):
        self._append_element(self._canvas.curveto_closure(x1, y1, x2, y2, x3, y3), (CURVETO, x1, y1, x2, y2, x3, y3))

    def closepath(self):
        if self._elements:
            start_el = self[0]
            self._append_element(self._canvas.closepath_closure(), (CLOSE, start_el.x, start_el.y))
            self.closed = True

    def ellipse(self, x, y, w, h, ellipsemode=CORNER):
        # convert values if ellipsemode is not CORNER
        if ellipsemode == CENTER:
            x = x - (w / 2)
            y = y - (h / 2)
        elif ellipsemode == CORNERS:
            w = w - x
            h = h - y
        self._append_element(self._canvas.ellipse_closure(x, y, w, h), (ELLIPSE, x, y, w, h))
        self.closed = True

    def rellineto(self, x, y):
        self._append_element(self._canvas.rellineto_closure(x, y), (RLINETO, x, y))

    def rect(self, x, y, w, h, roundness=0.0, rectmode=CORNER):
        # convert values if rectmode is not CORNER
        if rectmode == CENTER:
            x = x - (w / 2)
            y = y - (h / 2)
        elif rectmode == CORNERS:
            w = w - x
            h = h - y

        if not roundness:
            self.moveto(x, y)
            self.rellineto(w, 0)
            self.rellineto(0, h)
            self.rellineto(-w, 0)
            self.closepath()
        else:
            curve = min(w * roundness, h * roundness)
            self.moveto(x, y + curve)
            self.curveto(x, y, x, y, x + curve, y)
            self.lineto(x + w - curve, y)
            self.curveto(x + w, y, x + w, y, x + w, y + curve)
            self.lineto(x + w, y + h - curve)
            self.curveto(x + w, y + h, x + w, y + h, x + w - curve, y + h)
            self.lineto(x + curve, y + h)
            self.curveto(x, y + h, x, y + h, x, y + h - curve)
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

        record_surface = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, (-1, -1, 1, 1))
        dummy_ctx = cairo.Context(record_surface)
        self._traverse(dummy_ctx)

        self._bounds = dummy_ctx.path_extents()
        return self._bounds

    def _get_dimensions(self):
        x1, y1, x2, y2 = self._get_bounds()
        return x1, y1

    def contains(self, x, y):
        '''
        Return cached bounds of this Grob.
        If bounds are not cached, render to a meta surface, and
        keep the meta surface and bounds cached.
        '''
        if self._bounds:
            return self._bounds

        record_surface = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, (-1, -1, 1, 1))
        dummy_ctx = cairo.Context(record_surface)
        self._traverse(dummy_ctx)

        in_fill = dummy_ctx.in_fill(x, y)
        return in_fill

    def _get_center(self):
        '''
        Return cached bounds of this Grob.
        If bounds are not cached, render to a meta surface, and
        keep the meta surface and bounds cached.
        '''
        if self._center:
            return self._center

        # get the center point
        (x1, y1, x2, y2) = self._get_bounds()
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2

        center = self._center = x, y
        # TODO Cache function that draws using the RecordingSurface
        # Save the context or surface (without the bounding box strokecolor)
        # to optimise drawing
        return center

    center = property(_get_center)

    def _render_closure(self):
        '''Use a closure so that draw attributes can be saved'''
        fillcolor = self.fill
        strokecolor = self.stroke
        strokewidth = self.strokewidth

        def _render(cairo_ctx):
            '''
            At the moment this is based on cairo.

            TODO: Need to work out how to move the cairo specific
                  bits somewhere else.
            '''
            # Go to initial point (CORNER or CENTER):
            transform = self._call_transform_mode(self._transform)

            if fillcolor is None and strokecolor is None:
                # Fixes _bug_FillStrokeNofillNostroke.bot
                return

            cairo_ctx.set_matrix(transform)
            # Run the path commands on the cairo context:
            self._traverse(cairo_ctx)
            # Matrix affects stroke, so we need to reset it:
            cairo_ctx.set_matrix(cairo.Matrix())

            if fillcolor is not None and strokecolor is not None:
                if strokecolor[3] < 1:
                    # Draw onto intermediate surface so that stroke
                    # does not overlay fill
                    cairo_ctx.push_group()

                    cairo_ctx.set_source_rgba(*fillcolor)
                    cairo_ctx.fill_preserve()

                    e = cairo_ctx.stroke_extents()
                    cairo_ctx.set_source_rgba(*strokecolor)
                    cairo_ctx.set_operator(cairo.OPERATOR_SOURCE)
                    cairo_ctx.set_line_width(strokewidth)
                    cairo_ctx.stroke()

                    cairo_ctx.pop_group_to_source()
                    cairo_ctx.paint()
                else:
                    # Fast path if no alpha in stroke
                    cairo_ctx.set_source_rgba(*fillcolor)
                    cairo_ctx.fill_preserve()

                    cairo_ctx.set_source_rgba(*strokecolor)
                    cairo_ctx.set_line_width(strokewidth)
                    cairo_ctx.stroke()
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
        """
        # Originally from nodebox-gl
        contours = []
        current_contour = None
        empty = True
        for i, el in enumerate(self._get_elements()):
            if el.cmd == MOVETO:
                if not empty:
                    contours.append(current_contour)
                current_contour = BezierPath(self._bot)
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

    def _locate(self, t, segments=None):
        """ Locates t on a specific segment in the path.
            Returns (index, t, PathElement)
            A path is a combination of lines and curves (segments).
            The returned index indicates the start of the segment that contains point t.
            The returned t is the absolute time on that segment,
            in contrast to the relative t on the whole of the path.
            The returned point is the last MOVETO, any subsequent CLOSETO after i closes to that point.
            When you supply the list of segment lengths yourself, as returned from length(path, segmented=True),
            point() works about thirty times faster in a for-loop since it doesn't need to recalculate
            the length during each iteration.
        """
        # Originally from nodebox-gl
        if segments is None:
            segments = self._segment_lengths(relative=True)
        if len(segments) == 0:
            raise PathError, "The given path is empty"
        for i, el in enumerate(self._get_elements()):
            if i == 0 or el.cmd == MOVETO:
                closeto = Point(el.x, el.y)
            if t <= segments[i] or i == len(segments) - 1:
                break
            else:
                t -= segments[i]
        try:
            t /= segments[i]
        except ZeroDivisionError:
            pass
        if i == len(segments) - 1 and segments[i] == 0:
            i -= 1
        return (i, t, closeto)

    def point(self, t, segments=None):
        """
            Returns the PathElement at time t (0.0-1.0) on the path.

            Returns coordinates for point at t on the path.
            Gets the length of the path, based on the length of each curve and line in the path.
            Determines in what segment t falls. Gets the point on that segment.
            When you supply the list of segment lengths yourself, as returned from length(path, segmented=True),
            point() works about thirty times faster in a for-loop since it doesn't need to recalculate
            the length during each iteration.
        """
        # Originally from nodebox-gl
        if len(self._elements) == 0:
            raise PathError("The given path is empty")

        if self._segments is None:
            self._segments = self._get_length(segmented=True, precision=10)

        i, t, closeto = self._locate(t, segments=self._segments)
        x0, y0 = self[i].x, self[i].y
        p1 = self[i + 1]
        if p1.cmd == CLOSE:
            x, y = self._linepoint(t, x0, y0, closeto.x, closeto.y)
            return PathElement(LINETO, x, y)
        elif p1.cmd in (LINETO, MOVETO):
            x1, y1 = p1.x, p1.y
            x, y = self._linepoint(t, x0, y0, x1, y1)
            return PathElement(LINETO, x, y)
        elif p1.cmd == CURVETO:
            # Note: the handles need to be interpreted differenty than in a BezierPath.
            # In a BezierPath, ctrl1 is how the curve started, and ctrl2 how it arrives in this point.
            # Here, ctrl1 is how the curve arrives, and ctrl2 how it continues to the next point.
            x3, y3, x1, y1, x2, y2 = p1.x, p1.y, p1.ctrl1.x, p1.ctrl1.y, p1.ctrl2.x, p1.ctrl2.y
            x, y, c1x, c1y, c2x, c2y = self._curvepoint(t, x0, y0, x1, y1, x2, y2, x3, y3)
            return PathElement(CURVETO, c1x, c1y, c2x, c2y, x, y)
        else:
            raise PathError("Unknown cmd '%s' for p1 %s" % (p1.cmd, p1))

    def points(self, amount=100, start=0.0, end=1.0, segments=None):
        """ Returns an iterator with a list of calculated points for the path.
            To omit the last point on closed paths: end=1-1.0/amount
        """
        # Originally from nodebox-gl
        if len(self._elements) == 0:
            raise PathError("The given path is empty")
        n = end - start
        d = n
        if amount > 1:
            # The delta value is divided by amount-1, because we also want the last point (t=1.0)
            # If we don't use amount-1, we fall one point short of the end.
            # If amount=4, we want the point at t 0.0, 0.33, 0.66 and 1.0.
            # If amount=2, we want the point at t 0.0 and 1.0.
            d = float(n) / (amount - 1)
        for i in xrange(int(amount)):
            yield self.point(start + d * i, segments)

    def _linepoint(self, t, x0, y0, x1, y1):
        """ Returns coordinates for point at t on the line.
            Calculates the coordinates of x and y for a point at t on a straight line.
            The t parameter is a number between 0.0 and 1.0,
            x0 and y0 define the starting point of the line,
            x1 and y1 the ending point of the line.
        """
        # Originally from nodebox-gl
        out_x = x0 + t * (x1 - x0)
        out_y = y0 + t * (y1 - y0)
        return (out_x, out_y)

    def _linelength(self, x0, y0, x1, y1):
        """ Returns the length of the line.
        """
        # Originally from nodebox-gl
        a = pow(abs(x0 - x1), 2)
        b = pow(abs(y0 - y1), 2)
        return sqrt(a + b)

    def _curvepoint(self, t, x0, y0, x1, y1, x2, y2, x3, y3, handles=False):
        """ Returns coordinates for point at t on the spline.
            Calculates the coordinates of x and y for a point at t on the cubic bezier spline,
            and its control points, based on the de Casteljau interpolation algorithm.
            The t parameter is a number between 0.0 and 1.0,
            x0 and y0 define the starting point of the spline,
            x1 and y1 its control point,
            x3 and y3 the ending point of the spline,
            x2 and y2 its control point.
            If the handles parameter is set, returns not only the point at t,
            but the modified control points of p0 and p3 should this point split the path as well.
        """
        # Originally from nodebox-gl
        mint = 1 - t
        x01 = x0 * mint + x1 * t
        y01 = y0 * mint + y1 * t
        x12 = x1 * mint + x2 * t
        y12 = y1 * mint + y2 * t
        x23 = x2 * mint + x3 * t
        y23 = y2 * mint + y3 * t
        out_c1x = x01 * mint + x12 * t
        out_c1y = y01 * mint + y12 * t
        out_c2x = x12 * mint + x23 * t
        out_c2y = y12 * mint + y23 * t
        out_x = out_c1x * mint + out_c2x * t
        out_y = out_c1y * mint + out_c2y * t
        if not handles:
            return (out_x, out_y, out_c1x, out_c1y, out_c2x, out_c2y)
        else:
            return (out_x, out_y, out_c1x, out_c1y, out_c2x, out_c2y, x01, y01, x23, y23)

    def _curvelength(self, x0, y0, x1, y1, x2, y2, x3, y3, n=20):
        """ Returns the length of the spline.
            Integrates the estimated length of the cubic bezier spline defined by x0, y0, ... x3, y3,
            by adding the lengths of lineair lines between points at t.
            The number of points is defined by n
            (n=10 would add the lengths of lines between 0.0 and 0.1, between 0.1 and 0.2, and so on).
            The default n=20 is fine for most cases, usually resulting in a deviation of less than 0.01.
        """
        # Originally from nodebox-gl
        length = 0
        xi = x0
        yi = y0
        for i in range(n):
            t = 1.0 * (i + 1) / n
            pt_x, pt_y, pt_c1x, pt_c1y, pt_c2x, pt_c2y = \
                self._curvepoint(t, x0, y0, x1, y1, x2, y2, x3, y3)
            c = sqrt(pow(abs(xi - pt_x), 2) + pow(abs(yi - pt_y), 2))
            length += c
            xi = pt_x
            yi = pt_y
        return length

    def _segment_lengths(self, relative=False, n=20):
        """ Returns a list with the lengths of each segment in the path.
        """
        # From nodebox_gl
        lengths = []
        first = True
        for el in self._get_elements():
            if first is True:
                close_x, close_y = el.x, el.y
                first = False
            elif el.cmd == MOVETO:
                close_x, close_y = el.x, el.y
                lengths.append(0.0)
            elif el.cmd == CLOSE:
                lengths.append(self._linelength(x0, y0, close_x, close_y))
            elif el.cmd == LINETO:
                lengths.append(self._linelength(x0, y0, el.x, el.y))
            elif el.cmd == CURVETO:
                x3, y3, x1, y1, x2, y2 = el.x, el.y, el.c1x, el.c1y, el.c2x, el.c2y
                # (el.c1x, el.c1y, el.c2x, el.c2y, el.x, el.y)
                lengths.append(self._curvelength(x0, y0, x1, y1, x2, y2, x3, y3, n))
            if el.cmd != CLOSE:
                x0 = el.x
                y0 = el.y
        if relative:
            length = sum(lengths)
            try:
                # Relative segment lengths' sum is 1.0.
                return map(lambda l: l / length, lengths)
            except ZeroDivisionError:
                # If the length is zero, just return zero for all segments
                return [0.0] * len(lengths)
        else:
            return lengths

    def _get_length(self, segmented=False, precision=10):
        """ Returns the length of the path.
            Calculates the length of each spline in the path, using n as a number of points to measure.
            When segmented is True, returns a list containing the individual length of each spline
            as values between 0.0 and 1.0, defining the relative length of each spline
            in relation to the total path length.
        """
        # Originally from nodebox-gl
        if not segmented:
            return sum(self._segment_lengths(n=precision), 0.0)
        else:
            return self._segment_lengths(relative=True, n=precision)

    def _get_elements(self):
        '''
        Yields all elements as PathElements
        '''
        for index, el in enumerate(self._elements):
            if isinstance(el, tuple):
                el = PathElement(*el)
                self._elements[index] = el
            yield el

    def extend(self, pathelements):
        self._elements.extend(pathelements)

    def __getitem__(self, item):
        '''
        el is either a PathElement or the parameters to pass
        to one.
        If el is a PathElement return it
        If el is parameters, create a PathElement and return it
        '''
        if isinstance(item, slice):
            indices = item.indices(len(self))
            return [self.__getitem__(i) for i in range(*indices)]
        else:
            el = self._elements[item]
            if isinstance(el, tuple):
                el = PathElement(*el)
                self._elements[item] = el
            return el

    def __iter__(self):
        for index in xrange(len(self._elements)):
            yield self.__getitem__(index)

    def __len__(self):
        return len(self._elements)

    bounds = property(_get_bounds)
    contours = property(_get_contours)
    length = property(_get_length)


class ClippingPath(BezierPath):

    _state_attributes = {'fillcolor', 'strokecolor', 'strokewidth'}

    def __init__(self, bot, path=None, **kwargs):
        BezierPath.__init__(self, bot, **kwargs)
        self._drawn = False
        self._path = path

    def _render_closure(self):
        def render(cairo_ctx):
            # Go to initial point (CORNER or CENTER):
            transform = self._call_transform_mode(self._transform)
            cairo_ctx.set_matrix(transform)

            # Traverse the path
            self._path._traverse(cairo_ctx)
            cairo_ctx.save()
            cairo_ctx.clip()

        return render


class EndClip(Grob):
    def __init__(self, bot, **kwargs):
        Grob.__init__(self, bot)

    def _render_closure(self):
        def render(cairo_ctx):
            cairo_ctx.restore()
        return render

    def draw(self):
        self._deferred_render(self._render_closure())


class CtrlPoint(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


EMPTY_CTRL = CtrlPoint(None, None)


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

    def __init__(self, cmd=None, *args):
        self.cmd = cmd
        if len(args) == 1:
            while len(args) == 1:
                args = args[0]
        self.values = list(chain(args))  # flatten args, so that tuples of (x,y), (x2, y2) are supported
        self._ctrl1 = self._ctrl2 = None

        if cmd == MOVETO or cmd == RMOVETO:
            self.x, self.y = self.values
            self.c1x = self.c1y = self.c2x = self.c2y = None
        elif cmd == LINETO or cmd == RLINETO:
            self.x, self.y = self.values
            self.c1x, self.c1y = self.values  # Possibly should be 0
            self.c2x, self.c2y = self.values  # Possibly should be 0
        elif cmd == CURVETO or cmd == RCURVETO:
            if len(self.values) == 3:
                self.values = list(chain.from_iterable(self.values))
            self.c1x, self.c1y, self.c2x, self.c2y, self.x, self.y = self.values
        elif cmd == CLOSE:
            self.c1x = self.c1y = self.c2x = self.c2y = self.x = self.y = None
        elif cmd == ARC:
            self.x, self.y, self.radius, self.angle1, self.angle2 = self.values
        elif cmd == ELLIPSE:
            # it doesn't feel right having an "ellipse" element, but we need
            # some cairo specific functions to draw it in draw_cairo()
            self.x, self.y, self.w, self.h = self.values
        elif cmd is None:
            self.x = self.y = self.c1x = self.c1y = self.c1x = self.c1y = 0
        else:
            raise ValueError(_('Wrong initialiser for PathElement (got "%s")') % (cmd))

    def set_ctrl1(self, ctrl1):
        self._ctrl1 = ctrl1

    def get_ctrl1(self):
        if self._ctrl1 is None:
            self._ctrl1 = CtrlPoint(self.c1x, self.c1y)
        return self._ctrl1

    def set_ctrl2(self, ctrl2):
        self._ctrl2 = ctrl2

    def get_ctrl2(self):
        if self._ctrl2 is None:
            self._ctrl2 = CtrlPoint(self.c2x, self.c2y)
        return self._ctrl2

    def __getitem__(self, key):
        data = list(self.values)
        data.insert(0, self.cmd)
        return data[key]

    def __repr__(self):
        data = list(self. values)
        data.insert(0, self.cmd)
        return "PathElement" + str(tuple(data))

    def __eq__(self, other):
        if other is None:
            return False
        if self.cmd != other.cmd:
            return False
        if self.values != other.values:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    ctrl1 = property(get_ctrl1, set_ctrl1)
    ctrl2 = property(get_ctrl2, set_ctrl2)


class PathError(Exception):
    # Originally from nodebox-gl
    pass


class NoCurrentPointForPath(Exception):
    # Originally from nodebox-gl
    pass


class NoCurrentPath(Exception):
    # Originally from nodebox-gl
    pass


# --- POINT -------------------------------------------------------------------------------------------

class Point(object):
    # Originally from nodebox-gl
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def _get_xy(self):
        return (self.x, self.y)

    def _set_xy(self, (x, y)):
        self.x = x
        self.y = y

    xy = property(_get_xy, _set_xy)

    def __iter__(self):
        return iter((self.x, self.y))

    def __repr__(self):
        return "Point(x=%.1f, y=%.1f)" % (self.x, self.y)

    def __eq__(self, pt):
        if not isinstance(pt, Point):
            return False
        return self.x == pt.x and self.y == pt.y

    def __ne__(self, pt):
        return not self.__eq__(pt)
