#!/usr/bin/env python

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

import sys
import shoebot
import locale, gettext
import math as _math
import cairo

APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
#gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext

CENTER = 'center'

TOP_LEFT = 1
BOTTOM_LEFT = 2

class Canvas:
    DEFAULT_SIZE = 400, 400
    DEFAULT_MODE = CENTER

    ''' Abstract canvas class '''
    def __init__(self, sink):
        self.sink = sink

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

    def reset_canvas(self):
        self.fillcolor = (0.5, 0.5, 0.5, 1.0)
        self.stroke = None
        self.strokewidth = 1.0
        self.strokecolor = None
        self.background = (1, 1, 1, 1)

        self.reset_transform()
        self.reset_drawqueue()

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
        if self.size != None:
            return self.size[0]
        else:
            return self.DEFAULT_SIZE[0]

    def get_height(self):
        if self.size != None:
            return self.size[1]
        else:
            return self.DEFAULT_SIZE[1]

    def output(self, target, immediate=False, file_number=None):
        '''
        Ask the drawqueue to output to target.

        target can be anything supported by the combination
        of canvas implementation and drawqueue implmentation.

        If target is not supported then an exception is thrown.
        '''
        output_func = self.output_closure(target, file_number)
        if immediate:
            self.drawqueue.append_immediate(output_func)
        else:
            self.drawqueue.append(output_func)

    def render(self, frame):
        '''
        Passes the drawqueue to the sink for rendering
        '''
        ### TODO - Threading this could be a place to spawn
        ### a thread
        self.sink.render(self.size_or_default(), frame, self.drawqueue)

    width = property(get_width)
    height = property(get_height)

