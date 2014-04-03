import os
import sys
import gtk

from collections import deque
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
    def __init__(self, title = None, show_vars = False, menu_enabled = True, server=False, port=7777, fullscreen=False):
        gtk.Window.__init__(self)
        DrawQueueSink.__init__(self)
        GtkInputDeviceMixin.__init__(self)

        self.menu_enabled = menu_enabled
        self.has_server = server
        self.serverport = port
        self.show_vars = show_vars
        self.var_window = None
        self.is_fullscreen = False

        sb_widget = ShoebotWidget(input_device=self)

        if title:
            self.set_title(title)
        if fullscreen:
            self.is_fullscreen = True
            self.fullscreen()
        self.connect("delete-event", self.do_window_close)
        #self.connect("destroy", )

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
                                 ('close', 'Close window', _('_Close Window'), "<Control>w", None, self.do_window_close)
                                ])

        actiongroup.add_toggle_actions([('vars', 'Variables Window', _('Va_riables Window'), "<Control>r", None, self.do_toggle_variables, self.show_vars),
                                        ('fullscreen', 'Fullscreen', _('_Fullscreen'), "<Control>f", None, self.do_toggle_fullscreen, False)])





        menuxml = '''
        <popup action="Save as">
            <menuitem action="vars"/>
            <menuitem action="fullscreen"/>
            <separator/>
            <menuitem action="svg"/>
            <menuitem action="ps"/>
            <menuitem action="pdf"/>
            <menuitem action="png"/>
            <separator/>
            <separator/>
            <menuitem action="close"/>
        </popup>
        '''

        self.uimanager.insert_action_group(actiongroup, 0)
        self.uimanager.add_ui_from_string(menuxml)

        sb_widget.show()
        self.add(sb_widget)

        self.present()

        self.scheduled_snapshots = deque()

        while gtk.events_pending():
            gtk.main_iteration()
        if server:
            self.server('', self.serverport)

        self.window_open = True


    def gtk_mouse_button_down(self, widget, event):
        ''' Handle right mouse button clicks '''
        if self.menu_enabled and event.button == 3:
            menu = self.uimanager.get_widget('/Save as')
            menu.popup(None, None, None, event.button, event.time)
        else:
            super(ShoebotWindow, self).gtk_mouse_button_down(widget, event)

    def create_rcontext(self, size, frame):
        ''' Delegates to the ShoebotWidget  '''

        ### Any snapshots that need to be taken
        for snapshot_func in self.scheduled_snapshots:
            snapshot_func()
        else:
            self.scheduled_snapshots = deque()

        return self.sb_widget.create_rcontext(size, frame)

    def rendering_finished(self, size, frame, cairo_ctx):
        ''' Delegates to the ShoebotWidget '''
        # A bit hacky... only show the variable window once bot has
        # executed once and there are some variables.
        if self.show_vars:
            self.show_variables_window()
        else:
            self.hide_variables_window()

        return self.sb_widget.rendering_finished(size, frame, cairo_ctx)

    def schedule_snapshot(self, format):
        '''
        Since the right click comes in after things have been rendered
        it's easiest to schedule snapshots for the next render.

        (There is only a bitmap copy of the screen available at this
         point...)
        '''
        self.scheduled_snapshots.append(lambda: self.do_snapshot(format))

    def show_variables_window(self):
        '''
        If bot has variables and var window not visible then create it
        '''
        if self.var_window is None and self.bot._vars:
            self.var_window = VarWindow(self, self.bot, '%s variables' % (self.title or 'Shoebot'))

    def hide_variables_window(self):
        '''
        Hide the var window
        '''
        if self.var_window is not None:
            self.var_window.window.destroy()
            self.var_window = None

    def var_changed(self, name, value):
        self.bot._namespace[name] = value
        if self.var_window:
            return self.var_window.update_var(name, value)


    def do_snapshot(self, format):
        bot = self.bot
        script = bot._namespace['__file__']
        if script:
            filename = os.path.splitext(script)[0] + '.' + format
        else:
            filename = 'output.' + format
        self.bot._canvas.user_snapshot(filename)

    def snapshot_svg(self, widget):
        self.schedule_snapshot('svg')

    def snapshot_ps(self, widget):
        self.schedule_snapshot('ps')

    def snapshot_pdf(self, widget):
        self.schedule_snapshot('pdf')

    def snapshot_png(self, widget):
        self.schedule_snapshot('png')

    def do_fullscreen(self, widget):
        self.fullscreen()
        # next lines seem to be needed for window switching really to
        # fullscreen mode before reading it's size values
        while gtk.events_pending():
            gtk.main_iteration(block=False)
        # we pass informations on full-screen size to bot
        self.bot._screen_width = gtk.gdk.screen_width()
        self.bot._screen_height = gtk.gdk.screen_height()
        self.bot._screen_ratio = self.bot._screen_width / self.bot._screen_height

    def do_unfullscreen(self, widget):
        self.unfullscreen()
        self.bot._screen_ratio = None

    def do_window_close(self, widget,data=None):
        self.bot._quit = True

        if self.has_server:
            self.sock.close()

        self.hide_variables_window()

        self.destroy()
        self.window_open = False

    def do_toggle_fullscreen(self, action):
        self.is_fullscreen = action.get_active()
        if self.is_fullscreen:
            self.fullscreen()
        else:
            self.unfullscreen()
                

    def do_toggle_variables(self, action):
        self.show_vars = action.get_active()
        if self.show_vars:
            self.show_variables_window()
        else:
            self.hide_variables_window()



    def finish(self):
        while self.bot._quit == False and self.window_open == True:
            gtk.main_iteration()
            ### Any snapshots that need to be taken
            for snapshot_func in self.scheduled_snapshots:
                snapshot_func()
            else:
                self.scheduled_snapshots = deque()

