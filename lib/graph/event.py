# Copyright (c) 2007 Tom De Smedt.
# See LICENSE.txt for details.

try: from en import wordnet
except:
    try: import wordnet
    except:
        pass

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

#### GRAPH HOVER/CLICK/DRAG EVENTS ###################################################################

class events:
    
    def __init__(self, graph, _ctx):
        
        self.graph = graph
        self._ctx = _ctx
        
        # Can contain a node:
        self.hovered = None
        self.pressed = None
        self.dragged = None
        self.clicked = None
        
        # Displays when hovering over a node.
        self.popup = False
        self.popup_text = {}
    
    def copy(self, graph):
    
        """ Returns a copy of the event handler, remembering the last node clicked.
        """
    
        e = events(graph, self._ctx)
        e.clicked = self.clicked
        return e
    
    def _mouse(self):
        
        return Point(
            self._ctx._ns["MOUSEX"], 
            self._ctx._ns["MOUSEY"]
        )
        
    mouse = property(_mouse)
 
    def _mousedown(self):
        
        if self._ctx._ns["mousedown"]:
            return True
        else:
            return False

    mousedown = property(_mousedown)

    def update(self):
    
        """ Interacts with the graph by clicking or dragging nodes.
        Hovering a node fires the callback function events.hover().
        Clicking a node fires the callback function events.click().
        """
    
        if self.mousedown:
        
            # When not pressing or dragging, check each node.
            if not self.pressed and not self.dragged:
                for n in self.graph.nodes:
                    if self.mouse in n:
                        self.pressed = n
                        break
                    
            # If a node is pressed, check if a drag is started.
            elif self.pressed and not self.mouse in self.pressed:
                self.dragged = self.pressed
                self.pressed = None
            
            # Drag the node (right now only for springgraphs).
            elif self.dragged and self.graph.layout.type == "spring":
                self.drag(self.dragged)
                self.graph.layout.i = min(100, max(2, self.graph.layout.n-100))
    
        # Mouse is clicked on a node, fire callback.
        elif self.pressed and self.mouse in self.pressed:
            self.clicked = self.pressed
            self.pressed = None
            self.graph.layout.i = 2
            self.click(self.clicked)
    
        # Mouse up.
        else:
            self.hovered = None
            self.pressed = None
            self.dragged = None
        
            # Hovering over a node?
            for n in self.graph.nodes:
                if self.mouse in n:
                    self.hovered = n
                    self.hover(n)
                    break
    
    def drag(self, node):

        """ Drags given node to mouse location.
        """
    
        dx = self.mouse.x - self.graph.x
        dy = self.mouse.y - self.graph.y

        # A dashed line indicates the drag vector.
        s = self.graph.styles.default
        self._ctx.nofill()
        self._ctx.nostroke()
        if s.stroke: 
            self._ctx.strokewidth(s.strokewidth)
            self._ctx.stroke(
                s.stroke.r, 
                s.stroke.g, 
                s.stroke.g, 
                0.75
            )
        p = self._ctx.line(node.x, node.y, dx, dy, draw=False)
        try: p._nsBezierPath.setLineDash_count_phase_([2,4], 2, 50)
        except:
            pass
        self._ctx.drawpath(p)
        r = node.__class__(None).r * 0.75
        self._ctx.oval(dx-r/2, dy-r/2, r, r)
    
        node.vx = dx / self.graph.d
        node.vy = dy / self.graph.d
        
    def hover(self, node):
        
        """ Displays a popup when hovering over a node.
        """
        
        if self.popup == False: return
        if self.popup == True or self.popup.node != node:
            if self.popup_text.has_key(node.id):
                texts = self.popup_text[node.id]
            else:
                texts = None
            self.popup = popup(self._ctx, node, texts)
        self.popup.draw()

    def click(self, node):
        
        pass

### POPUP ############################################################################################   

class popup:
    
    """ An information box used when hovering over a node.
    It takes a list of alternating texts to display.
    """
    
    def __init__(self, _ctx, node, texts=None, width=200, speed=2.0):
        
        if texts != None and not isinstance(texts, (tuple, list)):
            texts = [texts]
        
        self._ctx = _ctx
        self.node = node
        
        self.i = 0 
        self.q = texts

        # When no texts were supplied, fall back to WordNet.
        # If WordNet is loaded, gather gloss descriptions for the node's id.
        if self.q == None:
            self.q = []
            try:
                id = str(self.node.id)
                for i in range(wordnet.count_senses(id)):
                    txt  = id + " | " + wordnet.gloss(id, sense=i)
                    self.q.append(txt)
            except:
                pass
    
        # Defaults for colors and typography.
        self.background = self._ctx.color(0.00, 0.10, 0.15, 0.60)
        self.text       = self._ctx.color(1.00, 1.00, 1.00, 0.80)
        self.font       = "Verdana"
        self.fontsize   = 9.5

        # Cached outlined versions of the text.
        self._textpaths = []
        self._w = width
        
        self.speed = speed
        self.delay = 20 / self.speed

        self.fi = 0  # current frame
        self.fn = 0  # frame count
        self.mf = 50 # minimum frame count

    def textpath(self, i):
        
        """ Returns a cached textpath of the given text in queue.
        """
        
        if len(self._textpaths) == i:
            self._ctx.font(self.font, self.fontsize)
            txt = self.q[i]
            if len(self.q) > 1:
                # Indicate current text (e.g. 5/13).
                txt += " ("+str(i+1)+"/" + str(len(self.q))+")"
            p = self._ctx.textpath(txt, 0, 0, width=self._w)
            h = self._ctx.textheight(txt, width=self._w)
            self._textpaths.append((p, h))

        return self._textpaths[i]
        
    def update(self):
        
        """ Rotates the queued texts and determines display time.
        """
        
        if self.delay > 0:
            # It takes a while for the popup to appear.
            self.delay -= 1; return
            
        if self.fi == 0:
            # Only one text in queue, displayed infinitely.
            if len(self.q) == 1: 
                self.fn = float("inf")
            # Else, display time depends on text length.
            else:
                self.fn = len(self.q[self.i]) / self.speed
                self.fn = max(self.fn, self.mf)            
            
        self.fi += 1
        if self.fi > self.fn:
            # Rotate to the next text in queue.
            self.fi = 0
            self.i = (self.i+1) % len(self.q)
        
    def draw(self):
        
        """ Draws a popup rectangle with a rotating text queue.        
        """ 
        
        if len(self.q) > 0:
            self.update()
            
            if self.delay == 0:
                
                # Rounded rectangle in the given background color.
                p, h = self.textpath(self.i)
                f = self.fontsize
                self._ctx.fill(self.background)
                self._ctx.rect(
                    self.node.x + f*1.0, 
                    self.node.y + f*0.5, 
                    self._w + f, 
                    h + f*1.5, 
                    roundness=0.2
                )
                
                # Fade in/out the current text.
                alpha = 1.0
                if self.fi < 5: 
                    alpha = 0.2 * self.fi
                if self.fn-self.fi < 5: 
                    alpha = 0.2 * (self.fn-self.fi)
                self._ctx.fill(
                    self.text.r,
                    self.text.g,
                    self.text.b,
                    self.text.a * alpha
                )
                
                self._ctx.translate(self.node.x + f*2.0, self.node.y + f*2.5)
                self._ctx.drawpath(p)