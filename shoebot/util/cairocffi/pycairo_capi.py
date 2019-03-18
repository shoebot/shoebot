# From pycairo
# see pycairo.h

import ctypes
import sys

from ctypes import py_object, c_void_p


class CAPI(ctypes.Structure):
    _fields_ = [
        ("Context_Type", py_object),
        ("Context_FromContext", ctypes.PYFUNCTYPE(py_object, c_void_p, py_object, py_object)),
    ]


def get_capi():
    import cairo
    if sys.version_info[0] == 2:
        PyCObject_AsVoidPtr = ctypes.PYFUNCTYPE(c_void_p, py_object)(
            ('PyCObject_AsVoidPtr', ctypes.pythonapi))
        ptr = PyCObject_AsVoidPtr(cairo.CAPI)
    else:
        PyCapsule_GetPointer = ctypes.PYFUNCTYPE(c_void_p, py_object, c_char_p)(
            ('PyCapsule_GetPointer', ctypes.pythonapi))
        ptr = PyCapsule_GetPointer(cairo.CAPI, b"cairo.CAPI")

    ptr = ctypes.cast(ptr, ctypes.POINTER(CAPI))
    return ptr.contents
