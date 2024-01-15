from typing import Optional, List

from .point import Point
from .color import Color

from enum import Enum, auto

from ..core.state.bezierpath import BezierPathState
from ..core.state.stateful import Stateful


class Alignments(Enum):
    CENTER = auto()
    CORNER = auto()
    CORNERS = auto()
class StrokeCaps(Enum):
    BUTT = auto()
    ROUND = auto()
    SQUARE = auto()

class StrokeJoins(Enum):
    BEVEL = auto()
    ROUND = auto()
    MITER = auto()

class BlendModes(Enum):
    OVER = auto()
    MULTIPLY = auto()
    SCREEN = auto()
    OVERLAY = auto()
    DARKEN = auto()
    LIGHTEN = auto()
    COLORDODGE = auto()
    COLORBURN = auto()
    HARDLIGHT = auto()
    SOFTLIGHT = auto()
    DIFFERENCE = auto()
    EXCLUSION = auto()
    HUE = auto()
    SATURATION = auto()
    COLOR = auto()
    LUMINOSITY = auto()
    IN = auto()
    OUT = auto()
    ATOP = auto()
    XOR = auto()
    ADD = auto()
    SATURATE = auto()

class PathElementTypes(Enum):
    # TODO - review the types, we may need less.
    ARC = auto()
    CLOSE = auto()
    CURVETO = auto()
    ELLIPSE = auto()
    LINETO = auto()
    MOVETO = auto()
    RCURVETO = auto()
    RLINETO = auto()
    RMOVETO = auto()


class BezierPath(Stateful):
    def __init__(self, context, *args, **kwargs):
        self._context = context

        if args and isinstance(args[0], BezierPath):
            # Copy constructor
            # TODO - check compatibility
            other: BezierPath = args[0]
            state = other.__state__.copy()
            self._elements = list(other._elements)
        else:
            state = BezierPathState.from_kwargs(**kwargs)
            self._elements = []

        super().__init__(state, context.__state_stack__)  # noqa

    # We need a way of specifying that the thing doing the reading/writing is a Stateful
    # object - and handle sorting out state with it.
    fill: Color = BezierPathState.readwrite_state_value_property(Color)
    stroke: Color = BezierPathState.readwrite_state_value_property(Color)

    # pen: Color = BezierPathState.readwrite_property()
    closed: bool = BezierPathState.readonly_property()

    # TODO _ check these:
    def append(self, element):
        if isinstance(element, PathElement):
            self._elements.append(element)
        else:
            raise ValueError(_("append only accepts PathElements"))
    def copy(self):
        return BezierPath(self._context, self)

    def moveto(self, x, y):
        self.append(PathElement(PathElementTypes.MOVETO, ((x, y),)))

    def relmoveto(self, x, y):
        self.append(PathElement(PathElementTypes.RMOVETO, ((x, y),)))

    def lineto(self, x, y):
        self.append(PathElement(PathElementTypes.LINETO, ((x, y),)))

    def rellineto(self, x, y):
        self.append(PathElement(PathElementTypes.RLINETO, ((x, y),)))

    def line(self, x1, y1, x2, y2):
        self.moveto(x1, y1)
        self.lineto(x2, y2)

    def curveto(self, x1, y1, x2, y2, x3, y3):
        self.append(PathElement(PathElementTypes.CURVETO, (x1, y1), (x2, y2), (x3, y3)))

    def relcurveto(self, x1, y1, x2, y2, x3, y3):
        self.append(PathElement(PathElementTypes.RCURVETO, (x1, y1), (x2, y2), (x3, y3)))
    #
    # def arc(self, x, y, radius, angle1, angle2):
    #     self.append(PathElement(PathElementTypes.ARC, x, y, radius, angle1, angle2))

    def closepath(self):
        if self._elements:
            pt = self[0]
            self.append(PathElement(PathElementTypes.CLOSE))
            self.__state__.closed = True
        # TODO - do we want PathElement.CLOSE, we have __state__.closed as well.
        # TODO - is this right, if we have no elements ?
        # TODO - this should check the last element isn't a CLOSE
        # TODO - should we moveto the first point ?

    # def ellipse(self, x, y, w, h, ellipsemode=Alignments.CORNER):
    # TODO - ellipse should be implemented in terms of Shoebot drawing commands.
    #     # convert values if ellipsemode is not CORNER
    #     if ellipsemode == CENTER:
    #         x = x - (w / 2)
    #         y = y - (h / 2)
    #     elif ellipsemode == CORNERS:
    #         w = w - x
    #         h = h - y
    #     self.append(PathElement(ELLIPSE, x, y, w, h))
    #     self.closed = True
    def rect(self, x, y, w, h, roundness=0.0, rectmode=Alignments.CORNER):
        # convert values if rectmode is not CORNER
        if rectmode == Alignments.CENTER:
            x = x - (w / 2)
            y = y - (h / 2)
        elif rectmode == Alignments.CORNERS:
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

    def draw(self):
        self._context.canvas.draw_path(self)

    def __getitem__(self, item):
        return self._elements[item]


class ClippingPath(BezierPath):
    pass

class EndClip:
    pass


def verify_len(what, argname, expected_len, arg):
    # TODO - move somewhere sensible.
    if expected_len != len(arg):
        raise ValueError(f"{what} requires {expected_len} {argname}s, got {arg}")

class PathElement:
    def __init__(self, cmd: PathElementTypes, pts: Optional[List[Point]] = None):
        # TODO - this has all the relative versions - it may be better to have
        # store something like a "mode" for relative/absolute - and possibly
        # that may not even live in here.
        self.cmd = cmd
        if cmd in (
                PathElementTypes.MOVETO,
                PathElementTypes.RMOVETO,
                PathElementTypes.LINETO,
                PathElementTypes.RLINETO
        ):
            verify_len(cmd.name, "pts", 1, pts)
            self.x, self.y = pts[0]
            self.ctrl1 = Point(pts[0])
            self.ctrl2 = Point(pts[0])
        elif cmd in (PathElementTypes.CURVETO, PathElementTypes.RCURVETO):
            verify_len(cmd.name, "pts", 3, pts)
            self.x, self.y = pts[2]
            self.ctrl1 = Point(pts[0])
            self.ctrl2 = Point(pts[1])
        elif cmd == PathElementTypes.CLOSE:
            assert pts is None, "CLOSE command should not have any points"
            self.x = self.y = 0.0
            self.ctrl1 = Point()
            self.ctrl2 = Point()
        else:
            # TODO - Nodebox actually lets you have an unknown command here - should we ?
            raise ValueError(f"Unknown PathElement type: {cmd}")
