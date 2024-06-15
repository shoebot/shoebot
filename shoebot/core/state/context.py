import dataclasses

from affine import Affine

from shoebot.core.state.chain_dataclass import MISSING
from shoebot.core.state.pen import PenState
from shoebot.core.state.color_data import ColorData
from shoebot.core.state.transform import TransformState


# Context (can have its own values, or use defaults)

@dataclasses.dataclass
class ContextState(PenState, TransformState):
    background: ColorData = MISSING
    fill: ColorData = MISSING
    stroke: ColorData = MISSING
    affine_transform: Affine = MISSING
