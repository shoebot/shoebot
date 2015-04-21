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

import os
import signal
import sys
import threading

# TODO - Check if this needs importing here:
#from shoebot.data import MOVETO, RMOVETO, LINETO, RLINETO, CURVETO, RCURVETO, ARC, ELLIPSE, CLOSE, LEFT, RIGHT, ShoebotError, ShoebotScriptError


RGB = "rgb"
HSB = "hsb"
CMYK = 'cmyk'

CENTER = "center"
CORNER = "corner"
CORNERS = "corners"

NODEBOX = 'nodebox'
DRAWBOT = 'drawbot'


def _save():
    # Dummy function used by color lib; TODO investigate if this can be implemented
    pass


def _restore():
    # Dummy function used by color lib; TODO investigate if this can be implemented
    pass


## Convenience functions to create create a bot, it's canvas and 'sink'

def create_canvas(src, format=None, outputfile=None, multifile=False, buff=None, window=False, title=None, fullscreen=None, server=False, port=7777, show_vars=False):
    """
    Create canvas and sink for attachment to a bot

    canvas is what draws images, 'sink' is the final consumer of the images
    """
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
        sink = CairoImageSink(outputfile, format, multifile, buff)
    canvas = CairoCanvas(sink)

    return canvas


def create_bot(src=None, grammar=NODEBOX, format=None, outputfile=None, iterations=1, buff=None, window=False, title=None, fullscreen=None, server=False, port=7777, show_vars=False, vars=None):
    """
    Create a canvas and a bot with the same canvas attached to it

    bot parameters
    :param grammar: DRAWBOT or NODEBOX - decides what kind of bot is created
    :param vars: preset dictionary of vars from the called

    canvas parameters:
    ... everything else ...
    """
    canvas = create_canvas(src, format, outputfile, iterations > 1, buff, window, title, fullscreen=fullscreen, server=server, port=port, show_vars=show_vars)

    if grammar == DRAWBOT:
        from shoebot.grammar import DrawBot
        bot = DrawBot(canvas, vars=vars)
    else:
        from shoebot.grammar import NodeBot
        bot = NodeBot(canvas, vars=vars)
    return bot


class ShoebotThread(threading.Thread):
    """
    Run shoebot in an alternate thread.

    This way the commandline shell can run on the main thread
    and the GUI in a seperate thread
    """
    def __init__(self,
            create_args, create_kwargs,
            run_args, run_kwargs,
            send_sigint=False):
        """
        :param create_args: passed to create_bot
        :param create_kwargs: passed to create_bot
        :param run_args: passed to bot.run
        :param run_kwargs: passed to bot.run
        :param send_sigint: if True then SIGINT will be sent on bot completion
                            so the main thread can terminate
        """
        super(ShoebotThread, self).__init__()
        # isSet() will return True once the bot has been created
        self.bot_ready = threading.Event()

        self.create_args = create_args
        self.create_kwargs = create_kwargs

        self.run_args = run_args
        self.run_kwargs = run_kwargs

        self.send_sigint = send_sigint
        self._sbot = None

    def run(self):
        try:
            sbot = create_bot(*self.create_args, **self.create_kwargs)

            self._sbot = sbot
            self.bot_ready.set()
            sbot.run(*self.run_args, **self.run_kwargs)
        except Exception:
            print('DOH')
            raise
        finally:
            if self.send_sigint:
                os.kill(os.getpid(), signal.SIGINT)

    @property
    def sbot(self):
        """
        :return: bot instance for communication
        """
        self.bot_ready.wait()
        return self._sbot


def run(src,
        grammar=NODEBOX,
        format=None,
        outputfile=None,
        iterations=1,
        buff=None,
        window=False,
        title=None,
        fullscreen=None,
        close_window=False,
        server=False,
        port=7777,
        show_vars=False,
        vars=None,
        run_shell=False,
        args=[],
        verbose=False,
        background_thread=True):
    """
    Create and run a bot, the arguments all correspond to sanitized
    commandline options.
    """
    # Munge shoebogt sys.argv
    sys.argv = [sys.argv[0]] + args  # Remove shoebot parameters so sbot can be used in place of the python interpreter (e.g. for sphinx).

    # arguments for create_bot
    create_args = [src,
        grammar,
        format,
        outputfile,
        iterations,
        buff,
        window,
        title,
        fullscreen,
        server,
        port,
        show_vars]
    create_kwargs = dict(vars=vars)
    run_args = [src]
    run_kwargs = dict(
        run_forever=window if close_window is False else False,
        frame_limiter=window,
        verbose=verbose
    )

    # Run shoebot in a background thread so we can run a cmdline shell in the current thread
    if background_thread:
        sbot_thread = ShoebotThread(
            create_args=create_args,
            create_kwargs=create_kwargs,
            run_args=run_args,
            run_kwargs=run_kwargs,
            send_sigint=run_shell
        )
        sbot_thread.start()
        sbot = sbot_thread.sbot
    else:
        print('background thread disabled')
        # This is a debug option, things should always work using the
        # background thread (crosses fingers)
        if run_shell:
            # python readline is blocking, so ui must run in a seperate
            # thread
            raise ValueError('UI Must run in a seperate thread to shell and shell needs main thread')

        sbot_thread = None
        sbot = create_bot(*create_args, **create_kwargs)
        sbot.run(*run_args, **run_kwargs)

    if run_shell:
        import shoebot.io.shell
        shell = shoebot.io.shell.ShoebotCmd(sbot)
        try:
            shell.cmdloop()
        except KeyboardInterrupt:
            if not sbot._quit:
                # TODO - must be
                raise

    if sbot_thread is not None:
        sbot_thread.join()

    return sbot
