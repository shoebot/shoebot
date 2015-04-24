# TODO, Move 'bot' out of here, push responsibility back to 'Nodebox' and other grammars,
#       Enabling seperation of BezierPath etc

import cairocffi as cairo

CENTER = 'center'
CORNER = 'corner'


class Grob(object):
    '''A GRaphic OBject is the base class for all DrawingPrimitives.'''

    def __init__(self, bot):
        # Takes bot rather than canvas for compatibility with libraries - e.g. the colors library
        self._canvas = canvas = bot._canvas
        self._bot = bot
        self._set_mode(canvas.mode)
        self._transform = cairo.Matrix(*canvas.transform)

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

    def _get_pathmode(self):
        '''Return pathmode or get it from self._canvas'''
        if self._pathmode is not None:
            return self._pathmode
        else:
            return self._canvas.pathmode

    def _get_center(self):
        '''Implementations must return the x, y of their center'''
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
        Pass a function to the canvas for deferred rendering,
        defaults to self._render
        '''
        self._canvas.deferred_render(render_func or self._render)

    def _render(self, ctx):
        '''For overriding by GRaphicOBjects'''
        raise NotImplementedError()

