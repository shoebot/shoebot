#!/usr/bin/env python

'''
Shoebox module

Copyright 2007, 2008 Ricardo Lafuente 
Developed at the Piet Zwart Institute, Rotterdam

This file is part of Shoebox.

Shoebox is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Shoebox is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Shoebox.  If not, see <http://www.gnu.org/licenses/>.

This file uses code from Nodebox (http://www.nodebox.net).
The relevant code parts are marked with a "Taken from Nodebox" note.

'''

import cairo
import util
from data import *

class ShoeboxError(Exception): pass

class Box:
    '''
    The Box class is an abstraction to hold a Cairo context and all
    methods to access and manipulate it. The Nodebox language is
    implemented here.
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

    def __init__ (self, target, width=1000, height=1000):
        # if the target is a string, should be a filename
        if isinstance(target, basestring):
            self.targetfilename = target
            self.surface = util.surfacefromfilename(target,width,height)
            self.cairo = cairo.Context(self.surface)
        # and if it's a surface, attach our Cairo context to it
        elif isinstance(target, cairo.Surface):
            self.cairo = cairo.Context(target)
        else:
            raise ShoeboxError("Argument must be a file name or a Cairo surface")
        
        # set width and height constants
        self.WIDTH = int(width)
        self.HEIGHT = int(height)
      
        # create options object
        self.opt = OptionsContainer()
        # init internal path container
        self._path = None
        self._autoclosepath = True
        # init temp value holders
        self._fill = None
        self._stroke = None
        
    # ---- SHAPE -----

    def rect(self, x, y, width, height, roundness=0.0, fill=None, stroke=None):
        '''
        Draws a rectangle with top left corner in (x,y)
        The roundness variable sets rounded corners.
        Taken from Nodebox and modified.
        '''
        
        # take care of fill and stroke arguments
        if fill is not None or stroke is not None:
            if fill is not None: self._fill = fill
            if stroke is not None: self._stroke = stroke
        
        if roundness == 0.0:
            self.cairo.rectangle(x, y, width, height)
            self.fill_and_stroke()
        else:
            curve = min(width*roundness, height*roundness)
            self.beginpath()
            self.moveto(x, y+curve)
            self.curveto(x, y, x, y, x+curve, y)
            self.lineto(x+width-curve, y)
            self.curveto(x+width, y, x+width, y, x+width, y+curve)
            self.lineto(x+width, y+height-curve)
            self.curveto(x+width, y+height, x+width, y+height, x+width-curve, y+height)
            self.lineto(x+curve, y+height)
            self.curveto(x, y+height, x, y+height, x, y+height-curve)
            self.endpath()

        if fill is not None or stroke is not None:
            self._fill = None
            self._stroke = None
    
    def oval(self, x, y, width, height):
        '''
        Draws an ellipse starting from (x,y)
        '''
        from math import pi
        self.cairo.save()
        self.cairo.translate (x + width / 2., y + height / 2.);
        self.scale (width / 2., height / 2.);
        self.arc (0., 0., 1., 0., 2 * pi);
        self.fill_and_stroke()
        self.cairo.restore()
    
    def line(self, x1, y1, x2, y2):
        '''
        Draws a line from (x1,y1) to (x2,y2)
        '''
        self.cairo.move_to(x1,y1)
        self.cairo.line_to(x2,y2)
        self.fill_and_stroke()
        # maybe use only a stroke?
    
    def arrow(self, x, y, width, type=NORMAL):
        '''
        Draws an arrow.
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
            self.fill_and_stroke()
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
            self.fill_and_stroke()
        else:
            raise NameError("arrow: available types for arrow() are NORMAL and FORTYFIVE\n")

    def star(self, startx, starty, points=20, outer=100, inner=50):
        '''
        Draws a star.
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
        self.fill_and_stroke()

    # ----- PATH -----
    # Path functions taken from Nodebox and modified

    def beginpath(self, x=None, y=None):
        self._path = BezierPath((x,y))
        self._path.closed = False
        ## FIXME: This ought to work:
        if x is not None and y is not None:
            # This is not working
            self._path.moveto(x,y)

    def moveto(self, x, y):
        # trying to fix this
        if self._path is None:
            self.beginpath()
            #raise ShoeboxError, "No current path. Use beginpath() first."
        self._path.moveto(x,y)

    def lineto(self, x, y):
        if self._path is None:
            raise ShoeboxError, "No current path. Use beginpath() first."
        self._path.lineto(x, y)

    def curveto(self, x1, y1, x2, y2, x3, y3):
        if self._path is None:
            raise ShoeboxError, "No current path. Use beginpath() first."
        self._path.curveto(x1, y1, x2, y2, x3, y3)

    def closepath(self):
        if self._path is None:
            raise ShoeboxError, "No current path. Use beginpath() first."
        if not self._path.closed:
            self._path.closepath()
            self._path.closed = True

    def endpath(self, draw=True):
        if self._path is None:
            raise ShoeboxError, "No current path. Use beginpath() first."
        if self._autoclosepath:
            self._path.closepath()
        p = self._path
        #p.inheritFromContext()
        if draw:
            self.drawpath(p)
        self._path = None
        #self._path.closed = False
        #return p
        
    def drawpath(self,path):
        if not isinstance(path, BezierPath):
            raise ShoeboxError, "drawpath(): Input is not a valid BezierPath object"
        self.cairo.save()
        for element in path._pathdata:
            if isinstance(element,basestring):
                cmd = element
            elif isinstance(element,PathElement):
                cmd = element[0]
            else:
                raise ShoeboxError("drawpath(): Invalid path element (check command string)")
            if cmd == MOVETO:
                x = element[1]
                y = element[2]
                self.cairo.move_to(x, y)
            elif cmd == LINETO:
                x = element[1]
                y = element[2]
                self.cairo.line_to(x, y)
            elif cmd == CURVETO:
                c1x = element[1]
                c1y = element[2]
                c2x = element[3]
                c2y = element[4]
                x = element[5]
                y = element[6]
                self.cairo.curve_to(c1x, c1y, c2x, c2y, x, y)
            elif cmd == CLOSE:
                self.cairo.close_path()
            else:
                raise ShoeboxError("PathElement(): error parsing path element command")
        ## TODO
        # if path has state attributes, set the context to those, saving
        # before and replacing them afterwards with the old values
        # else, use context
        self.fill_and_stroke()
        self.cairo.restore()

    def autoclosepath(self, close=True):
        self._autoclosepath = close

    def findpath(self, points, curvature=1.0):
        import bezier
        path = bezier.findpath(points, curvature=curvature)
        #path._ctx = self
        #path.inheritFromContext()
        return path

    def relmoveto(self, x, y):
        self.cairo.rel_move_to(x,y)

    def rellineto(self, x,y):
        self.cairo.rel_line_to(x,y)

    def relcurveto(self, h1x, h1y, h2x, h2y, x, y):
        self.cairo.rel_curve_to(h1x, h1y, h2x, h2y, x, y)
    
    def arc(self,centerx, centery, radius, angle1, angle2):
        self.cairo.arc(centerx, centery, radius, angle1, angle2)
    
    def findpath(self, list, curvature=1.0): 
        ''' 
        NOT IMPLEMENTED 
        Builds a path from a list of point coordinates.
        Curvature: 0=straight lines 1=smooth curves
        '''
        raise NotImplementedError("findpath() isn't implemented yet (sorry)")
        #import bezier
        #path = bezier.findpath(points, curvature=curvature)
        #path.ctx = self
        #path.inheritFromContext()
        #return path
        pass
    
    def beginclip(self, path):
        '''
        NOT IMPLEMENTED
        '''        
        pass
    
    def endclip(self):
        '''
        NOT IMPLEMENTED
        '''        
        pass
    
    # ----- -----

    def transform(self, mode=CENTER): # Mode can be CENTER or CORNER
        '''
        NOT IMPLEMENTED
        '''    
        raise NotImplementedError("transform() isn't implemented yet")

    def matrix(self, mtrx):
        '''
        Adds mtrx to the current transformation matrix
        '''
        # matrix = cairo.Matrix (xx=1.0, yx=0.0, xy=0.0, yy=1.0, x0=0.0, y0=0.0)
        self.transform(mtrx)
    
    def translate(self, x, y):
        '''
        Shifts the origin point by (x,y)
        '''
        self.cairo.translate(x, y)
    
    def rotate(self, radians=0):
        self.cairo.rotate(radians)
    
    def scale(self, x=1, y=None):
        if y is None:
            self.cairo.scale(x,x)
        else:
            self.cairo.scale(x,y)
    
    def skew(self, x, y=None):
        self.transform(mtrx)
        pass
    
    def push(self):
        #self.push_group()
        self.cairo.save()
    
    def pop(self):
        #self.pop_group()
        self.cairo.restore()
    
    def reset(self):
        pass
    
    # ----- COLOR -----
    
    def outputmode(self):
        '''
        NOT IMPLEMENTED
        '''        
        raise NotImplementedError("outputmode() isn't implemented yet")
    
    def colormode(self, mode=None, range=None):
        if mode is not None:
            if mode == "rgb":
                self.opt.colormode = RGB
            elif mode == "hsb":
                self.opt.colormode = HSB
            else:
                raise NameError, "Only RGB and HSB colormode is supported."
        if range is not None:
            self.opt.colorrange = range
        return self.opt.colormode
    
    def color(self,*args):
        if len(args) == 1:
            return Color(self.opt.colormode, self.opt.colorrange, args)
        elif len(args) == 3:
            return Color(self.opt.colormode, self.opt.colorrange, args[0], args[1], args[2])
        elif len(args) == 4:
            return Color(self.opt.colormode, self.opt.colorrange, args[0], args[1], args[2], args[3]) 
    
    def colorrange(self, range):
        if isinstance(range, int):
            self.opt.colorrange = range
            print "DEBUG(colorrange): Set to " + str(range)
        else:
            raise ShoeboxError("Wrong value for colorrange() - it must be an int")
            
    
    def fill(self,*args):	# apply fill and define fill colour
        self.opt.fillapply = True
        if isinstance(args[0], Color):
            self.opt.fillcolor = Color(self.opt.colormode,1,args[0])
        else:
            self.opt.fillcolor = Color(self.opt.colormode,1,args[0])  
        return self.opt.fillcolor
    
    def nofill(self):
        self.opt.fillapply = False
    
    def stroke(self,*args):
        self.opt.strokeapply = True
        if len(args) > 0:
            self.opt.strokecolor = self.color(*args)
        return self.opt.strokecolor
    
    def nostroke(self):
        self.opt.strokeapply = False
    
    def strokewidth(self, w=None):
        if w is not None:
            self.cairo.set_line_width(w)
        else:
            return self.cairo.get_line_width
    
    def background(self,r,g,b,a=None):
        if a is None:
            self.cairo.set_source_rgb(r,g,b)
            self.cairo.paint()
        else:
            self.cairo.paint_with_alpha(a)
    
    # ----- TEXT-----
    
    def font(self, fontpath=None, fontsize=None):
        if fontpath is not None:
            face = util.create_cairo_font_face_for_file (fontpath, 0)
            self.cairo.set_font_face(face)
        else:
            self.get_font_face()
        if fontsize is not None:
            self.fontsize(fontsize)
    
    def fontsize(self, fontsize=None):
        if fontsize is not None:
            self.cairo.set_font_size(fontsize)
        else:
            self.cairo.get_font_size()
    
    def text(self, txt, x, y, width=None, height=1000000, outline=False):
        '''
        Draws a string of text according to font settings
        '''
        # TODO: Check for malformed requests (x,y,txt is a common mistake)
        if width is not None:
            raise NotImplementedError("text(): width settings aren't implemented yet")
        if outline is True:
            self.textpath(txt, x, y, width, height)
        else:
            self.cairo.move_to(x,y)
            self.cairo.show_text(txt)
        self.fill_and_stroke()
    
    def textpath(self, txt, x, y, width=None, height=1000000):
        '''
        Draws an outlined path of the input text
        '''
        self.moveto(x,y)
        self.cairo.text_path(txt)
        self.fill_and_stroke()
        return self._path
    
    def textwidth(self, txt, width=None):
        '''
        Returns the width of a string of text according to the current font settings
        '''
        return textmetrics(txt)[0]
    
    def textheight(self, txt, width=None):
        '''
        Returns the height of a string of text according to the current font settings
        '''    
        return textmetrics(txt)[1]
    
    def textmetrics(self, txt, width=None):
        ''' 
        returns x-y extents as a tuple
        '''
        # for now only returns width and height (as per Nodebox behaviour)
        # but maybe we could use the other data from cairo
        x_bearing, y_bearing, textwidth, textheight, x_advance, y_advance = self.text_extents(txt)
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
        raise NotImplementedError("align() isn't implemented yet")
    
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
        self.cairo.set_source_surface (imagesurface, x, y)
        self.cairo.rectangle(x, y, width, height)
        self.cairo.fill()

    def imagesize(self, path):
        '''
        NOT IMPLEMENTED
        '''
        # get an external image's size
        raise NotImplementedError("imagesize() isn't implemented yet")

    # ----- UTILITY -----

    def size(self,w,h):
        '''
        NOT IMPLEMENTED
        '''
        ##self.WIDTH = int(w)
        ##self.HEIGHT = int(h)
        ## self.surface.scale*something*
        print "WARNING: size() isn't implemented yet (instead specify width and height arguments in the terminal). Ignoring."

    def var(self, name, type, default=None, min=0, max=100, value=None):
        '''
        NOT IMPLEMENTED
        '''        
        print "WARNING: var() is not implemented yet. Ignoring."
        #v = Variable(name, type, default, min, max, value)
        #v = self.addvar(v)

    def addvar(self, v):
        '''
        NOT IMPLEMENTED
        '''        
        raise NotImplementedError("addvar() isn't implemented yet")
        #oldvar = self.findvar(v.name)
        #if oldvar is not None:
            #if oldvar.compliesTo(v):
                #v.value = oldvar.value
        #self._vars.append(v)
        #self._ns[v.name] = v.value

    def findvar(self, name):
        '''
        NOT IMPLEMENTED
        '''        
        raise NotImplementedError("findvar() isn't implemented yet")
        #for v in self._oldvars:
            #if v.name == name:
                #return v
        #return None
        

    def random(self,v1=None, v2=None):
        # ipsis verbis from Nodebox
        import random
        if v1 != None and v2 == None:
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
        """
        Returns an iterator that contains coordinate tuples.
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

    def open(self):
        '''
        NOT IMPLEMENTED
        '''        
        raise NotImplementedError("open() isn't implemented yet")

    def files(self, path="*"):
        """Returns a list of files.

        You can use wildcards to specify which files to pick, e.g.
            f = files('*.gif')

        """

        # Taken ipsis verbis from Nodebox
        from glob import glob
        return glob(path)

    def autotext(self):
        '''
        NOT IMPLEMENTED
        '''        
        raise NotImplementedError("autotext() isn't implemented yet")

    def fill_and_stroke(self):
        '''
        Apply fill and stroke settings, and apply the current path to the final surface.
        '''
        print "DEBUG: Beginning fill_and_stroke()"
        # we need to give cairo values between 0-1
        # and for that we need to make a special request to Color()
        if self._fill is not None:
            fillclr = Color(self.opt.colormode, 1, self._fill)
        if self._stroke is not None:
            strokeclr = Color(self.opt.colormode, 1, self._stroke)
        else:
            fillclr = Color(self.opt.colormode, 1, self.opt.fillcolor)
            strokeclr = Color(self.opt.colormode, 1, self.opt.strokecolor)

        self.cairo.save()
        if self.opt.fillapply is True:
            self.cairo.set_source_rgba(fillclr[0],fillclr[1],fillclr[2],fillclr[3])
            if self.opt.strokeapply is True:
                # if there's a stroke still to be applied, we need to call fill_preserve()
                # which still leaves this path as active
                self.cairo.fill_preserve()
                self.cairo.set_source_rgba(strokeclr[0],strokeclr[1],strokeclr[2],strokeclr[3])
                # now apply the stroke (stroke ends the path, we'd use stroke_preserve()
                # for further operations if needed)
                self.cairo.stroke()
            else:
                # if there isn't a stroke, use plain fill() to close the path
                self.cairo.fill()
        elif self.opt.strokeapply is True:
            # if there's no fill, apply stroke only
            self.cairo.set_source_rgba(strokeclr[0],strokeclr[1],strokeclr[2],strokeclr[3])
            self.cairo.stroke()
        else:
            pass
        self.cairo.restore()

    def finish(self):
        '''
        I wrote this in a rush, sorry
        '''
        # get the extension from the filename
        ext = self.targetfilename[-3:]
        # if this is a vector file, wrap up and finish
        if ext in ("svg",".ps","pdf"):
            self.cairo.show_page()
            self.surface.finish()
        # but bitmap surfaces need us to tell them to save to a file
        elif ext == "png":
            # write to file
            self.surface.write_to_png(self.targetfilename)
        else:
            raise ShoeboxError("finish(): invalid extension")
        
    def snapshot(self,filename=None):
        '''
        Save a png file of current surface contents
        without finishing the surface
        (currently works only with PNG surfaces)
        '''
        if filename is None:
            raise ShoeboxError("snapshot() requires a filename argument")
        ext = self.targetfilename[-3:]
        # check if we're working on a PNG surface
        if ext == "png":
            # write to file
            self.surface.write_to_png(filename)
        else:
            raise ShoeboxError("snapshot() can only be called on PNG surfaces (current surface is " + str(ext))
        
    
    def run(self,filename):
        '''
        Executes the contents of a Nodebox/Shoebox script
        in current surface's context.
        '''
        self.cairo.save()
        # get the file contents
        file = open(filename, 'rU')
        source_or_code = file.read()
        file.close()
        # now run the code
        self.namespace = {}
        for name in dir(self):
            self.namespace[name] = getattr(self, name)
        try:
            # if it's a string, it needs compiling first; if it's a file, no action needed
            if isinstance(source_or_code, basestring):
                source_or_code = compile(source_or_code + "\n\n", "<Untitled>", "exec")
            # do the Cairo magic
            exec source_or_code in self.namespace
##          if self.namespace.has_key("setup"):
##              self.fastRun(self.namespace["setup"])
            
            
        except:
            # if something goes wrong, print verbose system output
            # maybe this is too verbose, but okay for now
            import traceback, sys
            print "Exception in user code:"
            print '-='*20
            traceback.print_exc(file=sys.stdout)
            print '-='*20
            sys.exit()
        else:
            # finish by restoring the Cairo context state
            self.cairo.restore()

class OptionsContainer:
    def __init__(self):
        self.outputmode = RGB
        self.colormode = RGB
        self.colorrange = 1.

        self.fillapply = True
        self.strokeapply = False
        self.fillcolor = (.7,.7,.7,1)
        self.strokecolor = (.2,.2,.2,1)
        self.strokewidth = 1.0

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

        #self._outputmode = RGB
        #self._colormode = RGB
        #self._colorrange = 1.0
        #self._fillcolor = self.Color()
        #self._strokecolor = None
        #self._strokewidth = 1.0
        #self.canvas.background = self.Color(1.0)
        #self._path = None
        #self._autoclosepath = True
        #self._transform = Transform()
        #self._transformmode = CENTER
        #self._transformstack = []
        #self._fontname = "Helvetica"
        #self._fontsize = 24
        #self._lineheight = 1.2
        #self._align = LEFT
        #self._noImagesHint = False
        #self._oldvars = self._vars
        #self._vars = []


if __name__ == "__main__":
    print '''
    This file can only be used as a Python module.
    Use console.py for commandline use.
    '''
    import sys
    sys.exit()

