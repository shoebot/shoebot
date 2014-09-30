## nodebox compatibility - from nodebox1

# shoebot -
# Currently (2013-April) only has enough to make nodebox - evolution
# work - since this is obsolete unlikely that much more will need
# to be added.


# This file is obsolete.
# NodeBox now uses a package structure.
# The drawing primitives are now in the new "nodebox.graphics" package.
# This will also ensure you get the graphics package for the correct platform.

from shoebot.data import CENTER, LEFT, RIGHT

__all__ = ['files', 'random']

import warnings
warnings.warn('DrawingPrimitives is deprecated. Please use "from nodebox import graphics"', DeprecationWarning, stacklevel=2)

from glob import glob
import random as _random

def files(pattern = '*'):
    return glob(pattern)


def random(v1 = None, v2 = None):
    if isinstance(v1, int):
        if v2 is None:
            v2 = v1 + 1
        return _random.randint(min(v1, v2), max(v1, v2))
    elif isinstance(v1, float):
        if v2 is None:
            return _random.random() * v1
        else:
            return _random.uniform(v1, v2)
    pass
