from dataclasses import dataclass, MISSING

from shoebot.core.state.state import State


@dataclass
class TextState(State):
    text: str = MISSING
    x: float = MISSING
    y: float = MISSING
    font_name: str = MISSING
    font_size: float = MISSING
    line_height: float = MISSING
    # align: str


class TextDefaults:
    text = "",
    x = 0
    y = 0
    font_name = "Helvetica"
    font_size = 24
    line_height = 1.2
    # align = LEFT
