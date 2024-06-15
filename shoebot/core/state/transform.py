from dataclasses import dataclass

from affine import Affine

from shoebot.core.state.chain_dataclass import MISSING
from shoebot.core.state.state import State


@dataclass
class TransformState(State):
    affine_transform: Affine = MISSING
