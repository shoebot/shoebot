from collections import deque
from math import pi as _pi
import cairo

from canvas import Canvas
from drawqueue import DrawQueue
from cairo_drawqueue import CairoDrawQueue

class CairoCanvas(Canvas):
    ''' Cairo implementation of Canvas '''
    def __init__(self, sink, enable_cairo_queue = False):
        Canvas.__init__(self, sink)
        self.size = None
        self.enable_cairo_queue = enable_cairo_queue
        self.reset_canvas()

    def initial_drawqueue(self):
        '''
        Once the canvas size has been set the
        CairoDrawQueue can be used for better
        performance (well, hopefully in future).
        '''
        if self.size and self.enable_cairo_queue:
            return CairoDrawQueue(self.size)
        else:
            return DrawQueue()

    def initial_transform(self):
        '''
        Return an identity matrix
        '''
        return cairo.Matrix()

    def reset_drawqueue(self):
        self.drawqueue = self.initial_drawqueue()
        self.drawqueue.append(self.ctx_render_background)

    def reset_transform(self):
        self.mode = self.DEFAULT_MODE
        self.matrix_stack = deque()
        self.transform = self.initial_transform()
        return self.transform

    ### Draw stuff
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
            ctx.translate(x + w / 2., y + h / 2.)
            ctx.scale(w / 2., h / 2.)
            ctx.arc(0., 0., 1., 0., 2 * _pi)
            ctx.close_path()
        return ellipse

    def rellineto_closure(self, x, y):
        def rellineto(ctx):
            ctx.rel_line_to(x, y)
        return rellineto
    
    def ctx_render_background(self, cairo_ctx):
        '''
        Draws the background colour of the bot
        '''
        cairo_ctx.set_source_rgba(*self.background)
        cairo_ctx.paint()

