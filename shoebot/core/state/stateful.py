class Stateful:
    """
    In Shoebot Stateful objects such as Grobs delegate state storage to
    a State object. This allows the state to be stored in a single
    place, and for the state to be shared between multiple objects.
    """
    def __init__(self, _state=None):
        if _state is None:
            state = State()
        self._state = state

    def __getattr__(self, name):
        return getattr(self._state, name)

    def __setattr__(self, name, value):
        if name == "_state":
            super().__setattr__(name, value)
        else:
            setattr(self._state, name, value)

    def __delattr__(self, name):
        delattr(self._state, name)

    def __dir__(self):
        return dir(self._state)

    def __repr__(self):
        return "<Stateful: %s>" % self._state