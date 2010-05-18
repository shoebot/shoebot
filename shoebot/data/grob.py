import cairo

class Grob:
    '''A GRaphic OBject is the base class for all DrawingPrimitives.'''

    def __init__(self, canvas):
        self._canvas = canvas
        self._drawqueue = canvas.drawqueue

    def _get_center():
        raise NotImplementedError()

    def _center_transform(self, transform):
        ''''
        Works like setupTransform of a version of java nodebox
        http://dev.nodebox.net/browser/nodebox-java/branches/rewrite/src/java/net/nodebox/graphics/Grob.java
        '''
        dx, dy = self._get_center()
        t = cairo.Matrix()
        t.translate(dx, dy)
        t = transform * t
        t.translate(-dx, -dy)
        return t

    def _corner_transform(self, transform):
        '''
        CORNER is the default, so we just return the transform
        '''
        return transform

    def _stamp(self, render_func=None):
        self._transform = cairo.Matrix(*self._canvas.transform)
        self._drawqueue.append(render_func or self._render)

    def _render(self, ctx):
        raise NotImplementedError()
        pass
