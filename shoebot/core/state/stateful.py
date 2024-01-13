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
        self._state = state
        if parent_state is None:
            self._stacked_state = ChainDataClass(state)
        else:
            self._stacked_state = ChainDataClass(state, parent_state)

    def __repr__(self):
        return f"<{type(self)}: {self._state}>"

class StateValueContainer:
    def __init__(self, attribute_name: str):
        self._state_attribute_name = attribute_name
    @property
    def __state_value__(self):
        return getattr(self, self._state_attribute_name)
