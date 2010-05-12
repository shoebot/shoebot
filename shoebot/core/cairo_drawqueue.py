import cairo

from drawqueue import DrawQueue
from shoebot.util import RecordingSurface

class CairoDrawQueue(DrawQueue):
    '''
    Runs functions on a meta surface as the bot is running, instead of running
    them all at the end.

    TODO Threading:
    As functions are added to the queue, another thread takes them off the queue
    and draws them to the recording_surface

    Hacks:  1st command is currently special cased (it draws the background)
    '''
    def __init__(self, canvas_size):
        DrawQueue.__init__(self)
        self.recording_surface = RecordingSurface(*canvas_size)
        self.context = cairo.Context(self.recording_surface)
        self.count = 0
        self.initial_func = None

    def append_immediate(self, render_func):
        '''
        ## TODO - The queue will execute up until render_func
        ##        is executed before returning.
        This is how snapshots of surfaces get back to the bot

        Note - Once threading is enabled, calling append immediate
        Will probably severly affect performance
        '''
        raise NotImplementedError()

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

    def render(self, cairo_ctx):
        self.initial_func(cairo_ctx)
        cairo_ctx.set_source_surface(self.recording_surface)
        cairo_ctx.paint()
