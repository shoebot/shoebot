from shoebot.data import _copy_attrs

class Grob(object):
    """A GRaphic OBject is the base class for all DrawingPrimitives."""

    def __init__(self, bot):
        """Initializes this object with the current bot instance."""
        self._bot = bot
        
    def copy(self):
        """Returns a deep copy of this grob."""
        raise NotImplementedError, _("Copy is not implemented on this Grob class.")

    def draw(self):
        """Appends the grob to the canvas.
           This will result in a draw later on, when the scene graph is rendered."""
        
        self._bot.canvas.add(self)
##
##    def inheritFromContext(self, ignore=()):
##        attrs_to_copy = list(self.__class__.stateAttributes)
##        [attrs_to_copy.remove(k) for k, v in _STATE_NAMES.items() if v in ignore]
##        _copy_attrs(self._bot, self, attrs_to_copy)

    def checkKwargs(self, kwargs):
        remaining = [arg for arg in kwargs.keys() if arg not in self.kwargs]
        if remaining:
            raise ValueError, _("Unknown argument(s) '%s'") % ", ".join(remaining)
    checkKwargs = classmethod(checkKwargs)


