"""
Graphics state required by backends to graphics.BezierPath.

See `state.py` for more information.
"""
from dataclasses import dataclass
from .chain_dataclass import MISSING
from .state import State
from .color_data import ColorData
from .pen import PenState

@dataclass
class BezierPathState(State):
    # TODO this should really extend the relevant base dataclasses
    fill: ColorData = MISSING
    stroke: ColorData = MISSING
    pen: PenState = MISSING
    closed: bool = False
