#from __future__ import division
import sys, os
import gtk
import cairo
from socket_server import SocketServerMixin

from shoebot.core import DrawQueueSink
from shoebot.util import RecordingSurface

ICON_FILE = os.path.join(sys.prefix, 'share', 'shoebot', 'icon.png')

class ShoebotWidget(gtk.DrawingArea, DrawQueueSink, SocketServerMixin):
    '''
    Create a double buffered GTK+ widget on which we will draw using Cairo        
    '''

    # Draw in response to an expose-event
    __gsignals__ = { "expose-event": "override" }
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        DrawQueueSink.__init__(self)
        
        # Default picture is the shoebot icon
        if os.path.isfile(ICON_FILE):
            self.backing_store = cairo.ImageSurface.create_from_png(ICON_FILE)
        else:
            self.backing_store = cairo.ImageSurface(cairo.FORMAT_ARGB32, 64, 64) 
        self.size = None
	self.last_rendering = None

    def do_expose_event(self, event):
        '''
        Draw just the exposed part of the backing store
        '''
        # Create the cairo context
        cr = self.window.cairo_create()

        cr.set_source_surface(self.backing_store)
        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y,
                event.area.width, event.area.height)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.fill()

    def create_rcontext(self, size, frame):
        '''
        Creates a meta surface for the bot to draw on

        Uses a proxy to an SVGSurface to render on so 
        it's scalable
        '''
        if self.window and not self.size:
            self.set_size_request(*size)
            self.size = size
        meta_surface = RecordingSurface(*size)
        return cairo.Context(meta_surface)

    def rendering_finished(self, size, frame, cairo_ctx):
        '''
        Update the backing store from a cairo context and
        schedule a redraw (expose event)
        '''
        if (self.backing_store.get_width(), self.backing_store.get_height()) == size:
            backing_store = self.backing_store
        else:
            backing_store = cairo.ImageSurface(cairo.FORMAT_ARGB32, *size)
        
        cr = cairo.Context(backing_store)
        cr.set_source_surface(cairo_ctx.get_target())
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        
        self.backing_store = backing_store
        self.queue_draw()
        
        while gtk.events_pending():
            gtk.main_iteration()
