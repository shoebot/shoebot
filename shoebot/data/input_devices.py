import gtk

class PointingDevice:
    """
    Base class for pointing device, contains only dummy values
    """
    def __init__(self):
        self.x = 0
        self.y = 0
        self.buttons_pressed = set()
        self.listeners = []
    
    def add_listener(self, listener):
        self.listeners.append(listener)
    
    def get_button_down(self):
        """
        Return true if any of the buttons are pressed
        """
        return bool(self.buttons_pressed)
    
    def pointer_moved(self, x, y):
        self.x = x
        self.y = y
        for listener in self.listeners:
            listener.pointer_moved(self)
            
            
    def button_pressed(self, button):
        self.buttons_pressed.add(button)
        for listener in self.listeners:
            listener.mouse_down(self)
        
    def button_released(self, button):
        self.buttons_pressed.remove(button)
        for listener in self.listeners:
            listener.mouse_up(self)

    button_down = property(get_button_down)
         

class GTKPointer(PointingDevice):
    def __init__(self):
        PointingDevice.__init__(self)
        
    def gtk_motion_event(self, widget, event):
        self.pointer_moved(event.x, event.y)
        
    def gtk_button_press_event(self, widget, event):
        self.button_pressed(event.button)
        
    def gtk_button_release_event(self, widget, event):
        self.button_released(event.button)


class KeyStateHandler:
    '''
    Base class for the state of the keyboard
    '''
    def __init__(self):
        self.key = None
        self.keycode = None
        self.keys_pressed = set()
        self.listeners = []
        
    def add_listener(self, listener):
        self.listeners.append(listener)
        
    def get_key_down(self):
        ''' Return True if any key is pressed '''
        return bool(self.keys_pressed)
    
    def key_pressed(self, key, keycode):
        self.key = key
        self.keycode = keycode
        self.keys_pressed.add(keycode)
        for listener in self.listeners:
            listener.key_down(self)
            
    def key_released(self, keycode):
        self.keys_pressed.discard(keycode)
        for listener in self.listeners:
            listener.key_up(self)
    
    key_down = property(get_key_down)


class GTKKeyStateHandler(KeyStateHandler):
    def __init__(self):
        KeyStateHandler.__init__(self)
        
    def gtk_key_press_event(self, widget, event):
        if event.type == gtk.gdk.KEY_PRESS:
            self.key_pressed(event.string, event.keyval)
        else:
            self.key_released(event.keyval)

class PointerGroup(PointingDevice):
    """
    Contains a set of pointers
    """
    pointers = None
    
    def __init__(self):
        PointingDevice.__init__(self)
        self.pointers = []
    
    def button_down(self):
        """
        Return True if any button on any pointer is pressed
        """
        for pointer in self.pointers:
            if pointer.button_down:
                return True
        return False
    
    def average_x(self):
        x = 0
        for pointer in pointers:
            x += pointer.x
        else:
            return x / len(pointers)
        return 0
        
    def average_y(self):
        y = 0
        for pointer in pointers:
            y += pointer.y
        else:
            return y / len(pointers)
        return 0

    def add_pointer(pointer):
        pointers.append(pointer)
    
    x = property(average_x)
    y = property(average_y)


