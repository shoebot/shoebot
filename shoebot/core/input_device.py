import gtk

class InputDeviceMixin(object):
    def __init__(self, **kwargs):
        def nop(**kwargs):
            pass
        self._key_press_func = kwargs.get('key_pressed', nop)
        self._key_release_func = kwargs.get('key_released', nop)
        self._mouse_button_press = kwargs.get('mouse_button_press', nop)
        self._mouse_button_release = kwargs.get('mouse_button_release', nop)
        self._mouse_pointer_move = kwargs.get('mouse_pointer_move', nop)


