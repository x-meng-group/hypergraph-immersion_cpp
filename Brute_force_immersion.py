from Hypergraph import hypergraph
from Matching import matching
from Immersion_function import immersion_function

class brute_force_immersion:

    def __init__(self, G: hypergraph, H: hypergraph) -> None:
        '''
        :param G: the graph you are trying to immerse onto
        :param H: the graph you want to immerse into G
        '''
        self.G = G
        self.H = H
        
        self.immersions = [] # list of all possible immersion functions

        pass
    
    def get_node_mapping(self, edge_mapping: dict) -> None:
        '''
        :param edge_mapping: the dictionary that maps edges from H to sets of edges in G
        '''
        # first we must check if every edge maps to a connected subgraph
        for H_edge in self.H.hyperedges:
            if not self.G.is_connected(set(edge_mapping[H_edge])):
                return None
        match_graph = matching()
        # itterating through all nodes in H
        for H_node in self.H.nodes:
            possible_mappings = self.G.nodes.copy()
            for H_edge in self.H.node_sets[H_node]:
                G_node_set = set()
                for G_edge in edge_mapping[H_edge]:
                    G_node_set |= self.G.hyperedge_sets[G_edge]
                possible_mappings &= G_node_set
            if len(possible_mappings) > 0:
                for G_node in possible_mappings:
                    match_graph.add_edge(H_node, G_node)
            else:
                return None
        
        # Now we just need to do the matching
        match_exists, graph_matching = match_graph.match()
        if match_exists:
            node_mapping = dict()
            for H_node in self.H.nodes:
                node_mapping[H_node] = graph_matching[H_node][0]
            self.immersions.append(immersion_function(node_mapping, edge_mapping, self.G, self.H))
        
        pass
    
    # edge_list must be sorted for this to work 
    # edge mapping maps to ordered tuples of edges in G
    def complete_edge_mapping(self, edge_mapping: dict, edge_list: list, depth: int = 0) -> None:
        '''
        :param edge_mapping: the current state of the mapping of H edges to G edges
        :param edge_list: sorted list of edges in G
        :param depth: an internal paramiter that measures recursion depth
        '''
        self.get_node_mapping(edge_mapping)

        if depth >= len(edge_list):
            return None
        
        for jump in range(depth, len(edge_list)):
            for H_edge in self.H.hyperedges:
                if edge_list[jump] > edge_mapping[H_edge][0]:
                    new_edge_mapping = edge_mapping.copy()
                    new_edge_mapping[H_edge] += (edge_list[jump],)
                    self.complete_edge_mapping(new_edge_mapping, edge_list, jump + 1)
        
        # previous code
        '''
        self.complete_edge_mapping(edge_mapping, edge_list, depth + 1)
        
        G_edge = edge_list[depth]

        for H_edge in self.H.hyperedges:
            if G_edge > edge_mapping[H_edge][0]:
                new_edge_mapping = edge_mapping.copy()
                new_edge_mapping[H_edge] += (G_edge,)
                self.complete_edge_mapping(new_edge_mapping, edge_list, depth + 1)
        '''
        
        return None
    
    def immerse(self, edge_mapping: dict = dict(), H_edges: list = [], remaining_G_edges: set = set(), depth: int = 0) -> None:
        '''
        :param edge_mapping: the current state of the mapping of H edges to G edges
        :param H_edges: a list of all edges in H
        :param remaining_G_edges: a set of all unmapped to edges in G
        :param depth: an internal paramiter that measures recursion depth
        '''

        if depth == 0:
            edge_mapping = dict()
            H_edges = list(self.H.hyperedges)
            remaining_G_edges = self.G.hyperedges.copy()

        if depth >= len(H_edges):
            return self.complete_edge_mapping(edge_mapping, sorted(remaining_G_edges))
        
        H_edge = H_edges[depth]

        for G_edge in remaining_G_edges:
            new_edge_mapping = edge_mapping.copy()
            new_edge_mapping[H_edge] = (G_edge,)
            self.immerse(new_edge_mapping, H_edges, remaining_G_edges - {G_edge,}, depth + 1)

        return None