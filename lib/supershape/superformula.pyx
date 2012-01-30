import cython

from libc.math cimport sin, cos, pow, abs

# Else, use the native python
# calculation of supershapes.

@cython.cdivision(True)    # turn division by zero checking off
def supercalc(double m, double n1, double n2, double n3, double phi):
    cdef double a = 1.0
    cdef double b = 1.0

    cdef double t1 = cos(m * phi / 4) / a
    t1 = abs(t1)
    t1 = pow(t1, n2)

    cdef double t2 = sin(m * phi / 4) / b
    t2 = abs(t2)
    if t2 != 0:
        t2 = pow(t2, n3)

    cdef double r = pow(t1 + t2, 1 / n1)
    if abs(r) == 0:
        return (0,0)
    else:
        r = 1 / r
        return (r * cos(phi), r * sin(phi))
