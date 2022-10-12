# This file was automatically generated by SWIG (http://www.swig.org).
# Version 1.3.31
#
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.

import new

from . import _Blob

new_instancemethod = new.instancemethod
try:
    _swig_property = property
except NameError:
    pass  # Python < 2.2 doesn't have 'property'.


def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if name == "thisown":
        return self.this.own(value)
    if name == "this":
        if type(value).__name__ == "PySwigObject":
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if (not static) or hasattr(self, name):
        self.__dict__[name] = value
    else:
        raise AttributeError(f"You cannot add attributes to {self}")


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr(self, class_type, name):
    if name == "thisown":
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    raise AttributeError(name)


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except:
        strthis = ""
    return f"<{self.__class__.__module__}.{self.__class__.__name__}; {strthis} >"


import types

try:
    _object = object
    _newclass = 1
except AttributeError:

    class _object:
        pass

    _newclass = 0
del types


class CBlob(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, CBlob, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlob, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _Blob.new_CBlob(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlob
    __del__ = lambda self: None

    def IsEmpty(*args):
        return _Blob.CBlob_IsEmpty(*args)

    def ClearEdges(*args):
        return _Blob.CBlob_ClearEdges(*args)

    def CopyEdges(*args):
        return _Blob.CBlob_CopyEdges(*args)

    def GetConvexHull(*args):
        return _Blob.CBlob_GetConvexHull(*args)

    def GetEllipse(*args):
        return _Blob.CBlob_GetEllipse(*args)

    def FillBlob(*args):
        return _Blob.CBlob_FillBlob(*args)

    def Label(*args):
        return _Blob.CBlob_Label(*args)

    def Parent(*args):
        return _Blob.CBlob_Parent(*args)

    def Area(*args):
        return _Blob.CBlob_Area(*args)

    def Perimeter(*args):
        return _Blob.CBlob_Perimeter(*args)

    def ExternPerimeter(*args):
        return _Blob.CBlob_ExternPerimeter(*args)

    def Exterior(*args):
        return _Blob.CBlob_Exterior(*args)

    def Mean(*args):
        return _Blob.CBlob_Mean(*args)

    def StdDev(*args):
        return _Blob.CBlob_StdDev(*args)

    def MinX(*args):
        return _Blob.CBlob_MinX(*args)

    def MinY(*args):
        return _Blob.CBlob_MinY(*args)

    def MaxX(*args):
        return _Blob.CBlob_MaxX(*args)

    def MaxY(*args):
        return _Blob.CBlob_MaxY(*args)

    def Edges(*args):
        return _Blob.CBlob_Edges(*args)

    def SumX(*args):
        return _Blob.CBlob_SumX(*args)

    def SumY(*args):
        return _Blob.CBlob_SumY(*args)

    def SumXX(*args):
        return _Blob.CBlob_SumXX(*args)

    def SumYY(*args):
        return _Blob.CBlob_SumYY(*args)

    def SumXY(*args):
        return _Blob.CBlob_SumXY(*args)

    __swig_setmethods__["etiqueta"] = _Blob.CBlob_etiqueta_set
    __swig_getmethods__["etiqueta"] = _Blob.CBlob_etiqueta_get
    if _newclass:
        etiqueta = _swig_property(_Blob.CBlob_etiqueta_get, _Blob.CBlob_etiqueta_set)
    __swig_setmethods__["exterior"] = _Blob.CBlob_exterior_set
    __swig_getmethods__["exterior"] = _Blob.CBlob_exterior_get
    if _newclass:
        exterior = _swig_property(_Blob.CBlob_exterior_get, _Blob.CBlob_exterior_set)
    __swig_setmethods__["area"] = _Blob.CBlob_area_set
    __swig_getmethods__["area"] = _Blob.CBlob_area_get
    if _newclass:
        area = _swig_property(_Blob.CBlob_area_get, _Blob.CBlob_area_set)
    __swig_setmethods__["perimeter"] = _Blob.CBlob_perimeter_set
    __swig_getmethods__["perimeter"] = _Blob.CBlob_perimeter_get
    if _newclass:
        perimeter = _swig_property(_Blob.CBlob_perimeter_get, _Blob.CBlob_perimeter_set)
    __swig_setmethods__["externPerimeter"] = _Blob.CBlob_externPerimeter_set
    __swig_getmethods__["externPerimeter"] = _Blob.CBlob_externPerimeter_get
    if _newclass:
        externPerimeter = _swig_property(
            _Blob.CBlob_externPerimeter_get,
            _Blob.CBlob_externPerimeter_set,
        )
    __swig_setmethods__["parent"] = _Blob.CBlob_parent_set
    __swig_getmethods__["parent"] = _Blob.CBlob_parent_get
    if _newclass:
        parent = _swig_property(_Blob.CBlob_parent_get, _Blob.CBlob_parent_set)
    __swig_setmethods__["sumx"] = _Blob.CBlob_sumx_set
    __swig_getmethods__["sumx"] = _Blob.CBlob_sumx_get
    if _newclass:
        sumx = _swig_property(_Blob.CBlob_sumx_get, _Blob.CBlob_sumx_set)
    __swig_setmethods__["sumy"] = _Blob.CBlob_sumy_set
    __swig_getmethods__["sumy"] = _Blob.CBlob_sumy_get
    if _newclass:
        sumy = _swig_property(_Blob.CBlob_sumy_get, _Blob.CBlob_sumy_set)
    __swig_setmethods__["sumxx"] = _Blob.CBlob_sumxx_set
    __swig_getmethods__["sumxx"] = _Blob.CBlob_sumxx_get
    if _newclass:
        sumxx = _swig_property(_Blob.CBlob_sumxx_get, _Blob.CBlob_sumxx_set)
    __swig_setmethods__["sumyy"] = _Blob.CBlob_sumyy_set
    __swig_getmethods__["sumyy"] = _Blob.CBlob_sumyy_get
    if _newclass:
        sumyy = _swig_property(_Blob.CBlob_sumyy_get, _Blob.CBlob_sumyy_set)
    __swig_setmethods__["sumxy"] = _Blob.CBlob_sumxy_set
    __swig_getmethods__["sumxy"] = _Blob.CBlob_sumxy_get
    if _newclass:
        sumxy = _swig_property(_Blob.CBlob_sumxy_get, _Blob.CBlob_sumxy_set)
    __swig_setmethods__["minx"] = _Blob.CBlob_minx_set
    __swig_getmethods__["minx"] = _Blob.CBlob_minx_get
    if _newclass:
        minx = _swig_property(_Blob.CBlob_minx_get, _Blob.CBlob_minx_set)
    __swig_setmethods__["maxx"] = _Blob.CBlob_maxx_set
    __swig_getmethods__["maxx"] = _Blob.CBlob_maxx_get
    if _newclass:
        maxx = _swig_property(_Blob.CBlob_maxx_get, _Blob.CBlob_maxx_set)
    __swig_setmethods__["miny"] = _Blob.CBlob_miny_set
    __swig_getmethods__["miny"] = _Blob.CBlob_miny_get
    if _newclass:
        miny = _swig_property(_Blob.CBlob_miny_get, _Blob.CBlob_miny_set)
    __swig_setmethods__["maxy"] = _Blob.CBlob_maxy_set
    __swig_getmethods__["maxy"] = _Blob.CBlob_maxy_get
    if _newclass:
        maxy = _swig_property(_Blob.CBlob_maxy_get, _Blob.CBlob_maxy_set)
    __swig_setmethods__["mean"] = _Blob.CBlob_mean_set
    __swig_getmethods__["mean"] = _Blob.CBlob_mean_get
    if _newclass:
        mean = _swig_property(_Blob.CBlob_mean_get, _Blob.CBlob_mean_set)
    __swig_setmethods__["stddev"] = _Blob.CBlob_stddev_set
    __swig_getmethods__["stddev"] = _Blob.CBlob_stddev_get
    if _newclass:
        stddev = _swig_property(_Blob.CBlob_stddev_get, _Blob.CBlob_stddev_set)
    __swig_setmethods__["m_storage"] = _Blob.CBlob_m_storage_set
    __swig_getmethods__["m_storage"] = _Blob.CBlob_m_storage_get
    if _newclass:
        m_storage = _swig_property(_Blob.CBlob_m_storage_get, _Blob.CBlob_m_storage_set)
    __swig_setmethods__["edges"] = _Blob.CBlob_edges_set
    __swig_getmethods__["edges"] = _Blob.CBlob_edges_get
    if _newclass:
        edges = _swig_property(_Blob.CBlob_edges_get, _Blob.CBlob_edges_set)


CBlob_swigregister = _Blob.CBlob_swigregister
CBlob_swigregister(CBlob)


class CBlobGetArea(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetArea,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetArea, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetArea___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetArea_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetArea(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetArea
    __del__ = lambda self: None


CBlobGetArea_swigregister = _Blob.CBlobGetArea_swigregister
CBlobGetArea_swigregister(CBlobGetArea)


class CBlobGetPerimeter(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetPerimeter,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetPerimeter, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetPerimeter___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetPerimeter_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetPerimeter(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetPerimeter
    __del__ = lambda self: None


CBlobGetPerimeter_swigregister = _Blob.CBlobGetPerimeter_swigregister
CBlobGetPerimeter_swigregister(CBlobGetPerimeter)


class CBlobGetExterior(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetExterior,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetExterior, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetExterior___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetExterior_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetExterior(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetExterior
    __del__ = lambda self: None


CBlobGetExterior_swigregister = _Blob.CBlobGetExterior_swigregister
CBlobGetExterior_swigregister(CBlobGetExterior)


class CBlobGetMean(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetMean,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetMean, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetMean___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetMean_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetMean(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetMean
    __del__ = lambda self: None


CBlobGetMean_swigregister = _Blob.CBlobGetMean_swigregister
CBlobGetMean_swigregister(CBlobGetMean)


class CBlobGetStdDev(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetStdDev,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetStdDev, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetStdDev___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetStdDev_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetStdDev(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetStdDev
    __del__ = lambda self: None


CBlobGetStdDev_swigregister = _Blob.CBlobGetStdDev_swigregister
CBlobGetStdDev_swigregister(CBlobGetStdDev)


class CBlobGetCompactness(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetCompactness,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetCompactness, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetCompactness___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetCompactness_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetCompactness(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetCompactness
    __del__ = lambda self: None


CBlobGetCompactness_swigregister = _Blob.CBlobGetCompactness_swigregister
CBlobGetCompactness_swigregister(CBlobGetCompactness)


class CBlobGetLength(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetLength,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetLength, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetLength___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetLength_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetLength(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetLength
    __del__ = lambda self: None


CBlobGetLength_swigregister = _Blob.CBlobGetLength_swigregister
CBlobGetLength_swigregister(CBlobGetLength)


class CBlobGetBreadth(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetBreadth,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetBreadth, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetBreadth___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetBreadth_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetBreadth(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetBreadth
    __del__ = lambda self: None


CBlobGetBreadth_swigregister = _Blob.CBlobGetBreadth_swigregister
CBlobGetBreadth_swigregister(CBlobGetBreadth)


class CBlobGetDiffX(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetDiffX,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetDiffX, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetDiffX___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetDiffX_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetDiffX(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetDiffX
    __del__ = lambda self: None


CBlobGetDiffX_swigregister = _Blob.CBlobGetDiffX_swigregister
CBlobGetDiffX_swigregister(CBlobGetDiffX)


class CBlobGetDiffY(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetDiffY,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetDiffY, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetDiffY___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetDiffY_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetDiffY(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetDiffY
    __del__ = lambda self: None


CBlobGetDiffY_swigregister = _Blob.CBlobGetDiffY_swigregister
CBlobGetDiffY_swigregister(CBlobGetDiffY)


class CBlobGetMoment(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetMoment,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetMoment, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _Blob.new_CBlobGetMoment(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    def __call__(*args):
        return _Blob.CBlobGetMoment___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetMoment_GetNom(*args)

    __swig_destroy__ = _Blob.delete_CBlobGetMoment
    __del__ = lambda self: None


CBlobGetMoment_swigregister = _Blob.CBlobGetMoment_swigregister
CBlobGetMoment_swigregister(CBlobGetMoment)


class CBlobGetHullPerimeter(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetHullPerimeter,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetHullPerimeter, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetHullPerimeter___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetHullPerimeter_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetHullPerimeter(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetHullPerimeter
    __del__ = lambda self: None


CBlobGetHullPerimeter_swigregister = _Blob.CBlobGetHullPerimeter_swigregister
CBlobGetHullPerimeter_swigregister(CBlobGetHullPerimeter)


class CBlobGetHullArea(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetHullArea,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetHullArea, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetHullArea___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetHullArea_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetHullArea(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetHullArea
    __del__ = lambda self: None


CBlobGetHullArea_swigregister = _Blob.CBlobGetHullArea_swigregister
CBlobGetHullArea_swigregister(CBlobGetHullArea)


class CBlobGetMinXatMinY(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetMinXatMinY,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetMinXatMinY, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetMinXatMinY___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetMinXatMinY_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetMinXatMinY(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetMinXatMinY
    __del__ = lambda self: None


CBlobGetMinXatMinY_swigregister = _Blob.CBlobGetMinXatMinY_swigregister
CBlobGetMinXatMinY_swigregister(CBlobGetMinXatMinY)


class CBlobGetMinYatMaxX(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetMinYatMaxX,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetMinYatMaxX, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetMinYatMaxX___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetMinYatMaxX_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetMinYatMaxX(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetMinYatMaxX
    __del__ = lambda self: None


CBlobGetMinYatMaxX_swigregister = _Blob.CBlobGetMinYatMaxX_swigregister
CBlobGetMinYatMaxX_swigregister(CBlobGetMinYatMaxX)


class CBlobGetMaxXatMaxY(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetMaxXatMaxY,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetMaxXatMaxY, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetMaxXatMaxY___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetMaxXatMaxY_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetMaxXatMaxY(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetMaxXatMaxY
    __del__ = lambda self: None


CBlobGetMaxXatMaxY_swigregister = _Blob.CBlobGetMaxXatMaxY_swigregister
CBlobGetMaxXatMaxY_swigregister(CBlobGetMaxXatMaxY)


class CBlobGetMaxYatMinX(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetMaxYatMinX,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetMaxYatMinX, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetMaxYatMinX___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetMaxYatMinX_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetMaxYatMinX(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetMaxYatMinX
    __del__ = lambda self: None


CBlobGetMaxYatMinX_swigregister = _Blob.CBlobGetMaxYatMinX_swigregister
CBlobGetMaxYatMinX_swigregister(CBlobGetMaxYatMinX)


class CBlobGetMinX(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetMinX,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetMinX, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetMinX___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetMinX_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetMinX(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetMinX
    __del__ = lambda self: None


CBlobGetMinX_swigregister = _Blob.CBlobGetMinX_swigregister
CBlobGetMinX_swigregister(CBlobGetMinX)


class CBlobGetMaxX(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetMaxX,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetMaxX, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetMaxX___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetMaxX_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetMaxX(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetMaxX
    __del__ = lambda self: None


CBlobGetMaxX_swigregister = _Blob.CBlobGetMaxX_swigregister
CBlobGetMaxX_swigregister(CBlobGetMaxX)


class CBlobGetMinY(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetMinY,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetMinY, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetMinY___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetMinY_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetMinY(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetMinY
    __del__ = lambda self: None


CBlobGetMinY_swigregister = _Blob.CBlobGetMinY_swigregister
CBlobGetMinY_swigregister(CBlobGetMinY)


class CBlobGetMaxY(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetMaxY,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetMaxY, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetMaxY___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetMaxY_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetMaxY(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetMaxY
    __del__ = lambda self: None


CBlobGetMaxY_swigregister = _Blob.CBlobGetMaxY_swigregister
CBlobGetMaxY_swigregister(CBlobGetMaxY)


class CBlobGetElongation(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetElongation,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetElongation, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetElongation___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetElongation_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetElongation(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetElongation
    __del__ = lambda self: None


CBlobGetElongation_swigregister = _Blob.CBlobGetElongation_swigregister
CBlobGetElongation_swigregister(CBlobGetElongation)


class CBlobGetRoughness(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetRoughness,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetRoughness, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetRoughness___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetRoughness_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetRoughness(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetRoughness
    __del__ = lambda self: None


CBlobGetRoughness_swigregister = _Blob.CBlobGetRoughness_swigregister
CBlobGetRoughness_swigregister(CBlobGetRoughness)


class CBlobGetDistanceFromPoint(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetDistanceFromPoint,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(
        self,
        CBlobGetDistanceFromPoint,
        name,
    )
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _Blob.new_CBlobGetDistanceFromPoint(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    def __call__(*args):
        return _Blob.CBlobGetDistanceFromPoint___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetDistanceFromPoint_GetNom(*args)

    __swig_destroy__ = _Blob.delete_CBlobGetDistanceFromPoint
    __del__ = lambda self: None


CBlobGetDistanceFromPoint_swigregister = _Blob.CBlobGetDistanceFromPoint_swigregister
CBlobGetDistanceFromPoint_swigregister(CBlobGetDistanceFromPoint)


class CBlobGetExternPerimeter(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetExternPerimeter,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetExternPerimeter, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetExternPerimeter___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetExternPerimeter_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetExternPerimeter(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetExternPerimeter
    __del__ = lambda self: None


CBlobGetExternPerimeter_swigregister = _Blob.CBlobGetExternPerimeter_swigregister
CBlobGetExternPerimeter_swigregister(CBlobGetExternPerimeter)


class CBlobGetExternPerimeterRatio(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetExternPerimeterRatio,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(
        self,
        CBlobGetExternPerimeterRatio,
        name,
    )
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetExternPerimeterRatio___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetExternPerimeterRatio_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetExternPerimeterRatio(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetExternPerimeterRatio
    __del__ = lambda self: None


CBlobGetExternPerimeterRatio_swigregister = (
    _Blob.CBlobGetExternPerimeterRatio_swigregister
)
CBlobGetExternPerimeterRatio_swigregister(CBlobGetExternPerimeterRatio)


class CBlobGetExternHullPerimeterRatio(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetExternHullPerimeterRatio,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(
        self,
        CBlobGetExternHullPerimeterRatio,
        name,
    )
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetExternHullPerimeterRatio___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetExternHullPerimeterRatio_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetExternHullPerimeterRatio(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetExternHullPerimeterRatio
    __del__ = lambda self: None


CBlobGetExternHullPerimeterRatio_swigregister = (
    _Blob.CBlobGetExternHullPerimeterRatio_swigregister
)
CBlobGetExternHullPerimeterRatio_swigregister(CBlobGetExternHullPerimeterRatio)


class CBlobGetXCenter(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetXCenter,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetXCenter, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetXCenter___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetXCenter_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetXCenter(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetXCenter
    __del__ = lambda self: None


CBlobGetXCenter_swigregister = _Blob.CBlobGetXCenter_swigregister
CBlobGetXCenter_swigregister(CBlobGetXCenter)


class CBlobGetYCenter(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetYCenter,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetYCenter, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetYCenter___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetYCenter_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetYCenter(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetYCenter
    __del__ = lambda self: None


CBlobGetYCenter_swigregister = _Blob.CBlobGetYCenter_swigregister
CBlobGetYCenter_swigregister(CBlobGetYCenter)


class CBlobGetMajorAxisLength(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetMajorAxisLength,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetMajorAxisLength, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetMajorAxisLength___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetMajorAxisLength_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetMajorAxisLength(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetMajorAxisLength
    __del__ = lambda self: None


CBlobGetMajorAxisLength_swigregister = _Blob.CBlobGetMajorAxisLength_swigregister
CBlobGetMajorAxisLength_swigregister(CBlobGetMajorAxisLength)


class CBlobGetAreaElipseRatio(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetAreaElipseRatio,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetAreaElipseRatio, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetAreaElipseRatio___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetAreaElipseRatio_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetAreaElipseRatio(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetAreaElipseRatio
    __del__ = lambda self: None


CBlobGetAreaElipseRatio_swigregister = _Blob.CBlobGetAreaElipseRatio_swigregister
CBlobGetAreaElipseRatio_swigregister(CBlobGetAreaElipseRatio)


class CBlobGetMinorAxisLength(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetMinorAxisLength,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetMinorAxisLength, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetMinorAxisLength___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetMinorAxisLength_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetMinorAxisLength(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetMinorAxisLength
    __del__ = lambda self: None


CBlobGetMinorAxisLength_swigregister = _Blob.CBlobGetMinorAxisLength_swigregister
CBlobGetMinorAxisLength_swigregister(CBlobGetMinorAxisLength)


class CBlobGetOrientation(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetOrientation,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetOrientation, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetOrientation___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetOrientation_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetOrientation(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetOrientation
    __del__ = lambda self: None


CBlobGetOrientation_swigregister = _Blob.CBlobGetOrientation_swigregister
CBlobGetOrientation_swigregister(CBlobGetOrientation)


class CBlobGetOrientationCos(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetOrientationCos,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetOrientationCos, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetOrientationCos___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetOrientationCos_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetOrientationCos(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetOrientationCos
    __del__ = lambda self: None


CBlobGetOrientationCos_swigregister = _Blob.CBlobGetOrientationCos_swigregister
CBlobGetOrientationCos_swigregister(CBlobGetOrientationCos)


class CBlobGetAxisRatio(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetAxisRatio,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetAxisRatio, name)
    __repr__ = _swig_repr

    def __call__(*args):
        return _Blob.CBlobGetAxisRatio___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetAxisRatio_GetNom(*args)

    def __init__(self, *args):
        this = _Blob.new_CBlobGetAxisRatio(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    __swig_destroy__ = _Blob.delete_CBlobGetAxisRatio
    __del__ = lambda self: None


CBlobGetAxisRatio_swigregister = _Blob.CBlobGetAxisRatio_swigregister
CBlobGetAxisRatio_swigregister(CBlobGetAxisRatio)


class CBlobGetXYInside(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self,
        CBlobGetXYInside,
        name,
        value,
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBlobGetXYInside, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _Blob.new_CBlobGetXYInside(*args)
        try:
            self.this.append(this)
        except:
            self.this = this

    def __call__(*args):
        return _Blob.CBlobGetXYInside___call__(*args)

    def GetNom(*args):
        return _Blob.CBlobGetXYInside_GetNom(*args)

    __swig_destroy__ = _Blob.delete_CBlobGetXYInside
    __del__ = lambda self: None


CBlobGetXYInside_swigregister = _Blob.CBlobGetXYInside_swigregister
CBlobGetXYInside_swigregister(CBlobGetXYInside)
