import cairo

from drawqueue import DrawQueue
from shoebot.util import RecordingSurface

class CairoDrawQueue(DrawQueue):
    '''
    Runs functions on a meta surface as the bot is running, instead of running
    them all at the end.

    TODO Threading:
    As functions are added to the queue, another thread takes them off the queue
    and draws them to the meta_surface

    Hacks:  1st command is currently special cased (it draws the background)
    '''
    def __init__(self, canvas_size):
        DrawQueue.__init__(self)
        self.meta_surface = RecordingSurface(*canvas_size)
        self.context = cairo.Context(self.meta_surface)
        self.count = 0
        self.initial_func = None

    def append(self, render_func):
        '''
        This needs to hand the function a queue so it
        can be executed by the rendering thread.
        '''
        ## super(DrawQueue, self).append(render_func)
        if self.count:
            render_func(self.context)
        else:
            self.initial_func = render_func
        self.count += 1

    def render(self, ctx):
        self.initial_func(ctx)
        ctx.set_source_surface(self.meta_surface)
        ctx.paint()
