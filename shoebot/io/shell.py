from __future__ import print_function

import re

"""
Simple command shell

Launch shoebot with -l to activate it.

IDEs can launch shoebot with -wl and communicate via this shell
You can also try it as a user

sbot -wl ~/examples/animation/hypnoval.bot


For Livecoding IDEs can use the load_base64 command, simply pass
the updated python code as the first parameter.

Other commands are available to control playback, try 'help' to
list them.
"""

import base64
import cmd
import shlex

PROMPT = "[^_^] "
RESPONSE_PROMPT = "[o_o] "
INTRO = RESPONSE_PROMPT + '"Shoebot Shell."'


class ShoebotCmd(cmd.Cmd):
    """Simple command processor example."""

    shortcuts = {
        'rw': 'rewind',
        '?': 'help',
        'h': 'help',
        's': 'speed',
        'g': 'goto',
        'p': 'pause',
        'q': 'quit',
        'r': 'restart'
    }

    def __init__(self, bot, **kwargs):
        self.bot =\
            bot
        self.pause_speed = None
        cmd.Cmd.__init__(self, **kwargs)
        self.intro = INTRO
        self.prompt = PROMPT
        self.use_rawinput = False
        self.cookie = None

    def print_response(self, *args):
        """
        print response, if cookie is set then print that each line
        :param args:
        :return:
        """
        lines = str(" ".join(args)).splitlines()
        if self.cookie:
            for line in str("".join(args)).splitlines():
                print("%s %s" % (self.cookie, line))
        else:
            print(RESPONSE_PROMPT)
            if len(lines):
                print("\n")
            print(str("".join(args)))

    def handler(signum, frame):
        self.print_response('Caught CTRL-C, press enter to continue')

    def emptyline(self):
        """
        Kill the default behaviour of repeating the last line.

        :return:
        """
        print(RESPONSE_PROMPT)
        return ""

    def do_prompt(self, arg):
        self.print_response('prompt: %s' % PROMPT, '\n', 'response: %s' % RESPONSE_PROMPT)

    def do_title(self, title):
        """
        Change window title.
        """
        pass

    def do_speed(self, speed):
        """
        rewind
        """
        if speed:
            try:
                self.bot._speed = float(speed)
            except Exception as e:
                self.print_response('%s is not a valid framerate' % speed)
                return
        self.print_response('Speed: %s FPS' % self.bot._speed)

    def do_restart(self, line):
        """
        Attempt to restart the bot.
        """
        self.bot._frame = 0
        self.bot._namespace.clear()
        self.bot._namespace.update(self.bot._initial_namespace)

    def do_pause(self, line):
        """
        Toggle pause
        :param line:
        :return:
        """
        # TODO - move this into bot controller
        # along with stuff in socketserver and shell
        if self.pause_speed is None:
            self.pause_speed = self.bot._speed
            self.bot._speed = 0
            self.print_response('Paused')
        else:
            self.bot._speed = self.pause_speed
            self.pause_speed = None
            self.print_response('Playing')

    def do_play(self, line):
        """
        Resume playback if bot is paused

        :param line:
        :return:
        """
        if self.pause_speed is None:
            self.bot._speed = self.pause_speed
            self.pause_speed = None
        self.print_response("Play")

    def do_goto(self, line):
        """
        Go to specific frame
        :param line:
        :return:
        """
        self.print_response("Go to frame %s" % line)
        self.bot._frame = int(line)

    def do_rewind(self, line):
        """
        rewind
        """
        self.print_response("Rewinding from frame %s to 0" % self.bot._frame)
        self.bot._frame = 0

    def do_load_base64(self, line):
        """
        load filename=(file)
        load base64=(base64 encoded)
        """
        try:
            source = str(base64.b64decode(line))
            # Test compile
            compile(source + '\n\n', "shoebot_code", "exec")
            self.bot._executor.load_edited_source(source)
        except Exception as e:
            # TODO Use simple traceback here
            self.print_response("Error Compiling")
            self.print_response(e)

    def do_bye(self, line):
        return self.do_exit(line)

    def do_exit(self, line):
        self.print_response('Bye.\n')
        self.bot._quit = True
        return True

    def do_quit(self, line):
        return self.do_exit(line)

    def do_fullscreen(self, line):
        self.print_response('TODO - toggle fullscreen')

    def do_windowed(self, line):
        self.print_response('TODO - set windowed mode')

    def do_EOF(self, line):
        return self.do_exit(line)

    def do_help(self, arg):
        print(RESPONSE_PROMPT)
        return cmd.Cmd.do_help(self, arg)

    def precmd(self, line):
        """
        Allow commands to have a last parameter of 'cookie=somevalue'

        TODO somevalue will be prepended onto any output lines so
        that editors can distinguish output from certain kinds
        of events they have sent.

        :param line:
        :return:
        """
        args = shlex.split(line or "")
        last_arg = args[-1]
        if 'cookie=' in last_arg:
            cookie_index = line.index('cookie=')
            cookie = line[cookie_index+7:]
            line = line[:cookie_index].strip()
            self.cookie=cookie
        if len(args) and args[0] in self.shortcuts:
            return "%s %s" % (self.shortcuts[args[0]], " ".join(args[1:]))
        else:
            return line

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished."""
        self.cookie = None
        return stop

    def postloop(self):
        print('')

