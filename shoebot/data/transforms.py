#
# transforms.py from old shoebot
#

import sys

from shoebot.core.backend import cairo
from math import sin, cos
from bezier import BezierPath

TRANSFORMS = ['translate', 'scale', 'rotate', 'skew', 'push', 'pop']
CENTER = 'center'
CORNER = 'corner'
CORNERS = "corners"

import locale, gettext
APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
#gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext


class Transform:
    '''
    This class represents a stack of transformations. Supported operations are
    translation, scaling, rotation and skewing.

    '''
    def __init__(self, transform=None):
        self.stack = []
        if transform is None:
            pass
        elif isinstance(transform, Transform):
            self.append(transform)
        elif isinstance(transform, (list, tuple)):
            matrix = tuple(transform)
            t = cairo.Matrix(*matrix)
            self.append(t)
        elif isinstance(transform, cairo.Matrix):
            self.append(transform)
        else:
            raise ValueError, _("Transform: Don't know how to handle transform %s.") % transform

    def translate(self, x, y):
        t = ('translate', x, y)
        self.stack.append(t)

    def scale(self, x, y):
        t = ('scale', x, y)
        self.stack.append(t)

    def rotate(self, a):
        t = ('rotate', a)
        self.stack.append(t)

    def skew(self, x, y):
        t = ('skew', x, y)
        self.stack.append(t)

    def push(self):
        t = ('push',)
        self.stack.append(t)

    def pop(self):
        t = ('pop',)
        self.stack.append(t)


    def append(self, t):
        if isinstance(t, Transform):
            for item in t.stack:
                self.stack.append(item)
        elif isinstance(t, cairo.Matrix):
            self.stack.append(t)
        else:
            raise ValueError(_("Transform: Can only append Transforms or Cairo matrices (got %s)") % (t))

    def prepend(self,t):
        if isinstance(t, Transform):
            newstack = []
            for item in t.stack:
                newstack.append(item)
            for item in self.stack:
                newstack.append(item)
            self.stack = newstack
        elif isinstance(t, cairo.Matrix):
            self.stack.insert(0,t)
        else:
            raise ValueError(_("Transform: Can only append Transforms or Cairo matrices (got %s)") % (t))

    def copy(self):
        return self.__class__(self)
    def __iter__(self):
        for value in self.stack:
            yield value
    ### calculates tranformation matrix
    def get_matrix_with_center(self,x,y,mode):
        m = cairo.Matrix()
        centerx =x
        centery = y
        m_archived = []

        for trans in self.stack:
            if isinstance(trans, cairo.Matrix):
                # multiply matrix
                m *= trans
            elif isinstance(trans, tuple) and trans[0] in TRANSFORMS:
                # parse transform command
                cmd = trans[0]
                args = trans[1:]
                t = cairo.Matrix()

                if cmd == 'translate':
                    xt = args[0]
                    yt = args[1]
                    m.translate(xt,yt)
                elif cmd == 'rotate':
                    if mode == 'corner':
                        # apply existing transform to cornerpoint
                        deltax,deltay = m.transform_point(0,0)
                        a = args[0]
                        ct = cos(a)
                        st = sin(a)
                        m *= cairo.Matrix(ct, st, -st, ct,deltax-(ct*deltax)+(st*deltay),deltay-(st*deltax)-(ct*deltay))
                    elif mode == 'center':
                        # apply existing transform to centerpoint
                        deltax,deltay = m.transform_point(centerx,centery)
                        a = args[0]
                        ct = cos(a)
                        st = sin(a)
                        m *= cairo.Matrix(ct, st, -st, ct,deltax-(ct*deltax)+(st*deltay),deltay-(st*deltax)-(ct*deltay))
                elif cmd == 'scale':
                    if mode == 'corner':
                        t.scale(args[0], args[1])
                        m *= t
                    elif mode == 'center':
                        # apply existing transform to centerpoint
                        deltax,deltay = m.transform_point(centerx,centery)
                        x, y = args
                        m1 = cairo.Matrix()
                        m2 = cairo.Matrix()
                        m1.translate(-deltax, -deltay)
                        m2.translate(deltax, deltay)
                        m *= m1
                        m *= cairo.Matrix(x,0,0,y,0,0)
                        m *= m2

                elif cmd == 'skew':
                    if mode == 'corner':
                        x, y = args
                        ## TODO: x and y should be the tangent of an angle
                        t *= cairo.Matrix(1,0,x,1,0,0)
                        t *= cairo.Matrix(1,y,0,1,0,0)
                        m *= t
                    elif mode == 'center':
                        # apply existing transform to centerpoint
                        deltax,deltay = m.transform_point(centerx,centery)
                        x,y = args
                        m1 = cairo.Matrix()
                        m2 = cairo.Matrix()
                        m1.translate(-deltax, -deltay)
                        m2.translate(deltax, deltay)
                        t *= m
                        t *= m1
                        t *= cairo.Matrix(1,0,x,1,0,0)
                        t *= cairo.Matrix(1,y,0,1,0,0)
                        t *= m2
                        m = t
                elif cmd == 'push':
                    m_archived.append(m)
                elif cmd == 'pop':
                    m = m_archived.pop()

        return m

    def get_matrix(self):
        '''Returns this transform's matrix. Its centerpoint is presumed to be
        (0,0), which is the Cairo default.'''
        return self.get_matrix_with_center(0,0)



    def transformBezierPath(self, path):
        # From nodebox
        if isinstance(path, BezierPath):
            path = path.copy()
        else:
            raise ValueError("Can only transform BezierPaths")

        for point in path:
            print point
        #path._nsBezierPath = self._nsAffineTransform.transformBezierPath_(path._nsBezierPath)
        return path


class TransformMixin(object):

    """Mixin class for transformation support.
    Adds the _transform and _transformmode attributes to the class."""

    def __init__(self):
        self._reset()

    def _reset(self):
        self._transform = Transform()
        self._transformmode = CENTER

    def _get_transform(self):
        return self._transform
    def _set_transform(self, transform):
        self._transform = Transform(transform)
    transform = property(_get_transform, _set_transform)

    def _get_transformmode(self):
        return self._transformmode
    def _set_transformmode(self, mode):
        self._transformmode = mode
    transformmode = property(_get_transformmode, _set_transformmode)

    def reset(self):
        self._transform = Transform()
    def rotate(self, degrees=0, radians=0):
        self._transform.rotate(degrees,radians)
    def translate(self, x=0, y=0):
        self._transform.translate(x,y)
    def scale(self, x=1, y=None):
        self._transform.scale(x,y)
    def skew(self, x=0, y=0):
        self._transform.skew(x,y)


