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
'''Convenience function to run a bot'''

import os
import signal
import sys
#import thread
import threading

NODEBOX = 'nodebox'
DRAWBOT = 'drawbot'

def create_canvas(src, format=None, outputfile=None, multifile=False, buff=None, window=False, title=None, fullscreen=None, server=False, port=7777, show_vars=False):
    '''
    Convience file to create canvas and output sink for a shoebot bot

    Creates a CairoCanvas on a ShoebotWindow or attached to a CairoImageSink
    '''
    from core import CairoCanvas, CairoImageSink

    if window or show_vars:
        from gui import ShoebotWindow

        if not title:
            if src and os.path.isfile(src):
                title = os.path.splitext(os.path.basename(src))[0] + ' - Shoebot'
            else:
                title = 'Untitled - Shoebot'
        sink = ShoebotWindow(title, show_vars, server=server, port=port, fullscreen=fullscreen)
    else:
        if outputfile is None:
            if src and os.path.isfile(src):
                outputfile = os.path.splitext(os.path.basename(src))[0] + '.' + (format or 'svg')
            else:
                outputfile = 'output.svg'
        sink = CairoImageSink(outputfile, format, multifile)
    canvas = CairoCanvas(sink)

    return canvas


def bot(src = None, grammar=NODEBOX, format=None, outputfile=None, iterations=1, buff=None, window=False, title=None, fullscreen=None, server=False, port=7777, show_vars=False, vars=None):
    '''
    Convienience function to create a bot
    '''
    canvas = create_canvas(src, format, outputfile, iterations > 1, buff, window, title, fullscreen=fullscreen, server=server, port=port, show_vars = show_vars)

    from shoebot.grammar import DrawBot, NodeBot
    if grammar == DRAWBOT:
        bot = DrawBot(canvas, vars = vars)
    else:
        bot = NodeBot(canvas, vars = vars)

    return bot


class ShoebotThread(threading.Thread):
    def __init__(self, sbot, *args, **kwargs):
        threading.Thread.__init__(self)
        self.sbot = sbot
        self.args = args
        self.setDaemon(True)
        if 'shell' in kwargs:
            self.shell = kwargs['shell']
            del kwargs['shell']

        self.kwargs = kwargs

    def run(self):
        #self.sbot.run(src, iterations, run_forever=window if close_window == False else False, frame_limiter = window)
        self.sbot.run(*self.args, **self.kwargs)
        if self.shell is not None:
            # Send the kill
            os.kill(os.getpid(), signal.SIGINT)


def run(src, grammar = NODEBOX, format = None, outputfile = None, iterations = 1, buff=None, window = False, title = None, fullscreen = None, close_window = False, server=False, port=7777, show_vars = False, vars = None, run_shell=False, args = []):
    # Munge shoebot sys.argv
    sys.argv = [sys.argv[0]] + args  # Remove shoebot parameters so sbot can be used in place of the python interpreter (e.g. for sphinx).
    sbot = bot(src, grammar, format, outputfile, iterations, window, title, fullscreen, server, port, show_vars, vars = vars)

    if run_shell:
        import shoebot.gui.shell
        shell = shoebot.gui.shell.ShoebotCmd(sbot)
    else:
        shell = None

    # Run shoebot in a background thread so we can run a cmdline shell in the current thread
    sbot_thread = ShoebotThread(sbot, src, iterations, run_forever=window if close_window == False else False, frame_limiter = window, shell=shell)
    sbot_thread.start()
    if shell is not None:
        try:
            shell.cmdloop()
        except KeyboardInterrupt:
            if not sbot._quit:
                raise
            else:
                print '\nBye.'
    else:
        sbot_thread.join()

    return bot
