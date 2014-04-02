from collections import namedtuple
import queue
import time
from distutils.spawn import find_executable as which
import os
import subprocess
from urllib.request import pathname2url

from gi.repository import Gtk, Gio, GObject, Gedit, Pango
import re
from gettext import gettext as _


def find_example_dir():
    """
    Find examples dir .. a little bit ugly..

    # TODO - Move to extensions lib
    """

    # Needs to run in same python env as shoebot (may be different to gedits)
    cmd = ["python", "-c", "import sys; print '{}/share/shoebot/examples/'.format(sys.prefix)"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, errors = p.communicate()
    if errors:
        print('Could not find shoebot examples')
        print('Errors: {}'.format(errors))
        return None
    else:
        examples_dir = output.decode('utf-8').strip()
        if os.path.isdir(examples_dir):
            return examples_dir
        else:
            print('Could not find shoebot examples at {}'.format(examples_dir))


if not which('sbot'):
    print('Shoebot executable not found.')

_example_dir = find_example_dir()

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


def get_example_dir():
    return _example_dir


def make_readable_filename(fn):
    return os.path.splitext(fn)[0].replace('_', ' ').capitalize()


def examples_menu(root_dir=None, depth=0):
    """
    :return: xml for menu, [(bot_action, label), ...], [(menu_action, label), ...]
    """
    examples_dir = get_example_dir()
    if not examples_dir:
        return "", [], []
    
    root_dir = root_dir or examples_dir

    file_tmpl = '<menuitem name="{name}" action="{action}"/>'
    dir_tmpl = '<menu name="{name}" action="{action}">{menu}</menu>'

    file_actions = []
    submenu_actions = []
    
    xml = ""

    for fn in sorted(os.listdir(root_dir)):
        path = os.path.join(root_dir, fn)
        rel_path = path[len(examples_dir):]
        if os.path.isdir(path):            
            action = 'ShoebotExampleMenu {}'.format(rel_path)
            label = fn.capitalize()

            sm_xml, sm_file_actions, sm_menu_actions = examples_menu(os.path.join(root_dir, fn), depth+1)

            submenu_actions.extend(sm_menu_actions)
            file_actions.extend(sm_file_actions)
            submenu_actions.append((action, label))
            xml += dir_tmpl.format(name=fn, action=action, menu=sm_xml)
        elif os.path.splitext(path)[1] in ['.bot', '.py'] and not fn.startswith('_'):
            action = 'ShoebotExampleOpen {}'.format(rel_path)
            label = make_readable_filename(fn)

            xml += file_tmpl.format(name=fn, action=action)
            file_actions.append((action, label))

    return xml, file_actions, submenu_actions

examples_xml, example_actions, submenu_actions = examples_menu()

ui_str = """
<ui>
  <menubar name="MenuBar">
    <menu name="ShoebotMenu" action="Shoebot">
      <placeholder name="ShoebotOps_1">
        <menuitem name="Run in Shoebot" action="ShoebotRun"/>
            <separator/>
                 <menu name="ShoebotExampleMenu" action="ShoebotOpenExampleMenu">
                    {}
                </menu>
        <separator/>
        <menuitem name="Enable Socket Server" action="ShoebotSocket"/>
        <menuitem name="Show Variables Window" action="ShoebotVarWindow"/>
        <menuitem name="Go Fullscreen" action="ShoebotFullscreen"/>
      </placeholder>
    </menu>
  </menubar>
</ui>
""".format(examples_xml) # Splice in the examples menu


def get_child_by_name(parent, name):
    """
    Iterate through a gtk container, `parent`, 
    and return the widget with the name `name`.
    """
    # http://stackoverflow.com/questions/2072976/access-to-widget-in-gtk
    def iterate_children(widget, name):
        if widget.get_name() == name:
            return widget
        try:
            for w in widget.get_children():
                result = iterate_children(w, name)
                if result is not None:
                    return result
                else:
                    continue
        except AttributeError:
            pass
    return iterate_children(parent, name)


import threading
import subprocess


class AsynchronousFileReader(threading.Thread):
    '''
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.
    '''

    def __init__(self, fd, q):
        assert isinstance(q, queue.Queue)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = q

    def run(self):
        '''The body of the tread: read lines and put them on the queue.'''
        try:
            for line in iter(self._fd.readline, False):
                self._queue.put(line)
                if not line:
                    time.sleep(0.1)
        except ValueError:  # This can happen if we are closed during readline - TODO - better fix.
            if not self._fd.closed:
                raise

    def eof(self):
        '''Check whether there is no more content to expect.'''
        return (not self.is_alive()) and self._queue.empty() or self._fd.closed



#class ShoebotThread(threading.Thread):
#    ''' 
#    Run shoebot in seperate thread
#    '''
#    # http://stackoverflow.com/questions/984941/python-subprocess-popen-from-a-thread
#    def __init__(self, cmd, textbuffer, workingdir = None):
#        self.cmd = cmd
#        self.textbuffer = textbuffer
#        self.workingdir = workingdir
#        self.stdout = None
#        self.stderr = None
#        threading.Thread.__init__(self)

#    def run(self):
#        textbuffer = self.textbuffer
#        
#        try:
#            proc = subprocess.Popen(self.cmd,
#                                 shell=False,
#                                 stdout=subprocess.PIPE,
#                                 stderr=subprocess.PIPE,
#                                 cwd=self.workingdir)
#        except OSError as e:
#            if e.errno == 2:
#                textbuffer.insert(textbuffer.get_end_iter(), 'Shoebot executable sbot not found in path.')
#            else:
#                textbuffer.insert(textbuffer.get_end_iter(), str(e))
#            return
#            

#        textbuffer.set_text('')
#        #self.stdout, self.stderr = proc.communicate()

#        panel = Gedit.App.get_default().get_active_window().get_bottom_panel()
#        visible = panel.get_property("visible")
#        while proc.poll() is None:
#            line = proc.stdout.readline()
#            if line:
#                # Process output here
#                textbuffer.insert(textbuffer.get_end_iter(), line)
#                while Gtk.events_pending():
#                            Gtk.main_iteration()
#                if not visible:
#                    panel.set_property("visible", True)
#        if proc.returncode != 0:
#            panel.set_property("visible", True)


class ShoebotProcess:
    def __init__(self, code, use_socketserver, show_varwindow, use_fullscreen, title, cwd=None):
        command = ['sbot', '-w', '-t%s - Shoebot on gedit' % title]

        if use_socketserver:
            command.append('-s')

        if not show_varwindow:
            command.append('-dv')

        if use_fullscreen:
            command.append('-f')

        command.append(code)

        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, close_fds=True, shell=False, cwd=cwd)

        # Launch the asynchronous readers of the process' stdout and stderr.
        self.stdout_queue = queue.Queue()
        self.stdout_reader = AsynchronousFileReader(self.process.stdout, self.stdout_queue)
        self.stdout_reader.start()
        self.stderr_queue = queue.Queue()
        self.stderr_reader = AsynchronousFileReader(self.process.stderr, self.stderr_queue)
        self.stderr_reader.start()


    def _update_ui_text(self, output_widget):
        textbuffer = output_widget.get_buffer()
        while False == (self.stdout_queue.empty() and self.stderr_queue.empty()):
            if not self.stdout_queue.empty():
                line = self.stdout_queue.get().decode('utf-8')
                textbuffer.insert(textbuffer.get_end_iter(), line)

            if not self.stderr_queue.empty():
                line = self.stderr_queue.get().decode('utf-8')
                textbuffer.insert(textbuffer.get_end_iter(), line)
        #else:
        output_widget.scroll_to_iter(textbuffer.get_end_iter(), 0.0, True, 0.0, 0.0)
        while Gtk.events_pending():
            Gtk.main_iteration()

    def update_shoebot(self, output_widget):
        """
        :param textbuffer: Gtk textbuffer to append shoebot output to.
        :output_widget: Gtk widget containing the output
        :return: True if shoebot still running, False if terminated.
        Send any new shoebot output to a textbuffer.
        """
        self._update_ui_text(output_widget)

        if self.process.poll() is not None:
            # Close subprocess' file descriptors.
            self._update_ui_text(output_widget)
            self.process.stdout.close()
            self.process.stderr.close()
            return False

        result = not (self.stdout_reader.eof() or self.stderr_reader.eof())
        return result


class ShoebotWindowHelper:
    def __init__(self, plugin, window):
        self.example_bots = {}

        self.window = window
        panel = window.get_bottom_panel()
        self.output_widget = get_child_by_name(panel, 'shoebot-output')

        self.plugin = plugin
        self.insert_menu()
        self.shoebot_window = None
        self.id_name = 'ShoebotPluginID'

        self.use_socketserver = False
        self.show_varwindow = True
        self.use_fullscreen = False

        self.started = False
        self.shoebot_thread = None
        
        for view in self.window.get_views():
            self.connect_view(view)

        self.bot = None

    
    def deactivate(self):
        self.remove_menu()
        self.window = None
        self.plugin = None
        self.action_group = None
        del self.shoebot_window

    def insert_menu(self):
        manager = self.window.get_ui_manager()
        self.action_group = Gtk.ActionGroup("ShoebotPluginActions")
        self.action_group.add_actions([
            ("Shoebot", None, _("Shoe_bot"), None, _("Shoebot"), None),
            ("ShoebotRun", None, _("Run in Shoebot"), '<control>R', _("Run in Shoebot"), self.on_run_activate),
            ('ShoebotOpenExampleMenu', None, _('E_xamples'), None, None, None)
            ])
        

        for action, label in example_actions:
            self.action_group.add_actions([(action, None, (label), None, None, self.on_open_example)])

        for action, label in submenu_actions:
            self.action_group.add_actions([(action, None, (label), None, None, None)])

        self.action_group.add_toggle_actions([
            ("ShoebotSocket", None, _("Enable Socket Server"), '<control><alt>S', _("Enable Socket Server"), self.toggle_socket_server, False),
            ("ShoebotVarWindow", None, _("Show Variables Window"), '<control><alt>V', _("Show Variables Window"), self.toggle_var_window, False),
            ("ShoebotFullscreen", None, _("Go Fullscreen"), '<control><alt>F', _("Go Fullscreen"), self.toggle_fullscreen, False),
            ])
        manager.insert_action_group(self.action_group)
        
        self.ui_id = manager.add_ui_from_string(ui_str)
        manager.ensure_update()

    def on_open_example(self, action):
        example_dir = get_example_dir()
        filename = os.path.join(example_dir, action.get_name()[len('ShoebotOpenExample'):].strip())
        
        uri      = "file:///" + pathname2url(filename)
        gio_file = Gio.file_new_for_uri(uri)
        self.window.create_tab_from_location(
            gio_file,
            None,  # encoding
            0,
            0,     # column
            False, # Do not create an empty file
            True)  # Switch to the tab


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

        title = doc.get_short_name_for_display()
        cwd = os.path.dirname(doc.get_uri_for_display()) or None

        start, end = doc.get_bounds()
        code = doc.get_text(start, end, False)
        if not code:
            return False

        textbuffer = self.output_widget.get_buffer()
        textbuffer.set_text('')
        while Gtk.events_pending():
           Gtk.main_iteration()


        self.bot = ShoebotProcess(code, self.use_socketserver, self.show_varwindow, self.use_fullscreen, title, cwd=cwd)

        GObject.idle_add(self.update_shoebot)


    def update_shoebot(self):
        if self.bot:
            running = self.bot.update_shoebot(self.output_widget)

            if not running:
                 return False
        return True

    
    def toggle_socket_server(self, action):
        self.use_socketserver = action.get_active()
    def toggle_var_window(self, action):
        self.show_varwindow = action.get_active()
    def toggle_fullscreen(self, action):
        #no full screen for you!
        self.use_fullscreen = False
        #self.use_fullscreen = action.get_active()
        
    # Right-click menu items (for quicktorials)

    def connect_view(self, view):
        # taken from gedit-plugins-python-openuricontextmenu
        #handler_id = view.connect('populate-popup', self.on_view_populate_popup)
        #view.set_data(self.id_name, [handler_id])

        pass


    def on_view_populate_popup(self, view, menu):
        # taken from gedit-plugins-python-openuricontextmenu
        doc = view.get_buffer()
        win = view.get_window(Gtk.TextWindowType.TEXT)
        ptr_window, x, y, mod = win.get_pointer()
        x, y = view.window_to_buffer_coords(Gtk.TextWindowType.TEXT, x, y) 

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

        word = unicode(doc.get_text(start, insert, False))

        if len(word) == 0:
            return True

        word = self.validate_word(word)
        if not word:
            return True

        open_quicktorial_item = Gtk.ImageMenuItem(_("Know more about '%s'") % (word))
        open_quicktorial_item.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, Gtk.IconSize.MENU))
        open_quicktorial_item.connect('activate', self.on_open_quicktorial, word)
        open_quicktorial_item.show()

        separator = Gtk.SeparatorMenuItem()
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

class ShoebotPlugin(GObject.Object, Gedit.WindowActivatable):
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
        self.instances = {}
        self.tempfiles = []

    def do_activate(self):
        self.text = Gtk.TextView()
        self.text.set_editable(False)
        fontdesc = Pango.FontDescription("Monospace")
        self.text.modify_font(fontdesc)
        self.text.set_name('shoebot-output')
        self.panel = self.window.get_bottom_panel()

        image = Gtk.Image()
        image.set_from_stock(Gtk.STOCK_EXECUTE, Gtk.IconSize.BUTTON)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self.text)
        scrolled_window.show_all()
        
        self.panel.add_item(scrolled_window, 'Shoebot', 'Shoebot', image)   
        self.output_widget = scrolled_window

        self.instances[self.window] = ShoebotWindowHelper(self, self.window)


    def do_deactivate(self):
        self.panel.remove_item(self.text)
        self.instances[self.window].deactivate()
        del self.instances[self.window]
        for tfilename in self.tempfiles:
            os.remove(tfilename)

        self.panel.remove_item(self.output_widget)


    def do_update_state(self):
        self.instances[self.window].update_ui()


