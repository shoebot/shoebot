import dataclasses

from shoebot.core.state.chain_dataclass import MISSING
from shoebot.core.state.pen import PenDefaults
from shoebot.core.state.color_data import ColorData
from shoebot.core.state.state import State


# Context (can have its own values, or use defaults)

@dataclasses.dataclass
class ContextState(State):
    fill: ColorData = MISSING
    stroke: ColorData = MISSING
    # pen: Pen = MISSING
