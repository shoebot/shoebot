"""
Gtk3 support for shoebot in editors and IDEs
"""

import itertools
import os
from shoebotit import ide_utils
from gi.repository import Gio, Gtk, GLib


MENU_UI = """
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
"""


def examples_menu(root_dir=None, depth=0):
    """
    :return: xml for menu, [(bot_action, label), ...], [(menu_action, label), ...]
    """
    examples_dir = ide_utils.get_example_dir()
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
            label = ide_utils.make_readable_filename(fn)

            xml += file_tmpl.format(name=fn, action=action)
            file_actions.append((action, label))

    return xml, file_actions, submenu_actions


def gedit3_menu(xml):
    """
    Build XML for GEDIT3 Menus.

    Pass in the xml returned by example_menu
    """
    return MENU_UI.format(xml) # Splice in the examples menu


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



def venv_has_script(script):
    """
    :param script: script to look for in bin folder
    """
    def f(venv):
        path=os.path.join(venv, 'bin', script)
        if os.path.isfile(path):
            return True
    return f


def is_venv(directory, executable='python'):
    """
    :param directory: base directory of python environment
    """
    path=os.path.join(directory, 'bin', executable)
    return os.path.isfile(path)


def vw_envs(filter=None):
    """
    :return: python environments in ~/.virtualenvs

    :param filter: if this returns False the venv will be ignored

    >>> vw_envs(filter=venv_has_script('pip'))
    """
    vw_root=os.path.abspath(os.path.expanduser(os.path.expandvars('~/.virtualenvs')))
    venvs=[]
    for directory in os.listdir(vw_root):
        venv=os.path.join(vw_root, directory)
        if os.path.isdir(os.path.join(venv)):
            if filter and not filter(venv):
                continue
            venvs.append(venv)
    return sorted(venvs)


class VirtualEnvChooser(Gtk.Box):
    """
    Allow the user to choose a virtualenv.

    :param gsetting: save settings to this prefix
    """
    def __init__(self, gsettings=None):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        
        self.gsettings=gsettings
        if gsettings:
            current_virtualenv = self.gsettings.get_string('current-virtualenv')
            self.user_envs=sorted(gsettings.get_value('virtualenvs'))
        else:
            current_virtualenv = None
            self.user_envs=[]

        virtualenv_store = Gtk.ListStore(str, str)
        virtualenv_combo = Gtk.ComboBox.new_with_model(virtualenv_store)
        
        sys_envs=[ ['SYSTEM', 'System'], ['python', 'Default'] ]

        all_envs = itertools.chain( 
            sys_envs,
            [ [os.path.basename(venv), venv] for venv in vw_envs(filter=venv_has_script('sbot')) ],
            [ [os.path.basename(venv), venv] for venv in self.user_envs ]
        )
        
        for i, (name, venv) in enumerate(all_envs):
            virtualenv_store.append([os.path.basename(venv), venv])

            if gsettings and venv == current_virtualenv:
                virtualenv_combo.set_active(i)

        virtualenv_combo.connect("changed", self.on_virtualenv_combo_changed)
        virtualenv_combo.set_entry_text_column(1)
        renderer_text = Gtk.CellRendererText()
        virtualenv_combo.pack_start(renderer_text, True)
        virtualenv_combo.add_attribute(renderer_text, "text", 0)

        self.virtualenv_combo=virtualenv_combo
        self.virtualenv_store=virtualenv_store
        
        self.pack_start(virtualenv_combo, False, False, True)

        add_button = Gtk.Button(None, image=Gtk.Image(stock=Gtk.STOCK_ADD))
        add_button.connect("clicked", self.on_add_virtualenv)
        self.pack_start(add_button, True, True, 0)

        remove_button = Gtk.Button(None, image=Gtk.Image(stock=Gtk.STOCK_REMOVE))
        remove_button.connect("clicked", self.on_remove_virtualenv)
        remove_button.set_sensitive(current_virtualenv in self.user_envs)

        self.pack_start(remove_button, True, True, 0)
        self.remove_button=remove_button


    def on_virtualenv_combo_changed(self, combo):
        # TODO - Name these
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            name, venv = model[tree_iter][:2]
            if self.gsettings:
                self.gsettings.set_string('current-virtualenv', venv)
            
            self.remove_button.set_sensitive(venv in self.user_envs)
        else:
            entry = combo.get_child()
            print("Entered: %s" % entry.get_text())

    def on_remove_virtualenv(self, widget):
        index=self.virtualenv_combo.get_active()
        item=self.virtualenv_store[index]
        venv=item[1]
        
        self.virtualenv_combo.set_active(0)
        
        # Use gtk iterator to delete item
        _iter=self.virtualenv_store.get_iter(index)
        self.virtualenv_store.remove(_iter)

        if venv in self.user_envs:
            self.user_envs.remove(venv)
            self.gsettings.set_value('virtualenvs', GLib.Variant('as', self.user_envs))

    def on_add_virtualenv(self, widget):
        # TODO - complete this and remove print statements
        dialog = Gtk.FileChooserDialog("Please choose a virtualenv", widget.get_toplevel(),
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             "Select", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:            
            print("Select clicked")
            print("Folder selected: " + dialog.get_filename())
            folder=dialog.get_filename()
            if is_venv(folder):
                self.add_virtualenv(folder)
                dialog.destroy()
            else:
                print('Not a venv')
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
            dialog.destroy()

    def add_virtualenv(self, venv):
        self.virtualenv_store.append([os.path.basename(venv), venv])
        self.user_envs.append(venv)
        self.gsettings.set_value('virtualenvs', GLib.Variant('as', self.user_envs))
        self.virtualenv_combo.set_active(len(self.virtualenv_store)-1)



class ShoebotPreferences(Gtk.Box):
    """
    Allow the user to choose a virtualenv.
    """
    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=2)

        label = Gtk.Label("Python Environment")
        self.add(label)
        self.pack_start(label, True, True, 0)

        gsettings=self.load_gsettings()
        virtualenv_chooser=VirtualEnvChooser(gsettings=gsettings)
        self.add(virtualenv_chooser)


    def load_gsettings(self):
        schema_id="apps.shoebot.gedit"
        path="/apps/shoebot/gedit/"

        here=os.path.dirname(os.path.abspath(__file__))
        #schema_dir=os.path.abspath(os.path.join(here, '../../gedit3-plugin'))
        schema_dir=here
        schema_source = Gio.SettingsSchemaSource.new_from_directory(schema_dir,
                        Gio.SettingsSchemaSource.get_default(), False)
        schema = Gio.SettingsSchemaSource.lookup(schema_source, schema_id,False)
        if not schema:
            raise Exception("Cannot get GSettings  schema")
        settings = Gio.Settings.new_full(schema, None, path)
        return settings




if __name__=='__main__':
    # Debug - create the configuration
    win = Gtk.Window()
    win.add(ShoebotPreferences())
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()

