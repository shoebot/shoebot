from __future__ import print_function

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
        self.intro = 'Experimental Feature - for ide integration.'
        self.prompt = '(bot) '
        self.use_rawinput = False

    def handler(signum, frame):
        print('Caught CTRL-C, press enter to continue')

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
                print('%s is not a valid framerate' % speed)
                return
        print('Speed: %s FPS' % self.bot._speed)

    def do_restart(self, line):
        """
        Attempt to restart the bot.
        """
        self.bot._frame = 0
        self.bot._namespace.clear()
        self.bot._namespace.update(self.bot._initial_namespace)

    def do_pause(self, line):
        if self.pause_speed is None:
            self.pause_speed = self.bot._speed
            self.bot._speed = None
            print("Paused - \"play\" to resume")

    def do_play(self, line):
        """
        Resume playback if bot is paused

        :param line:
        :return:
        """
        if self.pause_speed is None:
            self.bot._speed = self.pause_speed
            self.pause_speed = None
        print("Play")

    def do_goto(self, line):
        """
        Go to specific frame
        :param line:
        :return:
        """
        print("Go to frame %s" % line)
        self.bot._frame = int(line)

    def do_rewind(self, line):
        """
        rewind
        """
        print("Rewinding from frame %s to 0" % self.bot._frame)
        self.bot._frame = 0

    def do_load_base64(self, line):
        """
        load filename=(file)
        load base64=(base64 encoded)
        """
        print("shoebot: load_base64 ")
        try:
            source = str(base64.b64decode(line))
            # Test compile
            code = compile(source + '\n\n', "shoebot_code", "exec")
            self.bot._executor.load_edited_source(source)
        except Exception as e:
            # TODO Use simple traceback here
            print ("Error Compiling")
            print (e)

    def do_bye(self, line):
        return self.do_exit(line)

    def do_exit(self, line):
        print('Bye.')
        self.bot._quit = True
        return True

    def do_quit(self, line):
        return self.do_exit(line)

    def do_fullscreen(self, line):
        print('TODO - toggle fullscreen')

    def do_windowed(self, line):
        print('TODO - set windowed mode')

    def do_EOF(self, line):
        return self.do_exit(line)

    def precmd(self, line):
        """
        See if
        :param line:
        :return:
        """
        args = shlex.split(line or "")
        if len(args) and args[0] in self.shortcuts:
            return "%s %s" % (self.shortcuts[args[0]], " ".join(args[1:]))
        else:
            return line

    def postloop(self):
        print('')

