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
'''Cairo implementation of the canvas'''
import os.path

from math import pi as _pi

from .backend import cairo
from .input_device import InputDeviceMixin
from .canvas import Canvas
from .drawqueue import DrawQueue


class CairoCanvas(Canvas):
    ''' Cairo implementation of Canvas '''
    def __init__(self, sink):
        Canvas.__init__(self, sink)
        self.size = None

    def initial_drawqueue(self):
        return DrawQueue()

    def initial_transform(self):
        '''
        Return an identity matrix
        '''
        return cairo.Matrix()

    def get_input_device(self):
        if isinstance(self.sink, InputDeviceMixin):
            return self.sink
        else:
            return None

    def reset_drawqueue(self):
        self._drawqueue = self.initial_drawqueue()
        self._drawqueue.append(self.ctx_render_background)

    def reset_transform(self):
        self.mode = self.DEFAULT_MODE
        self.transform = self.initial_transform()
        return self.transform

    # Draw stuff
    def push_matrix(self):
        self.matrix_stack.append(self.transform)
        self.transform = cairo.Matrix(*self.transform)

    def pop_matrix(self):
        self.transform = self.matrix_stack.pop()

    def translate(self, xt, yt):
        self.transform.translate(xt, yt)

    def rotate(self, radians):
        self.transform.rotate(radians)

    def scale(self, w, h):
        self.transform.scale(w, h)

    def moveto_closure(self, x, y):
        def moveto(ctx):
            ctx.move_to(x, y)
        return moveto

    def lineto_closure(self, x, y):
        def lineto(ctx):
            ctx.line_to(x, y)
        return lineto

    def curveto_closure(self, x1, y1, x2, y2, x3, y3):
        def curveto(ctx):
            ctx.curve_to(x1, y1, x2, y2, x3, y3)
        return curveto

    def closepath_closure(self):
        def closepath(ctx):
            ctx.close_path()
        return closepath

    def ellipse_closure(self, x, y, w, h):
        def ellipse(ctx):
            if w != 0.0 and h != 0.0:
                ctx.save()
                ctx.translate(x + w / 2., y + h / 2.)
                ctx.scale(w * 0.5, h * 0.5)
                ctx.arc(0., 0., 1., 0., 2 * _pi)
                ctx.close_path()
                ctx.restore()
        return ellipse

    def rellineto_closure(self, x, y):
        def rellineto(ctx):
            ctx.rel_line_to(x, y)
        return rellineto

    def output_closure(self, target, file_number=None):
        '''
        Function to output to a cairo surface

        target is a cairo Context or filename
        if file_number is set, then files will be numbered
        (this is usually set to the current frame number)
        '''
        def output_context(ctx):
            target_ctx = target
            target_ctx.set_source_surface(ctx.get_target())
            target_ctx.paint()
            return target_ctx

        def output_surface(ctx):
            target_ctx = cairo.Context(target)
            target_ctx.set_source_surface(ctx.get_target())
            target_ctx.paint()
            return target_ctx

        def output_file(ctx):
            root, extension = os.path.splitext(target)
            if file_number:
                filename = '%s_%04d%s' % (root, file_number, extension)
            else:
                filename = target

            extension = extension.lower()
            if extension == '.png':
                surface = ctx.get_target()
                surface.write_to_png(target)
            elif extension == '.pdf':
                target_ctx = cairo.Context(cairo.PDFSurface(filename, *self.size_or_default()))
                target_ctx.set_source_surface(ctx.get_target())
                target_ctx.paint()
            elif extension in ('.ps', '.eps'):
                target_ctx = cairo.Context(cairo.PSSurface(filename, *self.size_or_default()))
                if extension == '.eps':
                    target_ctx.set_eps(extension='.eps')
                target_ctx.set_source_surface(ctx.get_target())
                target_ctx.paint()
            elif extension == '.svg':
                target_ctx = cairo.Context(cairo.SVGSurface(filename, *self.size_or_default()))
                target_ctx.set_source_surface(ctx.get_target())
                target_ctx.paint()
            return filename

        if isinstance(target, cairo.Context):
            return output_context
        elif isinstance(target, cairo.Surface):
            return output_surface
        else:
            return output_file

    def ctx_render_background(self, cairo_ctx):
        '''
        Draws the background colour of the bot
        '''
        # TODO - rename this
        cairo_ctx.set_source_rgba(*self.background)
        cairo_ctx.paint()
