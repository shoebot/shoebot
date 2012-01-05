class InputDeviceMixin(object):
    SUPPORTED_CALLBACKS = 'key_pressed', 'key_released', 'mouse_button_down', 'mouse_button_up', 'mouse_pointer_moved'

    def __init__(self, **kwargs):
        def nop(*args):
            pass

        for name in self.SUPPORTED_CALLBACKS:
            func = kwargs.get(name, nop)
            setattr(self, name, func)

        # Implementation needs to manipulate keys_pressed, mouse_buttons_down
        self.keys_pressed = set()
        self.mouse_buttons_down = set()


    def set_callbacks(self, **kwargs):
        ''' Set callbacks for input events '''
        for name in self.SUPPORTED_CALLBACKS:
            func = kwargs.get(name, getattr(self, name))
            setattr(self, name, func)

    def get_key_down(self):
        ''' Return True if any key is pressed '''
        return bool(self.keys_pressed)

    def get_mouse_down(self):
        ''' Return True if any mouse button is pressed '''
        return bool(self.mouse_buttons_down)
        
    def get_key_map(self):
        return {}

    key_down = property(get_key_down)
    mouse_down = property(get_mouse_down)

            

