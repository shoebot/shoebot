from gi.repository import Gtk

from shoebot.core.runner import ShoebotRunner
from shoebot.core.window.app import ShoebotApp
from shoebot.core.window.gtk4_window import Gtk4Window


class Gtk4App(ShoebotApp):
    """
    In
    """

    name = "gtk4"

    def __init__(self):
        self.window = Gtk4Window()
        runner = ShoebotRunner(self.get_output()

        super().__init__(runner)

    def get_output(self):
        """
        Returns the output object for the window.
        """
        return self.window.get_output()
    def run(self):
        """
        Runs the Gtk Main Loop until the app is quit.
        """
        self.window.show()

        # TODO: hook things up here (or in the window itself??)

        Gtk.main_loop()