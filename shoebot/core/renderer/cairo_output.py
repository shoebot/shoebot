import cairo

from shoebot.core.renderer import CairoRenderer
from shoebot.core.renderer.output import FileOutput, Output


class CairoFileOutput(FileOutput):
    """
    Manage a cairo surface that will be written to a file.

    PDF, PS and SVG use the corresponding cairo surface type.
    PNG uses an ImageSurface with the ARGB32 pixel format and calls write_to_png.
    """
    SUPPORTED_FILE_FORMATS = ["png", "pdf", "ps", "svg"]

    def __init__(self, filename_template):
        super().__init__(filename_template)

    # TODO allow parameters about pixel format: we may want formats other than ARGB32

    def create_renderer(self, *dimensions):
        """
        Create a cairo Context and Surface for the given dimensions.+
        """
        # TODO - can this be def create_renderer(self, *dimensions) -> CairoRenderer
        self.dimensions = dimensions
        if self.format == "png":
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *dimensions)
        elif self.format == "pdf":
            surface = cairo.PDFSurface(self.filename_template, *dimensions)
        elif self.format == "ps":
            surface = cairo.PSSurface(self.filename_template, *dimensions)
        elif self.format == "svg":
            surface = cairo.SVGSurface(self.filename_template, *dimensions)
        else:
            raise ValueError("Unknown format: %s" % self.format)
        ctx = cairo.Context(surface)
        self.renderer = CairoRenderer(ctx)

    def destroy_renderer(self):
        """
        If the format is png then write the surface to the filename template, for other formats
        """
        if self.format == "png":
            ctx = self.renderer.target
            surface = ctx.get_target()
            surface.write_to_png(self.filename_template)
            del ctx
            del surface

        super().destroy_renderer()


class CairoMemorySurfaceOutput(Output):
    def create_renderer(self, surface):
        self.renderer = CairoRenderer(cairo.Context(surface))

    def destroy_renderer(self):
        del self.renderer