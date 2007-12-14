#!/usr/bin/env python

# Shoebox's graphics backend
# Copyleft Ricardo Lafuente 2007
# 
# See copyright and license notice in
# vectorbox.py
# .
# TODO 
#
# - include gradient and image fills (Cairo only)

import cairo
import util
from data import *



class Box:
    '''
    GET A GOOD DESCRIPTION, DAMNIT
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

    #M_PI = pi

    def __init__ (self, target, width, height):
        # if the target is a string, should be a filename

        if isinstance(target, basestring):
            self.targetfilename = target
            self.surface = util.surfacefromfilename(target,width,height)
            self.cairo = cairo.Context(self.surface)
        elif isinstance(target, cairo.Surface):
            self.cairo = cairo.Context(target)
        else:
            raise VectorboxError("Argument must be a file name or a Cairo surface")
        
        self.width = width
        self.height = height
        
        self.opt = OptionsContainer()
        self._path = None
        self._autoclosepath = True
        
    # ---- SHAPE -----

    def rect(self, x, y, width, height, roundness=0.0):
        '''
        Draws a rectangle with top left corner in (x,y)
        The roundness variable sets rounded corners.
        Taken from Nodebox. (or was it? i gotta double-check)
        '''
        if roundness == 0.0:
            self.cairo.rectangle(x, y, width, height)
            self.fill_and_stroke()
        else:
            curve = min(width*roundness, height*roundness)
            self.moveto(x, y+curve)
            self.curveto(x, y, x, y, x+curve, y)
            self.lineto(x+width-curve, y)
            self.curveto(x+width, y, x+width, y, x+width, y+curve)
            self.lineto(x+width, y+height-curve)
            self.curveto(x+width, y+height, x+width, y+height, x+width-curve, y+height)
            self.lineto(x+curve, y+height)
            self.curveto(x, y+height, x, y+height, x, y+height-curve)
            self.endpath()
    
    
    def oval(self, x, y, width, height):
        '''
        Draws an ellipse starting from (x,y)
        '''
        # TODO: document behaviour (center? corner?)
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
        if type == NORMAL:
            head = width * .4
            tail = width * .2
            moveto(x, y)
            lineto(x-head, y+head)
            lineto(x-head, y+tail)
            lineto(x-width, y+tail)
            lineto(x-width, y-tail)
            lineto(x-head, y-tail)
            lineto(x-head, y-head)
            lineto(x, y)
            endpath()
            self.fill_and_stroke()
        elif type == FORTYFIVE:
            head = .3
            tail = 1 + head
            moveto(x, y)
            lineto(x, y+width*(1-head))
            lineto(x-width*head, y+width)
            lineto(x-width*head, y+width*tail*.4)
            lineto(x-width*tail*.6, y+width)
            lineto(x-width, y+width*tail*.6)
            lineto(x-width*tail*.4, y+width*head)
            lineto(x-width, y+width*head)
            lineto(x-width*(1-head), y)
            lineto(x, y)
            self.fill_and_stroke()
        else:
            raise NameError("arrow: available types for arrow() are NORMAL and FORTYFIVE\n")

    def star(self, startx, starty, points=20, outer=100, inner=50):
        '''
        Draws a star.
        Taken from Nodebox.
        '''
        from math import sin, cos, pi
        moveto(startx, starty + outer)

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
            lineto(x,y)

        endpath()
        self.fill_and_stroke()

    # ----- PATH -----
    # Path functions taken from Nodebox and modified

    def beginpath(self, x=None, y=None):
        #print "  beginpath"
        self._path = BezierPath((x,y))
        self._path.closed = False
        #print "so far so good"
        #if x != None and y != None:
            ## This is not working
            #self._path.moveto(x,y)

    def moveto(self, x, y):
        #print "  moveto"
        if self._path is None:
            raise VectorboxError, "No current path. Use beginpath() first."
        self._path.moveto(x,y)

    def lineto(self, x, y):
        #print "  lineto"
        if self._path is None:
            raise VectorboxError, "No current path. Use beginpath() first."
        self._path.lineto(x, y)

    def curveto(self, x1, y1, x2, y2, x3, y3):
        #print "  curveto"
        if self._path is None:
            raise VectorboxError, "No current path. Use beginpath() first."
        self._path.curveto(x1, y1, x2, y2, x3, y3)

    def closepath(self):
        #print "  closepath"
        if self._path is None:
            raise VectorboxError, "No current path. Use beginpath() first."
        if not self._path.closed:
            self._path.closepath()
            self._path.closed = True

    # FIXME: put draw working properly
    def endpath(self, draw=True):
        if self._path is None:
            raise VectorboxError, "No current path. Use beginpath() first."
        if self._autoclosepath:
            self._path.closepath()
        p = self._path
        #p.inheritFromContext()
        if draw:
            self.drawpath(p)
        self._path = None
        #self._path.closed = False
        #return p


    #def drawpath(self, path):
        #if isinstance(path, (list, tuple)):
            #path = BezierPath(path)
        
    def drawpath(self,path):
        if not isinstance(path, BezierPath):
            raise VectorboxError, "drawpath(): Input is not a valid BezierPath object"
        # include fill_and_stroke behaviour wrt stroke and fill
        #print "beginning drawing"
        self.cairo.save()
        for element in path.pathdata:
            if isinstance(element,basestring):
                cmd = element
                print "!! element is string: " + element
            elif isinstance(element,PathElement):
                cmd = element[0]
                #print cmd
            else:
                raise "WRONG PATH ELEMENT FED TO draw()"
            if cmd == MOVETO:
                x = element[1]
                y = element[2]
                #print "MOVETO"
                self.cairo.move_to(x, y)
            elif cmd == LINETO:
                x = element[1]
                y = element[2]
                #print "LINETO"
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
                #print "CLOSE"
                self.cairo.close_path()
            else:
                raise "BOLLOCKS, PathElement() is broken"
        # if has state attributes, set the context to those, saving before and replacing them afterwards
        # with the old values
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
    
    #def endpath(self, draw=True): # close the path and apply the fill and stroke
        #self.cairo.close_path()
        #if draw: 
            #self.currentpath.draw(self)

    
    def findpath(self, list, curvature=1.0): 
        ''' Builds a path from a list of point coordinates. Curvature: 0=straight lines 1=smooth curves
        #import bezier
        #path = bezier.findpath(points, curvature=curvature)
        #path.ctx = self
        #path.inheritFromContext()
        #return path
        '''
        pass
    
    def beginclip(self, path):
        pass
    
    def endclip(self):
        pass
    
    # ----- -----

    def transform(self, mode=CENTER): # Mode can be CENTER or CORNER
        print "WARNING: transform() wasn't implemented yet. Ignoring."

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
        print "WARNING: outputmode() is not implemented yet. Ignoring."
    
    def colormode(self, mode=None, range=None):
        if mode is not None:
            if mode == "rgb":
                self.opt.colormode = RGB
            elif mode == "hsb":
                self.opt.colormode = HSB
            else:
                raise NameError, "Only RGB and HSB colormode is supported."
        if range is not None:
            self.opt.colorrange = float(range)
        return self.opt.colormode
    
    def color(self,*args):
        mode = self.opt.colormode
        crange = self.opt.colorrange
        return Color(mode, crange, args)
    
    def fill(self,*args):	# apply fill and define fill colour
        self.opt.fillapply = True
        if len(args) > 0:
            self.opt.fillcolor = self.color(*args)
        return self.opt.fillcolor
    
    def nofill(self):
        #global self.opt.fillapply
        self.opt.fillapply = False
    
    def stroke(self,*args):
        self.opt.strokeapply = True
        if len(args) > 0:
            self.opt.strokecolor = self.color(*args)
        return self.opt.strokecolor
    
    def nostroke(self):
        #global self.opt.strokeapply
        self.opt.strokeapply = False
    
    def strokewidth(self, w=None):
        if w is not None:
            self.cairo.set_line_width(w)
        else:
            return self.cairo.get_line_width
    
    def background(self,r,g,b,a=None):
        # discard objects?
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
            print "WARNING: Text width settings are not implemented yet. Ignoring."
        #if outline is True:
            #textpath(txt, x, y, width, height)
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
        # default: 1.2
        # sets leading
        print "WARNING: lineheight() is not implemented yet. Ignoring."
        pass
    
    def align(self, align="LEFT"):
        # sets alignment to LEFT, RIGHT, CENTER or JUSTIFY
        print "WARNING: align() is not implemented yet. Ignoring."
        pass
    
    # TODO: Set the framework to setup font options
    
    def fontoptions(self, hintstyle=None, hintmetrics=None, subpixelorder=None, antialias=None):
        pass

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
        # get an external image's size
        print "WARNING: imagesize() is not implemented yet. Ignoring."
        pass

    # ----- UTILITY -----

    def size(self,w,h):
        #xfactor = w / width
        #yfactor = h / height
        #self.scale(xfactor, yfactor)
        print "WARNING: size() isn't implemented yet (instead specify width and height arguments in the terminal). Ignoring."

    def var(self, name, type, default=None, min=0, max=100, value=None):
        print "WARNING: var() is not implemented yet. Ignoring."
        #v = Variable(name, type, default, min, max, value)
        #v = self.addvar(v)

    def addvar(self, v):
        print "WARNING: addvar() is not implemented yet. Ignoring."
        #oldvar = self.findvar(v.name)
        #if oldvar is not None:
            #if oldvar.compliesTo(v):
                #v.value = oldvar.value
        #self._vars.append(v)
        #self._ns[v.name] = v.value

    def findvar(self, name):
        print "WARNING: findvar() is not implemented yet. Ignoring."
        #for v in self._oldvars:
            #if v.name == name:
                #return v
        #return None
        

    def random(self,v1=None, v2=None):
        # ipsis verbis from Nodebox
        import random
        if v1 != None and v2 == None: # One value means 0 -> v1
            if isinstance(v1, float):
                return random.random() * v1
            else:
                return int(random.random() * v1)
        elif v1 != None and v2 != None: # v1 -> v2
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
    
        Taken ipsis verbis from Nodebox
        """
        
        rowRange = range(int(rows))
        colRange = range(int(cols))
        if (shuffled):
            shuffle(rowRange)
            shuffle(colRange)
        for y in rowRange:
            for x in colRange:
                yield (x*colSize,y*rowSize)

    def open(self):
        print "WARNING: open() is not implemented yet. Ignoring."

    def files(self, path="*"):
        """Returns a list of files.

        You can use wildcards to specify which files to pick, e.g.
            f = files('*.gif')

        Taken ipsis verbis from Nodebox
        """
        from glob import glob
        return glob(path)

    def autotext(self):
        print "WARNING: Autotext is not implemented yet. Ignoring."

    def fill_and_stroke(self):
        '''
        Apply fill and stroke settings, and apply the current path to the final surface.
        '''

        # we need to give cairo values between 0-1
        # and for that we need to make a special request to Color()
        fillclr = Color(self.opt.colormode, 1, self.opt.fillcolor)
        strokeclr = Color(self.opt.colormode, 1, self.opt.strokecolor)

        self.cairo.save()
        if self.opt.fillapply is True:
            #print "setting source"
            #print fillclr
            self.cairo.set_source_rgba(fillclr[0],fillclr[1],fillclr[2],fillclr[3])
            #print "source set"
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
            print "WARNING: Fill and stroke: No operation done."
        self.cairo.restore()

    def finish(self):
        '''
        I wrote this in a rush, sorry
        '''
        ext = self.targetfilename[-3:]
        if ext in ("svg",".ps","pdf"):
            self.cairo.show_page()
            self.surface.finish()
        # but bitmap surfaces need us to tell them to save to a file
        elif ext == "png":
            self.surface.write_to_png(self.targetfilename)
            print self.targetfilename
        else:
            raise VectorboxError("VECTORBOX PANIC in finish()")
        
    def run(self,filename):
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
            #exec source_or_code in self.namespace
            exec source_or_code in self.namespace
        except:
            # something went wrong; print verbose system output
            # maybe this is too verbose, but okay for now
            import sys
            print sys.exc_info()
            exc_type, exc_value = sys.exc_info()[:2]
            print >> sys.stderr, exc_type, exc_value
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
    Use console.py for commandline use.
    This file can only be used as a Python module.
    '''
    import sys
    sys.exit()

