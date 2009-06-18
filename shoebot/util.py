#!/usr/bin/env python

# This file is part of Shoebot.
# Copyright (C) 2009 the Shoebot authors
# See the COPYING file for the full license text.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
#   The name of the author may not be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED
#   WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#   MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
#   EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#   OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''Assorted utility functions, mainly for color and font handling'''

from __future__ import division

import os
import string
# import data
import ctypes
import cairo
'''
def rgb_to_hsl(r, g, b):
    """Converts RGB values to the HSL colourspace. """

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
    """Helper function for converting HSL to RGB """

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
    """Converts HSL values to RGB."""

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
'''

'''
def rgb_to_hsv(r, g, b):
    
    h = s = 0
    v = max(r, g, b)
    d = v - min(r, g, b)

    if v != 0:
        s = d / float(v)

    if s != 0:
        if   r == v : h = 0 + (g-b) / d
        elif g == v : h = 2 + (b-r) / d
        else        : h = 4 + (r-g) / d

    h = h * (60.0/360)
    if h < 0: 
        h = h + 1.0
    hsv=[h,s,v]    
    return hsv
'''

"""def hsv_to_rgb(h, s, v):
    
    ''' Hue, saturation, brightness to red, green, blue.
    http://www.koders.com/python/fidB2FE963F658FE74D9BF74EB93EFD44DCAE45E10E.aspx
    Results will differ from the way NSColor converts color spaces.
    '''
    
    if s == 0: return v, v, v
        
    h = h / (60.0/360)
    i =  floor(h)
    f = h - i
    p = v * (1-s)
    q = v * (1-s * f)
    t = v * (1-s * (1-f))
    
    if   i == 0 : r = v; g = t; b = p
    elif i == 1 : r = q; g = v; b = p
    elif i == 2 : r = p; g = v; b = t
    elif i == 3 : r = p; g = q; b = v
    elif i == 4 : r = t; g = p; b = v
    else        : r = v; g = p; b = q
    
    return list(r, g, b)
"""




_initialized = False
def create_cairo_font_face_for_file (filename, faceindex=0, loadoptions=0):
    '''Freetype font face loader'''

    # Taken from the Cairo cookbook
    # http://cairographics.org/freetypepython/

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

        _initialized = True

    class PycairoContext(ctypes.Structure):
        _fields_ = [("PyObject_HEAD", ctypes.c_byte * object.__basicsize__),
            ("ctx", ctypes.c_void_p),
            ("base", ctypes.c_void_p)]

    _surface = cairo.ImageSurface (cairo.FORMAT_A8, 0, 0)

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


#def rgba_to_argb(stringImage):
    #tempBuffer = [None]*len(stringImage) # Create an empty array of the same size as stringImage
    #tempBuffer[0::4] = stringImage[3::4]
    #tempBuffer[1::4] = stringImage[0::4]
    #tempBuffer[2::4] = stringImage[1::4]
    #tempBuffer[3::4] = stringImage[2::4]
    #stringImage = ''.join(tempBuffer)
    #return stringImage

