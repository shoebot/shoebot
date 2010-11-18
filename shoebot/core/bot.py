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
'''Bot base class'''

import sys, os
import shoebot

from shoebot import ShoebotError, \
                    RGB, HSB, \
                    CENTER, CORNER, CORNERS

from shoebot.data import BezierPath, EndClip, Color, Text, Variable, \
                         Image, ClippingPath, \
                         NUMBER, TEXT, BOOLEAN, BUTTON

from grammar import Grammar

from glob import glob
import random as r
import traceback

import locale, gettext
APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
#gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext

import sys
LIB_DIRS = [
    os.path.join(sys.prefix, 'local', 'share', 'shoebot', 'lib'), 
    os.path.join(sys.prefix, 'share', 'shoebot', 'lib')]
for LIB_DIR in LIB_DIRS:
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

    def __init__(self, canvas, namespace = None):
        Grammar.__init__(self, canvas, namespace)
        self._autoclosepath = True
        self._path = None

        self._canvas.size = None
        self._frame = 1
        self._set_initial_defaults() ### TODO Look at these

        
    def _set_initial_defaults(self):
        '''Set the default values. Called at __init__ and at the end of run(),
        do that new draw loop iterations don't take up values left over by the
        previous one.'''
        self.WIDTH, self.HEIGHT = self._canvas.DEFAULT_SIZE

        self._transformmode = Bot.CENTER

        self._canvas.settings(
            fontfile = "assets/notcouriersans.ttf",
            fontsize = 16,
            align = Bot.LEFT,
            lineheight = 1,
            fillcolor = self.color(.2),
            strokecolor = None,
            strokewidth = 1.0,
            background = self.color(1, 1, 1))

    def _set_dynamic_vars(self):
        self._namespace['FRAME'] = self._frame


    # Get input

    def _mouse_button_down(self, button):
        self._namespace['mousedown'] = True

    def _mouse_button_up(self, button):
        self._namespace['mousedown'] = self._input_device.mouse_down

    def _mouse_pointer_moved(self, x, y):
        self._namespace['MOUSEX'] = x
        self._namespace['MOUSEY'] = y

    def _key_pressed(self, key, keycode):
        self._namespace['key'] = key
        self._namespace['keycode'] = keycode
        self._namespace['keydown'] = True

    def _key_released(self, key, keycode):
        self._namespace['keydown'] = self._input_device.key_down

    #### Functions for override

    def setup(self):
        """ For override by user sketch """
        pass

    def draw(self):
        """ For override by user sketch """
        self._dynamic = False

    #### Classes

    def _makeInstance(self, clazz, args, kwargs):
        '''Creates an instance of a class defined in this document.
           This method sets the context of the object to the current context.'''
        inst = clazz(self, *args, **kwargs)
        return inst

    def EndClip(self, *args, **kwargs):
        return self._makeInstance(EndClip, args, kwargs)
    def BezierPath(self, *args, **kwargs):
        return self._makeInstance(BezierPath, args, kwargs)
    def ClippingPath(self, *args, **kwargs):
        return self._makeInstance(ClippingPath, args, kwargs)
    def Rect(self, *args, **kwargs):
        return self._makeInstance(Rect, args, kwargs)
    def Oval(self, *args, **kwargs):
        return self._makeInstance(Oval, args, kwargs)
    def Ellipse(self, *args, **kwargs):
        return self._makeInstance(Ellipse, args, kwargs)
    def Color(self, *args, **kwargs):
        return self._makeInstance(Color, args, kwargs)
    def Image(self, *args, **kwargs):
        return self._makeInstance(Image, args, kwargs)
    def Text(self, *args, **kwargs):
        return self._makeInstance(Text, args, kwargs)

    #### Variables

    def var(self, name, type, default=None, min=0, max=255, value=None):
        v = Variable(name, type, default, min, max, value)
        return self._addvar(v)


    #### Utility

    def color(self, *args):
        return self.Color(mode = self.color_mode, color_range = self.color_range, *args)
        #return self.Color(*args)

    choice = r.choice

    def random(self,v1=None, v2=None):
        # ipsis verbis from Nodebox
        if v1 is not None and v2 is None:
            if isinstance(v1, float):
                return r.random() * v1
            else:
                return int(r.random() * v1)
        elif v1 != None and v2 != None:
            if isinstance(v1, float) or isinstance(v2, float):
                start = min(v1, v2)
                end = max(v1, v2)
                return start + r.random() * (end-start)
            else:
                start = min(v1, v2)
                end = max(v1, v2) + 1
                return int(start + r.random() * (end-start))
        else: # No values means 0.0 -> 1.0
            return r.random()

    def grid(self, cols, rows, colSize=1, rowSize=1, shuffled = False):
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
                yield (x*colSize,y*rowSize)

    def files(self, path="*"):
        """Returns a list of files.
        You can use wildcards to specify which files to pick, e.g.
            f = files('*.gif')
        """
        # Taken ipsis verbis from Nodebox
        return glob(path)

    def snapshot(self,filename=None, surface=None, defer=None, autonumber=False):
        '''Save the contents of current surface into a file or cairo surface/context

        Defer option:
        Decides whether the action needs to happen now or can happen later.

        Defer set to False
        Ensures that a file is written before returning, but can hamper performance.
        Usually you won't want to do this.

        For files defer defaults to True, and for Surfaces to False, this means
        writing files won't stop execution, while the surface will be ready when
        snapshot returns.
        
        The drawqueue will have to stop and render everything up until this
        point.
        '''
        if autonumber:
            file_number=self._frame
        else:
            file_number=None
        if surface:
            if defer is None:
                defer=False
            self._canvas.snapshot(surface, defer)
        if filename is None:
            # If nothing specied, we can see if a filename is available
            script_file = self._namespace.get('__file__')
            if script_file:
                filename = os.path.splitext(script_file)[0] + '.svg'
                file_number=True

        if filename:
            if defer is None:
                defer=True
            self._canvas.snapshot(filename, defer=defer, file_number=file_number)
            
            

    # from Nodebox, a function to import Nodebox libraries

    def ximport(self, libName):
        lib = __import__(libName)
        self._namespace[libName] = lib
        lib._ctx = self
        return lib


    #### Core functions

    def size(self, w = None, h = None):
        '''Sets the size of the canvas, and creates a Cairo surface and context.

        Only the first call will actually be effective.'''
        
        if not w:
            w = self._canvas.width
        if not h:
            h = self._canvas.height
        if not w and not h:
            return (self._canvas.width, self._canvas.height)

        w, h = self._canvas.set_size((w, h))
        self._namespace['WIDTH'] = w
        self._namespace['HEIGHT'] = h

    def speed(self, framerate):
        if framerate:
            self._speed = framerate
            self._dynamic = True
        else:
            return self._speed

