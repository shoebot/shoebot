import os
import gedit
import gtk
import re
from gettext import gettext as _

try:
    from shoebot import sbot
    import shoebot
except ImportError:
    print "Failed Import"

# regex taken from openuricontextmenu.py and slightly changed
# to work with Python functions
RE_DELIM = re.compile(r'[\w#/\?:%@&\=\+\.\\~-]+', re.UNICODE|re.MULTILINE)

BASE_QUICKTORIAL_URL = "http://www.quicktorials.org/id/org.shoebot=en=0.3=%s"

# function name -> quicktorial id mapping
QUICKTORIAL_KEYWORDS = {
        'rect': 'rect01',
        'oval': 'ellipse01',
        'var': 'var01'
        }


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
        self.id_name = 'ShoebotPluginID'

        self.use_socketserver = False
        self.use_varwindow = False
        self.use_fullscreen = False

        self.started = False

        for view in self.window.get_views():
            self.connect_view(view)

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
        # hack to make sure that views are connected
        # since activate() is not called on startup
        if not self.started and self.window.get_views():
            for view in self.window.get_views():
                self.connect_view(view)
            self.started = True

    def on_run_activate(self, action):
        # get the text buffer
        doc = self.window.get_active_document()
        if not doc:
            return
        start, end = doc.get_bounds()
        code = doc.get_text(start, end)
        if not code:
            return False
        # scraped if window_is_open and just render the stuff right there
        try:
          self.shoebot_window = sbot.run(code,
                                        iterations = None,
                                        window = True,
                                        title = doc.get_short_name_for_display() + ' - Shoebot',
                                        server = self.use_socketserver,
                                        show_vars = self.use_varwindow)
                                        # no more fullscreen for you!
                                        ##close_window = True)
        #except Error, NameError:
        except:
            import traceback 
            errmsg = traceback.format_exc(limit=1)
            err = "Error in Shoebot script:\n %s" % (errmsg)
            # TODO: This traceback should be sent over to a
            # log window at the bottom of Gedit
            print err
    
    def toggle_socket_server(self, action):
        self.use_socketserver = action.get_active()
    def toggle_var_window(self, action):
        self.use_varwindow = action.get_active()
    def toggle_fullscreen(self, action):
        #no full screen for you!
        self.use_fullscreen = False
        #self.use_fullscreen = action.get_active()
        
    # Right-click menu items (for quicktorials)

    def connect_view(self, view):
        # taken from gedit-plugins-python-openuricontextmenu
        handler_id = view.connect('populate-popup', self.on_view_populate_popup)
        view.set_data(self.id_name, [handler_id])

    def on_view_populate_popup(self, view, menu):
        # taken from gedit-plugins-python-openuricontextmenu
        doc = view.get_buffer()
        win = view.get_window(gtk.TEXT_WINDOW_TEXT)
        x, y, mod = win.get_pointer()
        x, y = view.window_to_buffer_coords(gtk.TEXT_WINDOW_TEXT, x, y) 

        # first try at pointer location
        insert = view.get_iter_at_location(x, y)

        # second try at cursor
        if insert == None:
            insert = doc.get_iter_at_mark(doc.get_insert())

        while insert.forward_char():
            if not RE_DELIM.match(insert.get_char()):
                break

        start = insert.copy()
        while start.backward_char():
            if not RE_DELIM.match(start.get_char()):
                start.forward_char()
                break

        word = unicode(doc.get_text(start, insert))

        if len(word) == 0:
            return True

        word = self.validate_word(word)
        if not word:
            return True

        open_quicktorial_item = gtk.ImageMenuItem(_("Know more about '%s'") % (word))
        open_quicktorial_item.set_image(gtk.image_new_from_stock(gtk.STOCK_JUMP_TO, gtk.ICON_SIZE_MENU))
        open_quicktorial_item.connect('activate', self.on_open_quicktorial, word)
        open_quicktorial_item.show()

        separator = gtk.SeparatorMenuItem()
        separator.show()

        menu.prepend(separator)
        menu.prepend(open_quicktorial_item)

    def validate_word(self, word):
        if word in QUICKTORIAL_KEYWORDS:
            return word
        return None

    def on_open_quicktorial(self, menu_item, word):
        self.open_quicktorial(word)
        return True

    def open_quicktorial(self, word):
        import webbrowser
        q_id = QUICKTORIAL_KEYWORDS[word]
        url = BASE_QUICKTORIAL_URL % q_id
        webbrowser.open(url)

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


