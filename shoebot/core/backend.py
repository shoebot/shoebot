class BackendMixin:
    def import_impl(self, module_names, impl_name):
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

    def get_imp(self):
        return {}


class CairoGIBackend(BackendMixin):
    """
    Graphics backend using gi.repository or pgi
    PyCairo / Pycairo + CairoCFFI
    """
    def __init__(self):
        self.cairo_impl, self.cairo_module = self.import_impl(['cairo', 'cairocffi'],
                                                               'Cairo')
        self.gi_impl, self.gi_module = self.setup_gi()

    def get_imp(self):
        return {
            "gi": self.gi_impl,
            "cairo": self.cairo_impl,
        }

    def setup_gi(self):
        name, gi_module = self.import_impl(['gi', 'pgi'], 'gi')
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
            from shoebot.cairocffi_util import _UNSAFE_cairocffi_context_to_pycairo
            return _UNSAFE_cairocffi_context_to_pycairo(ctx)
        else:
            return ctx

    def ensure_cairocffi_context(self, ctx):
        if self.has_cairo and isinstance(ctx, self.cairo.Context):
            from shoebot.cairocffi_util import _UNSAFE_pycairo_context_to_cairocffi
            return _UNSAFE_pycairo_context_to_cairocffi(ctx)
        else:
            return ctx


graphics_impl = CairoGIBackend()
gi = graphics_impl.gi_module
cairo = graphics_impl.cairo_module
