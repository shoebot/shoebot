### CREDITS ##########################################################################################

# Copyright (c) 2007-2009 Tom De Smedt.
# See LICENSE.txt for details.
# See also the SVG DOM specification: http://www.w3.org/TR/SVG/

__author__    = "Tom De Smedt"
__version__   = "1.9.4.5"
__copyright__ = "Copyright (c) 2007-2009 Tom De Smedt"
__license__   = "GPL"

from . import arc
import xml.dom.minidom as parser
import re
from hashlib import md5
from shoebot.data import RGB, MOVETO

#### CACHE ###########################################################################################

class cache(dict):

    """Caches BezierPaths from parsed SVG data."""

    def id(self, svg):
        hash = md5.new()
        hash.update(str(_ctx)+svg)
        return hash.digest()

    def save(self, id, paths):
        self[id] = paths

    def load(self, id, copy=True):
        if id in self:
            if copy:
                return [self.copypath(path) for path in self[id]]
            return self[id]

    def copypath(self, path):
        # Expand the path copy with the properties from add_color_info()
        p = path.copy()
        p.fill = path.fill
        p.stroke = path.stroke
        p.strokewidth = path.strokewidth
        p.closed = path.closed
        p.id = path.id
        return p

    def clear(self):
        for k in list(self.keys()): del self[k]

_cache = cache()

#### SVG PARSER ######################################################################################

def parse(svg, cached=False, _copy=True):
    """Returns cached copies unless otherwise specified."""

    if not cached:
        dom = parser.parseString(svg)
        paths = parse_node(dom, [])
    else:
        id = _cache.id(svg)
        if id not in _cache:
            dom = parser.parseString(svg)
            _cache.save(id, parse_node(dom, []))
        paths = _cache.load(id, _copy)

    return paths

def parse_as_dict(svg, cached=False, _copy=True):
    paths_dict = {}
    noid = 0
    paths = parse(svg)
    for p in paths:
        if p.id:
            paths_dict[p.id] = p
        else:
            noid += 1
            paths_dict["no_id_"+str(noid)] = p
    return paths_dict

def get_attribute(element, attribute, default=0):
    """Returns XML element's attribute, or default if none."""

    a = element.getAttribute(attribute)
    if a == "":
        return default
    return a

#--- XML NODE ----------------------------------------------------------------------------------------

def parse_node(node, paths=[], ignore=["pattern"]):
    """Recurse the node tree and find drawable tags.

    Recures all the children in the node. If a child is something we can
    draw, a line, rect, oval or path, parse it to a PathElement drawable
    with drawpath()
    """

    # Ignore paths in Illustrator pattern swatches etc.
    if node.nodeType == node.ELEMENT_NODE and node.tagName in ignore:
        return []

    if node.hasChildNodes():
        for child in node.childNodes:
            paths = parse_node(child, paths)

    if node.nodeType == node.ELEMENT_NODE:

        if node.tagName == "line":
            paths.append(parse_line(node))
        elif node.tagName == "rect":
            paths.append(parse_rect(node))
        elif node.tagName == "circle":
            paths.append(parse_circle(node))
        elif node.tagName == "ellipse":
            paths.append(parse_oval(node))
        elif node.tagName == "polygon":
            paths.append(parse_polygon(node))
        elif node.tagName == "polyline":
            paths.append(parse_polygon(node))
        elif node.tagName == "path":
            paths.append(parse_path(node))

        if node.tagName in ("line", "rect", "circle", "ellipse", "polygon", "polyline", "path"):
            paths[-1] = parse_transform(node, paths[-1])
            paths[-1] = add_color_info(node, paths[-1])

    return paths

#--- LINE --------------------------------------------------------------------------------------------

def parse_line(e):
    x1 = float(get_attribute(e, "x1"))
    y1 = float(get_attribute(e, "y1"))
    x2 = float(get_attribute(e, "x2"))
    y2 = float(get_attribute(e, "y2"))
    p = _ctx.line(x1, y1, x2, y2, draw=False)
    return p

#--- RECT --------------------------------------------------------------------------------------------

def parse_rect(e):
    x = float(get_attribute(e, "x"))
    y = float(get_attribute(e, "y"))
    w = float(get_attribute(e, "width"))
    h = float(get_attribute(e, "height"))
    p = _ctx.rect(x, y, w, h, draw=False)
    return p

#--- CIRCLE -----------------------------------------------------------------------------------------

def parse_circle(e):
    x = float(get_attribute(e, "cx"))
    y = float(get_attribute(e, "cy"))
    r = float(get_attribute(e, "r"))
    p = _ctx.oval(x-r, y-r, r*2, r*2, draw=False)
    return p

#--- OVAL -------------------------------------------------------------------------------------------

def parse_oval(e):
    x = float(get_attribute(e, "cx"))
    y = float(get_attribute(e, "cy"))
    w = float(get_attribute(e, "rx"))*2
    h = float(get_attribute(e, "ry"))*2
    p = _ctx.oval(x-w/2, y-h/2, w, h, draw=False)
    return p

#--- POLYGON -----------------------------------------------------------------------------------------

def parse_polygon(e):
    d = get_attribute(e, "points", default="")
    d = d.replace(" ", ",")
    d = d.replace("-", ",")
    d = d.split(",")
    points = []
    for x in d:
        if x != "": points.append(float(x))

    _ctx.autoclosepath()
    if (e.tagName == "polyline") :
        _ctx.autoclosepath(False)

    _ctx.beginpath(points[0], points[1])
    for i in range(len(points)/2):
        _ctx.lineto(points[i*2], points[i*2+1])
    p = _ctx.endpath(draw=False)
    return p

#--- PATH --------------------------------------------------------------------------------------------

def parse_path(e):
    d = get_attribute(e, "d", default="")

    # Divide the path data string into segments.
    # Each segment starts with a path command,
    # usually followed by coordinates.
    segments = []
    i = 0
    for j in range(len(d)):
        commands = ["M", "m", "Z", "z", "L", "l", "H", "h", "V", "v", "C","c", "S", "s", "A"]
        if d[j] in commands:
            segments.append(d[i:j].strip())
            i = j
    segments.append(d[i:].strip())
    segments.remove("")

    previous_command = ""

    # Path origin (moved by MOVETO).
    x0 = 0
    y0 = 0

    # The current point in the path.
    dx = 0
    dy = 0

    # The previous second control handle.
    dhx = 0
    dhy = 0

    _ctx.autoclosepath(False)
    _ctx.beginpath(0,0)
    for segment in segments:

        command = segment[0]

        if command in ["Z", "z"]:
            _ctx.closepath()
        else:
            # The command is a pen move, line or curve.
            # Get the coordinates.
            points = segment[1:].strip()
            points = points.replace("-", ",-")
            points = points.replace(" ", ",")
            points = re.sub(",+", ",", points)
            points = points.strip(",")
            points = [float(i) for i in points.split(",")]

        # Absolute MOVETO.
        # Move the current point to the new coordinates.
        if command == "M":
            for i in range(int(len(points)/2)):
                # More than one value is an implicit LINETO
                # see https://www.w3.org/TR/SVG/paths.html#PathDataMovetoCommands
                if i == 0:
                    _ctx.moveto(points[i*2], points[i*2+1])
                else:
                    _ctx.lineto(points[i*2], points[i*2+1])
                dx = points[i*2]
                dy = points[i*2+1]
                x0 = dx
                y0 = dy

        # Relative MOVETO.
        # Offset from the current point.
        elif command == "m":
            for i in range(int(len(points)/2)):
                # More than one value is an implicit LINETO
                # see https://www.w3.org/TR/SVG/paths.html#PathDataMovetoCommands
                if i == 0:
                    _ctx.moveto(dx+points[i*2], dy+points[i*2+1])
                else:
                    _ctx.lineto(dx+points[i*2], dy+points[i*2+1])
                dx += points[i*2]
                dy += points[i*2+1]
                x0 = dx
                y0 = dy

        # Absolute LINETO.
        # Draw a line from the current point to the new coordinate.
        elif command == "L":
            for i in range(int(len(points)/2)):
                _ctx.lineto(points[i*2], points[i*2+1])
                dx = points[i*2]
                dy = points[i*2+1]

        # Relative LINETO.
        # Offset from the current point.
        elif command == "l":
            for i in range(int(len(points)/2)):
                _ctx.lineto(dx+points[i*2], dy+points[i*2+1])
                dx += points[i*2]
                dy += points[i*2+1]

        # Absolute horizontal LINETO.
        # Only the vertical coordinate is supplied.
        elif command == "H":
            _ctx.lineto(points[0], dy)
            dx = points[0]

        # Relative horizontal LINETO.
        # Offset from the current point.
        elif command == "h":
            _ctx.lineto(dx+points[0], dy)
            dx += points[0]

        # Absolute vertical LINETO.
        # Only the horizontal coordinate is supplied.
        if command == "V":
            _ctx.lineto(dx, points[0])
            dy = points[0]

        # Relative vertical LINETO.
        # Offset from the current point.
        elif command == "v":
            _ctx.lineto(dx, dy+points[0])
            dy += points[0]

        # Absolute CURVETO.
        # Draw a bezier with given control handles and destination.
        elif command == "C":
            for i in range(int(len(points)/6)):
                _ctx.curveto(points[i*6],   points[i*6+1],
                             points[i*6+2], points[i*6+3],
                             points[i*6+4], points[i*6+5])
                dhx = points[i*6+2]
                dhy = points[i*6+3]
                dx = points[i*6+4]
                dy = points[i*6+5]

        # Relative CURVETO.
        # Offset from the current point.
        elif command == "c":
            for i in range(int(len(points)/6)):
                _ctx.curveto(dx+points[i*6],   dy+points[i*6+1],
                             dx+points[i*6+2], dy+points[i*6+3],
                             dx+points[i*6+4], dy+points[i*6+5])
                dhx = dx+points[i*6+2]
                dhy = dy+points[i*6+3]
                dx += points[i*6+4]
                dy += points[i*6+5]

        # Absolute reflexive CURVETO.
        # Only the second control handle is given,
        # the first is the reflexion of the previous handle.
        elif command == "S":
            for i in range(int(len(points)/4)):
                if previous_command not in ["C", "c", "S", "s"]:
                    dhx = dx
                    dhy = dy
                else:
                    dhx = dx-dhx
                    dhy = dy-dhy
                _ctx.curveto(dx+dhx, dy+dhy,
                             points[i*4],   points[i*4+1],
                             points[i*4+2], points[i*4+3])
                dhx = points[i*4]
                dhy = points[i*4+1]
                dx = points[i*4+2]
                dy = points[i*4+3]

        # Relative reflexive CURVETO.
        # Offset from the current point.
        elif command == "s":
            for i in range(int(len(points)/4)):
                if previous_command not in ["C", "c", "S", "s"]:
                    dhx = dx
                    dhy = dy
                else:
                    dhx = dx-dhx
                    dhy = dy-dhy
                _ctx.curveto(dx+dhx, dy+dhy,
                             dx+points[i*4],   dy+points[i*4+1],
                             dx+points[i*4+2], dy+points[i*4+3])
                dhx = dx+points[i*4]
                dhy = dy+points[i*4+1]
                dx += points[i*4+2]
                dy += points[i*4+3]

        # Absolute elliptical arc.
        elif command == "A":
            for i in range(int(len(points)/7)):
                rx, ry, phi, large_arc_flag, sweep_flag, x2, y2 = points[i*7:i*7+7]
                for p in arc.elliptical_arc_to(dx, dy, rx, ry, phi, large_arc_flag, sweep_flag, x2, y2):
                    if len(p) == 2:
                        _ctx.lineto(*p)
                    elif len(p) == 6:
                        _ctx.curveto(*p)
                dx = p[-2]
                dy = p[-1]

        previous_command = command

    p = _ctx.endpath(draw=False)
    return p

#--- PATH TRANSFORM ----------------------------------------------------------------------------------

def parse_transform(e, path):
    """Transform the path according to a defined matrix.

    Attempts to extract a transform="matrix()|translate()" attribute.
    Transforms the path accordingly.
    """

    t = get_attribute(e, "transform", default="")

    for mode in ("matrix", "translate"):
        if t.startswith(mode):
            v = t.replace(mode, "").lstrip("(").rstrip(")")
            v = v.replace(", ", ",").replace(" ", ",")
            v = [float(x) for x in v.split(",")]
            from nodebox.graphics import Transform
            t = Transform()
            if mode == "matrix":
                t.set_matrix(v)
            elif mode == "translate":
                t.translate(*v)
            path = t.transformBezierPath(path)
            break

    # Transformations can also be defined as <g transform="matrix()"><path /><g>
    # instead of <g><path transform="matrix() /></g>.
    e = e.parentNode
    if e and e.tagName == "g":
        path = parse_transform(e, path)

    return path

#--- PATH COLOR INFORMATION --------------------------------------------------------------------------

def add_color_info(e, path):
    """Expand the path with color information.

    Attempts to extract fill and stroke colors from the element and adds
    it to path attributes.
    """

    _ctx.colormode(RGB, 1.0)

    def _color(hex, alpha=1.0):
        if hex == "none": return None
        n = int(hex[1:],16)
        r = (n>>16)&0xff
        g = (n>>8)&0xff
        b = n&0xff
        return _ctx.color(r/255.0, g/255.0, b/255.0, alpha)

    path.fill = (0,0,0,0)
    path.stroke = (0,0,0,0)
    path.strokewidth = 0

    # See if we can find an opacity attribute,
    # which is the color's alpha.
    alpha = get_attribute(e, "opacity", default="")
    if alpha == "":
        alpha = 1.0
    else:
        alpha = float(alpha)

    # Colors stored as fill="" or stroke="" attributes.
    try: path.fill = _color(get_attribute(e, "fill", default="#00000"), alpha)
    except:
        pass
    try: path.stroke = _color(get_attribute(e, "stroke", default="none"), alpha)
    except:
        pass
    try: path.strokewidth = float(get_attribute(e, "stroke-width", default="1"))
    except:
        pass

    # Colors stored as a CSS style attribute, for example:
    # style="fill:#ff6600;stroke:#ffe600;stroke-width:0.06742057"
    style = get_attribute(e, "style", default="").split(";")
    for s in style:
        try:
            if s.startswith("fill:"):
                path.fill = _color(s.replace("fill:", ""))
            elif s.startswith("stroke:"):
                path.stroke = _color(s.replace("stroke:", ""))
            elif s.startswith("stroke-width:"):
                path.strokewidth = float(s.replace("stroke-width:", ""))
        except:
            pass

    # A path with beginning and ending coordinate
    # at the same location is considered closed.
    # Unless it contains a MOVETO somewhere in the middle.
    path.closed = False
    if path[0].x == path[len(path)-1].x and \
       path[0].y == path[len(path)-1].y:
        path.closed = True
    for i in range(1,-1):
        if path[i].cmd == MOVETO:
            path.closed = False

    return path

#-----------------------------------------------------------------------------------------------------
# 1.9.4.5
# Added default fill color and strokewidth.

# 1.9.4.4
# Added absolute elliptical arc.
# transform attributes on a <g> node are processed.
# transform attributes on shapes other than path are processed.
# transform="translate()" is processed.

# 1.9.4.3
# Ignore Illustrator pattern swatches.

# 1.9.4.2
# get_attribute() returns a default value for missing XML element attributes instead of "".

# 1.9.4.1
# Added the missing parse_circle().
