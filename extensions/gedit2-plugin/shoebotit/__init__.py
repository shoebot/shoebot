from distutils.spawn import find_executable as which
from urllib.request import pathname2url

from gettext import gettext as _
from shoebotit import ide_utils, gtk3_utils

import gedit
import gtk
import pango
import os

if not which('sbot'):
    print('Shoebot executable not found.')


class ShoebotWindowHelper:
    def __init__(self, plugin, window):
        self.example_bots = {}

        self.window = window
        self.plugin = plugin
        self.insert_menu()

        self.id_name = 'ShoebotPluginID'

        self.use_socketserver = False
        self.show_varwindow = True
        self.use_fullscreen = False

        self.started = False

        for view in self.window.get_views():
            self.connect_view(view)

    def deactivate(self):
        self.remove_menu()
        self.window = None
        self.plugin = None
        self.action_group = None

    def insert_menu(self):
        manager = self.window.get_ui_manager()
        self.action_group = gtk.ActionGroup("ShoebotPluginActions")
        self.action_group.add_actions([
            ("Shoebot", None, _("Shoebot"), None, _("Shoebot"), None),
            ("ShoebotRun", None, _("Run in Shoebot"), '<control>R', _("Run in Shoebot"), self.on_run_activate),
            ])
        self.action_group.add_toggle_actions([
            ("ShoebotSocket", None, _("Enable Socket Server"), '<control><alt>S', _("Enable Socket Server"), self.toggle_socket_server, False),
            ("ShoebotVarWindow", None, _("Show Variables Window"), '<control><alt>V', _("Show Variables Window"), self.toggle_var_window, False),
            ("ShoebotFullscreen", None, _("Go Fullscreen"), '<control><alt>F', _("Go Fullscreen"), self.toggle_fullscreen, False),
            ])
        manager.insert_action_group(self.action_group, -1)
        self.ui_id = manager.add_ui_from_string(ui_str)

    def remove_menu(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self.ui_id)
        manager.remove_action_group(self.action_group)
        # Make sure the manager updates
        manager.ensure_update()

    def update_ui(self):
        self.action_group.set_sensitive(self.window.get_active_document() != None)
        # hack to make sure that views are connected
        # since activate() is not called on startup
        if not self.started and self.window.get_views():
            for view in self.window.get_views():
                self.connect_view(view)
            self.started = True

    def on_run_activate(self, action):
        self.start_shoebot()

    def start_shoebot(self):
        if not which('sbot'):
            textbuffer = self.output_widget.get_buffer()
            textbuffer.set_text('Cannot find sbot in path.')
            while Gtk.events_pending():
               Gtk.main_iteration()
            return False

        if self.bot and self.bot.process.poll() == None:
            print('Has a bot already')
            return False

        # get the text buffer
        doc = self.window.get_active_document()
        if not doc:
            return

        title = '%s - Shoebot on gedit' % doc.get_short_name_for_display()
        cwd = os.path.dirname(doc.get_uri_for_display()) or None

        start, end = doc.get_bounds()
        code = doc.get_text(start, end, False)
        if not code:
            return False

        textbuffer = self.output_widget.get_buffer()
        textbuffer.set_text('')
        while Gtk.events_pending():
           Gtk.main_iteration()

        self.bot = ide_utils.ShoebotProcess(code, self.use_socketserver, self.show_varwindow, self.use_fullscreen, title, cwd=cwd)

        GObject.idle_add(self.update_shoebot)

    def update_shoebot(self):
        if self.bot:
            textbuffer = self.output_widget.get_buffer()
            for stdout_line, stderr_line, running in self.bot.get_output():
                if stdout_line is not None:
                    textbuffer.insert(textbuffer.get_end_iter(), stdout_line)
                if stderr_line is not None:
                    textbuffer.insert(textbuffer.get_end_iter(), stderr_line)
            self.output_widget.scroll_to_iter(textbuffer.get_end_iter(), 0.0, True, 0.0, 0.0)
            while Gtk.events_pending():
                Gtk.main_iteration()

        return self.bot.running
    
    def toggle_socket_server(self, action):
        self.use_socketserver = action.get_active()

    def toggle_var_window(self, action):
        self.show_varwindow = action.get_active()

    def toggle_fullscreen(self, action):
        self.use_fullscreen = action.get_active()

    def connect_view(self, view):
        # taken from gedit-plugins-python-openuricontextmenu
        pass


class ShoebotPlugin(gedit.Plugin):
    def __init__(self):
        gedit.Plugin.__init__(self)
        self.instances = {}
        self.tempfiles = []

    def activate(self, window):
        self.instances[window] = ShoebotWindowHelper(self, window)

    def deactivate(self, window):
        self.instances[window].deactivate()
        del self.instances[window]
        for tfilename in self.tempfiles:
            os.remove(tfilename)

    def update_ui(self, window):
        self.instances[window].update_ui()


