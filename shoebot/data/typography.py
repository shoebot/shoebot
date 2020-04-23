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
from operator import attrgetter

from shoebot import ShoebotInstallError
from shoebot.core.backend import cairo, gi, driver

try:
    gi.require_version("Pango", "1.0")
    gi.require_version("PangoCairo", "1.0")
    from gi.repository import Pango, PangoCairo
except ValueError as e:
    global Pango, PangoCairo

    # workaround for readthedocs where Pango is not installed,
    print("Pango not found - typography will not be available.", file=sys.stderr)

    class FakePango(object):
        def __getattr__(self, item):
            raise NotImplementedError("FakePango does not implement %s" % item)

    Pango = FakePango()
    PangoCairo = FakePango()

from shoebot.data import Grob, BezierPath, ColorMixin, _copy_attrs
from cairo import PATH_MOVE_TO, PATH_LINE_TO, PATH_CURVE_TO, PATH_CLOSE_PATH


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


# Map Nodebox / Shoebot names to Pango:
def _style_name_to_pango(style="normal"):
    """
    Given a Shoebot/Nodebox style name return the a Pango constant.
    """
    if style == "normal":
        return Pango.Style.NORMAL
    elif style == "italic":
        return Pango.Style.ITALIC
    elif style == "oblique":
        return Pango.Style.OBLIQUE
    raise AttributeError(
        "Invalid font style, valid styles are: normal, italic and oblique."
    )


def _alignment_name_to_pango(alignment):
    if alignment == "right":
        return Pango.Alignment.RIGHT
    elif alignment == "center":
        return Pango.Alignment.CENTER
    elif alignment == "justify":
        return Pango.Alignment.LEFT

    return Pango.Alignment.LEFT


PANGO_WEIGHTS = {
    "ultralight": Pango.Weight.ULTRALIGHT,
    "light": Pango.Weight.LIGHT,
    "normal": Pango.Weight.NORMAL,
    "bold": Pango.Weight.BOLD,
    "ultrabold": Pango.Weight.ULTRABOLD,
    "heavy": Pango.Weight.HEAVY,
    None: Pango.Weight.NORMAL,  # default
}


def _weight_name_to_pango(weight="normal"):
    """
    :param weight:  "normal", or "bold"
    :return:  Corresponding pango font weight from Pango.Weight
    """
    if weight not in PANGO_WEIGHTS:
        raise AttributeError("Invalid font weight.")

    return PANGO_WEIGHTS.get(weight)


class Text(Grob, ColorMixin):
    """
    Changes from Nodebox 1:
        font in Nodebox is a native Cocoa font, here it is the font name.
        _fontsize, _fontsize, _lineheight, _align in Nodebox are public fields.

        Implementation of fonts uses Pango instead of Cocoa.
    """

    # several reference docs can be found at http://www.pyGtk.org/docs/pygtk/class-pangofontdescription.html

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
        enableRendering=True,
        **kwargs
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
        self.style = kwargs.get("style", "normal")
        self.weight = kwargs.get("weight", "normal")

        self.align = kwargs.get("align", canvas.align)
        self.indent = kwargs.get("indent")
        self.lineheight = kwargs.get("lineheight", canvas.lineheight)

        # Setup hidden vars for Cairo / Pango specific bits:
        self._ctx = ctx
        self._pangocairo_ctx = None
        self._pango_fontface = Pango.FontDescription.from_string(self.font)

        # then we set fontsize (multiplied by Pango.SCALE)
        self._pango_fontface.set_absolute_size(self.fontsize * Pango.SCALE)
        self._pango_fontface.set_style(_style_name_to_pango(self.style))
        self._pango_fontface.set_weight(_weight_name_to_pango(self.weight))

        # Pre-render some stuff to enable metrics sizing
        self._pre_render()

        if (
            enableRendering
        ):  # this way we do not render if we only need to create metrics
            if bool(ctx):
                self._render(self._ctx)
            else:
                # Normal rendering, can be deferred
                self._deferred_render()
        self._prerendered = enableRendering

    # pre rendering is needed to measure the metrics of the text, it's also useful to get the path, without the need to call _render()
    def _pre_render(self):
        # we use a new CairoContext to pre render the text
        rs = cairo.RecordingSurface(cairo.CONTENT_ALPHA, None)
        cr = cairo.Context(rs)
        cr = driver.ensure_pycairo_context(cr)
        self._pangocairo_ctx = pangocairo_create_context(cr)
        self._pango_layout = PangoCairo.create_layout(cr)
        # layout line spacing
        # TODO: the behaviour is not the same as nodebox yet
        # self.layout.set_spacing(int(((self.lineheight-1)*self._fontsize)*Pango.SCALE)) #pango requires an int casting
        # we pass pango font description and the text to the pango layout
        self._pango_layout.set_font_description(self._pango_fontface)
        self._pango_layout.set_text(self.text, -1)

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

    # this function is quite computational expensive
    # there should be a way to make it faster, by not creating a new context each time it's called

    @property
    def path(self):
        if not self._pangocairo_ctx:
            self._pre_render()

        # here we create a new cairo.Context in order to hold the pathdata
        tempCairoContext = cairo.Context(
            cairo.RecordingSurface(cairo.CONTENT_ALPHA, None)
        )
        tempCairoContext = driver.ensure_pycairo_context(tempCairoContext)
        tempCairoContext.move_to(self.x, self.y - self.baseline)
        # in here we create a pangoCairoContext in order to display layout on it

        # supposedly showlayout should work, but it fills the path instead,
        # therefore we use layout_path instead to render the layout to pangoCairoContext
        # tempCairoContext.show_layout(self.layout)
        PangoCairo.layout_path(tempCairoContext, self._pango_layout)
        # here we extract the path from the temporal cairo.Context we used to draw on the previous step
        pathdata = tempCairoContext.copy_path()

        # creates a BezierPath instance for storing new shoebot path
        p = BezierPath(self._bot)

        # parsing of cairo path to build a shoebot path
        for item in pathdata:
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
        return p

    def _get_center(self):
        """Returns the center point of the path, disregarding transforms.
        """
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
                "style",
                "weight",
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
