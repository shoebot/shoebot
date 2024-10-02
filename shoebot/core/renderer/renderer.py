import abc
from typing import Any


class Renderer(metaclass=abc.ABCMeta):
    def __init__(self, target: Any):
        """
        :target the native target to render to.
        """
        self.target = target

    def __del__(self):
        del self.target

    @abc.abstractmethod
    def render_pathelement(self, element):
        """
        Run command corresponding to this PathElement on a cairo Context.
        """
        pass

    @abc.abstractmethod
    def render_bezierpath(self, path, state):
        pass
