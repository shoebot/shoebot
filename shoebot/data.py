'''
Shoebot data structures for bezier path handling
'''

from __future__ import division
import util

RGB = "rgb"
HSB = "hsb"

MOVETO = "moveto"
LINETO = "lineto"
RLINETO = "rlineto"
CURVETO = "curveto"
RCURVETO = "rcurveto"
CLOSE = "close"

DEBUG = False

NUMBER = 1
TEXT = 2
BOOLEAN = 3
BUTTON = 4

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

class BezierPath:
    """
    Shoebot implementation of Nodebox's BezierPath wrapper.
    While Nodebox relies on Cocoa/QT for its data structures,
    this is more of an "agnostic" implementation that won't
    require any other back-ends to work with paths.
    """

    def __init__(self, path=None):
        if path is None:
            self.data = []
        elif isinstance(path, (tuple,list)):
            self.data = []
            self.extend(path)
        elif isinstance(path, BezierPath):
            self.data = path.data
            ##util._copy_attrs(path, self, self.stateAttributes)
        elif isinstance(path, basestring):
            # SVG path goes here
            # - check if SVG datastring is valid
            # - parse it
            pass
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
        self.data.append(PathElement(MOVETO, x, y))

    def lineto(self, x, y):
        self.data.append(PathElement(LINETO, x, y))

    def curveto(self, c1x, c1y, c2x, c2y, x, y):
        self.data.append(PathElement(CURVETO, c1x, c1y, c2x, c2y, x, y))

    def closepath(self):
        self.data.append(PathElement(CLOSE))
        self.closed = True

    def __getitem__(self, index):
        return self.data[index]
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

        # parsepathdata()

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
        # parsepathdata()
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
            self.x, self.y = args
            self.c1x = self.c1y = self.c2x = self.c2y = None
        elif cmd == LINETO:
            assert len(args) == 2
            self.x, self.y = args
            self.c1x = self.c1y = self.c2x = self.c2y = None
        elif cmd == RLINETO:
            assert len(args) == 2
            self.x, self.y = args
            self.c1x = self.c1y = self.c2x = self.c2y = None
        elif cmd == CURVETO:
            assert len(args) == 6
            self.c1x, self.c1y, self.c2x,self.c2y, self.x, self.y = args
        elif cmd == RCURVETO:
            assert len(args) == 6
            self.c1x, self.c1y, self.c2x,self.c2y, self.x, self.y = args
        elif cmd == CLOSE:
            assert args is None or len(args) == 0
            self.x = self.y = self.c1x = self.c1y = self.c2x = self.c2y = None
        else:
            raise ShoebotError('Wrong initialiser for PathElement (got "%s")' % (cmd))

    def __getitem__(self,key):
        if self.cmd == MOVETO:
            return (MOVETO, self.x, self.y)[key]
        elif self.cmd == LINETO:
            return (LINETO, self.x, self.y)[key]
        elif self.cmd == RLINETO:
            return (RLINETO, self.x, self.y)[key]
        elif self.cmd == CURVETO:
            return (CURVETO, self.c1x, self.c1y, self.c2x, self.c2y, self.x, self.y)[key]
        elif self.cmd == RCURVETO:
            return (RCURVETO, self.c1x, self.c1y, self.c2x, self.c2y, self.x, self.y)[key]
        elif self.cmd == CLOSE:
            return (CLOSE,)[key]
        return
    def __repr__(self):
        if self.cmd == MOVETO:
            return "(MOVETO, %.6f, %.6f)" % (self.x, self.y)
        elif self.cmd == LINETO:
            return "(LINETO, %.6f, %.6f)" % (self.x, self.y)
        elif self.cmd == RLINETO:
            return "(RLINETO, %.6f, %.6f)" % (self.x, self.y)
        elif self.cmd == CURVETO:
            return "(CURVETO, %.6f, %.6f, %.6f, %.6f, %.6f, %.6f)" % (self.c1x, self.c1y, self.c2x, self.c2y, self.x, self.y)
        elif self.cmd == RCURVETO:
            return "(RCURVETO, %.6f, %.6f, %.6f, %.6f, %.6f, %.6f)" % (self.c1x, self.c1y, self.c2x, self.c2y, self.x, self.y)
        elif self.cmd == CLOSE:
            return "(CLOSE,)"
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

    Attributes:
    r, g, b (0-1)
    hue, saturation, lightness (0-1)

    This stores color values as a list of 4 floats (RGBA) in a 0-1 range.
    Settings for color mode and range can be specified, and the input values
    will be converted to 0-1 range and RGB mode.

    A box instance can be passed to it, in which case, Color will read
    the input values according to that Box's color mode and range settings.


    Shoebot's color() includes these arguments on the object constructor; they should be used in
    any other case where color() is not enough and a direct call to Color() is needed.
    '''

    def __init__(self, v, color_range = 1, mode=RGB, box=None):
        # if we got a box argument, use its values
        if box:
            self.color_range = box.opt.color_range
            self.color_mode = box.opt.color_mode
        else:
            self.color_range = color_range
            self.color_mode = mode

        if self.color_mode is RGB:
            self.r, self.g, self.b, self.a = util.parse_color(v, self.color_range)
        elif self.color_mode is HSB:
            self.r, self.g, self.b, self.a = util.parse_hsb_color(v, self.color_range)

        # convenience attributes
        self.red = self.r
        self.green = self.g
        self.blue = self.b
        self.alpha = self.a

        self.hue, self.saturation, self.lightness = util.rgb_to_hsl(self.r, self.g, self.b)

    def __getitem__(self, index):
        return (self.r, self.g, self.b, self.a)[index]
    def __repr__(self):
        return "(%f,%f,%f,%f)" % (self.r, self.g, self.b, self.a)
    def __div__(self, other):
        value = float(other)
        return (self.red/value, self.green/value, self.blue/value, self.alpha/value)

    def blend(self,other,factor):
        r = (self.r + other.r) / factor
        g = (self.g + other.g) / factor
        b = (self.b + other.b) / factor
        a = (self.a + other.a) / factor
        return Color(r,g,b,a)
    def copy(self):
        new = self.__class__()
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





