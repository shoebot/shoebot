#from __future__ import division
import sys, os
from gi.repository import Gtk
import cairo
from socket_server import SocketServerMixin

from shoebot.core import DrawQueueSink
from shoebot.util import RecordingSurface

ICON_FILE = os.path.join(sys.prefix, 'share', 'pixmaps', 'shoebot-ide.png')

class ShoebotWidget(Gtk.DrawingArea, DrawQueueSink, SocketServerMixin):
    '''
    Create a double buffered GTK+ widget on which we will draw using Cairo        
    '''

    # Draw in response to an expose-event
    def __init__(self, scale_fit = True):
        Gtk.DrawingArea.__init__(self)
        DrawQueueSink.__init__(self)
        self.connect("draw", self.draw)

        self.scale_fit = scale_fit

        # Default picture is the shoebot icon
        if os.path.isfile(ICON_FILE):
            self.backing_store = cairo.ImageSurface.create_from_png(ICON_FILE)
        else:
            self.backing_store = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 400)
        self.size = None
        self.first_run = True
	self.last_rendering = None

    def draw(self, widget, cr):
        '''
        Draw just the exposed part of the backing store
        '''

        # Create the cairo context
        if self.scale_fit:
            source_width = self.backing_store.get_width()
            source_height = self.backing_store.get_height()

            size = self.get_allocation()

            if size.width > source_width or size.height > source_height:
                # Scale up by largest dimension
                if size.width > source_width:
                    xscale = float(size.width) / float(source_width)
                else:
                    xscale = 1.0

                if size.height > source_height:
                    yscale = float(size.height) / float(source_height)
                else:
                    yscale = 1.0

                if xscale > yscale:
                    cr.scale(xscale, xscale)
                else:
                    cr.scale(yscale, yscale)


        cr.set_source_surface(self.backing_store)
        cr.rectangle(0, 0,
                size.width, size.height)
        if self.first_run:
            cr.set_operator(cairo.OPERATOR_OVER)
        else:
            cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.fill()

    def create_rcontext(self, size, frame):
        '''
        Creates a meta surface for the bot to draw on

        Uses a proxy to an SVGSurface to render on so 
        it's scalable
        '''
        if self.get_window() and not self.size:
            self.set_size_request(*size)
            self.size = size
            while Gtk.events_pending():
                Gtk.main_iteration_do(False)
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
        
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)

