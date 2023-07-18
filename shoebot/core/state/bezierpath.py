"""
Graphics state required by backends to graphics.BezierPath.

See `state.py` for more information.
"""
from dataclasses import dataclass
from .chain_dataclass import MISSING
from .state import State
from .color import ColorState
from .pen import PenState

@dataclass
class BezierPathState(State):
    # TODO this should really extend the relevant base dataclasses
    fill: ColorState = MISSING
    stroke: ColorState = MISSING
    pen: PenState = MISSING
    closed: bool = False
