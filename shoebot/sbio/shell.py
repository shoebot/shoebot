"""
Simple command shell

Launch shoebot with -l to activate it.

IDEs can launch shoebot with -l and communicate via this shell
You can also try it as a user:

$ sbot -l ~/examples/animation/hypnoval.bot


For live coding, IDEs can use the load_base64 command to load new
source:  The first parameter is the base64 encoded source code.

Cookie parameter:

If an editor wants to know the status of specific commands, set
cookie=unique_value as the last parameter of any command.

The cookie will be the first text on the line, followed by > or :

Examples:

%cookie> this is an intermediate line
%cookie>
%cookie: this is the last line, the client can dispose of the cookie

%cookie status>
%cookie:

%cookie status:

This makes it possible to filter responses from other info on stdout.


List available commands:

Type 'help' to list all the available commands.
"""

from __future__ import print_function
import base64
import cmd
import shlex

from shoebot.core.events import (
    QUIT_EVENT,
    SOURCE_CHANGED_EVENT,
    publish_event,
    SET_WINDOW_TITLE_EVENT,
)

PROMPT = ""
RESPONSE_PROMPT = ""
INTRO = RESPONSE_PROMPT + '"Shoebot Shell."'

RESPONSE_CODE_OK = "CODE_OK"
RESPONSE_REVERTED = "REVERTED"

trusted_cmds = set()


def trusted_cmd(f):
    """
    Decorator for methods that are trusted commands.

    If self.trusted is not set, then the command prints an error.

    :param f: do_XXX function to decorate.
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
        "rw": "rewind",
        "?": "help",
        "h": "help",
        "s": "speed",
        "g": "goto",
        "p": "pause",
        "q": "quit",
        "r": "restart",
    }

    # Trusted commands can only be run if trusted is set, e.g. when running from the commandline
    # not a socket.
    trusted_cmds = set()

    def __init__(self, bot, intro=None, trusted=False, **kwargs):
        """

        :param bot: bot instance
        :param intro: intro banner to display.
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
        self.response_prompt = ""
        self.use_rawinput = False
        self.cookie = None
        self.escape_nl = False
        self.live_prefix = ""
        self.trusted = trusted

    def print_response(self, input="", keep=False, *args, **kwargs):
        """
        print response, if cookie is set then print that each line
        :param args:
        :param keep: if True more output is to follow.
        :param cookie: set a custom cookie,
                       if set to 'None' then self.cookie will be used.
                       if set to 'False' disables cookie output entirely
        """
        status = kwargs.get("status")
        lines = input.splitlines()

        # Get cookie - unique string that can be provided by the sender to
        # filter replies to its requests that can arrive later.
        cookie = kwargs.get("cookie")
        if cookie is None:
            cookie = self.cookie or ""

        if status and not lines:
            # Nothing to output, just send a newline.
            print("", file=self.stdout)
            return

        if not cookie:
            # Standard output, lines arrive as they are.
            for line in lines:
                print(line, file=self.stdout)
            return

        # Prefix lines with unique str "cookie" and : or > on the last line.
        for i, line in enumerate(lines):
            if i != len(lines) - 1 or keep is True:
                cookie_char = ">"
            else:
                # last line
                cookie_char = ":"

            print(
                f"{cookie} {status or ''}{cookie_char}{line.strip()}",
                file=self.stdout,
            )

    def emptyline(self):
        """
        Override the default behaviour of repeating the last line.

        :return:
        """
        return ""

    def do_escape_nl(self, arg):
        """
        Toggle escaping newlines.
        """
        if arg.lower() == "off":
            self.escape_nl = False
        else:
            self.escape_nl = True

    def do_prompt(self, arg):
        """
        Enable or disable prompt
        :param arg: on|off
        :return:
        """
        if arg.lower() == "off":
            self.response_prompt = ""
            self.prompt = ""
            return
        elif arg.lower() == "on":
            self.prompt = PROMPT
            self.response_prompt = RESPONSE_PROMPT
        self.print_response(
            f"prompt: {self.prompt}\n" + f"response: {self.response_prompt}"
        )

    def do_title(self, title):
        """
        Change window title.
        """
        publish_event(SET_WINDOW_TITLE_EVENT, data=title)

    def do_speed(self, speed):
        """
        rewind
        """
        if speed:
            try:
                new_speed = float(speed)
            except ValueError as e:
                self.print_response(f"{speed} is not a valid framerate")
                return

            self.bot._speed = new_speed
        self.print_response(f"Speed: {self.bot._speed} FPS")

    def do_restart(self, line):
        """
        Attempt to restart bot by clearing its namespace and resetting FRAME to 0.
        """
        self.bot._frame = 0
        self.bot._namespace.clear()  # noqa
        self.bot._namespace.update(self.bot._initial_namespace)  # noqa

    def do_pause(self, line):
        """
        Toggle paused state.

        Stores the bots speed in pause_speed and temporarily sets the bot speed to 0.
        """
        if self.pause_speed is None:
            self.pause_speed = self.bot._speed
            self.bot._speed = 0
            self.print_response("Paused")
            return

        self.bot._speed = self.pause_speed
        self.pause_speed = None
        self.print_response("Playing")

    def do_play(self, line):
        """
        Resume playback if bot is paused
        """
        if self.pause_speed is not None:
            self.bot._speed = self.pause_speed
            self.pause_speed = None
        self.print_response("Play")

    def do_goto(self, line):
        """
        Go to specific frame
        """
        try:
            new_frame = int(line)
        except ValueError:
            self.print_response(f"{line} is not a valid framerate")
            return

        self.print_response(f"Go to frame {new_frame}")
        self.bot._frame = new_frame

    def do_rewind(self, line):
        """
        rewind
        """
        self.print_response(f"Rewinding from frame {self.bot._frame} to 0")
        self.bot._frame = 0

    def do_vars(self, line):
        """
        List bot variables and values.
        """
        if self.bot._vars:  # noqa
            max_name_len = max([len(name) for name in self.bot._vars])  # noqa
            for i, (name, v) in enumerate(self.bot._vars.items()):  # noqa
                keep = i < len(self.bot._vars) - 1  # noqa
                self.print_response(
                    f"{name.ljust(max_name_len)} = {v.value}", keep=keep
                )
        else:
            self.print_response("No vars")

    @trusted_cmd
    def do_load_base64(self, line):
        """
        load filename=(file)
        load base64=(base64 encoded)

        Send new code to shoebot.

        If it does not run successfully shoebot will attempt to role back.

        Editors can enable live-coding by sending new code as it is edited.
        """
        # TODO use publish_event to change source, and let the mainloop update the executor.
        cookie = self.cookie
        executor = self.bot._executor  # noqa

        def source_good():
            self.print_response(status=RESPONSE_CODE_OK, cookie=cookie)
            executor.clear_callbacks()

        def source_bad(tb):
            if called_good:
                # good and bad callbacks shouldn't both be called
                raise ValueError(
                    "Unexpected condition, Good and bad callbacks were called !"
                )

            self.print_response(status=RESPONSE_REVERTED, keep=True, cookie=cookie)
            self.print_response(tb.replace("\n", "\\n"), cookie=cookie)
            executor.clear_callbacks()

        called_good = False
        source = base64.b64decode(line).decode("utf-8")
        # Test compile
        publish_event(
            SOURCE_CHANGED_EVENT, data=source, extra_channels="shoebot.source"
        )
        self.bot._executor.load_edited_source(  # noqa
            source, good_cb=source_good, bad_cb=source_bad
        )

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
        self.print_response("Bye.\n")
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
        # TODO: use publish_event to set toggle fullscreen instead of calling trigger_fullscreen_action directly.
        self.bot.canvas.sink.trigger_fullscreen_action(True)
        print(self.response_prompt, file=self.stdout)

    def do_window(self, line):
        """
        Un-fullscreen and
        """
        # TODO: use publish_event to set toggle fullscreen instead of calling trigger_fullscreen_action directly.
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
        # TODO: use publish_event to set Variable instead of directly changing it.
        try:
            name, value = [part.strip() for part in line.split("=")]
            if name not in self.bot._vars:  # noqa
                self.print_response(
                    "No such variable %s enter vars to see available vars" % name
                )
                return
            variable = self.bot._vars[name]
            variable.value = variable.sanitize(value.strip(";"))

            success, msg = self.bot.canvas.sink.var_changed(name, variable.value)
            if success:
                print(f"{name}={variable.value}", file=self.stdout)
            else:
                print(f"{msg}\n", file=self.stdout)
        except Exception:
            print("Invalid Syntax for set command")

    def precmd(self, line):
        """
        Preprocess the commandline.

        Cookies:
            Allow commands to have a last parameter of 'cookie=arbitrary_string'

            Editors can send a "cookie" value - an arbitrary string, usually
            a uuid, for commands that have responses, this will be prepended
            to the response, along with : if there is more data to follow
            or > on the last line.

        :param line:  input command line.
        :return:  processed command line.
        """
        args = shlex.split(line or "")
        if not args or args[0].startswith("#"):
            # Ignore empty lines and comments.
            return ""

        if "cookie=" in args[-1]:
            # Get the cookie value.
            line, self.cookie = line.rsplit("cookie=")
            line = line.strip()
            del args[-1]
            if not args:
                return ""

        if hasattr(self, f"do_{args[0]}"):
            # This stops var=value parsing trying to handle load_base64 which
            # may contain = signs.
            return line

        # Further parsing
        if "=" in line:
            # Variable Assignment: somevar=value
            #
            # Convert var=value into set var=value
            #
            if "set" not in args[0]:
                return f"set {line}"
            return line
        elif args[0] in self.shortcuts:
            # Shortcuts
            #
            # If the first item on the commandline is a shortcut, the substitute it for
            # the full command.
            return self.shortcuts[args[0]] + " ".join(args[1:])

        return line

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished."""
        self.cookie = None
        return stop

    def postloop(self):
        print("", file=self.stdout)
