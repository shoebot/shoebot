import cmd

class ShoebotCmd(cmd.Cmd):
    """Simple command processor example."""

    def __init__(self, bot, **kwargs):
        self.bot = bot
        cmd.Cmd.__init__(self, **kwargs)

    def do_greet(self, person):
        """greet [person]
        Greet the named person"""
        if person:
            print "hi,", person
        else:
            print 'hi'

    def do_load(self, **kwargs):
        """

        """
        if not kwargs:
            return
        if kwargs.get('load'):
            print 'Load from file'
            pass
        elif kwargs.get('load64'):
            print 'Load from base64'
            pass

    def do_EOF(self, line):
        self.bot.finish()
        return True
    
    def postloop(self):
        print

#if __name__ == '__main__':
#    ShoebotCmd().cmdloop()