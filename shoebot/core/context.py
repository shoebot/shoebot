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
'''Machinery to run a bot'''

import os
import traceback

class Context(object):
    """
    Context that Bot is executed within.

    Contains the machinery to actually run the bot

    To avoid confusion with cairo Contexts, cairo contexts
    will always use ctx in the name, and bot contexts
    context.
    """
    def __init__(self, bot_class, canvas, namespace = None):
        self.canvas = canvas
        self.set_defaults()
        self.dynamic = True
        self.speed = None
        self.quit = False
        self.iteration = 0

        self.namespace = namespace or {}
        self.bot = bot_class(self, canvas, self.namespace)
        canvas.sink.set_botcontext(self)

    def set_defaults(self):
        '''
        Set defaults before rendering
        '''
        self.canvas.size = None
        self.frame = 0

    def _load_namespace(self, filename = None):
        namespace = self.namespace

        for name in dir(self.bot):
            if name[0] != '_':
                namespace[name] = getattr(self.bot, name)

        from shoebot import data
        for name in dir(data):
            namespace[name] = getattr(data, name)

        if filename:
            namespace['__file__'] = filename
        self.namespace = namespace

    def _set_dynamic_vars(self):
        self.namespace['FRAME'] = self.frame

    def _exec_frame(self, source_or_code):
        '''
        Run single frame of the bot
        '''
        namespace = self.namespace
        self.canvas.reset_canvas()
        self._set_dynamic_vars()
        if self.iteration == 0:
            # First frame
            exec source_or_code in namespace
            namespace['setup']()
            namespace['draw']()
        else:
            # Subsequent frames
            if self.dynamic:
                namespace['draw']()
            else:
                exec source_or_code in namespace
        
        self.frame += 1
        self.iteration += 1

    def should_run(self, iterations):
        '''
        Return False if bot should quit
        '''
        if self.iteration == 0:
            # First frame always runs
            return True
        if self.quit:
            return False
        if iterations:
            if self.iteration < iterations:
                return True
        elif iterations is None:
            return True
        if not self.dynamic:
            ### TODO... gtk window needs to run in another thread, that will keep
            ### going until explicitly closed
            print '###TODO'
            return False
        return False

    def run(self, inputcode, iterations = None, run_forever = False):
        '''
        Executes the contents of a Nodebox/Shoebot script
        in current surface's context.

        ctx_create_func, is a function called, every time
        a Cairo Context is needed, the bot context is passed in.
        '''
        source_or_code = ""

        # is it a proper filename?
        if os.path.isfile(inputcode):
            with open(inputcode, 'rU') as file:
                source_or_code = file.read()
            self._load_namespace(inputcode)
        else:
            # if not, try parsing it as a code string
            source_or_code = inputcode
            self._load_namespace()

        try:
            # if it's a string, it needs compiling first; if it's a file, no action needed
            if isinstance(source_or_code, basestring):
                source_or_code = compile(source_or_code + "\n\n", "shoebot_code", "exec")
            # do the magic            
            canvas = self.canvas
            if not iterations:
                if run_forever:
                    iterations = None
                else:
                    iterations = 1
            while self.should_run(iterations):
                frame = self.frame
                self._exec_frame(source_or_code)
                canvas.render(frame)

        except NameError:
            # if something goes wrong, print verbose system output
            # maybe this is too verbose, but okay for now
            errmsg = traceback.format_exc()
            print errmsg
