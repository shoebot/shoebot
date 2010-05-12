from collections import deque

class DrawQueue:
    '''
    A list of draw commands, stored as callables that, are
    passed a set of parameters to draw on from the canvas
    implementation.
    '''
    def __init__(self, render_funcs = None):
        self.render_funcs = render_funcs or deque()

    def append_immediate(self, render_func):
        '''
        In implementations of drawqueue that use buffering
        this will run the whole queue up to this point
        '''
        raise NotImplementedError('Not supported in DrawQueue')

    def append(self, render_func):
        '''
        Add a render function to the queue
        '''
        self.render_funcs.append(render_func)

    def render(self, r_context):
        '''
        Call all the render functions with r_context

        r_context, is the render_context - Set of
        keyword args that should make sense to the
        canvas implementation
        '''
        for render_func in self.render_funcs:
            render_func(r_context)


class DrawQueueSink:
    '''
    DrawQueueSink, creates parameters for use by the draw queue.
    (the render_context).

    The render context is a set of platform sepecific
    parameters used by implementations of the drawqueue,
    canvas, and sink.
    '''
    def __init__(self):
        pass

    def render(self, size, frame, drawqueue):
        '''
        Accepts a drawqueue and
        '''
        r_context = self.create_rcontext(size, frame)
        drawqueue.render(r_context)
        self.rcontext_ready(size, frame, r_context)

    #def create_rcontext(self, size, frame):
    #    '''
    #    Returns a cairo context for drawing this
    #    frame of the bot
    #    '''
    #    raise NotImplementedError('Child class should implement create_rcontext')
    
    #def rcontext_ready(self, size, frame, r_context):
    #    '''
    #    Called when the bot has been rendered
    #    '''
    #    raise NotImplementedError('Child class should implement rcontext_ready')
