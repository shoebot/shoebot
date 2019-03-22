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

from shoebot.core.backend import cairo


class ShoebotInstallError(Exception):
    pass


# TODO - Check if this needs importing here:
# from shoebot.data import MOVETO, RMOVETO, LINETO, RLINETO, CURVETO, RCURVETO, ARC, ELLIPSE, CLOSE, LEFT, RIGHT, ShoebotError, ShoebotScriptError
from time import sleep

from shoebot.core.events import publish_event, QUIT_EVENT

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


# Convenience functions to create a bot, its canvas and sink

def create_canvas(src, format=None, outputfile=None, multifile=False, buff=None, window=False, title=None,
                  fullscreen=None, show_vars=False):
    """
    Create canvas and sink for attachment to a bot

    canvas is what draws images, 'sink' is the final consumer of the images

    :param src: Defaults for title or outputfile if not specified.

    :param format: CairoImageSink image format, if using buff instead of outputfile
    :param buff: CairoImageSink buffer object to send output to

    :param outputfile: CairoImageSink output filename e.g. "hello.svg"
    :param multifile: CairoImageSink if True,

    :param title: ShoebotWindow - set window title
    :param fullscreen: ShoebotWindow - set window title
    :param show_vars: ShoebotWindow - display variable window

    Two kinds of sink are provided: CairoImageSink and ShoebotWindow

    ShoebotWindow

    Displays a window to draw shoebot inside.


    CairoImageSink

    Output to a filename (or files if multifile is set), or a buffer object.
    """
    from core import CairoCanvas, CairoImageSink # https://github.com/shoebot/shoebot/issues/206

    if outputfile:
        sink = CairoImageSink(outputfile, format, multifile, buff)
    elif window or show_vars:
        from gui import ShoebotWindow
        if not title:
            if src and os.path.isfile(src):
                title = os.path.splitext(os.path.basename(src))[0] + ' - Shoebot'
            else:
                title = 'Untitled - Shoebot'
        sink = ShoebotWindow(title, show_vars, fullscreen=fullscreen)
    else:
        if src and isinstance(src, cairo.Surface):
            outputfile = src
            format = 'surface'
        elif src and os.path.isfile(src):
            outputfile = os.path.splitext(os.path.basename(src))[0] + '.' + (format or 'svg')
        else:
            outputfile = 'output.svg'
        sink = CairoImageSink(outputfile, format, multifile, buff)
    canvas = CairoCanvas(sink)

    return canvas


def create_bot(src=None, grammar=NODEBOX, format=None, outputfile=None, iterations=1, buff=None, window=False,
               title=None, fullscreen=None, server=False, port=7777, show_vars=False, vars=None, namespace=None):
    """
    Create a canvas and a bot with the same canvas attached to it

    bot parameters
    :param grammar: DRAWBOT or NODEBOX - decides what kind of bot is created
    :param vars: preset dictionary of vars from the called

    canvas parameters:
    ... everything else ...

    See create_canvas for details on those parameters.

    """
    canvas = create_canvas(src, format, outputfile, iterations > 1, buff, window, title, fullscreen=fullscreen,
                           show_vars=show_vars)

    if grammar == DRAWBOT:
        from shoebot.grammar import DrawBot
        bot = DrawBot(canvas, namespace=namespace, vars=vars)
    else:
        from shoebot.grammar import NodeBot
        bot = NodeBot(canvas, namespace=namespace, vars=vars)

    if server:
        from shoebot.sbio import SocketServer
        socket_server = SocketServer(bot, "", port=port)
    return bot


class ShoebotThread(threading.Thread):
    """
    Run shoebot in an alternate thread.

    This way the commandline shell can run on the main thread
    and the GUI in a seperate thread without readline
    blocking it.
    """

    def __init__(self, create_args, create_kwargs,
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
            print('Exception in shoebot code')
            self.bot_ready.set()  # need to stop waiting
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
        window=True,
        title=None,
        fullscreen=None,
        close_window=False,
        server=False,
        port=7777,
        show_vars=False,
        vars=None,
        namespace=None,
        run_shell=False,
        args=[],
        verbose=False,
        background_thread=True):
    """
    Create and run a bot, the arguments all correspond to sanitized
    commandline options.

    :param background_thread: If True then use a background thread.


    Other args are split into create_args and run_args

    See create_bot for details on create_args

    run_args are passed to bot.run - see Nodebot.run or Drawbot.run



    Background thread:

    readline in python is blocking, running the app in a background
    thread opens up the main thread for IO on stdin/stdout, which
    can be used for communication with shoebot when livecoding is
    enabled.

    See shoebot.io for implementation of the shell, and the gedit
    plugin for an example of using livecoding.
    """
    # Munge shoebogt sys.argv
    sys.argv = [sys.argv[
                    0]] + args  # Remove shoebot parameters so sbot can be used in place of the python interpreter (e.g. for sphinx).

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
    create_kwargs = dict(vars=vars, namespace=namespace)
    run_args = [src]
    run_kwargs = dict(
        iterations=iterations,
        frame_limiter=window,
        verbose=verbose,
        # run forever except 1. windowed mode is off 2. if --close-window was specified and
        # 3. if an output file was indicated
        run_forever=window and not (close_window or bool(outputfile)),
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
            raise ValueError('UI Must run in a separate thread to shell and shell needs main thread')

        sbot_thread = None
        sbot = create_bot(*create_args, **create_kwargs)
        sbot.run(*run_args, **run_kwargs)

    if run_shell:
        import shoebot.sbio.shell
        shell = shoebot.sbio.shell.ShoebotCmd(sbot, trusted=True)
        try:
            shell.cmdloop()
        except KeyboardInterrupt as e:
            publish_event(QUIT_EVENT)  # Handle Ctrl-C
            # KeyboardInterrupt is generated by os.kill from the other thread
            if verbose:
                raise
            else:
                return
    elif background_thread:
        try:
            while sbot_thread.is_alive():
                sleep(1)
        except KeyboardInterrupt:
            publish_event(QUIT_EVENT)

    if all((background_thread, sbot_thread)):
        sbot_thread.join()

    return sbot
