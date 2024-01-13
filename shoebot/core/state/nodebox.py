from dataclasses import dataclass
from enum import Enum

from shoebot.core.state.color_data import RGBData, RGBAData
from shoebot.core.state.context import ContextState



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
@dataclass
class NodeBotContextDefaults(ContextState):
    """Default values for the NodebotContext"""
    # TODO - review the types, we may need less.

    def __init__(self):
        self.fill = RGBData(0, 0, 1)
        self.stroke = RGBAData(0, 0, 0, 0)