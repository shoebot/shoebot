#!/usr/bin/env python

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
import cairo
import pango
import pangocairo
from shoebot.data import Grob, BezierPath, TransformMixin, ColorMixin, _copy_attrs
from shoebot.util import RecordingSurfaceA8
from cairo import PATH_MOVE_TO, PATH_LINE_TO, PATH_CURVE_TO, PATH_CLOSE_PATH

class Text(Grob, ColorMixin):

    def __init__(self, canvas, text, x=0, y=0, width=None, height=None, outline=False, ctx=None, **kwargs):
        Grob.__init__(self, canvas)
        ColorMixin.__init__(self, canvas, **kwargs)

        self._transform = canvas.transform

        self._ctx = ctx
        self._pang_ctx = None

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

        # here we start to do the magic with pango, first we set typeface    
        self._fontface = pango.FontDescription()
        self._fontface.set_family(self._fontfile)

        # then the font weight
        self._weight = pango.WEIGHT_NORMAL
        if kwargs.has_key("weight"):
            if kwargs["weight"]=="ultralight":
                self._weight = pango.WEIGHT_ULTRALIGHT
            elif kwargs["weight"]=="light":
                self._weight = pango.WEIGHT_LIGHT
            elif kwargs["weight"]=="bold":
                self._weight = pango.WEIGHT_BOLD
            elif kwargs["weight"]=="ultrabold":
                self._weight = pango.WEIGHT_ULTRABOLD
            elif kwargs["weight"]=="heavy":
                self._weight = pango.WEIGHT_HEAVY                                                
        self._fontface.set_weight(self._weight)

        # the variant
        self._variant = pango.VARIANT_NORMAL
        if kwargs.has_key("variant"):
            if kwargs["variant"]=="small-caps" or kwargs["variant"]=="smallcaps":
                self._variant = pango.VARIANT_SMALL_CAPS
        self._fontface.set_variant(self._variant)

        # the style        
        self._style = pango.STYLE_NORMAL
        if kwargs.has_key("style"):
            if kwargs["style"]=="italic" or kwargs["style"]=="oblique":
                self._style = pango.STYLE_ITALIC
        self._fontface.set_style(self._style)       
        # the stretch
        self._stretch = pango.STRETCH_NORMAL
        if kwargs.has_key("stretch"):
            if kwargs["stretch"]=="ultracondensed" or kwargs["stretch"]=="ultra-condensed":
                self._stretch = pango.STRETCH_ULTRA_CONDENSED
            if kwargs["stretch"]=="condensed":
                self._stretch = pango.STRETCH_CONDENSED
            if kwargs["stretch"]=="expanded":
                self._stretch = pango.STRETCH_EXPANDED            
            if kwargs["stretch"]=="ultraexpanded" or kwargs["stretch"]=="ultra-expanded":
                self._stretch = pango.STRETCH_ULTRA_EXPANDED
        self._fontface.set_stretch(self._stretch)                                              
        # then we set fontsize (multiplied by pango.SCALE)
        self._fontface.set_absolute_size(self._fontsize*pango.SCALE)


        if bool(ctx):
            self._render(self._ctx)
        else:
            # Normal rendering, can be deferred
            self._deferred_render()

    def _get_context(self):
        self._ctx = self._ctx or cairo.Context(RecordingSurfaceA8(0, 0))
        return self._ctx

    def _render(self, ctx = None):
        ctx = ctx or self._get_context()
        # we build a PangoCairo context linked to cairo context
        # then we create a pango layout
        self._pang_ctx = pangocairo.CairoContext(ctx)
        self.layout = self._pang_ctx.create_layout()
        # layout line spacing
        # TODO: the behaviour is not the same as nodebox yet
        self.layout.set_spacing(((self._lineheight-1)*self._fontsize)*pango.SCALE)
        # we pass pango font description and the text to the pango layout
        self.layout.set_font_description(self._fontface)
        self.layout.set_text(self.text)
        # check if max text width is set and pass it to pango layout
        # text will wrap, meanwhile it checks if and indent has to be applied
        # indent is subordinated to width because it makes no sense on a single-line text block
        if self.width:
            self.layout.set_width(self.width*pango.SCALE)
            if self._indent:
                self.layout.set_indent(self._indent*pango.SCALE)                
        # set text alignment    
        if self._align == "right":
            self.layout.set_alignment(pango.ALIGN_RIGHT)
        elif self._align == "center":
            self.layout.set_alignment(pango.ALIGN_CENTER)
        elif self._align == "justify":
            self.layout.set_alignment(pango.ALIGN_LEFT)
            self.layout.set_justify(True)
        else:
            self.layout.set_alignment(pango.ALIGN_LEFT)

        if self._fillcolor is not None:
            # Go to initial point (CORNER or CENTER):
            transform = self._call_transform_mode(self._transform)
            ctx.set_matrix(self._canvas.transform)

            ctx.move_to(self.x,self.y)
            
            if self._outline is False:
                ctx.set_source_rgba(*self._fillcolor)
            self._pang_ctx.show_layout(self.layout)
            self._pang_ctx.update_layout(self.layout)
        


    # This version is probably more pangoesque, but the layout iterator
    # caused segfaults on some system
    #def _get_baseline(self):
        #self.iter = self.layout.get_iter()
        #baseline_y = self.iter.get_baseline()
        #baseline_delta = baseline_y/pango.SCALE
        #return (baseline_delta)
    #baseline = property(_get_baseline)

    def _get_baseline(self):
        # retrieves first line of text block
        first_line = self.layout.get_line(0)
        # get the logical extents rectangle of first line
        first_line_extent = first_line.get_extents()[1]
        # get the descent value, in order to calculate baseline position
        first_line_descent = pango.DESCENT(first_line.get_extents()[1])
        # gets the baseline offset from the top of thext block
        baseline_delta = (first_line_extent[3]-first_line_descent)/pango.SCALE
        return (baseline_delta)
    baseline = property(_get_baseline)

    
    def _get_metrics(self):
        w,h = self.layout.get_pixel_size()
        return (w,h)
    metrics = property(_get_metrics)

    def _get_path(self):
        if not self._pang_ctx:
            self._render()
        # add pango layout to current cairo path in temporary context
        self._pang_ctx.layout_path(self.layout)
        # retrieve current path from current context
        pathdata = self._get_context().copy_path()
        # creates a BezierPath instance for storing new shoebot path
        p = BezierPath(self._canvas)
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
        # cairo function for freeing path memory
        pathdata.path_destroy()
    path = property(_get_path)

    def _get_center(self):
        '''Returns the center point of the path, disregarding transforms.
        '''
        w,h = self.layout.get_pixel_size()
        x = (self.x+w/2)
        y = (self.y+h/2)
        return (x,y)
    center = property(_get_center)

    def copy(self):
        new = self.__class__(self._bot, self.text)
        _copy_attrs(self, new,
            ('x', 'y', 'width', 'height', '_transform', '_transformmode',
            '_fillcolor', '_fontfile', '_fontsize', '_align', '_lineheight'))
        return new

