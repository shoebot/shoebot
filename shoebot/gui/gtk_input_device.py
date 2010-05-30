import gtk

from shoebot.core import InputDeviceMixin

class GtkInputDeviceMixin(InputDeviceMixin):
    def __init__(self, **kwargs):
        InputDeviceMixin.__init__(self, **kwargs)
    
    def attach_gtk(self, widget):
        # necessary for catching keyboard events
        widget.set_flags(gtk.CAN_FOCUS)

        widget.add_events(gtk.gdk.BUTTON_PRESS_MASK |
            gtk.gdk.BUTTON_RELEASE_MASK |
            gtk.gdk.POINTER_MOTION_MASK |
            gtk.gdk.KEY_PRESS_MASK |
            gtk.gdk.KEY_RELEASE_MASK)
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
        self.mouse_pointer_moved(event.x, event.y)

    def gtk_key_pressed(self, widget, event):
        self.keys_pressed.add(event.keyval)
        self.key_pressed(event.string, event.keyval)

    def gtk_key_released(self, widget, event):
        self.keys_pressed.discard(event.keyval)
        self.key_released(event.string, event.keyval)


