from shoebot.core.backend import cairo, gi, driver
from shoebot.data import _copy_attrs

import array
from StringIO import StringIO
import os.path

from PIL import Image as PILImage

try:
    gi.require_version('Rsvg', '2.0')
    from gi.repository import Rsvg
except ImportError, ValueError:
    Rsvg = None

from shoebot.data import Grob, ColorMixin

CENTER = 'center'
CORNER = 'corner'


class SurfaceRef(object):
    ''' Cannot have a weakref to a cairo surface, so wrapper is used '''
    def __init__(self, surface):
        self.surface = surface


class Image(Grob, ColorMixin):
    _surface_cache = {}   # Did have a WeakValueDictionary here but this caused a memory leak of images every frame
    _state_attributes = {'transform', 'pathmode'}  # NBX uses transform and transformmode here

    def __init__(self, bot, path=None, x=0, y=0, width=None, height=None, alpha=1.0, data=None, pathmode=CORNER, **kwargs):
        Grob.__init__(self, bot)
        ColorMixin.__init__(self, **kwargs)

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.alpha = alpha
        self.path = path
        self.data = data
        self._pathmode = pathmode
        sh = sw = None  # Surface Height and Width

        if isinstance(self.data, cairo.ImageSurface):
            sw = self.data.get_width()
            sh = self.data.get_height()
            self._imagesurface = self.data
        else:
            # checks if image data is passed in command call, in this case it wraps
            # the data in a StringIO oject in order to use it as a file
            # the data itself must contain an entire image, not just pixel data
            # it can be useful for example to retrieve images from the web without
            # writing temp files (e.g. using nodebox's web library, see example 1 of the library)
            # if no data is passed the path is used to open a local file
            if self.data is None:
                surfaceref = self._surface_cache.get(path)
                if surfaceref:
                    imagesurface = surfaceref.surface
                    sw = imagesurface.get_width()
                    sh = imagesurface.get_height()
                elif os.path.splitext(path)[1].lower() == '.svg' and Rsvg is not None:
                    handle = Rsvg.Handle()
                    svg = handle.new_from_file(path)
                    dimensions = svg.get_dimensions()
                    sw = dimensions.width
                    sh = dimensions.height
                    imagesurface = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, (0, 0, sw, sh))
                    ctx = cairo.Context(imagesurface)
                    pycairo_ctx = driver.ensure_pycairo_context(ctx)
                    svg.render_cairo(pycairo_ctx)
                elif os.path.splitext(path)[1].lower() == '.png':
                    imagesurface = cairo.ImageSurface.create_from_png(path)
                    sw = imagesurface.get_width()
                    sh = imagesurface.get_height()
                else:
                    img = PILImage.open(path)

                    if img.mode != 'RGBA':
                        img = img.convert("RGBA")

                    sw, sh = img.size
                    # Would be nice to not have to do some of these conversions :-\
                    bgra_data = img.tobytes('raw', 'BGRA', 0, 1)
                    bgra_array = array.array('B', bgra_data)
                    imagesurface = cairo.ImageSurface.create_for_data(bgra_array, cairo.FORMAT_ARGB32, sw, sh, sw * 4)

                self._surface_cache[path] = SurfaceRef(imagesurface)
            else:
                img = PILImage.open(StringIO(self.data))

                if img.mode != 'RGBA':
                    img = img.convert("RGBA")

                sw, sh = img.size
                # Would be nice to not have to do some of these conversions :-\
                bgra_data = img.tobytes('raw', 'BGRA', 0, 1)
                bgra_array = array.array('B', bgra_data)
                imagesurface = cairo.ImageSurface.create_for_data(bgra_array, cairo.FORMAT_ARGB32, sw, sh, sw * 4)

            if width is not None or height is not None:
                if width:
                    wscale = float(width) / sw
                else:
                    wscale = 1.0
                if height:
                    hscale = float(height) / sh
                else:
                    if width:
                        hscale = wscale
                    else:
                        hscale = 1.0
                self._transform.scale(wscale, hscale)

            self.width = width or sw
            self.height = height or sh
            self._imagesurface = imagesurface

        self._deferred_render()

    def _render(self, ctx):
        if self.width and self.height:
            # Go to initial point (CORNER or CENTER):
            transform = self._call_transform_mode(self._transform)

            ctx.set_matrix(transform)
            ctx.translate(self.x, self.y)
            ctx.set_source_surface(self._imagesurface)
            ctx.paint()

    def draw(self):
        self._deferred_render()

    def _get_center(self):
        '''Returns the center point of the path, disregarding transforms.
        '''
        x = (self.x + self.width / 2)
        y = (self.y + self.height / 2)
        return (x, y)
    center = property(_get_center)

    def copy(self):
        p = self.__class__(self._bot, self.path, self.x, self.y, self.width, self.height)
        _copy_attrs(self._bot, p, self.state_attributes)
        return p
