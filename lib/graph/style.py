# Copyright (c) 2007 Tom De Smedt.
# See LICENSE.txt for details.

from math import degrees, sqrt, atan2
from math import radians, sin, cos

CORNER = "corner"
CENTER = "center"

DEFAULT   = "default"
HIGHLIGHT = "highlight"  # used to mark shortest paths in pink
ROOT      = "root"       # used for the root node, big pink text
LIGHT     = "light"      # slightly important nodes (these are a bit darker)
DARK      = "dark"       # very important nodes (these are blue)
BACK      = "back"       # used as "back-button", green with a curved edge
IMPORTANT = "important"  # like dark, but with a double stroke
MARKED    = "marked"     # has a white dot inside the node

#### GRAPH STYLES ####################################################################################

class styles(dict):
    
    def __init__(self, graph):
        self.guide = styleguide(graph)
    
    def apply(self):
        self.guide.apply()
    
    def create(self, stylename, **kwargs):
        """ Creates a new style which inherits from the default style,
        or any other style which name is supplied to the optional template parameter.
        """
        if stylename == "default":    
            self[stylename] = style(stylename, self._ctx, **kwargs)
            return self[stylename]
        k = kwargs.get("template", "default")
        s = self[stylename] = self[k].copy(stylename)
        for attr in kwargs:
            if s.__dict__.has_key(attr):
                s.__dict__[attr] = kwargs[attr]
        return s
    
    def append(self, style):
        self[style.name] = style
    
    def __getattr__(self, a):
        """ Keys in the dictionaries are accessible as attributes.
        """
        if self.has_key(a): 
            return self[a]
        raise AttributeError, "'styles' object has no attribute '"+a+"'"
        
    def __setattr__(self, a, v):
        """ Setting an attribute is like setting it in all of the contained styles.
        """
        if a == "guide":
            self.__dict__["guide"] = v
        elif len(self) > 0 and self.values()[0].__dict__.has_key(a):
            for style in self.values(): 
                style.__dict__[a] = v
        else:
            raise AttributeError, "'style' object has no attribute '"+a+"'"
            
    def copy(self, graph):
        """ Returns a copy of all styles and a copy of the styleguide.
        """
        s = styles(graph)
        s.guide = self.guide.copy(graph)
        dict.__init__(s, [(v.name, v.copy()) for v in self.values()])
        return s

#### GRAPH STYLE GUIDE ###############################################################################
# Each node gets the default colors, type and drawing functions.
# The guide defines how and when to apply other styles based on node properties.
# It contains a set of style name keys linked to x(graph, node) functions.
# If such a function returns True for a node, the style is applied to that node.

class styleguide(dict):
    
    def __init__(self, graph):
        self.graph = graph
        self.order = []
    
    def append(self, stylename, function):
        """ The name of a style and a function that takes a graph and a node.
        It returns True when the style should be applied to the given node.
        """
        self[stylename] = function
    
    def clear(self):
        self.order = []
        dict.__init__(self)
    
    def apply(self):
        """ Check the rules for each node in the graph and apply the style.
        """
        sorted = self.order + self.keys()
        unique = []; [unique.append(x) for x in sorted if x not in unique]
        for node in self.graph.nodes:
            for s in unique:
                if self.has_key(s) and self[s](self.graph, node): 
                    node.style = s

    def copy(self, graph):
        """ Returns a copy of the styleguide for the given graph.
        """
        g = styleguide(graph)
        g.order = self.order
        dict.__init__(g, [(k, v) for k, v in self.iteritems()])
        return g

#### GRAPH STYLE #####################################################################################

class style:
    
    def __init__(self, name, _ctx, **kwargs):
        
        """ Graph styling. 
        The default style is used for edges.
        When text is set to None, no id label is displayed.
        """

        self.name = name
        self._ctx = _ctx
        if not _ctx: 
            return
        
        # Defaults for colors and typography.
        #self.background  = _ctx.color(0.18, 0.23, 0.28, 1.00)
	self.background  = _ctx.color(0.45, 0.45, 0.5, 1.00)
        self.traffic     = _ctx.color(0.00, 0.00, 0.00, 0.07)
        self.fill        = _ctx.color(0.00, 0.00, 0.00, 0.10)
        self.stroke      = _ctx.color(0.80, 0.80, 0.80, 0.75)
        self.strokewidth = 0.5
        self.text        = _ctx.color(1.00, 1.00, 1.00, 0.85)
        self.font        = "Calibri"
        self.fontsize    = 10
        self.textwidth   = 100
        self.align       = 1
        self.depth       = True
            
        # The actual drawing methods are just a bunch of monkey patches,
        # so another function can easily be assigned.
        # Call style.draw_method(style, params) instead of style.draw_method(params).
        self.graph_background = graph_background
        self.graph_traffic    = graph_traffic
        self.node             = node
        self.node_label       = node_label
        self.edges            = edges
        self.edge             = edge
        self.edge_arrow       = edge_arrow
        self.edge_label       = edge_label
        self.path             = path
        
        # Each of the attributes is an optional named parameter in __init__().
        for attr in kwargs:
            if self.__dict__.has_key(attr):
                self.__dict__[attr] = kwargs[attr]

        # Use the Colors library for gradients and shadows?
        if self.depth:
            try: 
                global colors
                colors = _ctx.ximport("colors")
            except:
                self.depth = False

    def copy(self, name=None):
        
        # Copy all attributes, link all monkey patch methods.
        s = style(self.name, self._ctx)
        for attr in self.__dict__: 
            v = self.__dict__[attr]
            if isinstance(v, self.fill.__class__): v = v.copy()
            s.__dict__[attr] = v
        if name != None: 
            s.name = name
        
        return s

#--- GRAPH BACKGROUND --------------------------------------------------------------------------------

def graph_background(s):

    """ Graph background color.
    """

    if s.background == None:
        s._ctx.background(None)
    else:
        s._ctx.background(s.background)  

    if s.depth:
        try:
            clr = colors.color(s.background).darker(0.2)
            p = s._ctx.rect(0, 0, s._ctx.WIDTH, s._ctx.HEIGHT, draw=False)
            colors.gradientfill(p, clr, clr.lighter(0.35))
            colors.shadow(dx=0, dy=0, blur=2, alpha=0.935, clr=s.background)
        except:
            pass

#--- GRAPH TRAFFIC -----------------------------------------------------------------------------------

def graph_traffic(s, node, alpha=1.0):
    
    """ Visualization of traffic-intensive nodes (based on their centrality).
    """
    
    r = node.__class__(None).r
    r += (node.weight+0.5) * r * 5
    s._ctx.nostroke()
    if s.traffic:
        s._ctx.fill(
            s.traffic.r, 
            s.traffic.g, 
            s.traffic.b, 
            s.traffic.a * alpha
        )
        s._ctx.oval(node.x-r, node.y-r, r*2, r*2)      

#--- NODE --------------------------------------------------------------------------------------------

def node(s, node, alpha=1.0):

    """ Visualization of a default node.
    """

    if s.depth:
        try: colors.shadow(dx=5, dy=5, blur=10, alpha=0.5*alpha)
        except: pass
    
    s._ctx.nofill()
    s._ctx.nostroke()
    if s.fill:
        s._ctx.fill(
            s.fill.r, 
            s.fill.g, 
            s.fill.b, 
            s.fill.a * alpha
        )
    if s.stroke: 
        s._ctx.strokewidth(s.strokewidth)
        s._ctx.stroke(
            s.stroke.r, 
            s.stroke.g, 
            s.stroke.b, 
            s.stroke.a * alpha * 3
        )
    r = node.r
    s._ctx.oval(node.x-r, node.y-r, r*2, r*2)        

#--- NODE LABEL -------------------------------------------------------------------------------------

def node_label(s, node, alpha=1.0):

    """ Visualization of a node's id.
    """

    if s.text:
        #s._ctx.lineheight(1)    
        s._ctx.font(s.font)
        s._ctx.fontsize(s.fontsize)
        s._ctx.nostroke()
        s._ctx.fill(
            s.text.r, 
            s.text.g, 
            s.text.b, 
            s.text.a * alpha
        )

        # Cache an outlined label text and translate it.
        # This enhances the speed and avoids wiggling text.
        try: p = node._textpath
        except: 
            txt = node.label
            try: txt = unicode(txt)
            except:
                try: txt = txt.decode("utf-8")
                except:
                    pass
            # Abbreviation.
            #root = node.graph.root
            #if txt != root and txt[-len(root):] == root: 
            #    txt = txt[:len(txt)-len(root)]+root[0]+"."
            dx, dy = 0, 0
            if s.align == 2: #CENTER
                dx = -s._ctx.textwidth(txt, s.textwidth) / 2
                dy =  s._ctx.textheight(txt) / 2
            node._textpath = s._ctx.textpath(txt, dx, dy, width=s.textwidth)
            p = node._textpath
        
        if s.depth:
            try: __colors.shadow(dx=2, dy=4, blur=5, alpha=0.3*alpha)
            except: pass
        
        s._ctx.push()
        s._ctx.translate(node.x, node.y)
        s._ctx.scale(alpha)
        s._ctx.drawpath(p.copy())
        s._ctx.pop()

#--- EDGES -------------------------------------------------------------------------------------------

def edges(s, edges, alpha=1.0, weighted=False, directed=False):
    
    """ Visualization of the edges in a network.
    """
    
    p = s._ctx.BezierPath()
    
    if directed and s.stroke: 
        pd = s._ctx.BezierPath()           
    if weighted and s.fill: 
        pw = [s._ctx.BezierPath() for i in range(11)]
    
    # Draw the edges in a single BezierPath for speed.
    # Weighted edges are divided into ten BezierPaths,
    # depending on their weight rounded between 0 and 10.
    if len(edges) == 0: return
    for e in edges:
        try:  s2 = e.node1.graph.styles[e.node1.style]
        except: s2 = s
        if s2.edge:
            s2.edge(s2, p, e, alpha)
            if directed and s.stroke:
                s2.edge_arrow(s2, pd, e, radius=10)
            if weighted and s.fill:
                s2.edge(s2, pw[int(e.weight*10)], e, alpha)                

    s._ctx.autoclosepath(False)
    s._ctx.nofill()
    s._ctx.nostroke()

    

    # All weighted edges use the default fill.
    if weighted and s.fill:
        r = e.node1.__class__(None).r
        s._ctx.stroke(
            s.fill.r,
            s.fill.g,
            s.fill.b,
            s.fill.a * 0.65 * alpha
        )
        for w in range(1, len(pw)):
            s._ctx.strokewidth(r*w*0.1)
            s._ctx.drawpath(pw[w].copy())        

    # All edges use the default stroke.
    if s.stroke: 
        s._ctx.strokewidth(s.strokewidth)
	
        s._ctx.stroke(
            s.stroke.r, 
            s.stroke.g, 
            s.stroke.b, 
            s.stroke.a * 0.65 * alpha
        )
    
    s._ctx.drawpath(p.copy())
    
    if directed and s.stroke:
        #clr = s._ctx.stroke().copy()
	clr=s._ctx.color(
            s.stroke.r, 
            s.stroke.g, 
            s.stroke.b, 
            s.stroke.a * 0.65 * alpha
        )
		
        clr.a *= 1.3
        
	s._ctx.stroke(clr)
        
    	s._ctx.drawpath(pd.copy())
    
    for e in edges:
        try:  s2 = self.styles[e.node1.style]
        except: s2 = s
        if s2.edge_label:
            s2.edge_label(s2, e, alpha)

#--- EDGE --------------------------------------------------------------------------------------------

def edge(s, path, edge, alpha=1.0):
    
    """ Visualization of a single edge between two nodes.
    """
    
    path.moveto(edge.node1.x, edge.node1.y)
    if edge.node2.style == BACK:
        path.curveto(
            edge.node1.x,
            edge.node2.y,
            edge.node2.x,
            edge.node2.y,
            edge.node2.x,
            edge.node2.y,
        )        
    else:
        path.lineto(
            edge.node2.x, 
            edge.node2.y
        )

#--- EDGE ARROW --------------------------------------------------------------------------------------

def edge_arrow(s, path, edge, radius):

    if edge.node2.style == BACK: return

    x0, y0 = edge.node1.x, edge.node1.y
    x1, y1 = edge.node2.x, edge.node2.y

    coordinates = lambda x, y, d, a: (x+cos(radians(a))*d, y+sin(radians(a))*d)

    # Find the edge's angle based on node1 and node2 position.
    a = degrees(atan2(y1-y0, x1-x0))
    
    # The arrow points to node2's rim instead of it's center.
    r = edge.node2.r
    d = sqrt(pow(x1-x0, 2) + pow(y1-y0, 2))
    x01, y01 = coordinates(x0, y0, d-r-1, a)
    
    # Find the two other arrow corners under the given angle.
    r = edge.node1.r
    r = radius
    dx1, dy1 = coordinates(x01, y01, -r, a-20)
    dx2, dy2 = coordinates(x01, y01, -r, a+20)
    
    path.moveto(x01, y01)
    path.lineto(dx1, dy1)
    path.lineto(dx2, dy2)
    path.lineto(x01, y01)
    path.moveto(x1, y1)

#--- EDGE LABEL --------------------------------------------------------------------------------------

def edge_label(s, edge, alpha=1.0):

    """ Visualization of the label accompanying an edge.
    """

    if s.text and edge.label != "":       
        s._ctx.nostroke()
        s._ctx.fill(
            s.text.r, 
            s.text.g, 
            s.text.b, 
            s.text.a * alpha*0.75
        )
        s._ctx.lineheight(1)    
        s._ctx.font(s.font)
        s._ctx.fontsize(s.fontsize*0.75)
        
        # Cache an outlined label text and translate it.
        # This enhances the speed and avoids wiggling text.
        try: p = edge._textpath
        except:
            try: txt = unicode(edge.label)
            except:
                try: txt = edge.label.decode("utf-8")
                except:
                    pass
            edge._textpath = s._ctx.textpath(txt, s._ctx.textwidth(" "), 0, width=s.textwidth)
            p = edge._textpath
        
        # Position the label centrally along the edge line.
        a  = degrees( atan2(edge.node2.y-edge.node1.y, edge.node2.x-edge.node1.x) )
        d  = sqrt((edge.node2.x-edge.node1.x)**2 +(edge.node2.y-edge.node1.y)**2)
        d  = abs(d-s._ctx.textwidth(edge.label)) * 0.5
        
        s._ctx.push()
        s._ctx.transform(CORNER)
        s._ctx.translate(edge.node1.x, edge.node1.y)
        s._ctx.rotate(-a)
        s._ctx.translate(d, s.fontsize*1.0)
        s._ctx.scale(alpha)
        
        # Flip labels on the left hand side so they are legible.
        if 90 < a%360 < 270:
            s._ctx.translate(s._ctx.textwidth(edge.label), -s.fontsize*2.0)
            s._ctx.transform(CENTER)
            s._ctx.rotate(180)
            s._ctx.transform(CORNER)
        
        s._ctx.drawpath(p.copy())
        s._ctx.pop()        

#---- PATH -------------------------------------------------------------------------------------------

def path(s, graph, path):

    """ Visualization of a shortest path between two nodes.
    """

    def end(n):
        r = n.r * 0.35
        s._ctx.oval(n.x-r, n.y-r, r*2, r*2)

    if path and len(path) > 1 and s.stroke:

        s._ctx.nofill()
        s._ctx.stroke(
            s.stroke.r,
            s.stroke.g,
            s.stroke.b,
            s.stroke.a
        )
        if s.name != DEFAULT:
            s._ctx.strokewidth(s.strokewidth)
        else:
            s._ctx.strokewidth(s.strokewidth*2)
            
        first = True
        for id in path:
            n = graph[id]
            if first:
                first = False
                s._ctx.beginpath(n.x, n.y)
                end(n)
            else:
                s._ctx.lineto(n.x, n.y)
        s._ctx.endpath()
        end(n)
