#!/usr/bin/env python3

# This file is part of Shoebot.
# Copyright (C) 2007-2009 the Shoebot authors
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
import sys
from collections import namedtuple
from enum import Enum

from cairo import PATH_CLOSE_PATH, PATH_CURVE_TO, PATH_LINE_TO, PATH_MOVE_TO

from shoebot.core.backend import cairo, driver, gi
from shoebot.util import ShoebotInstallError, _copy_attrs

from .basecolor import ColorMixin
from .bezier import BezierPath
from .grob import Grob

try:
    gi.require_version("Pango", "1.0")
    gi.require_version("PangoCairo", "1.0")
    from gi.repository import Pango, PangoCairo
except ValueError as no_pango:
    global Pango, PangoCairo

    # workaround for readthedocs where Pango is not installed,
    print(_("Pango not found - typography will not be available."), file=sys.stderr)

    class FakePango(object):
        class Weight(Enum):
            # Weights copied from PangoWeight
            THIN = 100
            ULTRALIGHT = 200
            LIGHT = 300
            SEMILIGHT = 350
            BOOK = 380
            NORMAL = 400
            MEDIUM = 500
            SEMIBOLD = 600
            BOLD = 700
            ULTRABOLD = 800
            HEAVY = 900
            ULTRAHEAVY = 1000

        def __getattr__(self, item):
            if item == "Weight":
                return FakePango.Weight

            raise NotImplementedError("FakePango does not implement %s" % item)

    Pango = FakePango()
    PangoCairo = FakePango()


# Pango Utility functions
def pangocairo_create_context(cr):
    """
    Create a PangoCairo context from a given pycairo context.

    If python-gi-cairo is not installed PangoCairo.create_context dies
    with an unhelpful KeyError, output a better error if that happens.
    """
    # TODO move this to core.backend
    try:
        return PangoCairo.create_context(cr)
    except KeyError as e:
        if e.args == ("could not find foreign type Context",):
            raise ShoebotInstallError(
                "Error creating PangoCairo missing dependency: python-gi-cairo"
            )
    raise


def _alignment_name_to_pango(alignment):
    if alignment == "right":
        return Pango.Alignment.RIGHT
    elif alignment == "center":
        return Pango.Alignment.CENTER
    elif alignment == "justify":
        return Pango.Alignment.LEFT

    return Pango.Alignment.LEFT


TextBounds = namedtuple("TextBounds", "x y width height")
TextBounds.__doc__ = """\
Text Bounds in pixels.

:param x: X position in pixels.
:param y: Y position in pixels.
:param width: Width in pixels.
:param height: Height in pixels."""


class Text(Grob, ColorMixin):
    """
    Changes from Nodebox 1:
        font in Nodebox is a native Cocoa font, here it is the font name.
        _fontsize, _fontsize, _lineheight, _align in Nodebox are public fields.

        Implementation of fonts uses Pango instead of Cocoa.
    """

    def __init__(
        self,
        bot,
        text,
        x=0,
        y=0,
        width=None,
        height=None,
        outline=False,
        ctx=None,
        draw=True,
        **kwargs,
    ):
        self._canvas = canvas = bot._canvas
        Grob.__init__(self, bot)
        ColorMixin.__init__(self, **kwargs)

        self.text = str(text)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.outline = outline

        self.font = kwargs.get("font", canvas.fontfile)
        self.fontsize = kwargs.get("fontsize", canvas.fontsize)
        self.align = kwargs.get("align", canvas.align)
        self.lineheight = kwargs.get("lineheight", canvas.lineheight)
        self.indent = kwargs.get("indent")

        self.hintstyle = kwargs.get("hintstyle", canvas.hintstyle)
        self.hintmetrics = kwargs.get("hintmetrics", canvas.hintmetrics)
        self.antialias = kwargs.get("antialias", canvas.antialias)
        self.subpixelorder = kwargs.get("subpixelorder", canvas.subpixelorder)
        # these are the settings that we have to define with the
        # Pango.Markup hack (see below in _pre_render), so it's neater to
        # have them in a dict
        self.markup_vars = {
            arg: kwargs[arg]
            for arg in (
                "underline",
                "underlinecolor",
                "overline",
                "overlinecolor",
            )
            if arg in kwargs
        }
        if "tracking" in kwargs:
            # different name in Pango
            # and also the value of letter_spacing is in 1/1024ths of
            # a pt, so we multiply that. AND it needs ints
            self.markup_vars["letter_spacing"] = int(1024 * kwargs["tracking"])

        # Setup hidden vars for Cairo / Pango specific bits:
        self._ctx = ctx
        self._pangocairo_ctx = None
        self._pango_fontface = Pango.FontDescription.from_string(self.font)

        # then we set fontsize (multiplied by Pango.SCALE)
        self._pango_fontface.set_absolute_size(self.fontsize * Pango.SCALE)

        # Pre-render some stuff to enable metrics sizing
        self._pre_render()

        if draw:
            # this way we do not render if we only need to create metrics
            if bool(ctx):
                self._render(self._ctx)
            else:
                # Normal rendering, can be deferred
                self._deferred_render()
        self._prerendered = draw

    # pre rendering is needed to measure the metrics of the text, it's also
    # useful to get the path, without the need to call _render()
    def _pre_render(self):
        # we use a new CairoContext to pre render the text
        rs = cairo.RecordingSurface(cairo.CONTENT_ALPHA, None)
        cr = cairo.Context(rs)
        cr = driver.ensure_pycairo_context(cr)

        # apply font options if set
        if self.hintstyle or self.hintmetrics or self.subpixelorder or self.antialias:
            opts = cairo.FontOptions()
            # map values to Cairo constants
            if self.antialias:
                opts.set_antialias(getattr(cairo.Antialias, self.antialias.upper()))
            if self.hintstyle:
                opts.set_hint_style(getattr(cairo.HintStyle, self.hintstyle.upper()))
            if self.hintmetrics:
                opts.set_hint_metrics(
                    getattr(cairo.HintMetrics, self.hintmetrics.upper())
                )
            if self.subpixelorder:
                opts.set_subpixel_order(
                    getattr(cairo.SubpixelOrder, self.subpixelorder.upper())
                )
            cr.set_font_options(opts)

        self._pangocairo_ctx = pangocairo_create_context(cr)
        self._pango_layout = PangoCairo.create_layout(cr)
        # layout line spacing
        # TODO: the behaviour is not the same as nodebox yet
        # self.layout.set_spacing(int(((self.lineheight-1)*self._fontsize)*Pango.SCALE)) #pango requires an int casting
        # we pass pango font description and the text to the pango layout
        self._pango_layout.set_font_description(self._pango_fontface)

        if not self.markup_vars:
            self._pango_layout.set_text(self.text, -1)
            return
        # some of the specified settings require a Pango.Markup hack
        # see https://stackoverflow.com/questions/55533312/how-to-create-a-letter-spacing-attribute-with-pycairo
        # and https://developer.gnome.org/pango/1.46/pango-Markup.html

        # we want to output something like
        # <span letter_spacing="2048">Hello World</span>
        markup_styles = " ".join(
            [f'{setting}="{value}"' for setting, value in self.markup_vars.items()]
        )
        self._pango_layout.set_markup(f"<span {markup_styles}>{self.text}</span>")

        # check if max text width is set and pass it to pango layout
        # text will wrap, meanwhile it checks if and indent has to be applied
        # indent is subordinated to width because it makes no sense on a single-line text block
        if self.width:
            self._pango_layout.set_width(int(self.width) * Pango.SCALE)
            if self.indent:
                self._pango_layout.set_indent(self.indent * Pango.SCALE)
        # set text alignment
        self._pango_layout.set_alignment(_alignment_name_to_pango(self.align))
        if self.align == "justify":
            self._pango_layout.set_justify(True)

    def _get_context(self):
        self._ctx = self._ctx or cairo.Context(
            cairo.RecordingSurface(cairo.CONTENT_ALPHA, None)
        )
        return self._ctx

    def _render(self, ctx=None):
        if not self._prerendered:
            return
        ctx = ctx or self._get_context()
        pycairo_ctx = driver.ensure_pycairo_context(ctx)
        # we build a PangoCairo context linked to cairo context
        # then we create a pango layout.
        # Update the context as we already used a null one on the pre-rendering
        # supposedly there should not be a big performance penalty
        self._pangocairo_ctx = pangocairo_create_context(pycairo_ctx)

        if self._fillcolor is None:
            return

        # Go to initial point (CORNER or CENTER):
        transform = self._call_transform_mode(self._transform)
        ctx.set_matrix(transform)
        ctx.translate(self.x, self.y - self.baseline)

        if not self.outline:
            # In outline, the caller will stroke the generated path
            ctx.set_source_rgba(*self._fillcolor)
        PangoCairo.show_layout(pycairo_ctx, self._pango_layout)
        PangoCairo.update_layout(pycairo_ctx, self._pango_layout)

    # This version is probably more pangoesque, but the layout iterator
    # caused segfaults on some system
    @property
    def baseline(self):
        self.iter = self._pango_layout.get_iter()
        baseline_y = self.iter.get_baseline()
        baseline_delta = baseline_y / Pango.SCALE
        return baseline_delta

    #    @property
    #    def baseline(self):
    #        # retrieves first line of text block
    #        first_line = self.layout.get_line(0)
    #        # get the logical extents rectangle of first line
    #        first_line_extent = first_line.get_extents()[1]
    #        # get the descent value, in order to calculate baseline position
    #        first_line_descent = Pango.DESCENT(first_line.get_extents()[1])
    #        # gets the baseline offset from the top of thext block
    #        baseline_delta = (first_line_extent[3]-first_line_descent)/Pango.SCALE
    #        return (baseline_delta)

    @property
    def metrics(self):
        w, h = self._pango_layout.get_pixel_size()
        return w, h

    @property
    def bounds(self):
        """
        :return: TextBounds namedtuple containing bounds as (x, y, width, height)
        """
        bounds_rect, _ = self._pango_layout.get_pixel_extents()
        return TextBounds(
            bounds_rect.x + self.x,
            bounds_rect.y + self.y - self.baseline,
            bounds_rect.width,
            bounds_rect.height,
        )

    # this function is quite computational expensive
    # there should be a way to make it faster, by not creating a new context each time it's called

    @property
    def path(self):
        if not self._pangocairo_ctx:
            self._pre_render()

        # Render path data to a temporary cairo Context
        cairo_ctx = cairo.Context(cairo.RecordingSurface(cairo.CONTENT_ALPHA, None))
        cairo_ctx = driver.ensure_pycairo_context(cairo_ctx)
        cairo_ctx.move_to(self.x, self.y - self.baseline)
        # show_layout should work here, but fills the path instead,
        # instead, use layout_path to render the layout.
        PangoCairo.layout_path(cairo_ctx, self._pango_layout)

        # Parse cairo path into Shoebot BezierPath
        cairo_text_path = cairo_ctx.copy_path()
        p = BezierPath(self._bot)
        for item in cairo_text_path:
            cmd = item[0]
            args = item[1]
            if cmd == PATH_MOVE_TO:
                p.moveto(*args)
            elif cmd == PATH_LINE_TO:
                p.lineto(*args)
            elif cmd == PATH_CURVE_TO:
                p.curveto(*args)
            elif cmd == PATH_CLOSE_PATH:
                p.closepath()

        del cairo_ctx
        return p

    def _get_center(self):
        """Returns the center point of the path, disregarding transforms."""
        w, h = self._pango_layout.get_pixel_size()
        x = self.x + w / 2
        y = self.y + h / 2
        return x, y

    center = property(_get_center)

    def copy(self):
        copied_instance = self.__class__(self._bot, self.text)
        _copy_attrs(
            self,
            copied_instance,
            (
                "x",
                "y",
                "width",
                "height",
                "_fillcolor",
                "fontfile",
                "fontsize",
                "align",
                "lineheight",
                "_transform",
                "_transformmode",
            ),
        )
        return copied_instance
