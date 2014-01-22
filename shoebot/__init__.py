from sbot import run, bot, create_canvas

class ShoebotError(Exception): pass
class ShoebotScriptError(Exception): pass

RGB = "rgb"
HSB = "hsb"
CMYK = 'cmyk'

CENTER = "center"
CORNER = "corner"
CORNERS = "corners"

# TODO - Check if this needs importing here:
from data import MOVETO, RMOVETO, LINETO, RLINETO, CURVETO, RCURVETO, ARC, ELLIPSE, CLOSE, LEFT, RIGHT


def _save():
    # Dummy function used by color lib; TODO investigate what is needed
    pass

def _restore():
    # Dummy function used by color lib; TODO investigate what is needed
    pass
