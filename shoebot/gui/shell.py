import base64
import cmd
import copy
import compiler

class ShoebotCmd(cmd.Cmd):
    """Simple command processor example."""

    def __init__(self, bot, **kwargs):
        self.bot = bot
        cmd.Cmd.__init__(self, **kwargs)
        self.intro = 'Experimental Feature - for ide integration.'
        self.prompt = '(bot) '
        self.use_rawinput = False

    def handler(signum, frame):
        print 'Caught CTRL-C, press enter to continue'

    def do_title(self, title):
        """
        Change window title.
        """
        pass

    def do_speed(self, speed):
        """rewind
        """
        try:
            self.bot._speed = float(speed)
        except:
            pass

    def do_restart(self, line):
        """
        Attempt to restart the bot.
        """
        self.bot._namespace.clear()
        self.bot._namespace.update(self.bot._initial_namespace)


    def do_rewind(self, line):
        """rewind
        """
        self.bot._frame = 0

    def do_load_base64(self, line):
        """
        load filename=(file)
        load base64=(base64 encoded)
        """
        print 'shoebot: load_base64 '
        try:
            source = str(base64.b64decode(line))
            code = compile(source + '\n\n', "shoebot_code", "exec")
            self.bot._executor.load_edited_code(code)
        except Exception as e:
            print 'Error Compiling'
            print e

    def do_bye(self, line):
        return self.do_exit(line)

    def do_exit(self, line):
        print('Bye.')
        self.bot._quit = True
        return True

    def do_quit(self, line):
        return self.do_exit(line)

    def do_EOF(self, line):
        return self.do_exit(line)
    
    def postloop(self):
        print

#if __name__ == '__main__':
#    ShoebotCmd().cmdloop()

