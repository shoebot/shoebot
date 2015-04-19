#from __future__ import division

from pkg_resources import resource_filename, Requirement
ICON_FILE = resource_filename(Requirement.parse("shoebot"), "share/pixmaps/shoebot-ide.png")

import sys, os
from pgi.repository import Gtk

import os
import sys
import cairocffi as cairo
from shoebot.io.socket_server import SocketServerMixin
from shoebot.util import RecordingSurface

from shoebot.util import RecordingSurface

class ShoebotWidget(Gtk.DrawingArea, SocketServerMixin):
    '''
    Create a double buffered GTK+ widget on which we will draw using Cairo        
    '''

    # Draw in response to an expose-event
    def __init__(self, scale_fit=True, input_device=None):
        Gtk.DrawingArea.__init__(self)
        self.connect("draw", self.draw)

        self.scale_fit = scale_fit
        self.input_device = input_device

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

            if self.first_run or size.width > source_width or size.height > source_height:
                # Scale up by largest dimension
                if size.width > source_width:
                    scale_x = float(size.width) / float(source_width)
                else:
                    scale_x = 1.0

                if size.height > source_height:
                    scale_y = float(size.height) / float(source_height)
                else:
                    scale_y = 1.0

                if scale_x > scale_y:
                    cr.scale(scale_x, scale_x)
                    if self.input_device:
                        self.input_device.scale_x = scale_x
                        self.input_device.scale_y = scale_x
                else:
                    cr.scale(scale_y, scale_y)
                    if self.input_device:
                        self.input_device.scale_x = scale_y
                        self.input_device.scale_y = scale_y

        cr.set_source_surface(self.backing_store)
        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(0, 0,
                source_width, source_height)
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

