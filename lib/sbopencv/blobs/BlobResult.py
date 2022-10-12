# This file was automatically generated by SWIG (http://www.swig.org).
# Version 1.3.31
#
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.

from . import _BlobResult
import new
new_instancemethod = new.instancemethod
try:
    _swig_property = property
except NameError:
    pass # Python < 2.2 doesn't have 'property'.
def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "thisown"): return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'PySwigObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static) or hasattr(self,name):
        self.__dict__[name] = value
    else:
        raise AttributeError(f"You cannot add attributes to {self}")

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    if (name == "thisown"): return self.this.own()
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError(name)

def _swig_repr(self):
    try: strthis = "proxy of " + self.this.__repr__()
    except: strthis = ""
    return f"<{self.__class__.__module__}.{self.__class__.__name__}; {strthis} >"

import types
try:
    _object = object
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0
del types


B_INCLUDE = _BlobResult.B_INCLUDE
B_EXCLUDE = _BlobResult.B_EXCLUDE
B_EQUAL = _BlobResult.B_EQUAL
B_NOT_EQUAL = _BlobResult.B_NOT_EQUAL
B_GREATER = _BlobResult.B_GREATER
B_LESS = _BlobResult.B_LESS
B_GREATER_OR_EQUAL = _BlobResult.B_GREATER_OR_EQUAL
B_LESS_OR_EQUAL = _BlobResult.B_LESS_OR_EQUAL
B_INSIDE = _BlobResult.B_INSIDE
B_OUTSIDE = _BlobResult.B_OUTSIDE
EXCEPTION_BLOB_OUT_OF_BOUNDS = _BlobResult.EXCEPTION_BLOB_OUT_OF_BOUNDS
EXCEPCIO_CALCUL_BLOBS = _BlobResult.EXCEPCIO_CALCUL_BLOBS
class CBlobResult(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, CBlobResult, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobResult, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _BlobResult.new_CBlobResult(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _BlobResult.delete_CBlobResult
    __del__ = lambda self : None;
    def __add__(*args): return _BlobResult.CBlobResult___add__(*args)
    def filter_blobs(*args): return _BlobResult.CBlobResult_filter_blobs(*args)
    def AddBlob(*args): return _BlobResult.CBlobResult_AddBlob(*args)
    def GetSTLResult(*args): return _BlobResult.CBlobResult_GetSTLResult(*args)
    def GetNumber(*args): return _BlobResult.CBlobResult_GetNumber(*args)
    def Filter(*args): return _BlobResult.CBlobResult_Filter(*args)
    def GetNthBlob(*args): return _BlobResult.CBlobResult_GetNthBlob(*args)
    def GetBlob(*args): return _BlobResult.CBlobResult_GetBlob(*args)
    def ClearBlobs(*args): return _BlobResult.CBlobResult_ClearBlobs(*args)
    def PrintBlobs(*args): return _BlobResult.CBlobResult_PrintBlobs(*args)
    def GetNumBlobs(*args): return _BlobResult.CBlobResult_GetNumBlobs(*args)
CBlobResult_swigregister = _BlobResult.CBlobResult_swigregister
CBlobResult_swigregister(CBlobResult)



