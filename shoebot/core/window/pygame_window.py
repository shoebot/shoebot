from shoebot.core.window import ShoebotWindow


class PyGameWindow(ShoebotWindow):
    """
    The pygame window uses the CairoRenderer for rendering.

    Right-click menus are not supported.
    """
    name = "pygame"
    can_show_right_click_menu = False


    def get_output(self):
        pass
    def update(self):
        pass

