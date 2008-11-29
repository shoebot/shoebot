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
class ShoebotScriptError(Exception): pass

class Bot:
    '''
    A Bot is an interface to receive user commands (through scripts or direct
    calls) and pass them to a canvas for drawing.
    '''

    inch = 72
    cm = 28.3465
    mm = 2.8346

    DEFAULT_WIDTH = 200
    DEFAULT_HEIGHT = 200

    def __init__ (self, inputscript=None, targetfilename=None, canvas=None, gtkmode=False, ns=None):

        self.inputscript = inputscript
        self.targetfilename = targetfilename

        # init internal path container
        self._path = None
        self._autoclosepath = True

        self.color_range = 1.
        self.color_mode = RGB

        self._fillcolor = self.color(.2)
        self._strokecolor = None
        self._strokewidth = 1.0

        self._transform = Transform()
        self._transformmode = CENTER
        self.transform_stack = []

        self._fontfile = "assets/notcouriersans.ttf"
        self._fontsize = 16
        self._align = LEFT
        self._lineheight = 1

        self.gtkmode = gtkmode
        self.vars = []
        self._oldvars = self.vars
        self.namespace = {}

        self.WIDTH = Bot.DEFAULT_WIDTH
        self.HEIGHT = Bot.DEFAULT_HEIGHT

        if canvas:
            self.canvas = canvas
        else:
            self.canvas = CairoCanvas(bot = self,
                                      target = self.targetfilename,
                                      width = self.WIDTH,
                                      height = self.HEIGHT,
                                      gtkmode = self.gtkmode)
	# from nodebox	
	if ns is None:
            ns = {}
        self._ns = ns

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
    def Ellipse(self, *args, **kwargs):
        return self._makeInstance(Ellipse, args, kwargs)
    def Color(self, *args, **kwargs):
        return self._makeInstance(Color, args, kwargs)
    def Image(self, *args, **kwargs):
        return self._makeInstance(Image, args, kwargs)
    def Text(self, *args, **kwargs):
        return self._makeInstance(Text, args, kwargs)

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

    def color(self, *args):
        #return Color(self.color_mode, self.color_range, *args)
        return Color(mode=self.color_mode, color_range=self.color_range, *args)

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
          another Bot instance with the currently loaded script, copy the
          current namespace and save its output in a file.

        The shortcomings of this is that
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
                raise ShoebotError("run() needs an input file name or code string (if none was specified when creating the Bot instance)")
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
            # get all stuff in the Bot namespaces
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


class NodeBot(Bot):

    RGB = "rgb"
    HSB = "hsb"

    NORMAL = "1"
    FORTYFIVE = "2"

    LEFT = 'left'
    RIGHT = 'right'

    CENTER = "center"
    CORNER = "corner"
    CORNERS = "corners"

    def __init__(self, inputscript=None, targetfilename=None, canvas=None, gtkmode=False):
        Bot.__init__(self, inputscript, targetfilename, canvas, gtkmode)


    #### Drawing

    # Image

    def image(self, path, x, y, width=None, height=None, alpha=1.0, data=None, draw=True, **kwargs):
        '''Draws a image form path, in x,y and resize it to width, height dimensions.
        '''
        r = self.Image(path, x, y, width, height, alpha, data, **kwargs)        
        if draw:
            self.canvas.add(r)
        return r


    def imagesize(self, path):
        import Image
        img = Image.open(path)
        return img.size


    # Paths

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
        '''Draws an ellipse starting from (x,y) -  ovals and ellipses are not the same'''
        from math import pi
        r = self.BezierPath(**kwargs)
        r.ellipse(x,y,width,height)
        # r.inheritFromContext(kwargs.keys())
        if draw:
            self.canvas.add(r)
        return r

    def ellipse(self, x, y, width, height, draw=True, **kwargs):
        '''Draws an ellipse starting from (x,y)'''
        from math import pi
        r = self.BezierPath(**kwargs)
        r.ellipse(x,y,width,height)
        # r.inheritFromContext(kwargs.keys())
        if draw:
            self.canvas.add(r)
        return r

    def circle(self, x, y, diameter):
        self.ellipse(x, y, diameter, diameter)

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

    def obama(self, x=0, y=0, s=1):    
        self.beginpath()
        self.moveto(x+0, y+0) 
        self.moveto(x+30.155835*s, y+3.3597362999999998*s) 
        self.curveto(x+22.226585999999998*s, y+3.4767912999999999*s, x+17.558824000000001*s, y+11.938165*s, x+17.099542*s, y+19.025210999999999*s) 
        self.curveto(x+16.557696*s, y+22.805612999999997*s, x+15.694208*s, y+27.570126999999999*s, x+20.886292999999998*s, y+24.358142999999998*s) 
        self.curveto(x+22.063617999999998*s, y+23.262867999999997*s, x+16.210089999999997*s, y+25.217665999999998*s, x+20.032938999999999*s, y+22.868894999999998*s) 
        self.curveto(x+25.583684999999999*s, y+23.357593999999999*s, x+22.084018*s, y+16.985720000000001*s, x+18.091563000000001*s, y+19.354975*s) 
        self.curveto(x+17.196534*s, y+12.990902999999999*s, x+21.360583000000002*s, y+6.1242342999999995*s, x+28.662463000000002*s, y+7.5544572999999993*s) 
        self.curveto(x+38.693815999999998*s, y+5.1428252999999993*s, x+39.505282000000001*s, y+14.898575999999998*s, x+40.712510000000002*s, y+15.298545999999998*s) 
        self.curveto(x+41.478746000000001*s, y+17.796257999999998*s, x+38.611923000000004*s, y+17.259235999999998*s, x+41.188965000000003*s, y+20.135055999999999*s) 
        self.curveto(x+41.031133000000004*s, y+21.093715*s, x+40.828136000000001*s, y+22.054302999999997*s, x+40.595178000000004*s, y+23.017814999999999*s) 
        self.curveto(x+37.462203000000002*s, y+22.218651999999999*s, x+39.577568000000007*s, y+20.442938999999999*s, x+35.418173000000003*s, y+21.627851999999997*s) 
        self.curveto(x+33.602451000000002*s, y+19.520005999999999*s, x+26.432436000000003*s, y+20.067235999999998*s, x+32.427879000000004*s, y+19.574813999999996*s) 
        self.curveto(x+36.576917000000002*s, y+22.536335999999995*s, x+36.206899000000007*s, y+18.657166999999998*s, x+32.257211000000005*s, y+18.227402999999995*s) 
        self.curveto(x+30.574708000000005*s, y+18.213692999999996*s, x+25.753600000000006*s, y+17.080653999999996*s, x+26.102409000000005*s, y+20.064142999999994*s) 
        self.curveto(x+26.629214000000005*s, y+23.430944999999994*s, x+38.445660000000004*s, y+20.437210999999994*s, x+31.723868000000003*s, y+22.684509999999996*s) 
        self.curveto(x+25.411513000000003*s, y+23.251439999999995*s, x+37.020808000000002*s, y+23.018320999999997*s, x+40.577397000000005*s, y+23.095826999999996*s) 
        self.curveto(x+39.397572000000004*s, y+27.939184999999995*s, x+37.394660000000002*s, y+32.818625999999995*s, x+35.748844000000005*s, y+37.477711999999997*s) 
        self.curveto(x+33.876538000000004*s, y+37.505711999999995*s, x+40.912494000000002*s, y+27.210657999999995*s, x+33.551462000000008*s, y+28.513852999999997*s) 
        self.curveto(x+29.408984000000007*s, y+26.166980999999996*s, x+30.338694000000007*s, y+27.710668999999996*s, x+33.110568000000008*s, y+30.191032999999997*s) 
        self.curveto(x+33.542732000000008*s, y+33.300877999999997*s, x+27.883396000000008*s, y+31.263332999999996*s, x+24.356592000000006*s, y+31.595176999999996*s) 
        self.curveto(x+26.592705000000006*s, y+31.132081999999997*s, x+32.999869000000004*s, y+26.980728999999997*s, x+25.889071000000005*s, y+28.137995999999998*s) 
        self.curveto(x+24.787247000000004*s, y+28.528912999999999*s, x+23.694590000000005*s, y+29.248256999999999*s, x+22.461438000000005*s, y+29.045728999999998*s) 
        self.curveto(x+19.269951000000006*s, y+27.610359999999996*s, x+20.894864000000005*s, y+31.648117999999997*s, x+23.304124000000005*s, y+31.790200999999996*s) 
        self.curveto(x+23.016163000000006*s, y+31.879840999999995*s, x+22.756522000000004*s, y+31.999426999999997*s, x+22.532552000000006*s, y+32.155418999999995*s) 
        self.curveto(x+18.385237000000007*s, y+34.449280999999992*s, x+20.349656000000007*s, y+30.779214999999994*s, x+19.403592000000007*s, y+29.169828999999993*s) 
        self.curveto(x+13.060974000000007*s, y+29.491880999999992*s, x+17.907451000000005*s, y+36.572479999999992*s, x+20.239166000000008*s, y+40.144177999999997*s) 
        self.curveto(x+18.873123000000007*s, y+37.739430999999996*s, x+18.08608000000001*s, y+32.890574999999998*s, x+19.360926000000006*s, y+33.977977999999993*s) 
        self.curveto(x+20.037191000000007*s, y+36.986654999999992*s, x+25.938847000000006*s, y+41.74645499999999*s, x+26.130852000000004*s, y+38.06631999999999*s) 
        self.curveto(x+20.628474000000004*s, y+36.782302999999992*s, x+27.449303000000004*s, y+35.551605999999992*s, x+29.746934000000003*s, y+35.648064999999988*s) 
        self.curveto(x+30.410632000000003*s, y+33.076153999999988*s, x+19.772083000000002*s, y+38.383369999999985*s, x+23.268567000000004*s, y+33.779412999999991*s) 
        self.curveto(x+27.615261000000004*s, y+31.829713999999992*s, x+31.833047000000004*s, y+35.101421999999992*s, x+35.688399000000004*s, y+31.89302799999999*s) 
        self.curveto(x+35.013363000000005*s, y+37.811202999999992*s, x+31.504216000000003*s, y+45.616307999999989*s, x+24.125476000000006*s, y+44.718296999999993*s) 
        self.curveto(x+19.661164000000007*s, y+41.819234999999992*s, x+21.309011000000005*s, y+48.927480999999993*s, x+14.919938000000005*s, y+51.24616799999999*s) 
        self.curveto(x+9.8282387000000053*s, y+53.10291999999999*s, x+5.8473682000000053*s, y+52.883251999999992*s, x+6.0155459000000047*s, y+56.432774999999992*s) 
        self.curveto(x+12.987418000000005*s, y+55.93589999999999*s, x+13.997744000000004*s, y+56.35166499999999*s, x+21.252523000000004*s, y+55.912477999999993*s) 
        self.curveto(x+20.898605000000003*s, y+53.130379999999995*s, x+19.688185000000004*s, y+41.857771999999997*s, x+23.656133000000004*s, y+47.023085999999992*s) 
        self.curveto(x+25.569923000000003*s, y+49.452668999999993*s, x+28.134662000000006*s, y+51.620268999999993*s, x+30.831404000000006*s, y+52.278003999999996*s) 
        self.curveto(x+28.088531000000007*s, y+53.314066999999994*s, x+28.752400000000005*s, y+58.240187999999996*s, x+30.522060000000007*s, y+56.199688999999992*s) 
        self.curveto(x+26.248979000000006*s, y+52.41766599999999*s, x+40.622643000000011*s, y+60.60644099999999*s, x+34.287476000000005*s, y+53.45876299999999*s) 
        self.lineto(x+33.032337000000005*s, y+52.455290999999988*s) 
        self.curveto(x+38.130551000000004*s, y+52.222700999999986*s, x+42.570123000000009*s, y+42.380979999999987*s, x+42.152545000000003*s, y+48.047831999999985*s) 
        self.curveto(x+43.123448000000003*s, y+54.821857999999985*s, x+40.010563000000005*s, y+56.547931999999989*s, x+47.969558000000006*s, y+56.614551999999989*s) 
        self.curveto(x+53.619178000000005*s, y+56.352016999999989*s, x+55.95324500000001*s, y+57.119506999999992*s, x+59.298673000000008*s, y+56.060458999999987*s) 
        self.curveto(x+58.382843999999999*s, y+46.073152*s, x+39.067419999999998*s, y+53.375225999999998*s, x+43.301012*s, y+37.764923000000003*s) 
        self.curveto(x+43.428455999999997*s, y+31.694825000000002*s, x+54.123880999999997*s, y+29.681982999999999*s, x+50.010494999999999*s, y+22.514310999999999*s) 
        self.curveto(x+47.938220999999999*s, y+20.563641000000001*s, x+44.097188000000003*s, y+25.356368*s, x+47.994453*s, y+21.312273999999999*s) 
        self.curveto(x+50.682201999999997*s, y+9.7576163000000005*s, x+40.191285999999998*s, y+3.6382382999999998*s, x+30.155835*s, y+3.3597362999999998*s) 
        self.moveto(x+20.239166000000001*s, y+40.144177999999997*s) 
        self.curveto(x+20.618817*s, y+40.762231*s, x+20.633900000000001*s, y+40.753855999999999*s, x+20.239166000000001*s, y+40.144177999999997*s) 
        self.moveto(x+48.335794999999997*s, y+25.116951*s) 
        self.curveto(x+52.603257999999997*s, y+28.884436000000001*s, x+42.579355*s, y+36.129815000000001*s, x+44.680596999999999*s, y+27.957156999999999*s) 
        self.curveto(x+46.699556999999999*s, y+28.476931999999998*s, x+47.871873000000001*s, y+29.936544999999999*s, x+48.335794999999997*s, y+25.116951*s)
        self.endpath()

    easteregg = obama

    #### Path
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
        p = self.BezierPath(path)
        self.canvas.add(p)

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

    def findpath(self, points, curvature=1.0):
    
        """Constructs a path between the given list of points.
    
        Interpolates the list of points and determines
        a smooth bezier path betweem them.
    
        The curvature parameter offers some control on
        how separate segments are stitched together:
        from straight angles to smooth curves.
        Curvature is only useful if the path has more than  three points.
        """
    
        # The list of points consists of Point objects,
        # but it shouldn't crash on something straightforward
        # as someone supplying a list of (x,y)-tuples.
    
        from types import TupleType
        for i, pt in enumerate(points):
            if type(pt) == TupleType:
                points[i] = Point(pt[0], pt[1])
    
        if len(points) == 0: return None
        if len(points) == 1:
            path = self.BezierPath(None)
            path.moveto(points[0].x, points[0].y)
            return path
        if len(points) == 2:
            path = self.BezierPath(None)
            path.moveto(points[0].x, points[0].y)
            path.lineto(points[1].x, points[1].y)
            return path
              
        # Zero curvature means straight lines.
    
        curvature = max(0, min(1, curvature))
        if curvature == 0:
            path = self.BezierPath(None)
            path.moveto(points[0].x, points[0].y)
            for i in range(len(points)): 
                path.lineto(points[i].x, points[i].y)
            return path
        
        curvature = 4 + (1.0-curvature)*40
    
        dx = {0: 0, len(points)-1: 0}
        dy = {0: 0, len(points)-1: 0}
        bi = {1: -0.25}
        ax = {1: (points[2].x-points[0].x-dx[0]) / 4}
        ay = {1: (points[2].y-points[0].y-dy[0]) / 4}
    
        for i in range(2, len(points)-1):
            bi[i] = -1 / (curvature + bi[i-1])
            ax[i] = -(points[i+1].x-points[i-1].x-ax[i-1]) * bi[i]
            ay[i] = -(points[i+1].y-points[i-1].y-ay[i-1]) * bi[i]
        
        r = range(1, len(points)-1)
        r.reverse()
        for i in r:
            dx[i] = ax[i] + dx[i+1] * bi[i]
            dy[i] = ay[i] + dy[i+1] * bi[i]

        path = self.BezierPath(None)
        path.moveto(points[0].x, points[0].y)
        for i in range(len(points)-1):
            path.curveto(points[i].x + dx[i], 
                         points[i].y + dy[i],
                         points[i+1].x - dx[i+1], 
                         points[i+1].y - dy[i+1],
                         points[i+1].x,
                         points[i+1].y)
    
        return path

    #### Transform and utility

##    def beginclip(self,x,y,w,h):
##        self.save()
##        self.context.rectangle(x, y, w, h)
##        self.context.clip()
##
##    def endclip(self):
##        self.restore()

    def transform(self, mode=None): # Mode can be CENTER or CORNER
        if mode:
            self._transformmode = mode
        return self._transformmode

    def translate(self, x, y):
        self._transform.translate(x,y)
    def rotate(self, degrees=0, radians=0):
        from math import radians as deg2rad
        if radians:
            angle = radians
        else:
            angle = deg2rad(degrees)
        self._transform.rotate(-angle)
    def scale(self, x=1, y=None):
        if not y:
            y = x
        if x == 0 or x == -1:
            # Cairo borks on zero values
            x = 1
        if y == 0 or y == -1:
            y = 1
        self._transform.scale(x,y)

    def skew(self, x=1, y=0):
        self._transform.skew(x,y)

    def push(self):
        self.transform_stack.append(self._transform.copy())

    def pop(self):
        self._transform = self.transform_stack.pop()

    def reset(self):
        self._transform = Transform()

    #### Color

    def outputmode(self):
        '''
        NOT IMPLEMENTED
        '''
        raise NotImplementedError("outputmode() isn't implemented yet")

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
        self._fillcolor = self.color(*args)
        return self._fillcolor

    def nofill(self):
        ''' Stop applying fills to new paths.'''
        self._fillcolor = None

    def stroke(self,*args):
        '''Set a stroke color, applying it to new paths.'''
        self._strokecolor = self.color(*args)
        return self._strokecolor

    def nostroke(self):
        ''' Stop applying strokes to new paths.'''
        self._strokecolor = None

    def strokewidth(self, w=None):
        '''Set the stroke width.'''
        if w is not None:
            self._strokewidth = w
        else:
            return self._strokewidth

    def background(self,*args):
        '''Set the background colour.'''
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
            self._fontfile = fontpath
        else:
            return self._fontfile
        if fontsize is not None:
            self._fontsize = fontsize

    def fontsize(self, fontsize=None):
        if fontsize is not None:
            self._fontsize = fontsize
        else:
            return self.canvas.font_size

    def text(self, txt, x, y, width=None, height=1000000, outline=False, draw=True, **kwargs):
        '''
        Draws a string of text according to current font settings.
        '''
        txt = self.Text(txt, x, y, width, height, **kwargs)
        if outline:
          path = txt.path
          if draw:
              self.canvas.add(path)
          return path
        else:
          if draw:
            self.canvas.add(txt)
          return txt

    def textpath(self, txt, x, y, width=None, height=1000000, draw=True, **kwargs):
        '''
        Draws an outlined path of the input text
        '''
        txt = self.Text(txt, x, y, width, height, **kwargs)
        path = txt.path
        if draw:
            self.canvas.add(path)
        return path

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

    def textmetrics(self, txt, width=None, height=None, **kwargs):
        '''Returns the width and height of a string of text as a tuple
        (according to current font settings).
        '''
        # for now only returns width and height (as per Nodebox behaviour)
        # but maybe we could use the other data from cairo
        txt = self.Text(txt, 0, 0, width, height, **kwargs)
        return txt.metrics

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


class Canvas:
    '''
    This class contains a Cairo context or surface, as well as methods to pass
    drawing commands to it.

    Its intended use is to get drawable objects from a Bot instance, store them
    in a stack and draw them to the Cairo context when necessary.
    '''
    def __init__(self, bot=None, target=None, width=None, height=None, gtkmode=False):

        if bot:
            self._bot = bot

        self.grobstack = []
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

    def add(self, grob):
        if not isinstance(grob, data.Grob):
            raise ShoebotError("Canvas.add() - wrong argument: expecting a Grob, received %s" % (grob))
        self.grobstack.append(grob)

    def setsurface(self):
        pass
    def get_context(self):
        return self._context
    def get_surface(self):
        return self._surface

    def draw(self, ctx=None):
        pass
    def output(self, filename):
        pass

    def clear(self):
        self.grobstack = []

class CairoCanvas(Canvas):
    def __init__(self, bot=None, target=None, width=None, height=None, gtkmode=False):
        Canvas.__init__(self, bot, target, width, height, gtkmode)

        if not gtkmode:
            # image output mode, we need to make a surface
            self.setsurface(target, width, height)

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

    def draw(self, ctx=None):
        if not ctx:
            ctx = self._context

        for item in self.grobstack:
            if isinstance(item, BezierPath):
                ctx.save()
                deltax, deltay = item.center
                m = item._transform.get_matrix_with_center(deltax,deltay,item._transformmode)
                ctx.transform(m)
                self.drawpath(item)
            elif isinstance(item, Text):
                ctx.save()
                x,y = item.metrics[0:2]
                deltax, deltay = item.center
                ctx.translate(item.x,item.y)                
                m = item._transform.get_matrix_with_center(deltax,deltay,item._transformmode)
                ctx.transform(m)
                self.drawtext(item)
            elif isinstance(item, Image):
                ctx.save()
                deltax, deltay = item.center
                m = item._transform.get_matrix_with_center(deltax,deltay,item._transformmode)
                ctx.transform(m)
                self.drawimage(item)        

            ctx.restore()


    def drawtext(self,txt,ctx=None):
        if not ctx:
            ctx = self._context

        ctx.set_font_face(txt._fontface)
        ctx.set_font_size(txt._fontsize)
        ctx.text_path(txt.text)

        if txt._fillcolor:
            self._context.set_source_rgba(*txt._fillcolor)
            if txt._strokecolor:
                # if there's a stroke still to be applied, we need to call fill_preserve()
                # which still leaves this path as active
                self._context.fill_preserve()
                self._context.set_source_rgba(*txt._strokecolor)
                # now apply the stroke (stroke ends the path, we'd use stroke_preserve()
                # for further operations if needed)
                self._context.stroke()
            else:
                # if there isn't a stroke, use plain fill() to close the path
                self._context.fill()
        elif txt._strokecolor:
            # if there's no fill, apply stroke only
            self._context.set_source_rgba(*txt._strokecolor)
            self._context.stroke()
        else:
            print "Warning: Canvas object had no fill or stroke values"

    def drawimage(self,image,ctx=None):
        if not ctx:
            ctx = self._context
        ctx.set_source_surface (image.imagesurface, image.x, image.y)
        ctx.rectangle(image.x, image.y, image.width, image.height)
        ctx.fill()

    def drawpath(self,path,ctx=None):
        '''Passes the path to a Cairo context.'''
        if not isinstance(path, BezierPath):
            raise ShoebotError("drawpath(): Expecting a BezierPath, got %s" % (path))

        if not ctx:
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
            print "Warning: Canvas object had no fill or stroke values"

    def finish(self):
        if isinstance(self._surface, (cairo.SVGSurface, cairo.PSSurface, cairo.PDFSurface)):
            self._context.show_page()
            self._surface.finish()
        else:
            self._context.write_to_png("DUMMYOUTPUT.png")

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
                # vector snapshots are made with another temporary Bot

                # create a Bot instance using the current running script
                box = Bot(inputscript=self.inputscript, canvas=self)
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

if __name__ == "__main__":
    print '''
    This file can only be used as a Python module.
    Use the 'sbot' script for commandline use.
    '''
    import sys
    sys.exit()



