from distutils.spawn import find_executable as which
from gi.repository import Gtk, Gio, GObject, Gedit, Pango, PeasGtk
from gettext import gettext as _
from shoebotit import ide_utils, gtk3_utils

import os


class ShoebotWindowHelper(object):
    def __init__(self, plugin, window):
        self.example_bots = {}

        self.window = window
        self.changed_handler_id = None
        self.idle_handler_id = None
        panel = window.get_bottom_panel()
        self.output_widget = gtk3_utils.get_child_by_name(panel, "shoebot-output")
        self.live_output_widget = gtk3_utils.get_child_by_name(panel, "shoebot-live")

        self.plugin = plugin
        self.insert_menu()
        self.id_name = "ShoebotPluginID"

        self.use_socketserver = False
        self.show_varwindow = True
        self.use_fullscreen = False
        self.livecoding = False
        self.verbose_output = False  # TODO - no UI to change this currently

        self.started = False

        for view in self.window.get_views():
            self.connect_view(view)

        self.bot = None

    def deactivate(self):
        self.remove_menu()
        self.window = None
        self.plugin = None

    def insert_menu(self):
        examples_xml, example_actions, submenu_actions = gtk3_utils.examples_menu()
        ui_str = gtk3_utils.gedit3_menu(examples_xml)

        manager = self.window.get_ui_manager()
        self.action_group = Gtk.ActionGroup("ShoebotPluginActions")
        self.action_group.add_actions(
            [
                ("Shoebot", None, _("Shoe_bot"), None, _("Shoebot"), None),
                (
                    "ShoebotRun",
                    None,
                    _("Run in Shoebot"),
                    "<control>R",
                    _("Run in Shoebot"),
                    self.on_run_activate,
                ),
                ("ShoebotOpenExampleMenu", None, _("E_xamples"), None, None, None),
            ]
        )

        for action, label in example_actions:
            self.action_group.add_actions(
                [(action, None, (label), None, None, self.on_open_example)]
            )

        for action, label in submenu_actions:
            self.action_group.add_actions([(action, None, (label), None, None, None)])

        self.action_group.add_toggle_actions(
            [
                (
                    "ShoebotSocket",
                    None,
                    _("Enable Socket Server"),
                    "<control><alt>S",
                    _("Enable Socket Server"),
                    self.toggle_socket_server,
                    False,
                ),
                (
                    "ShoebotVarWindow",
                    None,
                    _("Show Variables Window"),
                    "<control><alt>V",
                    _("Show Variables Window"),
                    self.toggle_var_window,
                    False,
                ),
                (
                    "ShoebotFullscreen",
                    None,
                    _("Go Fullscreen"),
                    "<control><alt>F",
                    _("Go Fullscreen"),
                    self.toggle_fullscreen,
                    False,
                ),
                (
                    "ShoebotLive",
                    None,
                    _("Live Code"),
                    "<control><alt>C",
                    _("Live Code"),
                    self.toggle_livecoding,
                    False,
                ),
            ]
        )
        manager.insert_action_group(self.action_group)

        self.ui_id = manager.add_ui_from_string(ui_str)
        manager.ensure_update()

    def on_open_example(self, action):
        example_dir = ide_utils.get_example_dir()
        filename = os.path.join(
            example_dir, action.get_name()[len("ShoebotOpenExample") :].strip()
        )

        drive, directory = os.path.splitdrive(
            os.path.abspath(os.path.normpath(filename))
        )
        uri = "file:///%s%s" % (drive, directory)
        gio_file = Gio.file_new_for_uri(uri)
        self.window.create_tab_from_location(
            gio_file,
            None,  # encoding
            0,
            0,  # column
            False,  # Do not create an empty file
            True,
        )  # Switch to the tab

    def remove_menu(self):
        manager = self.window.get_ui_manager()
        manager.remove_action_group(self.action_group)
        for bot, ui_id in self.example_bots.items():
            manager.remove_ui(ui_id)
        manager.remove_ui(self.ui_id)

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
        sbot_bin = gtk3_utils.sbot_executable()
        if not sbot_bin:
            textbuffer = self.output_widget.get_buffer()
            textbuffer.set_text("Cannot find sbot in path.")
            while Gtk.events_pending():
                Gtk.main_iteration()
            return False

        if self.bot and self.bot.process.poll() == None:
            print("Sending quit.")
            self.bot.send_command("quit")

        # get the text buffer
        doc = self.window.get_active_document()
        if not doc:
            return

        title = "%s - Shoebot on gedit" % doc.get_short_name_for_display()
        cwd = os.path.dirname(doc.get_uri_for_display()) or None

        start, end = doc.get_bounds()
        source = doc.get_text(start, end, False)
        if not source:
            return False

        textbuffer = self.output_widget.get_buffer()
        textbuffer.set_text("running shoebot at %s\n" % sbot_bin)

        while Gtk.events_pending():
            Gtk.main_iteration()

        self.disconnect_change_handler(doc)
        self.changed_handler_id = doc.connect("changed", self.doc_changed)

        self.bot = ide_utils.ShoebotProcess(
            source,
            self.use_socketserver,
            self.show_varwindow,
            self.use_fullscreen,
            self.verbose_output,
            title,
            cwd=cwd,
            sbot=sbot_bin,
        )
        self.idle_handler_id = GObject.idle_add(self.update_shoebot)

    def disconnect_change_handler(self, doc):
        if self.changed_handler_id is not None:
            doc.disconnect(self.changed_handler_id)
            self.changed_handler_id = None

    def get_source(self, doc):
        """
        Grab contents of 'doc' and return it

        :param doc: The active document
        :return:
        """
        start_iter = doc.get_start_iter()
        end_iter = doc.get_end_iter()
        source = doc.get_text(start_iter, end_iter, False)
        return source

    def doc_changed(self, *args):
        if self.livecoding and self.bot:
            doc = self.window.get_active_document()
            source = self.get_source(doc)

            try:
                self.bot.live_source_load(source)
            except Exception:
                self.bot = None
                self.disconnect_change_handler(doc)
                raise
            except IOError as e:
                self.bot = None
                self.disconnect_change_handler()
                if e.errno == errno.EPIPE:
                    # EPIPE error
                    print("FIXME: %s" % str(e))
                else:
                    # Something else bad happened
                    raise

    def update_shoebot(self):
        if self.bot:
            textbuffer = self.output_widget.get_buffer()
            for stdout_line, stderr_line in self.bot.get_output():
                if stdout_line is not None:
                    textbuffer.insert(textbuffer.get_end_iter(), stdout_line)
                if stderr_line is not None:
                    # Use the 'error' tag so text is red
                    textbuffer.insert(textbuffer.get_end_iter(), stderr_line)
                    offset = textbuffer.get_char_count() - len(stderr_line)
                    start_iter = textbuffer.get_iter_at_offset(offset)
                    end_iter = textbuffer.get_end_iter()
                    textbuffer.apply_tag_by_name("error", start_iter, end_iter)
            self.output_widget.scroll_to_iter(
                textbuffer.get_end_iter(), 0.0, True, 0.0, 0.0
            )

            textbuffer = self.live_output_widget.get_buffer()
            for response in self.bot.get_command_responses():
                if response is None:
                    # sentinel value - clear the buffer
                    textbuffer.delete(
                        textbuffer.get_start_iter(), textbuffer.get_end_iter()
                    )
                else:
                    cmd, status, info = response.cmd, response.status, response.info
                    if cmd == ide_utils.CMD_LOAD_BASE64:
                        if status == ide_utils.RESPONSE_CODE_OK:
                            textbuffer.delete(
                                textbuffer.get_start_iter(), textbuffer.get_end_iter()
                            )
                            # TODO switch panels to 'Shoebot' if on 'Shoebot Live'
                        elif status == ide_utils.RESPONSE_REVERTED:
                            textbuffer.insert(
                                textbuffer.get_end_iter(),
                                "\n".join(info).replace("\\n", "\n"),
                            )

            while Gtk.events_pending():
                Gtk.main_iteration()

        if self.bot:
            return self.bot.running
        else:
            return False

    def toggle_socket_server(self, action):
        self.use_socketserver = action.get_active()

    def toggle_var_window(self, action):
        self.show_varwindow = action.get_active()

    def toggle_fullscreen(self, action):
        self.use_fullscreen = action.get_active()

    def toggle_livecoding(self, action):
        self.livecoding = action.get_active()
        panel = self.window.get_bottom_panel()
        if self.livecoding and self.bot:
            doc = self.window.get_active_document()
            source = self.get_source(doc)
            self.bot.live_source_load(source)

            icon = Gtk.Image()
            panel.add_item(
                self.live_output_widget, "Shoebot Live", "Shoebot Live", icon
            )
        else:
            panel.remove_item(self.live_output_widget)

    # Right-click menu items (for quicktorials)

    def connect_view(self, view):
        # taken from gedit-plugins-python-openuricontextmenu
        # handler_id = view.connect('populate-popup', self.on_view_populate_popup)
        # view.set_data(self.id_name, [handler_id])

        pass


class ShoebotPlugin(GObject.Object, Gedit.WindowActivatable, PeasGtk.Configurable):
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
        self.instances = {}

    def _create_view(self, name="shoebot-output"):
        """ Create the gtk.TextView used for shell output """
        view = Gtk.TextView()
        view.set_editable(False)

        fontdesc = Pango.FontDescription("Monospace")
        view.modify_font(fontdesc)
        view.set_name(name)

        buff = view.get_buffer()
        buff.create_tag("error", foreground="red")
        return view

    def do_activate(self):
        self.text = self._create_view("shoebot-output")
        self.live_text = self._create_view("shoebot-live")
        self.panel = self.window.get_bottom_panel()

        icon = Gtk.Image()
        icon.set_from_stock(Gtk.STOCK_EXECUTE, Gtk.IconSize.BUTTON)

        output_widget = Gtk.ScrolledWindow()
        output_widget.add(self.text)
        output_widget.show_all()

        self.panel.add_item(output_widget, "Shoebot", "Shoebot", icon)
        self.output_widget = output_widget

        live_output_widget = Gtk.ScrolledWindow()
        live_output_widget.add(self.live_text)
        live_output_widget.show_all()

        self.panel.add_item(live_output_widget, "Shoebot Live", "Shoebot Live", icon)
        self.live_output_widget = live_output_widget

        self.instances[self.window] = ShoebotWindowHelper(self, self.window)

    def do_deactivate(self):
        self.panel.remove_item(self.text)
        self.instances[self.window].deactivate()
        del self.instances[self.window]

        self.panel.remove_item(self.output_widget)

    def do_update_state(self):
        self.instances[self.window].update_ui()

    def do_create_configure_widget(self):
        widget = gtk3_utils.ShoebotPreferences()
        return widget
