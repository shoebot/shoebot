from dataclasses import dataclass
from textwrap import dedent
from typing import Tuple

from shoebot.core.color.conversion import COLOR_CONVERSIONS


def as_format_docstring(cls_name, src, dest):
    """
    Generate a docstring for a color conversion method.

    :param cls_name: Name of the Color class
    :param src: Source format
    :param dest: Destination format
    """
    if src == dest:
        return dedent(f"""\
                Retrieve the color's current {src.upper()} values.

                :return: A tuple representing the color in its native {src.upper()} format, each component in the range [0, 1].
            """)
    else:
        return dedent(f"""\
                Convert this {cls_name} object from {src.upper()} format to {dest.upper()} format.

                :return: A tuple representing the color in {dest.upper()} format, each component in the range [0, 1].
            """)


class ColorMeta(type):
    """
    Dynamically adds color conversion methods to color classes.

    Color conversion functions such as `rgb_to_hsv` registered in the `conversion`
    module are automatically added as methods to color classes.

    For example, the `RGB` class will have the methods such as:
    - `as_rgb`
    - `as_hsv`
    ...etc
    """
    def __new__(cls, name, bases, dct):
        if bases:
            format = dct.get('format')
            # For each conversion function in the conversion module that can
            # convert from the current format, create a method that converts
            # the color to the destination format.
            null_conversion_method = lambda self: self.channels
            null_conversion_method.__name__ = f'as_{format}'
            null_conversion_method.__doc__ = as_format_docstring(cls.__name__, format, format)
            dct[f'as_{format}'] = null_conversion_method

            for (src, dest), func in COLOR_CONVERSIONS.items():
                if src == format:
                    method_name = f'as_{dest}'

                    def create_conversion_method(f):
                        def conversion_method(self):
                            return f(self.channels)

                        return conversion_method

                    conversion_method = create_conversion_method(func)
                    conversion_method.__name__ = method_name
                    conversion_method.__doc__ = as_format_docstring(name, src, dest)
                    dct[method_name] = conversion_method

            # For the component channels, create named properties with getters and setters
            for i, channel in enumerate(dct.get('format', '')):
                def create_channel_accessor(idx):
                    def get_channel(self):
                        return self.channels[idx]

                    def set_channel(self, value):
                        if not (0.0 <= value <= 1.0):
                            raise ValueError(f"{channel.upper()} component must be in the range [0, 1]")
                        self.channels = self.channels[:idx] + (value,) + self.channels[idx + 1:]

                    return get_channel, set_channel

                get_channel, set_channel = create_channel_accessor(i)
                channel_property = property(get_channel, set_channel)
                channel_property.__doc__ = f"Get or set the {channel.upper()} component of the color."
                dct[channel] = channel_property

            if 'channel_names' not in dct:
                dct['channel_names'] = tuple(format.upper())
        return type.__new__(cls, name, bases, dct)


@dataclass(init=False)
class ColorData(metaclass=ColorMeta):
    """
    Base class for color data classes.

    Color data classes specify format, as a string, e.g. "rgb",
    channels is a Tuple of the same length, representing the color
    in it's native format.

    >>> class RGBData(ColorData):
    ...    format = "rgb"
    ...
    >>> half_red = RGBData(0.5, 0, 0)
    """
    format: str
    channels: Tuple

    def __init__(self, *channels):
        """
        Create a new color data object.

        :param channels: A tuple of floats representing the color in its native format.
        """
        if not channels:
            channels = (0.0,) * len(self.format)
        else:
            assert len(channels) == len(self.format), f"Expected {len(self.format)} channels, got {len(channels)}"
        self.channels = channels

    def as_long_dict(self):
        """
        Return a dictionary with the channel names as keys and the channel values as values.

        :return: A dictionary with the keys being the channel names and the values being the channel values.
        """
        return dict(zip(self.channel_names, self.channels))

    def as_dict(self):
        """
        Return a dictionary with the channel names as keys and the channel values as values.

        :return: A dictionary with the keys being the channel names and the values being the channel values.
        """
        return dict(zip(self.format, self.channels))


@dataclass(init=False)
class RGBData(ColorData):
    """
    Represents a color in RGB format.

    RGB is a color model that defines a color according to its red, green, and blue components.

    The red, green, and blue values here are floats between 0.0 and 1.0.
    """
    format = 'rgb'
    channel_names = 'Red Green Blue'.split()

    @property
    def rgb(self):
        return self.as_rgb()


@dataclass(init=False)
class RGBAData(ColorData):
    """
    Represents a color in RGBA format.

    RGBA is a color model that adds alpha channel to RGB.

    The red, green, and blue values here are floats between 0.0 and 1.0.
    The alpha channel represents the transparency of the color.

    The alpha value is a number between 0.0 (fully transparent) and 1.0 (fully opaque).
    """
    format = 'rgba'
    channel_names = 'Red Green Blue Alpha'.split()

    @property
    def rgb(self):
        return self.as_rgb()


@dataclass(init=False)
class HSVData(ColorData):
    """
    Represents a color in HSV format.

    HSV is a cylindrical-coordinate representation of points in an RGB color model.

    HSV stands for hue, saturation, and value.

    The HSV model was created in 1978 by Alvy Ray Smith.

    The HSV color space has the same geometry as the RGB color space, but with the hexcone
    extended outwards from the center perpendicular to the hexcone base.
    """
    format = 'hsv'
    channel_names = 'Hue Saturation Value'.split()


class HSLData(ColorData):
    """
    Represents a color in HSL format.

    HSL is a cylindrical-coordinate representation of points in an RGB color model.

    HSL stands for hue, saturation, and lightness.

    The HSL color space has the same geometry as the HSV color space, but with the hexcone
    extended inwards from the center perpendicular to the hexcone base.

    The HSL color space is also known as HSI (hue, saturation, intensity), or HLS (hue, lightness, saturation).
    """
    format = 'hsl'
    channel_names = 'Hue Saturation Lightness'.split()

# TODO - is "V" the right name ?
@dataclass(init=False)
class VData(ColorData):
    """
    Represents a color in V format.
    """
    format = 'v'

@dataclass(init=False)
class VAData(ColorData):
    """
    Represents a color in VA format.
    """
    format = 'va'