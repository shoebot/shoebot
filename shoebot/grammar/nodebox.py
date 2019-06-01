import os.path
import sys

from shoebot.core.backend import cairo
from shoebot.kgp import KantGenerator
from shoebot.data import ShoebotError
from bot import Bot
from shoebot.data import geometry, Point, BezierPath, Image, RGB, HSB, \
    CORNER, CENTER, \
    MOVETO, RMOVETO, LINETO, RLINETO, CURVETO, RCURVETO, ARC, ELLIPSE, \
    CLOSE, \
    LEFT, RIGHT

from math import sin, cos, pi
from math import radians as deg2rad
from types import TupleType
from PIL import Image as PILImage

import locale
import gettext
APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
ASSETS_DIR = sys.prefix + '/share/shoebot/data'
gettext.bindtextdomain(APP, DIR)
# gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext

# Nodebox compatibility shim
sys.path.append(os.path.join(os.path.dirname(__file__), 'nodebox-lib'))
sys.path.append('.')  # ximport can work from current dir


class NodeBot(Bot):

    NORMAL = "1"
    FORTYFIVE = "2"

    CORNER = CORNER
    CENTER = CENTER
    MOVETO = MOVETO
    RMOVETO = RMOVETO
    LINETO = LINETO
    RLINETO = RLINETO
    CURVETO = CURVETO
    RCURVETO = RCURVETO
    ARC = ARC
    ELLIPSE = ELLIPSE  # Shoebot, not nodebox 1.x
    CLOSE = CLOSE

    LEFT = LEFT
    RIGHT = RIGHT

    # Default values
    color_mode = RGB
    color_range = 1

    def __init__(self, canvas=None, namespace=None, vars=None):
        '''
        Nodebot grammar constructor

        :param canvas: Canvas implementation for output.
        :param namespace: Optionally specify a dict to inject as namespace
        :param vars: Optional dict containing initial values for variables
        '''
        Bot.__init__(self, canvas, namespace=namespace, vars=vars)
        canvas.mode = CORNER
        self._ns = self._namespace

    # Drawing

    # Image

    def image(self, path, x, y, width=None, height=None, alpha=1.0, data=None, draw=True, **kwargs):
        '''Draws a image form path, in x,y and resize it to width, height dimensions.
        '''
        return self.Image(path, x, y, width, height, alpha, data, **kwargs)

    def imagesize(self, path):
        '''
        :param: path    Path to image file.
        :return: image size as tuple (width, height)
        '''
        img = PILImage.open(path)
        return img.size

    # Paths

    def rect(self, x, y, width, height, roundness=0.0, draw=True, **kwargs):
        '''
        Draw a rectangle from x, y of width, height.

        :param startx: top left x-coordinate
        :param starty: top left y-coordinate

        :param width: height  Size of rectangle.
        :roundness: Corner roundness defaults to 0.0 (a right-angle).
        :draw: If True draws immediately.
        :fill: Optionally pass a fill color.

        :return: path representing the rectangle.

        '''
        path = self.BezierPath(**kwargs)
        path.rect(x, y, width, height, roundness, self.rectmode)
        if draw:
            path.draw()
        return path

    def rectmode(self, mode=None):
        '''
        Set the current rectmode.

        :param mode: CORNER, CENTER, CORNERS
        :return: rectmode if mode is None or valid.
        '''
        if mode in (self.CORNER, self.CENTER, self.CORNERS):
            self.rectmode = mode
            return self.rectmode
        elif mode is None:
            return self.rectmode
        else:
            raise ShoebotError(_("rectmode: invalid input"))

    def ellipsemode(self, mode=None):
        '''
        Set the current ellipse drawing mode.

        :param mode: CORNER, CENTER, CORNERS
        :return: ellipsemode if mode is None or valid.
        '''
        if mode in (self.CORNER, self.CENTER, self.CORNERS):
            self.ellipsemode = mode
            return self.ellipsemode
        elif mode is None:
            return self.ellipsemode
        else:
            raise ShoebotError(_("ellipsemode: invalid input"))

    def oval(self, x, y, width, height, draw=True, **kwargs):
        '''Draw an ellipse starting from (x,y) -  ovals and ellipses are not the same'''
        path = self.BezierPath(**kwargs)
        path.ellipse(x, y, width, height, self.ellipsemode)
        if draw:
            path.draw()
        return path

    def ellipse(self, x, y, width, height, draw=True, **kwargs):
        '''Draw an ellipse starting from (x,y)'''
        path = self.BezierPath(**kwargs)
        path.ellipse(x, y, width, height, self.ellipsemode)
        if draw:
            path.draw()
        return path

    def circle(self, x, y, diameter, draw=True, **kwargs):
        '''Draw a circle
        :param x: x-coordinate of the top left corner
        :param y: y-coordinate of the top left corner
        :param diameter: Diameter of circle.
        :param draw: Draw immediately (defaults to True, set to False to inhibit drawing)
        :return: Path object representing circle
        '''
        return self.ellipse(x, y, diameter, diameter, draw, **kwargs)

    def line(self, x1, y1, x2, y2, draw=True):
        '''Draw a line from (x1,y1) to (x2,y2)
        :param x1: start x-coordinate
        :param y1: start y-coordinate
        :param x2: end x-coordinate
        :param y2: end y-coordinate
        '''
        p = self._path
        self.beginpath()
        self.moveto(x1, y1)
        self.lineto(x2, y2)
        self.endpath(draw=draw)
        self._path = p
        return p

    def arrow(self, x, y, width, type=NORMAL, draw=True, **kwargs):
        '''Draw an arrow.

        Arrows can be two types: NORMAL or FORTYFIVE.

        :param x: top left x-coordinate
        :param y: top left y-coordinate
        :param width: width of arrow
        :param type:  NORMAL or FORTYFIVE
        :draw:  If True draws arrow immediately

        :return: Path object representing the arrow.
        '''
        # Taken from Nodebox
        path = self.BezierPath(**kwargs)
        if type == self.NORMAL:
            head = width * .4
            tail = width * .2
            path.moveto(x, y)
            path.lineto(x - head, y + head)
            path.lineto(x - head, y + tail)
            path.lineto(x - width, y + tail)
            path.lineto(x - width, y - tail)
            path.lineto(x - head, y - tail)
            path.lineto(x - head, y - head)
            path.lineto(x, y)
        elif type == self.FORTYFIVE:
            head = .3
            tail = 1 + head
            path.moveto(x, y)
            path.lineto(x, y + width * (1 - head))
            path.lineto(x - width * head, y + width)
            path.lineto(x - width * head, y + width * tail * .4)
            path.lineto(x - width * tail * .6, y + width)
            path.lineto(x - width, y + width * tail * .6)
            path.lineto(x - width * tail * .4, y + width * head)
            path.lineto(x - width, y + width * head)
            path.lineto(x - width * (1 - head), y)
            path.lineto(x, y)
        else:
            raise NameError(_("arrow: available types for arrow() are NORMAL and FORTYFIVE\n"))
        if draw:
            path.draw()
        return path

    def star(self, startx, starty, points=20, outer=100, inner=50, draw=True, **kwargs):
        '''Draws a star.
        '''
        # Taken from Nodebox.
        self.beginpath(**kwargs)
        self.moveto(startx, starty + outer)

        for i in range(1, int(2 * points)):
            angle = i * pi / points
            x = sin(angle)
            y = cos(angle)
            if i % 2:
                radius = inner
            else:
                radius = outer
            x = startx + radius * x
            y = starty + radius * y
            self.lineto(x, y)

        return self.endpath(draw)

    # Path
    # Path functions taken from Nodebox and modified

    def beginpath(self, x=None, y=None, **kwargs):
        self._path = self.BezierPath(**kwargs)
        # if we have arguments, do a moveto too
        if x is not None and y is not None:
            self._path.moveto(x, y)

    def moveto(self, x, y):
        if self._path is None:
            # self.beginpath()
            raise ShoebotError(_("No current path. Use beginpath() first."))
        self._path.moveto(x, y)

    def lineto(self, x, y):
        if self._path is None:
            raise ShoebotError(_("No current path. Use beginpath() first."))
        self._path.lineto(x, y)

    def curveto(self, x1, y1, x2, y2, x3, y3):
        if self._path is None:
            raise ShoebotError(_("No current path. Use beginpath() first."))
        self._path.curveto(x1, y1, x2, y2, x3, y3)

    def arc(self, x, y, radius, angle1, angle2):
        if self._path is None:
            raise ShoebotError(_("No current path. Use beginpath() first."))
        self._path.arc(x, y, radius, angle1, angle2)

    def closepath(self):
        if self._path is None:
            raise ShoebotError(_("No current path. Use beginpath() first."))
        if not self._path.closed:
            self._path.closepath()
            self._path.closed = True

    def endpath(self, draw=True):
        if self._path is None:
            raise ShoebotError(_("No current path. Use beginpath() first."))
        p = self._path
        if self._autoclosepath is True:
            self._path.closepath()
        if draw:
            p.draw()
        else:
            # keep the transform so we don't lose it
            self._path.transform = cairo.Matrix(*self._canvas.transform)
        self._path = None
        return p

    def drawpath(self, path, **kwargs):
        if isinstance(path, BezierPath):
            p = self.BezierPath(path=path, **kwargs)
            p.draw()
        elif isinstance(path, Image):
            path.draw()  # Is this right ? - added to make test_clip_4.bot work
        elif hasattr(path, '__iter__'):
            p = self.BezierPath()
            for point in path:
                p.addpoint(point)
            p.draw()

    def drawimage(self, image, x=None, y=None):
        """
        :param image: Image to draw
        :param x: optional, x coordinate (default is image.x)
        :param y: optional, y coordinate (default is image.y)
        :return:
        """
        if x is None:
            x = image.x
        if y is None:
            y = image.y
        self.image(image.path, image.x, image.y, data=image.data)

    def autoclosepath(self, close=True):
        self._autoclosepath = close

    def relmoveto(self, x, y):
        '''Move relatively to the last point.'''
        if self._path is None:
            raise ShoebotError(_("No current path. Use beginpath() first."))
        self._path.relmoveto(x, y)

    def rellineto(self, x, y):
        '''Draw a line using relative coordinates.'''
        if self._path is None:
            raise ShoebotError(_("No current path. Use beginpath() first."))
        self._path.rellineto(x, y)

    def relcurveto(self, h1x, h1y, h2x, h2y, x, y):
        '''Draws a curve relatively to the last point.
        '''
        if self._path is None:
            raise ShoebotError(_("No current path. Use beginpath() first."))
        self._path.relcurveto(h1x, h1y, h2x, h2y, x, y)

    def findpath(self, points, curvature=1.0):

        """Constructs a path between the given list of points.

        Interpolates the list of points and determines
        a smooth bezier path betweem them.

        The curvature parameter offers some control on
        how separate segments are stitched together:
        from straight angles to smooth curves.
        Curvature is only useful if the path has more than  three points.
        """

        # The list of points consists of Point objects,
        # but it shouldn't crash on something straightforward
        # as someone supplying a list of (x,y)-tuples.

        for i, pt in enumerate(points):
            if type(pt) == TupleType:
                points[i] = Point(pt[0], pt[1])

        if len(points) == 0:
            return None
        if len(points) == 1:
            path = self.BezierPath(None)
            path.moveto(points[0].x, points[0].y)
            return path
        if len(points) == 2:
            path = self.BezierPath(None)
            path.moveto(points[0].x, points[0].y)
            path.lineto(points[1].x, points[1].y)
            return path

        # Zero curvature means straight lines.

        curvature = max(0, min(1, curvature))
        if curvature == 0:
            path = self.BezierPath(None)
            path.moveto(points[0].x, points[0].y)
            for i in range(len(points)):
                path.lineto(points[i].x, points[i].y)
            return path

        curvature = 4 + (1.0 - curvature) * 40

        dx = {0: 0, len(points) - 1: 0}
        dy = {0: 0, len(points) - 1: 0}
        bi = {1: -0.25}
        ax = {1: (points[2].x - points[0].x - dx[0]) / 4}
        ay = {1: (points[2].y - points[0].y - dy[0]) / 4}

        for i in range(2, len(points) - 1):
            bi[i] = -1 / (curvature + bi[i - 1])
            ax[i] = -(points[i + 1].x - points[i - 1].x - ax[i - 1]) * bi[i]
            ay[i] = -(points[i + 1].y - points[i - 1].y - ay[i - 1]) * bi[i]

        r = range(1, len(points) - 1)
        r.reverse()
        for i in r:
            dx[i] = ax[i] + dx[i + 1] * bi[i]
            dy[i] = ay[i] + dy[i + 1] * bi[i]

        path = self.BezierPath(None)
        path.moveto(points[0].x, points[0].y)
        for i in range(len(points) - 1):
            path.curveto(points[i].x + dx[i],
                         points[i].y + dy[i],
                         points[i + 1].x - dx[i + 1],
                         points[i + 1].y - dy[i + 1],
                         points[i + 1].x,
                         points[i + 1].y)

        return path

    # Transform and utility

    def beginclip(self, path):
        # FIXME: this save should go into Canvas
        p = self.ClippingPath(path)
        p.draw()
        return p

    def endclip(self):
        p = self.EndClip()
        p.draw()

    def transform(self, mode=None):
        '''
        Set the current transform mode.

        :param mode: CENTER or CORNER'''
        if mode:
            self._canvas.mode = mode
        return self._canvas.mode

    def translate(self, xt, yt, mode=None):
        '''
        Translate the current position by (xt, yt) and
        optionally set the transform mode.

        :param xt: Amount to move horizontally
        :param yt: Amount to move vertically
        :mode: Set the transform mode to CENTER or CORNER
        '''
        self._canvas.translate(xt, yt)
        if mode:
            self._canvas.mode = mode

    def rotate(self, degrees=0, radians=0):
        '''
        Set the current rotation in degrees or radians.

        :param degrees: Degrees to rotate
        :param radians: Radians to rotate
        '''
        # TODO change canvas to use radians
        if radians:
            angle = radians
        else:
            angle = deg2rad(degrees)
        self._canvas.rotate(-angle)

    def scale(self, x=1, y=None):
        '''
        Set a scale at which to draw objects.

        1.0 draws objects at their natural size

        :param x: Scale on the horizontal plane
        :param y: Scale on the vertical plane
        '''
        if not y:
            y = x
        if x == 0:
            # Cairo borks on zero values
            x = 1
        if y == 0:
            y = 1
        self._canvas.scale(x, y)

    def skew(self, x=1, y=0):
        # TODO bring back transform mixin
        t = self._canvas.transform
        t *= cairo.Matrix(1, 0, x, 1, 0, 0)
        t *= cairo.Matrix(1, y, 0, 1, 0, 0)
        self._canvas.transform = t

    def push(self):
        self._canvas.push_matrix()

    def pop(self):
        self._canvas.pop_matrix()

    def reset(self):
        self._canvas.reset_transform()

    # Color

    def outputmode(self):
        '''
        NOT IMPLEMENTED
        '''
        raise NotImplementedError(_("outputmode() isn't implemented yet"))

    def colormode(self, mode=None, crange=None):
        '''Set the current colormode (can be RGB or HSB) and eventually
        the color range.

        If called without arguments, it returns the current colormode.

        :param mode: Color mode, either "rgb", or "hsb"
        :param crange: Maximum scale value for color, e.g. 1.0 or 255

        :return: Returns the current color mode.
        '''
        if mode is not None:
            if mode == "rgb":
                self.color_mode = RGB
            elif mode == "hsb":
                self.color_mode = HSB
            else:
                raise NameError(_("Only RGB and HSB colormodes are supported."))
        if crange is not None:
            self.color_range = crange
        return self.color_mode

    def colorrange(self, crange):
        '''By default colors range from 0.0 - 1.0 using colorrange
        other defaults can be used, e.g. 0.0 - 255.0

        :param crange: Color range of 0.0 - 255:
        >>> colorrange(256)
        '''
        self.color_range = float(crange)

    def fill(self, *args):
        '''Sets a fill color, applying it to new paths.

        :param args: color in supported format
        '''
        if args is not None:
            self._canvas.fillcolor = self.color(*args)
        return self._canvas.fillcolor

    def nofill(self):
        ''' Stop applying fills to new paths.'''
        self._canvas.fillcolor = None

    def stroke(self, *args):
        '''Set a stroke color, applying it to new paths.

        :param args: color in supported format
        '''
        if args is not None:
            self._canvas.strokecolor = self.color(*args)
        return self._canvas.strokecolor

    def nostroke(self):
        ''' Stop applying strokes to new paths.

        :return: stroke color before nostroke was called.
        '''
        c = self._canvas.strokecolor
        self._canvas.strokecolor = None
        return c

    def strokewidth(self, w=None):
        '''Set the stroke width.

        :param w: Stroke width.
        :return: If no width was specified then current width is returned.
        '''
        if w is not None:
            self._canvas.strokewidth = w
        else:
            return self._canvas.strokewidth

    def background(self, *args):
        '''Set the background color.

        :param color: See color() function for supported color formats.
        '''
        self._canvas.background = self.color(*args)

    # Text

    def font(self, fontpath=None, fontsize=None):
        '''Set the font to be used with new text instances.

        :param fontpath: path to truetype or opentype font.
        :param fontsize: size of font

        :return: current current fontpath (if fontpath param not set)
        Accepts TrueType and OpenType files. Depends on FreeType being
        installed.'''
        if fontpath is not None:
            self._canvas.fontfile = fontpath
        else:
            return self._canvas.fontfile
        if fontsize is not None:
            self._canvas.fontsize = fontsize

    def fontsize(self, fontsize=None):
        '''
        Set or return size of current font.

        :param fontsize: Size of font.
        :return: Size of font (if fontsize was not specified)
        '''
        if fontsize is not None:
            self._canvas.fontsize = fontsize
        else:
            return self._canvas.fontsize

    def text(self, txt, x, y, width=None, height=1000000, outline=False, draw=True, **kwargs):
        '''
        Draws a string of text according to current font settings.

        :param txt: Text to output
        :param x: x-coordinate of the top left corner
        :param y: y-coordinate of the top left corner
        :param width: text width
        :param height: text height
        :param outline: If True draws outline text (defaults to False)
        :param draw: Set to False to inhibit immediate drawing (defaults to True)
        :return: Path object representing the text.
        '''
        txt = self.Text(txt, x, y, width, height, outline=outline, ctx=None, **kwargs)
        if outline:
            path = txt.path
            if draw:
                path.draw()
            return path
        else:
            return txt

    def textpath(self, txt, x, y, width=None, height=1000000, draw=False, **kwargs):
        '''
        Generates an outlined path of the input text.

        :param txt: Text to output
        :param x: x-coordinate of the top left corner
        :param y: y-coordinate of the top left corner
        :param width: text width
        :param height: text height
        :param draw: Set to False to inhibit immediate drawing (defaults to False)
        :return: Path object representing the text.
        '''
        txt = self.Text(txt, x, y, width, height, enableRendering=False, **kwargs)
        path = txt.path
        if draw:
            path.draw()
        return path

    def textmetrics(self, txt, width=None, height=None, **kwargs):
        '''

        :return: the width and height of a string of text as a tuple
        according to current font settings.
        '''
        # for now only returns width and height (as per Nodebox behaviour)
        # but maybe we could use the other data from cairo
        txt = self.Text(txt, 0, 0, width, height, enableRendering=False, **kwargs)
        return txt.metrics

    def textwidth(self, txt, width=None):
        '''

        :return: the width of a string of text according to the current
        font settings.
        '''
        w = width
        return self.textmetrics(txt, width=w)[0]

    def textheight(self, txt, width=None):
        '''Returns the height of a string of text according to the current
        font settings.

        :param txt: string to measure
        :param width: width of a line of text in a block
        '''
        w = width
        return self.textmetrics(txt, width=w)[1]

    def lineheight(self, height=None):
        '''Set text lineheight.

        :param height: line height.
        '''
        if height is not None:
            self._canvas.lineheight = height

    def align(self, align=LEFT):
        '''
        Set text alignment

        :param align: Text alignment (LEFT, CENTER, RIGHT)
        '''
        self._canvas.align = align

    # TODO: Set the framework to setup font options

    def fontoptions(self, hintstyle=None, hintmetrics=None, subpixelorder=None, antialias=None):
        raise NotImplementedError(_("fontoptions() isn't implemented yet"))

    def autotext(self, sourceFile):
        k = KantGenerator(sourceFile, searchpaths=['.', ASSETS_DIR])
        return k.output()

    @property
    def canvas(self):
        """
        Not entirely sure compatible the Shoebot 'canvas' is with Nodebox
        but there you go.
        :return:
        """
        return self._canvas

    def angle(self, x0, y0, x1, y1):
        return geometry.angle(x0, y0, x1, y1)

    def distance(self, x0, y0, x1, y1):
        return geometry.distance(x0, y0, x1, y1)

    def coordinates(self, x0, y0, distance, angle):
        return geometry.coordinates(x0, y0, distance, angle)
