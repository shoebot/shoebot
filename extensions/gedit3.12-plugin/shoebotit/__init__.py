from distutils.spawn import find_executable as which
from gi.repository import Gtk, GLib, Gio, GObject, Gedit, Pango, PeasGtk
from gettext import gettext as _
from shoebotit import ide_utils, gtk3_utils

import base64
import os

WINDOW_ACTIONS = [
    (_("Run in Shoebot"), "run")
]

WINDOW_TOGGLES = [  # these are accompanied by vars e.g.   window.socket_server_enabled
    (_("Variable Window"), "var_window", True),
    (_("Socket Server"), "socket_server", False),
    (_("Live Coding"), "live_coding", False),
    (_("Full screen"), "full_screen", False)
]

WINDOW_ACCELS = [("run", "<Control>R")]

EXAMPLES=[]

class ShoebotPlugin(GObject.Object, Gedit.WindowActivatable, PeasGtk.Configurable):
    __gtype_name__ = "ShoebotPlugin"
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

        self.changed_handler_id = None
        self.idle_handler_id = None
        
        self.text = None
        self.live_text = None

        self.id_name = 'ShoebotPluginID'

        for _, name, default in WINDOW_TOGGLES:
            setattr(self, "%s_enabled" % name, default)
        
        self.bot = None

    def do_activate(self):
        self.add_output_widgets()
        self.add_window_actions()

    def _create_view(self, name="shoebot-output"):
        """
        Create the gtk.TextView inside a Gtk.ScrolledWindow
        :return: container, text_view
        """
        text_view = Gtk.TextView()
        text_view.set_editable(False)

        fontdesc = Pango.FontDescription("Monospace")
        text_view.modify_font(fontdesc)
        text_view.set_name(name)

        buff = text_view.get_buffer()
        buff.create_tag('error', foreground='red')

        container = Gtk.ScrolledWindow()
        container.add(text_view)
        container.show_all()
        return container, text_view

    def add_output_widgets(self):
        self.output_container, self.text = self._create_view("shoebot-output")
        self.live_container, self.live_text = self._create_view("shoebot-live")
        self.panel = self.window.get_bottom_panel()

        self.panel.add_titled(self.output_container, 'Shoebot', 'Shoebot')
        self.panel.add_titled(self.live_container, 'Shoebot Live', 'Shoebot Live')

    def add_window_actions(self):
        for rel_path in EXAMPLES:
            action = Gio.SimpleAction.new(
                "open_example__%s" % gtk3_utils.encode_relpath(rel_path),
                None)
        
            action.connect("activate", self.on_open_example)
            self.window.add_action(action)

        for _, name in WINDOW_ACTIONS:
            action_name = "on_%s" % name
            action = Gio.SimpleAction.new(name=action_name)
            action.connect("activate", getattr(self, action_name))
            self.window.add_action(action)

        for _, name, default in WINDOW_TOGGLES:
            action_name = "toggle_%s" % name
            action = Gio.SimpleAction.new(name=action_name)
            action = Gio.SimpleAction.new_stateful(
                action_name, 
                None, 
                GLib.Variant.new_boolean(default))
            action.connect("activate", getattr(self, action_name))
            self.window.add_action(action)

    def on_run(self, action, user_data):
        self.start_shoebot()

    def on_open_example(self, action, user_data):
        b64_path = action.get_name()[len('open_example__'):].encode("UTF-8")

        example_dir = ide_utils.get_example_dir()
        rel_path = base64.b64decode(b64_path).decode("UTF-8")
        path = os.path.join(example_dir, rel_path)

        drive, directory = os.path.splitdrive(os.path.abspath(os.path.normpath(path)))
        uri = "file://%s%s" % (drive, directory)
        gio_file = Gio.file_new_for_uri(uri)
        self.window.create_tab_from_location(
            gio_file,
            None,  # encoding
            0,
            0,     # column
            False, # Do not create an empty file
            True)  # Switch to the tab

    def start_shoebot(self):
        sbot_bin=gtk3_utils.sbot_executable()
        if not sbot_bin:
            textbuffer = self.text.get_buffer()
            textbuffer.set_text('Cannot find sbot in path.')
            while Gtk.events_pending():
               Gtk.main_iteration()
            return False
            
        if self.bot and self.bot.process.poll() == None:
            print('Sending quit.')
            self.bot.send_command("quit")

        # get the text buffer
        doc = self.window.get_active_document()
        if not doc:
            return

        title = '%s - Shoebot on gedit' % doc.get_short_name_for_display()
        cwd = os.path.dirname(doc.get_uri_for_display()) or None

        start, end = doc.get_bounds()
        source = doc.get_text(start, end, False)
        if not source:
            return False

        textbuffer = self.text.get_buffer()
        textbuffer.set_text('running shoebot at %s\n' % sbot_bin)

        while Gtk.events_pending():
           Gtk.main_iteration()

        self.disconnect_change_handler(doc)
        self.changed_handler_id = doc.connect("changed", self.doc_changed)

        self.bot = ide_utils.ShoebotProcess(
            source,
            self.socket_server_enabled,
            self.var_window_enabled,
            self.full_screen_enabled,
            title,
            cwd=cwd,
            sbot=sbot_bin)
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
        if self.live_coding_enabled and self.bot:
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
                    print('FIXME: %s' % str(e))
                else:
                    # Something else bad happened
                    raise

    def update_shoebot(self):
        if self.bot:
            textbuffer = self.text.get_buffer()
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
            self.text.scroll_to_iter(textbuffer.get_end_iter(), 0.0, True, 0.0, 0.0)

            textbuffer = self.live_text.get_buffer()
            for response in self.bot.get_command_responses():
                if response is None:
                    # sentinel value - clear the buffer
                    textbuffer.delete(textbuffer.get_start_iter(), textbuffer.get_end_iter())
                else:
                    cmd, status, info = response.cmd, response.status, response.info
                    if cmd == ide_utils.CMD_LOAD_BASE64:
                        if status == ide_utils.RESPONSE_CODE_OK:
                            textbuffer.delete(textbuffer.get_start_iter(), textbuffer.get_end_iter())
                            # TODO switch panels to 'Shoebot' if on 'Shoebot Live'
                        elif status == ide_utils.RESPONSE_REVERTED:
                            textbuffer.insert(textbuffer.get_end_iter(), '\n'.join(info).replace('\\n', '\n'))

            while Gtk.events_pending():
                Gtk.main_iteration()

        if self.bot:
            return self.bot.running
        else:
            return False
    
    def toggle_socket_server(self, action, user_data):
        action.set_state(GLib.Variant.new_boolean(not action.get_state()))
        self.socket_server_enabled = action.get_state().get_boolean()

    def toggle_var_window(self, action, user_data):
        action.set_state(GLib.Variant.new_boolean(not action.get_state()))
        self.var_window_enabled = action.get_state().get_boolean()

    def toggle_full_screen(self, action, user_data):
        action.set_state(GLib.Variant.new_boolean(not action.get_state()))
        self.full_screen_enabled = action.get_state().get_boolean()

    def toggle_live_coding(self, action, user_data):
        action.set_state(GLib.Variant.new_boolean(not action.get_state()))
        self.live_coding_enabled = action.get_state().get_boolean()
        panel = self.window.get_bottom_panel()
        if self.live_coding_enabled and self.bot:
            doc = self.window.get_active_document()
            source = self.get_source(doc)
            self.bot.live_source_load(source)

            panel.add_titled(self.live_container, 'Shoebot Live', 'Shoebot Live')
        else:
            panel.remove(self.live_container)

    def do_deactivate(self):
        self.panel.remove(self.live_container)
        self.panel.remove(self.output_container)

    def do_create_configure_widget(self):
        widget = gtk3_utils.ShoebotPreferences()    
        return widget


class ShoebotPluginMenu(GObject.Object, Gedit.AppActivatable):
    app = GObject.property(type=Gedit.App)

    def __init__(self):
        GObject.Object.__init__(self)
        self.shoebot_menu = None

    def do_activate(self):
        global _
        def mk_menu(text):
            global _
            menu = Gio.Menu.new()
            item = Gio.MenuItem.new_submenu(text, menu)

            examples_item, examples = gtk3_utils.mk_examples_menu(_("E_xamples"))
            if not EXAMPLES:
                EXAMPLES.extend(examples)
            menu.append_item(examples_item)

            for text, name in WINDOW_ACTIONS:
                menu.append(text, "win.on_%s" % name)
                
            for text, name, toggled in WINDOW_TOGGLES:
                action_name = "win.toggle_%s" % name
                menu.append(text, action_name)

            return item, menu
        
        base, menu = mk_menu(_("Shoebot"))

        for name, accel in WINDOW_ACCELS:
            self.app.add_accelerator(accel, "win.on_%s" % name, None)
        
        self.shoebot_menu = base
        self.tools_menu_ext = self.extend_menu("tools-section")
        self.tools_menu_ext.append_menu_item(base)

    def do_deactivate(self):
        pass
