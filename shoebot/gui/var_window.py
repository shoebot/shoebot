#!/usr/bin/env python2
import gtk
import os.path
import sys

NUMBER = 1
TEXT = 2
BOOLEAN = 3
BUTTON = 4

ICON_FILE = next(f for f in ['/usr/share/shoebot/shoebot-ide.png', '/usr/local/share/pixmaps/shoebot-ide.png', os.path.join(sys.prefix, 'share', 'pixmaps', 'shoebot-ide.png')] if os.path.exists(f))

class VarWindow(object):
    def __init__(self, parent, bot, title = None):
        self.parent = parent
        self.bot = bot

        self.window = gtk.Window()
        self.window.set_destroy_with_parent(True)
        self.window.connect("destroy", self.do_quit)
        vbox = gtk.VBox(homogeneous=True, spacing=20)

        # set up sliders
        self.widgets = {}

        for item in sorted(bot._vars.values()):
            if item.type is NUMBER:
                self.widgets[item.name] = self.add_number(vbox, item)
            elif item.type is TEXT:
                self.widgets[item.name] = self.add_text(vbox, item)
            elif item.type is BOOLEAN:
                self.widgets[item.name] = self.add_boolean(vbox, item)
            elif item.type is BUTTON:
                self.widgets[item.name] = self.add_button(vbox, item)
            else:
                raise ValueError('Unknown variable type.')

        self.window.add(vbox)
        self.window.set_size_request(400,35*len(self.widgets.keys()))
        self.window.show_all()

        if title:
            self.window.set_title(title)
        ## gtk.main()

    def add_number(self, container, v):
        # create a slider for each var
        sliderbox = gtk.HBox(homogeneous=False, spacing=0)
        label = gtk.Label(v.name)
        sliderbox.pack_start(label, False, True, 20)

        if v.max - v.min > 2:
            adj = gtk.Adjustment(v.value, v.min, v.max, .1, 2, 1)
        else:
            adj = gtk.Adjustment(v.value, v.min, v.max, .1)
        adj.connect("value_changed", self.widget_changed, v)
        hscale = gtk.HScale(adj)
        hscale.set_value_pos(gtk.POS_RIGHT)
        hscale.set_value(v.value)
        sliderbox.pack_start(hscale, True, True, 0)
        container.pack_start(sliderbox, True, True, 0)

        return hscale

    def add_text(self, container, v):
        textcontainer = gtk.HBox(homogeneous=False, spacing=0)
        label = gtk.Label(v.name)
        textcontainer.pack_start(label, False, True, 20)

        entry = gtk.Entry(max=0)
        entry.set_text(v.value)
        entry.connect("changed", self.widget_changed, v)
        textcontainer.pack_start(entry, True, True, 0)
        container.pack_start(textcontainer, True, True, 0)

        return entry

    def add_boolean(self, container, v):
        buttoncontainer = gtk.HBox(homogeneous=False, spacing=0)
        button = gtk.CheckButton(label=v.name)
        button.set_active(v.value)
        # we send the state of the button to the callback method
        button.connect("toggled", self.widget_changed, v)

        buttoncontainer.pack_start(button, True, True, 0)
        container.pack_start(buttoncontainer, True, True, 0)

        return button


    def add_button(self, container, v):
        buttoncontainer = gtk.HBox(homogeneous=False, spacing=0)
        # in buttons, the varname is the function, so we use __name__

        func_name = v.name

        def call_func(*args):
            func = self.bot._namespace[func_name]
            func()

        button = gtk.Button(label=v.name)
        button.connect("clicked", call_func, None)
        buttoncontainer.pack_start(button, True, True, 0)
        container.pack_start(buttoncontainer, True, True, 0)

        return button


    def do_quit(self, widget):
        pass

    def update_var(self, name, value):
        """
        :return: success, err_msg_if_failed
        """
        widget = self.widgets.get(name)
        if widget is None:
            return False, 'No widget found matching, {}'.format(name)

        try:
            if isinstance(widget, gtk.CheckButton):
                widget.set_active(value)
                return True, widget.get_active()
            elif isinstance(widget, gtk.Entry):
                widget.set_text(value)
                return True, widget.get_text()
            else:
                widget.set_value(value)
                return True, widget.get_value()
        except Exception as e:
            return False, str(e)

    def widget_changed(self, widget, v):
        ''' Called when a slider is adjusted. '''
        # set the appropriate bot var
        if v.type is NUMBER:
            self.bot._namespace[v.name] = widget.value
            self.bot._vars[v.name].value = widget.value  ## Not sure if this is how to do this - stu
        elif v.type is BOOLEAN:
            self.bot._namespace[v.name] = widget.get_active()
            self.bot._vars[v.name].value = widget.get_active()  ## Not sure if this is how to do this - stu
        elif v.type is TEXT:
            self.bot._namespace[v.name] = widget.get_text()
            self.bot._vars[v.name].value = widget.get_text()  ## Not sure if this is how to do this - stu


