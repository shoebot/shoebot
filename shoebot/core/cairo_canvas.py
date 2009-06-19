import sys, os
import cairo
from math import pi
# FIXME: we ought to make relative imports, but only when Cairocanvas is not called
# from BezierPath
import shoebot
from shoebot import ShoebotError
from shoebot.core import Canvas


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

class CairoCanvas(Canvas):    
   
    def __init__(self, bot=None, target=None, width=None, height=None, gtkmode=False):
        Canvas.__init__(self, bot, target, width, height, gtkmode)

        self.bot = bot

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
            raise ShoebotError(_("setsurface(): No target specified!"))
        if isinstance(target, basestring):
            # if the target is a string, should be a filename
            filename = target
            if not width:
                width = self.WIDTH
            if not height:
                height = self.HEIGHT
            self._surface = surfacefromfilename(filename,width,height)
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
            raise ShoebotError(_("setsurface: Argument must be a file name, a Cairo surface or a Cairo context"))

    def draw(self, ctx=None):
        if not ctx:
            ctx = self._context

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
                ctx.translate(self.fullscreen_deltax, self.fullscreen_deltay)
                ctx.scale(self.fullscreen_scale, self.fullscreen_scale)

        # draws things
        for item in self.grobstack:
            if isinstance(item, shoebot.data.ClippingPath):
                ctx.save()
                ctx.save()
                deltax, deltay = item.center
                m = item._transform.get_matrix_with_center(deltax,deltay,item._transformmode)
                ctx.transform(m)
                self.drawclip(item, ctx)
            elif isinstance(item, shoebot.data.RestoreCtx):
                ctx.restore()
            else:
                if isinstance(item, shoebot.data.BezierPath):
                    ctx.save()
                    deltax, deltay = item.center
                    m = item._transform.get_matrix_with_center(deltax,deltay,item._transformmode)
                    ctx.transform(m)
                    self.drawpath(item, ctx)
                elif isinstance(item, shoebot.data.Text):
                    ctx.save()
                    x,y = item.metrics[0:2]
                    deltax, deltay = item.center
                    m = item._transform.get_matrix_with_center(deltax,deltay-item.baseline,item._transformmode)
                    ctx.transform(m)
                    ctx.translate(item.x,item.y-item.baseline)
                    self.drawtext(item, ctx)
                elif isinstance(item, shoebot.data.Image):
                    ctx.save()
                    deltax, deltay = item.center
                    m = item._transform.get_matrix_with_center(deltax,deltay,item._transformmode)
                    ctx.transform(m)
                    self.drawimage(item, ctx)

                ctx.restore()

    def drawclip(self,path,ctx=None):
        '''Passes the path to a Cairo context.'''
        if not isinstance(path, shoebot.data.ClippingPath):
            raise shoebot.ShoebotError(_("drawpath(): Expecting a ClippingPath, got %s") % (path))

        if not ctx:
            ctx = self._context

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
                x, y, w, h = values
                ctx.save()
                ctx.translate (x + w / 2., y + h / 2.)
                ctx.scale (w / 2., h / 2.)
                ctx.arc (0., 0., 1., 0., 2 * pi)
                ctx.restore()
            else:
                raise ShoebotError(_("PathElement(): error parsing path element command (got '%s')") % (cmd))
        ctx.restore()
        ctx.clip()


    def drawtext(self,txt,ctx=None):
        if not ctx:
            ctx = self._context
        if txt._fillcolor:
            ctx.set_source_rgba(*txt._fillcolor)
            if txt._strokecolor:
                # if there's a stroke still to be applied, we need to call fill_preserve()
                # which still leaves this path as active
                ctx.fill_preserve()
                ctx.set_source_rgba(*txt._strokecolor)
                # now apply the stroke (stroke ends the path, we'd use stroke_preserve()
                # for further operations if needed)
                ctx.stroke()
            else:
                # if there isn't a stroke, use plain fill() to close the path
                ctx.fill()
        elif txt._strokecolor:
            # if there's no fill, apply stroke only
            ctx.set_source_rgba(*txt._strokecolor)
            ctx.stroke()
        else:
            print _("Warning: Canvas object had no fill or stroke values")

        txt.pang_ctx.update_layout(txt.layout)
        txt.pang_ctx.show_layout(txt.layout)



    def drawimage(self,image,ctx=None):
        if not ctx:
            ctx = self._context
        ctx.set_source_surface (image.imagesurface, image.x, image.y)
        ctx.rectangle(image.x, image.y, image.width, image.height)
        ctx.fill()

    def drawpath(self,path,ctx=None):
        '''Passes the path to a Cairo context.'''
        if not isinstance(path, shoebot.data.BezierPath):
            raise ShoebotError(_("drawpath(): Expecting a BezierPath, got %s") % (path))

        if not ctx:
            ctx = self._context

        if path._strokewidth:
            ctx.set_line_width(path._strokewidth)

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
            elif cmd == ARC:
                ctx.arc(*values)
            elif cmd == CLOSE:
                ctx.close_path()
            elif cmd == ELLIPSE:
                x, y, w, h = values
                ctx.save()
                ctx.translate (x + w / 2., y + h / 2.)
                ctx.scale (w / 2., h / 2.)
                ctx.arc (0., 0., 1., 0., 2 * pi)
                ctx.restore()
            else:
                raise ShoebotError(_("PathElement(): error parsing path element command (got '%s')") % (cmd))

        if path._fillcolor:
            ctx.set_source_rgba(*path._fillcolor)
            if path._strokecolor:
                # if there's a stroke still to be applied, we need to call fill_preserve()
                # which still leaves this path as active
                ctx.fill_preserve()
                ctx.set_source_rgba(*path._strokecolor)
                # now apply the stroke (stroke ends the path, we'd use stroke_preserve()
                # for further operations if needed)
                ctx.stroke()
            else:
                # if there isn't a stroke, use plain fill() to close the path
                ctx.fill()
        elif path._strokecolor:
            # if there's no fill, apply stroke only
            ctx.set_source_rgba(*path._strokecolor)
            ctx.stroke()
        else:
            print _("Warning: Canvas object had no fill or stroke values")

    def finish(self):
        if isinstance(self._surface, (cairo.SVGSurface, cairo.PSSurface, cairo.PDFSurface)):
            self._context.show_page()
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

            if ext not in EXTENSIONS:
                raise ShoebotError('CairoCanvas.output: Invalid filename extension')

            output_surface = util.surfacefromfilename(filename, self.bot.WIDTH, self.bot.HEIGHT)
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
            ctx = target
            self.draw(ctx)
        elif isinstance(target, cairo.Surface):
            ctx = target.get_context()
            self.draw(ctx)


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

