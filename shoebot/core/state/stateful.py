from typing import Optional

from shoebot.core.state.chain_dataclass import ChainDataClass
from shoebot.core.state.state import State


class Stateful:
    """
    Stateful objects such as Grobs delegate state storage to
    a State object.

    This allows the state to be stored in a single
    place, and for the state to be shared between multiple objects.
    """
    def __init__(self, state: State, parent_state: Optional[State] = None):
        self.__state__ = state
        if parent_state is None:
            self.__state_stack__ = ChainDataClass(state)
        else:
            self.__state_stack__ = ChainDataClass(state, parent_state)

    def __repr__(self):
        return f"<{type(self)}: {self.__state__}>"

def get_state(obj: Stateful):
    return obj.__state__

class StateValueContainer:
    def __init__(self, attribute_name: str):
        self.__state_attribute_name__ = attribute_name
    @property
    def __state_value__(self):
        return getattr(self, self.__state_attribute_name__)


def get_state_value(container: StateValueContainer):
    return container.__state_value__