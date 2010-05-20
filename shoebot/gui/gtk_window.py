import gtk

from shoebot.gui import ShoebotWidget, VarWindow
from shoebot.core import DrawQueueSink

class ShoebotWindow(gtk.Window, DrawQueueSink):
    '''Create a GTK+ window that contains a ShoebotWidget'''

    # Draw in response to an expose-event
    __gsignals__ = { "expose-event": "override" }
    def __init__(self, botcontext, **kwargs):
        gtk.Window.__init__(self)
        DrawQueueSink.__init__(self, botcontext)

        sb_widget = ShoebotWidget(botcontext)

        title = kwargs['title']
        if title:
            self.set_title(title)
        self.connect("delete-event", gtk.main_quit)
        self.connect("destroy", self.do_window_close)

        sb_widget.show()
        self.add(sb_widget)

        #if show_vars:
        #    self.var_window = VarWindow(self, self.bot)
        self.present()

        while gtk.events_pending():
            gtk.main_iteration()

        self.sb_widget = sb_widget

    def create_rcontext(self, size, frame):
        '''
        Delegates to the ShoebotWidget
        '''
        return self.sb_widget.create_rcontext(size, frame)

    def rcontext_ready(self, size, frame, cairo_ctx):
        '''
        Delegates to the ShoebotWidget
        '''
        return self.sb_widget.rcontext_ready(size, frame, cairo_ctx)

    def do_window_close(self, widget):
        self.botcontext.quit = True
