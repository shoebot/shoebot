from sbot import run

class ShoebotError(Exception): pass
class ShoebotScriptError(Exception): pass

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
    # Dummy function used by color lib; TODO investigate what is needed
    pass

def _restore():
    # Dummy function used by color lib; TODO investigate what is needed
    pass
