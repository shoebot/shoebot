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

    DEFAULT_WIDTH = 200
    DEFAULT_HEIGHT = 200

    def __init__ (self, inputscript=None, targetfilename=None, canvas=None, gtkmode=False, ns=None):

        self.inputscript = inputscript
        self.targetfilename = targetfilename
        
        # init internal path container
        self._path = None
        self._autoclosepath = True

        self._transform = Transform()
        self.transform_stack = []

        self.gtkmode = gtkmode
        self.vars = []
        self._oldvars = self.vars
        self.namespace = {}
        self.FRAME = 0
        self.screen_ratio = None

        self.set_defaults()

        if canvas:
            self.canvas = canvas
        else:
            self.canvas = shoebot.core.CairoCanvas(bot = self,
                                      target = self.targetfilename,
                                      width = self.WIDTH,
                                      height = self.HEIGHT,
                                      gtkmode = self.gtkmode)
        # from nodebox
        if ns is None:
            ns = {}
            self._ns = ns

    #### Object

    def set_defaults(self):
        '''Set the default values. Called at __init__ and at the end of run(),
        do that new draw loop iterations don't take up values left over by the
        previous one.'''

        self._fontfile = "assets/notcouriersans.ttf"
        self._fontsize = 16
        self._align = Bot.LEFT
        self._lineheight = 1

        self.framerate = 30

        self.WIDTH = Bot.DEFAULT_WIDTH
        self.HEIGHT = Bot.DEFAULT_HEIGHT

        self._transformmode = Bot.CENTER

        self.color_range = 1.
        self.color_mode = Bot.RGB
        self._fillcolor = self.color(.2)
        self._strokecolor = None
        self._strokewidth = 1.0

    def _makeInstance(self, clazz, args, kwargs):
        """Creates an instance of a class defined in this document.
           This method sets the context of the object to the current context."""
        inst = clazz(self, *args, **kwargs)
        return inst
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
        v = self.addvar(v)

    def addvar(self, v):
        ''' Sets a new accessible variable.'''

        oldvar = self.findvar(v.name)
        if oldvar is not None:
            if oldvar.compliesTo(v):
                v.value = oldvar.value
        self.vars.append(v)
        self.namespace[v.name] = v.value

    def findvar(self, name):
        for v in self._oldvars:
            if v.name == name:
                return v
        return None

    def setvars(self,args):
        '''Defines the variables that can be externally set.

        Accepts a dictionary with variable names assigned
        to default values. If called more than once, it updates
        already existing values and adds new keys to accomodate
        new entries.

        DEPRECATED, use addvar() instead
        '''
        if not isinstance(args, dict):
            raise ShoebotError(_('setvars(): setvars needs a dict!'))
        vardict = args
        for item in vardict:
            self.var(item, NUMBER, vardict[item])

    #### Utility

    def drawing_closed(self):
        pass

    def color(self, *args):
        #return Color(self.color_mode, self.color_range, *args)
        return Color(mode=self.color_mode, color_range=self.color_range, *args)

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

    def snapshot(self,filename=None, surface=None):
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

        if filename:
            self.canvas.output(filename)
        elif surface:
            self.canvas.output(surface)

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

    def size(self,w=None,h=None):
        '''Sets the size of the canvas, and creates a Cairo surface and context.

        Needs to be the first function call in a script.'''

        if not w:
            w = self.WIDTH
        if not h:
            h = self.HEIGHT

        if self.gtkmode:
            # in windowed mode we don't set the surface in the Bot itself,
            # the gtkui module takes care of doing that
            # TODO: Parent widget as an argument?
            self.WIDTH = int(w)
            self.HEIGHT = int(h)
            self.namespace['WIDTH'] = self.WIDTH
            self.namespace['HEIGHT'] = self.HEIGHT

        else:
            self.WIDTH = int(w)
            self.HEIGHT = int(h)
            # hack to get WIDTH and HEIGHT into the local namespace for running
            self.namespace['WIDTH'] = self.WIDTH
            self.namespace['HEIGHT'] = self.HEIGHT
            # make a new surface for us
            self.canvas.setsurface(self.targetfilename, w, h)

        # return (self.WIDTH, self.HEIGHT)

    def speed(self, value):
        if value:
            self.framerate = value
        return self.framerate

    def finish(self):
        '''Finishes the surface and writes it to the output file.'''
        self.canvas.finish()

    def load_namespace(self):
        from shoebot import data
        for name in dir(self):
            # get all stuff in the Bot namespaces
            self.namespace[name] = getattr(self, name)
        for name in dir(data):
            self.namespace[name] = getattr(data, name)

    def run(self, inputcode=None):
        '''
        Executes the contents of a Nodebox/Shoebot script
        in current surface's context.
        '''

        source_or_code = ""

        if not inputcode:
        # no input? see if box has an input file name or string set
            if not self.inputscript:
                raise ShoebotError(_("run() needs an input file name or code string (if none was specified when creating the Bot instance)"))
            inputcode = self.inputscript
        else:
            self.inputscript = inputcode


        # is it a proper filename?
        if os.path.exists(inputcode):
            filename = inputcode
            file = open(filename, 'rU')
            source_or_code = file.read()
            file.close()
        else:
            # if not, try parsing it as a code string
            source_or_code = inputcode

        self.load_namespace()

        try:
            # if it's a string, it needs compiling first; if it's a file, no action needed
            if isinstance(source_or_code, basestring):
                source_or_code = compile(source_or_code + "\n\n", "shoebot_code", "exec")
            # do the magic
            exec source_or_code in self.namespace
        except NameError:
            # if something goes wrong, print verbose system output
            # maybe this is too verbose, but okay for now
            errmsg = traceback.format_exc()

#            print "Exception in Shoebot code:"
#            traceback.print_exc(file=sys.stdout)
            if not self.gtkmode:
                sys.stderr.write(errmsg)
                sys.exit()
            else:
                # if on gtkmode, print the error and don't break
                raise shoebot.ShoebotError(errmsg)

        # go back to default values for next iteration
        self.set_defaults()

    def next_frame(self):
        '''Updates the FRAME value.'''
        self.namespace['FRAME'] += 1

    def mouse_down(self, pointer):
        self.namespace['mousedown'] = True

    def mouse_up(self, pointer):
        self.namespace['mousedown'] = False

    def pointer_moved(self, pointer):
        self.namespace['MOUSEX'] = pointer.x
        self.namespace['MOUSEY'] = pointer.y

    def key_down(self, keystate):
        self.namespace['key'] = keystate.key
        self.namespace['keycode'] = keystate.keycode
        self.namespace['keydown'] = True

    def key_up(self, keystate):
        self.namespace['keydown'] = False


