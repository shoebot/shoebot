import os
import cairo

from drawqueue import DrawQueueSink

class CairoImageSink(DrawQueueSink):
    '''
    DrawQueueSink that uses cairo contexts as the render context.
    '''
    def __init__(self, filename, format = None, multifile = False):
        DrawQueueSink.__init__(self)
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

    def create_rcontext(self, size, frame):
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

    def rcontext_ready(self, size, frame, cairo_ctx):
        '''
        Called when CairoCanvas has rendered a bot
        '''
        if self.format == 'png':
            surface = ctx.get_target()
            surface.write_to_png(self._filename(frame))


