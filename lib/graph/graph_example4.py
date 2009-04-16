# A graph that browses through the WordNet dictionary.
# You can click on nodes (including "has-parts" and "has-specific").
# You'll need the NodeBox Linguistics library installed.
# Author: Tom De Smedt.

query = "bird"

try:
    graph = ximport("graph")
except ImportError:
    graph = ximport("__init__")
    reload(graph)

import en
from random import shuffle

#### WORDNET GRAPH ###################################################################################

class wordnetgraph(graph.graph):
    
    """ Browse WordNet in a graph.
    
    The wordnetgraph class is based on the standard graph class.
    I've added some functionality to fetch data from WordNet and browse through it.
    When you click on a node, the wordnetgraph.click() method is fired.
    This will check if the clicked node is a noun in WordNet, and if so,
    reload the graph's nodes and connections with that noun at the root.
    
    The main methods, get_senses() and get_relations(),
    are called when the graph reloads.
    They retrieve data from WordNet and format it as nodes.
    The expand() method is called when you click on "has-specific" or "has-parts".
    
    A helper class, senses, draws the interactive word sense selection buttons.
    
    """
    
    def __init__(self, iterations=2000, distance=1.3):
        
        graph.graph.__init__(self, iterations, distance)
        self.styles = graph.create().styles
        self.events.click = self.click
        self.events.popup = True
        
        # Display a maximum of 20 nodes.
        self.max = 20
        
        # A row of buttons to select the current word sense.
        self.senses = senses(self, 20, 20)
    
    def is_expandable(self, id):
        
        """ Some of the branches are expandable:
        if you click on has-parts or has-specific, a detailed view will load.
        """
        
        if id in ["has-parts", "has-specific"]: 
            return True
        else:
            return False
    
    def is_clickable(self, node):
        
        """ Every node that is a noun is clickable (except the root).
        """
        
        if en.is_noun(str(node.id.lower())) \
        or self.is_expandable(node.id) and node != self.root: 
            return True
        else:
            return False
    
    def get_senses(self, word, top=6):
 
        """ The graph displays the different senses of a noun,
        e.g. light -> lighter, luminosity, sparkle, ...
        """
        
        word = str(word)
        
        if self.is_expandable(word): return []
        
        # If there are 4 word senses and each of it a list of words,
        # take the first word from each list, then take the second etc.
        words = []
        for i in range(2):
            for sense in en.noun.senses(word):
                if len(sense) > i \
                and sense[i] != word \
                and sense[i] not in words: 
                    words.append(sense[i])
                    
        return words[:top]
    
    def get_relations(self, word, previous=None):
        
        """ The graph displays semantic relations for a noun,
        e.g. light -> has-specific -> candlelight.
        """
        
        word = str(word)
        
        if self.is_expandable(word): 
            return self.expand(word, previous)

        words = []
        lexname = en.noun.lexname(word)
        if lexname != "":
            words.append((lexname, "category "))
        
        relations = [
            (6, en.noun.holonym  , "has-parts"),
            (2, en.noun.meronym  , "is-part-of"),
            (2, en.noun.antonym  , "is-opposite-of"),
            (3, en.noun.hypernym , "is-a"),
            (2, en.verb.senses   , "is-action"),
            (6, en.noun.hyponym  , "has-specific"),
        ]
        # Get related words from WordNet.
        # Exclude long words and take the top of the list.
        for top, f, relation in relations:
            r = []
            try: rng = f(word, sense=self.senses.current)
            except:
                try: rng = f(word)
                except:
                    continue
            for w in rng:
                if  w[0] != word \
                and w[0] not in r \
                and len(w[0]) < 20:
                    r.append((w[0], relation))
                    
            words.extend(r[:top])
            
        return words
    
    def expand(self, relation, previous=None):
        
        """ Zoom in to the hyponym or holonym branch.
        """
        
        if relation == "has-specific" : f = en.noun.hyponym
        if relation == "has-parts"    : f = en.noun.holonym
        
        root = str(self.root.id.lower())
        unique = []
        if previous: previous = str(previous)
        for w in f(previous, sense=self.senses.current):
            if w[0] not in unique: unique.append(w[0])
        shuffle(unique)
        
        words = []
        i = 0
        for w in unique:
            # Organise connected nodes in branches of 4 nodes each.
            # Nodes that have the root id in their own id,
            # form a branch on their own.
            label = " "
            if w.find(root) < 0:
                label = (i+4)/4*"  "
                i += 1
            words.append((w, label))
            
        return words
    
    def click(self, node):
        
        """ If the node is indeed clickable, load it.
        """
        
        if self.is_clickable(node):
            p = self.root.id
            # Use the previous back node instead of "has specific".
            if self.is_expandable(p): p = self.nodes[-1].id
            self.load(node.id, previous=p)
    
    def load(self, word, previous=None):
        
        self.clear()
        
        word = str(word)
        
        # Add the root (the clicked node) with the ROOT style.
        self.add_node(word, root=True, style="root")
        
        # Add the word senses to the root in the LIGHT style.
        for w in self.get_senses(word):
            self.add_node(w, style=self.styles.light.name)
            self.add_edge(word, w, 0.5)
            if len(self) > self.max: break

        # Add relation branches to the root in the DARK style.
        for w, r in self.get_relations(word, previous):
            self.add_node(r, style="dark")
            self.add_edge(w, r, 1.0)
            self.add_edge(word, r)
            if len(self) > self.max: break    

        # Provide a back link to the previous word.
        if previous and previous != self.root.id:
            n = self.add_node(previous, 10)
            if len(n.links) == 0: self.add_edge(word, n.id)
            n.style = "back"
        
        # Indicate the word corresponding to the current sense.
        if self.senses.count() > 0:
            for w in en.noun.senses(word)[self.senses.current]:
                n = self.node(w)
                if n and n != self.root: 
                    n.style = "marked"

    def draw(self, *args, **kwargs):
        
        """ Additional drawing for sense selection buttons.
        """
        
        graph.graph.draw(self, *args, **kwargs)
        self.senses.draw()

### WORD SENSE SELECTION #############################################################################

class senses:
    
    """ A row of word sense selection buttons.
    """
    
    def __init__(self, graph, x, y):
        
        self.graph = graph
        self.word = ""
        self.x = x
        self.y = y
        
        self.current = 0
        self.pressed = None
    
    def count(self):
        
        """ The number of senses for the current word.
        The current word is synched to the graph's root node.
        """
        
        if self.word != self.graph.root.id:
            self.word = str(self.graph.root.id)
            self.current = 0
            self._count = 0
            try: self._count = len(en.noun.senses(self.word))
            except:
                pass
                
        return self._count
    
    def draw(self):
        
        s = self.graph.styles.default
        x, y, f = self.x, self.y, s.fontsize
        
        _ctx.reset()
        _ctx.nostroke()
        _ctx.fontsize(f)
        
        for i in range(self.count()):
            
            clr = s.fill
            if i == self.current:
                clr = self.graph.styles.default.background
            _ctx.fill(clr)
            p = _ctx.rect(x, y, f*2, f*2)
            _ctx.fill(s.text)
            _ctx.align(CENTER)
            _ctx.text(str(i+1), x-f, y+f*1.5, width=f*4)
            x += f * 2.2
            
            self.log_pressed(p, i)
            self.log_clicked(p, i)
    
    def log_pressed(self, path, i):
        
        """ Update senses.pressed to the last button pressed.
        """
        
        if mousedown \
        and self.graph.events.dragged == None \
        and path.contains(MOUSEX, MOUSEY):
            self.pressed = i

    def log_clicked(self, path, i):
        
        """ Update senses.current to the last button clicked.
        """
        
        if not mousedown and self.pressed == i:
            self.pressed = None
            if path.contains(MOUSEX, MOUSEY):
                self.current = i
                self.graph.load(self.graph.root.id)      
        
######################################################################################################

g = wordnetgraph(distance=1.2)
g.load(query)

size(550, 550)
speed(30) 
def draw():
    g.styles.textwidth = 120
    g.draw(
        directed=True, 
        weighted=True,
        traffic=True
    )
    