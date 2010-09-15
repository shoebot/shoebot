import sys, locale, gettext
from shoebot.data import _copy_attrs
from shoebot.data import Grob, ColorMixin, TransformMixin
from shoebot import MOVETO, RMOVETO, LINETO, RLINETO, CURVETO, RCURVETO, ARC, ELLIPSE, CLOSE

CENTER = 'center'

APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
#gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext


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

    # transforms are not here because they shouldn't be inherited from Bot
    stateAttributes = ('_fillcolor', '_strokecolor', '_strokewidth',)
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
            raise ValueError, _("Don't know what to do with %s.") % path
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
            raise TypeError(_("Wrong data passed to BezierPath.append(): %s") % el)

# the following functions were used to determine the center point of the
# path, but this logic was moved to the canvas to avoid creating a new
# context for each path.

"""
    def _get_bounds(self):
        '''Returns the path's bounding box. Note that this doesn't
        take transforms into account.'''
        # we don't have any direct way to calculate bbox from a path, but Cairo
        # does! So we make a new cairo context to calculate path bounds
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
        ctx = cairo.Context(surface)
        # FIXME: this is a bad way to do it, but we don't have a shape drawing
        # library yet...

        # pass path to temporary context
        for element in self.data:
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
                x, y, w, h = values
                ctx.save()
                ctx.translate (x + w / 2., y + h / 2.)
                ctx.scale (w / 2., h / 2.)
                ctx.arc (0., 0., 1., 0., 2 * pi)
                ctx.restore()
        # get boundaries
        bbox = ctx.stroke_extents()
        # is this line necessary? Or does python garbage collect this?
        del surface, ctx
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
    abs_center = property(_get_abs_center)

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
"""
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
            raise ValueError(_('Wrong initialiser for PathElement (got "%s")') % (cmd))

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


