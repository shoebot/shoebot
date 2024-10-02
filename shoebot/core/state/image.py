from dataclasses import dataclass

from shoebot.core.state.state import State


@dataclass
class ImageState(State):
    x: float = 0
    y: float = 0
    width: float = None
    height: float = None
    alpha: float = 1.0
    path: str = None
    format: str = None

    # TODO - work out exactly how the data of the image fits in
    #        with the backend.
    # data: array = None