"""
Cairo implementation and GObject preference can be set by channging the environment variable SHOEBOT_GRAPHICS.

Cairo:

Shoebot Core [cairo|cairocffi]
Shoebot GUI  [cairo (can convert from cairocffi]

GObject:

GI  - Works for everything
PGI - Text does not work (because of Pango issues).


Environment variable:

Set SHOEBOT_GRAPHICS environment variable to change the order Shoebot will try import graphics modules.

SHOEBOT_GRAPHICS='cairo=cairocffi,cairo gi=pgi'

There is currently no output if Shoebot can't use the chosen implementation.


Check settings

Use setup.py diagnose to output the current graphics settings.
"""

import os
import sys


class BackendMixin(object):
    """
    Mixin to abstract different implementations of the same library.
    """

    def import_libs(self, module_names, impl_name):
        """
        Loop through module_names,
        add has_.... booleans to class
        set ..._impl to first successful import

        :param module_names:  list of module names to try importing
        :param impl_name:  used in error output if no modules succeed
        :return: name, module from first successful implementation
        """
        for name in module_names:
            try:
                module = __import__(name)
                has_module = True
            except ImportError:
                module = None
                has_module = False
            setattr(self, name, module)
            setattr(self, 'has_%s' % name, has_module)

        for name in module_names:
            try:
                return name, __import__(name)
            except ImportError:
                pass
        raise ImportError('No %s Implementation found, tried: %s' % (impl_name, ' '.join(module_names)))

    def get_libs(self):
        return {}


def sort_by_preference(options, prefer):
    """
    :param options: List of options
    :param prefer: Prefered options
    :return:

    Pass in a list of options, return options in 'prefer' first

    >>> sort_by_preference(["cairo", "cairocffi"], ["cairocffi"])
    ["cairocffi", "cairo"]
    """
    if not prefer:
        return options
    return sorted(options, key=lambda x: (prefer + options).index(x))


class CairoGIBackend(BackendMixin):
    """
    Graphics backend using gi.repository or pgi
    PyCairo / CairoCFFI (+PyCairo needed if using Gtk Too)
    """
    def __init__(self, options):
        cairo_pref = sort_by_preference(["cairo", "cairocffi"], options.get("cairo", "").split(','))
        gi_pref = sort_by_preference(["gi", "pgi"], options.get("gi", "").split(','))
        self.cairo_lib, self.cairo_module = self.import_libs(cairo_pref,
                                                             'Cairo')
        self.gi_lib, self.gi_module = self.setup_gi(gi_pref)

    def get_libs(self):
        return {
            "gi": self.gi_lib,
            "cairo": self.cairo_lib,
        }

    def setup_gi(self, gi_pref):
        name, gi_module = self.import_libs(['gi', 'pgi'], 'gi')
        if name == 'pgi':
            gi_module.install_as_gi()
        return name, gi_module

    def ensure_pycairo_context(self, ctx):
        """
        If ctx is a cairocffi Context convert it to a PyCairo Context
        otherwise return the original context

        :param ctx:
        :return:
        """
        if self.cairocffi and isinstance(ctx, self.cairocffi.Context):
            from shoebot.util.cairocffi.cairocffi_to_pycairo import _UNSAFE_cairocffi_context_to_pycairo
            return _UNSAFE_cairocffi_context_to_pycairo(ctx)
        else:
            return ctx


def get_driver_options():
    """
    Interpret env var as key=value
    :return:
    """
    options = os.environ.get("SHOEBOT_GRAPHICS")
    if not options:
        return {}

    try:
        return dict([kv.split('=') for kv in options.split()])
    except ValueError:
        sys.stderr.write("Bad option format.\n")
        sys.stderr.write("Environment variable should be in the format key=value separated by spaces.\n\n")
        sys.stderr.write("SHOEBOT_GRAPHICS='cairo=cairocffi,cairo gi=pgi'\n")
        sys.exit(1)


driver = CairoGIBackend(get_driver_options())
gi = driver.gi_module
cairo = driver.cairo_module
