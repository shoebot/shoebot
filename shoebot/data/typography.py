#!/usr/bin/env python2

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

from shoebot import ShoebotInstallError
from shoebot.core.backend import cairo, gi, driver


try:
    gi.require_version('Pango', '1.0')
    gi.require_version('PangoCairo', '1.0')
    from gi.repository import Pango, PangoCairo
except ValueError as e:
    global Pango, PangoCairo

    # workaround for readthedocs where Pango is not installed
    print("Pango not found - typography will not be available.")

    class FakePango(object):
        def __getattr__(self, item):
            raise e
    Pango = FakePango()
    PangoCairo = FakePango()

from shoebot.data import Grob, BezierPath, ColorMixin, _copy_attrs
from cairo import PATH_MOVE_TO, PATH_LINE_TO, PATH_CURVE_TO, PATH_CLOSE_PATH


def pangocairo_create_context(cr):
    """
    If python-gi-cairo is not installed, using PangoCairo.create_context
    dies with an unhelpful KeyError, check for that and output somethig
    useful.
    """
    # TODO move this to core.backend
    try:
        return PangoCairo.create_context(cr)
    except KeyError as e:
        if e.args == ('could not find foreign type Context',):
            raise ShoebotInstallError("Error creating PangoCairo missing dependency: python-gi-cairo")
        else:
            raise


class Text(Grob, ColorMixin):

    # several reference docs can be found at http://www.pyGtk.org/docs/pygtk/class-pangofontdescription.html

    def __init__(self, bot, text, x=0, y=0, width=None, height=None, outline=False, ctx=None, enableRendering=True, **kwargs):
        self._canvas = canvas = bot._canvas
        Grob.__init__(self, bot)
        ColorMixin.__init__(self, **kwargs)

        # self._transform = canvas.transform # TODO remove - this is in grob

        self._ctx = ctx
        self._pang_ctx = None

        self._doRender = enableRendering

        self.text = unicode(text)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self._outline = outline

        self._fontfile = kwargs.get('font', canvas.fontfile)
        self._fontsize = kwargs.get('fontsize', canvas.fontsize)
        self._lineheight = kwargs.get('lineheight', canvas.lineheight)
        self._align = kwargs.get('align', canvas.align)
        self._indent = kwargs.get("indent")

        # we use the pango parser instead of trying this by hand
        self._fontface = Pango.FontDescription.from_string(self._fontfile)

        # then we set fontsize (multiplied by Pango.SCALE)
        self._fontface.set_absolute_size(self._fontsize * Pango.SCALE)

        # the style
        self._style = Pango.Style.NORMAL
        if kwargs.get("style") in ["italic", "oblique"]:
            self._style = Pango.Style.ITALIC
        self._fontface.set_style(self._style)

        # we need to pre-render some stuff to enable metrics sizing
        self._pre_render()

        if self._doRender:  # this way we do not render if we only need to create metrics
            if bool(ctx):
                self._render(self._ctx)
            else:
                # Normal rendering, can be deferred
                self._deferred_render()

    # pre rendering is needed to measure the metrics of the text, it's also useful to get the path, without the need to call _render()
    def _pre_render(self):
        # we use a new CairoContext to pre render the text
        rs = cairo.RecordingSurface(cairo.CONTENT_ALPHA, None)
        cr = cairo.Context(rs)
        cr = driver.ensure_pycairo_context(cr)
        self._pang_ctx = pangocairo_create_context(cr)
        self.layout = PangoCairo.create_layout(cr)
        # layout line spacing
        # TODO: the behaviour is not the same as nodebox yet
        # self.layout.set_spacing(int(((self._lineheight-1)*self._fontsize)*Pango.SCALE)) #pango requires an int casting
        # we pass pango font description and the text to the pango layout
        self.layout.set_font_description(self._fontface)
        self.layout.set_text(self.text, -1)
        # check if max text width is set and pass it to pango layout
        # text will wrap, meanwhile it checks if and indent has to be applied
        # indent is subordinated to width because it makes no sense on a single-line text block
        if self.width:
            self.layout.set_width(int(self.width) * Pango.SCALE)
            if self._indent:
                self.layout.set_indent(self._indent * Pango.SCALE)
        # set text alignment
        if self._align == "right":
            self.layout.set_alignment(Pango.Alignment.RIGHT)
        elif self._align == "center":
            self.layout.set_alignment(Pango.Alignment.CENTER)
        elif self._align == "justify":
            self.layout.set_alignment(Pango.Alignment.LEFT)
            self.layout.set_justify(True)
        else:
            self.layout.set_alignment(Pango.Alignment.LEFT)

    def _get_context(self):
        self._ctx = self._ctx or cairo.Context(cairo.RecordingSurface(cairo.CONTENT_ALPHA, None))
        return self._ctx

    def _render(self, ctx=None):
        if not self._doRender:
            return
        ctx = ctx or self._get_context()
        pycairo_ctx = driver.ensure_pycairo_context(ctx)
        # we build a PangoCairo context linked to cairo context
        # then we create a pango layout

        # we update the context as we already used a null one on the pre-rendering
        # supposedly there should not be a big performance penalty
        self._pang_ctx = pangocairo_create_context(pycairo_ctx)

        if self._fillcolor is not None:
            # Go to initial point (CORNER or CENTER):
            transform = self._call_transform_mode(self._transform)
            ctx.set_matrix(transform)

            ctx.translate(self.x, self.y - self.baseline)

            if self._outline is False:
                ctx.set_source_rgba(*self._fillcolor)
            PangoCairo.show_layout(pycairo_ctx, self.layout)
            PangoCairo.update_layout(pycairo_ctx, self.layout)

    # This version is probably more pangoesque, but the layout iterator
    # caused segfaults on some system
    @property
    def baseline(self):
        self.iter = self.layout.get_iter()
        baseline_y = self.iter.get_baseline()
        baseline_delta = baseline_y / Pango.SCALE
        return (baseline_delta)

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
        w, h = self.layout.get_pixel_size()
        return w, h

    # this function is quite computational expensive
    # there should be a way to make it faster, by not creating a new context each time it's called

    @property
    def path(self):
        if not self._pang_ctx:
            self._pre_render()

        # here we create a new cairo.Context in order to hold the pathdata
        tempCairoContext = cairo.Context(cairo.RecordingSurface(cairo.CONTENT_ALPHA, None))
        tempCairoContext = driver.ensure_pycairo_context(tempCairoContext)
        tempCairoContext.move_to(self.x, self.y - self.baseline)
        # in here we create a pangoCairoContext in order to display layout on it

        # supposedly showlayout should work, but it fills the path instead,
        # therefore we use layout_path instead to render the layout to pangoCairoContext
        # tempCairoContext.show_layout(self.layout)
        PangoCairo.layout_path(tempCairoContext, self.layout)
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
        # cairo function for freeing path memory
        return p

    def _get_center(self):
        '''Returns the center point of the path, disregarding transforms.
        '''
        w, h = self.layout.get_pixel_size()
        x = (self.x + w / 2)
        y = (self.y + h / 2)
        return x, y

    center = property(_get_center)

    def copy(self):
        new = self.__class__(self._bot, self.text)
        _copy_attrs(self, new,
                    ('x', 'y', 'width', 'height', '_transform', '_transformmode',
                     '_fillcolor', '_fontfile', '_fontsize', '_align', '_lineheight'))
        return new
