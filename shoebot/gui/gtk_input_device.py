from shoebot.core.backend import gi

from gi.repository import Gdk, Gtk
from shoebot.core import InputDeviceMixin


class GtkInputDeviceMixin(InputDeviceMixin):

    def __init__(self, **kwargs):
        InputDeviceMixin.__init__(self, **kwargs)
        self.scale_x = 1.0
        self.scale_y = 1.0

    def attach_gtk(self, widget):
        # necessary for catching keyboard events
        widget.set_can_focus(True)

        widget.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.KEY_PRESS_MASK |
            Gdk.EventMask.KEY_RELEASE_MASK)
        widget.connect('button_press_event', self.gtk_mouse_button_down)
        widget.connect('button_release_event', self.gtk_mouse_button_up)
        widget.connect('motion_notify_event', self.gtk_mouse_pointer_moved)

        widget.connect('key_press_event', self.gtk_key_pressed)
        widget.connect('key_release_event', self.gtk_key_released)

    def gtk_mouse_button_down(self, widget, event):
        self.mouse_button_down(event.button)

    def gtk_mouse_button_up(self, widget, event):
        self.mouse_button_up(event.button)

    def gtk_mouse_pointer_moved(self, widget, event):
        self.mouse_pointer_moved(event.x / self.scale_x, event.y / self.scale_y)

    def get_mapped_key(self, keyval):
        # Horrible hack to support key values used in beziereditor2 from nodebox
        #
        # Values are from beziereditor2 example, probably mac values - probably
        # should be a way of toggling this hack
        if keyval == Gdk.KEY_Tab:
            keyval = 48
        elif keyval == Gdk.KEY_Escape:
            keyval = 53
        return keyval

    def gtk_key_pressed(self, widget, event):
        keyval = self.get_mapped_key(event.keyval)
        self.keys_pressed.add(keyval)
        self.key_pressed(event.string, keyval)

    def gtk_key_released(self, widget, event):
        keyval = self.get_mapped_key(event.keyval)
        self.keys_pressed.discard(keyval)
        self.key_released(event.string, keyval)

    def get_key_map(self):
        '''
        Return a dict in the form of

        SHOEBOT_KEY_NAME, GTK_VALUE

        Shoebot key names look like KEY_LEFT, whereas Gdk uses KEY_Left
        - Shoebot key names are derived from Nodebox 1, which was a mac
          app.
        '''
        kdict = {}
        for gdk_name in dir(Gdk):
            nb_name = gdk_name.upper()
            kdict[nb_name] = getattr(Gdk, gdk_name)
        return kdict


