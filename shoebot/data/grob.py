import cairo

CENTER = 'center'
CORNER = 'corner'

class Grob:
    '''A GRaphic OBject is the base class for all DrawingPrimitives.'''

    def __init__(self, canvas):
        self._canvas = canvas
        self._drawqueue = canvas.drawqueue
        self._set_mode(canvas.mode)
        self._transform = cairo.Matrix(*self._canvas.transform)

    def _set_mode(self, mode):
        '''
        Sets call_transform_mode to point to the
        center_transform or corner_transform
        '''
        if mode == CENTER:
            self._call_transform_mode = self._center_transform
        elif mode == CORNER:
            self._call_transform_mode = self._corner_transform
        else:
            raise ValueError('mode must be CENTER or CORNER')

    def _get_center():
        raise NotImplementedError()

    def _call_transform_mode(self):
        '''
        This should never get called:
        set mode, changes the value of this to point

        corner_transform or center_transform
        '''
        raise NotImplementedError('_call_transform_mode called without mode set!')

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

    def _deferred_render(self, render_func=None):
        '''
        Add a render function to the draw queue, defaults to self._render'''
        self._drawqueue.append(render_func or self._render)

    def _render(self, ctx):
        '''For overriding by GRaphicOBjects'''
        raise NotImplementedError()

