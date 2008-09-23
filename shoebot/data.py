'''
Shoebot data structures for bezier path handling
'''

import util

RGB = "rgb"
HSB = "hsb"

MOVETO = "moveto"
LINETO = "lineto"
CURVETO = "curveto"
CLOSE = "close"

DEBUG = False

NUMBER = 1
TEXT = 2
BOOLEAN = 3
BUTTON = 4

class ShoebotError(Exception): pass

class Point:
    '''
    Taken from Nodebox and modified
    '''
    def __init__(self, *args):
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

    # i added this
    def __getitem__(self,key):
        return (float(self.x), float(self.y))[key]

    def __eq__(self, other):
        if other is None: return False
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)

class BezierPath:
    """
    Shoebot implementation of Nodebox's BezierPath wrapper.
    While Nodebox relies on Cocoa/QT for its data structures,
    this is more of an "agnostic" implementation that won't
    require any other back-ends to work with paths.
    """
    # we don't use these yet
    stateAttributes = ('_fillcolor', '_strokecolor', '_strokewidth', '_transform', '_transformmode')
    #kwargs = ('fill', 'stroke', 'strokewidth')

    def __init__(self, path=None):
        if path is None:
            self.data = []
        elif isinstance(path, (tuple,list)):
            self.data = []
            self.extend(path)
        elif isinstance(path, BezierPath):
            self.data = path.data
            ##util._copy_attrs(path, self, self.stateAttributes)
        else:
            raise ShoebotError, "Don't know what to do with %s." % path
        self.closed = False

    # testing string output
    #def __str__(self):
        #return self.data

    def copy(self):
        return self.__class__(self)

    ### Path methods ###

    def moveto(self, x, y):
        el = PathElement(MOVETO, x, y)
        self.data.append(el)

    def lineto(self, x, y):
        el = PathElement(LINETO, x, y)
        self.data.append(el)

    def curveto(self, c1x, c1y, c2x, c2y, x, y):
        el = PathElement(CURVETO, c1x, c1y, c2x, c2y, x, y)
        self.data.append(el)

    def closepath(self):
        el = PathElement(CLOSE)
        self.data.append(el)
        self.closed = True

    def __getitem__(self, index):
        cmd, el = self.data[index]
        return PathElement(cmd, el)

    def __iter__(self):
        for i in range(len(self.data)):
            yield self.data[i]

    def __len__(self):
        return len(self.data)

    def extend(self, args):
        '''
        This method is still work in progress,
        don't rely on it :o)
        '''
        self.segment_cache = None

        ## TODO
        # Initial check, we should check for
        # - points
        # - tuples
        # - list
        # - PathElement
        
        # oh my, this just creates straight lines, no curves
        # this needs to be rewritten

        # check if we got [x,y] as an argument
        if isinstance(args, list) and len(args) == 2 and isinstanceargs[0]:
            # does the path have something?
            if len(self.data) == 0:
                # if not, move to [x,y]
                cmd = MOVETO
            else:
                # otherwise, draw a line to [x,y]
                cmd = LINETO
            # assign the elements to specific vars
            x = args[0]
            y = args[1]
            self.data.append(PathElement(cmd, x, y))

        elif isinstance(args,list):
            for el in pathElements:
                if isinstance(el, (list, tuple, PathElement)):
                    x, y = el
                    if len(self.data) == 0:
                        cmd = MOVETO
                    else:
                        cmd = LINETO
                    self.data.append(PathElement(cmd, x, y))
                elif isinstance(el, PathElement):
                    self.data.append(el)
                else:
                    raise ShoebotError, "Don't know how to handle %s" % el

    def append(self, el):
        '''
        Wrapper method for hiding the data var
        from public access
        '''
        if isinstance(el, PathElement):
            self.data.append(el)
        else:
            raise TypeError("Wrong data passed to BezierPath.append()")

class PathElement:
    '''
    Taken from Nodebox and modified
    '''
    def __init__(self, cmd, *args):
        self.cmd = cmd
        if cmd == MOVETO:
            assert len(args) == 2
            self.x = args[0]
            self.y = args[1]
            self.c1x = self.c1y = None
            self.c2x = self.c2y = None
        elif cmd == LINETO:
            assert len(args) == 2
            self.x, self.y = args[0], args[1]
            self.c1x = self.c1y = None
            self.c2x = self.c2y = None
        elif cmd == CURVETO:
            assert len(args) == 6
            self.c1x,self.c1y = args[0], args[1]
            self.c2x,self.c2y = args[2], args[3]
            self.x, self.y = args[4], args[5]
        elif cmd == CLOSE:
            assert args is None or len(args) == 0
            self.x = self.y = None
            self.c1x = self.c1y = None
            self.c2x = self.c2y = None
        else:
            print "MALFORMED PATH ELEMENT"
            self.x = self.y = None
            self.ctrl1 = None
            self.ctrl2 = None

    def __getitem__(self,key):
        if self.cmd == MOVETO:
            return (MOVETO, self.x, self.y)[key]
        elif self.cmd == LINETO:
            return (LINETO, self.x, self.y)[key]
        elif self.cmd == CURVETO:
            return (CURVETO, self.c1x, self.c1y, self.c2x, self.c2y, self.x, self.y)[key]
        elif self.cmd == CLOSE:
            # the extra coordinates are to avoid a one-element tuple, which doesn't
            # play nice with BezierPath
            return (CLOSE, 0.0, 0.0)[key]
        return

    def __repr__(self):
        if self.cmd == MOVETO:
            return "(MOVETO, %.6f, %.6f)" % (self.x, self.y)
        elif self.cmd == LINETO:
            return "(LINETO, %.6f, %.6f)" % (self.x, self.y)
        elif self.cmd == CURVETO:
            return "(CURVETO, %.6f, %.6f, %.6f, %.6f, %.6f, %.6f)" % (self.c1x, self.c1y, self.c2x, self.c2y, self.x, self.y)
        elif self.cmd == CLOSE:
            return "(CLOSE, 0.0, 0.0)"

    def __eq__(self, other):
        if other is None: return False
        if self.cmd != other.cmd: return False
        return self.x == other.x and self.y == other.y \
            and self.c1x == other.c1x and self.c1y == other.c1y \
            and self.c1x == other.c1x and self.c1y == other.c1y

    def __ne__(self, other):
        return not self.__eq__(other)

class Color(object):
    '''
    Taken from Nodebox and modified.
    Since we have no Cocoa, we have no way to use colour management for the moment.
    So we took another approach.

    This stores color values as a list of 4 floats (RGBA) in a 0-1 range.
    Mode and range are mandatory arguments so we know how we need to parse
    the input and make sure output works.

    Shoebot's color() includes these arguments on the object constructor; they should be used in
    any other case where color() is not enough and a direct call to Color() is needed.
    '''

    # This code is still very messy, recovering from a big bug hunt. But works!

    def __init__(self, mode=RGB, crange=1, *args):
        # check for proper input
        if not isinstance(mode, basestring):
            raise TypeError("ERROR: Color() was called with an invalid mode argument (" + str(mode) + ")")

        if DEBUG:
            print "-----------------------------------------"
            print "DEBUG(Color): __init__ args: " + str(args)
            print "DEBUG(Color): range: " + str(crange)
            print "DEBUG(Color): mode: " + str(mode)

        if len(args) == 1 and isinstance(args[0], tuple):
            if DEBUG: print "DEBUG(Color): got a tuple: " + str(args[0])
            clr = args[0]
            if len(clr) == 3:
                if DEBUG: print "DEBUG(Color): Got a 3 element tuple"
                clr = (clr[0]/crange, clr[1]/crange, clr[2]/crange, 1)
            elif len(clr) == 4:
                if DEBUG: print "DEBUG(Color): Got a 4 element tuple"
                clr = (clr[0]/crange, clr[1]/crange, clr[2]/crange, clr[3])
            elif len(clr) == 1:
                if isinstance(clr, tuple):
                    if DEBUG: print "DEBUG(Color): Got a 1 element tuple"
                    clr = clr[0]
                    clr = (clr[0]/crange,clr[1]/crange,clr[2]/crange,1)
            elif len(clr) == 2:
                if DEBUG: print "DEBUG(Color): Got a 2 element tuple"
                clr = (clr[0]/crange,clr[0]/crange,clr[0]/crange,clr[1])
            else:
                raise ShoebotError("Wrong colour tuple")
        elif len(args) == 1 and args[0] is None:
            if DEBUG: print "DEBUG(Color): Got nothing, defaulting to black"
            clr = (0,0,0,1)
        elif len(args) == 1 and isinstance(args[0], Color):
            if DEBUG: print "DEBUG(Color): Got a Color object"
            clr = args[0].get_rgba(1)
        elif len(args) == 1 and isinstance(args[0], (int,float)): # Gray, no alpha
            if DEBUG: print "DEBUG(Color): got an int/float:" + str(args[0])
            g = float(args[0])
            clr = (g/crange, g/crange, g/crange, 1)
        elif len(args) == 2: # Gray and alpha
            if DEBUG: print "DEBUG(Color): Got 2 args"
            g, a = args
            clr = (g, g, g, a)
        elif len(args) == 3 and mode == RGB: # RGB, no alpha
            if DEBUG: print "DEBUG(Color): Got 3 args"
            r, g, b = args
            clr = (r/crange, g/crange, b/crange, 1)
        elif len(args) == 3 and mode == HSB: # HSB, no alpha
            if DEBUG: print "DEBUG(Color): Got 3 args (HSB):" + str(args)
            h, s, b = args
            r, g, b = util.hsl_to_rgb(float(h)/crange, float(s)/crange, float(b)/crange)
            clr = (r, g, b, 1)
        elif len(args) == 4 and mode == RGB: # RGB and alpha
            if DEBUG: print "DEBUG(Color): Got 4 args"
            r, g, b, a = args
            clr = (r/crange, g/crange, b/crange, a)
        elif len(args) == 4 and mode == HSB: # HSB and alpha
            if DEBUG: print "DEBUG(Color): Got 4 args (HSB)"
            h, s, b, a = args
            r, g, b = util.hsl_to_rgb(h/crange, s/crange, b/crange)
            clr = (r, g, b, a/crange)
        else:
            if DEBUG: print "DEBUG(Color): WARNING: Couldn't parse input, defaulting to black"
            clr = (0,0,0,1)

        # debug device for warning when a colour is not inside expected values
        warn = False
        for value in clr:
            if not (value >= 0 and value <= 1):
                warn = True
        if warn and DEBUG:
            if DEBUG: print "WARNING(Color): Output color is not a float between 0 and 1"
            if DEBUG: print str(clr)

        self.red = clr[0]
        self.green = clr[1]
        self.blue = clr[2]
        self.alpha = clr[3]

        if DEBUG:
            print "DEBUG(Color): Color set to (" + ', '.join((str(self.red), str(self.green), str(self.blue), str(self.alpha))) + ")"
            print

        #print self.red, self.green, self.blue, self.alpha

        clr_hsb = util.rgb_to_hsl(self.red, self.green, self.blue)
        self.hue = clr_hsb[0]
        self.saturation = clr_hsb[1]
        self.lightness = clr_hsb[2]

    def get_rgb(self,colorrange):
        colorrange = float(colorrange)
        return (self.red*colorrange,self.green*colorrange,self.blue*colorrange)
    def get_rgba(self,colorrange):
        colorrange = float(colorrange)
        return (self.red*colorrange,self.green*colorrange,self.blue*colorrange,self.alpha*colorrange)
    def get_hsb(self,colorrange):
        colorrange = float(colorrange)
        return (self.hue*colorrange,self.saturation*colorrange,self.brightness*colorrange)
    def get_hsba(self,colorrange):
        colorrange = float(colorrange)
        return (self.hue*colorrange,self.saturation*colorrange,self.brightness*colorrange,self.alpha*colorrange)

    def __getitem__(self, key):
        return tuple(self.get_rgba(1))[key]

    def __repr__(self):
        #return "%s(%.3f, %.3f, %.3f, %.3f)" % (self.__class__.__name__, self.red,
                #self.green, self.blue, self.alpha)
        # Note: I'm not sure this is right coding practice -- ricardo
        return str(self.get_rgba(1))

    def __str__(self):
        return str(self.get_rgba(1))

    def __div__(self, other):
        value = float(other)
        return (self.red/value, self.green/value, self.blue/value, self.alpha/value)

    def copy(self):
        new = self.__class__()
        return new

    ##def blend(self, otherColor, factor):
        #"""Blend the color with otherColor with a factor; return the new color. Factor
        #is a float between 0.0 and 1.0.
        #"""
        ##if hasattr(otherColor, "color"):
            ##otherColor = otherColor._rgb
        ##return self.__class__(color=self._rgb.blendedColorWithFraction_ofColor_(
            ##factor, otherColor))

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
                self.default = "hello"
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
            return unicode(str(val), "utf_8", "replace")
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
