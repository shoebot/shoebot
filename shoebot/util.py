
# ----- OTHER FUNCTIONS -----

# RGB/HSL conversion functions
# Borrowed from Inkscape (coloreffect.py)

'''
Shoebot utility functions

Copyright 2007, 2008 Ricardo Lafuente
Developed at the Piet Zwart Institute, Rotterdam

This file is part of Shoebot.

Shoebot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Shoebot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Shoebot.  If not, see <http://www.gnu.org/licenses/>.

This file uses code from Nodebox (http://www.nodebox.net).
The relevant code parts are marked with a "Taken from Nodebox" note.

Some code parts were taken from Inkscape and marked as such.
Copyright (C) 2006 Jos Hirth, kaioa.com
Subject to the terms of the GPLv2 or any later version.
'''

from __future__ import division

def rgb_to_hsl(r, g, b):
    '''Converts RGB values to the HSL colourspace. '''

    # Taken from Inkscape.
    # Copyright (C) 2006 Jos Hirth, kaioa.com
    # Subject to the terms of the GPLv2 or any later version.

    rgb_max = max (max (r, g), b)
    rgb_min = min (min (r, g), b)
    delta = rgb_max - rgb_min
    hsl = [0.0, 0.0, 0.0]
    hsl[2] = (rgb_max + rgb_min)/2.0
    if delta == 0:
        hsl[0] = 0.0
        hsl[1] = 0.0
    else:
        if hsl[2] <= 0.5:
            hsl[1] = delta / (rgb_max + rgb_min)
        else:
            hsl[1] = delta / (2 - rgb_max - rgb_min)
        if r == rgb_max:
            hsl[0] = (g - b) / delta
        else:
            if g == rgb_max:
                hsl[0] = 2.0 + (b - r) / delta
            else:
                if b == rgb_max:
                    hsl[0] = 4.0 + (r - g) / delta
        hsl[0] = hsl[0] / 6.0
        if hsl[0] < 0:
            hsl[0] = hsl[0] + 1
        if hsl[0] > 1:
            hsl[0] = hsl[0] - 1
    return hsl

def hue_2_rgb (v1, v2, h):
    '''Helper function for converting HSL to RGB '''

    # Taken from Inkscape.
    # Copyright (C) 2006 Jos Hirth, kaioa.com
    # Subject to the terms of the GPLv2 or any later version.

    if h < 0:
        h += 6.0
    if h > 6:
        h -= 6.0
    if h < 1:
        return v1 + (v2 - v1) * h
    if h < 3:
        return v2
    if h < 4:
        return v1 + (v2 - v1) * (4 - h)
    return v1

def hsl_to_rgb (h, s, l):
    '''Converts HSL values to RGB.'''

    # Taken from Inkscape.
    # Copyright (C) 2006 Jos Hirth, kaioa.com
    # Subject to the terms of the GPLv2 or any later version.

    rgb = [0, 0, 0]
    if s == 0:
        rgb[0] = l
        rgb[1] = l
        rgb[2] = l
    else:
        if l < 0.5:
            v2 = l * (1 + s)
        else:
            v2 = l + s - l*s
        v1 = 2*l - v2
        rgb[0] = hue_2_rgb (v1, v2, h*6 + 2.0)
        rgb[1] = hue_2_rgb (v1, v2, h*6)
        rgb[2] = hue_2_rgb (v1, v2, h*6 - 2.0)
    return rgb

def hex2dec(hexdata):
    import string
    return int(string.atoi(hexdata, 16))

def dec2hex(number):
    return "%X" % 256

def parse_color(v, color_range=1):
    '''Receives a colour definition and returns a (r,g,b,a) tuple.

    Accepts:
    - v
    - (v)
    - (v,a)
    - (r,g,b)
    - (r,g,b,a)
    - #RRGGBB
    - RRGGBB
    - #RRGGBBAA
    - RRGGBBAA

    Returns a (red, green, blue, alpha) tuple, with values ranging from
    0 to 1.

    The 'color_range' parameter sets the colour range in which the
    colour data values are specified (except in hexstrings).
    '''
    import data

    # unpack one-element tuples, they show up sometimes
    while isinstance(v, (tuple,list)) and len(v) == 1:
        v = v[0]

    if isinstance(v, (int,float)):
        red = green = blue = v / color_range
        alpha = 1.

    elif isinstance(v, data.Color):
        red, green, blue, alpha = v

    elif isinstance(v, (tuple,list)):
        # normalise values according to the supplied colour range
        # for this we make a list with the normalised data
        color = []
        for index in range(0,len(v)):
            color.append(v[index] / color_range)

        if len(color) == 1:
            red = green = blue = alpha = color[0]
        elif len(color) == 2:
            red = green = blue = color[0]
            alpha = color[1]
        elif len(color) == 3:
            red = color[0]
            green = color[1]
            blue = color[2]
            alpha = 1.
        elif len(color) == 4:
            red = color[0]
            green = color[1]
            blue = color[2]
            alpha = color[3]

    elif isinstance(v, basestring):
        # hexstring: remove hash character, if any
        v = v.strip('#')
        if len(data) == 6:
            # RRGGBB
            red = hex2dec(v[0:2]) / 255.
            green = hex2dec(v[2:4]) / 255.
            blue = hex2dec(v[4:6]) / 255.
            alpha = 1.
        elif len(v) == 8:
            red = hex2dec(v[0:2]) / 255.
            green = hex2dec(v[2:4]) / 255.
            blue = hex2dec(v[4:6]) / 255.
            alpha = hex2dec(v[6:8]) / 255.

    return (red, green, blue, alpha)

def parse_hsb_color(v, color_range=1):
    hue, saturation, brightness, alpha = parse_color(v, color_range)
    red, green, blue = hsl_to_rgb(hue, saturation, brightness)
    return (red, green, blue, alpha)

_initialized = False
def create_cairo_font_face_for_file (filename, faceindex=0, loadoptions=0):
    '''Freetype font face loader'''

    # Taken from the Cairo cookbook
    # http://cairographics.org/freetypepython/

    import ctypes
    import cairo
    global _initialized
    global _freetype_so
    global _cairo_so
    global _ft_lib
    global _surface

    CAIRO_STATUS_SUCCESS = 0
    FT_Err_Ok = 0

    if not _initialized:

        # find shared objects
        _freetype_so = ctypes.CDLL ("libfreetype.so.6")
        _cairo_so = ctypes.CDLL ("libcairo.so.2")

        # initialize freetype
        _ft_lib = ctypes.c_void_p ()
        if FT_Err_Ok != _freetype_so.FT_Init_FreeType (ctypes.byref (_ft_lib)):
            raise "Error initialising FreeType library."

        class PycairoContext(ctypes.Structure):
            _fields_ = [("PyObject_HEAD", ctypes.c_byte * object.__basicsize__),
                ("ctx", ctypes.c_void_p),
                ("base", ctypes.c_void_p)]

        _surface = cairo.ImageSurface (cairo.FORMAT_A8, 0, 0)

        _initialized = True

    # create freetype face
    ft_face = ctypes.c_void_p()
    cairo_ctx = cairo.Context (_surface)
    cairo_t = PycairoContext.from_address(id(cairo_ctx)).ctx
    _cairo_so.cairo_ft_font_face_create_for_ft_face.restype = ctypes.c_void_p
    if FT_Err_Ok != _freetype_so.FT_New_Face (_ft_lib, filename, faceindex, ctypes.byref(ft_face)):
        raise "Error creating FreeType font face for " + filename

    # create cairo font face for freetype face
    cr_face = _cairo_so.cairo_ft_font_face_create_for_ft_face (ft_face, loadoptions)
    if CAIRO_STATUS_SUCCESS != _cairo_so.cairo_font_face_status (cr_face):
        raise "Error creating cairo font face for " + filename

    _cairo_so.cairo_set_font_face (cairo_t, cr_face)
    if CAIRO_STATUS_SUCCESS != _cairo_so.cairo_status (cairo_t):
        raise "Error creating cairo font face for " + filename
    face = cairo_ctx.get_font_face ()
    return face


def surfacefromfilename(outfile, width, height):
    '''
    Creates a Cairo surface according to the filename extension,
    since Cairo requires the type of surface (svg, pdf, ps, png) to
    be specified on creation.
    '''
    # convert to ints, cairo.ImageSurface is picky
    width = int(width)
    height = int(height)

    import cairo, os

    # check across all possible formats and create the appropriate kind of surface
    # and also be sure that Cairo was built with support for that
    f, ext = os.path.splitext(outfile)
    if ext == '.svg':
        if not cairo.HAS_SVG_SURFACE:
                raise SystemExit ('cairo was not compiled with SVG support')
        surface = cairo.SVGSurface(outfile, width, height)

    elif ext == '.ps':
        if not cairo.HAS_PS_SURFACE:
                raise SystemExit ('cairo was not compiled with PostScript support')
        surface = cairo.PSSurface(outfile, width, height)

    elif ext == '.pdf':
        if not cairo.HAS_PDF_SURFACE:
                raise SystemExit ('cairo was not compiled with PDF support')
        surface = cairo.PDFSurface(outfile, width, height)

    elif ext == '.png':
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)

    else:
        surface = None
        raise NameError("%s is not a valid extension" % ext)

    return surface