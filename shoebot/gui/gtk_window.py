import os
import sys

from pathlib import Path
from shoebot.core.backend import gi
from shoebot.core.events import (
    publish_event,
    QUIT_EVENT,
    VARIABLE_CHANGED_EVENT,
    REDRAW_EVENT,
)
from gi.repository import Gdk, Gtk

from pkg_resources import resource_filename, Requirement

from shoebot.gui import ShoebotWidget, VarWindow
from shoebot.core import DrawQueueSink
from .gtk_input_device import GtkInputDeviceMixin

import locale
import gettext

APP = "shoebot"
DIR = sys.prefix + "/share/shoebot/locale"
ICON_FILE = resource_filename(
    Requirement.parse("shoebot"), "share/pixmaps/shoebot-ide.png"
)
locale.setlocale(locale.LC_ALL, "")
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext


class ShoebotWindow(Gtk.Window, GtkInputDeviceMixin, DrawQueueSink):
    """
    Create a GTK+ window that contains a ShoebotWidget
    """

    # Draw in response to an expose-event
    def __init__(
        self,
        title=None,
        show_vars=False,
        menu_enabled=True,
        server=False,
        port=7777,
        fullscreen=False,
        outputfile=None,
    ):
        Gtk.Window.__init__(self)
        DrawQueueSink.__init__(self)
        GtkInputDeviceMixin.__init__(self)

        if os.path.isfile(ICON_FILE):
            self.set_icon_from_file(ICON_FILE)

        self.menu_enabled = menu_enabled
        self.has_server = server
        self.serverport = port
        self.show_vars = show_vars
        self.var_window = None
        self.is_fullscreen = False

        sb_widget = ShoebotWidget(input_device=self)

        self.title = title
        if title:
            self.set_title(title)
        if fullscreen:
            self.is_fullscreen = True
            self.fullscreen()
        self.connect("delete-event", self.do_window_close)

        self.sb_widget = sb_widget
        self.attach_gtk(self)

        self.uimanager = Gtk.UIManager()
        accelgroup = self.uimanager.get_accel_group()
        self.add_accel_group(accelgroup)

        self.action_group = Gtk.ActionGroup(name="Canvas")

        self.action_group.add_actions(
            [
                ("Save as", None, _("_Save as")),
                (
                    "svg",
                    "Save as SVG",
                    _("Save as _SVG"),
                    "<Control>1",
                    None,
                    self.snapshot_svg,
                ),
                (
                    "pdf",
                    "Save as PDF",
                    _("Save as _PDF"),
                    "<Control>2",
                    None,
                    self.snapshot_pdf,
                ),
                (
                    "ps",
                    "Save as PS",
                    _("Save as P_S"),
                    "<Control>3",
                    None,
                    self.snapshot_ps,
                ),
                (
                    "png",
                    "Save as PNG",
                    _("Save as P_NG"),
                    "<Control>4",
                    None,
                    self.snapshot_png,
                ),
                (
                    "close",
                    "Close window",
                    _("_Close Window"),
                    "<Control>w",
                    None,
                    self.do_window_close,
                ),
            ]
        )

        self.action_group.add_toggle_actions(
            [
                (
                    "vars",
                    "Variables Window",
                    _("Va_riables Window"),
                    "<Control>r",
                    None,
                    self.do_toggle_variables,
                    self.show_vars,
                ),
                (
                    "fullscreen",
                    "Fullscreen",
                    _("_Fullscreen"),
                    "<Control>f",
                    None,
                    self.do_toggle_fullscreen,
                    False,
                ),
                ("play", "Play", _("_Play"), "<Alt>p", None, self.do_toggle_play, True),
            ]
        )

        menuxml = """
        <popup action="Save as">
            <menuitem action="play"/>
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
        """

        self.uimanager.insert_action_group(self.action_group, 0)
        self.uimanager.add_ui_from_string(menuxml)

        sb_widget.show()
        self.add(sb_widget)

        self.present()

        self.pending_snapshots = []  # list of filenames to save after rendering.
        if outputfile:
            # The test harness uses this to get the gui to output an image, otherwise it may not make much sense
            # to have an output file with a GUI window ?
            self.pending_snapshots.append(outputfile)

        while Gtk.events_pending():
            Gtk.main_iteration()

        self.window_open = True
        self.pause_speed = None  # TODO - factor out bot controller stuff

    def gtk_mouse_button_down(self, widget, event):
        """ Handle right mouse button clicks """
        if self.menu_enabled and event.button == 3:
            menu = self.uimanager.get_widget("/Save as")
            menu.popup(None, None, None, None, event.button, event.time)
        else:
            super(ShoebotWindow, self).gtk_mouse_button_down(widget, event)

    def render(self, size, frame, drawqueue):
        cairo_ctx = super(self.__class__, self).render(size, frame, drawqueue)
        self.sb_widget.do_drawing(size, frame, cairo_ctx)

    def rendering_finished(self, size, frame, r_context):
        """
        Save any snapshots that were scheduled from the GUI

        :param size:  width, height
        :param frame:   frame  number
        :param r_context:  cairo context
        """
        canvas = self.bot.canvas

        pending_snapshots = self.pending_snapshots
        for filename in pending_snapshots:
            # TODO, show filename in the GUI.
            print(f"Save snapshot: {filename}", file=sys.stderr)
            # TODO - remove many of these closures.
            f = canvas.output_closure(filename)
            f(r_context)

        super().rendering_finished(size, frame, r_context)

    def create_rcontext(self, size, frame):
        """
        Delegates to the sb_widget
        """
        return self.sb_widget.create_rcontext(size, frame)

    def show_variables_window(self):
        """
        Show the variables window.
        """
        if self.var_window is None and self.bot._vars:
            self.var_window = VarWindow(
                self, self.bot, "%s variables" % (self.title or "Shoebot")
            )
            self.var_window.window.connect("destroy", self.var_window_closed)

    def hide_variables_window(self):
        """
        Hide the variables window
        """
        if self.var_window is not None:
            self.var_window.window.destroy()
            self.var_window = None

    def var_window_closed(self, widget):
        """
        Called if user clicked close button on var window
        :param widget:
        :return:
        """
        # TODO - Clean up the menu handling stuff its a bit spaghetti right now
        self.action_group.get_action("vars").set_active(False)
        self.show_vars = False
        self.var_window = None

    def var_changed(self, name, value):
        self.bot._namespace[name] = value
        if self.var_window:
            return self.var_window.update_var(name, value)
        else:
            v = self.bot._vars[name]
            publish_event(VARIABLE_CHANGED_EVENT, v)
            return True, value

    def output_image_filename(self, format):
        """
        :param format:  Format, e.g. svg, pdf, png
        :return:  Full image filename, based on bot name
        """
        script = self.bot._namespace["__file__"]
        if script:
            return f"{Path(script).stem}.{format}"

        return f"output.{format}"

    def snapshot_svg(self, widget):
        """
        Request to save an SVG file after drawing is complete.
        """
        self.pending_snapshots.append(self.output_image_filename("svg"))
        publish_event(
            REDRAW_EVENT, data=(None, None)
        )  # TODO - this probably wants its own event

    def snapshot_ps(self, widget):
        """
        Request to save a Postscript file after drawing is complete.
        """
        self.pending_snapshots.append(self.output_image_filename("ps"))
        publish_event(
            REDRAW_EVENT, data=(None, None)
        )  # TODO - this probably wants its own event

    def snapshot_pdf(self, widget):
        """
        Request to save a PDF file after drawing is complete.
        """
        self.pending_snapshots.append(self.output_image_filename("pdf"))
        publish_event(
            REDRAW_EVENT, data=(None, None)
        )  # TODO - this probably wants its own event

    def snapshot_png(self, widget):
        """
        Request to save a PNG file after drawing is complete.
        """
        self.pending_snapshots.append(self.output_image_filename("png"))
        publish_event(
            REDRAW_EVENT, data=(None, None)
        )  # TODO - this probably wants its own event

    def trigger_fullscreen_action(self, fullscreen):
        """
        Toggle fullscreen from outside the GUI,
        causes the GUI to updated and run all its actions.
        """
        action = self.action_group.get_action("fullscreen")
        action.set_active(fullscreen)

    def do_fullscreen(self, widget):
        """
        Widget Action to Make the window fullscreen and update the bot.
        """
        self.fullscreen()
        self.is_fullscreen = True
        # next lines seem to be needed for window switching really to
        # fullscreen mode before reading it's size values
        while Gtk.events_pending():
            Gtk.main_iteration()
        # we pass the full-screen size to bot
        self.bot._screen_width = Gdk.Screen.width()
        self.bot._screen_height = Gdk.Screen.height()
        self.bot._screen_ratio = self.bot._screen_width / self.bot._screen_height

    def do_unfullscreen(self, widget):
        """
        Widget Action to set Windowed Mode.
        """
        self.unfullscreen()
        self.is_fullscreen = False
        self.bot._screen_ratio = None

    def do_window_close(self, widget, data=None):
        """
        Widget Action to Close the window, triggering the quit event.
        """
        publish_event(QUIT_EVENT)

        if self.has_server:
            self.sock.close()

        self.hide_variables_window()

        self.destroy()
        self.window_open = False

    def do_toggle_fullscreen(self, action):
        """
        Widget Action to Toggle fullscreen from the GUI
        """
        is_fullscreen = action.get_active()
        if is_fullscreen:
            self.fullscreen()
        else:
            self.unfullscreen()

    def do_toggle_play(self, action):
        """
        Widget Action to toggle play / pause.
        """
        # TODO - move this into bot controller
        # along with stuff in socketserver and shell
        if self.pause_speed is None and not action.get_active():
            self.pause_speed = self.bot._speed
            self.bot._speed = 0
        else:
            self.bot._speed = self.pause_speed
            self.pause_speed = None

    def do_toggle_variables(self, action):
        """
        Widget Action to toggle showing the variables window.
        """
        self.show_vars = action.get_active()
        if self.show_vars:
            self.show_variables_window()
        else:
            self.hide_variables_window()

    def main_iteration(self):
        """
        Called from main loop, if your sink needs to handle GUI events
        do it here.

        Check any GUI flags then call Gtk.main_iteration to update things.
        """
        if self.show_vars:
            self.show_variables_window()
        else:
            self.hide_variables_window()

        while Gtk.events_pending():
            Gtk.main_iteration()
