# TODO - split out all shoebot specific data bits.
"""
ChainDataClass provides a chain of dataclasses, providing attribute lookup in order of the chain.
"""
import dataclasses


class MissingState:
    pass


MISSING = MissingState()


## TODO - move these out and actually implement state using this


# Defaults



class ChainDataClass:
    def __init__(self, *args):
        if not args:
            raise ValueError("At least one dataclass instance is required.")

        _dataclasses = []
        # TODO - this arg checking is temporary
        for arg in args:
            if isinstance(arg, ChainDataClass):
                for _arg in arg._dataclasses:
                    if not dataclasses.is_dataclass(_arg):
                        raise ValueError(f"Expected a dataclass instance, got {type(_arg)} from passed in ChainDataclass")
                _dataclasses.extend(arg._dataclasses)

            elif not dataclasses.is_dataclass(arg):
                raise ValueError(f"Expected a dataclass instance, got {type(arg)}")
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

    def new_child(self, *args):
        return ChainDataClass(*args, *self._dataclasses)
# Usage
## default_settings = Defaults()
## context_settings = Context()
##bezier_path_settings = BezierPath()

#ChainDataClass(bezier_path_settings, context_settings, default_settings)

#chain = ChainDataClass(bezier_path_settings, context_settings, default_settings)
#print(chain.fill)  # This should get the fill color from Defaults (red)
