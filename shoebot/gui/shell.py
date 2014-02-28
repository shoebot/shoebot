import base64
import cmd
import copy

class ShoebotCmd(cmd.Cmd):
    """Simple command processor example."""

    def __init__(self, bot, **kwargs):
        self.bot = bot
        cmd.Cmd.__init__(self, **kwargs)
        self.intro = 'Experimental Feature - for ide integration.'
        self.prompt = '(bot) '

    def do_speed(self, speed):
        """rewind
        """
        try:
            self.bot._speed = float(speed)
        except:
            pass

    def do_restart(self, line):
        # TODO - restart
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
        try:
            print 'shoebot: load_base64 '
            print line
            source = str(base64.b64decode(line))
            self.bot.source_or_code = compile(source + '\n\n', "shoebot_code", "exec")
            #self.bot.source_or_code = compile("def draw():\n    print FRAME" + '\n\n', "shoebot_code", "exec")
            exec self.bot.source_or_code in self.bot._namespace
            #self.bot._load_namespace()
        except Exception as e:
            print 'got exception'
            print e

    def d(self, line):
        if not kwargs:
            return
        if kwargs.get('filename'):
            print 'Load from file'
            pass
        elif kwargs.get('base64'):
            print 'Load from base64'
            pass

    def do_bye(self, line):
        self.bot._quit = True
        return True

    def do_exit(self, line):
        self.bot._quit = True
        return True

    def do_quit(self, line):
        self.bot._quit = True
        return True

    def do_EOF(self, line):
        self.bot._quit = True
        return True
    
    def postloop(self):
        print

#if __name__ == '__main__':
#    ShoebotCmd().cmdloop()