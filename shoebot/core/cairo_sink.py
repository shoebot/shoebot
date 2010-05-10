class CairoSink:
    '''
    Cairo canvases need a CairoSink to create and recieve
    cairo contexts for it.
    '''
    def __init__(self):
        pass

    def ctx_create(self, context, frame):
        '''
        Returns a cairo context for drawing this
        frame of the bot
        '''
        raise NotImplementedExceptio()
    
    def ctx_ready(self, ctx):
        '''
        Called when the bot has been rendered
        '''
        raise NotImplementedExceptio()


class CairoImageSink(CairoSink):
    '''
    Generates cairo contexts that output to supported formats
    '''
    def __init__(self, filename, format = None, multifile = False):
        CairoSink.__init__(self)
        if format is None:
            format = os.path.splitext(filename)[1][1:].lower()
        self.format = format
        self.filename = filename
        self.multifile = multifile
        self.file_root, self.file_ext = os.path.splitext(filename)

    def _filename(self, frame):
        if self.multifile:
            return self.file_root + "_%03d" % frame + self.file_ext
        else:
            return self.filename

    def ctx_create(self, size, frame):
        '''
        Called when CairoCanvas needs a cairo context to draw on
        '''
        if self.format == 'pdf':
            surface = cairo.PDFSurface(self._filename(frame), *size)
        elif self.format == 'png':
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *size)
        elif self.format == 'ps':
            surface = cairo.PSSurface(cairo.FORMAT_ARGB32, *size)
        if self.format == 'svg':
            surface = cairo.SVGSurface(self._filename(frame), *size)
        return cairo.Context(surface)

    def ctx_ready(self, size, frame, ctx):
        '''
        Called when CairoCanvas has rendered a bot
        '''
        if self.format == 'png':
            surface = ctx.get_target()
            surface.write_to_png(self._filename(frame))


