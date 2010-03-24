import sys, os
import cairo
from math import pi
# FIXME: we ought to make relative imports, but only when Cairocanvas is not called
# from BezierPath
from shoebot import ShoebotError
from shoebot.core import Canvas
from shoebot.data import BezierPath, ClippingPath, EndClip, Image, Text

import locale, gettext
APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
#gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext

MOVETO = "moveto"
RMOVETO = "rmoveto"
LINETO = "lineto"
RLINETO = "rlineto"
CURVETO = "curveto"
RCURVETO = "rcurveto"
ARC = 'arc'
ELLIPSE = 'ellipse'
CLOSE = "close"

CENTER = 'center'
CORNER = 'corner'

TOP_LEFT = 1
BOTTOM_LEFT = 2

class CairoCanvas(Canvas):    
   
    def __init__(self, bot=None, target=None, width=None, height=None, gtkmode=False):
        Canvas.__init__(self, bot, target, width, height, gtkmode)
        self.bot = bot

        # keep track of save/restore times
        self.saves = 0

        if not gtkmode:
            # image output mode, we need to make a surface
            self.setsurface(target, width, height)

        # following block checks if we are in gtkmode and in case of fullscreen it scales cairo context
        # and centers it on screen
        if self.bot.gtkmode:
            if self.bot.screen_ratio:
                self.canvas_ratio = self.bot.WIDTH / self.bot.HEIGHT
                if self.bot.screen_ratio < self.canvas_ratio:
                    self.fullscreen_scale =  float(self.bot.screen_width) / float(self.bot.WIDTH)
                    self.fullscreen_deltay = (self.bot.screen_height - (self.bot.HEIGHT*self.fullscreen_scale))/2
                    self.fullscreen_deltax = 0
                else:
                    self.fullscreen_scale =  float(self.bot.screen_height) / float(self.bot.HEIGHT)
                    self.fullscreen_deltax = (self.bot.screen_width - (self.bot.WIDTH*self.fullscreen_scale))/2
                    self.fullscreen_deltay = 0
                self.context.translate(self.fullscreen_deltax, self.fullscreen_deltay)
                self.context.scale(self.fullscreen_scale, self.fullscreen_scale)
                
        # we'll use these to calculate path bounds and centerpoints
        self.dummy_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
        self.dummy_ctx = cairo.Context(self.dummy_surface)



    def drawitem(self, item):
        # clips are special cases
        if isinstance(item, EndClip):
            # end clip instruction -> restore cairo context (it's saved in drawclip)
            self.pop()
            self.pop()
            return
        elif isinstance(item, ClippingPath):
            self.push()

        # get the bot's current transform matrix and apply it to the context
        self.push()
        if self.bot._transformmode == CORNER:
            deltax, deltay = (0,0)
        else:
            deltax, deltay = self.get_item_center(item)
                       
        mtrx = self.bot._transform.get_matrix_with_center(deltax,deltay)
        self.context.transform(mtrx)

        # get the item's transform, if appropriate
        if item.transform.stack:
            self.push()
            cx, cy = self.get_item_center(item) 
            self.context.transform(item.transform.get_matrix_with_center(cx, cy))
        
        # find item type and call appropriate drawing method
        if isinstance(item, ClippingPath):
            self.drawclip(item)
        elif isinstance(item, BezierPath):
            self.drawpath(item)
        elif isinstance(item, Text):
            self.drawtext(item)
        elif isinstance(item, Image):
            self.drawimage(item)
        
        if item.transform.stack:
            self.pop()
       
        if isinstance(item, ClippingPath):
            self.context.clip()
        else:
            # clip paths must keep the graphics context, i spent hours before i figured this out
            self.pop()

        # TODO: see if this improves performance
        del item


    def drawclip(self,path):
        for element in path.data:
            cmd = element[0]
            values = element[1:]

            # apply cairo context commands
            if cmd == MOVETO:
                self.context.move_to(*values)
            elif cmd == LINETO:
                self.context.line_to(*values)
            elif cmd == CURVETO:
                self.context.curve_to(*values)
            elif cmd == RLINETO:
                self.context.rel_line_to(*values)
            elif cmd == RCURVETO:
                self.context.rel_curve_to(*values)
            elif cmd == CLOSE:
                self.context.close_path()
            elif cmd == ELLIPSE:
                x, y, w, h = values
                self.context.save()
                self.context.translate (x + w / 2., y + h / 2.)
                self.context.scale (w / 2., h / 2.)
                self.context.arc (0., 0., 1., 0., 2 * pi)
                self.context.restore()
            else:
                raise ShoebotError(_("PathElement(): error parsing path element command (got '%s')") % (cmd))
        # self.context.clip() is called inside drawitem() because Cairo's fucking picky (or maybe i'm a dumb
        # coder, you choose)

    def drawtext(self,txt):
        self.context.save()
        self.context.translate(txt.x, txt.y-txt.baseline)

        if txt._fillcolor:
            self.context.set_source_rgba(*txt._fillcolor)
            if txt._strokecolor:
                # if there's a stroke still to be applied, we need to call fill_preserve()
                # which still leaves this path as active
                self.context.fill_preserve()
                self.context.set_source_rgba(*txt._strokecolor)
                # now apply the stroke (stroke ends the path, we'd use stroke_preserve()
                # for further operations if needed)
                self.context.stroke()
            else:
                # if there isn't a stroke, use plain fill() to close the path
                self.context.fill()
        elif txt._strokecolor:
            # if there's no fill, apply stroke only
            self.context.set_source_rgba(*txt._strokecolor)
            self.context.stroke()
        else:
            print _("Warning: Canvas object had no fill or stroke values")

        txt.pang_ctx.update_layout(txt.layout)
        txt.pang_ctx.show_layout(txt.layout)

        self.context.restore()

    def drawimage(self,image):
        self.context.set_source_surface (image.imagesurface, image.x, image.y)
        self.context.rectangle(image.x, image.y, image.width, image.height)
        self.context.fill()

    def drawpath(self,path):
        '''Passes the path to a Cairo context.'''

        if path._strokewidth:
            self.context.set_line_width(path._strokewidth)
        
        for element in path.data:
            cmd = element[0]
            values = element[1:]

            # apply cairo context commands
            if cmd == MOVETO:
                self.context.move_to(*values)
            elif cmd == LINETO:
                self.context.line_to(*values)
            elif cmd == CURVETO:
                self.context.curve_to(*values)
            elif cmd == RLINETO:
                self.context.rel_line_to(*values)
            elif cmd == RCURVETO:
                self.context.rel_curve_to(*values)
            elif cmd == ARC:
                self.context.arc(*values)
            elif cmd == CLOSE:
                self.context.close_path()
            elif cmd == ELLIPSE:
                x, y, w, h = values
                self.context.save()
                self.context.translate (x + w / 2., y + h / 2.)
                self.context.scale (w / 2., h / 2.)
                self.context.arc (0., 0., 1., 0., 2 * pi)
                self.context.restore()
            else:
                raise ShoebotError(_("PathElement(): error parsing path element command (got '%s')") % (cmd))

        if path._fillcolor:
            self.context.set_source_rgba(*path._fillcolor)
            if path._strokecolor:
                # if there's a stroke still to be applied, we need to call fill_preserve()
                # which still leaves this path as active
                self.context.fill_preserve()
                self.context.set_source_rgba(*path._strokecolor)
                # now apply the stroke (stroke ends the path, we'd use stroke_preserve()
                # for further operations if needed)
                self.context.stroke()
            else:
                # if there isn't a stroke, use plain fill() to close the path
                self.context.fill()
        elif path._strokecolor:
            # if there's no fill, apply stroke only
            self.context.set_source_rgba(*path._strokecolor)
            self.context.stroke()
        else:
            print _("Warning: Canvas object had no fill or stroke values")

    def get_item_center(self, item):
        '''Returns the path's center point. Note that this doesn't
        take transforms into account.'''
        
        # we don't have any direct way to calculate bbox from a path, but Cairo
        # does! So we make a new cairo context to calculate path bounds
        
        # this is a bad way to do it, but until we change the path code
        # to use 2geom, this is the next best thing
        
        # text objects have their own center-fetching method
        if isinstance(item, Text):
            x,y = self.get_textitem_center(item)
            y -= item.baseline
            return (x,y)

        # same for images
        if isinstance(item, Image):
            x,y = item.center
            return(x,y)

        # pass path to temporary context
        for element in item.data:
            cmd = element[0]
            values = element[1:]

            # apply cairo context commands
            if cmd == MOVETO:
                self.dummy_ctx.move_to(*values)
            elif cmd == LINETO:
                self.dummy_ctx.line_to(*values)
            elif cmd == CURVETO:
                self.dummy_ctx.curve_to(*values)
            elif cmd == RLINETO:
                self.dummy_ctx.rel_line_to(*values)
            elif cmd == RCURVETO:
                self.dummy_ctx.rel_curve_to(*values)
            elif cmd == CLOSE:
                self.dummy_ctx.close_path()
            elif cmd == ELLIPSE:
                x, y, w, h = values
                self.dummy_ctx.save()
                self.dummy_ctx.translate (x + w / 2., y + h / 2.)
                self.dummy_ctx.scale (w / 2., h / 2.)
                self.dummy_ctx.arc (0., 0., 1., 0., 2 * pi)
                self.dummy_ctx.restore()
        # get boundaries
        bbox = self.dummy_ctx.stroke_extents()
        
        # get the center point
        (x1,y1,x2,y2) = bbox
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        
        # reset the dummy context
        self.dummy_ctx.new_path()
        
        # here's the point you asked for, kind sir, can i get you
        # a martini with that?
        return (x,y)

    def get_textitem_center(self, item):
        '''Returns the center point of the text item, disregarding transforms.
        '''
        w,h = item.layout.get_pixel_size()
        x = (item.x+w/2)
        y = (item.y+h/2)
        return (x,y)

    def push(self):
        '''Save the context; this is here for help debugging save/restore queues'''
        self.saves += 1
        # print 'Save:      ' + str(self.saves)
        self.context.save()

    def pop(self):
        '''Restore the graphics context'''
        self.saves -= 1
        # print 'Restore:   ' + str(self.saves)
        self.context.restore()

    def finish(self):
        if isinstance(self._surface, (cairo.SVGSurface, cairo.PSSurface, cairo.PDFSurface)):
            self.context.show_page()
            self._surface.finish()
        else:
            self._surface.write_to_png(self._bot.targetfilename)

    def output(self, target):
        '''
        Output the canvas contents to a file, Cairo surface or Cairo context.
        '''

        if isinstance(target, basestring): # is it a filename?
            filename = target

            f, ext = os.path.splitext(filename)
            EXTENSIONS = ['.svg', '.png', '.ps', '.pdf']
            if ext not in EXTENSIONS:
                raise ShoebotError('CairoCanvas.output: Invalid filename extension')

            output_surface = surfacefromfilename(filename, self.bot.WIDTH, self.bot.HEIGHT)
            output_context = cairo.Context(output_surface)
            self.draw(output_context)
            if ext == '.png':
                output_surface.write_to_png(filename)
            else:
                output_context.show_page()
                output_surface.finish()

            del output_context, output_surface
            print _("Saved snapshot to %s") % filename

        elif isinstance(target, cairo.Context):
            self.context = target
            self.draw(self.context)
        elif isinstance(target, cairo.Surface):
            self.context = target.get_context()
            self.draw(self.context)


    def setsurface(self, target=None, width=None, height=None):
        '''Sets the surface on which the Canvas object will operate.

        Besides attaching surfaces, it can also create new ones based on an
        output filename; it also accepts a Cairo surface or context as an
        argument, and attaches to them as expected.
        '''

        if not target:
            raise ShoebotError(_("setsurface(): No target specified!"))
        if isinstance(target, basestring):
            # if the target is a string, should be a filename
            filename = target
            if not width:
                width = self.WIDTH
            if not height:
                height = self.HEIGHT
            self._surface = surfacefromfilename(filename,width,height)
            self.context = cairo.Context(self._surface)
        elif isinstance(target, cairo.Surface):
            # and if it's a surface, attach our Cairo context to it
            self._surface = target
            self.context = cairo.Context(self._surface)
        elif isinstance(target, cairo.Context):
            # if it's a Cairo context, use it instead of making a new one
            self.context = target
            self._surface = self.context.get_target()
        else:
            raise ShoebotError(_("setsurface: Argument must be a file name, a Cairo surface or a Cairo context"))
        

def surfacefromfilename(outfile, width, height):
    '''
    Creates a Cairo surface according to the filename extension,
    since Cairo requires the type of surface (svg, pdf, ps, png) to
    be specified on creation.
    '''
    # convert to ints, cairo.ImageSurface is picky
    width = int(width)
    height = int(height)

    # check across all possible formats and create the appropriate kind of surface
    # and also be sure that Cairo was built with support for that
    f, ext = os.path.splitext(outfile)
    if ext == '.svg':
        if not cairo.HAS_SVG_SURFACE:
                raise SystemExit ('cairo was not compiled with SVG support')
        surface = cairo.SVGSurface(outfile, width, height)

    elif ext == '.ps':
        if not cairo.HAS_PS_SURFACE:
                raise SystemExit ('cairo was not compiled with PostScript support')
        surface = cairo.PSSurface(outfile, width, height)

    elif ext == '.pdf':
        if not cairo.HAS_PDF_SURFACE:
                raise SystemExit ('cairo was not compiled with PDF support')
        surface = cairo.PDFSurface(outfile, width, height)

    elif ext == '.png':
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)

    else:
        surface = None
        raise NameError("%s is not a valid extension" % ext)

    return surface

