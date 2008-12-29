'''
Shoebot data structures for bezier path handling
'''

from __future__ import division
import util
import cairo
import pango
import pangocairo


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

LEFT = 'left'
RIGHT = 'right'
JUSTIFY = 'justify'

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
            self._fillcolor = Color(kwargs['fill'], mode='rgb', color_range=1)
        except KeyError:
            if self._bot._fillcolor:
                self._fillcolor = self._bot._fillcolor.copy()
            else:
                self._fillcolor = None
        try:
            self._strokecolor = Color(kwargs['stroke'], mode='rgb', color_range=1)
        except KeyError:
            if self._bot._strokecolor:
                self._strokecolor = self._bot._strokecolor.copy()
            else:
                self._strokecolor = None
        self._strokewidth = kwargs.get('strokewidth', 1.0)

    def _get_fill(self):
        return self._fillcolor
    def _set_fill(self, *args):
        self._fillcolor = Color(mode='rgb', color_range=1, *args)
    fill = property(_get_fill, _set_fill)

    def _get_stroke(self):
        return self._strokecolor
    def _set_stroke(self, *args):
        self._strokecolor = Color(mode='rgb', color_range=1, *args)
    stroke = property(_get_stroke, _set_stroke)

    def _get_strokewidth(self):
        return self._strokewidth
    def _set_strokewidth(self, strokewidth):
        self._strokewidth = max(strokewidth, 0.0001)
    strokewidth = property(_get_strokewidth, _set_strokewidth)

class RestoreCtx(Grob):

    def __init__(self, bot, **kwargs):
        self._bot = bot

class BezierPath(Grob, TransformMixin, ColorMixin):
    """
    Represents a Bezier path as a list of PathElements.

    Shoebot implementation of Nodebox's BezierPath wrapper.
    While Nodebox relies on Cocoa/QT for its data structures,
    this is more of an "agnostic" implementation that won't
    require any other back-ends to do some simple work with paths.

    (this last sentence is not so correct: we use a bit of Cairo
    for getting path dimensions)
    """

    stateAttributes = ('_fillcolor', '_strokecolor', '_strokewidth', '_transform', '_transformmode')
    kwargs = ('fill', 'stroke', 'strokewidth')

    def __init__(self, bot, path=None, **kwargs):
        self._bot = bot
        #self._counter=len(self._bot._transform.stack)
        super(BezierPath, self).__init__(self._bot)
        TransformMixin.__init__(self)
        ColorMixin.__init__(self, **kwargs)

        # inherit the Bot properties if applicable

        if self._bot:
            _copy_attrs(self._bot, self, self.stateAttributes)

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
        #return self.__class__(self._bot, self)
	p = self.__class__(self._bot, self)
	_copy_attrs(self._bot, p, self.stateAttributes)
	return p

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

    ## alternative ellipse implementation, more consistent with nodebox primitives
    #def ellipse(self,x,y,w,h):
        #k = 0.5522847498    
        #self.moveto(x,y+h/2)
        #self.curveto(x,y+(1-k)*h/2,x+(1-k)*w/2,y,x+w/2,y)
        #self.curveto(x+(1+k)*w/2,y,x+w,y+(1-k)*h/2,x+w,y+h/2)
        #self.curveto(x+w,y+(1+k)*h/2,x+(1+k)*w/2,y+h,x+w/2,y+h)
        #self.curveto(x+(1-k)*w/2,y+h,x,y+(1+k)*h/2,x,y+h/2)
        #self.closepath()

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
        bbox = ctx.stroke_extents()
        # is this line necessary? Or does python garbage collect this?
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

class ClippingPath(BezierPath):
    
    stateAttributes = ('_fillcolor', '_strokecolor', '_strokewidth', '_transform', '_transformmode')
    kwargs = ('fill', 'stroke', 'strokewidth')    
    
    def __init__(self, bot, path=None, **kwargs):
        BezierPath.__init__(self, bot, path, **kwargs)

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
    Taken from Nodebox colors library and modified.
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
    
    The CMYK parts have been commented out, as it may slow down code execution
    and at this point is quite useless, left it in place for a possible future implementation
    '''

    def __init__(self, *a, **kwargs):
        
        # Values are supplied as a tuple.
        if len(a) == 1 and isinstance(a[0], tuple):
            a = a[0]
            
        # No values or None, transparent black.
        if len(a) == 0 or (len(a) == 1 and a[0] == None):
            raise ShoebotError("got Color() with value None!")         
            self.r, self.g, self.b, self.a = 0, 0, 0, 0
            
        # One value, another color object.
        elif len(a) == 1 and isinstance(a[0], Color):
            self.r, self.g, self.b, self.a = a[0].r, a[0].g, a[0].b, a[0].a
            
        # One value, a hexadecimal string.
        elif len(a) == 1 and isinstance(a[0], str):
            r, g, b, a = util.hex2rgb(a[0])
            self.r, self.g, self.b, self.a = r, g, b, a
            
        # One value, grayscale.
        elif len(a) == 1:
            if kwargs.has_key("color_range"):
                ra = int(kwargs["color_range"])
            else:
                ra = 1
            self.r, self.g, self.b, self.a = a[0]/ra, a[0]/ra, a[0]/ra, 1
            
        # Two values, grayscale and alpha.
        elif len(a) == 2:
            if kwargs.has_key("color_range"):
                ra = int(kwargs["color_range"])
            else:
                ra = 1
            self.r, self.g, self.b, self.a = a[0]/ra, a[0]/ra, a[0]/ra, a[1]/ra
            
        # Three to five parameters, either RGB, RGBA, HSB, HSBA, CMYK, CMYKA
        # depending on the mode parameter.
        elif len(a) >= 3:
            if kwargs.has_key("color_range"):
                ra = int(kwargs["color_range"])
            else:
                ra = 1            
            alpha, mode = 1, "rgb" 
            if len(a) > 3: alpha = a[-1]/ra
	    
            if kwargs.has_key("mode"): 
                mode = kwargs["mode"].lower()
            if mode == "rgb":                
                self.r, self.g, self.b, self.a = a[0]/ra, a[1]/ra, a[2]/ra, alpha               
            elif mode == "hsb":                
                self.h, self.s, self.brightness, self.a = a[0]/ra, a[1]/ra, a[2]/ra, alpha                
            #elif mode == "cmyk":
                #if len(a) == 4: alpha = 1
                #self.a = alpha
                #self.c, self.m, self.y, self.k = a[0], a[1], a[2], a[3]
	    

        # Added this
        self.red = self.r
        self.green = self.g
        self.blue = self.b
        self.alpha = self.a

        self.data = [self.r, self.g, self.b, self.a]
        #end added



    def __repr__(self):
        return "%s(%.3f, %.3f, %.3f, %.3f)" % (self.__class__.__name__, 
            self.red, self.green, self.blue, self.alpha)

    def copy(self):
	return tuple(self.data)
        
    def _update_rgb(self, r, g, b):
        self.__dict__["__r"] = r
        self.__dict__["__g"] = g
        self.__dict__["__b"] = b
    
    #def _update_cmyk(self, c, m, y, k):
        #self.__dict__["__c"] = c
        #self.__dict__["__m"] = m
        #self.__dict__["__y"] = y
        #self.__dict__["__k"] = k
        
    def _update_hsb(self, h, s, b):
        self.__dict__["__h"] = h
        self.__dict__["__s"] = s
        self.__dict__["__brightness"] = b
    
    def _hasattrs(self, list):
        for a in list:
            if not self.__dict__.has_key(a):
                return False
        return True
    
    #added
    def __getitem__(self, index):
        return (self.r, self.g, self.b, self.a)[index]
        

    def __iter__(self):
        for i in range(len(self.data)):
           yield self.data[i]

    def __div__(self, other):
        value = float(other)
        return (self.red/value, self.green/value, self.blue/value, self.alpha/value)    
    #end added


    def __setattr__(self, a, v):
        
        if a in ["a", "alpha"]:
            self.__dict__["__"+a[0]] = max(0, min(v, 1))
        
        # RGB changes, update CMYK and HSB accordingly.
        elif a in ["r", "g", "b", "red", "green", "blue"]:
            self.__dict__["__"+a[0]] = max(0, min(v, 1))
            if self._hasattrs(("__r", "__g", "__b")):
                r, g, b = (
                    self.__dict__["__r"], 
                    self.__dict__["__g"], 
                    self.__dict__["__b"]
                )
                #self._update_cmyk(*util.rgb2cmyk(r, g, b))
                self._update_hsb(*util.rgb2hsb(r, g, b))
        
        # HSB changes, update RGB and CMYK accordingly.
        elif a in ["h", "s", "hue", "saturation", "brightness"]:
            if a != "brightness": a = a[0]
            if a == "h": v = min(v, 0.99999999)
            self.__dict__["__"+a] = max(0, min(v, 1))
            if self._hasattrs(("__h", "__s", "__brightness")):
                r, g, b = util.hsb2rgb(
                    self.__dict__["__h"], 
                    self.__dict__["__s"], 
                    self.__dict__["__brightness"]
                )
                self._update_rgb(r, g, b)
                #self._update_cmyk(*util.rgb2cmyk(r, g, b))
        
        # CMYK changes, update RGB and HSB accordingly.
        #elif a in ["c", "m", "y", "k", "cyan", "magenta", "yellow", "black"]:
            #if a != "black": a = a[0]
            #self.__dict__["__"+a] = max(0, min(v, 1))
            #if self._hasattrs(("__c", "__m", "__y", "__k")):
                #r, g, b = util.cmyk2rgb(
                    #self.__dict__["__c"], 
                    #self.__dict__["__m"], 
                    #self.__dict__["__y"], 
                    #self.__dict__["__k"]
                #)
                #self._update_rgb(r, g, b)
                #self._update_hsb(*util.rgb2hsb(r, g, b))
                
        else:
            self.__dict__[a] = v

    def __getattr__(self, a):
        
        """ Available properties:
        r, g, b, a or red, green, blue, alpha
        c, m, y, k or cyan, magenta, yellow, black,
        h, s or hue, saturation, brightness
        
        """
        
        if self.__dict__.has_key(a):
            return a
        #elif a == "black":
            #return self.__dict__["__k"]        
        elif a == "brightness":
            return self.__dict__["__brightness"]
        #CMYK
        #elif a in ["a", "alpha",
                   #"r", "g", "b", "red", "green", "blue",
                   #"h", "s", "hue", "saturation",
                   #"c", "m", "y", "k", "cyan", "magenta", "yellow"]:
        #NO-CMYK 
        elif a in ["a", "alpha",
                   "r", "g", "b", "red", "green", "blue",
                   "h", "s", "hue", "saturation"]:
            return self.__dict__["__"+a[0]]
        
        raise AttributeError, "'"+str(self.__class__)+"' object has no attribute '"+a+"'"




class Text(Grob, TransformMixin, ColorMixin):
    stateAttributes = ('_transform', '_transformmode', '_fillcolor', '_fontfile', '_fontsize', '_align', '_lineheight')
    #kwargs = ('fill', 'font', 'fontsize', 'align', 'lineheight')

    def __init__(self, bot, text, x=0, y=0, width=None, height=None, ctx=None, **kwargs):
        self._bot = bot
        super(Text, self).__init__(self._bot)
        TransformMixin.__init__(self)
        ColorMixin.__init__(self, **kwargs)
        # in case of textpath it creates a temp cairo context for path extraction
        if ctx is None:
            surface = cairo.ImageSurface(cairo.FORMAT_A8, 0, 0)
            ctx = cairo.Context(surface)
        
        self.ctx = ctx              
        if self._bot:
            _copy_attrs(self._bot, self, self.stateAttributes)
        self.text = unicode(text)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        if kwargs.has_key("font"):
            self._fontfile = kwargs["font"]
        # here we start to do the magic with pango, first we set typeface    
        self._fontface = pango.FontDescription()
        self._fontface.set_family(self._fontfile)
        # then the font weight
        self._weight = pango.WEIGHT_NORMAL
        if kwargs.has_key("weight"):
            if kwargs["weight"]=="ultralight":
                self._weight = pango.WEIGHT_ULTRALIGHT
            if kwargs["weight"]=="light":
                self._weight = pango.WEIGHT_LIGHT
            if kwargs["weight"]=="bold":
                self._weight = pango.WEIGHT_BOLD
            if kwargs["weight"]=="ultrabold":
                self._weight = pango.WEIGHT_ULTRABOLD
            if kwargs["weight"]=="heavy":
                self._weight = pango.WEIGHT_HEAVY                                                
        self._fontface.set_weight(self._weight)
        # the variant
        self._variant = pango.VARIANT_NORMAL
        if kwargs.has_key("variant"):
            if kwargs["variant"]=="small-caps" or kwargs["variant"]=="smallcaps":
                self._variant = pango.VARIANT_SMALL_CAPS
        self._fontface.set_variant(self._variant)
        # the style        
        self._style = pango.STYLE_NORMAL
        if kwargs.has_key("style"):
            if kwargs["style"]=="italic" or kwargs["style"]=="oblique":
                self._style = pango.STYLE_ITALIC
        self._fontface.set_style(self._style)       
        # the stretch
        self._stretch = pango.STRETCH_NORMAL
        if kwargs.has_key("stretch"):
            if kwargs["stretch"]=="ultracondensed" or kwargs["stretch"]=="ultra-condensed":
                self._stretch = pango.STRETCH_ULTRA_CONDENSED
            if kwargs["stretch"]=="condensed":
                self._stretch = pango.STRETCH_CONDENSED
            if kwargs["stretch"]=="expanded":
                self._stretch = pango.STRETCH_EXPANDED            
            if kwargs["stretch"]=="ultraexpanded" or kwargs["stretch"]=="ultra-expanded":
                self._stretch = pango.STRETCH_ULTRA_EXPANDED
        self._fontface.set_stretch(self._stretch)                                              
        # then we set fontsize (multiplied by pango.SCALE)
        if kwargs.has_key("fontsize"):
            self._fontsize = kwargs["fontsize"] 
        self._fontface.set_absolute_size(self._fontsize*pango.SCALE)
        if kwargs.has_key("lineheight"):
            self._lineheight = kwargs["lineheight"]           
        if kwargs.has_key("align"):
            self._align= kwargs["align"] 
        # we build a PangoCairo context linked to cairo context
        # then we create a pango layout
        self.pang_ctx = pangocairo.CairoContext(self.ctx)
        self.layout = self.pang_ctx.create_layout()
        # layout line spacing
        # TODO: the behaviour is not the same as nodebox yet
        self.layout.set_spacing(((self._lineheight-1)*self._fontsize)*pango.SCALE)
        # we pass pango font description and the text to the pango layout
        self.layout.set_font_description(self._fontface)
        self.layout.set_text(self.text)
        # check if max text width is set and pass it to pango layout
        # text will wrap, meanwhile it checks if and indent has to be applied
        # indent is subordinated to width because it makes no sense on a single-line text block
        if self.width:
            self.layout.set_width(self.width*pango.SCALE)
            if kwargs.has_key("indent"):
                self.layout.set_indent(kwargs["indent"]*pango.SCALE)                
        # set text alignment    
        if self._align == "right":
            self.layout.set_alignment(pango.ALIGN_RIGHT)
        elif self._align == "center":
            self.layout.set_alignment(pango.ALIGN_CENTER)
        elif self._align == "justify":
            self.layout.set_alignment(pango.ALIGN_LEFT)
            self.layout.set_justify(True)
        else:
            self.layout.set_alignment(pango.ALIGN_LEFT)

    # This version is probably more pangoesque, but the layout iterator
    # caused segfaults on some system
    #def _get_baseline(self):
        #self.iter = self.layout.get_iter()
        #baseline_y = self.iter.get_baseline()
        #baseline_delta = baseline_y/pango.SCALE
        #return (baseline_delta)
    #baseline = property(_get_baseline)

    def _get_baseline(self):
        # retrieves first line of text block
        first_line = self.layout.get_line(0)
        # get the logical extents rectangle of first line
        first_line_extent = first_line.get_extents()[1]
        # get the descent value, in order to calculate baseline position
        first_line_descent = pango.DESCENT(first_line.get_extents()[1])
        # gets the baseline offset from the top of thext block
        baseline_delta = (first_line_extent[3]-first_line_descent)/pango.SCALE
        return (baseline_delta)
    baseline = property(_get_baseline)

    
    def _get_metrics(self):
        w,h = self.layout.get_pixel_size()
        return (w,h)
    metrics = property(_get_metrics)

    def _get_path(self):
        self.ctx.move_to(self.x,self.y)
        # add pango layout to current cairo path in temporary context
        self.pang_ctx.layout_path(self.layout)
        # retrieve current path from current context
        pathdata = self.ctx.copy_path()
        # creates a BezierPath instance for storing new shoebot path
        p = BezierPath(self._bot)
        # parsing of cairo path to build a shoebot path
        for item in pathdata:
            cmd = item[0]
            args = item[1]
            if cmd == 0: # moveto
                p.moveto(*args)
            elif cmd == 1: # lineto
                p.lineto(*args)
            elif cmd == 2: # curveto
                p.curveto(*args)
            elif cmd == 3: # close
                p.closepath()
        return p
        # cairo function for freeing path memory
        pathdata.path_destroy()
    path = property(_get_path)

    def _get_center(self):
        '''Returns the center point of the path, disregarding transforms.
        '''
        w,h = self.layout.get_pixel_size()
        x = (self.x+w/2)
        y = (self.y+h/2)
        return (x,y)
    center = property(_get_center)

    def copy(self):
        new = self.__class__(self._bot, self.text)
        _copy_attrs(self, new,
            ('x', 'y', 'width', 'height', '_transform', '_transformmode',
            '_fillcolor', '_fontfile', '_fontsize', '_align', '_lineheight'))
        return new

class Image(Grob, TransformMixin, ColorMixin):
    stateAttributes = ('_transform', '_transformmode')
    kwargs = ()

    def __init__(self, bot, path, x, y, width=None, height=None, alpha=1.0, data=None, **kwargs):
        self._bot = bot
        #super(Image, self).__init__(self._bot)
        TransformMixin.__init__(self)
        ColorMixin.__init__(self, **kwargs)

        if self._bot:
            _copy_attrs(self._bot, self, self.stateAttributes)

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.alpha = alpha
        self.path = path
        self.data = data

        import Image       
        from array import array

        # checks if image data is passed in command call, in this case it wraps
        # the data in a StringIO oject in order to use it as a file
        # the data itself must contain an entire image, not just pixel data
        # it can be useful for example to retrieve images from the web without 
        # writing temp files (e.g. using nodebox's web library, see example 1 of the library)
        # if no data is passed the path is used to open a local file
        if self.data is None:
            img = Image.open(self.path)
        elif self.data:
            from StringIO import StringIO
            img = Image.open(StringIO(self.data))

        # retrieves original image size
        Width, Height = img.size
        # if no width is given, it assumes the original image size, else image is resized
        if self.width is None:
            if self.height is None:
                self.width = Width
                self.height = Height
            else:
                self.width = int(self.height*Width/Height)
                size = self.width, self.height
                img = img.resize(size, Image.ANTIALIAS)
        else:
            if self.height is None:
                self.height = int(self.width*Height/Width)
            size = self.width, self.height
            img = img.resize(size, Image.ANTIALIAS)
        # check image mode and transforms it in ARGB32 for cairo, transforming it to string, swapping channels
        # and fills a buffer from array module, then passes it to cairo image surface constructor
        if img.mode == "RGBA":
            img_buffer = array('c')
            img_buffer.fromstring(util.rgba_to_argb(img.tostring()))
            imagesurface = cairo.ImageSurface.create_for_data(img_buffer, cairo.FORMAT_ARGB32, self.width, self.height)
        elif img.mode == "RGB":
            img = img.convert('RGBA')
            img_buffer = array('c')
            img_buffer.fromstring(util.rgba_to_argb(img.tostring()))
            imagesurface = cairo.ImageSurface.create_for_data(img_buffer, cairo.FORMAT_ARGB32, self.width, self.height)            
        else:
            raise NotImplementedError("sorry, this image mode is not implemented yet")
        #this is the item that will be drawn
        self.imagesurface = imagesurface


    def _get_center(self):
        '''Returns the center point of the path, disregarding transforms.
        '''
        x = (self.x+self.width/2)
        y = (self.y+self.height/2)
        return (x,y)
    center = property(_get_center)

    def copy(self):
        new = self.__class__(self._bot, self.path, self.x, self.y, self.width, self.height)
        _copy_attrs(self, new, ('x', 'y', 'width', 'height', 'alpha', '_transform', '_transformmode'))
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

TRANSFORMS = ['translate', 'scale', 'rotate', 'skew', 'push', 'pop']

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

    def push(self):
        t = ('push',)
        self.stack.append(t)

    def pop(self):
        t = ('pop',)
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
    ### calculates tranformation matrix
    def get_matrix_with_center(self,x,y,mode):
        from math import sin, cos
        m = cairo.Matrix()
        rotang = 0
        centerx =x
        centery = y
        m_archived = []

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
                    xt = args[0]*cos(-rotang)+args[1]*sin(-rotang)
                    yt = args[1]*cos(-rotang)-args[0]*sin(-rotang)
                    t.translate(xt,yt)
                    m *= t
                elif cmd == 'rotate':
                    if mode == 'corner':                        
                        # apply existing transform to cornerpoint
                        deltax,deltay = m.transform_point(0,0)
                        a = args[0]
                        m1 = cairo.Matrix()
                        m2 = cairo.Matrix()
                        m1.translate(-deltax, -deltay)
                        m2.translate(deltax, deltay)
                        # transform centerpoint according to current matrix
                        m *= m1
                        m *= cairo.Matrix(cos(a), sin(a), -sin(a), cos(a),0,0)
                        m *= m2
                        rotang += a
                    elif mode == 'center':
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
                        rotang += a
                elif cmd == 'scale':
                    if mode == 'corner':
                        t.scale(args[0], args[1])
                        m *= t
                    elif mode == 'center':
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

                elif cmd == 'skew':
                    if mode == 'corner':
                        x, y = args
                        ## TODO: x and y should be the tangent of an angle
                        t *= cairo.Matrix(1,0,x,1,0,0)
                        t *= cairo.Matrix(1,y,0,1,0,0)
                        m *= t
                    elif mode == 'center':
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

		elif cmd == 'push':
                    m_archived.append((m, rotang))

		elif cmd == 'pop':
                    m, rotang = m_archived.pop()

        return m        

    def get_matrix(self):
        '''Returns this transform's matrix. Its centerpoint is presumed to be
        (0,0), which is the Cairo default.'''
        return self.get_matrix_with_center(0,0)

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
While I am less pleased with my parsing function, I think it works. And that
is important. There will be time for improvement later.
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





