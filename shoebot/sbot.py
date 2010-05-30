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
'''Convenience function to run a bot'''

import os.path

NODEBOX = 'nodebox'
DRAWBOT = 'drawbot'
SHOEBOT = 'shoebot'

def run(src, grammar = NODEBOX, format = None, outputfile = 'output.svg', iterations = None, window = False, show_vars = False):
    '''
    Convenience function to make it easy to start bots from external programs
    '''
    from core import CairoCanvas, CairoImageSink
    from gui import ShoebotWidget, ShoebotWindow

    from core import NodeBot
    from core import DrawBot

    if window or show_vars:
        if os.path.isfile(src):
            title = os.path.splitext(os.path.basename(src))[0] + ' - Shoebot'
        else:
            title = 'Untitled - Shoebot'
        sink = ShoebotWindow(title, show_vars)
    else:
        if iterations is None:
            iterations = 1
        sink = CairoImageSink(filename = outputfile, format = format, multifile = iterations > 1)

    canvas = CairoCanvas(sink = sink, enable_cairo_queue=True)
    BOT_CLASSES = {
        DRAWBOT : DrawBot,
        NODEBOX : NodeBot,
        #SHOEBOT : Shoebot,
    }
    bot = BOT_CLASSES[grammar](canvas)
    canvas.set_bot(bot)
    bot.sb_run(src, iterations, run_forever = window, frame_limiter = window)

