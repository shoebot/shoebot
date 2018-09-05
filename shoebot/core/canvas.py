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
'''Abstract canvas class'''

from collections import deque
from abc import ABCMeta, abstractproperty
import sys
import locale
import gettext
from shoebot.core.drawqueue import DrawQueue

APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
# gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext

CENTER = 'center'
CORNER = 'corner'

TOP_LEFT = 1
BOTTOM_LEFT = 2


class Canvas(object):
    __metaclass__ = ABCMeta

    DEFAULT_SIZE = 400, 400
    DEFAULT_MODE = CENTER

    ''' Abstract canvas class '''
    def __init__(self, sink):
        # Construct sink class:
        self.sink = sink

        self.finished = False
        self.color_range = 1
        self.color_mode = 1
        self.path_mode = CORNER
        self.size = None
        self.reset_canvas()

    def set_bot(self, bot):
        ''' Bot must be set before running '''
        self.bot = bot
        self.sink.set_bot(bot)

    def get_input_device(self):
        ''' Overrides can return actual input device '''
        return None

    def initial_drawqueue(self):
        '''
        Override to create use special kinds of draw queue
        '''
        return DrawQueue()

    def initial_transform(self):
        '''
        Must be overriden to create initial transform matrix
        '''
        pass

    @abstractproperty
    def reset_drawqueue(self):
        pass

    @abstractproperty
    def reset_transform(self):
        pass

    def reset_canvas(self):
        self.reset_transform()
        self.reset_drawqueue()
        self.matrix_stack = deque()

    def settings(self, **kwargs):
        '''
        Pass a load of settings into the canvas
        '''
        for k, v in kwargs.items():
            setattr(self, k, v)

    def size_or_default(self):
        '''
        If size is not set, otherwise set size to DEFAULT_SIZE
        and return it.

        This means, only the first call to size() is valid.
        '''
        if not self.size:
            self.size = self.DEFAULT_SIZE
        return self.size

    def set_size(self, size):
        '''
        Size is only set the first time it is called

        Size that is set is returned
        '''
        if self.size is None:
            self.size = size
            return size
        else:
            return self.size

    def get_width(self):
        if self.size is not None:
            return self.size[0]
        else:
            return self.DEFAULT_SIZE[0]

    def get_height(self):
        if self.size is not None:
            return self.size[1]
        else:
            return self.DEFAULT_SIZE[1]

    def snapshot(self, target, defer=True, file_number=None):
        '''
        Ask the drawqueue to output to target.

        target can be anything supported by the combination
        of canvas implementation and drawqueue implmentation.

        If target is not supported then an exception is thrown.
        '''
        output_func = self.output_closure(target, file_number)
        if defer:
            self._drawqueue.append(output_func)
        else:
            self._drawqueue.append_immediate(output_func)

    def flush(self, frame):
        '''
        Passes the drawqueue to the sink for rendering
        '''
        self.sink.render(self.size_or_default(), frame, self._drawqueue)
        self.reset_drawqueue()

    def deferred_render(self, render_func):
        '''Add a render function to the queue for rendering later'''
        self._drawqueue.append(render_func)

    width = property(get_width)
    height = property(get_height)
