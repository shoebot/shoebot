#!/usr/bin/env python3
import argparse
import colorsys
import errno
import gettext
import locale
import os
import sys

import shoebot

from shoebot.data import ShoebotError
from shoebot.core.backend import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
gi.require_version("GtkSource", "3.0")

from gi.repository import Gdk, GLib, GObject, Gtk, GtkSource, Pango

DEBUG = os.environ.get("SHOEBOT_DEBUG_IDE", "0").lower() in ["1", "yes", "true"]

APP = "shoebot"
LOCALE_DIR = sys.prefix + "/share/shoebot/locale"

SEARCH_BACKWARD = -1
SEARCH_FORWARD = 1

locale.setlocale(locale.LC_ALL, "")
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

ICON_FILE = f"{sys.prefix}/shoebot/icon.png"

GTK_WRAP_MODES = {
    "WrapWords": Gtk.WrapMode.WORD,
    "WrapChars": Gtk.WrapMode.CHAR,
    "WrapNone": Gtk.WrapMode.NONE,
}


def hue_to_rgb(hue):
    if hue > 1.0:
        raise ValueError("Hue cannot be > 1.0")

    return colorsys.hsv_to_rgb(hue, 1.0, 1.0)


class SourceBuffer(GtkSource.Buffer):
    N_COLORS = 16
    PANGO_SCALE = 1024

    def __init__(self, filename=None):
        GObject.GObject.__init__(self)

        self.refcount = 0
        if filename is None:
            self.filename = ShoebotIDE.get_next_untitled_filename()
        else:
            self.open_file(filename)
            self.filename = filename

        self.color_tags = [self.create_tag() for i in range(self.N_COLORS)]
        self.color_cycle_timeout_id = 0
        self.start_hue = 0.0

        # self.invisible_tag = self.create_tag(None, invisible=True)
        self.not_editable_tag = self.create_tag(editable=False, foreground="purple")
        self.found_text_tag = self.create_tag(foreground="red")

        tabs = Pango.TabArray.new(4, True)
        tabs.set_tab(0, Pango.TabAlign.LEFT, 10)
        tabs.set_tab(1, Pango.TabAlign.LEFT, 30)
        tabs.set_tab(2, Pango.TabAlign.LEFT, 60)
        tabs.set_tab(3, Pango.TabAlign.LEFT, 120)
        self.custom_tabs_tag = self.create_tag(tabs=tabs, foreground="green")

    def pretty_name(self):
        return os.path.basename(self.filename)

    def search(self, text, view, direction=SEARCH_FORWARD):
        if not text:
            return
        # remove tag from whole buffer
        start, end = self.get_bounds()
        self.remove_tag(self.found_text_tag, start, end)

        it = self.get_iter_at_mark(self.get_insert())

        total_matches = 0
        while True:
            if direction == SEARCH_FORWARD:
                match = it.forward_search(text, Gtk.TextSearchFlags.TEXT_ONLY)
            else:
                match = it.backward_search(text, Gtk.TextSearchFlags.TEXT_ONLY)
            if not match:
                break
            match_start, match_end = match
            total_matches += 1
            self.apply_tag(self.found_text_tag, match_start, match_end)
            it = match_end

        dialog = Gtk.MessageDialog(
            view,
            Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK,
            _("%d strings found and marked in red") % total_matches,
        )
        dialog.connect("response", lambda x, y: dialog.destroy())
        dialog.show()

    def ref(self):
        self.refcount += 1

    def unref(self):
        self.refcount -= 1
        if self.refcount == 0:
            self.set_colors(False)
            del self

    def color_cycle_timeout(self):
        self.cycle_colors()
        return True

    def set_colors(self, enabled):
        hue = 0.0

        if enabled and self.color_cycle_timeout_id == 0:
            self.color_cycle_timeout_id = GLib.timeout_add(
                200, self.color_cycle_timeout
            )
        elif not enabled and self.color_cycle_timeout_id:
            GLib.source_remove(self.color_cycle_timeout_id)
            self.color_cycle_timeout_id = 0

        for tag in self.color_tags:
            if enabled:
                color = Gdk.RGBA(*hue_to_rgb(hue))
                tag.set_property("foreground_rgba", color)
            else:
                tag.set_property("foreground_set", False)
            hue += 1.0 / SourceBuffer.N_COLORS

    def cycle_colors(self):
        hue = self.start_hue

        for tag in self.color_tags:
            color = Gdk.Color(*hue_to_rgb(hue))
            tag.set_property("foreground_gdk", color)

            hue += 1.0 / SourceBuffer.N_COLORS
            if hue > 1.0:
                hue = 0.0

        self.start_hue += 1.0 / SourceBuffer.N_COLORS
        if self.start_hue > 1.0:
            self.start_hue = 0.0

    def tag_event_handler(self, tag, widget, event, it):
        char_index = it.get_offset()
        tag_name = tag.get_property("name")
        if event.type == Gdk.MOTION_NOTIFY:
            print(f"Motion event at char {char_index} tag `{tag_name}'\n")
        elif event.type == Gdk.EventType.BUTTON_PRESS:
            print(f"Button press at char {char_index} tag `{tag_name}'\n")
        elif event.type == Gdk.EventType.TwoButtonPress:
            print(f"Double click at char {char_index} tag `{tag_name}'\n")
        elif event.type == Gdk.EventType.TRIPLE_BUTTON_PRESS:
            print(f"Triple click at char {char_index} tag `{tag_name}'\n")
        elif event.type == Gdk.BUTTON_RELEASE:
            print(f"Button release at char {char_index} tag `{tag_name}'\n")
        elif event.type == Gdk.KEY_PRESS or event.type == Gdk.KEY_RELEASE:
            print(f"Key event at char {char_index} tag `{tag_name}'\n")
        return False

    def open_file(self, filename):
        with open(filename, "r") as f:
            content = f.read()
            self.set_text(content)
            self.set_modified(False)
            self.filename = filename


class ShoebotFileChooserDialog(Gtk.FileChooserDialog):
    CWD = None

    def __init__(self, *args, **kwargs):
        super(ShoebotFileChooserDialog, self).__init__(*args, **kwargs)

        # set some defaults
        self.set_default_response(Gtk.ResponseType.OK)
        self.set_property("do-overwrite-confirmation", True)

        # set the working directory if available
        if ShoebotFileChooserDialog.CWD is not None:
            self.set_current_folder(ShoebotFileChooserDialog.CWD)

    def run(self):
        response = super(ShoebotFileChooserDialog, self).run()

        # get the working directory if the user clicked accepted the action
        if response == Gtk.ResponseType.ACCEPT:
            ShoebotFileChooserDialog.CWD = self.get_current_folder()

        return response


class ConsoleWindow:
    def __init__(self):
        # we define a scrollable window with automatic behavior for scrolling bars
        self.text_window = Gtk.ScrolledWindow()
        self.text_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.text_area = Gtk.TextView()
        self.text_area.set_editable(False)
        self.text_area.set_wrap_mode(Gtk.WrapMode.WORD)
        self.text_area.connect("size-allocate", self.on_contents_changed)
        self.text_window.add(self.text_area)
        # here we set default values for background and text of console window
        self.text_area.modify_base(Gtk.StateType.NORMAL, Gdk.color_parse("dark grey"))
        self.text_area.modify_text(Gtk.StateType.NORMAL, Gdk.color_parse("red"))
        # then we define some text tag for defining colors for system messages and stdout
        self.tag_table = self.text_buffer.get_tag_table()

        self.stdout_tag = self.text_buffer.create_tag(
            "stdout", foreground="black", weight=600, size_points=9
        )
        self.system_message_tag = self.text_buffer.create_tag(
            "system", foreground="darkgrey"
        )
        self.text_area.modify_font(Pango.FontDescription("monospace 9"))

    def write(self, message, output=None, system=None):
        if not output:
            # no tags set for stderr messages, color will be the one set for TextView
            self.text_buffer.insert_at_cursor(message)
        elif system:
            # if output and system values are set, text is treated as a system message
            # and system tag is used
            it = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
            self.text_buffer.insert_with_tags(it, message, self.system_message_tag)
        else:
            # if only output value is set, tag used will be stdout
            it = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
            self.text_buffer.insert_with_tags(it, message, self.stdout_tag)

        while Gtk.events_pending():
            # Refresh the Window
            Gtk.main_iteration()

    def clear(self):
        self.text_buffer.set_text("")

    def on_contents_changed(self, widget, event):
        # scroll to bottom when there's new text
        # https://stackoverflow.com/questions/5218948/how-to-auto-scroll-a-gtk-scrolledwindow
        adj = self.text_window.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())

    @property
    def text_buffer(self):
        return self.text_area.get_buffer()


class StdoutFilter(object):
    def __init__(self, parent):
        self.parent = parent

    def write(self, data):
        message = data
        self.parent.write(message, True)

    def flush(self):
        pass


UI_INFO = """
<ui>
  <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menuitem action='FileNew' />
      <menuitem action='FileOpen' />
      <menuitem action='FileSave' />
      <menuitem action='FileSaveAs' />
      <separator />
      <menuitem action='FileClose' />
      <menuitem action='FileQuit' />
    </menu>
    <menu action='EditMenu'>
      <menuitem action='EditUndo' />
      <menuitem action='EditRedo' />
      <separator />
      <menuitem action='EditFind' />
      <separator />
      <menuitem action='ClearConsole' />
    </menu>
    <menu action='RunMenu'>
      <menuitem action='Run' />
      <separator />
      <menuitem action='VarWindow' />
      <menuitem action='FullScreen' />
      <menuitem action='SocketServer' />
    </menu>
    <menu action='SettingsMenu'>
      <menuitem action='WrapNone' />
      <menuitem action='WrapWords' />
      <menuitem action='WrapChars' />
      <separator />
      <menuitem action='ThemeLight' />
      <menuitem action='ThemeDark' />
    </menu>
    <menu action='HelpMenu'>
      <menuitem action='HelpAbout' />
    </menu>
  </menubar>
</ui>
"""


class ShoebotEditorWindow(Gtk.Window):
    FONT = None

    def __init__(self, filename=None):
        GObject.GObject.__init__(self)
        ShoebotIDE.add_editor_window(self)

        source_buffer = SourceBuffer(filename)
        source_buffer.ref()

        self.connect("delete_event", self.on_close_window)

        action_group = Gtk.ActionGroup("menubar_actions")
        action_group.add_actions(
            [
                ("FileMenu", None, _("_File")),
                (
                    "FileNew",
                    Gtk.STOCK_NEW,
                    _("_New"),
                    "<control>N",
                    None,
                    self.on_new_file,
                ),
                (
                    "FileOpen",
                    Gtk.STOCK_OPEN,
                    _("_Open"),
                    "<control>O",
                    None,
                    self.on_open_file,
                ),
                (
                    "FileSave",
                    Gtk.STOCK_SAVE,
                    _("_Save"),
                    "<control>S",
                    None,
                    self.on_save_file,
                ),
                (
                    "FileSaveAs",
                    Gtk.STOCK_SAVE_AS,
                    _("Save _As"),
                    "<control><alt>S",
                    None,
                    self.on_save_file_as,
                ),
                (
                    "FileClose",
                    Gtk.STOCK_CLOSE,
                    _("_Close"),
                    "<control>W",
                    None,
                    self.on_close_file,
                ),
                (
                    "FileQuit",
                    Gtk.STOCK_QUIT,
                    _("_Quit"),
                    "<control>Q",
                    None,
                    self.on_quit,
                ),
            ]
        )

        action_group.add_actions(
            [
                ("EditMenu", None, _("_Edit")),
                (
                    "EditUndo",
                    Gtk.STOCK_UNDO,
                    _("_Undo"),
                    "<control>Z",
                    None,
                    self.on_undo,
                ),
                (
                    "EditRedo",
                    Gtk.STOCK_REDO,
                    _("_Redo"),
                    "<control><shift>Z",
                    None,
                    self.on_redo,
                ),
                (
                    "EditFind",
                    Gtk.STOCK_FIND,
                    _("_Find"),
                    "<control>F",
                    None,
                    self.on_find,
                ),
                (
                    "ClearConsole",
                    Gtk.STOCK_CLEAR,
                    _("_Clear console"),
                    "<control><shift>C",
                    None,
                    self.on_clear_console,
                ),
            ]
        )

        action_group.add_action(Gtk.Action("SettingsMenu", _("_Settings"), None, None))
        action_group.add_radio_actions(
            [
                ("WrapNone", None, _("Wrap None"), None, None, Gtk.WrapMode.NONE),
                ("WrapWords", None, _("Wrap Words"), None, None, Gtk.WrapMode.WORD),
                ("WrapChars", None, _("Wrap Chars"), None, None, Gtk.WrapMode.CHAR),
            ],
            1,
            self.on_wrap_changed,
        )
        action_group.add_radio_actions(
            [
                ("ThemeLight", None, _("Light Theme"), None, None, True),
                ("ThemeDark", None, _("Dark Theme"), None, None, False),
            ],
            0 if ShoebotIDE.dark_theme else 1,
            self.on_theme_changed,
        )

        action_group.add_actions(
            [
                ("RunMenu", None, _("_Run")),
                (
                    _("Run"),
                    Gtk.STOCK_MEDIA_PLAY,
                    "_Run Script",
                    "<control>R",
                    None,
                    self.on_run_script,
                ),
            ]
        )
        variable_window_action = Gtk.ToggleAction(
            "VarWindow", _("Show variables window"), None, None
        )
        variable_window_action.connect("toggled", self.on_varwindow_changed)
        action_group.add_action(variable_window_action)
        full_screen_action = Gtk.ToggleAction(
            "FullScreen", _("Full screen"), None, None
        )
        full_screen_action.connect("toggled", self.on_fullscreen_changed)
        action_group.add_action(full_screen_action)
        socket_server_action = Gtk.ToggleAction(
            "SocketServer", _("Run socket server"), None, None
        )
        socket_server_action.connect("toggled", self.on_socketserver_changed)
        action_group.add_action(socket_server_action)

        action_group.add_actions(
            [
                ("HelpMenu", None, _("_Help")),
                ("HelpAbout", Gtk.STOCK_INFO, _("_About"), None, None, self.on_about),
            ]
        )

        ui_manager = Gtk.UIManager()
        # Throws exception if something went wrong
        ui_manager.add_ui_from_string(UI_INFO)
        # Add the accelerator group to the toplevel window
        accel_group = ui_manager.get_accel_group()
        self.add_accel_group(accel_group)
        # Add menu actions
        ui_manager.insert_action_group(action_group)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        menu_bar = ui_manager.get_widget("/MenuBar")
        box.pack_start(menu_bar, False, False, 0)

        hpaned = Gtk.HPaned()
        vbox = Gtk.VBox(False, 0)
        hpaned.add1(vbox)
        box.pack_start(hpaned, True, True, 0)

        self.add(box)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.source_view = GtkSource.View.new_with_buffer(source_buffer)
        self.source_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.source_view.set_show_line_numbers(True)

        # Configure source view for editing python:
        self.source_view.set_auto_indent(True)
        self.source_view.set_insert_spaces_instead_of_tabs(True)
        self.source_view.set_tab_width(4)
        self.source_view.set_indent_width(4)
        # self.source_view.connect("expose_event", self.tab_stops_expose)

        self.toggle_dark_theme(dark=ShoebotIDE.dark_theme)

        self.bhid = source_buffer.connect("mark_set", self.cursor_set_callback)

        if ShoebotEditorWindow.FONT is None:
            # Get font or fallback
            context = self.source_view.get_pango_context()
            fonts = context.list_families()
            for font in fonts:
                if font.get_name() == "Bitstream Vera Sans Mono":
                    ShoebotEditorWindow.FONT = "Bitstream Vera Sans Mono 10"
                    break
            else:
                print("Bitstream Vera Font not found.")
                print("Download and install it from here")
                print("http://ftp.gnome.org/pub/GNOME/sources/ttf-bitstream-vera/1.10/")
                ShoebotEditorWindow.FONT = "Mono 10"

            self.source_view.modify_font(
                Pango.FontDescription(ShoebotEditorWindow.FONT)
            )

        vbox.pack_start(scrolled_window, True, True, 0)
        scrolled_window.add(self.source_view)

        # this creates a console error and output window besides script window
        self.console_error = ConsoleWindow()
        # we create an instance for stdout filter
        self.stdout_filter = StdoutFilter(self.console_error)
        # we redirect stderr
        if not DEBUG:
            sys.stderr = self.console_error
            # stdout is redirected too, but through the filter in order to get different color for text
            sys.stdout = self.stdout_filter
            # error-console window is added to container as second child
        hpaned.add2(self.console_error.text_window)
        hpaned.set_position(450)
        # message displayed in console-error window at start, the double true values passed makes it render with system message tag
        self.console_error.write(
            _(
                "This is the console window.\n\nScript output and error messages are shown here.\n\nYou can clear the window with the 'Edit - Clear console' option or pressing Ctrl-Shift-C.\n\n"
            ),
            True,
            True,
        )

        self.set_default_size(800, 500)
        self.source_view.grab_focus()

        self.update_window_title()
        self.init_menus()

        self.shoebot_window = None

        # option toggles
        self.use_varwindow = False
        self.use_socketserver = False
        self.go_fullscreen = False

        # setup syntax highlighting
        language_manager = GtkSource.LanguageManager()
        language = language_manager.guess_language(None, "text/x-python")
        source_buffer.set_language(language)

        try:
            self.set_icon_from_file(ICON_FILE)
        except GObject.GError:
            # icon not found = no icon
            pass

        self.show_all()

    @staticmethod
    def open_file(filename):
        """
        Open filename.

        :param filename: filename to open.
        :return:  True if file was opened.
        """
        try:
            ShoebotEditorWindow(filename)
            return True
        except IOError as e:
            errmsg = e.args[1]
            dialog = Gtk.MessageDialog(
                None,
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK,
                _("Cannot open file '%s': %s") % (filename, errmsg),
            )
        dialog.run()
        dialog.destroy()
        return False

    def on_close_file(self, widget):
        if self.confirm_quit_or_save():
            self.close_view()
            return False
        return True

    def on_close_window(self, window, event, data=None):
        if self.confirm_quit_or_save():
            self.close_view()
            return False
        return True

    def on_new_file(self, widget):
        ShoebotEditorWindow()

    def on_open_file(self, widget):
        chooser = ShoebotFileChooserDialog(
            _("Open File"),
            None,
            Gtk.FileChooserAction.OPEN,
            (
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.ACCEPT,
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
            ),
        )

        if chooser.run() == Gtk.ResponseType.ACCEPT:
            try:
                source_buffer = self.get_source_buffer()
                if (
                    source_buffer.can_undo() is False
                    and source_buffer.can_redo() is False
                ):
                    # Opening in an unmodified buffer, so a new window is not needed
                    source_buffer.open_file(chooser.get_filename())
                else:
                    # Default, open a new window
                    ShoebotEditorWindow(chooser.get_filename())
            except IOError as e:
                errmsg = e.args[1]
                error_dialog = Gtk.MessageDialog(
                    None,
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.INFO,
                    Gtk.ButtonsType.OK,
                    f"Cannot open file '{chooser.get_filename()}': {errmsg}",
                )
                error_dialog.run()
                error_dialog.destroy()

        chooser.destroy()

    def save_or_save_as(self):
        """
        Call save_as if file has never been saved otherwise call save.
        """
        filename = self.source_view.get_buffer().filename
        if filename:
            self.save(filename)
        else:
            self.save_as()

    def on_save_file_as(self, widget):
        self.save_as()

    def on_save_file(self, widget):
        self.save_or_save_as()

    def on_quit(self, widget):
        for view in ShoebotIDE.editor_windows:
            if not view.confirm_quit_or_save():
                return
        if self.shoebot_window is not None:
            self.shoebot_window.destroy()

        Gtk.main_quit()
        sys.exit()

    def on_insert_and_scroll(self, callback_action, widget):
        buffer = self.get_source_buffer()

        start, end = buffer.get_bounds()
        mark = buffer.create_mark(None, end, False)

        buffer.insert(
            end,
            "Hello this is multiple lines of text\n"
            "Line 1\n"
            "Line 2\n"
            "Line 3\n"
            "Line 4\n"
            "Line 5\n",
        )

        self.source_view.scroll_to_mark(mark, 0, True, 0.0, 1.0)
        buffer.delete_mark(mark)

    def toggle_dark_theme(self, dark=False):
        Gtk.Settings.get_default().set_property(
            "gtk-application-prefer-dark-theme", dark
        )
        if dark:
            scheme_name = "cobalt"
        else:
            scheme_name = "classic"

        ShoebotIDE.set_source_buffers_style_scheme(scheme_name)
        ShoebotIDE.dark_theme = dark

    def on_theme_changed(self, widget, current):
        # Theme is either ThemeLight or ThemeDark
        self.toggle_dark_theme(dark=current.get_name() == "ThemeDark")

    def on_wrap_changed(self, widget, current):
        self.source_view.set_wrap_mode(GTK_WRAP_MODES[current.get_name()])

    def on_varwindow_changed(self, widget):
        self.use_varwindow = widget.get_active()

    def on_socketserver_changed(self, widget):
        self.use_socketserver = widget.get_active()

    def on_fullscreen_changed(self, widget):
        self.go_fullscreen = widget.get_active()

    def on_color_cycle_changed(self, widget):
        self.source_view.get_buffer().set_colors(widget.get_active())

    def on_apply_tabs(self, callback_action, widget):
        source_buffer = self.get_source_buffer()
        bounds = source_buffer.get_selection_bounds()
        if bounds:
            start, end = bounds
            if callback_action:
                source_buffer.remove_tag(source_buffer.custom_tabs_tag, start, end)
            else:
                source_buffer.apply_tag(source_buffer.custom_tabs_tag, start, end)

    def on_apply_colors(self, callback_action, widget):
        source_buffer = self.get_source_buffer()
        bounds = source_buffer.get_selection_bounds()
        if bounds:
            start, end = bounds
            if not callback_action:
                for tag in source_buffer.color_tags:
                    source_buffer.remove_tag(tag, start, end)
            else:
                tmp = source_buffer.color_tags
                i = 0
                next = start.copy()
                while next.compare(end) < 0:
                    next.forward_chars(2)
                    if next.compare(end) >= 0:
                        next = end

                    source_buffer.apply_tag(tmp[i], start, next)
                    i += 1
                    if i >= len(tmp):
                        i = 0
                    start = next.copy()

    def on_remove_tags(self, callback_action, widget):
        source_buffer = self.get_source_buffer()
        bounds = source_buffer.get_selection_bounds()
        if bounds:
            start, end = bounds
            source_buffer.remove_all_tags(start, end)

    def on_clear_console(self, widget):
        self.console_error.clear()

    def search_dialog_handler(self, dialog, search_direction):
        if search_direction not in [SEARCH_FORWARD, SEARCH_BACKWARD]:
            dialog.destroy()
            return

        start, end = dialog.get_source_buffer.get_bounds()
        search_string = start.get_text(end)

        print(_(f"Searching for `{search_string}'\n"))

        buffer = self.get_source_buffer()
        buffer.search(search_string, self, search_direction)
        dialog.destroy()

    def on_find(self, widget):
        search_text = Gtk.TextView()
        dialog = Gtk.Dialog(
            _("Search"),
            self,
            Gtk.DialogFlags.DESTROY_WITH_PARENT,
            (
                _("Forward"),
                SEARCH_FORWARD,
                _("Backward"),
                SEARCH_BACKWARD,
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.NONE,
            ),
        )
        dialog.vbox.pack_end(search_text, True, True, 0)
        dialog.source_buffer = search_text.get_buffer()
        dialog.connect("response", self.search_dialog_handler)

        search_text.show()
        search_text.grab_focus()
        dialog.show_all()

    def on_undo(self, widget):
        source_buffer = self.get_source_buffer()
        if source_buffer.can_undo():
            source_buffer.undo()

    def on_redo(self, widget):
        source_buffer = self.get_source_buffer()
        if source_buffer.can_redo():
            source_buffer.redo()

    def on_about(self, widget):
        about_dialog = Gtk.AboutDialog()
        website = "http://shoebot.net/"
        authors = [
            "Dave Crossland <dave AT lab6.com>",
            "est <electronixtar AT gmail.com>",
            "Francesco Fantoni <francesco AT hv-a.com>",
            "Paulo Silva <nitrofurano AT gmail.com>",
            "Pedro Angelo <pangelo AT virii-labs.org>",
            "Ricardo Lafuente <ricardo AT sollec.org>",
            "Stuart Axon <stuaxo2 AT yahoo.com>",
            "Tetsuya Saito <t2psyto AT gmail.com>",
        ]
        about_dialog.set_version("1.4")
        about_dialog.set_name("shoebot")
        about_dialog.set_license("GPLv3")
        about_dialog.set_authors(authors)
        about_dialog.set_website(website)

        about_dialog.connect("response", lambda dialog, data: dialog.destroy())
        about_dialog.show_all()

    def init_menus(self):
        text_view = self.source_view
        direction = text_view.get_direction()
        wrap_mode = text_view.get_wrap_mode()
        menu_item = None

        # if direction == Gtk.TextDirection.LTR:
        #     menu_item = self.item_factory.get_widget("/Settings/Left-to-Right")
        # elif direction == Gtk.TextDirection.RTL:
        #     menu_item = self.item_factory.get_widget("/Settings/Right-to-Left")

        if menu_item:
            menu_item.activate()

        # if wrap_mode == Gtk.WrapMode.NONE:
        #     menu_item = self.item_factory.get_widget("/Settings/Wrap Off")
        # elif wrap_mode == Gtk.WrapMode.WORD:
        #     menu_item = self.item_factory.get_widget("/Settings/Wrap Words")
        # elif wrap_mode == Gtk.WrapMode.CHAR:
        #     menu_item = self.item_factory.get_widget("/Settings/Wrap Chars")

        # if menu_item:
        #     menu_item.activate()

    def close_view(self):
        ShoebotIDE.remove_editor_window(self)
        source_buffer = self.get_source_buffer()
        # source_buffer.unref()
        source_buffer.disconnect(self.bhid)
        self.source_view.destroy()
        del self.source_view
        self.source_view = None
        self.destroy()
        del self
        if not ShoebotIDE.editor_windows:
            Gtk.main_quit()

    def confirm_quit_or_save(self):
        if self.get_source_buffer().get_modified():
            dialog = Gtk.MessageDialog(
                self,
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.YES_NO,
                _("Save changes to '%s'?") % self.get_source_buffer().pretty_name(),
            )
            dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
            result = dialog.run()
            dialog.destroy()
            if result == Gtk.ResponseType.YES:
                self.save_or_save_as()
            else:
                return result == Gtk.ResponseType.NO
        return True

    def save(self, filename):
        """
        :param filename:  Filename to save to
        :return:  True on success.

        Updates source_buffer.filename on success.
        """
        save_succeeded = False
        have_backup = False
        backup_filename = filename + "~"
        try:
            if os.path.isfile(backup_filename):
                os.remove(backup_filename)
            os.rename(filename, backup_filename)
        except (OSError, IOError) as e:
            errnum, errmsg = e.args
            if errnum != errno.ENOENT:
                err = f"Cannot back up '{filename}' to '{backup_filename}': {errmsg}"
                dialog = Gtk.MessageDialog(
                    self,
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.INFO,
                    Gtk.ButtonsType.OK,
                    err,
                )
                dialog.run()
                dialog.destroy()
                return False

        have_backup = True
        source_buffer = self.get_source_buffer()
        start, end = source_buffer.get_bounds()
        chars = source_buffer.get_slice(start, end, False)
        try:
            with open(self.get_source_buffer().filename, "w") as f:
                f.write(chars)
            save_succeeded = True
            self.get_source_buffer().set_modified(False)
            self.get_source_buffer().filename = filename
        except IOError as e:
            err = f"Error writing to '{filename}': {e.args[1]}"
            dialog = Gtk.MessageDialog(
                self,
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK,
                err,
            )
            dialog.run()
            dialog.destroy()

        if not save_succeeded and have_backup:
            try:
                os.rename(backup_filename, filename)
            except OSError as e:
                err = f"Can't restore backup file '{filename}' to '{back_filename}': {e.args[1]}\nBackup left as '{backup_filename}'"
                dialog = Gtk.MessageDialog(
                    self,
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.INFO,
                    Gtk.ButtonsType.OK,
                    err,
                )
                dialog.run()
                dialog.destroy()

        return save_succeeded

    def save_as(self):
        """
        Return True if the source_buffer was saved
        """
        chooser = ShoebotFileChooserDialog(
            _("Save File"),
            None,
            Gtk.FileChooserAction.SAVE,
            (
                Gtk.STOCK_SAVE,
                Gtk.ResponseType.ACCEPT,
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
            ),
        )
        chooser.set_do_overwrite_confirmation(True)
        chooser.set_transient_for(self)
        saved = chooser.run() == Gtk.ResponseType.ACCEPT
        if saved:
            filename = chooser.get_filename()
            if self.save(filename):
                self.update_window_title()
        chooser.destroy()
        return saved

    def update_window_title(self):
        """
        Update the window title from the filename in the source_buffer.
        :return:
        """
        save_prefix = "*" if self.source_view.get_buffer().get_modified() else ""
        window_title = (
            f"Shoebot - {save_prefix}{self.source_view.get_buffer().pretty_name()}"
        )
        self.set_title(window_title)

    def cursor_set_callback(self, buffer, location, mark):

        # TODO: here should go the line syntax highlighter
        # 1. get buffer
        #      get modification state
        # 2. get line contents
        # 3. replace by pygmentised content
        #      revert to modification state
        self.update_window_title()

    def tab_stops_expose(self, widget, event):
        # print(self, widget, event)
        text_view = widget

        # See if this expose is on the tab stop window
        top_win = text_view.get_window(Gtk.TextWindowType.TOP)
        bottom_win = text_view.get_window(Gtk.TextWindowType.BOTTOM)

        if event.window == top_win:
            type = Gtk.TextWindowType.TOP
            target = top_win
        elif event.window == bottom_win:
            type = Gtk.TextWindowType.BOTTOM
            target = bottom_win
        else:
            return False

        first_x = event.area.x
        last_x = first_x + event.area.width

        first_x, y = text_view.window_to_buffer_coords(type, first_x, 0)
        last_x, y = text_view.window_to_buffer_coords(type, last_x, 0)

        source_buffer = text_view.get_buffer()
        insert = source_buffer.get_iter_at_mark(source_buffer.get_insert())
        attrs = Gtk.TextAttributes()
        insert.get_attributes(attrs)

        tabslist = []
        in_pixels = False
        if attrs.tabs:
            tabslist = attrs.tabs.get_tabs()
            in_pixels = attrs.tabs.get_positions_in_pixels()

        for align, position in tabslist:
            if not in_pixels:
                position = Pango.PIXELS(position)

            pos, y = text_view.buffer_to_window_coords(type, position, 0)
            target.draw_line(text_view.style.fg_gc[text_view.state], pos, 0, pos, 15)

        return True

    def get_lines(self, first_y, last_y, buffer_coords, numbers):
        text_view = self.source_view
        # Get iter at first y
        it, top = text_view.get_line_at_y(first_y)

        # For each iter, get its location and add it to the arrays.
        # Stop when we pass last_y
        count = 0

        while not it.is_end():
            y, height = text_view.get_line_yrange(it)
            buffer_coords.append(y)
            line_num = it.get_line()
            numbers.append(line_num)
            count += 1
            if (y + height) >= last_y:
                break
            it.forward_line()

        return count

    def on_run_script(self, widget):
        # get the buffer contents
        source_buffer = self.source_view.get_buffer()
        start, end = source_buffer.get_bounds()
        codestring = source_buffer.get_text(start, end, include_hidden_chars=False)
        window_title = self.get_title()
        try:
            buffer_dir = os.path.dirname(source_buffer.filename or "")
            if buffer_dir:
                os.chdir(buffer_dir)

            bot = shoebot.create_bot(
                codestring,
                shoebot.NODEBOX,
                server=self.use_socketserver,
                show_vars=self.use_varwindow,
                title=window_title,
                window=True,
            )
            self.shoebot_window = bot._canvas.sink
            bot.run(
                codestring, run_forever=True, max_iterations=None, frame_limiter=True
            )
        except (ShoebotError, NameError):
            import traceback
            import sys

            errmsg = traceback.format_exc(limit=1)
            err = _("Error in Shoebot script:") + "\n {errmsg}"
            dialog = Gtk.MessageDialog(
                self,
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK,
                err,
            )
            result = dialog.run()
            dialog.destroy()
            self.shoebot_window = None
            return False

        # TODO: have a try/except that shows an error window

    def get_source_buffer(self):
        return self.source_view.get_buffer()


class ShoebotIDE:
    colormap = None
    untitled_file_counter = 0
    editor_windows = list()

    dark_theme = (
        Gtk.Settings.get_default().get_property("gtk-theme-name").endswith("-dark")
    )  # TODO - Is there a proper way of doing this?

    def __init__(self, filenames):
        if not filenames:
            ShoebotEditorWindow()
        else:
            self.open_files(filenames)

    @classmethod
    def open_files(cls, filenames):
        files_not_opened = []
        files_were_opened = False
        for filename in filenames:
            filename = os.path.abspath(filename)
            try:
                ShoebotEditorWindow(filename)
            except IOError as e:
                files_not_opened.append(filename)
            else:
                files_were_opened = True

        if files_not_opened:
            dialog = Gtk.MessageDialog(
                None,
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK,
                _("Cannot open files:") + "\n%s" % "\n".join(files_not_opened),
            )
            dialog.run()
            dialog.destroy()

        if not files_were_opened:
            sys.exit(1)

    @classmethod
    def set_source_buffers_style_scheme(cls, scheme_name):
        style_manager = GtkSource.StyleSchemeManager.get_default()
        scheme = style_manager.get_scheme(scheme_name)

        for view in cls.editor_windows:
            source_buffer = view.get_source_buffer()
            source_buffer.set_style_scheme(scheme)

    @classmethod
    def add_editor_window(cls, view):
        cls.editor_windows.append(view)

    @classmethod
    def remove_editor_window(cls, view):
        cls.editor_windows.remove(view)

    @classmethod
    def get_next_untitled_filename(cls):
        cls.untitled_file_counter += 1
        if cls.untitled_file_counter == 1:
            return _("Untitled")
        else:
            return _("Untitled #%d") % cls.untitled_file_counter

    @property
    def source_buffer(self):
        return self.source_view.get_buffer()


def main():
    parser = argparse.ArgumentParser(_("usage: shoebot [file...[file]]"))
    parser.add_argument("filenames", nargs="*")

    args = parser.parse_args()

    filenames = vars(args)["filenames"]

    app = ShoebotIDE(filenames)
    Gtk.main()


if __name__ == "__main__":
    main()
