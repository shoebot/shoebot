from __future__ import division
import sys, os
import gtk
import gobject
import cairo
import shoebot
from shoebot.gui import SocketServerMixin, VarWindow
from shoebot.core import NodeBot, DrawBot

import locale
import gettext

APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
#gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext

NODEBOX = 'nodebox'
DRAWBOT = 'drawbot'

ICON_FILE = os.path.join(sys.prefix, 'share', 'shoebot', 'icon.png')

class GtkWidget(gtk.DrawingArea, CairoSink, SocketServerMixin):
    '''Create a GTK+ widget on which we will draw using Cairo'''

    # Draw in response to an expose-event
    __gsignals__ = { "expose-event": "override" }
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        CairoSink.__init__(self)
        
        if os.path.isfile(SHOEBOT_LOGO):
            self.backing_store = cairo.ImageSurface.create_from_png(SHOEBOT_LOGO)
        else:
            self.backing_store = cairo.ImageSurface(cairo.FORMAT_ARGB32, 64, 64) 
        self.size = None

    def as_window(self, title = None):
        '''
        Create a Gtk Window and add this Widget to it, returns the widget
        '''
        window = gtk.Window()
        if title:
            window.set_title(title)
        window.connect("delete-event", gtk.main_quit)

        self.show()
        window.add(self)
        window.present()

        while gtk.events_pending():
            gtk.main_iteration()

        return self

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

    def ctx_create(self, size, frame):
        '''
        Creates a meta surface for the bot to draw on

        As we don't have meta surfaces yet, use a PDFSurface
        with the buffer set to None
        '''
        if self.window and not self.size:
            self.set_size_request(*size)
            self.size = size
        meta_surface = RecordingSurface(*size)
        return cairo.Context(meta_surface)

    def ctx_ready(self, size, frame, ctx):
        '''
        Update the backing store from a cairo context and
        schedule a redraw (expose event)
        '''
        if (self.backing_store.get_width(), self.backing_store.get_height()) == size:
            backing_store = self.backing_store
        else:
            backing_store = cairo.ImageSurface(cairo.FORMAT_ARGB32, *size)
        
        cr = cairo.Context(backing_store)
        cr.set_source_surface(ctx.get_target())
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        
        self.backing_store = backing_store
        self.queue_draw()
        
        while gtk.events_pending():
            gtk.main_iteration()
