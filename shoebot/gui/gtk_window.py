import sys
import gtk

from shoebot.gui import ShoebotWidget, VarWindow, SocketServerMixin
from shoebot.core import DrawQueueSink
from gtk_input_device import GtkInputDeviceMixin

import locale
import gettext

APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
#gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext

class ShoebotWindow(gtk.Window, GtkInputDeviceMixin, DrawQueueSink, SocketServerMixin):
    '''Create a GTK+ window that contains a ShoebotWidget'''

    # Draw in response to an expose-event
    __gsignals__ = { "expose-event": "override" }
    def __init__(self, title = None, show_vars = False, menu_enabled = True, server=False, serverport=7777, go_fullscreen=False):
        gtk.Window.__init__(self)
        DrawQueueSink.__init__(self)
        GtkInputDeviceMixin.__init__(self)

        self.menu_enabled = menu_enabled
        self.has_server = server
        self.serverport = serverport
        self.show_vars = show_vars
        self.var_window = None

        sb_widget = ShoebotWidget()

        if title:
            self.set_title(title)
        self.connect("delete-event", gtk.main_quit)
        self.connect("destroy", self.do_window_close)

        self.sb_widget = sb_widget
        self.attach_gtk(self)

        self.uimanager = gtk.UIManager()
        accelgroup = self.uimanager.get_accel_group()
        self.add_accel_group(accelgroup)

        actiongroup = gtk.ActionGroup('Canvas')

        actiongroup.add_actions([('Save as', None, _('_Save as')),
                                 ('svg', 'Save as SVG', _('Save as _SVG'), "<Control>1", None, self.snapshot_svg),
                                 ('pdf', 'Save as PDF', _('Save as _PDF'), "<Control>2", None, self.snapshot_pdf),
                                 ('ps', 'Save as PS', _('Save as P_S'), "<Control>3", None, self.snapshot_ps),
                                 ('png', 'Save as PNG', _('Save as P_NG'), "<Control>4", None, self.snapshot_png),
                                 ('fullscreen', 'Go fullscreen', _('_Go fullscreen'), "<Control>5", None, self.do_fullscreen),
                                 ('unfullscreen', 'Exit fullscreen', _('_Exit fullscreen'), "<Control>6", None, self.do_unfullscreen),
                                 ('close', 'Close window', _('_Close Window'), "<Control>w", None, self.do_window_close)
                                ])

        menuxml = '''
        <popup action="Save as">
            <menuitem action="svg"/>
            <menuitem action="ps"/>
            <menuitem action="pdf"/>
            <menuitem action="png"/>
            <separator/>
            <menuitem action="fullscreen"/>
            <menuitem action="unfullscreen"/>
            <separator/>
            <menuitem action="close"/>
        </popup>
        '''

        self.uimanager.insert_action_group(actiongroup, 0)
        self.uimanager.add_ui_from_string(menuxml)

        sb_widget.show()
        self.add(sb_widget)

        self.present()

        while gtk.events_pending():
            gtk.main_iteration()
        if server:
            self.server('', self.serverport)


    def gtk_mouse_button_down(self, widget, event):
        ''' Handle right mouse button clicks '''
        if self.menu_enabled and event.button == 3:
            menu = self.uimanager.get_widget('/Save as')
            menu.popup(None, None, None, event.button, event.time)
        else:
            super(ShoebotWindow, self).gtk_mouse_button_down(widget, event)

    def create_rcontext(self, size, frame):
        ''' Delegates to the ShoebotWidget  '''
        return self.sb_widget.create_rcontext(size, frame)

    def rcontext_ready(self, size, frame, cairo_ctx):
        ''' Delegates to the ShoebotWidget '''
        ## A bit hacky... but makes sure bot has executed once:
        if self.show_vars and self.var_window is None:
            self.var_window = VarWindow(self, self.bot)

        return self.sb_widget.rcontext_ready(size, frame, cairo_ctx)

    def snapshot_svg(self, widget):
        bot = self.bot
        script = bot._namespace['__file__']
        if script:
            filename = os.path.splitext(script)[0] + '.svg'
        else:
            filename = 'output.svg'
        print filename
        ##self.bot.snapshot(self,filename=None, surface=None, defer=False, autonumber=bot.iterations > 1):
        ### Should save at end of frame
        print 'TODO'

    def snapshot_ps(self, widget):
        print 'TODO'

    def snapshot_pdf(self, widget):
        print 'TODO'

    def snapshot_png(self, widget):
        print 'TODO'

    def do_fullscreen(self, widget):
        self.fullscreen()
        # next lines seem to be needed for window switching really to
        # fullscreen mode before reading it's size values
        while gtk.events_pending():
            gtk.main_iteration(block=False)
        # we pass informations on full-screen size to bot
        #self.bot._screen_width = self.get_allocation().width
        #self.bot._screen_height = self.get_allocation().height
        self.bot._screen_width = gtk.gdk.screen_width()
        self.bot._screen_height = gtk.gdk.screen_height()
        self.bot._screen_ratio = self.bot.screen_width / self.bot.screen_height

    def do_unfullscreen(self, widget):
        self.unfullscreen()
        self.bot._screen_ratio = None

    def do_window_close(self, widget):
        self.bot._quit = True

        if self.has_server:
            self.sock.close()
        if self.var_window is not None:
            self.var_window.window.destroy()
            self.var_window = None

        self.destroy()

    def finish(self):
        if not self.bot._quit:
            gtk.main()
