import dataclasses

from shoebot.core.state.chain_dataclass import MISSING
from shoebot.core.state.pen import PenState
from shoebot.core.state.color_data import ColorData


# Context (can have its own values, or use defaults)

@dataclasses.dataclass
class ContextState(PenState):
    background: ColorData = MISSING
    fill: ColorData = MISSING
    stroke: ColorData = MISSING
