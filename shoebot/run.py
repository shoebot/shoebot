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
""" Shoebot console runner """

import argparse
import gettext
import locale
import shlex
import sys

DEFAULT_SERVERPORT = 7777

OUTPUT_EXTENSIONS = ('.png', '.svg', '.ps', '.pdf')
APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext

NODEBOX = 'nodebox'
DRAWBOT = 'drawbot'


def json_arg(s):
    try:
        import json
        d = json.loads(s)
        return d
    except Exception as e:
        error(_('Error parsing JSON, remember single quotes OUTSIDE, double QUOTES inside.'))
        raise e


def error(message):
    '''Prints an error message, the help message and quits'''
    global parser
    print (_("Error: ") + message)
    print ()
    parser.print_help()
    sys.exit()


def warn(message):
    '''Print a warning message'''
    print (_("Warning: ") + message)


def main():
    global parser

    # use ArgumentParser to interpret commandline options
    parser = argparse.ArgumentParser(_("usage: sbot [options] inputfile.bot [args]"))
    parser.add_argument("script", help="Shoebot / Nodebox script to run (filename or code)", nargs='?')

    group = parser.add_argument_group('Input / Output')
    # IO - Output to file
    group.add_argument("-o",
                       "--outputfile",
                       dest="outputfile",
                       help=_("run script and output to image file (accepts .png .svg .pdf and .ps extensions)"),
                       metavar="FILE")

    # Shoebot IO - Sockets
    group.add_argument("-s",
                       "--socketserver",
                       action="store_true",
                       dest="socketserver",
                       default=False,
                       help=_("run a socket server for external control (will run the script in windowed mode)"))
    group.add_argument("-p",
                       "--serverport",
                       type=int,
                       dest="serverport",
                       default=DEFAULT_SERVERPORT,
                       help=_("set socketserver port to listen for connections (default is 7777)"))

    # IO - Variables
    group.add_argument("-v",
                       "--vars",
                       dest="vars",
                       default=False,
                       help=_("Initial variables, in JSON (Note: Single quotes OUTSIDE, double INSIDE) --vars='{\"variable1\": 1}'"),
                       )
    # IO - Namespace
    group.add_argument("-ns",
                    "--namespace",
                    dest="namespace",
                    default=None,
                    help=_("Initial namespace, in JSON (Note: Single quotes OUTSIDE, double INSIDE) --namespace='{\"variable1\": 1}'"),
                    )
    # IO - IDE integration Shell
    group.add_argument("-l",
                    "--l",
                    dest="shell",
                    action="store_true",
                    default=False,
                    help=_("Simple shell - for IDE interaction"),
                    )

    # IO - Passing args to the bot
    group.add_argument("-a",
                    "--args",
                    dest="script_args",
                    help=_("Pass to the bot"),
                    )
    group.add_argument('script_args', nargs='?')

    group = parser.add_argument_group('Bot Lifecycle')
    # Bot Lifecycle
    group.add_argument("-r",
                       "--repeat",
                       type=int,
                       dest="repeat",
                       default=False,
                       help=_("set number of iteration, multiple images will be produced"))
    group.add_argument("-g",
                    "--grammar",
                    dest="grammar",
                    default=NODEBOX,
                    help=_("Select the bot grammar 'nodebox' (default) or 'drawbot' languages"),
                    )

    group = parser.add_argument_group('Window Management')
    group.add_argument("-w",
                       "--window",
                       action="store_true",
                       dest="window",
                       default=True,
                       help=_("run script in a GTK window")
                       )
    group.add_argument("-f",
                       "--fullscreen",
                       action="store_true",
                       dest="fullscreen",
                       default=False,
                       help=_("run in fullscreen mode")
                       )
    group.add_argument("-t",
                       "--title",
                       action="store",
                       dest="title",
                       default=None,
                       help=_("Set window title")
                       )
    group.add_argument("-c",
                       "--close",
                       action="store_true",
                       dest="close",
                       default=False,
                       help=_("Close window after running bot (use with -r for benchmarking)"),
                       )
    group.add_argument("-dv",
                       "--disable-vars",
                       action="store_true",
                       dest="disable_vars",
                       default=False,
                       help=_("disable the variables pane when in windowed mode."))

    group = parser.add_argument_group('Debugging / Dev flags')
    group.add_argument("-dn",
                       "--diagnose",
                       action="store_true",
                       default=False,
                       help=_("Output information for debugging installation / graphics issues."))
    group.add_argument("-dt",
                       "--disable-background-thread",
                       action="store_true",
                       dest="disable_background_thread",
                       default=sys.platform=='darwin',
                       help=_("disable running bot code in background thread (default on OSX)."))
    group.add_argument("-V",
                       "--verbose",
                       action="store_true",
                       dest="verbose",
                       default=False,
                       help=_("Show internal shoebot error information in traceback"),
                       )

    # get argparse arguments and check for sanity
    args, extra = parser.parse_known_args()

    if args.diagnose:
        from diagnose import diagnose
        diagnose()
        sys.exit()

    if not args.script:
        error(_('Please specify an input script!\n (check /usr/share/shoebot/examples/ for example scripts)'))

    if args.vars:
        vars = json_arg(args.vars)
    else:
        vars = None

    if args.namespace:
        namespace = json_arg(args.namespace)
    else:
        namespace = None

    from __init__ import run  # https://github.com/shoebot/shoebot/issues/206
    run(src=args.script,
        grammar=args.grammar,
        outputfile=args.outputfile,
        iterations=args.repeat or None,
        window=args.window or args.socketserver,
        fullscreen=args.fullscreen,
        title=args.title,
        close_window=args.close,
        server=args.socketserver,
        port=args.serverport,
        show_vars=args.window and args.disable_vars is False,
        vars=vars or None,
        namespace=namespace,
        run_shell=args.shell,
        args=shlex.split(args.script_args or ""),
        verbose=args.verbose,
        background_thread=not args.disable_background_thread,
        )


if __name__ == '__main__':
    main()
