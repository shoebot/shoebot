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
'''Cairo implementation of draw queue'''

import cairo

from drawqueue import DrawQueue
from shoebot.util import RecordingSurface

class CairoDrawQueue(DrawQueue):
    '''
    Runs functions on a meta surface as the bot is running, instead of running
    them all at the end.

    TODO Threading:
    As functions are added to the queue, another thread takes them off the queue
    and draws them to the recording_surface

    Hacks:  1st command is currently special cased (it draws the background)
    '''
    def __init__(self, canvas_size):
        DrawQueue.__init__(self)
        self.recording_surface = RecordingSurface(*canvas_size)
        self.context = cairo.Context(self.recording_surface)
        self.count = 0
        self.initial_func = None

    def append_immediate(self, render_func):
        '''
        ## TODO - The queue will execute up until render_func
        ##        is executed before returning.
        This is how snapshots of surfaces get back to the bot

        Note - Once threading is enabled, calling append immediate
        Will probably severly affect performance
        '''
        raise NotImplementedError()

    def append(self, render_func):
        '''
        This needs to hand the function a queue so it
        can be executed by the rendering thread.
        '''
        ## super(DrawQueue, self).append(render_func)
        if self.count:
            render_func(self.context)
        else:
            self.initial_func = render_func
        self.count += 1

    def render(self, cairo_ctx):
        self.initial_func(cairo_ctx)
        cairo_ctx.set_source_surface(self.recording_surface)
        cairo_ctx.paint()
        self._post_render(cairo_ctx)
