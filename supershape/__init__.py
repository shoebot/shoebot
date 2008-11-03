# SUPERSHAPE - last updated for NodeBox 1.9.4
# Author: Frederik De Bleser <frederik@pandora.be>
# Copyright (c) 2006 by Frederik De Bleser.
# See LICENSE.txt for details.

# The superformula was published by Johan Gielis,
# you may use it in NodeBox for non-commercial purposes.

from math import pi, sin, cos, pow
_range = range

TWOPI = pi * 2

try:
    
    # Attempt to import the C library
    # for faster performance.
    from cSuperformula import supercalc

except:
    
    # Else, use the native python
    # calculation of supershapes.
    def supercalc(m, n1, n2, n3, phi):
        a = 1.0
        b = 1.0
    
        t1 = cos(m * phi / 4) / a
        t1 = abs(t1)
        t1 = pow(t1, n2)
    
        t2 = sin(m * phi / 4) / b
        t2 = abs(t2)
        t2 = pow(t2, n3)
    
        r = pow(t1 + t2, 1 / n1)
        if abs(r) == 0:
            return (0,0)
        else:
            r = 1 / r
            return (r * cos(phi), r * sin(phi))

def path(x, y, w, h, m, n1, n2, n3, points=1000, percentage=1.0, range=TWOPI):
    first = True
    for i in _range(points):
        if i > points*percentage: 
            continue
        phi = i * range / points
        dx, dy = supercalc(m, n1, n2, n3, phi)
        dx = (dx * w) + x
        dy = (dy * h) + y
        if first:
            _ctx.beginpath(dx, dy)
            first = False
        else:
            _ctx.lineto(dx, dy)
    return _ctx.endpath(draw=False)
    
def transform(path, m, n1, n2, n3, points=100, range=TWOPI):
    first = True
    for i in _range(points):
        pt = path.point(float(i)/points)
        phi = i * range / points
        dx, dy = supercalc(m, n1, n2, n3, phi)
        if first:
            _ctx.beginpath(pt.x+dx, pt.y+dy)
            first = False
        else:
            _ctx.lineto(pt.x+dx, pt.y+dy)
    return _ctx.endpath(draw=False)

