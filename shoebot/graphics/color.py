from shoebot.core.state.color_data import RGBData
from shoebot.core.state.stateful import Stateful, StateValueContainer


class Color(StateValueContainer):
    """Represents a single color.

    Attributes (RGB and HSL) are values between 0 and 1

    This stores color values as a list of 4 floats (RGBA) in a 0-1 range.

    The value can come in the following flavours:
    - v
    - (v)
    - (v,a)
    - (r,g,b)
    - (r,g,b,a)
    - #RRGGBB
    - RRGGBB
    - #RRGGBBAA
    - RRGGBBAA
    """

    def __init__(self, *args, **kwargs):
        # TODO, it's really the nodebox context that
        # is in charge of defaults for color
        self._color_data = RGBData()  # TODO - probably
        super().__init__("_color_data")
