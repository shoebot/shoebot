#!/usr/bin/env python2

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


class ShoebotError(Exception):
    pass


class ShoebotScriptError(Exception):
    pass


class NodeBoxError(ShoebotError):
    pass


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
        raise NodeBoxError, _("Don't know how to copy '%s'.") % v


def _copy_attrs(source, target, attrs):
    for attr in attrs:
        setattr(target, attr, _copy_attr(getattr(source, attr)))


import geometry as geo
from point import Point
from basecolor import Color, ColorMixin
from grob import Grob
from bezier import BezierPath, PathElement, ClippingPath, EndClip
try:
    from typography import Text
except ImportError as e:
    Text = None
    print('Typography not available ', e)
from img import Image
from variable import Variable, NUMBER, TEXT, BOOLEAN, BUTTON
from transforms import Transform

MOVETO = "moveto"
RMOVETO = "rmoveto"
LINETO = "lineto"
RLINETO = "rlineto"
CURVETO = "curveto"
RCURVETO = "rcurveto"
ARC = 'arc'
ELLIPSE = 'ellipse'
CLOSE = "close"

CENTER = 'center'
CORNER = 'corner'
CORNERS = "corners"

LEFT = 'left'
RIGHT = 'right'

RGB = "rgb"
HSB = "hsb"
CMYK = "cmyk"
