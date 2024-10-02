class ShoebotWindow:
    """
    Subclasses of Shoebot Window are used to display Shoebot in a window.
    """

    name = None
    """Name of the window, used to select the window type from the command line."""

    can_show_right_click_menu = False
    """Feature flag: whether the window can show a right-click menu."""

    def __init__(self, width=None, height=None, fullscreen=False, title=None):
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        self.title = f"Shoebot [{self.name}]" if title is None else title
