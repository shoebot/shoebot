import sys
import shoebot
import locale, gettext
import math as _math
import cairo

APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
#gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext

CENTER = 'center'

TOP_LEFT = 1
BOTTOM_LEFT = 2

class Canvas:
    ''' Abstract canvas class '''
    def __init__(self):
        self.fill = (0.5, 0.5, 0.5)
        self.stroke = None
        self.strokewidth = 1
        self.background = (1, 1, 1)
        self.transform = cairo.Matrix()
        self.DEFAULT_MODE = CENTER

    def initial_drawqueue(self):
        '''
        Override to create use special kinds of draw queue
        '''
        return DrawQueue()
    
    def initial_transform(self):
        '''
        Must be overriden to create initial transform matrix
        '''
        pass

    def reset_canvas(self):
        self.reset_transform()
        self.reset_drawqueue()

    def size_or_default(self):
        '''
        If size is not set, otherwise set size to DEFAULT_SIZE
        and return it.

        This means, only the first call to size() is valid.
        '''
        if not self.size:
            self.size = DEFAULT_SIZE
        return self.size

    def set_size(self, size):
        '''
        Size is only set the first time it is called
        
        Size that is set is returned
        '''
        if self.size is None:
            self.size = size
            return size
        else:
            return self.size
    
    def get_width(self):
        if self.size != None:
            return self.size[0]
        else:
            return self.DEFAULT_SIZE[0]

    def get_height(self):
        if self.size != None:
            return self.size[1]
        else:
            return self.DEFAULT_SIZE[1]

    width = property(get_width)
    height = property(get_height)

