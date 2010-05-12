from cairo import SVGSurface

_svg_surface = None
def RecordingSurface(*size):
    '''
    We don't have RecordingSurfaces until cairo 1.10, so this kludge is used

    SVGSurfaces are created, but to stop them ever attempting to output, they
    are kept in a dict.

    When a surface is needed, create_similar is called to get a Surface from
    the SVGSurface of the same size
    '''
    if os.name == 'nt':
        fobj = 'nul'
    else:
        fobj = None
    if _svg_surface is None:
        _svg_surface = SVGSurface(fobj, 0, 0)
    return _svg_surface.create_similar(cairo.CONTENT_COLOR_ALPHA, *size)

