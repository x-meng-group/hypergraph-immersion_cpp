from networkx import Graph
from networkx.algorithms.bipartite import hopcroft_karp_matching

# let's start with a simple class that holds the matchings

class matching:

    def __init__(self) -> None:
        # nodes in H will match the numeric indexes of H, while nodes in G will be in tuples of (node number, "G")
        self.graph = Graph()
        self.H_set = set() # holds nodes of H
        self.G_set = set() # holds all nodes in G
        pass

    def copy(self):
        M = matching()
        M.graph = self.graph.copy()
        M.H_set = self.H_set.copy()
        M.G_set = self.G_set.copy()
        return M
    
    # just use G_node number
    def add_edge(self, H_node: int, G_node: int) -> None:
        '''
        :param H_node: a node in H
        :param G_node: a node in G
        '''
        self.graph.add_edge(H_node, (G_node, "G"))
        self.H_set.add(H_node)
        self.G_set.add(G_node)
        pass

    def remove_edge(self, H_node: int, G_node: int) -> None:
        '''
        :param H_node: a node in H
        :param G_node: a node in G
        '''
        self.graph.remove_edge(H_node, (G_node, "G"))
        pass

    def add_G_node(self, G_node: int) -> None:
        '''
        :param G_node: a node in G
        '''
        self.graph.add_node((G_node, "G"))
        self.G_set.add(G_node)
        pass

    def add_H_node(self, H_node: int) -> None:
        '''
        :param H_node: a node in H
        '''
        self.graph.add_node(H_node)
        self.H_set.add(H_node)
        pass

    def remove_G_node(self, G_node: int) -> None:
        '''
        :param G_node: a node in G
        '''
        self.G_set.remove(G_node)
        self.graph.remove_node((G_node, "G"))
        pass

    def remove_H_node(self, H_node: int) -> None:
        '''
        :param H_node: a node in H
        '''
        self.G_set.remove(H_node)
        self.graph.remove_node(H_node)
        pass

    def linked(self, H_node: int, G_node: int) -> bool:
        '''
        :param H_node: a node in H
        :param G_node: a node in G
        '''
        return self.graph.has_edge(H_node, (G_node, "G"))
    
    def G_node_neighbors(self, G_node: int) -> set[int]:
        '''
        :param G_node: a node in G
        '''
        s = set()
        for H_node in self.graph.neighbors((G_node, "G")):
            s.add(H_node)
        return s
    
    def H_node_neighbors(self, H_node: int) -> set[int]:
        '''
        :param H_node: a node in H
        '''
        s = set()
        for G_node in self.graph.neighbors(H_node):
            s.add(G_node[0])
        return s

    # does not return the actual matching, it just checks if it exists
    def match_exists(self) -> bool:
        return self.H_set <= set(hopcroft_karp_matching(self.graph, self.H_set).keys())
    
    # actually returns the matching
    def match(self):
        Match = hopcroft_karp_matching(self.graph, self.H_set)
        return self.H_set <= set(Match.keys()), Match