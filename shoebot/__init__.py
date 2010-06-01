#!/usr/bin/env python

class ShoebotError(Exception): pass
class ShoebotScriptError(Exception): pass

from sbot import run

RGB = "rgb"
HSB = "hsb"
CMYK = 'cmyk'

CENTER = "center"
CORNER = "corner"
CORNERS = "corners"

# TODO - Maybe put these in shoebot.data
MOVETO = "moveto"
RMOVETO = "rmoveto"
LINETO = "lineto"
RLINETO = "rlineto"
CURVETO = "curveto"
RCURVETO = "rcurveto"
ARC = 'arc'
ELLIPSE = 'ellipse'
CLOSE = "close"

def _save():
    ### Not entirely sure what this is for - stu
    pass

def _restore():
    ### Not entirely sure what this is for - stu
    pass
