import os
import gedit
import gtk
from gettext import gettext as _

try:
    # 0.2
    from shoebot import gtkui
    import shoebot
except ImportError:
    # 0.3
    from shoebot.gui import ShoebotWindow
    from shoebot import ShoebotError, ShoebotScriptError

ui_str = """
<ui>
  <menubar name="MenuBar">
    <menu name="ShoebotMenu" action="Shoebot">
      <placeholder name="ShoebotOps_1">
        <menuitem name="Run in Shoebot" action="ShoebotRun"/>
        <separator/>
        <menuitem name="Enable Socket Server" action="ShoebotSocket"/>
        <menuitem name="Show Variables Window" action="ShoebotVarWindow"/>
        <menuitem name="Go Fullscreen" action="ShoebotFullscreen"/>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""

class ShoebotWindowHelper:
    def __init__(self, plugin, window):
        self.window = window
        self.plugin = plugin
        self.insert_menu()
        self.shoebot_window = None

        self.use_socketserver = False
        self.use_varwindow = False
        self.use_fullscreen = False

    def deactivate(self):
        self.remove_menu()
        self.window = None
        self.plugin = None
        self.action_group = None
        del self.shoebot_window

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

    def on_run_activate(self, action):
        doc = self.window.get_active_document()
        if not doc:
            return
        start, end = doc.get_bounds()
        code = doc.get_text(start, end)
        try:
            self.shoebot_window = ShoebotWindow(code, 
                                                   self.use_socketserver, 7777, 
                                                   self.use_varwindow, 
                                                   self.use_fullscreen)
        except ShoebotError, NameError:
            import traceback            
            errmsg = traceback.format_exc(limit=1)
            err = "Error in Shoebot script:\n %s" % (errmsg)
            print err
    
    def toggle_socket_server(self, action):
        self.use_socketserver = action.get_active()
    def toggle_var_window(self, action):
        self.use_varwindow = action.get_active()
    def toggle_fullscreen(self, action):
        self.use_fullscreen = action.get_active()

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

