# TODO - split out all shoebot specific data bits.
"""
ChainDataClass provides a chain of dataclasses, providing attribute lookup in order of the chain.
"""
import dataclasses
from functools import lru_cache


class MissingState:
    pass


MISSING = MissingState()




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

        # Avoid custom setattr to avoid infinite recursion
        super().__setattr__("_dataclasses", args)

    @lru_cache(maxsize=1)
    def _get_fieldnames(self):
        # Each dataclass may have less fields than the lower one, so
        # the top level dataclass is the reference.
        toplevel_dataclass = self._dataclasses[0]
        return {field.name for field in dataclasses.fields(toplevel_dataclass)}

    def __getattr__(self, attr):
        if attr in self._get_fieldnames():
            for i, obj in enumerate(self._dataclasses):
                value = getattr(obj, attr, MISSING)
                if value is not MISSING:
                    return value

            raise AttributeError(f"AttributeError: attribute {attr} unset on chain of objects.")

        raise AttributeError(f"AttributeError: type object '{type(self)}' has no attribute '{attr}'")

    def __iter__(self):
        return iter(self._dataclasses)

    def __setattr__(self, key, value):
        setattr(self._dataclasses[0], key, value)

    def __repr__(self):
        return f"<{type(self).__name__} {self._dataclasses}>"

    def freeze(self):
        """
        Freeze the first dataclass in the chain.

        Any missing values are replaced by non missing values
        further up the chain.
        """
        # TODO - matrices need a way of special casing themselves...
        #        as they combine with the underlying matrix.
        obj = self._dataclasses[0]
        for field in dataclasses.fields(obj):
            value = getattr(obj, field.name)
            if value is MISSING:
                new_value = getattr(self, field.name)
                setattr(obj, field.name, new_value)

        return obj

    def new_child(self, *args):
        return ChainDataClass(*args, *self._dataclasses)

    def parent(self):
        return ChainDataClass(*self._dataclasses[1:])

# Usage
## default_settings = Defaults()
## context_settings = Context()
##bezier_path_settings = BezierPath()

#ChainDataClass(bezier_path_settings, context_settings, default_settings)

#chain = ChainDataClass(bezier_path_settings, context_settings, default_settings)
#print(chain.fill)  # This should get the fill color from Defaults (red)
