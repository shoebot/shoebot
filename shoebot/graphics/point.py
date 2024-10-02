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

        # TODO - remove these asserts, or only enable during testing somehow.
        assert isinstance(self.x, (int, float)), f"Expected x to be a number, got {self.x}"
        assert isinstance(self.y, (int, float)), f"Expected y to be a number, got {self.y}"
    def __iter__(self):
        return iter((self.x, self.y))

    @property
    def xy(self):
        # Taken from Nodebox-GL
        return self.x, self.y