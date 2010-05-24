#!/usr/bin/env python

class ShoebotError(Exception): pass
class ShoebotScriptError(Exception): pass

from sbot import run

RGB = "rgb"
HSB = "hsb"

# TODO - Put these in shoebot.data
MOVETO = "moveto"
RMOVETO = "rmoveto"
LINETO = "lineto"
RLINETO = "rlineto"
CURVETO = "curveto"
RCURVETO = "rcurveto"
ARC = 'arc'
ELLIPSE = 'ellipse'
CLOSE = "close"
