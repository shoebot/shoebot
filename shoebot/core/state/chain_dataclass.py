# TODO - split out all shoebot specific data bits.
"""
ChainDataClass provides a chain of dataclasses, providing attribute lookup in order of the chain.
"""


class MissingState:
    pass


MISSING = MissingState()


## TODO - move these out and actually implement state using this


# Defaults



class ChainDataClass:
    def __init__(self, *args):
        if not args:
            raise ValueError("At least one dataclass instance is required.")
        self._dataclasses = args

    def __getattr__(self, attr):
        for obj in self._dataclasses:
            if hasattr(obj, attr):
                value = getattr(obj, attr)
                if value is not MISSING:
                    return value
        raise AttributeError(f"No such attribute {attr} found in the chain of objects.")

    def __setitem__(self, key, value):
        setattr(self._dataclasses[0], key, value)
    def __repr__(self):
        return f"<{type(self).__name__} {self._dataclasses}>"


# Usage
## default_settings = Defaults()
## context_settings = Context()
##bezier_path_settings = BezierPath()

#chain = ChainDataClass(bezier_path_settings, context_settings, default_settings)
#print(chain.fill)  # This should get the fill color from Defaults (red)
