from collections import deque
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
    
    def ctx_render_background(self, ctx):
        '''
        Draws the background colour of the bot
        '''
        ctx.set_source_rgba(*self.background)
        ctx.paint()

