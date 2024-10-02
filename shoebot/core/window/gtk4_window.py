from gi.repository import Gtk
from .window import ShoebotWindow


class Gtk4Window(ShoebotWindow, Gtk.Window):
    """
    Gtk4 Window uses the CairoRenderer for rendering.
    """
    name = "gtk4"
    can_show_right_click_menu = True

    def __init__(self):
        pass