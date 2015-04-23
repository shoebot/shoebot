#!/usr/bin/env python2
# -*- coding: iso-8859-1 -*-

from __future__ import print_function
try:
    import gi
except ImportError:
    import pgi
    pgi.install_as_gi()

gi.require_version('Gtk', '3.0')

import errno
import os
import sys

from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GtkSource
from gi.repository import Pango

import shoebot

# for gtksourceview/gtksourceview2 compatibility
# try:
#     import gtksourceview
#
# except ImportError:
#     from gi.repository import GtkSource
#
#     class gtksourceview_SourceBuffer(GtkSource.Buffer):
#         def set_highlight(self, bool):
#             return self.set_highlight_syntax(bool)
#
#     class gtksourceview_SourceLanguagesManager(GtkSource.LanguageManager):
#         def get_language_from_mime_type(self, mime_types):
#             lang_manager = GtkSource.LanguageManager.get_default()
#             lang_result = None
#             for lang_id in lang_manager.get_language_ids():
#                  lang = lang_manager.get_language(lang_id)
#                  if mime_types in lang.get_mime_types():
#                       lang_result = lang
#                       break
#
#             return lang_result
#
#     gtksourceview = gtksourceview2
#     gtksourceview.SourceBuffer = gtksourceview_SourceBuffer
#     gtksourceview.SourceView = GtkSource.View
#     gtksourceview.SourceLanguagesManager = gtksourceview_SourceLanguagesManager
#     del gtksourceview_SourceBuffer
#     del gtksourceview_SourceLanguagesManager


from shoebot.data import ShoebotError


APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
RESPONSE_FORWARD = 0
RESPONSE_BACKWARD = 1


import locale
import gettext
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
#gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext


if sys.platform != 'win32':
    ICON_FILE = '/usr/share/shoebot/icon.png'
else:
    import os.path
    ICON_FILE = os.path.join(sys.prefix, 'share', 'shoebot', 'icon.png')

def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return (v, v, v)
    else:
        hue = h * 6.0
        saturation = s
        value = v

        if hue >= 6.0:
            hue = 0.0

        f = hue - int(hue)
        p = value * (1.0 - saturation)
        q = value * (1.0 - saturation * f)
        t = value * (1.0 - saturation * (1.0 - f))

        ihue = int(hue)
        if ihue == 0:
            return(value, t, p)
        elif ihue == 1:
                return(q, value, p)
        elif ihue == 2:
                return(p, value, t)
        elif ihue == 3:
            return(p, q, value)
        elif ihue == 4:
            return(t, p, value)
        elif ihue == 5:
            return(value, p, q)

def hue_to_color(hue):
    if hue > 1.0:
        raise ValueError

    h, s, v = hsv_to_rgb (hue, 1.0, 1.0)
    return (h*65535, s*65535, v*65535)


class Buffer(GtkSource.Buffer):
    N_COLORS = 16
    PANGO_SCALE = 1024

    def __init__(self):
        GObject.GObject.__init__(self)
        tt = self.get_tag_table()
        self.refcount = 0
        self.filename = None
        self.untitled_serial = -1
        self.color_tags = []
        self.color_cycle_timeout_id = 0
        self.start_hue = 0.0

        for i in range(Buffer.N_COLORS):
            tag = self.create_tag()
            self.color_tags.append(tag)

        #self.invisible_tag = self.create_tag(None, invisible=True)
        self.not_editable_tag = self.create_tag(editable=False,
                                                foreground="purple")
        self.found_text_tag = self.create_tag(foreground="red")

        tabs = Pango.TabArray.new(4, True)
        tabs.set_tab(0, Pango.TabAlign.LEFT, 10)
        tabs.set_tab(1, Pango.TabAlign.LEFT, 30)
        tabs.set_tab(2, Pango.TabAlign.LEFT, 60)
        tabs.set_tab(3, Pango.TabAlign.LEFT, 120)
        self.custom_tabs_tag = self.create_tag(tabs=tabs, foreground="green")
        TestText.buffers.push(self)

    def pretty_name(self):
        if self.filename:
            return os.path.basename(self.filename)
        else:
            if self.untitled_serial == -1:
                self.untitled_serial = TestText.untitled_serial
                TestText.untitled_serial += 1

            if self.untitled_serial == 1:
                return _('Untitled')
            else:
                return _('Untitled #%d') % self.untitled_serial

    def filename_set(self):
        for view in TestText.views:
            if view.text_view.get_buffer() == self:
                view.set_view_title()

    def search(self, str, view, forward):
        # remove tag from whole buffer
        start, end = self.get_bounds()
        self.remove_tag(self.found_text_tag, start, end)

        iter = self.get_iter_at_mark(self.get_insert())

        i = 0
        if str:
            if forward:
                while 1:
                    res = iter.forward_search(str, Gtk.TextSearchFlags.TEXT_ONLY)
                    if not res:
                        break
                    match_start, match_end = res
                    i += 1
                    self.apply_tag(self.found_text_tag, match_start, match_end)
                    iter = match_end
            else:
                while 1:
                    res = iter.backward_search(str, Gtk.TextSearchFlags.TEXT_ONLY)
                    if not res:
                        break
                    match_start, match_end = res
                    i += 1
                    self.apply_tag(self.found_text_tag, match_start, match_end)
                    iter = match_start

        dialog = Gtk.MessageDialog(view,
                                   Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                   Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK,
                                   _('%d strings found and marked in red') % i)

        dialog.connect("response", lambda x,y: dialog.destroy())

        dialog.show()

    def search_forward(self, str, view):
        self.search(str, view, True)

    def search_backward(self, str, view):
        self.search(str, view, False)

    def ref(self):
        self.refcount += 1

    def unref(self):
        self.refcount -= 1
        if self.refcount == 0:
            self.set_colors(False)
            TestText.buffers.remove(self)
            del self

    def color_cycle_timeout(self):
        self.cycle_colors()
        return True

    def set_colors(self, enabled):
        hue = 0.0

        if (enabled and self.color_cycle_timeout_id == 0):
            self.color_cycle_timeout_id = Gtk.timeout_add(
                200, self.color_cycle_timeout)
        elif (not enabled and self.color_cycle_timeout_id != 0):
            Gtk.timeout_remove(self.color_cycle_timeout_id)
            self.color_cycle_timeout_id = 0

        for tag in self.color_tags:
            if enabled:
                color = apply(TestText.colormap.alloc_color,
                              hue_to_color(hue))
                tag.set_property("foreground_gdk", color)
            else:
                tag.set_property("foreground_set", False)
            hue += 1.0 / Buffer.N_COLORS

    def cycle_colors(self):
        hue = self.start_hue

        for tag in self.color_tags:
            color = apply(TestText.colormap.alloc_color,
                          hue_to_color (hue))
            tag.set_property("foreground_gdk", color)

            hue += 1.0 / Buffer.N_COLORS
            if hue > 1.0:
                hue = 0.0

        self.start_hue += 1.0 / Buffer.N_COLORS
        if self.start_hue > 1.0:
            self.start_hue = 0.0

    def tag_event_handler(self, tag, widget, event, iter):
        char_index = iter.get_offset()
        tag_name = tag.get_property("name")
        if event.type == Gdk.MOTION_NOTIFY:
            print("Motion event at char %d tag `%s'\n" % (char_index, tag_name))
        elif event.type == Gdk.EventType.BUTTON_PRESS:
            print("Button press at char %d tag `%s'\n" % (char_index, tag_name))
        elif event.type == Gdk._2BUTTON_PRESS:
            print("Double click at char %d tag `%s'\n" % (char_index, tag_name))
        elif event.type == Gdk._3BUTTON_PRESS:
            print("Triple click at char %d tag `%s'\n" % (char_index, tag_name))
        elif event.type == Gdk.BUTTON_RELEASE:
            print("Button release at char %d tag `%s'\n" % (char_index, tag_name))
        elif (event.type == Gdk.KEY_PRESS or
              event.type == Gdk.KEY_RELEASE):
            print("Key event at char %d tag `%s'\n" % (char_index, tag_name))
        return False

    def fill_file_buffer(self, filename):
        try:
            f = open(filename, "r")
        except IOError, (errnum, errmsg):
            err = "Cannot open file '%s': %s" % (filename, errmsg)
            view = TestText.active_window_stack.get()
            dialog = Gtk.MessageDialog(view, Gtk.DialogFlags.MODAL,
                                       Gtk.MessageType.INFO,
                                       Gtk.ButtonsType.OK, err);
            result = dialog.run()
            dialog.destroy()
            return False

        iter = self.get_iter_at_offset(0)
        buf = f.read()
        f.close()
        self.set_text(buf)
        self.set_modified(False)

        return True

    def save_buffer(self):
        result = False
        have_backup = False
        if not self.filename:
            return False

        bak_filename = self.filename + "~"
        try:
            if os.path.isfile(bak_filename):
                os.remove(bak_filename)
            os.rename(self.filename, bak_filename)
        except (OSError, IOError), (errnum, errmsg):
            if errnum != errno.ENOENT:
                err = "Cannot back up '%s' to '%s': %s" % (self.filename,
                                                           bak_filename,
                                                           errmsg)
                view = TestText.active_window_stack.get()
                dialog = Gtk.MessageDialog(view, Gtk.DialogFlags.MODAL,
                                           Gtk.MessageType.INFO,
                                           Gtk.ButtonsType.OK, err);
                dialog.run()
                dialog.destroy()
                return False

        have_backup = True
        start, end = self.get_bounds()
        chars = self.get_slice(start, end, False)
        try:
            file = open(self.filename, "w")
            file.write(chars)
            file.close()
            result = True
            self.set_modified(False)
        except IOError, (errnum, errmsg):
            err = "Error writing to '%s': %s" % (self.filename, errmsg)
            view = TestText.active_window_stack.get()
            dialog = Gtk.MessageDialog(view, Gtk.DialogFlags.MODAL,
                                       Gtk.MessageType.INFO,
                                       Gtk.ButtonsType.OK, err);
            dialog.run()
            dialog.destroy()

        if not result and have_backup:
            try:
                os.rename(bak_filename, self.filename)
            except OSError, (errnum, errmsg):
                err = "Can't restore backup file '%s' to '%s': %s\nBackup left as '%s'" % (
                    self.filename, bak_filename, errmsg, bak_filename)
                view = TestText.active_window_stack.get()
                dialog = Gtk.MessageDialog(view, Gtk.DialogFlags.MODAL,
                                           Gtk.MessageType.INFO,
                                           Gtk.ButtonsType.OK, err);
                dialog.run()
                dialog.destroy()

        return result

    def confirm_overwrite_callback(self, chooser):
      uri = chooser.get_uri()
      if os.path.exists(self.filename):
          if os.path.exists(self.filename):
              if user_wants_to_replace_read_only_file (uri):
                  return Gtk.FILE_CHOOSER_CONFIRMATION_ACCEPT_FILENAME
              else:
                  return Gtk.FILE_CHOOSER_CONFIRMATION_SELECT_AGAIN
          else:
              # fall back to the default dialog
              return Gtk.FILE_CHOOSER_CONFIRMATION_CONFIRM

    def save_as_buffer(self):
        """
        Return True if the buffer was saved
        """
        chooser = ShoebotFileChooserDialog(_('Save File'), None, Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT,
             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        chooser.set_do_overwrite_confirmation(True)

        chooser.connect("confirm-overwrite", self.confirm_overwrite_callback)
        
        saved = chooser.run() == Gtk.ResponseType.ACCEPT
        if saved:
                old_filename = self.filename
                self.filename = chooser.get_filename()
                if self.save_buffer():
                    self.filename = chooser.get_filename()
                    self.filename_set()
                else:
                    self.filename = old_filename
        chooser.destroy()
        return saved

    def check_buffer_saved(self):
        """
        If the buffer was not saved then give the user the chance to save it
        or cancel.
        
        Return True is the buffer was saved in the end
        """
        if self.get_modified():
            pretty_name = self.pretty_name()
            msg = _("Save changes to '%s'?") % pretty_name
            view = TestText.active_window_stack.get()
            dialog = Gtk.MessageDialog(view, Gtk.DialogFlags.MODAL,
                                       Gtk.MessageType.QUESTION,
                                       Gtk.ButtonsType.YES_NO, msg);
            dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
            result = dialog.run()
            dialog.destroy()
            if result == Gtk.ResponseType.YES:
                if self.filename:
                    return self.save_buffer()
                else:
                    return self.save_as_buffer()
            elif result == Gtk.ResponseType.NO:
                return True
            else:
                return False
        else:
            return True


class ShoebotFileChooserDialog (Gtk.FileChooserDialog):

    CWD = None

    def __init__(self, *args, **kwargs):
        super(ShoebotFileChooserDialog, self).__init__ (*args, **kwargs)

        # set some defaults
        self.set_default_response (Gtk.ResponseType.OK)
        self.set_property('do-overwrite-confirmation', True)

        # set the working directory if available
        if ShoebotFileChooserDialog.CWD is not None:
            self.set_current_folder(ShoebotFileChooserDialog.CWD)

    def run(self):
        response = super (ShoebotFileChooserDialog, self).run()

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
        # set text area as editable in order to let it be cleaned by selecting and deleting
        # then we set wrap mode for text
        self.text_area.set_editable(True)
        self.text_area.set_wrap_mode(Gtk.WrapMode.WORD)
        self.text_buffer = self.text_area.get_buffer()        
        self.text_window.add(self.text_area)
        # here we set default values for background and text of console window
        self.text_area.modify_base(Gtk.StateType.NORMAL, Gdk.color_parse("dark grey"))
        self.text_area.modify_text(Gtk.StateType.NORMAL, Gdk.color_parse("red"))
        # then we define some text tag for defining colors for system messages and stdout
        self.tag_table = self.text_buffer.get_tag_table()
        ##self.stdout_tag = Gtk.TextTag("stdout")
        ##self.stdout_tag.set_property("foreground", "black")
        ##self.stdout_tag.set_property("style", "normal")
        #self.stdout_tag.set_property("weight", 600)   
        #self.stdout_tag.set_property("size-points", 9)

        self.stdout_tag = self.text_buffer.create_tag("system", foreground="black", weight=600, size_points=9)
        self.system_message_tag = self.text_buffer.create_tag("system", foreground="white")

        ##self.tag_table.add(self.stdout_tag)
        ##self.system_message_tag = Gtk.TextTag("system")
        ##self.system_message_tag.set_property("foreground", "white")
        ##self.system_message_tag.set_property("style", "normal")
        ##self.tag_table.add(self.system_message_tag)
        #self.text_area.modify_font(Pango.FontDescription("monospace italic 9"))


    def write(self, data, output=None, system=None):
        self.message = data
        if not output:
            # no tags set for stderr messages, color will be the one set for TextView            
            self.text_buffer.insert_at_cursor(self.message)
            self.message = ""
        elif system:
            # if output and system values are set, text is treated as a system message
            # and system tag is used
            self.iter = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
            self.text_buffer.insert_with_tags_by_name(self.iter, self.message, "system")
            self.message = ""
        else:
            # if only output value is set, tag used will be stdout
            self.iter = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
            self.text_buffer.insert_with_tags_by_name(self.iter, self.message, "stdout")
            self.message = ""
        # this is the trick to make gtk refresh the window                    
        while Gtk.events_pending():
            Gtk.main_iteration()


class Stdout_Filter(object):
    def __init__(self, parent):
        self.parent = parent
    def write(self, data):
        self.message = data
        self.parent.write(self.message, True)
        self.message = None

    
class View(Gtk.Window):
    ## Gtk3 TODO - GObject.type_register(ShoebotFileChooserDialog)
    FONT = None
    
    def __init__(self, buffer=None):
        menu_items = [
            ( _("/_File"), None, None, 0, "<Branch>" ),
            ( _("/File/_New"), "<control>N", self.do_new, 0, None ),
            ( _("/File/_Open"), "<control>O", self.do_open, 0, None ),
            ( _("/File/_Save"), "<control>S", self.do_save, 0, None ),
            ( _("/File/Save _As..."), None, self.do_save_as, 0, None ),
            ( _("/File/sep1"), None, None, 0, "<Separator>" ),
            ( _("/File/_Close"), "<control>W" , self.do_close, 0, None ),
            ( _("/File/E_xit"), "<control>Q" , self.do_exit, 0, None ),
            ( _("/_Edit"), None, None, 0, "<Branch>" ),
            ( _("/Edit/Undo"), "<control>Z", self.do_undo, 0, None ),
            ( _("/Edit/Redo"), "<control><shift>Z", self.do_redo, 0, None ),
            ( _("/Edit/sep1"), None, None, 0, "<Separator>" ),
            ( _("/Edit/Find..."), "<control>F", self.do_search, 0, None ),
            ( _("/_Settings"), None, None, 0, "<Branch>" ),
            ( _("/Settings/Wrap _Off"), None, self.do_wrap_changed, Gtk.WrapMode.NONE, "<RadioItem>" ),
            ( _("/Settings/Wrap _Words"), None, self.do_wrap_changed, Gtk.WrapMode.WORD, _("/Settings/Wrap Off") ),
            ( _("/Settings/Wrap _Chars"), None, self.do_wrap_changed, Gtk.WrapMode.CHAR, _("/Settings/Wrap Off") ),
            ( _("/_Run"), None, None, 0, "<Branch>" ),
            ( _("/Run/_Run script"), "<control>R", self.run_script, False, None ),
            ( _("/Run/sep1"), None, None, 0, "<Separator>" ),
            ( _("/Run/Run socket server"), None, self.do_socketserver_changed, True, "<ToggleItem>"),
            ( _("/Run/Show variables window"), None, self.do_varwindow_changed, True, "<ToggleItem>"),
            ( _("/Run/Run fullscreen"), None, self.do_fullscreen_changed, True, "<ToggleItem>"),
            ( _("/_Help"), None, None, 0, "<Branch>" ),
            ( _("/Help/_About"), None, self.do_about, 0, None )  
            ]

        if not buffer:
            buffer = Buffer()
        GObject.GObject.__init__(self)

        TestText.views.push(self)

        buffer.ref()

        ## Gtk3.TODO
        ##if not TestText.colormap:
        ##    TestText.colormap = self.get_colormap()

        self.connect("delete_event", self.delete_event_cb)

        self.accel_group = Gtk.AccelGroup()
        ##self.item_factory = Gtk.ItemFactory(Gtk.MenuBar, "<main>",
        ##                                self.accel_group)
        ##self.item_factory.set_data("view", self)
        ##self.item_factory.create_items(menu_items)

        self.add_accel_group(self.accel_group)
        
        hpaned = Gtk.HPaned()
        vbox = Gtk.VBox(False, 0)
        hpaned.add1(vbox)
        self.add(hpaned)

        ##vbox.pack_start(self.item_factory.get_widget("<main>", True, True, 0),
        ##                False, False, 0)

        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        ## self.text_view = gtksourceview.SourceView(buffer)
        self.text_view = GtkSource.View.new_with_buffer(buffer)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.text_view.set_show_line_numbers(True)
        self.text_view.set_auto_indent(True)
        self.text_view.set_insert_spaces_instead_of_tabs(True)
        # FIXME: the following 2 lines don't have any effect :/
        self.text_view.tab_width = 4
        self.text_view.indent_width = 4
        ##self.text_view.connect("expose_event", self.tab_stops_expose)

        self.bhid = buffer.connect("mark_set", self.cursor_set_callback)
        
        if View.FONT is None:
            # Get font or fallback
            context = self.text_view.get_pango_context()
            fonts = context.list_families()
            for font in fonts:
                if font.get_name() == 'Bitstream Vera Sans Mono':
                    View.FONT = 'Bitstream Vera Sans Mono 8'
                    break
            else:
                print('Bitstream Vera Font not found.')
                print('Download and install it from here')
                print('http://ftp.gnome.org/pub/GNOME/sources/ttf-bitstream-vera/1.10/')
                View.FONT = 'Mono 8'

        ##self.text_view.modify_font(Pango.FontDescription(View.FONT))

        vbox.pack_start(sw, True, True, 0)
        sw.add(self.text_view)

        # this creates a console error and output window besides script window
        self.console_error = ConsoleWindow()
        # we create an instance for stdout filter
        self.stdout_filter = Stdout_Filter(self.console_error)
        # we redirect stderr
        ##sys.stderr = self.console_error
        # stdout is redirected too, but through the filter in order to get different color for text
        ##sys.stdout = self.stdout_filter
        # error-console window is added to container as second child
        hpaned.add2(self.console_error.text_window)
        hpaned.set_position(450)
        # message displayed in console-error window at start, the double true values passed makes it render with system message tag
        self.console_error.write(_("This is a console window, error messages and script output are shown here,\n you can clear the window selecting and deleting the content\n\n"), True, True)        
                
        self.set_default_size(800, 500)
        self.text_view.grab_focus()

        self.set_view_title()
        self.init_menus()

        # options toggle
        self.use_varwindow = False
        self.use_socketserver = False
        self.go_fullscreen = False

        # setup syntax highlighting
        manager = GtkSource.LanguageManager()
        ##language = manager.get_language_from_mime_type("text/x-python")
        language = manager.guess_language(None, "text/x-python")
        buffer.set_language(language)
        ##buffer.set_highlight(True)

        self.shoebot_window = None

        try:
            self.set_icon_from_file(ICON_FILE)
        except GObject.GError:
            # icon not found = no icon
            pass

        self.show_all()

    def delete_event_cb(self, window, event, data=None):
        TestText.active_window_stack.push(self)
        self.check_close_view()
        TestText.active_window_stack.pop()
        return True
    #
    # Menu callbacks
    #
    def get_empty_view(self):
        buffer = self.text_view.get_buffer()
        if (not buffer.filename and not buffer.get_modified()):
            return self
        else:
            return View(Buffer())

    def view_from_widget(widget):
        if isinstance(widget, Gtk.MenuItem):
            item_factory = Gtk.item_factory_from_widget(widget)
            return item_factory.get_data("view")
        else:
            app = widget.get_toplevel()
            return app.get_data("view")

    def do_new(self, callback_action, widget):
        View()

    def open_ok_func(self, filename):
        new_view = self.get_empty_view()
        buffer = new_view.text_view.get_buffer()
        if not buffer.fill_file_buffer(filename):
            if new_view != self:
                new_view.close_view()
            return False
        else:
            buffer.filename = filename
            buffer.filename_set()
            return True

    def do_open(self, callback_action, widget):
        chooser = ShoebotFileChooserDialog('Open File', None, Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT,
             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

        if chooser.run() == Gtk.ResponseType.ACCEPT:
            self.open_ok_func(chooser.get_filename())
        chooser.destroy()


    def do_save_as(self, callback_action, widget):
        TestText.active_window_stack.push(self)
        self.text_view.get_buffer().save_as_buffer()
        TestText.active_window_stack.pop()

    def do_save(self, callback_action, widget):
        TestText.active_window_stack.push(self)
        buffer = self.text_view.get_buffer()
        if not buffer.filename:
            self.do_save_as(None, callback_action)
        else:
            buffer.save_buffer()
            TestText.active_window_stack.pop()

    def do_close(self, callback_action, widget):
        TestText.active_window_stack.push(self)
        self.check_close_view()
        TestText.active_window_stack.pop()

    def do_exit(self, callback_action, widget):
        TestText.active_window_stack.push(self)
        for tmp in TestText.buffers:
            if not tmp.check_buffer_saved():
                return
        if hasattr(self, 'sbot_window'):
            self.sbot_window.finish()
            self.sbot_window.destroy()

        Gtk.main_quit()
        TestText.active_window_stack.pop()
        import sys
        sys.exit()

    def do_insert_and_scroll(self, callback_action, widget):
        buffer = self.text_view.get_buffer()

        start, end = buffer.get_bounds()
        mark = buffer.create_mark(None, end, False)

        buffer.insert(end,
                      "Hello this is multiple lines of text\n"
                      "Line 1\n"  "Line 2\n"
                      "Line 3\n"  "Line 4\n"
                      "Line 5\n")

        self.text_view.scroll_to_mark(mark, 0, True, 0.0, 1.0)
        buffer.delete_mark(mark)

    def do_wrap_changed(self, callback_action, widget):
        self.text_view.set_wrap_mode(callback_action)

    def do_varwindow_changed(self, callback_action, widget):
        self.use_varwindow = not self.use_varwindow

    def do_socketserver_changed(self, callback_action, widget):
        self.use_socketserver = not self.use_socketserver
        
    def do_fullscreen_changed(self, callback_action, widget):
        self.go_fullscreen = not self.go_fullscreen

    def do_color_cycle_changed(self, callback_action, widget):
        self.text_view.get_buffer().set_colors(callback_action)

    def do_apply_tabs(self, callback_action, widget):
        buffer = self.text_view.get_buffer()
        bounds = buffer.get_selection_bounds()
        if bounds:
            start, end = bounds
            if callback_action:
                buffer.remove_tag(buffer.custom_tabs_tag, start, end)
            else:
                buffer.apply_tag(buffer.custom_tabs_tag, start, end)

    def do_apply_colors(self, callback_action, widget):
        buffer = self.text_view.get_buffer()
        bounds = buffer.get_selection_bounds()
        if bounds:
            start, end = bounds
            if not callback_action:
                for tag in buffer.color_tags:
                    buffer.remove_tag(tag, start, end)
            else:
                tmp = buffer.color_tags
                i = 0
                next = start.copy()
                while next.compare(end) < 0:
                    next.forward_chars(2)
                    if next.compare(end) >= 0:
                        next = end

                    buffer.apply_tag(tmp[i], start, next)
                    i += 1
                    if i >= len(tmp):
                        i = 0
                    start = next.copy()

    def do_remove_tags(self, callback_action, widget):
        buffer = self.text_view.get_buffer()
        bounds = buffer.get_selection_bounds()
        if bounds:
            start, end = bounds
            buffer.remove_all_tags(start, end)

    def dialog_response_callback(self, dialog, response_id):
        if (response_id != RESPONSE_FORWARD and
            response_id != RESPONSE_BACKWARD):
            dialog.destroy()
            return

        start, end = dialog.buffer.get_bounds()
        search_string = start.get_text(end)

        print(_("Searching for `%s'\n") % search_string)

        buffer = self.text_view.get_buffer()
        if response_id == RESPONSE_FORWARD:
            buffer.search_forward(search_string, self)
        elif response_id == RESPONSE_BACKWARD:
            buffer.search_backward(search_string, self)

        dialog.destroy()

    def do_search(self, callback_action, widget):
        search_text = Gtk.TextView()
        dialog = Gtk.Dialog(_("Search"), self,
                            Gtk.DialogFlags.DESTROY_WITH_PARENT,
                            (_("Forward"), RESPONSE_FORWARD,
                             _("Backward"), RESPONSE_BACKWARD,
                             Gtk.STOCK_CANCEL, Gtk.ResponseType.NONE))
        dialog.vbox.pack_end(search_text, True, True, 0)
        dialog.buffer = search_text.get_buffer()
        dialog.connect("response", self.dialog_response_callback)

        search_text.show()
        search_text.grab_focus()
        dialog.show_all()

    def do_undo(self, callback_action, widget):
        buffer = self.text_view.get_buffer()
        if buffer.can_undo():
            buffer.undo()

    def do_redo(self, callback_action, widget):
        buffer = self.text_view.get_buffer()
        if buffer.can_redo():
            buffer.redo()
            
    #def do_about(self, callback_action, widget):
        #about = '''Shoebot is a pure Python graphics robot: 
#it takes a Python script as input, which describes a drawing process,
#and outputs a graphic in a common open standard format (SVG, PDF, PostScript, or PNG).\n
#It has a simple text editor GUI, and scripts can describe their own GUIs for
#controlling variables interactively.\n\n
        #Thanks to:\n
        #Ricardo Lafuente <r AT sollec.org>
        #Francesco Fantoni<francesco AT hv-a.com>
        #Dave Crossland <dave AT lab6.com>
        #Stuart Axon <stuaxo AT gmail.com>
        #Paulo Silva <nitrofurano AT gmail.com>
        #Tetsuya Saito <t2psyto AT gmail.com>\n
        #http://shoebot.net/\n
        #Version: 0.4-beta                
        #'''
        #self.console_error.write(about)            

    def on_url(self, d, link, data):
        import webbrowser
        webbrowser.open_new(data)
        
    def do_about(self, callback_action, widget):
        # about dialog
        dlg = Gtk.AboutDialog()
        self.website = "http://shoebot.net/"
        self.authors = ["Dave Crossland <dave AT lab6.com>", "est <electronixtar AT gmail.com>", "Francesco Fantoni <francesco AT hv-a.com>", "Paulo Silva <nitrofurano AT gmail.com>", "Pedro Angelo <pangelo AT virii-labs.org>", "Ricardo Lafuente <ricardo AT sollec.org>", "Stuart Axon <stuaxo2 AT yahoo.com>", "Tetsuya Saito <t2psyto AT gmail.com>"]
        Gtk.about_dialog_set_url_hook(self.on_url, self.website)
        dlg.set_version("0.4")
        dlg.set_name("shoebot")
        # TODO: add license text
        dlg.set_license("GPLv3")
        dlg.set_authors(self.authors)
        dlg.set_website(self.website)
        def close(w, res):
            if res == Gtk.ResponseType.CANCEL:
                    w.hide()
        dlg.connect("response", close)
        dlg.run()
            

    def init_menus(self):
        text_view = self.text_view
        direction = text_view.get_direction()
        wrap_mode = text_view.get_wrap_mode()
        menu_item = None

        ##if direction == Gtk.TextDirection.LTR:
        ##    menu_item = self.item_factory.get_widget("/Settings/Left-to-Right")
        ##elif direction == Gtk.TextDirection.RTL:
        ##    menu_item = self.item_factory.get_widget("/Settings/Right-to-Left")

        if menu_item:
            menu_item.activate()

        ##if wrap_mode == Gtk.WrapMode.NONE:
        ##    menu_item = self.item_factory.get_widget("/Settings/Wrap Off")
        ##elif wrap_mode == Gtk.WrapMode.WORD:
        ##    menu_item = self.item_factory.get_widget("/Settings/Wrap Words")
        ##elif wrap_mode == Gtk.WrapMode.CHAR:
        ##    menu_item = self.item_factory.get_widget("/Settings/Wrap Chars")

        ##if menu_item:
        ##    menu_item.activate()

    def close_view(self):
        TestText.views.remove(self)
        buffer = self.text_view.get_buffer()
        # buffer.unref()
        buffer.disconnect(self.bhid)
        self.text_view.destroy()
        del self.text_view
        self.text_view = None
        self.destroy()
        del self
        if not TestText.views:
            Gtk.main_quit()

    def check_close_view(self):
        buffer = self.text_view.get_buffer()
        if (buffer.refcount > 1 or
            buffer.check_buffer_saved()):
            self.close_view()

    def set_view_title(self):
        pretty_name = self.text_view.get_buffer().pretty_name()
        title = "Shoebot - " + pretty_name
        self.set_title(title)

    def cursor_set_callback(self, buffer, location, mark):

        # TODO: here should go the line syntax highlighter
        # 1. get buffer
        #      get modification state
        # 2. get line contents
        # 3. replace by pygmentised content
        #      revert to modification state
        pass

    def tab_stops_expose(self, widget, event):
        #print(self, widget, event)
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

        buffer = text_view.get_buffer()
        insert = buffer.get_iter_at_mark(buffer.get_insert())
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
            target.draw_line(text_view.style.fg_gc[text_view.state],
                             pos, 0, pos, 15)

        return True

    def get_lines(self, first_y, last_y, buffer_coords, numbers):
        text_view = self.text_view
        # Get iter at first y
        iter, top = text_view.get_line_at_y(first_y)

        # For each iter, get its location and add it to the arrays.
        # Stop when we pass last_y
        count = 0
        size = 0

        while not iter.is_end():
            y, height = text_view.get_line_yrange(iter)
            buffer_coords.append(y)
            line_num = iter.get_line()
            numbers.append(line_num)
            count += 1
            if (y + height) >= last_y:
                break
            iter.forward_line()

        return count

    def run_script(self, callback_action, widget):
        # get the buffer contents
        buffer = self.text_view.get_buffer()
        start, end = buffer.get_bounds()
        codestring = buffer.get_text(start, end)
        try:
            if buffer.filename:
                os.chdir(os.path.dirname(buffer.filename))
                
                
            bot = shoebot.create_bot(codestring, 'NodeBox', server=self.use_socketserver, show_vars=self.use_varwindow, window = True)
            self.sbot_window = bot._canvas.sink
            bot.run(codestring, run_forever = True, iterations = None)
        except ShoebotError, NameError:
            import traceback
            import sys

            errmsg = traceback.format_exc(limit=1)
            err = "Error in Shoebot script:\n %s" % (errmsg)
            dialog = Gtk.MessageDialog(self, Gtk.DialogFlags.MODAL,
                                       Gtk.MessageType.INFO,
                                       Gtk.ButtonsType.OK, err);
            result = dialog.run()
            dialog.destroy()
            return False

        # TODO: have a try/except that shows an error window         

class Stack(list):
    def __init__(self):
        list.__init__(self)

    def push(self, item):
        self.insert(-1, item)

    def pop(self):
        del self[0]

    def get(self):
        return self[0]


class TestText(object):
    untitled_serial = 1
    colormap = None
    active_window_stack = Stack()
    buffers = Stack()
    views = Stack()

    def __init__(self, filelist):
        view = View()
        self.active_window_stack.push(view)
        for fname in filelist:
            filename = os.path.abspath(fname)
            view.open_ok_func(filename)
        self.active_window_stack.pop()

    def main(self):
        Gtk.main()
        return 0


def main():
    testtext = TestText(sys.argv[1:])
    testtext.main()

if __name__ == "__main__":
    main()
