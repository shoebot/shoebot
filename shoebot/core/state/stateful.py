from typing import Optional

from shoebot.core.state.chain_dataclass import ChainDataClass
from shoebot.core.state.state import State
from shoebot.core.state.state_value import get_state_value


class Stateful:
    """
    Stateful objects such as Grobs delegate state storage to
    a State object.

    This allows the state to be stored in a single
    place, and for the state to be shared between multiple objects.
    """
    _state_fields = {}
    _state_container_fields = {}

    def __init__(self, state: State, parent_state: Optional[State] = None):
        self.__state__ = state
        if parent_state is None:
            self.__state_stack__ = ChainDataClass(state)
        else:
            self.__state_stack__ = ChainDataClass(state, parent_state)

    def _state_kwargs(self, **kwargs):
        if not self._state_container_fields:
            return kwargs

        # TODO, probably need more general mapping from Stateful to State
        # that works for both kinds of fields.
        state_kwargs = {
            self._state_fields.get(field_name): field_args
            for field_name, field_args in kwargs.items()
            if field_name in self._state_fields
        }

        container_kwargs = {
            field_name: get_state_value(container_type(*kwargs[field_name]))
            for field_name, container_type in self._state_container_fields.items()
            if field_name in kwargs
        }

        return {**state_kwargs, **container_kwargs}

    def __repr__(self):
        return f"<{type(self)}: {self.__state__}>"

def get_state(obj: Stateful):
    return obj.__state__

def get_state_stack(obj: Stateful):
    return obj.__state_stack__