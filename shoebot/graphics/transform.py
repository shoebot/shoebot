import math
import sys
from dataclasses import dataclass, MISSING
from enum import auto, Enum

from affine import Affine

from shoebot.core.state.state import State
from shoebot.core.state.state_value import StateValueContainer
from shoebot.core.state.stateful import Stateful, get_state
from shoebot.core.state.transform import TransformState


# from shoebot.graphics import Point
# TODO - Move Alignments out of transform, but also can't be in bezierpath
# from shoebot.graphics.bezierpath import Alignments


class Transforms(Enum):
    TRANSLATE = auto()
    SCALE = auto()
    ROTATE = auto()
    SKEW = auto()
    PUSH = auto()
    POP = auto()


import locale, gettext

APP = "shoebot"
DIR = sys.prefix + "/share/shoebot/locale"
locale.setlocale(locale.LC_ALL, "")
gettext.bindtextdomain(APP, DIR)
# gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext


class Transform(StateValueContainer):

    # NOTE:  This is needed, since at the very least,
    # BezierPath.transform returns a Transform instance
    # So, this means that Context will probably need a stateful_value
    def __init__(self, transform=None):
        if transform is None:
            affine_transform = Affine.identity()
        elif isinstance(transform, Transform):
            affine_transform = get_state(transform).affine_transform
        elif isinstance(transform, Affine):
            affine_transform = transform
        elif isinstance(transform, (list, tuple)) and len(transform) == 6:
            affine_transform = Affine(*transform)
        else:
            raise ValueError("Invalid transform input: %s." % transform)

        transform_data = TransformState(affine_transform=affine_transform)
        StateValueContainer.__init__(self, "_affine_transform", transform_data)

    def copy(self):
        return Transform(self)
    #
    # def invert(self):
    #     self.matrix = ~self.matrix
    #
    # def append(self, other):
    #     if isinstance(other, Transform):
    #         other = other.matrix
    #     self.matrix *= other
    #
    # def prepend(self, other):
    #     if isinstance(other, Transform):
    #         other = other.matrix
    #     self.matrix = other * self.matrix
    #
    def translate(self, x, y):
        print("translate", self, x, y)
        state = get_state(self)
        state.affine_transform = state.affine_transform * Affine.translation(x, y)
    #
    # def rotate(self, degrees=0, radians=0):
    #     if degrees:
    #         radians = math.radians(degrees)
    #     self.matrix *= Affine.rotation(radians)
    #
    # def scale(self, x, y=None):
    #     if y is None:
    #         y = x
    #     self.matrix *= Affine.scale(x, y)
    #
    # def skew(self, x, y=0):
    #     x_rad = math.radians(x)
    #     y_rad = math.radians(y)
    #     self.matrix *= Affine.shear(x_rad, y_rad)
    #
    # def transformPoint(self, point: Point):
    #     # CamelCase for compatibility with nodebox
    #     return self.matrix * point.xy
    #
    # def tranformBezierPath(self, path):
    #     """Transforms a BezierPath using this transform."""
    #     raise NotImplementedError("This method is not implemented yet.")

    def __repr__(self):
        affine_transform = get_state(self).affine_transform
        return f"<{type(self).__name__} {affine_transform}>"

    def __iter__(self):
        affine_transform = get_state(self).affine_transform
        return iter((affine_transform.a, affine_transform.b,
                     affine_transform.c, affine_transform.d,
                     affine_transform.e, affine_transform.f))

    def __eq__(self, other):
        return get_state(self) == get_state(other)
