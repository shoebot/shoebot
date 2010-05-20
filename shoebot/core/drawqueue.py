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

from collections import deque

class DrawQueue(object):
    '''
    A list of draw commands, stored as callables that, are
    passed a set of parameters to draw on from the canvas
    implementation.
    '''
    def __init__(self, render_funcs = None):
        self.render_funcs = render_funcs or deque()

    def append_immediate(self, render_func):
        '''
        In implementations of drawqueue that use buffering
        this will run the whole queue up to this point
        '''
        raise NotImplementedError('Not supported in DrawQueue')

    def append(self, render_func):
        '''
        Add a render function to the queue.
        '''
        self.render_funcs.append(render_func)

    def render(self, r_context):
        '''
        Call all the render functions with r_context

        r_context, is the render_context - Set of
        keyword args that should make sense to the
        canvas implementation
        '''
        for render_func in self.render_funcs:
            render_func(r_context)


class DrawQueueSink(object):
    '''
    DrawQueueSink, creates parameters for use by the draw queue.
    (the render_context).

    The render context is a set of platform sepecific
    parameters used by implementations of the drawqueue,
    canvas, and sink.
    '''
    def __init__(self, botcontext):
        self.botcontext = botcontext

    def render(self, size, frame, drawqueue):
        '''
        Accepts a drawqueue and
        '''
        r_context = self.create_rcontext(size, frame)
        drawqueue.render(r_context)
        self.rcontext_ready(size, frame, r_context)

    def create_rcontext(self, size, frame):
        '''
        Returns a cairo context for drawing this
        frame of the bot
        '''
        raise NotImplementedError('Child class should implement create_rcontext')
    
    def rcontext_ready(self, size, frame, r_context):
        '''
        Called when the bot has been rendered
        '''
        raise NotImplementedError('Child class should implement rcontext_ready')
