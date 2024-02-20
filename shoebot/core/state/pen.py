from dataclasses import dataclass

from shoebot.core.state.chain_dataclass import MISSING
from shoebot.core.state.state import State


@dataclass
class PenState(State):
    stroke_width: float = MISSING