import array
import os.path
from dataclasses import dataclass
from io import StringIO

from shoebot.core.backend import cairo, driver, gi

from .grob import Grob
from ..core.state.image import ImageState



CENTER = "center"
CORNER = "corner"



class Image(Grob):
    def __init__(self, context, **kwargs):
        self._context = context
        self.__state__ = ImageState.from_kwargs(**kwargs)

    x = ImageState.readwrite_property()
    y = ImageState.readwrite_property()
    width = ImageState.readwrite_property()
    height = ImageState.readwrite_property()
    alpha = ImageState.readwrite_property()
    path = ImageState.readonly_property()
    def draw(self):
        self._context.draw_image(self)
