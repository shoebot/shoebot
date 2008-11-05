import heapq
from sets import Set
from random import random
from warnings import warn

#--- PRIORITY QUEUE ----------------------------------------------------------------------------------
# Currently not in use.

class priorityqueue(dict):
    
    def push(self, e, w): 
        self[e] = w
    
    def pop(self):
        p, w = None, float("inf")
        for e in self:
            if self[e] <= w: p, w = e, self[e]
        if p: del self[p]
        return p

#--- DEPTH-FIRST SEARCH ------------------------------------------------------------------------------

def depth_first_search(root, visit=lambda node: False, traversable=lambda node, edge: True):

    """ Simple, multi-purpose depth-first search.
    
    Visits all the nodes connected to the root, depth-first.
    The visit function is called on each node.
    Recursion will stop if it returns True, and ubsequently dfs() will return True.
    The traversable function takes the current node and edge,
    and returns True if we are allowed to follow this connection to the next node.
    For example, the traversable for directed edges is follows:
    lambda node, edge: node == edge.node1
    
    Note: node._visited is expected to be False for all nodes.
    
    """

    stop = visit(root)
    root._visited = True
    for node in root.links:
        if stop: return True
        if not traversable(root, root.links.edge(node)): continue
        if not node._visited:
            stop = depth_first_search(node, visit, traversable)
    return stop

#--- ADJACENCY LIST ----------------------------------------------------------------------------------

def adjacency(graph, directed=False, reversed=False, stochastic=False, heuristic=None):
    
    """ An edge weight map indexed by node id's.
    
    A dictionary indexed by node id1's in which each value is a
    dictionary of connected node id2's linking to the edge weight.
    If directed, edges go from id1 to id2, but not the other way.
    If stochastic, all the weights for the neighbors of a given node sum to 1.
    A heuristic can be a function that takes two node id's and returns
    and additional cost for movement between the two nodes.
    
    """
    
    v = {}
    for n in graph.nodes:
        v[n.id] = {}
    
    for e in graph.edges:
        
        id1 = e.node1.id
        id2 = e.node2.id
        if reversed:
            id1, id2 = id2, id1
            
        #if not v.has_key(id1): v[id1] = {}
        #if not v.has_key(id2): v[id2] = {}
        v[id1][id2] = 1.0 - e.weight*0.5
        
        if heuristic:
            v[id1][id2] += heuristic(id1, id2)
        
        if not directed: 
            v[id2][id1] = v[id1][id2]
        
    if stochastic:
        for id1 in v:
            d = sum(v[id1].values())
            for id2 in v[id1]: 
                v[id1][id2] /= d
    
    return v

#--- DIJKSTRA SHORTEST PATH --------------------------------------------------------------------------

def dijkstra_shortest_path(graph, id1, id2, heuristic=None):

    """ Dijkstra algorithm for finding shortest paths.
    
    Connelly Barnes, http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/119466
    Raises an IndexError between nodes on unconnected graphs.
    
    """
    
    G = adjacency(graph, heuristic=heuristic)
    start = id1
    end = id2
    
    # Flatten linked list of form [0,[1,[2,[]]]]
    def flatten(L):       
        while len(L) > 0:
            yield L[0]
            L = L[1]

    q = [(0, start, ())]  # Heap of (cost, path_head, path_rest).
    visited = Set()       # Visited vertices.
    while True:
        (cost1, v1, path) = heapq.heappop(q)
        if v1 not in visited:
            visited.add(v1)
        if v1 == end:
            return list(flatten(path))[::-1] + [v1]
        path = (v1, path)
        for (v2, cost2) in G[v1].iteritems():
            if v2 not in visited:
                heapq.heappush(q, (cost1 + cost2, v2, path))

#--- BRANDES BETWEENNESS CENTRALITY ------------------------------------------------------------------

def brandes_betweenness_centrality(graph, normalized=True):

    """ Betweenness centrality for nodes in the graph.
    
    Betweenness centrality is a measure of the number of shortests paths that pass through a node.
    Nodes in high-density areas will get a good score.
    
    The algorithm is Brandes' betweenness centrality,
    from NetworkX 0.35.1: Aric Hagberg, Dan Schult and Pieter Swart,
    based on Dijkstra's algorithm for shortest paths modified from Eppstein.
    https://networkx.lanl.gov/wiki
    
    """

    G = graph.keys()
    W = adjacency(graph)
    
    betweenness = dict.fromkeys(G, 0.0) # b[v]=0 for v in G
    for s in G: 
        S = [] 
        P = {} 
        for v in G: P[v] = [] 
        sigma = dict.fromkeys(G, 0) # sigma[v]=0 for v in G 
        D = {} 
        sigma[s] = 1
        seen = { s: 0 }  
        Q = [] # use Q as heap with (distance, node id) tuples 
        heapq.heappush(Q, (0, s, s)) 
        while Q:    
            (dist, pred, v) = heapq.heappop(Q) 
            if v in D: continue # already searched this node
            sigma[v] = sigma[v] + sigma[pred] # count paths 
            S.append(v) 
            D[v] = seen[v] 
            for w in graph[v].links:
                
                w = w.id
                vw_dist = D[v] + W[v][w]
                
                if w not in D and (w not in seen or vw_dist < seen[w]): 
                    seen[w] = vw_dist 
                    heapq.heappush(Q, (vw_dist, v, w)) 
                    P[w] = [v] 
                elif vw_dist == seen[w]: # handle equal paths 
                    sigma[w] = sigma[w] + sigma[v] 
                    P[w].append(v)
                    
        delta = dict.fromkeys(G,0)  
        while S: 
            w = S.pop() 
            for v in P[w]: 
                delta[v] = delta[v] + (float(sigma[v]) / float(sigma[w])) * (1.0 + delta[w]) 
            if w != s: 
                betweenness[w] = betweenness[w] + delta[w]

        #-----------------------------------
        if normalized:
            # Normalize between 0.0 and 1.0.
            m = max(betweenness.values())
            if m == 0: m = 1
        else:
            m = 1
            
        betweenness = dict([(id, w/m) for id, w in betweenness.iteritems()])
        return betweenness

#--- EIGENVECTOR CENTRALITY --------------------------------------------------------------------------

class NoConvergenceError(Exception): pass

def eigenvector_centrality(graph, normalized=True, reversed=True, rating={},
                           start=None, iterations=100, tolerance=0.0001):

    """ Eigenvector centrality for nodes in the graph (like Google's PageRank).
    
    Eigenvector centrality is a measure of the importance of a node in a directed network. 
    It rewards nodes with a high potential of (indirectly) connecting to high-scoring nodes.
    Nodes with no incoming connections have a score of zero.
    If you want to measure outgoing connections, reversed should be False.

    The eigenvector calculation is done by the power iteration method.
    It has no guarantee of convergence.
    A starting vector for the power iteration can be given in the start dict.
    
    You can adjust the importance of a node with the rating dictionary,
    which links node id's to a score.
    
    The algorithm is adapted from NetworkX, Aric Hagberg (hagberg@lanl.gov):
    https://networkx.lanl.gov/attachment/ticket/119/eigenvector_centrality.py

    """

    G = graph.keys()     
    W = adjacency (graph, directed=True, reversed=reversed)

    def _normalize(x):
        s = sum(x.values())
        if s != 0: s = 1.0 / s
        for k in x: 
            x[k] *= s
    
    x = start
    if x is None:
        x = dict([(n, random()) for n in G])
    _normalize(x)

    # Power method: y = Ax multiplication.
    for i in range(iterations):
        x0 = x
        x = dict.fromkeys(x0.keys(), 0)
        for n in x:
            for nbr in W[n]:
                r = 1
                if rating.has_key(n): r = rating[n]
                x[n] += 0.01 + x0[nbr] * W[n][nbr] * r
        _normalize(x)          
        e = sum([abs(x[n]-x0[n]) for n in x])
        if e < len(graph.nodes) * tolerance:
            if normalized:
                # Normalize between 0.0 and 1.0.
                m = max(x.values())
                if m == 0: m = 1
                x = dict([(id, w/m) for id, w in x.iteritems()])
            return x

    #raise NoConvergenceError
    warn("node weight is 0 because eigenvector_centrality() did not converge.", Warning)
    return dict([(n, 0) for n in G])