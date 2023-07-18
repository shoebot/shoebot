from dataclasses import dataclass

from shoebot.core.state.chain_dataclass import MISSING


@dataclass
class RGBColorData:
    red: float = 0.0
    green: float = 0.0
    blue: float = 0.0


@dataclass
class RGBAColorData(RGBColorData):
    alpha: float = 1.0


@dataclass
class ColorState:
    data: RGBAColorData = MISSING


class ColorDefaults:
    fill: ColorState = ColorState(data=RGBAColorData(1.0, 0.0, 0.0))  # Default fill color: Red
    stroke: ColorState = ColorState(data=RGBAColorData(0.0, 0.0, 1.0))  # Default stroke color: Blue
