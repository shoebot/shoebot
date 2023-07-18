from dataclasses import dataclass, MISSING

from shoebot.core.state.state import State


@dataclass
class TextState(State):
    font_name: str = MISSING
    font_size: float = MISSING
    line_height: float = MISSING
    # align: str


class TextDefaults:
    font_name = "Helvetica"
    font_size = 24
    line_height = 1.2
    # align = LEFT
