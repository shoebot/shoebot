'''
Shoebot data structures for bezier path handling
'''

from __future__ import division
import util
import cairo

RGB = "rgb"
HSB = "hsb"

MOVETO = "moveto"
RMOVETO = "rmoveto"
LINETO = "lineto"
RLINETO = "rlineto"
CURVETO = "curveto"
RCURVETO = "rcurveto"
ARC = 'arc'
ELLIPSE = 'ellipse'
CLOSE = "close"

DEBUG = False

NUMBER = 1
TEXT = 2
BOOLEAN = 3
BUTTON = 4

CENTER = 'center'
CORNER = 'corner'
CORNERS = 'corners'

_STATE_NAMES = {
    '_outputmode':    'outputmode',
    '_colorrange':    'colorrange',
    '_fillcolor':     'fill',
    '_strokecolor':   'stroke',
    '_strokewidth':   'strokewidth',
    '_transform':     'transform',
    '_transformmode': 'transformmode',
    '_fontname':      'font',
    '_fontsize':      'fontsize',
    '_align':         'align',
    '_lineheight':    'lineheight',
}

class ShoebotError(Exception): pass
class NodeBoxError(ShoebotError): pass

class Point:
    '''
    Taken from Nodebox and modified
    '''
    def __init__(self, *args):
        if len(args) == 3:
            self.x, self.y, self.z = args
        if len(args) == 2:
            self.x, self.y = args
        elif len(args) == 1:
            self.x, self.y = args[0]
        elif len(args) == 0:
            self.x = self.y = 0.0
        else:
            raise ShoebotError, "Wrong initializer for Point object"

    def __repr__(self):
        return (self.x, self.y)
    def __str__(self):
        return "Point(%.3f, %.3f)" % (self.x, self.y)
    def __getitem__(self,key):
        return (float(self.x), float(self.y))[key]
    def __eq__(self, other):
        if other is None: return False
        return self.x == other.x and self.y == other.y
    def __ne__(self, other):
        return not self.__eq__(other)

class Grob(object):
    """A GRaphic OBject is the base class for all DrawingPrimitives."""

    def __init__(self, bot):
        """Initializes this object with the current bot instance."""
        self._bot = bot

    def copy(self):
        """Returns a deep copy of this grob."""
        raise NotImplementedError, "Copy is not implemented on this Grob class."

    def draw(self):
        """Appends the grob to the canvas.
           This will result in a draw later on, when the scene graph is rendered."""
        self._bot.canvas.add(self)
##
##    def inheritFromContext(self, ignore=()):
##        attrs_to_copy = list(self.__class__.stateAttributes)
##        [attrs_to_copy.remove(k) for k, v in _STATE_NAMES.items() if v in ignore]
##        _copy_attrs(self._bot, self, attrs_to_copy)

    def checkKwargs(self, kwargs):
        remaining = [arg for arg in kwargs.keys() if arg not in self.kwargs]
        if remaining:
            raise ShoebotError, "Unknown argument(s) '%s'" % ", ".join(remaining)
    checkKwargs = classmethod(checkKwargs)

def _copy_attr(v):
    if v is None:
        return None
    elif hasattr(v, "copy"):
        return v.copy()
    elif isinstance(v, list):
        return list(v)
    elif isinstance(v, tuple):
        return tuple(v)
    elif isinstance(v, (int, str, unicode, float, bool, long)):
        return v
    else:
        raise NodeBoxError, "Don't know how to copy '%s'." % v

def _copy_attrs(source, target, attrs):
    for attr in attrs:
        setattr(target, attr, _copy_attr(getattr(source, attr)))

class TransformMixin(object):

    """Mixin class for transformation support.
    Adds the _transform and _transformmode attributes to the class."""

    def __init__(self):
        self._reset()

    def _reset(self):
        self._transform = Transform()
        self._transformmode = CENTER

    def _get_transform(self):
        return self._transform
    def _set_transform(self, transform):
        self._transform = Transform(transform)
    transform = property(_get_transform, _set_transform)

    def _get_transformmode(self):
        return self._transformmode
    def _set_transformmode(self, mode):
        self._transformmode = mode
    transformmode = property(_get_transformmode, _set_transformmode)

    def reset(self):
        self._transform = Transform()
    def rotate(self, degrees=0, radians=0):
        self._transform.rotate(degrees,radians)
    def translate(self, x=0, y=0):
        self._transform.translate(x,y)
    def scale(self, x=1, y=None):
        self._transform.scale(x,y)
    def skew(self, x=0, y=0):
        self._transform.skew(x,y)


class ColorMixin(object):

    """Mixin class for color support.
    Adds the _fillcolor, _strokecolor and _strokewidth attributes to the class."""

    def __init__(self, **kwargs):
        try:
            self._fillcolor = Color('rgb', 1, kwargs['fill'])
        except KeyError:
            if self.bot._fillcolor:
                self._fillcolor = self.bot._fillcolor.copy()
            else:
                self._fillcolor = None
        try:
            self._strokecolor = Color('rgb', 1, kwargs['stroke'])
        except KeyError:
            if self.bot._strokecolor:
                self._strokecolor = self.bot._strokecolor.copy()
            else:
                self._strokecolor = None
        self._strokewidth = kwargs.get('strokewidth', 1.0)

    def _get_fill(self):
        return self._fillcolor
    def _set_fill(self, *args):
        self._fillcolor = Color('rgb', 1, *args)
    fill = property(_get_fill, _set_fill)

    def _get_stroke(self):
        return self._strokecolor
    def _set_stroke(self, *args):
        self._strokecolor = Color('rgb', 1, *args)
    stroke = property(_get_stroke, _set_stroke)

    def _get_strokewidth(self):
        return self._strokewidth
    def _set_strokewidth(self, strokewidth):
        self._strokewidth = max(strokewidth, 0.0001)
    strokewidth = property(_get_strokewidth, _set_strokewidth)

class BezierPath(Grob, TransformMixin, ColorMixin):
    """
    Represents a Bezier path as a list of PathElements.

    Shoebot implementation of Nodebox's BezierPath wrapper.
    While Nodebox relies on Cocoa/QT for its data structures,
    this is more of an "agnostic" implementation that won't
    require any other back-ends to do some simple work with paths.
    """

    stateAttributes = ('_fillcolor', '_strokecolor', '_strokewidth', '_transform', '_transformmode')
    kwargs = ('fill', 'stroke', 'strokewidth')

    def __init__(self, bot, path=None, **kwargs):
        self.bot = bot
        super(BezierPath, self).__init__(self.bot)
        TransformMixin.__init__(self)
        ColorMixin.__init__(self, **kwargs)

        # inherit the Bot properties if applicable

        if self.bot:
            _copy_attrs(self.bot, self, self.stateAttributes)

        if path is None:
            self.data = []
        elif isinstance(path, (tuple,list)):
            # list of path elements
            self.data = []
            for element in path:
                self.append(element)
        elif isinstance(path, BezierPath):
            self.data = path.data
            _copy_attrs(path, self, self.stateAttributes)
        elif isinstance(path, basestring):
            self.data = svg2pathdata(path)
        else:
            raise ShoebotError, "Don't know what to do with %s." % path
        self.closed = False

    def copy(self):
        return self.__class__(self.bot, self)

    ### Path methods ###

    def moveto(self, x, y):
        self.data.append(PathElement(MOVETO, x, y))
    def lineto(self, x, y):
        self.data.append(PathElement(LINETO, x, y))
    def curveto(self, c1x, c1y, c2x, c2y, x, y):
        self.data.append(PathElement(CURVETO, c1x, c1y, c2x, c2y, x, y))
    def relmoveto(self, x, y):
        self.data.append(PathElement(RMOVETO, x, y))
    def rellineto(self, x, y):
        self.data.append(PathElement(RLINETO, x, y))
    def relcurveto(self, c1x, c1y, c2x, c2y, x, y):
        self.data.append(PathElement(RCURVETO, c1x, c1y, c2x, c2y, x, y))
    def arc(self, x, y, radius, angle1, angle2):
        self.data.append(PathElement(ARC, x, y, radius, angle1, angle2))
    def closepath(self):
        self.data.append(PathElement(CLOSE))
        self.closed = True
    def ellipse(self,x,y,w,h):
        self.data.append(PathElement(ELLIPSE,x,y,w,h))
        self.closepath()
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

    def __getitem__(self, index):
        return self.data[index]
    def __iter__(self):
        for i in range(len(self.data)):
            yield self.data[i]
    def __len__(self):
        return len(self.data)

    def append(self, el):
        '''
        Wrapper method for hiding the data var
        from public access
        '''
        # parsepathdata()
        if isinstance(el, PathElement):
            self.data.append(el)
        else:
            raise TypeError("Wrong data passed to BezierPath.append(): %s" % el)

    def _get_bounds(self):
        '''Returns the path's bounding box. Note that this doesn't
        take transforms into account.'''
        # we don't have any direct way to calculate bbox from a path, but Cairo
        # does! So we make a new cairo context to calculate path bounds
        from shoebot import CairoCanvas
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100,100)
        ctx = cairo.Context(surface)
        canvas = CairoCanvas(target=ctx)
        p = self.copy()
##        ctx.transform(p._transform._matrix)


        # pass path to temporary context
        for element in p.data:
            cmd = element[0]
            values = element[1:]

            # apply cairo context commands
            if cmd == MOVETO:
                ctx.move_to(*values)
            elif cmd == LINETO:
                ctx.line_to(*values)
            elif cmd == CURVETO:
                ctx.curve_to(*values)
            elif cmd == RLINETO:
                ctx.rel_line_to(*values)
            elif cmd == RCURVETO:
                ctx.rel_curve_to(*values)
            elif cmd == CLOSE:
                ctx.close_path()
            elif cmd == ELLIPSE:
                from math import pi
                x, y, w, h = values
                ctx.save()
                ctx.translate (x + w / 2., y + h / 2.)
                ctx.scale (w / 2., h / 2.)
                ctx.arc (0., 0., 1., 0., 2 * pi)
                ctx.restore()
        # get boundaries
        bbox = ctx.fill_extents()
        del surface, ctx, canvas, p
        return bbox
    bounds = property(_get_bounds)

    def _get_center(self):
        '''Returns the center point of the path, disregarding transforms.
        '''
        (x1,y1,x2,y2) = self.bounds
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        return (x,y)
    center = property(_get_center)

    def _get_abs_center(self):
        '''Returns the centerpoint of the path, taking transforms into account.
        '''
        (rel_x, rel_y) = self._get_center()
        m = self._transform.copy()._matrix
        return m.transform_point(rel_x, rel_y)

    def _get_transform(self):
        trans = self._transform.copy()
        if (self._transformmode == CENTER):
            deltax, deltay = self._get_center()
            t = Transform()
            t.translate(-deltax,-deltay)
            trans = t * trans
            t = Transform()
            t.translate(deltax,deltay)
            trans *= t
        return trans
    transform = property(_get_transform)

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
            self.c1x, self.c1y, self.c2x,self.c2y, self.x, self.y = self.values
        elif cmd == CLOSE:
            self.x = self.y = self.c1x = self.c1y = self.c2x = self.c2y = None
        elif cmd == ARC:
            self.x, self.y, self.radius, self.angle1, self.angle2 = self.values
        elif cmd == ELLIPSE:
            # it doesn't feel right having an "ellipse" element, but we need
            # some cairo specific functions to draw it in draw_cairo()
            self.x, self.y, self.w, self.h = self.values
        else:
            raise ShoebotError('Wrong initialiser for PathElement (got "%s")' % (cmd))

    def __getitem__(self,key):
        data = list(self.values)
        data.insert(0, self.cmd)
        return data[key]
    def __repr__(self):
        data = list(self.values)
        data.insert(0, self.cmd)
        return "PathElement" + str(tuple(data))
    def __eq__(self, other):
        if other is None: return False
        if self.cmd != other.cmd: return False
        if self.values != other.values: return False
        return True
    def __ne__(self, other):
        return not self.__eq__(other)

class Color(object):
    '''
    Taken from Nodebox and modified.
    Since we have no Cocoa, we have no way to use colour management for the moment.
    So we took another approach.

    Attributes:
    r, g, b (0-1)
    hue, saturation, lightness (0-1)

    This stores color values as a list of 4 floats (RGBA) in a 0-1 range.

    The value can come in the following flavours:
    - v
    - (v)
    - (v,a)
    - (r,g,b)
    - (r,g,b,a)
    - #RRGGBB
    - RRGGBB
    - #RRGGBBAA
    - RRGGBBAA
    '''

    def __init__(self, mode='rgb', color_range=1, *v):
        # unpack one-element tuples, they show up sometimes
        while isinstance(v, (tuple,list)) and len(v) == 1:
            v = v[0]

        if not v:
            raise ShoebotError("got Color() with no values!")
            self.r, self.g, self.b, self.a = (0,0,0,1)

        if isinstance(v, Color):
            self.r, self.g, self.b, self.a = v

        else:
            if mode is RGB:
                self.r, self.g, self.b, self.a = util.parse_color(v, color_range)
            elif mode is HSB:
                self.r, self.g, self.b, self.a = util.parse_hsb_color(v, color_range)

        # convenience attributes
        self.red = self.r
        self.green = self.g
        self.blue = self.b
        self.alpha = self.a

        self.data = [self.r, self.g, self.b, self.a]

        self.hue, self.saturation, self.lightness = util.rgb_to_hsl(self.r, self.g, self.b)

    def __getitem__(self, index):
        return (self.r, self.g, self.b, self.a)[index]
    def __iter__(self):
        for i in range(len(self.data)):
            yield self.data[i]
    def __repr__(self):
        return "(%f,%f,%f,%f)" % (self.r, self.g, self.b, self.a)
    def __div__(self, other):
        value = float(other)
        return (self.red/value, self.green/value, self.blue/value, self.alpha/value)

    def blend(self,other,factor):
        self.r = (self.r + other.r) / factor
        self.g = (self.g + other.g) / factor
        self.b = (self.b + other.b) / factor
        self.a = (self.a + other.a) / factor
    def copy(self):
        new = self.__class__('rgb',1,self.data)
        return new

class Text:
    stateAttributes = ('_transform', '_transformmode', '_fillcolor', '_fontfile', '_fontsize', '_align', '_lineheight')
    kwargs = ('fill', 'font', 'fontsize', 'align', 'lineheight')

    def __init__(self, bot, text, x=0, y=0, width=None, height=None, **kwargs):
        self._bot = bot
        super(Text, self).__init__(self._bot)
        TransformMixin.__init__(self)
        ColorMixin.__init__(self, **kwargs)
        self.text = unicode(text)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self._fontname = kwargs.get('font', "~/.fonts/notcouriersans.ttf")
        self._fontsize = kwargs.get('fontsize', 24)
        self._lineheight = max(kwargs.get('lineheight', 1.2), 0.01)
        self._align = kwargs.get('align', LEFT)

    def _get_cairo_font(self):
        return util.create_cairo_font_face_for_file(fontpath, 0)
    cairo_font = property(_get_cairo_font)

    def _get_metrics(self):
        surface = cairo.Surface(cairo.FORMAT_A8, 100, 100)
        ctx = cairo.Context(surface)
        face = util.create_cairo_font_face_for_file(self._fontfile, 0)
        ctx.set_font_face(face)
        e = ctx.text_extents(self.text)
        return (e.xbearing, e.ybearing, e.width, e.height, e.x_advance, e.y_advance)
    metrics = property(_get_metrics)

    def copy(self):
        new = self.__class__(self._bot, self.text)
        _copy_attrs(self, new,
            ('x', 'y', 'width', 'height', '_transform', '_transformmode',
            '_fillcolor', '_fontfile', '_fontsize', '_align', '_lineheight'))
        return new

class Variable(object):
    '''Taken from Nodebox'''
    def __init__(self, name, type, default=None, min=0, max=100, value=None):
        self.name = name
        self.type = type or NUMBER
        if self.type == NUMBER:
            if default is None:
                self.default = 50
            else:
                self.default = default
            self.min = min
            self.max = max
        elif self.type == TEXT:
            if default is None:
                self.default = "bonjour"
            else:
                self.default = default
        elif self.type == BOOLEAN:
            if default is None:
                self.default = True
            else:
                self.default = default
        elif self.type == BUTTON:
            self.default = self.name
        self.value = value or self.default

    def sanitize(self, val):
        """Given a Variable and a value, cleans it out"""
        if self.type == NUMBER:
            try:
                return float(val)
            except ValueError:
                return 0.0
        elif self.type == TEXT:
            try:
                return unicode(str(val), "utf_8", "replace")
            except:
                return ""
        elif self.type == BOOLEAN:
            if unicode(val).lower() in ("true", "1", "yes"):
                return True
            else:
                return False

    def compliesTo(self, v):
        """Return whether I am compatible with the given var:
             - Type should be the same
             - My value should be inside the given vars' min/max range.
        """
        if self.type == v.type:
            if self.type == NUMBER:
                if self.value < self.min or self.value > self.max:
                    return False
            return True
        return False

    def __repr__(self):
        return "Variable(name=%s, type=%s, default=%s, min=%s, max=%s, value=%s)" % (self.name, self.type, self.default, self.min, self.max, self.value)

TRANSFORMS = ['translate', 'scale', 'rotate', 'skew', 'cscale', 'crotate',
              'cskew']

class Transform:
    '''
    This class represents a stack of transformations. Supported operations are
    translation, scaling, rotation and skewing.

    '''
    def __init__(self, transform=None):
        self.stack = []
        if transform is None:
            pass
        elif isinstance(transform, Transform):
            self.append(transform)
        elif isinstance(transform, (list, tuple)):
            matrix = tuple(transform)
            t = cairo.Matrix(*matrix)
            self.append(t)
        elif isinstance(transform, cairo.Matrix):
            self.append(transform)
        else:
            raise ShoebotError, "Transform: Don't know how to handle transform %s." % transform

    def translate(self, x, y):
        t = ('translate', x, y)
        self.stack.append(t)
    def scale(self, x, y):
        t = ('scale', x, y)
        self.stack.append(t)
    def rotate(self, a):
        t = ('rotate', a)
        self.stack.append(t)
    def skew(self, x, y):
        t = ('skew', x, y)
        self.stack.append(t)
    def cscale(self, x, y):
        t = ('cscale', x, y)
        self.stack.append(t)
    def crotate(self, a):
        t = ('crotate', a)
        self.stack.append(t)
    def cskew(self, x, y):
        t = ('cskew', x, y)
        self.stack.append(t)

    def append(self, t):
        if isinstance(t, Transform):
            for item in t.stack:
                self.stack.append(item)
        elif isinstance(t, cairo.Matrix):
            self.stack.append(t)
        else:
            raise ShoebotError("Transform: Can only append Transforms or Cairo matrices (got %s)" % (t))

    def prepend(self,t):
        if isinstance(t, Transform):
            newstack = []
            for item in t.stack:
                newstack.append(item)
            for item in self.stack:
                newstack.append(item)
            self.stack = newstack
        elif isinstance(t, cairo.Matrix):
            self.stack.insert(0,t)
        else:
            raise ShoebotError("Transform: Can only append Transforms or Cairo matrices (got %s)" % (t))

    def copy(self):
        return self.__class__(self)
    def __iter__(self):
        for value in self.stack:
            yield value

    def get_matrix(self):
        '''Returns this transform's matrix. Its centerpoint is presumed to be
        (0,0), which is the Cairo default.'''
        return self.get_matrix_with_center(0,0)

    def get_matrix_with_center(self,x,y):
        '''Returns this transform's matrix, relative to a centerpoint (x,y).'''
        m = cairo.Matrix()

        centerx = x
        centery = y

        for trans in self.stack:
            if isinstance(trans, cairo.Matrix):
                # multiply matrix
                m *= trans
            elif isinstance(trans, tuple) and trans[0] in TRANSFORMS:
                # parse transform command
                cmd = trans[0]
                args = trans[1:]
                t = cairo.Matrix()

                if cmd == 'translate':
                    t.translate(args[0],args[1])
                    m *= t
                elif cmd == 'rotate':
                    t.rotate(args[0])
                    m *= t
                elif cmd == 'scale':
                    t.scale(args[0], args[1])
                    m *= t
                elif cmd == 'skew':
                    x, y = args
                    ## TODO: x and y should be the tangent of an angle
                    t *= cairo.Matrix(1,0,x,1,0,0)
                    t *= cairo.Matrix(1,y,0,1,0,0)
                    m *= t
                elif cmd == 'cscale':
                    # apply existing transform to centerpoint
                    deltax,deltay = m.transform_point(centerx,centery)
                    x, y = args

                    m1 = cairo.Matrix()
                    m2 = cairo.Matrix()
                    m1.translate(-deltax, -deltay)
                    m2.translate(deltax, deltay)

                    m *= m1
                    m *= cairo.Matrix(x,0,0,y,0,0)
                    m *= m2
                elif cmd == 'crotate':
                    from math import sin, cos
                    # apply existing transform to centerpoint
                    deltax,deltay = m.transform_point(centerx,centery)
                    a = args[0]
                    m1 = cairo.Matrix()
                    m2 = cairo.Matrix()
                    m1.translate(-deltax, -deltay)
                    m2.translate(deltax, deltay)
                    # transform centerpoint according to current matrix
                    m *= m1
                    m *= cairo.Matrix(cos(a), sin(a), -sin(a), cos(a),0,0)
                    m *= m2

                elif cmd == 'cskew':
                    # apply existing transform to centerpoint
                    deltax,deltay = m.transform_point(centerx,centery)
                    x,y = args

                    m1 = cairo.Matrix()
                    m2 = cairo.Matrix()
                    m1.translate(-deltax, -deltay)
                    m2.translate(deltax, deltay)
                    t *= m
                    t *= m1
                    t *= cairo.Matrix(1,0,x,1,0,0)
                    t *= cairo.Matrix(1,y,0,1,0,0)
                    t *= m2
                    m = t
        return m

class Stack(list):
    def __init__(self):
        list.__init__(self)

    def push(self, item):
        self.insert(0, item)

    def pop(self):
        del self[0]

    def get(self):
        return self[0]

def lexPath(d):
	"""
	returns an iterator that breaks path data
	identifies command and parameter tokens
	"""
	import re

	offset = 0
	length = len(d)
	delim = re.compile(r'[ \t\r\n,]+')
	command = re.compile(r'[MLHVCSQTAZmlhvcsqtaz]')
	parameter = re.compile(r'(([-+]?[0-9]+(\.[0-9]*)?|[-+]?\.[0-9]+)([eE][-+]?[0-9]+)?)')
	while 1:
		m = delim.match(d, offset)
		if m:
			offset = m.end()
		if offset >= length:
			break
		m = command.match(d, offset)
		if m:
			yield [d[offset:m.end()], True]
			offset = m.end()
			continue
		m = parameter.match(d, offset)
		if m:
			yield [d[offset:m.end()], False]
			offset = m.end()
			continue
		#TODO: create new exception
		raise Exception, 'Invalid path data!'
'''
While I am less pleased with my parsing function, I think it works. And that is important. There will be time for improvement later.
'''

'''
pathdefs = {commandfamily:
	[
	implicitnext,
	#params,
	[casts,cast,cast],
	[coord type,x,y,0]
	]}
'''

pathdefs = {
	'M':['L', 2, [float, float], ['x','y']],
	'L':['L', 2, [float, float], ['x','y']],
	'H':['H', 1, [float], ['x']],
	'V':['V', 1, [float], ['y']],
	'C':['C', 6, [float, float, float, float, float, float], ['x','y','x','y','x','y']],
	'S':['S', 4, [float, float, float, float], ['x','y','x','y']],
	'Q':['Q', 4, [float, float, float, float], ['x','y','x','y']],
	'T':['T', 2, [float, float], ['x','y']],
	'A':['A', 7, [float, float, float, int, int, float, float], [0,0,0,0,0,'x','y']],
	'Z':['L', 0, [], []]
	}

def parsePath(d):
	"""
	Parse SVG path and return an array of segments.
	Removes all shorthand notation.
	Converts coordinates to absolute.
	"""
	retval = []
	lexer = lexPath(d)

	pen = (0.0,0.0)
	subPathStart = pen
	lastControl = pen
	lastCommand = ''

	while 1:
		try:
			token, isCommand = lexer.next()
		except StopIteration:
			break
		params = []
		needParam = True
		if isCommand:
			if not lastCommand and token.upper() != 'M':
				raise Exception, 'Invalid path, must begin with moveto.'
			else:
				command = token
		else:
			#command was omited
			#use last command's implicit next command
			needParam = False
			if lastCommand:
				if token.isupper():
					command = pathdefs[lastCommand.upper()][0]
				else:
					command = pathdefs[lastCommand.upper()][0].lower()
			else:
				raise Exception, 'Invalid path, no initial command.'
		numParams = pathdefs[command.upper()][1]
		while numParams > 0:
			if needParam:
				try:
					token, isCommand = lexer.next()
					if isCommand:
						raise Exception, 'Invalid number of parameters'
				except StopIteration:
						raise Exception, 'Unexpected end of path'
			cast = pathdefs[command.upper()][2][-numParams]
			param = cast(token)
			if command.islower():
				if pathdefs[command.upper()][3][-numParams]=='x':
					param += pen[0]
				elif pathdefs[command.upper()][3][-numParams]=='y':
					param += pen[1]
			params.append(param)
			needParam = True
			numParams -= 1
		#segment is now absolute so
		outputCommand = command.upper()

		#Flesh out shortcut notation
		if outputCommand in ('H','V'):
			if outputCommand == 'H':
				params.append(pen[1])
			if outputCommand == 'V':
				params.insert(0,pen[0])
			outputCommand = 'L'
		if outputCommand in ('S','T'):
			params.insert(0,pen[1]+(pen[1]-lastControl[1]))
			params.insert(0,pen[0]+(pen[0]-lastControl[0]))
			if outputCommand == 'S':
				outputCommand = 'C'
			if outputCommand == 'T':
				outputCommand = 'Q'

		#current values become "last" values
		if outputCommand == 'M':
			subPathStart = tuple(params[0:2])
		if outputCommand == 'Z':
			pen = subPathStart
		else:
			pen = tuple(params[-2:])

		if outputCommand in ('Q','C'):
			lastControl = tuple(params[-4:-2])
		else:
			lastControl = pen
		lastCommand = command

		retval.append([outputCommand,params])
	return retval


def test_color():
    # this test checks with a 4 decimal point precision

    testvalues = {
        128: (0.501961,0.501961,0.501961,1.000000),
        (127,): (0.498039, 0.498039, 0.498039, 0.498039),
        (127, 64): (0.498039, 0.498039, 0.498039, 0.250979),
        (0, 127, 255): (0.0, 0.498039, 1.0, 1.0),
        (0, 127, 255, 64): (0.0, 0.498039, 1.0, 0.250979),
        '#0000FF': (0.000000,0.000000,1.000000,1.000000),
        '0000FF': (0.000000,0.000000,1.000000,1.000000),
        '#0000FFFF': (0.000000,0.000000,1.000000,1.000000),
        '000000ff': (0.000000,0.000000,0.000000,1.000000),
        }

    passed = True
    for value in testvalues:
        result = Color(value, color_range = 255)
        # print "%s = %s (%s, %s)" % (str(value), str(result), str(result.color_range), str(result.color_mode))
        equal = True
        for index in range(0,4):
            # check if difference is bigger than 0.0001, since floats
            # are tricky things and behave a bit weird when comparing directly
            if result[index] != 0. and testvalues[value][index] != 0.:
                if not 0.9999 < result[index] / testvalues[value][index] < 1.0001:
                    print result[index] / testvalues[value][index]
                    equal = False
        if not equal:
            print "Test Error:"
            print "  Value:      %s" % (str(value))
            print "  Expected:   %s" % (str(testvalues[value]))
            print "  Received:   %s" % (str(result))
            passed = False
    if passed:
        print "All color tests passed!"

if __name__ == '__main__':
    test_color()





