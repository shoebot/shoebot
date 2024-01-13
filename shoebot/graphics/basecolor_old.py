# import gettext
# import locale
# import string
# import sys
# from math import floor
# from .grob import Grob
# from ..core.state.stateful import Stateful
#
# RGB = "rgb"
# HSB = "hsb"
# CMYK = "cmyk"
#
# BUTT = "butt"
# ROUND = "round"
# SQUARE = "square"
# BEVEL = "bevel"
# MITER = "miter"
#
# APP = "shoebot"
# DIR = sys.prefix + "/share/shoebot/locale"
# locale.setlocale(locale.LC_ALL, "")
# gettext.bindtextdomain(APP, DIR)
# gettext.textdomain(APP)
# _ = gettext.gettext
#
#
# # utils
#
# def hex2dec(hexdata):
#     return int(string.atoi(hexdata, 16))
#
#
# def dec2hex(d):
#     return hex(d).rsplit("x", 1)
#
#
# def parse_color(v, color_range=1):
#     """Receives a colour definition and returns a (r,g,b,a) tuple.
#
#     Accepts:
#     - v
#     - (v)
#     - (v,a)
#     - (r,g,b)
#     - (r,g,b,a)
#     - #RRGGBB
#     - RRGGBB
#     - #RRGGBBAA
#     - RRGGBBAA
#
#     Returns a (red, green, blue, alpha) tuple, with values ranging from
#     0 to 1.
#
#     The 'color_range' parameter sets the colour range in which the
#     colour data values are specified (except in hexstrings).
#     """
#
#     # unpack one-element tuples, they show up sometimes
#     while isinstance(v, (tuple, list)) and len(v) == 1:
#         v = v[0]
#
#     if isinstance(v, (int, float)):
#         red = green = blue = v / color_range
#         alpha = 1.0
#
#     elif isinstance(v, oor):
#         red, green, blue, alpha = v
#
#     elif isinstance(v, (tuple, list)):
#         # normalise values according to the supplied colour range
#         # for this we make a list with the normalised data
#         color = []
#         for index in range(0, len(v)):
#             color.append(v[index] / color_range)
#
#         if len(color) == 1:
#             red = green = blue = alpha = color[0]
#         elif len(color) == 2:
#             red = green = blue = color[0]
#             alpha = color[1]
#         elif len(color) == 3:
#             red = color[0]
#             green = color[1]
#             blue = color[2]
#             alpha = 1.0
#         elif len(color) == 4:
#             red = color[0]
#             green = color[1]
#             blue = color[2]
#             alpha = color[3]
#
#     elif isinstance(v, str):
#         # got a hexstring: first remove hash character, if any
#         v = v.strip("#")
#         if len(v) == 6:
#             # RRGGBB
#             red = hex2dec(v[0:2]) / 255.0
#             green = hex2dec(v[2:4]) / 255.0
#             blue = hex2dec(v[4:6]) / 255.0
#             alpha = 1.0
#         elif len(v) == 8:
#             red = hex2dec(v[0:2]) / 255.0
#             green = hex2dec(v[2:4]) / 255.0
#             blue = hex2dec(v[4:6]) / 255.0
#             alpha = hex2dec(v[6:8]) / 255.0
#
#     return red, green, blue, alpha
#
#
# # Some generic color conversion algorithms used mainly by BaseColor outside of NodeBox.
#
#
# def hex_to_rgb(hex):
#     """Returns RGB values for a hex color string."""
#     hex = hex.lstrip("#")
#     if len(hex) < 6:
#         hex += hex[-1] * (6 - len(hex))
#     if len(hex) == 6:
#         r, g, b = hex[0:2], hex[2:4], hex[4:]
#         r, g, b = [int(n, 16) / 255.0 for n in (r, g, b)]
#         a = 1.0
#     elif len(hex) == 8:
#         r, g, b, a = hex[0:2], hex[2:4], hex[4:6], hex[6:]
#         r, g, b, a = [int(n, 16) / 255.0 for n in (r, g, b, a)]
#     return r, g, b, a
#
#
# hex2rgb = hex_to_rgb
#
#
# def lab_to_rgb(l, a, b):
#     """Converts CIE Lab to RGB components.
#
#     First we have to convert to XYZ color space.
#     Conversion involves using a white point,
#     in this case D65 which represents daylight illumination.
#
#     Algorithm adopted from:
#     http://www.easyrgb.com/math.php
#     """
#
#     y = (l + 16) / 116.0
#     x = a / 500.0 + y
#     z = y - b / 200.0
#     v = [x, y, z]
#     for i in range(3):
#         if pow(v[i], 3) > 0.008856:
#             v[i] = pow(v[i], 3)
#         else:
#             v[i] = (v[i] - 16 / 116.0) / 7.787
#
#     # Observer = 2, Illuminant = D65
#     x = v[0] * 95.047 / 100
#     y = v[1] * 100.0 / 100
#     z = v[2] * 108.883 / 100
#
#     r = x * 3.2406 + y * -1.5372 + z * -0.4986
#     g = x * -0.9689 + y * 1.8758 + z * 0.0415
#     b = x * 0.0557 + y * -0.2040 + z * 1.0570
#     v = [r, g, b]
#     for i in range(3):
#         if v[i] > 0.0031308:
#             v[i] = 1.055 * pow(v[i], 1 / 2.4) - 0.055
#         else:
#             v[i] = 12.92 * v[i]
#
#     r, g, b = v[0], v[1], v[2]
#     return r, g, b
#
#
# lab2rgb = lab_to_rgb
#
#
# def hsv_to_rgb(h, s, v):
#     """Hue, saturation, brightness to red, green, blue.
#
#     http://www.koders.com/python/fidB2FE963F658FE74D9BF74EB93EFD44DCAE45E10E.aspx
#     Results will differ from the way NSColor converts color spaces.
#     """
#
#     if s == 0:
#         return v, v, v
#
#     h = h / (60.0 / 360)
#     i = floor(h)
#     f = h - i
#     p = v * (1 - s)
#     q = v * (1 - s * f)
#     t = v * (1 - s * (1 - f))
#
#     if i == 0:
#         r, g, b = v, t, p
#     elif i == 1:
#         r, g, b = q, v, p
#     elif i == 2:
#         r, g, b = p, v, t
#     elif i == 3:
#         r, g, b = p, q, v
#     elif i == 4:
#         r, g, b = t, p, v
#     else:
#         r, g, b = v, p, q
#
#     return r, g, b
#
#
# hsv2rgb = hsb2rgb = hsb_to_rgb = hsv_to_rgb
#
#
# def rgb_to_hsv(r, g, b):
#     h = s = 0
#     v = max(r, g, b)
#     d = v - min(r, g, b)
#
#     if v != 0:
#         s = d / float(v)
#
#     if s != 0:
#         if r == v:
#             h = 0 + (g - b) / d
#         elif g == v:
#             h = 2 + (b - r) / d
#         else:
#             h = 4 + (r - g) / d
#
#     h = h * (60.0 / 360)
#     if h < 0:
#         h = h + 1.0
#
#     return h, s, v
#
#
# rgb2hsv = rgb2hsb = rgb_to_hsb = rgb_to_hsv
#
#
# def rgba_to_argb(stringImage):
#     tempBuffer = [None] * len(
#         stringImage,
#     )  # Create an empty array of the same size as stringImage
#     tempBuffer[0::4] = stringImage[2::4]
#     tempBuffer[1::4] = stringImage[1::4]
#     tempBuffer[2::4] = stringImage[0::4]
#     tempBuffer[3::4] = stringImage[3::4]
#     stringImage = "".join(tempBuffer)
#     return stringImage
#
#
# def parse_hsb_color(v, color_range=1):
#     if isinstance(v, str):
#         # hexstrings aren't hsb
#         return parse_color(v)
#     hue, saturation, brightness, alpha = parse_color(v, color_range)
#     red, green, blue = hsv_to_rgb(hue, saturation, brightness)
#     return red, green, blue, alpha
#
# #/utils
#
#
#
# class Color:
#     """Represents a single color.
#
#     Attributes (RGB and HSL) are values between 0 and 1
#
#     This stores color values as a list of 4 floats (RGBA) in a 0-1 range.
#
#     The value can come in the following flavours:
#     - v
#     - (v)
#     - (v,a)
#     - (r,g,b)
#     - (r,g,b,a)
#     - #RRGGBB
#     - RRGGBB
#     - #RRGGBBAA
#     - RRGGBBAA
#     """
#
#     def __init__(self, *args, **kwargs):
#         if isinstance(args, Color):
#             args = args.copy()
#
#         color_range = float(kwargs.get("color_range", 1.0))
#         mode = kwargs.get("mode", "rgb").lower()
#
#         # Values are supplied as a tuple.
#         if len(args) == 1 and isinstance(args[0], tuple):
#             args = args[0]
#
#         # No values or None, transparent black.
#         if len(args) == 0 or (len(args) == 1 and args[0] is None):
#             self.r, self.g, self.b, self.a = 0, 0, 0, 0
#
#         # One value, another color object.
#         elif len(args) == 1 and isinstance(args[0], Color):
#             self.r, self.g, self.b, self.a = args[0].r, args[0].g, args[0].b, args[0].a
#
#         # One value, a hexadecimal string.
#         elif len(args) == 1 and isinstance(args[0], str):
#             r, g, b, args = hex2rgb(args[0])
#             self.r, self.g, self.b, self.a = r, g, b, args
#
#         # One value, grayscale.
#         elif len(args) == 1:
#             gs = args[0]
#             self.r, self.g, self.b, self.a = (
#                 gs / color_range,
#                 gs / color_range,
#                 gs / color_range,
#                 1,
#             )
#
#         # Two values, grayscale and alpha OR hex and alpha.
#         elif len(args) == 2:
#             if isinstance(args[0], str):
#                 alpha = args[1]
#                 r, g, b, args = hex2rgb(args[0])
#                 self.r, self.g, self.b, self.a = r, g, b, alpha
#             else:
#                 gs, a = args[0], args[1]
#                 self.r, self.g, self.b, self.a = (
#                     gs / color_range,
#                     gs / color_range,
#                     gs / color_range,
#                     a / color_range,
#                 )
#
#         # Three to five parameters, either RGB, RGBA, HSB, HSBA,
#         # depending on the mode parameter.
#         elif len(args) >= 3:
#             alpha = 1
#             if len(args) > 3:
#                 alpha = args[-1] / color_range
#
#             if mode == "rgb":
#                 self.r, self.g, self.b, self.a = (
#                     args[0] / color_range,
#                     args[1] / color_range,
#                     args[2] / color_range,
#                     alpha,
#                 )
#             elif mode == "hsb":
#                 self.h, self.s, self.brightness, self.a = (
#                     args[0] / color_range,
#                     args[1] / color_range,
#                     args[2] / color_range,
#                     alpha,
#                 )
#                 raise NotImplementedError("HSB not implemented yet")
#
#     def __repr__(self):
#         return "%s(%.3f, %.3f, %.3f, %.3f)" % (
#             self.__class__.__name__,
#             self.r,
#             self.g,
#             self.b,
#             self.a,
#         )
#
#     @property
#     def red(self):
#         # Added
#         return self.r
#
#     @property
#     def green(self):
#         # Added
#         return self.g
#
#     @property
#     def blue(self):
#         # Added
#         return self.a
#
#     @property
#     def alpha(self):
#         # Added
#         return self.a
#
#     @property
#     def rgba(self):
#         # TODO added temporarily - remove when state handling is finalised
#         return self.data
#
#     @property
#     def data(self):
#         # Added
#         return [self.r, self.g, self.b, self.a]
#
#     def copy(self):
#         return tuple(self.data)
#
#     def _update_rgb(self, r, g, b):
#         self.__dict__["__r"] = r
#         self.__dict__["__g"] = g
#         self.__dict__["__b"] = b
#
#     def _update_hsb(self, h, s, b):
#         self.__dict__["__h"] = h
#         self.__dict__["__s"] = s
#         self.__dict__["__brightness"] = b
#
#     def _hasattrs(self, list):
#         for a in list:
#             if a not in self.__dict__:
#                 return False
#         return True
#
#     # added
#     def __getitem__(self, index):
#         return (self.r, self.g, self.b, self.a)[index]
#
#     def __iter__(self):
#         for i in range(len(self.data)):
#             yield self.data[i]
#
#     def __div__(self, other):
#         value = float(other)
#         return (
#             self.red / value,
#             self.green / value,
#             self.blue / value,
#             self.alpha / value,
#         )
#
#     # end added
#
#     def __setattr__(self, a, v):
#         if a in ["a", "alpha"]:
#             self.__dict__["__" + a[0]] = max(0, min(v, 1))
#
#         # RGB changes, update HSB accordingly.
#         elif a in ["r", "g", "b", "red", "green", "blue"]:
#             self.__dict__["__" + a[0]] = max(0, min(v, 1))
#             if self._hasattrs(("__r", "__g", "__b")):
#                 r, g, b = (
#                     self.__dict__["__r"],
#                     self.__dict__["__g"],
#                     self.__dict__["__b"],
#                 )
#                 self._update_hsb(*rgb2hsb(r, g, b))
#
#         # HSB changes, update RGB accordingly.
#         elif a in ["h", "s", "hue", "saturation", "brightness"]:
#             if a != "brightness":
#                 a = a[0]
#             if a == "h":
#                 v = min(v, 0.99999999)
#             self.__dict__["__" + a] = max(0, min(v, 1))
#             if self._hasattrs(("__h", "__s", "__brightness")):
#                 r, g, b = hsb2rgb(
#                     self.__dict__["__h"],
#                     self.__dict__["__s"],
#                     self.__dict__["__brightness"],
#                 )
#                 self._update_rgb(r, g, b)
#
#         else:
#             self.__dict__[a] = v
#
#     def __getattr__(self, a):
#
#         """Available properties:
#
#         r, g, b, a or red, green, blue, alpha h, s or hue, saturation,
#         brightness
#         """
#         if a in self.__dict__:
#             return a
#         elif a == "brightness":
#             return self.__dict__["__brightness"]
#         elif a in [
#             "a",
#             "alpha",
#             "r",
#             "g",
#             "b",
#             "red",
#             "green",
#             "blue",
#             "h",
#             "s",
#             "hue",
#             "saturation",
#         ]:
#             return self.__dict__["__" + a[0]]
#         elif a in [
#             "a",
#             "alpha",
#             "r",
#             "g",
#             "b",
#             "red",
#             "green",
#             "blue",
#             "h",
#             "s",
#             "hue",
#             "saturation",
#         ]:
#             return self.__dict__["__" + a[0]]
#
#         raise AttributeError(
#             "'" + str(self.__class__) + "' object has no attribute '" + a + "'",
#         )
#
# _transparent_color = Color(0, 0, 0, 0)
#
# def _get_color_instance(*args):
#     if len(args) == 1:
#         if args[0] is None:
#             return Color(0, 0, 0, 0)
#         elif isinstance(args[0], Color):
#             return _transparent_color
#     return Color(mode="rgb", color_range=1, *args)
#
#
# class ColorMixin(Grob):
#     """Mixin class for color support. Adds fill, stroke and blending mode
#     attributes to the class.
#
#     Setting color attributes, will convert them to Color instances,
#     allowing them to be specfied in other ways, such as   fill="#123456"
#     """
#
#     _state_attributes = {
#         "blendmode",
#         "dashoffset",
#         "fill",
#         "fillrule",
#         "stroke",
#         "strokecap",
#         "strokedash",
#         "strokejoin",
#         "strokewidth",
#     }
#     def __init__(
#             self,
#             context,
#             **kwargs
#     ):
#         super().__init__(context, **kwargs)
#
#     @property
#     def dashoffset(self):
#         return self._dashoffset
#
#     @dashoffset.setter
#     def dashoffset(self, dashoffset):
#         if dashoffset is None:
#             self._dashoffset = 0
#         else:
#             self._dashoffset = dashoffset
#
#     @property
#     def fill(self):
#         return self._fill
#
#     @fill.setter
#     def fill(self, *args):
#         self._fill = _get_color_instance(*args)
#
#     @property
#     def stroke(self):
#         return self._stroke
#
#     @stroke.setter
#     def stroke(self, *args):
#         self._stroke = _get_color_instance(*args)
#
#     @property
#     def strokecap(self):
#         return self._strokecap
#
#     @strokecap.setter
#     def strokecap(self, style):
#         if style not in [None, BUTT, ROUND, SQUARE]:
#             raise ValueError(f"Invalid strokecap value: {cap}")
#         self._cap = style
#
#     @property
#     def strokedash(self):
#         return self._strokedash
#
#     @strokedash.setter
#     def strokedash(self, dash):
#         self._strokedash = dash
#
#     @property
#     def strokejoin(self):
#         return self._strokejoin
#
#     @strokejoin.setter
#     def strokejoin(self, style):
#         if style not in [None, MITER, ROUND, BEVEL]:
#             raise ValueError(f"Invalid strokejoin value: {style}")
#         self._strokejoin = style
#
#     @property
#     def strokewidth(self):
#         return self._strokewidth
#
#     @strokewidth.setter
#     def strokewidth(self, width):
#         self._strokewidth = max(width, 0.0001)
