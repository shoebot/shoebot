from math import atan2
from math import cos
from math import degrees
from math import hypot
from math import radians
from math import sin


def distance(x1, y1, x2, y2):
    return hypot(x2 - x1, y2 - y1)


def angle(x0, y0, x1, y1):
    # from nodebox1
    a = degrees(atan2(y1 - y0, x1 - x0))
    return a


def coordinates(x0, y0, distance, angle):
    # from nodebox1
    x1 = x0 + cos(radians(angle)) * distance
    y1 = y0 + sin(radians(angle)) * distance
    return x1, y1


def reflect(x0, y0, x1, y1, d=1.0, a=180):
    # from nodebox1
    d *= distance(x0, y0, x1, y1)
    a += angle(x0, y0, x1, y1)
    x, y = coordinates(x0, y0, d, a)
    return x, y
