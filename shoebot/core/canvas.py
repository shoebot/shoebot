import sys
import shoebot
import locale, gettext
APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
#gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext

class Canvas:
    '''
    This class contains a Cairo context or surface, as well as methods to pass
    drawing commands to it.

    Its intended use is to get drawable objects from a Bot instance, store them
    in a stack and draw them to the Cairo context when necessary.
    '''
    def __init__(self, bot=None, target=None, width=None, height=None, gtkmode=False):

        if bot:
            self._bot = bot

        self.grobstack = []
        self.font_size = 12
        # self.outputmode = RGB
        # self.linecap
        # self.linejoin
        # self.fontweight
        # self.fontslant
        # self.hintmetrics
        # self.hintstyle
        # self.filter
        # self.operator
        # self.antialias
        # self.fillrule

    def add(self, grob):
        if not isinstance(grob, shoebot.data.Grob):
            raise ValueError(_("Canvas.add() - wrong argument: expecting a Grob, received %s") % (grob))
        self.grobstack.append(grob)

    def append(self, grob):
        self.add(self, grob)

    def setsurface(self):
        pass
    def get_context(self):
        return self._context
    def get_surface(self):
        return self._surface

    def draw(self, ctx=None):
        pass
    def output(self, filename):
        pass

    def clear(self):
        self.grobstack = []

