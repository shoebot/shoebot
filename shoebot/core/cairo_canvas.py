_svg_surface = None
def RecordingSurface(*size):
    '''
    We don't have RecordingSurfaces until cairo 1.10, so this kludge is used

    SVGSurfaces are created, but to stop them ever attempting to output, they
    are kept in a dict.

    When a surface is needed, create_similar is called to get a Surface from
    the SVGSurface of the same size
    '''
    if os.name == 'nt':
        fobj = 'nul'
    else:
        fobj = None
    if _svg_surface is None:
        _svg_surface = cairo.SVGSurface(fobj, 0, 0)
    return _svg_surface.create_similar(cairo.CONTENT_COLOR_ALPHA, *size)


class CairoCanvas(Canvas):
    ''' Cairo implementation of Canvas '''
    def __init__(self, ctx_sink, enable_cairo_queue = False):
        Canvas.__init__(self)
        self.size = None
        self.ctx_sink = ctx_sink
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

    def rotate(self, degrees):
        self.transform.rotate(_math.radians(degrees))

    def scale(self, size):
        self.transform.scale(size, size)
    
    def ctx_render_background(self, ctx):
        '''
        Draws the background colour of the bot
        '''
        ctx.set_source_rgb(*self.background)
        ctx.paint()

    def render(self, frame):
        '''
        Get a context from the CairoSink and render to it
        Once rendering is complete call ctx_ready
        '''
        ### TODO - Threading this could be a place to spawn
        ### a thread
        ctx = self.ctx_sink.ctx_create(self.size, frame)
        self.drawqueue.render(ctx)
        self.ctx_sink.ctx_ready(self.size, frame, ctx)

