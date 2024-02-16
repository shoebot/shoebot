import functools
from dataclasses import dataclass
from textwrap import dedent
from typing import Tuple, Dict

from shoebot.core.color.conversion import COLOR_CONVERSIONS

# Lookup color types by their name.
COLOR_TYPES: Dict[str, "ColorData"] = {}

@functools.cache
def get_color_type(format: str) -> "ColorData":  # noqa
    """
    Get the color type for a color format.

    :param name: Name of the color type
    """
    try:
        return COLOR_TYPES[format]
    except KeyError:
        raise ValueError(f"No ColorData for format: {format}")

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
            def create_as_format_method(f, destination_format):
                """
                Create a method to convert the color to another format

                For this to work there must be an existing class to
                represent the destination format, and a color conversion function.

                This will result in a method like .as_rgb

                :param f: conversion function e.g. hsv_to_rgb
                :param destination_format: destination format, e.g. "rgb"
                """
                print(name, f, destination_format)
                assert f.__name__.endswith(destination_format)

                def as_format_method(self):
                    dest_color_type = get_color_type(destination_format)
                    return dest_color_type(*f(self.channels))

                as_format_method.__name__ = f'as_{destination_format}'
                as_format_method.__doc__ = as_format_docstring(name, src, dest)
                return as_format_method

            def add_as_format_method(f, destination_format):
                # Add a single method that converts returns the Color in another color
                # format using `create_as_format_method`
                as_format_method = create_as_format_method(f, destination_format)
                dct[as_format_method.__name__] = as_format_method

            for (src, dest), func in COLOR_CONVERSIONS.items():
                # Create as_FORMAT methods to convert to each format,
                # e.g. as_hsv, as_rgb, as_cmyk, etc.
                #
                # If the source format is the same as the current format
                # then it is ignored here, as a null conversion method
                # will be created later.
                if src == format:
                    add_as_format_method(func, dest)

            dct[f"as_{format}"] = lambda self: self

            # For the component channels, create named properties with getters and setters,
            # So for rgb color, these would be named r, g, b.
            for i, channel in enumerate(format):
                def create_channel_accessor(idx):
                    def channel_getter(self):
                        return self.channels[idx]

                    def channel_setter(self, value):
                        if not (0.0 <= value <= 1.0):
                            raise ValueError(f"{channel.upper()} component must be in the range [0, 1]")
                        self.channels = self.channels[:idx] + (value,) + self.channels[idx + 1:]

                    return channel_getter, channel_setter

                get_channel, set_channel = create_channel_accessor(i)
                channel_property = property(get_channel, set_channel)
                channel_property.__doc__ = f"Get or set the {channel.upper()} component of the color."
                dct[channel] = channel_property

            if 'channel_names' not in dct:
                dct['channel_names'] = tuple(format.upper())

        new_class = type.__new__(cls, name, bases, dct)
        if bases:
            COLOR_TYPES[format] = new_class

        return new_class


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
    scale: float = 1.0

    def __init__(self, *channels):
        """
        Create a new color data object.

        :param channels: A tuple of floats representing the color in its native format.
        """
        print(type(self), channels, len(channels))
        if not len(channels):
            channels = (0.0,) * len(self.format)
        else:
            assert len(channels) == len(self.format), f"{type(self).__name__} Expected {len(self.format)} channels, got {len(channels)}"

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


@dataclass(init=False)
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

@dataclass(init=False)
class HSVData(ColorData):
    """
    Represents a color in HSV format.

    HSV is a cylindrical-coordinate representation of points in an RGB color model.

    HSV stands for hue, saturation, and value.

    The HSV model was created in 1978 by Alvy Ray Smith.

    The HSV color space has the same geometry as the RGB color space, but with the hexcone
    extended outwards from the center perpendicular to the hexcone base.

    The conversion calculations for HSV are the same as for HSL, except that the lightness component is replaced by value.
    """
    format = 'hsv'
    channel_names = 'Hue Saturation Value'.split()

    @property
    def rgb(self):
        return self.as_rgb().channels

    @property
    def rgba(self):
        return self.as_rgba().channels


@dataclass(init=False)
class HSBData(ColorData):
    """
    Represents a color in HSB format.

    HSB is a cylindrical-coordinate representation of points in an RGB color model.

    HSB stands for hue, saturation, and brightness.

    The HSB model is essentially the same as the HSV model, both representing colors in a way that's more aligned with human perception than the RGB model.

    The HSB color space has the same geometry as the RGB color space, but with the hexcone extended outwards from the center perpendicular to the hexcone base.

    The conversion calculations for HSB are the same as for HSV, as brightness in HSB corresponds to the value component in HSV.
    """
    format = 'hsb'
    channel_names = 'Hue Saturation Brightness'.split()

    @property
    def rgb(self):
        return self.as_rgb().channels

    @property
    def rgba(self):
        return self.as_rgba().channels

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
