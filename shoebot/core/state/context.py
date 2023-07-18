from shoebot.core.state.chain_dataclass import MISSING
from shoebot.core.state.pen import PenDefaults
from shoebot.core.state.color import ColorDefaults, ColorState
from shoebot.core.state.state import State


# Context (can have its own values, or use defaults)
class Context(State):
    fill: ColorState = MISSING
    stroke: ColorState = MISSING
    # pen: Pen = MISSING


# NodeBox Context._resetContext:
# (so we can see the defaults)
#
#     def _resetContext(self):
#         self._vars = self._oldvars
#         self._outputmode = RGB
#         self._colormode = RGB
#         self._colorrange = 1.0
#         self._fillcolor = self.Color()
#         self._strokecolor = None
#         self._strokewidth = 1.0
#         self._capstyle = BUTT
#         self._joinstyle = MITER
#         self.canvas.background = self.Color(1.0)
#         self._path = None
#         self._autoclosepath = True
#         self._transform = Transform()
#         self._transformmode = CENTER
#         self._transformstack = []
#         self._fontname = "Helvetica"
#         self._fontsize = 24
#         self._lineheight = 1.2
#         self._align = LEFT
#         self._noImagesHint = False
#         self._oldvars = self._vars
#         self._vars = []

class ContextDefaults(ColorDefaults, PenDefaults):
    pass