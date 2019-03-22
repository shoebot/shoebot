from __future__ import print_function

"""
Simple command shell

Launch shoebot with -l to activate it.

IDEs can launch shoebot with -wl and communicate via this shell
You can also try it as a user

sbot -wl ~/examples/animation/hypnoval.bot


For Livecoding IDEs can use the load_base64 command, simply pass
the updated python code as the first parameter.

If an editor wants to know the status of specific commands, set
cookie=unique_value as the last parameter of any command.

output will come back like this

%cookie> this is an intermediate line
%cookie>
%cookie: this is the last line, the client can dispose of the cookie

%cookie status>
%cookie:

%cookie status:

Other commands are available to control playback, try 'help' to
list them.
"""

import base64
import cmd
import shlex

from shoebot.core.events import QUIT_EVENT, SOURCE_CHANGED_EVENT, publish_event, SET_WINDOW_TITLE

PROMPT = ""
RESPONSE_PROMPT = ""
INTRO = RESPONSE_PROMPT + '"Shoebot Shell."'

RESPONSE_CODE_OK = "CODE_OK"
RESPONSE_REVERTED = "REVERTED"

trusted_cmds = set()


def trusted_cmd(f):
    """
    Trusted commands cannot be run remotely

    :param f:
    :return:
    """
    def run_cmd(self, line):
        if self.trusted:
            f(self, line)
        else:
            print("Sorry cannot do %s here." % f.__name__[3:])

    global trusted_cmds
    trusted_cmds.add(f.__name__)
    run_cmd.__doc__ = f.__doc__
    return run_cmd


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

    trusted_cmds = set()

    def __init__(self, bot, intro=None, trusted=False, **kwargs):
        """

        :param bot:
        :param intro:
        :param trusted: Only running from the commandline is trusted, not from sockets
                        untrusted can only change variables
        :param kwargs:
        :return:
        """
        cmd.Cmd.__init__(self, **kwargs)
        self.bot = bot
        self.pause_speed = None
        self.intro = intro or INTRO
        self.prompt = PROMPT
        self.response_prompt = ''
        self.use_rawinput = False
        self.cookie = None
        self.escape_nl = False
        self.live_prefix = ''
        self.trusted = trusted

    def print_response(self, input='', keep=False, *args, **kwargs):
        """
        print response, if cookie is set then print that each line
        :param args:
        :param keep: if True more output is to come
        :param cookie: set a custom cookie,
                       if set to 'None' then self.cookie will be used.
                       if set to 'False' disables cookie output entirely
        :return:
        """
        cookie = kwargs.get('cookie')
        if cookie is None:
            cookie = self.cookie or ''
        status = kwargs.get('status')
        lines = input.splitlines()
        if status and not lines:
            lines = ['']

        if cookie:
            output_template = '{cookie} {status}{cookie_char}{line}'
        else:
            output_template = '{line}'

        for i, line in enumerate(lines):
            if i != len(lines) - 1 or keep is True:
                cookie_char = '>'
            else:
                # last line
                cookie_char = ':'

            print(output_template.format(
                cookie_char=cookie_char,
                cookie=cookie,
                status=status or '',
                line=line.strip()), file=self.stdout)

    def emptyline(self):
        """
        Kill the default behaviour of repeating the last line.

        :return:
        """
        return ""

    def do_escape_nl(self, arg):
        """
        Escape newlines in any responses
        """
        if arg.lower() == 'off':
            self.escape_nl = False
        else:
            self.escape_nl = True

    def do_prompt(self, arg):
        """
        Enable or disable prompt
        :param arg: on|off
        :return:
        """
        if arg.lower() == 'off':
            self.response_prompt = ''
            self.prompt = ''
            return
        elif arg.lower() == 'on':
            self.prompt = PROMPT
            self.response_prompt = RESPONSE_PROMPT
        self.print_response('prompt: %s' % self.prompt, '\n', 'response: %s' % self.response_prompt)

    def do_title(self, title):
        """
        Change window title.
        """
        publish_event(SET_WINDOW_TITLE, data=title)

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
        """
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

    def do_vars(self, line):
        """
        List bot variables and values
        """
        if self.bot._vars:
            max_name_len = max([len(name) for name in self.bot._vars])
            for i, (name, v) in enumerate(self.bot._vars.items()):
                keep = i < len(self.bot._vars) - 1
                self.print_response("%s = %s" % (name.ljust(max_name_len), v.value), keep=keep)
        else:
            self.print_response("No vars")

    @trusted_cmd
    def do_load_base64(self, line):
        """
        load filename=(file)
        load base64=(base64 encoded)

        Send new code to shoebot.

        If it does not run successfully shoebot will attempt to role back.

        Editors can enable livecoding by sending new code as it is edited.
        """
        cookie = self.cookie
        executor = self.bot._executor

        def source_good():
            self.print_response(status=RESPONSE_CODE_OK, cookie=cookie)
            executor.clear_callbacks()

        def source_bad(tb):
            if called_good:
                # good and bad callbacks shouldn't both be called
                raise ValueError('Good AND Bad callbacks called !')
            self.print_response(status=RESPONSE_REVERTED, keep=True, cookie=cookie)
            self.print_response(tb.replace('\n', '\\n'), cookie=cookie)
            executor.clear_callbacks()

        called_good = False
        source = str(base64.b64decode(line))
        # Test compile
        publish_event(SOURCE_CHANGED_EVENT, data=source, extra_channels="shoebot.source")
        self.bot._executor.load_edited_source(source, good_cb=source_good, bad_cb=source_bad)

    def do_bye(self, line):
        """
        Exit shell and shoebot

        Alias for exit.
        """
        return self.do_exit(line)

    def do_exit(self, line):
        """
        Exit shell and shoebot
        """
        if self.trusted:
            publish_event(QUIT_EVENT)
        self.print_response('Bye.\n')
        return True

    def do_quit(self, line):
        """
        Exit shell and shoebot

        Alias for exit.
        """
        return self.do_exit(line)

    def do_fullscreen(self, line):
        """
        Make the current window fullscreen
        """
        self.bot.canvas.sink.trigger_fullscreen_action(True)
        print(self.response_prompt, file=self.stdout)

    def do_windowed(self, line):
        """
        Un-fullscreen the current window
        """
        self.bot.canvas.sink.trigger_fullscreen_action(False)
        print(self.response_prompt, file=self.stdout)

    def do_EOF(self, line):
        """
        Exit shell and shoebot

        Alias for exit.
        """
        print(self.response_prompt, file=self.stdout)
        return self.do_exit(line)

    def do_help(self, arg):
        """
        Show help on all commands.
        """
        print(self.response_prompt, file=self.stdout)
        return cmd.Cmd.do_help(self, arg)

    def do_set(self, line):
        """
        Set a variable.
        """
        try:
            name, value = [part.strip() for part in line.split('=')]
            if name not in self.bot._vars:
                self.print_response('No such variable %s enter vars to see available vars' % name)
                return
            variable = self.bot._vars[name]
            variable.value = variable.sanitize(value.strip(';'))

            success, msg = self.bot.canvas.sink.var_changed(name, variable.value)
            if success:
                print('{}={}'.format(name, variable.value), file=self.stdout)
            else:
                print('{}\n'.format(msg), file=self.stdout)
        except Exception as e:
            print('Invalid Syntax.', e)
            return

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
        if args and 'cookie=' in args[-1]:
            cookie_index = line.index('cookie=')
            cookie = line[cookie_index + 7:]
            line = line[:cookie_index].strip()
            self.cookie = cookie
        if line.startswith('#'):
            return ''
        elif '=' in line:
            # allow  somevar=somevalue

            # first check if we really mean a command
            cmdname = line.partition(" ")[0]
            if hasattr(self, "do_%s" % cmdname):
                return line

            if not line.startswith("set "):
                return "set " + line
            else:
                return line
        if len(args) and args[0] in self.shortcuts:
            return "%s %s" % (self.shortcuts[args[0]], " ".join(args[1:]))
        else:
            return line

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished."""
        self.cookie = None
        return stop

    def postloop(self):
        print('', file=self.stdout)
