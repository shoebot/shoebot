#!/usr/bin/env python

'''
Shoebot module

Copyright 2007, 2008 Ricardo Lafuente
Developed at the Piet Zwart Institute, Rotterdam

This file is part of Shoebot.

Shoebot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Shoebot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Shoebot.  If not, see <http://www.gnu.org/licenses/>.

This file uses code from Nodebox (http://www.nodebox.net).
The relevant code parts are marked with a "Taken from Nodebox" comment.

'''

import cairo
import util
from data import *

VERBOSE = False
DEBUG = False
EXTENSIONS = ('.png','.svg','.ps','.pdf')

class ShoebotError(Exception): pass

class Box:
    '''
    The Box class is an abstraction to hold a Cairo surface, context and all
    methods to access and manipulate it (the Nodebox language is
    implemented here).
    '''

    inch = 72
    cm = 28.3465
    mm = 2.8346

    RGB = "rgb"
    HSB = "hsb"

    NORMAL = "1"
    FORTYFIVE = "2"

    CENTER = "center"
    CORNER = "corner"
    CORNERS = "corners"

    DEFAULT_WIDTH = 200
    DEFAULT_HEIGHT = 200

    def __init__ (self, inputscript=None, targetfilename=None, canvas=None, gtkmode=False):

        self.inputscript = inputscript
        self.targetfilename = targetfilename

        # init internal path container
        self._path = None
        self._autoclosepath = True

        self.color_range = 1
        self.color_mode = RGB

        self._fillcolor = self.Color(.2)
        self._strokecolor = self.Color(.8)
        self._strokewidth = 1.0

        self._transform = Transform()
        self._transformmode = 'corner'

        self.gtkmode = gtkmode
        self.vars = []
        self._oldvars = self.vars
        self.namespace = {}

        self.WIDTH = Box.DEFAULT_WIDTH
        self.HEIGHT = Box.DEFAULT_HEIGHT

        if canvas:
            self.canvas = canvas
        else:
            self.canvas = CairoCanvas(self, self.targetfilename, self.WIDTH, self.HEIGHT, self.gtkmode)


    #### Object

    def _makeInstance(self, clazz, args, kwargs):
        """Creates an instance of a class defined in this document.
           This method sets the context of the object to the current context."""
        inst = clazz(self, *args, **kwargs)
        return inst
    def BezierPath(self, *args, **kwargs):
        return self._makeInstance(BezierPath, args, kwargs)
    def ClippingPath(self, *args, **kwargs):
        return self._makeInstance(ClippingPath, args, kwargs)
    def Rect(self, *args, **kwargs):
        return self._makeInstance(Rect, args, kwargs)
    def Oval(self, *args, **kwargs):
        return self._makeInstance(Oval, args, kwargs)
    def Color(self, *args, **kwargs):
        return self._makeInstance(Color, args, kwargs)
    def Image(self, *args, **kwargs):
        return self._makeInstance(Image, args, kwargs)
    def Text(self, *args, **kwargs):
        return self._makeInstance(Text, args, kwargs)

    #### Drawing

    def rect(self, x, y, width, height, roundness=0.0, draw=True, **kwargs):
        '''Draws a rectangle with top left corner at (x,y)

        The roundness variable sets rounded corners.
        '''
        r = self.BezierPath(**kwargs)
        r.rect(x,y,width,height,roundness,self.rectmode)
        #r.inheritFromContext(kwargs.keys())
        if draw:
            self.canvas.add(r)
        return r

    def rectmode(self, mode=None):
        if mode in (self.CORNER, self.CENTER, self.CORNERS):
            self.rectmode = mode
            return self.rectmode
        elif mode is None:
            return self.rectmode
        else:
            raise ShoebotError("rectmode: invalid input")

    def oval(self, x, y, width, height, draw=True, **kwargs):
        '''Draws an ellipse starting from (x,y)'''
        from math import pi

        r = self.BezierPath(**kwargs)
        r.ellipse(x,y,width,height)
        # r.inheritFromContext(kwargs.keys())
        if draw:
            self.canvas.add(r)
        return r

    def circle(self, x, y, diameter):
        self.oval(x, y, diameter, diameter)

    def line(self, x1, y1, x2, y2):
        '''Draws a line from (x1,y1) to (x2,y2)'''
        self.beginpath()
        self.moveto(x1,y1)
        self.lineto(x2,y2)
        self.endpath()

    def arrow(self, x, y, width, type=NORMAL):
        '''Draws an arrow.

        Arrows can be two types: NORMAL or FORTYFIVE.
        Taken from Nodebox.
        '''
        if type == self.NORMAL:
            head = width * .4
            tail = width * .2
            self.beginpath()
            self.moveto(x, y)
            self.lineto(x-head, y+head)
            self.lineto(x-head, y+tail)
            self.lineto(x-width, y+tail)
            self.lineto(x-width, y-tail)
            self.lineto(x-head, y-tail)
            self.lineto(x-head, y-head)
            self.lineto(x, y)
            self.endpath()
#            self.fill_and_stroke()
        elif type == self.FORTYFIVE:
            head = .3
            tail = 1 + head
            self.beginpath()
            self.moveto(x, y)
            self.lineto(x, y+width*(1-head))
            self.lineto(x-width*head, y+width)
            self.lineto(x-width*head, y+width*tail*.4)
            self.lineto(x-width*tail*.6, y+width)
            self.lineto(x-width, y+width*tail*.6)
            self.lineto(x-width*tail*.4, y+width*head)
            self.lineto(x-width, y+width*head)
            self.lineto(x-width*(1-head), y)
            self.lineto(x, y)
            self.endpath()
#            self.fill_and_stroke()
        else:
            raise NameError("arrow: available types for arrow() are NORMAL and FORTYFIVE\n")

    def star(self, startx, starty, points=20, outer=100, inner=50):
        '''Draws a star.

        Taken from Nodebox.
        '''
        from math import sin, cos, pi
        self.beginpath()
        self.moveto(startx, starty + outer)

        for i in range(1, int(2 * points)):
            angle = i * pi / points
            x = sin(angle)
            y = cos(angle)
            if i % 2:
                radius = inner
            else:
                radius = outer
            x = startx + radius * x
            y = starty + radius * y
            self.lineto(x,y)

        self.endpath()
#        self.fill_and_stroke()


    # ----- PATH -----
    # Path functions taken from Nodebox and modified

    def beginpath(self, x=None, y=None):
        self._path = self.BezierPath()
        if x and y:
            self._path.moveto(x,y)
        self._path.closed = False

        # if we have arguments, do a moveto too
        if x is not None and y is not None:
            self._path.moveto(x,y)

    def moveto(self, x, y):
        if self._path is None:
            ## self.beginpath()
            raise ShoebotError, "No current path. Use beginpath() first."
        self._path.moveto(x,y)

    def lineto(self, x, y):
        if self._path is None:
            raise ShoebotError, "No current path. Use beginpath() first."
        self._path.lineto(x, y)

    def curveto(self, x1, y1, x2, y2, x3, y3):
        if self._path is None:
            raise ShoebotError, "No current path. Use beginpath() first."
        self._path.curveto(x1, y1, x2, y2, x3, y3)

    def closepath(self):
        if self._path is None:
            raise ShoebotError, "No current path. Use beginpath() first."
        if not self._path.closed:
            self._path.closepath()
            self._path.closed = True

    def endpath(self, draw=True):
        if self._path is None:
            raise ShoebotError, "No current path. Use beginpath() first."
        if self._autoclosepath:
            self._path.closepath()
        p = self._path
        # p.inheritFromContext()
        if draw:
            self.canvas.add(p)
            self._path = None
        return p

    def drawpath(self,path):
        self.canvas.add(path)

    def autoclosepath(self, close=True):
        self._autoclosepath = close

    def relmoveto(self, x, y):
        '''Move relatively to the last point.'''
        if self._path is None:
            raise ShoebotError, "No current path. Use beginpath() first."
        self._path.relmoveto(x,y)

    def rellineto(self, x, y):
        '''Draw a line using relative coordinates.'''
        if self._path is None:
            raise ShoebotError, "No current path. Use beginpath() first."
        self._path.rellineto(x,y)

    def relcurveto(self, h1x, h1y, h2x, h2y, x, y):
        '''Draws a curve relatively to the last point.
        '''
        if self._path is None:
            raise ShoebotError, "No current path. Use beginpath() first."
        self._path.relcurveto(x,y)

    def findpath(self, list, curvature=1.0):
        ''' (NOT IMPLEMENTED) Builds a path from a list of point coordinates.
        Curvature: 0=straight lines 1=smooth curves
        '''
        raise NotImplementedError("findpath() isn't implemented yet (sorry)")
        #import bezier
        #path = bezier.findpath(points, curvature=curvature)
        #path.ctx = self
        #path.inheritFromContext()
        #return path

    #### Transform and utility

    def beginclip(self,x,y,w,h):
        self.save()
        self.context.rectangle(x, y, w, h)
        self.context.clip()

    def endclip(self):
        self.restore()

    def transform(self, mode=CENTER): # Mode can be CENTER or CORNER
        '''
        NOT IMPLEMENTED
        '''
        raise NotImplementedError("transform() isn't implemented yet")

    def translate(self, x, y):
        t = Transform()
        t.translate(x,y)
        self._transform *= t
    def rotate(self, degrees=0, radians=0):
        t = Transform()
        t.rotate(degrees, radians)
        self._transform *= t
    def scale(self, x=1, y=None):
        t = Transform()
        t.scale(x,y)
        self._transform *= t
    def skew(self, x=1, y=None):
        t = Transform()
        t.skew(x,y)
        self._transform *= t

    def push(self):
        #self.push_group()
        self.canvas.push()

    def pop(self):
        #self.pop_group()
        self.canvas.pop()

##    def reset(self):
##        self.canvas._context.identity_matrix()

    #### Color

    def outputmode(self):
        '''
        NOT IMPLEMENTED
        '''
        raise NotImplementedError("outputmode() isn't implemented yet")

    def color(self, *args):
        return Color(self, *args)

    def colormode(self, mode=None, crange=None):
        '''Sets the current colormode (can be RGB or HSB) and eventually
        the color range.

        If called without arguments, it returns the current colormode.
        '''
        if mode is not None:
            if mode == "rgb":
                self.color_mode = RGB
            elif mode == "hsb":
                self.color_mode = HSB
            else:
                raise NameError, "Only RGB and HSB colormodes are supported."
        if crange is not None:
            self.color_range = crange
        return self.color_mode

    def colorrange(self, crange):
        self.color_range = float(crange)

    def fill(self,*args):
        '''Sets a fill color, applying it to new paths.'''
        self._fillcolor = self.color(args)
        return self._fillcolor

    def nofill(self):
        ''' Stops applying fills to new paths.'''
        self._fillcolor = None

    def stroke(self,*args):
        '''Sets a stroke color, applying it to new paths.'''
        self._strokecolor = self.color(args)
        return self._strokecolor

    def nostroke(self):
        ''' Stops applying strokes to new paths.'''
        self.canvas._strokecolor = None

    def strokewidth(self, w=None):
        '''Sets the stroke width.'''
        if w is not None:
            self._strokewidth = w
        else:
            return self._strokewidth

    def background(self,*args):
        '''Sets the background colour.'''
        r = self.BezierPath()
        r.rect(0, 0, self.WIDTH, self.HEIGHT)
        r.fill = self.color(*args)
        self.canvas.add(r)

    #### Text

    def font(self, fontpath=None, fontsize=None):
        '''Set the font to be used with new text instances.

        Accepts TrueType and OpenType files. Depends on FreeType being
        installed.'''
        if fontpath is not None:
            face = util.create_cairo_font_face_for_file(fontpath, 0)
            self.context.set_font_face(face)
        else:
            self.context.get_font_face()
        if fontsize is not None:
            self.fontsize(fontsize)

    def fontsize(self, fontsize=None):
        if fontsize is not None:
            self.canvas.font_size = fontsize
        else:
            return self.canvas.font_size

    def text(self, txt, x, y, width=None, height=1000000, outline=False):
        '''
        Draws a string of text according to current font settings.
        '''
        # TODO: Check for malformed requests (x,y,txt is a common mistake)
        self.save()
        if width is not None:
            pass
        if outline is True:
            self.textpath(txt, x, y, width, height)
        else:
            self.context.move_to(x,y)
            self.context.show_text(txt)
            self.fill_and_stroke()
        self.restore()

    def textpath(self, txt, x, y, width=None, height=1000000, draw=True):
        '''
        Draws an outlined path of the input text
        '''
        ## FIXME: This should be handled by BezierPath
        self.save()
        self.context.move_to(x,y)
        self.context.text_path(txt)
        self.restore()
#        return self._path

    def textwidth(self, txt, width=None):
        '''Returns the width of a string of text according to the current
        font settings.
        '''
        return textmetrics(txt)[0]

    def textheight(self, txt, width=None):
        '''Returns the height of a string of text according to the current
        font settings.
        '''
        return textmetrics(txt)[1]

    def textmetrics(self, txt, width=None):
        '''Returns the width and height of a string of text as a tuple
        (according to current font settings).
        '''
        # for now only returns width and height (as per Nodebox behaviour)
        # but maybe we could use the other data from cairo
        x_bearing, y_bearing, textwidth, textheight, x_advance, y_advance = self.context.text_extents(txt)
        return textwidth, textheight

    def lineheight(self, height=None):
        '''
        NOT IMPLEMENTED
        '''
        # default: 1.2
        # sets leading
        raise NotImplementedError("lineheight() isn't implemented yet")

    def align(self, align="LEFT"):
        '''
        NOT IMPLEMENTED
        '''
        # sets alignment to LEFT, RIGHT, CENTER or JUSTIFY
        raise NotImplementedError("align() isn't implemented in Shoebot yet")

    # TODO: Set the framework to setup font options

    def fontoptions(self, hintstyle=None, hintmetrics=None, subpixelorder=None, antialias=None):
        raise NotImplementedError("fontoptions() isn't implemented yet")

    # ----- IMAGE -----

    def image(self, path, x, y, width=None, height=None, alpha=1.0, data=None):
        '''
        TODO:
        width and height ought to be for scaling, not clipping
        Use gdk.pixbuf to load an image buffer and convert it to a cairo surface
        using PIL
        '''
        #width, height = im.size
        imagesurface = cairo.ImageSurface.create_from_png(path)
        self.context.set_source_surface (imagesurface, x, y)
        self.context.rectangle(x, y, width, height)
        self.context.fill()

    #### Variables

    def var(self, name, type, default=None, min=0, max=100, value=None):
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
            raise ShoebotError('setvars(): setvars needs a dict!')
        vardict = args
        for item in vardict:
            self.var(item, NUMBER, vardict[item])

    #### Utility

    def random(self,v1=None, v2=None):
        # ipsis verbis from Nodebox
        import random
        if v1 is not None and v2 is None:
            if isinstance(v1, float):
                return random.random() * v1
            else:
                return int(random.random() * v1)
        elif v1 != None and v2 != None:
            if isinstance(v1, float) or isinstance(v2, float):
                start = min(v1, v2)
                end = max(v1, v2)
                return start + random.random() * (end-start)
            else:
                start = min(v1, v2)
                end = max(v1, v2) + 1
                return int(start + random.random() * (end-start))
        else: # No values means 0.0 -> 1.0
            return random.random()

    from random import choice

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
        from glob import glob
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
          another Box instance with the currently loaded script, copy the
          current namespace and save its output in a file.

        The shortcomings of this is that
        '''

        if filename:
            self.canvas.output(filename)
        elif surface:
            self.canvas.output(surface)

    #### Core functions

    def size(self,w=None,h=None):
        '''Sets the size of the canvas, and creates a Cairo surface and context.

        Needs to be the first function call in a script.'''

        if not w:
            w = self.WIDTH
        if not h:
            h = self.HEIGHT

        if self.gtkmode:
            # in windowed mode we don't set the surface in the Box itself,
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



    def finish(self):
        '''Finishes the surface and writes it to the output file.'''
        self.canvas.draw()
        self.canvas.finish()

    def run(self, inputcode=None):
        '''
        Executes the contents of a Nodebox/Shoebot script
        in current surface's context.
        '''

        source_or_code = ""

        if not inputcode:
        # no input? see if box has an input file name or string set
            if not self.inputscript:
                raise ShoebotError("run() needs an input file name or code string (if none was specified when creating the Box instance)")
            inputcode = self.inputscript
        else:
            self.inputscript = inputcode

        import os
        # is it a proper filename?
        if os.path.exists(inputcode):
            filename = inputcode
            file = open(filename, 'rU')
            source_or_code = file.read()
            file.close()
        else:
            # if not, try parsing it as a code string
            source_or_code = inputcode

        import data
        for name in dir(self):
            # get all stuff in the Box namespaces
            self.namespace[name] = getattr(self, name)
        for name in dir(data):
            self.namespace[name] = getattr(data, name)

        try:
            # if it's a string, it needs compiling first; if it's a file, no action needed
            if isinstance(source_or_code, basestring):
                source_or_code = compile(source_or_code + "\n\n", "shoebot_code", "exec")
            # do the magic
            exec source_or_code in self.namespace
        except NameError:
            # if something goes wrong, print verbose system output
            # maybe this is too verbose, but okay for now
            import traceback
            import sys
            errmsg = traceback.format_exc()

#            print "Exception in Shoebot code:"
#            traceback.print_exc(file=sys.stdout)
            if not self.gtkmode:
                sys.stderr.write(errmsg)
                sys.exit()
            else:
                # if on gtkmode, print the error and don't break
                raise ShoebotError(errmsg)

#    def setup(self):
#        if self.namespace.has_key("setup"):
#            self.namespace["setup"]()
#        else:
#            raise ShoebotError("setup: There's no setup() method in input script")
#
#    def draw(self):
#        if self.namespace.has_key("draw"):
#            self.namespace["draw"]()
#        else:
#            raise ShoebotError("draw: There's no draw() method in input script")
#

class CairoCanvas:
    '''
    This class contains a Cairo context or surface, as well as methods to pass
    drawing commands to it.

    Its intended use is to get drawable objects from a Bot instance, store them
    in a stack and draw them to the Cairo context when necessary.
    '''
    def __init__(self, bot, target=None, width=None, height=None, gtkmode=False):

        self._bot = bot

        self.stack = []
        self.transform_stack = Stack()
        if not gtkmode:
            # image output mode, we need to make a surface
            self.setsurface(target, width, height)

        self.font_size = 12

        # self.outputmode = RGB
        # self.linecap
        # self.linejoin
        # self.fontweight
        # self.fontslant
        # self.hintmetrics
        # self.hintstyle
        # self.filter
        # self.operator
        # self.antialias
        # self.fillrule

    def setsurface(self, target=None, width=None, height=None):
        '''Sets the surface on which the Canvas object will operate.

        Besides attaching surfaces, it can also create new ones based on an
        output filename; it also accepts a Cairo surface or context as an
        argument, and attaches to them as expected.
        '''

        if not target:
            raise ShoebotError("setsurface(): No target specified!")
        if isinstance(target, basestring):
            # if the target is a string, should be a filename
            filename = target
            if not width:
                width = self.WIDTH
            if not height:
                height = self.HEIGHT
            self._surface = util.surfacefromfilename(filename,width,height)
            self._context = cairo.Context(self._surface)
        elif isinstance(target, cairo.Surface):
            # and if it's a surface, attach our Cairo context to it
            self._surface = target
            self._context = cairo.Context(self._surface)
        elif isinstance(target, cairo.Context):
            # if it's a Cairo context, use it instead of making a new one
            self._context = target
            self._surface = self._context.get_target()
        else:
            raise ShoebotError("setsurface: Argument must be a file name, a Cairo surface or a Cairo context")

    def get_context(self):
        return self._context
    def get_surface(self):
        return self._surface

##    def _set_transform(self, matrix):
##        self._transform._matrix = matrix
##    def _get_transform(self):
##        return self._transform
##    transform = property(_get_transform, _set_transform)

    def add(self, grob):
        if not isinstance(grob, data.Grob):
            raise ShoebotError("Canvas.add() - wrong argument: expecting a Grob, received %s" % (grob))

        # set context values
        if self._bot._fillcolor and not grob._fillcolor:
            grob._fillcolor = self._bot._fillcolor
        if self._bot._strokecolor and not grob._fillcolor:
            grob._strokecolor = self._bot._strokecolor
        if self._bot._strokewidth and not grob._strokewidth:
            grob._strokewidth = self._bot._strokewidth
        if self._bot._transform:
            grob._transform *= self._bot._transform

        self.stack.append(grob)

    def draw(self, ctx=None):
        if not ctx:
            ctx = self._context
        for item in self.stack:
            if isinstance(item, Grob):
                # check if item has its own attributes
                # set context fill/stroke colors to the grob's
                # set transform matrix
                ctx.save()
                ctx.set_matrix(item._transform._matrix)
                self.drawpath(item)
                ctx.restore()
                # fill_and_stroke()

    def drawpath(self,path):
        '''Passes the path to a Cairo context.'''
        if not isinstance(path, BezierPath):
            raise ShoebotError("drawpath(): Expecting a BezierPath, got %s" % (path))

        ctx = self._context

        if path._strokewidth:
            self._context.set_line_width(path._strokewidth)

        for element in path.data:
            cmd = element[0]
            values = element[1:]

            # apply cairo context commands
            if cmd == MOVETO:
                ctx.move_to(*values)
            elif cmd == LINETO:
                ctx.line_to(*values)
            elif cmd == CURVETO:
                ctx.curve_to(*values)
            elif cmd == RLINETO:
                ctx.rel_line_to(*values)
            elif cmd == RCURVETO:
                ctx.rel_curve_to(*values)
            elif cmd == CLOSE:
                ctx.close_path()
            elif cmd == ELLIPSE:
                from math import pi
                x, y, w, h = values
                ctx.save()
                ctx.translate (x + w / 2., y + h / 2.)
                ctx.scale (w / 2., h / 2.)
                ctx.arc (0., 0., 1., 0., 2 * pi)
                ctx.restore()
            else:
                raise ShoebotError("PathElement(): error parsing path element command (got '%s')" % (cmd))

        if path._fillcolor:
            self._context.set_source_rgba(*path._fillcolor)
            if path._strokecolor:
                # if there's a stroke still to be applied, we need to call fill_preserve()
                # which still leaves this path as active
                self._context.fill_preserve()
                self._context.set_source_rgba(*path._strokecolor)
                # now apply the stroke (stroke ends the path, we'd use stroke_preserve()
                # for further operations if needed)
                self._context.stroke()
            else:
                # if there isn't a stroke, use plain fill() to close the path
                self._context.fill()
        elif path._strokecolor:
            # if there's no fill, apply stroke only
            self._context.set_source_rgba(*path._strokecolor)
            self._context.stroke()
        else:
            pass

    def push(self):
        self.transform_stack.push(self._transform)

    def pop(self):
        self._transform = self.transform_stack.get()
        self.transform_stack.pop()

    def finish(self):
        if isinstance(self._surface, (cairo.SVGSurface, cairo.PSSurface, cairo.PDFSurface)):
            self._context.show_page()
            self._surface.finish()
        else:
            self._context.write_to_png("DUMMYOUTPUT.png")

    def clear(self):
        self.stack = self.transform_stack = []

    def output(self, target):
        self.draw()
        if isinstance(target, basestring): # filename
            filename = target
            import os
            f, ext = os.path.splitext(filename)

            if ext == ".png":
                # bitmap snapshots can be done via Cairo
                if isinstance(self._surface, cairo.ImageSurface):
                    # if current surface is a bitmap image surface, we can write the
                    # file right away
                    self._surface.write_to_png(filename)
                else:
                    # otherwise, we clone the contents of current surface onto
                    # a temporary one
                    temp_surface = util.surfacefromfilename(filename, self.WIDTH, self.HEIGHT)
                    ctx = cairo.Context(temp_surface)
                    ctx.set_source_surface(self._surface, 0, 0)
                    ctx.paint()
                    temp_surface.write_to_png(filename)
                    del temp_surface

            if ext in (".svg",".ps",".pdf"):
                # vector snapshots are made with another temporary Box

                # create a Box instance using the current running script
                box = Box(inputscript=self.inputscript, canvas=self)
                box.run()

                # set its variables to the current ones
                for v in self.vars:
                    box.namespace[v.name] = self.namespace[v.name]
                if 'setup' in box.namespace:
                    box.namespace['setup']()
                if 'draw' in box.namespace:
                    box.namespace['draw']()
                box.finish()
                del box
            print "Saved snapshot to %s" % filename

        elif isinstance(target, cairo.Context):
            ctx = target
            self.draw(ctx)
        elif isinstance(target, cairo.Surface):
            ctx = target.get_context()
            self.draw(ctx)



    def apply_matrix(self, xx=1.0, yx=0.0, xy=0.0, yy=1.0, x0=0.0, y0=0.0):
        '''
        Adds mtrx to the current transformation matrix
        '''
        mtrx = cairo.Matrix(xx, yx, xy, yy, x0, y0)
        try:
            self._context.transform(mtrx)
        except cairo.Error:
            print "Invalid transformation matrix (%2f,%2f,%2f,%2f,%2f,%2f)" % (xx, yx, xy, yy, x0, y0)

if __name__ == "__main__":
    print '''
    This file can only be used as a Python module.
    Use the 'sbot' script for commandline use.
    '''
    import sys
    sys.exit()

