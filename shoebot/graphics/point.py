from dataclasses import dataclass
from typing import Optional


@dataclass
class Point:
    """Taken from Nodebox and modified."""
    x: float = 0.0
    y: Optional[float] = None
    def __post_init__(self):
        if self.y is None:
            self.y = self.x
    @property
    def xy(self):
        # Taken from Nodebox-GL
        return self.x, self.y