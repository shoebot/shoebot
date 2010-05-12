import sys, os
import shoebot

from shoebot import ShoebotError
from shoebot.data import BezierPath, EndClip, Color, Text, Variable, \
                         Image, ClippingPath, Transform

from glob import glob
import random as r
import traceback

import locale, gettext
APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
#gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext

import sys
LIB_DIR = sys.prefix + '/share/shoebot/lib'
sys.path.append(LIB_DIR)

TOP_LEFT = 1
BOTTOM_LEFT = 2

class Bot:
    '''
    A Bot is an interface to receive user commands (through scripts or direct
    calls) and pass them to a canvas for drawing.
    '''
    
    RGB = "rgb"
    HSB = "hsb"

    LEFT = 'left'
    RIGHT = 'right'

    CENTER = "center"
    CORNER = "corner"
    CORNERS = "corners"

    LEFT = 'left'
    RIGHT = 'right'
    JUSTIFY = 'justify'

    NUMBER = 'number'
    TEXT = 'text'
    BOOLEAN = 'boolean'
    BUTTON = 'button'

    inch = 72
    cm = 28.3465
    mm = 2.8346

    # Default mouse values
    MOUSEX = -1
    MOUSEY = -1
    mousedown = False

    # Default key values
    key = '-'
    keycode = 0
    keydown = False

    FRAME = 0

    def __init__(self, context, canvas, namespace):
        self._context = context
        self._canvas = canvas
        self._namespace = namespace
        self._autoclosepath = True
        self._set_defaults()
        
    def _set_defaults(self):
        '''Set the default values. Called at __init__ and at the end of run(),
        do that new draw loop iterations don't take up values left over by the
        previous one.'''
        ### TODO - Move this ?

        self._fontfile = "assets/notcouriersans.ttf"
        self._fontsize = 16
        self._align = Bot.LEFT
        self._lineheight = 1

        self.framerate = 30

        self.WIDTH, self.HEIGHT = self._canvas.DEFAULT_SIZE

        self._transformmode = Bot.CENTER

        self._color_range = 1.
        self._color_mode = Bot.RGB
        self._canvas.fillcolor = self.color(.2)
        self._canvas.strokecolor = None
        self._canvas.strokewidth = 1.0

    def _makeInstance(self, clazz, args, kwargs):
        '''Creates an instance of a class defined in this document.
           This method sets the context of the object to the current context.'''
        inst = clazz(self._canvas, *args, **kwargs)
        return inst

    def setup(self):
        """ For override by user sketch """
        pass

    def draw(self):
        """ For override by user sketch """
        pass

    def EndClip(self, *args, **kwargs):
        return self._makeInstance(EndClip, args, kwargs)
    def BezierPath(self, *args, **kwargs):
        return self._makeInstance(BezierPath, args, kwargs)
    def ClippingPath(self, *args, **kwargs):
        return self._makeInstance(ClippingPath, args, kwargs)
    def Rect(self, *args, **kwargs):
        return self._makeInstance(Rect, args, kwargs)
    def Oval(self, *args, **kwargs):
        return self._makeInstance(Oval, args, kwargs)
    def Ellipse(self, *args, **kwargs):
        return self._makeInstance(Ellipse, args, kwargs)
    def Color(self, *args, **kwargs):
        return self._makeInstance(Color, args, kwargs)
    def Image(self, *args, **kwargs):
        return self._makeInstance(Image, args, kwargs)
    def Text(self, *args, **kwargs):
        return self._makeInstance(Text, args, kwargs)

    #### Variables

    def var(self, name, type, default=None, min=0, max=255, value=None):
        v = Variable(name, type, default, min, max, value)
        v = self._addvar(v)

    def _addvar(self, v):
        ''' Sets a new accessible variable.'''
        ### TODO
        oldvar = self._findvar(v.name)
        if oldvar is not None:
            if oldvar.compliesTo(v):
                v.value = oldvar.value
        self._vars.append(v)
        self._namespace[v.name] = v.value

    def _findvar(self, name):
        for v in self._oldvars:
            if v.name == name:
                return v
        return None

    #### Utility

    def color(self, *args):
        #return Color(self.color_mode, self.color_range, *args)
        return Color(mode=self._color_mode, color_range=self._color_range, *args)

    choice = r.choice

    def random(self,v1=None, v2=None):
        # ipsis verbis from Nodebox
        if v1 is not None and v2 is None:
            if isinstance(v1, float):
                return r.random() * v1
            else:
                return int(r.random() * v1)
        elif v1 != None and v2 != None:
            if isinstance(v1, float) or isinstance(v2, float):
                start = min(v1, v2)
                end = max(v1, v2)
                return start + r.random() * (end-start)
            else:
                start = min(v1, v2)
                end = max(v1, v2) + 1
                return int(start + r.random() * (end-start))
        else: # No values means 0.0 -> 1.0
            return r.random()

    def grid(self, cols, rows, colSize=1, rowSize=1, shuffled = False):
        """Returns an iterator that contains coordinate tuples.
        The grid can be used to quickly create grid-like structures.
        A common way to use them is:
            for x, y in grid(10,10,12,12):
                rect(x,y, 10,10)
        """
        # Taken ipsis verbis from Nodebox
        from random import shuffle
        rowRange = range(int(rows))
        colRange = range(int(cols))
        if (shuffled):
            shuffle(rowRange)
            shuffle(colRange)
        for y in rowRange:
            for x in colRange:
                yield (x*colSize,y*rowSize)

    def files(self, path="*"):
        """Returns a list of files.
        You can use wildcards to specify which files to pick, e.g.
            f = files('*.gif')
        """
        # Taken ipsis verbis from Nodebox
        return glob(path)

    def snapshot(self,filename=None, surface=None, immediate=False):
        ### TODO correct comment for new drawing stuff
        '''Save the contents of current surface into a file.

        There's two uses for this method:
        - called from a script to create a output file
        - called from the Shoebot window menu, which requires the source surface
        to be specified in the arguments.

        - if output is bitmap (PNG, GTK), then it clones current surface via
          Cairo
        - if output is vector, doing the source paint in Cairo ends up in a
          vector file with an embedded bitmap - not good. So we just create
          another Bot instance with the currently loaded script, copy the
          current namespace and save its output in a file.
        '''

        '''
        If immediate is set to True, the bot will wait for the drawqueue
        to catch up, the output will happen.

        In general, this is bad for performance, so it's best to leave
        this set to False.  In the case of output to a surface, this
        always happens with immediate set to True otherwise the surface
        would not be ready on return.
        '''
        if filename:
            self._canvas.output(filename, immediate=immediate)
        elif surface:
            self._canvas.output(surface, immediate=True)

    # from Nodebox, a function to import Nodebox libraries
    def ximport(self, libName):
        try:
            lib = __import__("lib/"+libName)
        except:
            lib = __import__(libName)
        self._ns[libName] = lib
        lib._ctx = self
        return lib


    #### Core functions

    def size(self, w = None, h = None):
        '''Sets the size of the canvas, and creates a Cairo surface and context.

        Only the first call will actually be effective.'''
        
        if not w:
            w = self._canvas.width
        if not h:
            h = self._canvas.height
        if not w and not h:
            return (self._canvas.width, self._canvas.height)

        w, h = self._canvas.set_size((w, h))
        self._namespace['WIDTH'] = w
        self._namespace['HEIGHT'] = h

    def speed(self, framerate):
        if framerate:
            self._context.speed = framerate
            self._context.dynamic = True
        else:
            return self._context.speed


