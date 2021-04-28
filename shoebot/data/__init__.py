#!/usr/bin/env python3

# This file is part of Shoebot.
# Copyright (C) 2009 the Shoebot authors
# See the COPYING file for the full license text.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
#   The name of the author may not be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED
#   WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#   MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
#   EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#   OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
Data structures for use in Shoebot

These are 'agnostic' classes for representing primitive shapes, paths, colors,
transforms, text and image objects, live variables and user interaction
elements (such as pointing devices).

The drawing objects could benefit from an actual, proper Python library to
handle them. We're anxiously awaiting for the lib2geom Python bindings :-)

"""
import sys

from . import geometry as geo
from shoebot.core.backend import cairo
from .basecolor import (
    BUTT,
    ROUND,
    SQUARE,
    BEVEL,
    MITER,
    CMYK,
    HSB,
    RGB,
    Color,
    ColorMixin,
)
from .bezier import (
    ARC,
    CLOSE,
    CURVETO,
    ELLIPSE,
    LINETO,
    MOVETO,
    RCURVETO,
    RLINETO,
    RMOVETO,
    BezierPath,
    ClippingPath,
    EndClip,
    PathElement,
)
from .grob import Grob, CENTER, CORNER, CORNERS
from .img import Image
from .point import Point
from .transforms import Transform
from .variable import BOOLEAN, BUTTON, NUMBER, TEXT, Variable

try:
    from .typography import Text
except ImportError as e:
    Text = None
    print(_("Typography not available ", e), file=sys.stderr)

LEFT = "left"
RIGHT = "right"


class ShoebotError(Exception):
    pass


class NodeBoxError(ShoebotError):
    pass
