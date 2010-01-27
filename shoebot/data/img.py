from shoebot.data import _copy_attrs

from StringIO import StringIO
import cairo
import numpy
import Image as PILImage
from shoebot.data import Grob, TransformMixin, ColorMixin

class Image(Grob, TransformMixin, ColorMixin):
    stateAttributes = ('_transform', '_transformmode')
    kwargs = ()

    def __init__(self, bot, path, x, y, width=None, height=None, alpha=1.0, data=None, **kwargs):
        self._bot = bot
        #super(Image, self).__init__(self._bot)
        TransformMixin.__init__(self)
        ColorMixin.__init__(self, **kwargs)

        if self._bot:
            _copy_attrs(self._bot, self, self.stateAttributes)

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.alpha = alpha
        self.path = path
        self.data = data
        
        if isinstance(self.data, cairo.ImageSurface):
            self.width = self.data.get_width()
            self.height = self.data.get_height()
            self.imagesurface = self.data
            
        else:

            # checks if image data is passed in command call, in this case it wraps
            # the data in a StringIO oject in order to use it as a file
            # the data itself must contain an entire image, not just pixel data
            # it can be useful for example to retrieve images from the web without 
            # writing temp files (e.g. using nodebox's web library, see example 1 of the library)
            # if no data is passed the path is used to open a local file
            if self.data is None:
                img = PILImage.open(self.path)
            elif self.data:
                img = PILImage.open(StringIO(self.data))

            # retrieves original image size
            Width, Height = img.size
            # if no width is given, it assumes the original image size, else image is resized
            if self.width is None:
                if self.height is None:
                    self.width = Width
                    self.height = Height
                else:
                    self.width = int(self.height*Width/Height)
                    size = self.width, self.height
                    img = img.resize(size, PILImage.ANTIALIAS)
            else:
                if self.height is None:
                    self.height = int(self.width*Height/Width)
                size = self.width, self.height
                img = img.resize(size, PILImage.ANTIALIAS)
            # check image mode and transforms it in ARGB32 for cairo, transforming it to string, swapping channels
            # and fills an array from numpy module, then passes it to cairo image surface constructor
            if img.mode == "RGBA":
                # swapping b and r channels with PIL
                r,g,b,a = img.split()
                img = PILImage.merge("RGBA",(b,g,r,a))             
                img_buffer = numpy.asarray(img)
                # resulting numpy array defaults to read-only, but cairo needs a writeable object
                # so we are forced to change a flag
                img_buffer.flags.writeable=True
                imagesurface = cairo.ImageSurface.create_for_data(img_buffer, cairo.FORMAT_ARGB32, self.width, self.height)
            elif img.mode == "RGB":
                img = img.convert('RGBA')
                r,g,b,a = img.split()
                img = PILImage.merge("RGBA",(b,g,r,a)) 
                img_buffer = numpy.asarray(img)
                img_buffer.flags.writeable=True            
                imagesurface = cairo.ImageSurface.create_for_data(img_buffer, cairo.FORMAT_ARGB32, self.width, self.height)            
            else:
                raise NotImplementedError(_("sorry, this image mode is not implemented yet"))
            #this is the item that will be drawn
            self.imagesurface = imagesurface


    def _get_center(self):
        '''Returns the center point of the path, disregarding transforms.
        '''
        x = (self.x+self.width/2)
        y = (self.y+self.height/2)
        return (x,y)
    center = property(_get_center)

    def copy(self):
        p = self.__class__(self._bot, self.path, self.x, self.y, self.width, self.height)
        _copy_attrs(self._bot, p, self.stateAttributes)
        return p


