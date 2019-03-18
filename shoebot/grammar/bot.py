#!/usr/bin/env python2

# This file is part of Shoebot.
# Copyright (C) 2007-2009 the Shoebot authors
# See the COPYING file for the full license text.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
#   The name of the author may not be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED
#   WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#   MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
#   EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#   OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""
Drawbot and Nodebot are similar grammars, so they both inherit from Bot
"""

import sys
import os

from shoebot.core.backend import cairo
from shoebot.data import BezierPath, EndClip, Color, Text, Variable, \
                         Image, ClippingPath, \
                         NUMBER, TEXT, BOOLEAN, BUTTON, \
                         ShoebotError, \
                         RGB, HSB, \
                         CENTER, CORNER, CORNERS

from grammar import Grammar

from pkg_resources import resource_filename, Requirement
from glob import glob
import random as r

import locale
import gettext

SBOT_ROOT = resource_filename(Requirement.parse("shoebot"), "")
APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
# gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext

LIB_DIRS = [
    os.path.join(SBOT_ROOT, 'local', 'share', 'shoebot', 'lib'),
    os.path.join(SBOT_ROOT, 'lib'),
    os.path.join(SBOT_ROOT, 'share', 'shoebot', 'lib'),
    os.path.join(sys.prefix, 'share', 'shoebot', 'lib')]
for LIB_DIR in LIB_DIRS:
    if os.path.isdir(LIB_DIR):
        sys.path.append(LIB_DIR)

TOP_LEFT = 1
BOTTOM_LEFT = 2


class Bot(Grammar):
    '''
    The Parts of the Grammar common to DrawBot, NodeBot and ShoeBot.
    '''
    RGB = RGB
    HSB = HSB

    LEFT = 'left'
    RIGHT = 'right'

    CENTER = CENTER
    CORNER = CORNER
    CORNERS = CORNERS

    LEFT = 'left'
    RIGHT = 'right'
    JUSTIFY = 'justify'

    NUMBER = NUMBER
    TEXT = TEXT
    BOOLEAN = BOOLEAN
    BUTTON = BUTTON

    inch = 72
    cm = 28.3465
    mm = 2.8346

    # Default mouse values
    MOUSEX = -1
    MOUSEY = -1
    mousedown = False

    # Default key values
    key = '-'
    keycode = 0
    keydown = False

    def __init__(self, canvas, namespace=None, vars=None):
        '''
        :param canvas: Canvas implementation for output.
        :param namespace: Optionally specify a dict to inject as namespace
        :param vars: Optional dict containing initial values for variables
        '''
        Grammar.__init__(self, canvas, namespace=namespace, vars=vars)
        canvas.set_bot(self)

        self._autoclosepath = True
        self._path = None

        if self._input_device:
            # Get constants like KEY_DOWN, KEY_LEFT
            for key_name, value in self._input_device.get_key_map().items():
                self._namespace[key_name] = value
                setattr(self, key_name, value)

        self._canvas.size = None
        self._frame = 1
        self._set_initial_defaults() ### TODO Look at these

    def _set_initial_defaults(self):
        '''Set the default values. Called at __init__ and at the end of run(),
        do that new draw loop iterations don't take up values left over by the
        previous one.'''
        DEFAULT_WIDTH, DEFAULT_HEIGHT = self._canvas.DEFAULT_SIZE
        self.WIDTH = self._namespace.get('WIDTH', DEFAULT_WIDTH)
        self.HEIGHT = self._namespace.get('HEIGHT', DEFAULT_WIDTH)
        if 'WIDTH' in self._namespace or 'HEIGHT' in self._namespace:
            self.size(w=self._namespace.get('WIDTH'), h=self._namespace.get('HEIGHT'))

        self._transformmode = Bot.CENTER

        self._canvas.settings(
            fontfile="assets/notcouriersans.ttf",
            fontsize=16,
            align=Bot.LEFT,
            lineheight=1,
            fillcolor=self.color(.2),
            strokecolor=None,
            strokewidth=1.0,
            background=self.color(1, 1, 1))

    def _set_dynamic_vars(self):
        self._namespace['FRAME'] = self._frame

    # Input GUI callbacks

    def _mouse_button_down(self, button):
        '''GUI callback for mouse button down'''
        self._namespace['mousedown'] = True

    def _mouse_button_up(self, button):
        '''GUI callback for mouse button up'''
        self._namespace['mousedown'] = self._input_device.mouse_down

    def _mouse_pointer_moved(self, x, y):
        '''GUI callback for mouse moved'''
        self._namespace['MOUSEX'] = x
        self._namespace['MOUSEY'] = y

    def _key_pressed(self, key, keycode):
        '''GUI callback for key pressed'''
        self._namespace['key'] = key
        self._namespace['keycode'] = keycode
        self._namespace['keydown'] = True

    def _key_released(self, key, keycode):
        '''GUI callback for key released'''
        self._namespace['keydown'] = self._input_device.key_down

    # Functions for override #####

    def setup(self):
        """ For override by user sketch """
        pass

    def draw(self):
        """ For override by user sketch """
        self._dynamic = False

    # Classes #####

    def _makeInstance(self, clazz, args, kwargs):
        '''Creates an instance of a class defined in this document.
           This method sets the context of the object to the current context.'''
        inst = clazz(self, *args, **kwargs)
        return inst

    def _makeColorableInstance(self, clazz, args, kwargs):
        """
        Create an object, if fill, stroke or strokewidth
        is not specified, get them from the _canvas

        :param clazz:
        :param args:
        :param kwargs:
        :return:
        """
        kwargs = dict(kwargs)

        fill = kwargs.get('fill', self._canvas.fillcolor)
        if not isinstance(fill, Color):
            fill = Color(fill, mode='rgb', color_range=1)
        kwargs['fill'] = fill

        stroke = kwargs.get('stroke', self._canvas.strokecolor)
        if not isinstance(stroke, Color):
            stroke = Color(stroke, mode='rgb', color_range=1)
        kwargs['stroke'] = stroke

        kwargs['strokewidth'] = kwargs.get('strokewidth', self._canvas.strokewidth)
        inst = clazz(self, *args, **kwargs)
        return inst

    def EndClip(self, *args, **kwargs):
        return self._makeColorableInstance(EndClip, args, kwargs)

    def BezierPath(self, *args, **kwargs):
        return self._makeColorableInstance(BezierPath, args, kwargs)

    def ClippingPath(self, *args, **kwargs):
        return self._makeColorableInstance(ClippingPath, args, kwargs)

    def Rect(self, *args, **kwargs):
        return self._makeColorableInstance(Rect, args, kwargs)

    def Oval(self, *args, **kwargs):
        return self._makeColorableInstance(Oval, args, kwargs)

    def Ellipse(self, *args, **kwargs):
        return self._makeColorableInstance(Ellipse, args, kwargs)

    def Color(self, *args, **kwargs):
        return Color(*args, **kwargs)

    def Image(self, *args, **kwargs):
        return self._makeColorableInstance(Image, args, kwargs)

    def Text(self, *args, **kwargs):
        return self._makeColorableInstance(Text, args, kwargs)

    # Variables #####

    def var(self, name, type, default=None, min=0, max=255, value=None, step=None):
        v = Variable(name, type, default=default, min=min, max=max, value=value, step=step)
        return self._addvar(v)

    # Utility #####

    def color(self, *args):
        '''
        :param args: color in a supported format.

        :return: Color object containing the color.
        '''
        return self.Color(mode=self.color_mode, color_range=self.color_range, *args)

    choice = r.choice

    def random(self, v1=None, v2=None):
        # ipsis verbis from Nodebox
        if v1 is not None and v2 is None:
            if isinstance(v1, float):
                return r.random() * v1
            else:
                return int(r.random() * v1)
        elif v1 is not None and v2 is not None:
            if isinstance(v1, float) or isinstance(v2, float):
                start = min(v1, v2)
                end = max(v1, v2)
                return start + r.random() * (end - start)
            else:
                start = min(v1, v2)
                end = max(v1, v2) + 1
                return int(start + r.random() * (end - start))
        else:
            # No values means 0.0 -> 1.0
            return r.random()

    def grid(self, cols, rows, colSize=1, rowSize=1, shuffled=False):
        """Returns an iterator that contains coordinate tuples.
        The grid can be used to quickly create grid-like structures.
        A common way to use them is:
            for x, y in grid(10,10,12,12):
                rect(x,y, 10,10)
        """
        # Taken ipsis verbis from Nodebox
        from random import shuffle
        rowRange = range(int(rows))
        colRange = range(int(cols))
        if (shuffled):
            shuffle(rowRange)
            shuffle(colRange)
        for y in rowRange:
            for x in colRange:
                yield (x * colSize, y * rowSize)

    def files(self, path="*"):
        """Returns a list of files.
        You can use wildcards to specify which files to pick, e.g.
            f = files('*.gif')

        :param path: wildcard to use in file list.
        """
        # Taken ipsis verbis from Nodebox
        return glob(path)

    def snapshot(self, target=None, defer=None, autonumber=False):
        '''Save the contents of current surface into a file or cairo surface/context

        :param filename: Can be a filename or a Cairo surface.
        :param defer: If true, buffering/threading may be employed however output will not be immediate.
        :param autonumber: If true then a number will be appended to the filename.
        '''
        if autonumber:
            file_number = self._frame
        else:
            file_number = None

        if isinstance(target, cairo.Surface):
            # snapshot to Cairo surface
            if defer is None:
                self._canvas.snapshot(surface, defer)
                defer = False
            ctx = cairo.Context(target)
            # this used to be self._canvas.snapshot, but I couldn't make it work.
            # self._canvas.snapshot(target, defer)
            # TODO: check if this breaks when taking more than 1 snapshot
            self._canvas._drawqueue.render(ctx)
            return
        elif target is None:
            # If nothing specified, use a default filename from the script name
            script_file = self._namespace.get('__file__')
            if script_file:
                target = os.path.splitext(script_file)[0] + '.svg'
                file_number = True

        if target:
            # snapshot to file, target is a filename
            if defer is None:
                defer = True
            self._canvas.snapshot(target, defer=defer, file_number=file_number)
        else:
            raise ShoebotError('No image saved')

    def show(self, format='png', as_data=False):
        '''Returns an Image object of the current surface. Used for displaying
        output in Jupyter notebooks. Adapted from the cairo-jupyter project.'''

        from io import BytesIO

        b = BytesIO()

        if format == 'png':
            from IPython.display import Image
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.WIDTH, self.HEIGHT)
            self.snapshot(surface)
            surface.write_to_png(b)
            b.seek(0)
            data = b.read()
            if as_data:
                return data
            else:
                return Image(data)
        elif format == 'svg':
            from IPython.display import SVG
            surface = cairo.SVGSurface(b, self.WIDTH, self.HEIGHT)
            surface.finish()
            b.seek(0)
            data = b.read()
            if as_data:
                return data
            else:
                return SVG(data)

    def ximport(self, libName):
        '''
        Import Nodebox libraries.

        The libraries get _ctx, which provides
        them with the nodebox API.

        :param libName: Library name to import
        '''
        # from Nodebox
        lib = __import__(libName)
        self._namespace[libName] = lib
        lib._ctx = self
        return lib

    # Core functions ####

    def size(self, w=None, h=None):
        '''Set the canvas size

        Only the first call will actually be effective.

        :param w: Width
        :param h: height
        '''

        if not w:
            w = self._canvas.width
        if not h:
            h = self._canvas.height
        if not w and not h:
            return (self._canvas.width, self._canvas.height)

        # FIXME: Updating in all these places seems a bit hacky
        w, h = self._canvas.set_size((w, h))
        self._namespace['WIDTH'] = w
        self._namespace['HEIGHT'] = h
        self.WIDTH = w  # Added to make evolution example work
        self.HEIGHT = h  # Added to make evolution example work

    def speed(self, framerate=None):
        '''Set animation framerate.

        :param framerate: Frames per second to run bot.
        :return: Current framerate of animation.
        '''
        if framerate is not None:
            self._speed = framerate
            self._dynamic = True
        else:
            return self._speed

    @property
    def FRAME(self):
        return self._frame
