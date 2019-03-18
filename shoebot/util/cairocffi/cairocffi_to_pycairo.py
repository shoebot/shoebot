# From cairocffi
from pycairo_capi import get_capi


def _UNSAFE_cairocffi_context_to_pycairo(ctx):
    import cairocffi
    capi = get_capi()

    ptr = ctx._pointer
    cairocffi.cairo.cairo_reference(ptr)
    ptr = int(cairocffi.ffi.cast('uintptr_t', ptr))
    _ctx = capi.Context_FromContext(ptr, capi.Context_Type, None)
    return _ctx
