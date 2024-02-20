import abc


class ShoebotApp(metaclass=abc.ABCMeta):
    """
    App sets up the GUI for Shoebot.
    """

    name = None
    """Name of the app, used to select the app type from the command line."""

    def __init__(self, runner):
        self.runner = runner
        self.window = self.get_window()

    @abc.abstractmethod
    def run(self):
        pass