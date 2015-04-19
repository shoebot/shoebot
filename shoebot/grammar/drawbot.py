import sys
from bot import Bot
from shoebot.data import BezierPath, Image, ShoebotError
from math import radians as deg2rad

import locale, gettext
APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
#gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext

'''
    - text() should be flipped in CENTER mode, maybe include it in the text class?
'''

TOP_LEFT = 1
BOTTOM_LEFT = 2

CORNER = 'corner'

class DrawBot(Bot):

    def __init__(self, canvas, namespace = None, vars = None):
        ### TODO - Need to do whole drawbot class
        Bot.__init__(self, canvas, namespace = namespace, vars = None)
        self._transformmode = CORNER
        self._canvas.origin = BOTTOM_LEFT

    #### Drawing

    # Paths

    def rect(self, x, y, width, height, roundness=0.0, draw=True, **kwargs):
        '''Draws a rectangle with top left corner at (x,y)

        The roundness variable sets rounded corners.
        '''
        path = self.BezierPath(**kwargs)
        path.rect(x, y, width, height, roundness, self.rectmode)
        if draw:
            path.draw()
        return path

    def rectmode(self, mode=None):
        if mode in (self.CORNER, self.CENTER, self.CORNERS):
            self.rectmode = mode
            return self.rectmode
        elif mode is None:
            return self.rectmode
        else:
            raise ShoebotError(_("rectmode: invalid input"))

    def oval(self, x, y, width, height, draw=True, **kwargs):
        '''Draws an ellipse starting from (x,y) -  ovals and ellipses are not the same'''
        path = self.BezierPath(**kwargs)
        path.ellipse(x, y, width, height)
        if draw:
            path.draw()
        return path

    def ellipse(self, x, y, width, height, draw=True, **kwargs):
        '''Draws an ellipse starting from (x,y)'''
        path = self.BezierPath(**kwargs)
        path.ellipse(x,y,width,height)
        if draw:
            path.draw()
        return path

    def circle(self, x, y, diameter):
        self.ellipse(x, y, diameter, diameter)

    def line(self, x1, y1, x2, y2, draw=True):
        '''Draws a line from (x1,y1) to (x2,y2)'''
        p = self._path
        self.newpath()
        self.moveto(x1,y1)
        self.lineto(x2,y2)
        self.endpath(draw=draw)
        self._path = p
        return p

    #### Path
    # Path functions taken from Nodebox and modified

    def newpath(self, x=None, y=None):
        self._path = self.BezierPath()
        if x and y:
            self._path.moveto(x,y)
        self._path.closed = False

        # if we have arguments, do a moveto too
        if x is not None and y is not None:
            self._path.moveto(x,y)

    def moveto(self, x, y):
        if self._path is None:
            ## self.newpath()
            raise ShoebotError, _("No current path. Use newpath() first.")
        self._path.moveto(x,y)

    def lineto(self, x, y):
        if self._path is None:
            raise ShoebotError, _("No current path. Use newpath() first.")
        self._path.lineto(x, y)

    def curveto(self, x1, y1, x2, y2, x3, y3):
        if self._path is None:
            raise ShoebotError, _("No current path. Use newpath() first.")
        self._path.curveto(x1, y1, x2, y2, x3, y3)

    def arcto(self, x, y, radius, angle1, angle2):
        if self._path is None:
            raise ShoebotError, _("No current path. Use newpath() first.")
        self._path.arc(x, y, radius, angle1, angle2)

    def closepath(self):
        if self._path is None:
            raise ShoebotError, _("No current path. Use newpath() first.")
        if not self._path.closed:
            self._path.closepath()
            self._path.closed = True

    def endpath(self, draw=True):
        if self._path is None:
            raise ShoebotError, _("No current path. Use newpath() first.")
        if self._autoclosepath:
            self._path.closepath()
        p = self._path
        # p.inheritFromContext()
        if draw:
            self._path.draw()
            self._path = None
        return p

    def drawpath(self,path):
        if isinstance(path, BezierPath):
            p = self.BezierPath(path=path)
            p.draw()
        elif isinstance(path, Image):
            path.draw() # Is this right ? - added to make test_clip_4.bot work
        elif hasattr(path, '__iter__'):
            p = self.BezierPath()
            for point in path:
                p.addpoint(point)
            p.draw()
        

    def relmoveto(self, x, y):
        '''Move relatively to the last point.'''
        if self._path is None:
            raise ShoebotError, _("No current path. Use newpath() first.")
        self._path.relmoveto(x,y)

    def rellineto(self, x, y):
        '''Draw a line using relative coordinates.'''
        if self._path is None:
            raise ShoebotError, _("No current path. Use newpath() first.")
        self._path.rellineto(x,y)

    def relcurveto(self, h1x, h1y, h2x, h2y, x, y):
        '''Draws a curve relatively to the last point.
        '''
        if self._path is None:
            raise ShoebotError, _("No current path. Use newpath() first.")
        self._path.relcurveto(x,y)

    def autoclosepath(self, close=True): 
        self._autoclosepath = close

    # Image

    def image(self, path, x, y, width=None, height=None, alpha=1.0, data=None, draw=True, **kwargs):
        '''Draws a image form path, in x,y and resize it to width, height dimensions.
        '''
        return self.Image(path, x, y, width, height, alpha, data, **kwargs)

    def imagesize(self, path):
        img = Image.open(path)
        return img.size

    def drawimage(self, image):
        self.image(image.path, image.x, image.y, data = image.data)

    #### Transform and utility

    def translate(self, xt, yt, mode = None):
        self._canvas.translate(xt, yt)
        if mode:
            self._canvas.mode = mode

    def rotate(self, degrees=0, radians=0):
        ### TODO change canvas to use radians
        if radians:
            angle = radians
        else:
            angle = deg2rad(degrees)
        self._canvas.rotate(-angle)

    def scale(self, x=1, y=None):
        if not y:
            y = x
        if x == 0:
            # Cairo borks on zero values
            x = 1
        if y == 0:
            y = 1
        self._canvas.scale(x, y)

    def skew(self, x=1, y=0):
        ### TODO bring back transform mixin
        t = self._canvas.transform
        t *= cairo.Matrix(1,0,x,1,0,0)
        t *= cairo.Matrix(1,y,0,1,0,0)
        self._canvas.transform = t

    def push(self):
        self._canvas.push_matrix()

    def pop(self):
        self._canvas.pop_matrix()

    def reset(self):
        self._canvas.reset_transform()

    #### Color

    def colormode(self, mode=None, crange=None):
        '''Sets the current colormode (can be RGB or HSB) and eventually
        the color range.

        If called without arguments, it returns the current colormode.
        '''
        if mode is not None:
            if mode == "rgb":
                self.color_mode = Bot.RGB
            elif mode == "hsb":
                self.color_mode = Bot.HSB
            else:
                raise NameError, _("Only RGB and HSB colormodes are supported.")
        if crange is not None:
            self.color_range = crange
        return self.color_mode

    def colorrange(self, crange):
        self.color_range = float(crange)

    def fill(self,*args):
        '''Sets a fill color, applying it to new paths.'''
        self._fillcolor = self.color(*args)
        return self._fillcolor

    def nofill(self):
        ''' Stop applying fills to new paths.'''
        self._fillcolor = None

    def stroke(self,*args):
        '''Set a stroke color, applying it to new paths.'''
        self._strokecolor = self.color(*args)
        return self._strokecolor

    def nostroke(self):
        ''' Stop applying strokes to new paths.'''
        self._strokecolor = None

    def strokewidth(self, w=None):
        '''Set the stroke width.'''
        if w is not None:
            self._strokewidth = w
        else:
            return self._strokewidth

    def background(self,*args):
        '''Set the background colour.'''
        self._canvas.background = self.color(*args)

    #### Text

    def font(self, fontpath=None, fontsize=None):
        '''Set the font to be used with new text instances.

        Accepts any font Pango can recognize'''
        if fontpath is not None:
            self._canvas.fontfile = fontpath
        else:
            return self._canvas.fontfile
        if fontsize is not None:
            self._canvas.fontsize = fontsize

    def fontsize(self, fontsize=None):
        if fontsize is not None:
            self._canvas.fontsize = fontsize
        else:
            return self._canvas.font_size

    def text(self, txt, x, y, width=None, height=1000000, outline=False, draw=True, **kwargs):
        '''
        Draws a string of text according to current font settings.
        '''
        txt = self.Text(txt, x, y, width, height, outline=outline, ctx=None, **kwargs)
        if outline:
          path = txt.path
          if draw:
              path.draw()
          return path
        else:
          return txt

    def textpath(self, txt, x, y, width=None, height=1000000, enableRendering=False, **kwargs):
        '''
        Draws an outlined path of the input text
        '''
        txt = self.Text(txt, x, y, width, height, **kwargs)
        path = txt.path
        if draw:
            path.draw()
        return path

    def textmetrics(self, txt, width=None, height=None, **kwargs):
        '''Returns the width and height of a string of text as a tuple
        (according to current font settings).
        '''
        # for now only returns width and height (as per Nodebox behaviour)
        # but maybe we could use the other data from cairo
        
        # we send doRender=False to prevent the actual rendering process, only the path generation is enabled
        # not the most efficient way, but it generates accurate results
        txt = self.Text(txt, 0, 0, width, height, enableRendering=False, **kwargs)
        return txt.metrics

    def textwidth(self, txt, width=None):
        '''Returns the width of a string of text according to the current
        font settings.
        '''
        w = width
        return self.textmetrics(txt, width=w)[0]

    def textheight(self, txt, width=None):
        '''Returns the height of a string of text according to the current
        font settings.
        '''
        w = width
        return self.textmetrics(txt, width=w)[1]

    def lineheight(self, height=None):
        if height is not None:
            self._canvas.lineheight = height

    def align(self, align="LEFT"):
        self._canvas.align=align

    # TODO: Set the framework to setup font options


