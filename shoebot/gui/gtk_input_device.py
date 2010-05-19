from shoebot.core import InputDeviceMixin

class GtkInputDeviceMixin(InputDeviceMixin):
    def __init__(self):
        InputDeviceMixin.__init__(self)
    
    def _attach_gtk(self, widget):
        # necessary for catching keyboard events
        widget.set_flags(gtk.CAN_FOCUS)

        widget.add_events(gtk.gdk.BUTTON_PRESS_MASK |
            gtk.gdk.BUTTON_RELEASE_MASK |
            gtk.gdk.POINTER_MOTION_MASK |
            gtk.gdk.KEY_PRESS_MASK |
            gtk.gdk.KEY_RELEASE_MASK)
        widget.connect('button_press_event', self._gtk_mouse_button_press)
        widget.connect('button_release_event', self.gtk_mouse_button_release)
        widget.connect('motion_notify_event', self.gtk_mouse_move)

        widget.connect('key_press_event', self.gtk_key_press)
        widget.connect('key_release_event', self.gtk_key_release)

    def _gtk_mouse_button_press(self, widget, event):
        self._mouse_button_press_func()

    def _gtk_mouse_button_release(self, widget, event):
        self._mouse_button_release_func()

    def _gtk_mouse_move(self, widget, event):
        self._mouse_move_func()

    def _gtk_key_press(self, widget, event):
        self._key_press_func()

    def _gtk_key_release(self, widget, event):
        self._key_release_func()


