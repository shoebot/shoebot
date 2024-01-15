import os.path
import sys

from pkg_resources import resource_filename, Requirement

from shoebot.core.backend import cairo
from shoebot.kgp import KantGenerator
from shoebot.graphics import ShoebotError
from shoebot.util.fonts import list_pango_fonts
from shoebot.graphics import (
    geometry,
    Point,
    BezierPath,
    Image,
    RGB,
    HSB,
    CORNER,
    CORNERS,
    CENTER,
    MOVETO,
    RMOVETO,
    LINETO,
    RLINETO,
    CURVETO,
    RCURVETO,
    ARC,
    ELLIPSE,
    CLOSE,
    LEFT,
    RIGHT,
    BUTT,
    ROUND,
    SQUARE,
    BEVEL,
    MITER,
    Color,
    ClippingPath,
    EndClip,
    Transform,
    Grob,
    Text,
)

from .variable import (
    NUMBER,
    TEXT,
    BUTTON,
    BOOLEAN,
    Variable,
)

from math import sin, cos, pi
from math import radians as deg2rad
import random as r

import locale
import gettext

from .contextbase import ContextBase
from ..core.state.context import ContextState
from ..core.state.nodebox import NodeBotContextDefaults
from ..core.state.stateful import Stateful, get_state, get_state_value

SBOT_ROOT = resource_filename(Requirement.parse("shoebot"), "")
APP = "shoebot"
DIR = sys.prefix + "/share/shoebot/locale"
locale.setlocale(locale.LC_ALL, "")
ASSETS_DIR = sys.prefix + "/share/shoebot/data"
gettext.bindtextdomain(APP, DIR)
# gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext

LIB_DIRS = [
    os.path.join(SBOT_ROOT, "local", "share", "shoebot", "lib"),
    os.path.join(SBOT_ROOT, "lib"),
    os.path.join(SBOT_ROOT, "share", "shoebot", "lib"),
    os.path.join(sys.prefix, "share", "shoebot", "lib"),
]
for LIB_DIR in LIB_DIRS:
    if os.path.isdir(LIB_DIR):
        sys.path.append(LIB_DIR)

TOP_LEFT = 1
BOTTOM_LEFT = 2

# Nodebox compatibility shim
sys.path.append(os.path.join(os.path.dirname(__file__), "nodebox-lib"))
sys.path.append(".")  # ximport can work from current dir


class NodeBotContext(ContextBase):
    NORMAL = "1"
    FORTYFIVE = "2"

    PIE = "pie"
    CHORD = "chord"

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

    RGB = RGB
    HSB = HSB

    LEFT = "left"
    RIGHT = "right"

    CENTER = CENTER
    CORNER = CORNER
    CORNERS = CORNERS

    LEFT = "left"
    RIGHT = "right"
    JUSTIFY = "justify"

    NUMBER = NUMBER
    TEXT = TEXT
    BOOLEAN = BOOLEAN
    BUTTON = BUTTON

    inch = 72
    cm = 28.3465
    mm = 2.8346

    # Default mouse values
    MOUSEX = -1
    """The x-value of the mouse cursor coordinates."""
    MOUSEY = -1
    """The y-value of the mouse cursor coordinates."""
    mousedown = False
    """Is True if the mouse button is pressed."""

    # Default key values
    key = "-"
    keycode = 0
    keydown = False

    # Default values
    color_mode = RGB
    color_range = 1

    def __init__(self, canvas=None, namespace=None, vars=None):
        """Nodebot grammar constructor.

        :param canvas: Canvas implementation for output.
        :param namespace: Optionally specify a dict to inject as namespace
        :param vars: Optional dict containing initial values for variables
        """
        defaults = NodeBotContextDefaults()
        ContextBase.__init__(self, canvas, defaults, namespace=namespace, vars=vars)

        # self._autoclosepath = True
        # self._path = None
        #
        # if self._input_device:
        #     # Get constants like KEY_DOWN, KEY_LEFT
        #     for key_name, value in list(self._input_device.get_key_map().items()):
        #         self._namespace[key_name] = value
        #         setattr(self, key_name, value)
        #
        self._canvas.size = None
        if isinstance(namespace, dict) and "FRAME" in namespace:
            try:
                self._frame = int(namespace["FRAME"])
            except ValueError:
                raise ValueError("Frame must be an integer.")
        else:
            self._frame = 1
        #self._set_initial_defaults()  ### TODO Look at these

        canvas.mode = CORNER

    def _set_initial_defaults(self):
        """Set the default values.

        Called at __init__ and at the end of run(), so that new draw
        loop iterations don't take up values left over by the previous
        one.
        """
        # TODO DEFAULT_WIDTH, DEFAULT_HEIGHT
        DEFAULT_WIDTH, DEFAULT_HEIGHT = 800, 800
        # DEFAULT_WIDTH, DEFAULT_HEIGHT = self._canvas.DEFAULT_SIZE
        self.WIDTH = self._namespace.get("WIDTH", DEFAULT_WIDTH)
        self.HEIGHT = self._namespace.get("HEIGHT", DEFAULT_WIDTH)
        if "WIDTH" in self._namespace or "HEIGHT" in self._namespace:
            self.size(self._namespace.get("WIDTH"), self._namespace.get("HEIGHT"))

        #self._transformmode = NodeBot.CENTER

        # TODO implement canvas settings (check Nodebox, these will probably be attributes)
        # self._canvas.settings(
        #     fillcolor=self.color(0.2),
        #     fillrule=None,
        #     strokecolor=None,
        #     strokewidth=1.0,
        #     strokecap=None,
        #     strokejoin=None,
        #     strokedash=None,
        #     dashoffset=0,
        #     blendmode=None,
        #     background=self.color(1, 1, 1),
        #     fontfile="Sans",
        #     fontsize=16,
        #     align=Bot.LEFT,
        #     lineheight=1,
        #     tracking=0,
        #     underline=None,
        #     overline=None,
        #     underlinecolor=None,
        #     overlinecolor=None,
        #     hintstyle=None,
        #     hintmetrics=None,
        #     antialias=None,
        #     subpixelorder=None,
        # )

    # Input GUI callbacks

    def _mouse_button_down(self, button):
        """GUI callback for mouse button down."""
        self._namespace["mousedown"] = True

    def _mouse_button_up(self, button):
        """GUI callback for mouse button up."""
        self._namespace["mousedown"] = self._input_device.mouse_down

    def _mouse_pointer_moved(self, x, y):
        """GUI callback for mouse moved."""
        self._namespace["MOUSEX"] = x
        self._namespace["MOUSEY"] = y

    def _key_pressed(self, key, keycode):
        """GUI callback for key pressed."""
        self._namespace["key"] = key
        self._namespace["keycode"] = keycode
        self._namespace["keydown"] = True

    def _key_released(self, key, keycode):
        """GUI callback for key released."""
        self._namespace["keydown"] = self._input_device.key_down

    # Functions for override #####

    # Classes #####

    def _makeInstance(self, clazz, args, kwargs):
        """Creates an instance of a class defined in this document.

        This method sets the context of the object to the current
        context.
        """
        inst = clazz(self, *args, **kwargs)
        return inst

    def EndClip(self, *args, **kwargs):
        return self._makeInstance(EndClip, args, kwargs)

    def BezierPath(self, *args, **kwargs):
        return self._makeInstance(BezierPath, args, kwargs)

    def ClippingPath(self, *args, **kwargs):
        return self._makeInstance(ClippingPath, args, kwargs)

    def Rect(self, *args, **kwargs):
        return self._makeInstance(Rect, args, kwargs)

    def Oval(self, *args, **kwargs):
        return self._makeInstance(Oval, args, kwargs)

    def Ellipse(self, *args, **kwargs):
        return self._makeInstance(Ellipse, args, kwargs)

    def Color(self, *args, **kwargs):
        return Color(*args, **kwargs)

    def Image(self, *args, **kwargs):
        return self._makeInstance(Image, args, kwargs)

    def Text(self, *args, **kwargs):
        return self._makeInstance(Text, args, kwargs)

    # Variables #####

    def var(
        self,
        name,
        type,
        default=None,
        min=0,
        max=255,
        value=None,
        step=None,
        label=None,
    ):
        v = Variable(
            name,
            type,
            default=default,
            min=min,
            max=max,
            value=value,
            step=step,
            label=label,
        )
        return self._addvar(v)

    # Utility #####

    def color(self, *args):
        """
        :param args: color in a supported format.

        :return: Color object containing the color.
        """
        return self.Color(mode=self.color_mode, color_range=self.color_range, *args)

    choice = r.choice

    def random(self, v1=None, v2=None):
        # ipsis verbis from Nodebox
        if v1 is not None and v2 is None:
            if isinstance(v1, float):
                return r.random() * v1
            else:
                return int(r.random() * v1)
        elif v1 is not None and v2 is not None:
            if isinstance(v1, float) or isinstance(v2, float):
                start = min(v1, v2)
                end = max(v1, v2)
                return start + r.random() * (end - start)
            else:
                start = min(v1, v2)
                end = max(v1, v2) + 1
                return int(start + r.random() * (end - start))
        else:
            # No values means 0.0 -> 1.0
            return r.random()

    def grid(self, cols, rows, colSize=1, rowSize=1, shuffled=False):
        """Returns an iterator that contains coordinate tuples.

        This command can be used to quickly create grid-like structures.
        A common usage pattern is:

        .. code-block:: python

            for x, y in grid(10,10,12,12):
                rect(x,y, 10,10)
        """
        from random import shuffle

        rowRange = list(range(int(rows)))
        colRange = list(range(int(cols)))
        if shuffled:
            shuffle(rowRange)
            shuffle(colRange)
        for y in rowRange:
            for x in colRange:
                yield (x * colSize, y * rowSize)

    def files(self, path="*"):
        """Returns a list of files.

        Use wildcards to specify which files to pick, e.g. ``f =
        files('*.gif')``.

        :param path: wildcard to use in file list
        :return: list of file names
        """
        return glob(path)

    def snapshot(self, target=None, defer=None, autonumber=False):
        """Save the contents of current surface into a file or cairo
        surface/context.

        :param filename: Can be a filename or a Cairo surface.
        :param defer: When to snapshot, if set to True waits until the frame has finished rendering.
        :param autonumber: If true then a number will be appended to the filename.
        """
        if autonumber:
            file_number = self._frame
        else:
            file_number = None

        if isinstance(target, cairo.Surface):
            # snapshot to Cairo surface
            if defer is None:
                self._canvas.snapshot(target, defer)
                defer = False
            ctx = cairo.Context(target)
            # this used to be self._canvas.snapshot, but I couldn't make it work.
            # self._canvas.snapshot(target, defer)
            # TODO: check if this breaks when taking more than 1 snapshot
            self._canvas._drawqueue.render(ctx)
            return
        elif target is None:
            # If nothing specified, use a default filename from the script name
            script_file = self._namespace.get("__file__")
            if script_file:
                target = os.path.splitext(script_file)[0] + ".svg"
                file_number = True

        if target:
            # snapshot to file, target is a filename
            if defer is None:
                defer = True
            self._canvas.snapshot(target, defer=defer, file_number=file_number)
        else:
            raise ShoebotError(
                "Image not saved: no target, filename or default to save to.",
            )

    def show(self, format="png", as_data=False):
        """Returns an Image object of the current surface.

        Used for displaying output in Jupyter notebooks. Adapted from
        the cairo- jupyter project.
        """

        from io import BytesIO

        b = BytesIO()

        if format == "png":
            from IPython.display import Image

            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.WIDTH, self.HEIGHT)
            self.snapshot(surface)
            surface.write_to_png(b)
            b.seek(0)
            data = b.read()
            if as_data:
                return data
            else:
                return Image(data)
        elif format == "svg":
            from IPython.display import SVG

            surface = cairo.SVGSurface(b, self.WIDTH, self.HEIGHT)
            surface.restrict_to_version(cairo.SVGVersion.VERSION_1_2)
            surface.finish()
            b.seek(0)
            data = b.read()
            if as_data:
                return data
            else:
                return SVG(data)

    def ximport(self, libName):
        """Import Nodebox libraries.

        The libraries get _ctx, which provides
        them with the nodebox API.

        :param libName: Library name to import
        """
        # from Nodebox
        lib = __import__(libName)
        self._namespace[libName] = lib
        lib._ctx = self
        return lib

    # Core functions ####

    def size(self, w=None, h=None):
        """Set the canvas size.

        Only the first call will actually be effective.

        :param w: Width
        :param h: height
        """

        if not w:
            w = self._canvas.width
        if not h:
            h = self._canvas.height
        if not w and not h:
            return self._canvas.width, self._canvas.height

        # FIXME: Updating in all these places seems a bit hacky
        w, h = self._canvas.set_size(w, h)
        self._namespace["WIDTH"] = w
        self._namespace["HEIGHT"] = h
        self.WIDTH = w  # Added to make evolution example work
        self.HEIGHT = h  # Added to make evolution example work

    def speed(self, framerate=None):
        """Set animation framerate.

        :param framerate: Frames per second to run bot.
        :return: Current framerate of animation.
        """
        if framerate is not None:
            self._speed = framerate
            self._dynamic = True
        else:
            return self._speed

    @property
    def FRAME(self):
        return self._frame

    @property
    def _ns(self):
        """Nodebox1 API way of fetching namespace from _ctx."""
        return self._namespace

    # Drawing

    # Image

    def image(
        self,
        path,
        x,
        y,
        width=None,
        height=None,
        alpha=1.0,
        data=None,
        draw=True,
        **kwargs,
    ):
        """Draws a image with (x,y) as the top left corner.

        If width and height are specified, resize the image to fit.

        form path, in x,y and resize it to width, height dimensions.

        :param path: location of the image on disk
        :param x: x-coordinate of the top left corner
        :param y: y-coordinate of the top left corner
        :param width: image width (leave blank to use its original width)
        :param height: image height (leave blank to use its original height)
        :param alpha: opacity
        :param data: image data to load. Use this instead of ``path`` if you want to load an image from memory or have another source (e.g. using the `web` library)
        :param draw: whether to place the image immediately on the canvas or not
        :type path: filename
        :type x: float
        :type y: float
        :type width: float or None
        :type height: float or None
        :type alpha: float
        :type data: binary data
        :type draw: bool
        """

        return self.Image(path, x, y, width, height, alpha, data, **kwargs)

    def imagesize(self, path):
        """
        :param path: Path to image file.
        :return: image size as a (width, height) tuple
        """
        from PIL import Image as PILImage

        with PILImage.open(path) as img:
            return img.size

    # Paths

    def rect(self, x, y, width, height, roundness=0.0, draw=True, **kwargs):
        """Draw a rectangle.

        :param x: top left x-coordinate
        :param y: top left y-coordinate
        :param width: rectangle width
        :param height: rectangle height
        :param roundness: rounded corner radius
        :param boolean draw: whether to draw the shape on the canvas or not
        :param fill: fill color
        :return: BezierPath representing the rectangle
        """
        path = self.BezierPath(**kwargs)
        path.rect(x, y, width, height, roundness, self.rectmode)
        if draw:
            path.draw()
        return path

    def rectmode(self, mode=None):
        """Get or set the current rectmode.

        :param mode: the mode to draw new rectangles in
        :type mode: CORNER, CENTER or CORNERS
        :return: current rectmode value
        """
        if mode in (self.CORNER, self.CENTER, self.CORNERS):
            self.rectmode = mode
            return self.rectmode
        elif mode is None:
            return self.rectmode
        else:
            raise ShoebotError(_("rectmode: invalid input"))

    def ellipse(self, x, y, width, height, draw=True, **kwargs):
        """Draw an ellipse.

        :param x: top left x-coordinate
        :param y: top left y-coordinate
        :param width: ellipse width
        :param height: ellipse height
        :param boolean draw: whether to draw the shape on the canvas or not
        :return: BezierPath representing the ellipse
        """

        path = self.BezierPath(**kwargs)
        path.ellipse(x, y, width, height, self.ellipsemode)
        if draw:
            path.draw()
        return path

    oval = ellipse

    def circle(self, x, y, diameter, draw=True, **kwargs):
        """Draw a circle.

        :param x: x-coordinate of the top left corner
        :param y: y-coordinate of the top left corner
        :param diameter: circle diameter
        :param boolean draw: whether to draw the shape on the canvas or not
        :return: BezierPath representing the circle
        """
        return self.ellipse(x, y, diameter, diameter, draw, **kwargs)

    def ellipsemode(self, mode=None):
        """Set the current ellipse drawing mode.

        :param mode: CORNER, CENTER, CORNERS
        :return: ellipsemode if mode is None or valid.
        """
        if mode in (self.CORNER, self.CENTER, self.CORNERS):
            self.ellipsemode = mode
            return self.ellipsemode
        elif mode is None:
            return self.ellipsemode
        else:
            raise ShoebotError(_("ellipsemode: invalid input"))

    def line(self, x1, y1, x2, y2, draw=True, **kwargs):
        """Draw a line from (x1,y1) to (x2,y2).

        :param x1: x-coordinate of the first point
        :param y1: y-coordinate of the first point
        :param x2: x-coordinate of the second point
        :param y2: y-coordinate of the second point
        :param boolean draw: whether to draw the shape on the canvas or not
        :return: BezierPath representing the line
        """
        self.beginpath(**kwargs)
        self.moveto(x1, y1)
        self.lineto(x2, y2)
        return self.endpath(draw=draw, closed=False)

    def arc(self, x, y, radius, angle1, angle2, type=CHORD, draw=True, **kwargs):
        """Draw an arc with center (x,y) between two angles in degrees.

        :param x1: start x-coordinate
        :param y1: start y-coordinate
        :param radius: arc radius
        :param angle1: start angle
        :param angle2: end angle
        """
        self.beginpath(**kwargs)
        if type == self.PIE:
            # find the coordinates of the start and end points
            x1 = x + radius * cos(deg2rad(angle1))
            y1 = y + radius * sin(deg2rad(angle1))
            x2 = x + radius * cos(deg2rad(angle2))
            y2 = y + radius * sin(deg2rad(angle2))
            self.moveto(x2, y2)
            self.lineto(x, y)
            self.lineto(x1, y1)
        # self.moveto(x, y)  # uncomment to fix the "empty path" issue
        self.arcto(x, y, radius, angle1, angle2)
        return self.endpath(draw=draw)

    def arrow(self, x, y, width, type=NORMAL, draw=True, **kwargs):
        """Draw an arrow.

        :param x: arrow tip x-coordinate
        :param y: arrow tip y-coordinate
        :param width: arrow width (also sets height)
        :param type: arrow type
        :type type: NORMAL or FORTYFIVE
        :param boolean draw: whether to draw the shape on the canvas or not
        :return: BezierPath object representing the arrow
        """
        # Taken from Nodebox
        self.beginpath(**kwargs)
        if type == self.NORMAL:
            head = width * 0.4
            tail = width * 0.2
            self.moveto(x, y)
            self.lineto(x - head, y + head)
            self.lineto(x - head, y + tail)
            self.lineto(x - width, y + tail)
            self.lineto(x - width, y - tail)
            self.lineto(x - head, y - tail)
            self.lineto(x - head, y - head)
            self.lineto(x, y)
        elif type == self.FORTYFIVE:
            head = 0.3
            tail = 1 + head
            self.moveto(x, y)
            self.lineto(x, y + width * (1 - head))
            self.lineto(x - width * head, y + width)
            self.lineto(x - width * head, y + width * tail * 0.4)
            self.lineto(x - width * tail * 0.6, y + width)
            self.lineto(x - width, y + width * tail * 0.6)
            self.lineto(x - width * tail * 0.4, y + width * head)
            self.lineto(x - width, y + width * head)
            self.lineto(x - width * (1 - head), y)
            self.lineto(x, y)
        else:
            raise NameError(
                _("arrow: available types for arrow() are NORMAL and FORTYFIVE\n"),
            )
        return self.endpath(draw=draw)

    def star(self, x, y, points=20, outer=100, inner=50, draw=True, **kwargs):
        """Draws a star.

        :param x: center x-coordinate
        :param y: center y-coordinate
        :param points: amount of points
        :param outer: outer radius
        :param inner: inner radius
        :param boolean draw: whether to draw the shape on the canvas or not
        """

        # Taken from Nodebox.
        self.beginpath(**kwargs)
        self.moveto(x, y + outer)

        for i in range(1, int(2 * points)):
            angle = i * pi / points
            px = sin(angle)
            py = cos(angle)
            if i % 2:
                radius = inner
            else:
                radius = outer
            px = x + radius * px
            py = y + radius * py
            self.lineto(px, py)

        return self.endpath(draw)

    # Path
    # Path functions taken from Nodebox and modified

    def beginpath(self, x=None, y=None, **kwargs):
        """Start a new Bézier path.

        This command is needed before any other path drawing commands.

        :param x: x-coordinate of the starting point
        :param y: y-coordinate of the starting point
        :type x: float or None
        :type y: float or None
        """
        self._path = self.BezierPath(**kwargs)
        # if we have arguments, do a moveto too
        if x is not None and y is not None:
            self._path.moveto(x, y)

    def moveto(self, x, y):
        """Move the Bézier "pen" to the specified point without drawing.

        :param x: x-coordinate of the point to move to
        :param y: y-coordinate of the point to move to
        :type x: float
        :type y: float
        """
        if self._path is None:
            raise ShoebotError(_("No current path. Use beginpath() first."))
        self._path.moveto(x, y)

    def lineto(self, x, y):
        """Draw a line from the pen's current point.

        :param x: x-coordinate of the point to draw to
        :param y: y-coordinate of the point to draw to
        :type x: float
        :type y: float
        """
        if self._path is None:
            raise ShoebotError(_("No current path. Use beginpath() first."))
        self._path.lineto(x, y)

    def curveto(self, x1, y1, x2, y2, x3, y3):
        if self._path is None:
            raise ShoebotError(_("No current path. Use beginpath() first."))
        self._path.curveto(x1, y1, x2, y2, x3, y3)

    def arcto(self, x, y, radius, angle1, angle2):
        if self._path is None:
            raise ShoebotError(_("No current path. Use beginpath() first."))
        # use degrees by default
        angle1 = deg2rad(angle1)
        angle2 = deg2rad(angle2)
        self._path.arc(x, y, radius, angle1, angle2)

    def closepath(self):
        if self._path is None:
            raise ShoebotError(_("No current path. Use beginpath() first."))
        if not self._path.closed:
            self._path.closepath()
            self._path.closed = True

    def endpath(self, draw=True, closed=None):
        if self._path is None:
            raise ShoebotError(_("No current path. Use beginpath() first."))
        p = self._path
        if self._autoclosepath is True and closed is not False:
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
        elif hasattr(path, "__iter__"):
            p = self.BezierPath()
            for point in path:
                p.append(point)
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
        """Move relatively to the last point."""
        if self._path is None:
            raise ShoebotError(_("No current path. Use beginpath() first."))
        self._path.relmoveto(x, y)

    def rellineto(self, x, y):
        """Draw a line using relative coordinates."""
        if self._path is None:
            raise ShoebotError(_("No current path. Use beginpath() first."))
        self._path.rellineto(x, y)

    def relcurveto(self, h1x, h1y, h2x, h2y, x, y):
        """Draws a curve relatively to the last point."""
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
            if type(pt) == tuple:
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

        r = list(range(1, len(points) - 1))
        r.reverse()
        for i in r:
            dx[i] = ax[i] + dx[i + 1] * bi[i]
            dy[i] = ay[i] + dy[i + 1] * bi[i]

        path = self.BezierPath(None)
        path.moveto(points[0].x, points[0].y)
        for i in range(len(points) - 1):
            path.curveto(
                points[i].x + dx[i],
                points[i].y + dy[i],
                points[i + 1].x - dx[i + 1],
                points[i + 1].y - dy[i + 1],
                points[i + 1].x,
                points[i + 1].y,
            )

        return path

    # Transform and utility

    def beginclip(self, path):
        """Use a path as a clipping mask.

        All drawing commands between beginclip() and endclip() will be drawn
        inside the clipping mask set by beginclip().

        :param path: the path to be used as a clipping mask
        :type path: BezierPath
        """
        p = self.ClippingPath(path)
        p.draw()
        return p

    def endclip(self):
        """Finish a clipping mask and render the result."""
        p = self.EndClip()
        p.draw()

    def transform(self, mode=None):
        """Set the current transform mode.

        :param mode: the mode to base new transformations on
        :type mode: CORNER or CENTER
        """
        if mode:
            self._canvas.mode = mode
        return self._canvas.mode

    def translate(self, xt, yt):
        """Translate the canvas origin point by (xt, yt).

        :param xt: Amount to move horizontally
        :param yt: Amount to move vertically
        """
        self._canvas.translate(xt, yt)

    def rotate(self, degrees=0, radians=0):
        """Set the current rotation in degrees or radians.

        :param degrees: Degrees to rotate
        :param radians: Radians to rotate
        """
        # TODO change canvas to use radians
        if radians:
            angle = radians
        else:
            angle = deg2rad(degrees)
        self._canvas.rotate(-angle)

    def scale(self, x=1, y=None):
        """Set a scale at which to draw objects.

        1.0 draws objects at their natural size.

        :param x: Scale on the horizontal plane
        :param y: Scale on the vertical plane
        """
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
        """NOT IMPLEMENTED."""
        raise NotImplementedError(
            _("outputmode() isn't implemented; Shoebot does not support CMYK"),
        )

    def colormode(self, mode=None, range=None):
        """Set the current colormode (can be RGB or HSB) and eventually the
        color range.

        If called without arguments, it returns the current colormode.

        :param mode: Color mode to use
        :type mode: RGB or HSB
        :param float crange: Maximum value for the new color range to use
        :return: Current color mode
        """
        if mode is not None:
            if mode == RGB:
                self.color_mode = RGB
            elif mode == HSB:
                self.color_mode = HSB
            else:
                raise NameError(_("Only RGB and HSB colormodes are supported."))
        if range is not None:
            self.color_range = range
        return self.color_mode

    def colorrange(self, crange=None):
        """Sets the current color range.

        The default is 0-1; for a range of 0-255, use ``colorrange(256)``.

        :param float crange: maximum value for new color range
        :return: current range value
        """
        if crange is not None:
            self.color_range = float(crange)
        return self.color_range

    def fill(self, *args):
        """Sets a fill color, applying it to new paths.

        :param args: color in supported format
        """
        if args is not None:
            color = self.color(*args)
            get_state(self).fill = get_state_value(color)
        else:
            # TODO - color from state needed
            color = self.color(get_state(self).fill)
        return color

    def nofill(self):
        """Stop applying fills to new paths.

        :return: fill color before nofill() was called
        """
        c = self._canvas.fillcolor
        self._canvas.fillcolor = None
        return c

    def fillrule(self, r=None):
        """Set the fill rule to use in new paths.

        :param r: fill rule to apply
        :type r: WINDING or EVENODD
        :return: current fill rule value
        """
        if r is not None:
            self._canvas.fillrule = r
        return self._canvas.fillrule

    def stroke(self, *args):
        """Set a stroke color, applying it to new paths.

        :param args: color in supported format
        :return: new stroke color
        """
        if args is not None:
            self._canvas.strokecolor = self.color(*args)
        return self._canvas.strokecolor

    def nostroke(self):
        """Stop applying strokes to new paths.

        :return: stroke color before nostroke() was called
        """
        c = self._canvas.strokecolor
        self._canvas.strokecolor = None
        return c

    def strokewidth(self, w=None):
        """Set the stroke width to be used by stroke().

        :param w: width of the stroke to use
        :return: current stroke width value
        """
        if w is not None:
            self._canvas.strokewidth = w
        return self._canvas.strokewidth

    def strokedash(self, dashes=None, offset=0):
        """Sets the dash pattern to be used by stroke().

        :param list dashes: a sequence specifying alternate lengths of on and off stroke portions
        :param float offset: an offset into the dash pattern at which the stroke should start
        :return: tuple with dashes value and offset
        """
        if dashes is not None:
            self._canvas.strokedash = dashes
        if offset:
            self._canvas.dashoffset = offset
        return self._canvas.strokedash, self._canvas.dashoffset

    def strokecap(self, cap=None):
        """Set the stroke cap.

        :param w: new stroke cap value
        :return: current stroke cap value
        """
        if cap is not None:
            self._canvas.strokecap = cap
        return self._canvas.strokecap

    def strokejoin(self, join=None):
        """Set the stroke join.

        :param w: new stroke join value
        :return: current line join value
        """
        if join is not None:
            self._canvas.strokejoin = join
        return self._canvas.strokejoin

    def background(self, *args):
        """Set the canvas background color.

        :param color: background color to apply
        :return: new background color
        """
        self._canvas.background = self.color(*args)
        return self._canvas.background

    def blendmode(self, mode=None):
        """Set the current blending mode.

        :param mode: mode name (e.g. "multiply")
        """
        if mode:
            self._canvas.blendmode = mode
        return self._canvas.blendmode

    # Text

    def font(self, fontpath=None, fontsize=None, vars=None, *args, **kwargs):
        """Set the font to be used with new text instances.

        :param fontpath: font name (can include styles like "Bold")
        :param fontsize: font size
        :param vars: font variant values, as a dict of axis/value pairs (variable fonts only)
        :param var_XXXX: set variant value (variable fonts only)
        :return: current fontpath (if fontpath param not set)

        Accepts TrueType and OpenType files. Depends on FreeType being
        installed.
        """
        if fontpath is not None:
            # do we have variants set?
            if not vars:
                # make a list of "arg=value" strings to append to the font name below
                variants = [
                    f"{arg.replace('var_', '')}={value}"
                    for arg, value in kwargs.items()
                    if arg.startswith("var_")
                ]
            else:
                # make a list of "arg=value" strings from the provided dict
                variants = [f"{arg}={value}" for arg, value in vars.items()]
            if variants:
                # append to the font string
                # syntax: "Inconsolata @wdth=50,wght=600"
                fontpath += " @" + ",".join(variants)
            self._canvas.fontfile = fontpath

        if fontsize is not None:
            self._canvas.fontsize = fontsize

        return self._canvas.fontfile

    def fontsize(self, fontsize=None):
        """Sets and/or returns the current font size.

        :param fontsize: Font size in pt
        :return: the current font size value
        """
        if fontsize is not None:
            self._canvas.fontsize = fontsize
        return self._canvas.fontsize

    def text(
        self, txt, x, y, width=None, height=1000000, outline=False, draw=True, **kwargs
    ):
        """Draws a string of text according to the current font settings.

        :param txt: Text to output
        :param x: x-coordinate of the top left corner
        :param y: y-coordinate of the top left corner
        :param width: text width
        :param height: text height
        :param outline: If True, draws a path instead of a text object (defaults to False)
        :param draw: Set to False to inhibit immediate drawing (defaults to True)
        :return: Path object representing the text.
        """
        txt = self.Text(txt, x, y, width, height, outline=outline, ctx=None, **kwargs)
        if outline:
            path = txt.path
            if draw:
                path.draw()
            return path
        return txt

    def textpath(self, txt, x, y, width=None, height=1000000, draw=False, **kwargs):
        """Generates an outlined path of the input text.

        :param txt: Text to output
        :param x: x-coordinate of the top left corner
        :param y: y-coordinate of the top left corner
        :param width: text width
        :param height: text height
        :param draw: Set to False to inhibit immediate drawing (defaults to False)
        :return: BezierPath representing the text
        """
        txt = self.Text(txt, x, y, width, height, draw=False, **kwargs)
        path = txt.path
        if draw:
            path.draw()
        return path

    def textmetrics(self, txt, width=None, height=None, **kwargs):
        """Returns the dimensions of the text box of a string of text,
        according to the current font settings.

        :return: (width, height) tuple
        """
        # for now only returns width and height (as per Nodebox behaviour)
        # but maybe we could use the other data from cairo
        txt = self.Text(txt, 0, 0, width, height, draw=False, **kwargs)
        return txt.metrics

    def textbounds(self, txt, width=None, height=None, **kwargs):
        """Returns the dimensions of the actual shapes (inked part) of a string
        of text, according to the current font settings.

        :return: (width, height) tuple
        """
        txt = self.Text(txt, 0, 0, width, height, draw=False, **kwargs)
        return txt.bounds

    def textwidth(self, txt, width=None, **kwargs):
        """Returns the width of a string of text according to the current font
        settings.

        :return:
        """
        w = width
        return self.textmetrics(txt, width=w, **kwargs)[0]

    def textheight(self, txt, width=None, **kwargs):
        """Returns the height of a string of text according to the current font
        settings.

        :param txt: string to measure
        :param width: width of a line of text in a block
        """
        w = width
        return self.textmetrics(txt, width=w, **kwargs)[1]

    def lineheight(self, height=None):
        """Set text lineheight.

        :param height: line height.
        """
        if height is not None:
            self._canvas.lineheight = height
        return self._canvas.lineheight

    def align(self, align=LEFT):
        """Set text alignment.

        :param align: Text alignment (LEFT, CENTER, RIGHT)
        """
        self._canvas.align = align
        return self._canvas.align

    def fontoptions(
        self,
        hintstyle=None,
        hintmetrics=None,
        subpixelorder=None,
        antialias=None,
    ):
        """Set font rendering options.

        :param hintstyle: Hinting style (NONE, SLIGHT, MEDIUM, FULL)
        :param hintmetrics: Quantize font metrics (ON, OFF)
        :param antialias: Antialiasing type (NONE, GRAY, SUBPIXEL, FAST, GOOD, BEST)
        :param subpixelorder: Order of pixels when antialiasing in SUBPIXEL mode (RGB, BGR, VRGB, VBGR)
        """
        self._canvas.hintstyle = hintstyle
        self._canvas.hintmetrics = hintmetrics
        self._canvas.subpixelorder = subpixelorder
        self._canvas.antialias = antialias

    def fontnames(self):
        return list_pango_fonts()

    def autotext(self, sourceFile):
        k = KantGenerator(sourceFile, searchpaths=[".", ASSETS_DIR])
        return k.output()

    @property
    def canvas(self):
        """Not entirely sure compatible the Shoebot 'canvas' is with Nodebox
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
