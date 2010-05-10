import sys, locale, gettext
from shoebot.data import _copy_attrs
from shoebot.data import Grob, ColorMixin, TransformMixin
from math import pi as _pi

CENTER = 'center'

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
    def __init__(self, canvas, fill=None, stroke=None):
        # Internally stores two lists
        #
        # _render_funcs  References to functions to render each PathElement
        # _elements      Items start as tuples, but if a PathElement is
        #                requested then it is stored there.
        Grob.__init__(self)
        self._drawqueue = canvas.drawqueue
        self._canvas = canvas

        self._render_funcs = []
        self._elements = []
        self._fill = fill
        self._stroke = stroke
        self.closed = False

        self._set_mode(canvas.mode)
        self._drawn = False
        self._center = None

    def _append_element(self, render_func, element):
        '''
        Append an element to the list

        element is either a tuple containing arguments
        to pass to a PathElement or an actual PathElement
        '''
        self._render_funcs.append(render_func)
        self._elements.append(element)

    def _set_mode(self, mode):
        '''
        Sets call_transform_mode to point to the
        center_transform or corner_transform
        '''
        if mode == CENTER:
            self._call_transform_mode = self._center_transform
        elif mode == CORNER:
            self._call_transform_mode = self._corner_transform
        else:
            raise ValueError('mode must be CENTER or CORNER')

    def moveto(self, x, y):
        def render_moveto(ctx):
            ctx.move_to(x, y)
        self._append_element(render_moveto, (MOVETO, x, y))

    def lineto(self, x, y):
        def render(ctx):
            ctx.line_to(x, y)
        self._append_element(render, (LINETO, x, y))

    def curveto(self, x1, y1, x2, y2, x3, y3):
        def render(ctx):
            ctx.curve_to(x1, y1, x2, y2, x3, y3)
        self._append_element(render, (CURVETO, x1, y1, x2, y2, x3, y3))

    def closepath(self):
        def render_closepath(ctx):
            ctx.close_path()
        self._append_element(render_closepath, (CLOSE))
        self.closed = True

    def ellipse(self, x, y, w, h):
        def render_ellipse(ctx):
            ctx.translate(x + w / 2., y + h / 2.)
            ctx.scale(w / 2., h / 2.)
            ctx.arc(0., 0., 1., 0., 2 * _pi)
            ctx.close_path()
            
        self._append_element(render_ellipse, (ELLIPSE, x, y, w, h)) 

        self.closed = True

    def rellineto(self, x, y):
        def render_rellineto(ctx):
            ctx.rel_line_to(x, y)
        self._append_element(render_rellineto, (RLINETO, x, y))

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
    
    def _traverse(self, ctx):
        '''
        Traverse this path
        
        ### TODO - Investigate if Path should be a DrawQueue once
        it's more fully formed
        '''
        ##(render_func() for render_func in self._render_funcs)

        for render_func in self._render_funcs:
            render_func(ctx)

    def _call_transform_mode(self):
        '''
        This should never get called:
        set mode, changes the value of this to point

        corner_transform or center_transform
        '''
        raise Error('_call_transform_mode called without mode set!')

    def _get_center(self):
        '''
        Return cached bounds of this Grob.
        If bounds are not cached, render to a meta surface, and
        keep the meta surface and bounds cached.
        '''
        if self._center:
            return self._center

        # Cairo 1.10 Will have RecordingSurfaces, in the meantime we
        # can make use of a PDFSurface
        #
        meta_surface = RecordingSurface(*self._canvas.size)
        dummy_ctx = cairo.Context(meta_surface)
        self._traverse(dummy_ctx)
        
        #bounds = dummy_ctx.stroke_extents()
        bounds = dummy_ctx.path_extents()
        
        # get the center point
        (x1,y1,x2,y2) = bounds
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2

        center = self._center = x, y
        ### TODO Cache function that draws using the RecordingSurface
        ### Save the context or surface (without the bounding box stroke)
        ### to optimise drawing
        return center

    def _center_transform(self, transform):
        ''''
        Works like setupTransform of a version of java nodebox
        http://dev.nodebox.net/browser/nodebox-java/branches/rewrite/src/java/net/nodebox/graphics/Grob.java
        '''
        dx, dy = self._get_center()
        t = cairo.Matrix()
        t.translate(dx, dy)
        t = transform * t
        t.translate(-dx, -dy)
        return t

    def _corner_transform(self, transform):
        '''
        CENTER is the default, so we just return the transform
        '''
        return transform

    def _render(self, ctx):
        transform = self._call_transform_mode(self._transform)
        ctx.set_matrix(transform)
        self._traverse(ctx)
        
        if self._fill:
            ctx.set_source_rgb(*self._fill)
            if self._stroke:
                ctx.fill_preserve()
            else:
                ctx.fill()
        if self._stroke:
            ctx.set_source_rgb(*self._stroke)
            ctx.stroke()

    def draw(self):
        '''
        Save the current fill, stroke and transform
        then add the render function to the draw queue
        '''
        self._fill = self._fill or self._canvas.fill
        self._stroke = self._stroke or self._canvas.stroke
        self._strokewidth = self._canvas.strokewidth
        self._transform = cairo.Matrix(*self._canvas.transform)
        self._drawqueue.append(self._render)

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
    
    # stateAttributes = ('_fillcolor', '_strokecolor', '_strokewidth')
    # kwargs = ('fill', 'stroke', 'strokewidth')    
    
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

