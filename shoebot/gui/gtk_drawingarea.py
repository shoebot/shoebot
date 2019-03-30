import os
from math import radians

from pkg_resources import resource_filename, Requirement

from shoebot.core.backend import cairo, gi, driver
from shoebot.sbio.socket_server import SocketServer

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

pycairo = driver.cairo

ICON_FILE = resource_filename(Requirement.parse("shoebot"), "share/pixmaps/shoebot-ide.png")


class BackingStore:
    instance = None

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = pycairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)

    @property
    def dimensions(self):
        return self.width, self.height

    @classmethod
    def get_backingstore(cls, width, height):
        if cls.instance is None or (width, height) != cls.instance.dimensions:
            cls.instance = BackingStore(width, height)
        return cls.instance


class ShoebotWidget(Gtk.DrawingArea, SocketServer):
    '''
    Create a double buffered GTK+ widget on which we will draw using Cairo
    '''

    # Draw in response to an expose-event
    def __init__(self, scale_fit=True, input_device=None):
        Gtk.DrawingArea.__init__(self)
        self.connect("size_allocate", self.on_resize)
        self.connect("draw", self.draw)

        self.scale_fit = scale_fit
        self.input_device = input_device

        self.width, self.height = 1, 1
        self.bot_size = None
        self.frame = -1
        self.backing_store = BackingStore.get_backingstore(1, 1)

    def draw_default_image(self, cr):
        if os.path.isfile(ICON_FILE):
            icon = cairo.ImageSurface.create_from_png(ICON_FILE)
            cr.set_source_surface(icon)
            cr.paint()
        else:
            # A hint that shoebot is running in developer mode.
            # Can probably be removed once bug 212 is fixed.
            # https://github.com/shoebot/shoebot/issues/212
            cr.push_group()
            cr.translate(48, 48)
            cr.rotate(radians(45.0))
            cr.rectangle(-32, -32, 64, 64)
            cr.pop_group()
            cr.set_source_rgb(1, 1, 0)
            cr.fill()

    def on_resize(self, widget, dimensions):
        self.width = dimensions.width
        self.height = dimensions.height

    def scale_context(self, cr):
        """
        Scale context based on difference between bot size and widget
        """
        bot_width, bot_height = self.bot_size
        if self.width != bot_width or self.height != bot_height:
            # Scale up by largest dimension
            if self.width < self.height:
                scale_x = float(self.width) / float(bot_width)
                scale_y = scale_x
            elif self.width > self.height:
                scale_y = float(self.height) / float(bot_height)
                scale_x = scale_y
            else:
                scale_x = 1.0
                scale_y = 1.0
            cr.scale(scale_x, scale_y)
            self.input_device.scale_x = scale_y
            self.input_device.scale_y = scale_y

    def draw(self, widget, cr):
        '''
        Draw just the exposed part of the backing store, scaled to fit
        '''
        if self.bot_size is None:
            # No bot to draw yet.
            self.draw_default_image(cr)
            return

        cr = driver.ensure_pycairo_context(cr)

        cr.set_source_rgb(1, 1, 1)
        cr.paint()

        surface = self.backing_store.surface
        cr.set_source_surface(surface)

        cr.paint()

    def create_rcontext(self, size, frame):
        '''
        Creates a recording surface for the bot to draw on

        :param size: The width and height of bot
        '''
        self.frame = frame
        width, height = size
        meta_surface = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, (0, 0, width, height))

        ctx = cairo.Context(meta_surface)
        return ctx

    def do_drawing(self, size, frame, cairo_ctx):
        '''
        Update the backing store from a cairo context and
        schedule a redraw (expose event)

        :param size: width, height in pixels of bot
        :param frame: frame # thar was drawn
        :param cairo_ctx: cairo context the bot was drawn on
        '''
        if self.get_window() and not self.bot_size:
            # Get initial size for window
            self.set_size_request(*size)

        self.bot_size = size
        self.backing_store = BackingStore.get_backingstore(self.width, self.height)

        cr = pycairo.Context(self.backing_store.surface)
        if self.scale_fit:
            self.scale_context(cr)

        cairo_ctx = driver.ensure_pycairo_context(cairo_ctx)
        cr.set_source_surface(cairo_ctx.get_target())
        # Create the cairo context
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()

        self.queue_draw()

        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
