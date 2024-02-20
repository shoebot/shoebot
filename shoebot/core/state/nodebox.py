from dataclasses import dataclass
from enum import Enum

from shoebot.core.state.color_data import RGBData, RGBAData
from shoebot.core.state.context import ContextState
from shoebot.core.state.state import State


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

class DefaultValuesMixin:
    def __post_init__(self):
        # Iterate list of fields on the parent datafield class
        missing_fields = []
        for field in self.__dataclass_fields__.values():
            try:
                class_value = getattr(self.__class__, field.name)
            except AttributeError:
                missing_fields.append(field.name)
            setattr(self, field.name, class_value)

        if missing_fields:
            raise AttributeError(f"Missing defaults for fields: {missing_fields}")


@dataclass
class PenDefaults(State):
    stroke_width: float = 1.0
    cap_style: str = "butt"


@dataclass
class NodeBotContextDefaults(ContextState, DefaultValuesMixin, PenDefaults):
    """Default values for the NodebotContext"""

    background = RGBData(1, 1, 1)
    fill = RGBData(0, 1, 1)
    stroke = RGBAData(0, 0, 0, 0)

    stroke_width = 1.0
