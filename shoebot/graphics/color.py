from enum import Enum

from shoebot.core.state.color_data import RGBData, RGBAData, VData, get_color_type
from shoebot.core.state.state_value import StateValueContainer, get_state_value


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

        # Passing internal state is used internally for cloning, but isn't supported as a public API
        self._color_range = kwargs.pop("color_range", 1.0)
        color_data = kwargs.pop("state_value", None)
        if color_data:
            assert len(args) == 0
            super().__init__("_color_data", state_value = color_data)
            return

        # TODO - the state creation needs to be at least partially handled elsewhere
        # We would look up the correct state class by using nodeboxes color.mode,
        # which corresponds to the ColorData.format
        mode = kwargs.pop("mode", None)
        if isinstance(mode, Enum):
            mode = mode.value

        if mode:
            color_data = get_color_type(mode)(*args)
        else:
            if len(args) == 1:
                # TODO - this is wrong, we need a grayscale color data class
                color_data = RGBData(args[0], args[0], args[0])
            elif len(args) == 3:
                color_data = RGBData(*args)  # TODO - probably
            elif len(args) == 4:
                color_data = RGBAData(*args)
            else:
                raise NotImplemented("TODO")
        super().__init__("_color_data", value = color_data)

    def __iter__(self):
        # TODO - check against nodebox API
        return iter(self._color_data.as_rgba().channels)
    def __repr__(self):
        return f"<Color: {get_state_value(self)}>"
