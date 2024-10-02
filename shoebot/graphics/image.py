from .grob import Grob
from ..core.state.image import ImageState



CENTER = "center"
CORNER = "corner"



class Image(Grob):

    def __init__(self, context, path=None, x=0, y=0, width=None, height=None, alpha=1.0, image=None, data=None):

        if image:
            raise NotImplementedError("Passing in existing image")

        if data:
            raise NotImplementedError("Passing in existing data")

        self._context = context
        self.__state__ = ImageState.from_kwargs(path=path,
                                                x=x,
                                                y=y,
                                                width=width,
                                                height=height,
                                                alpha=alpha)

    x = ImageState.readwrite_property()
    y = ImageState.readwrite_property()
    width = ImageState.readwrite_property()
    height = ImageState.readwrite_property()
    alpha = ImageState.readwrite_property()
    path = ImageState.readonly_property()

    def draw(self):
        self._context.draw_image(self)
