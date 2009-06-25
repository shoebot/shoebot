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

TOP_LEFT = 1
BOTTOM_LEFT = 2

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

        self.width = 200
        self.height = 200
        self.origin = TOP_LEFT

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
        self.drawitem(grob)

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
    def drawitem(self, grob):
        pass
    def output(self, filename):
        pass

    def clear(self):
        self.grobstack = []


    def set_size(self, x, y):
        # reset transforms
        self.context.identity_matrix()
        self.width = x
        self.height = y

    def flip(self):
        w = self.width
        h = self.height
        self.context.translate(w/2., h/2.)
        self.context.scale(1,-1)
        self.context.translate(-w/2., -h/2.)

