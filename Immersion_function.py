from Hypergraph import hypergraph

class immersion_function:

    def __init__(self, node_mapping: dict, edge_mapping: dict, G: hypergraph, H: hypergraph) -> None:
        '''
        :param node_mapping: the keys are the nodes in H and the objects are the coresponding nodes in G
        :param edge_mapping: the keys are edges in H, which link to sets of edges in G (connected subgraphs)
        :param G: the graph you are trying to immerse onto
        :param H: the graph you want to immerse into G
        '''
        self.__node_mapping = node_mapping.copy()
        self.__edge_mapping = edge_mapping.copy()
        self.__G = G.copy()
        self.__H = H.copy()
        pass

    def evaluate(self, type: str, n: int) -> int | tuple:
        '''
        :param type: input "edge" for evalutation of an edge and "node" for evaluation or a node
        :param n: the numerical label of the node or edge you want to evaluate
        '''
        if type == "edge":
            return self.__edge_mapping[n]
        return self.__node_mapping[n]
    
    def image(self, Type: str, item: any) -> set:
        '''
        :param Type: input "edge" for evalutation of an edge and "node" for evaluation or a node
        :param item: any itterable or integer you want to evaluate
        '''
        s = set()
        if type(item) == int:
            if Type == "node":
                s.add(self.evaluate("node", item))
            else:
                s |= set(self.evaluate("edge", item))
        else:
            for n in item:
                s |= self.image(Type, n)
        return s
    
    def is_immersion(self) -> bool:

        # checking if the domain of our immersion function includes all nodes and edges of H
        if set(self.__edge_mapping.keys()) != self.__H.hyperedges:
            return False
        if set(self.__node_mapping.keys()) != self.__H.nodes:
            return False
        
        # checks for unique vertex mapping (requirement 1)
        # checks that each node in H maps to a unique node that is in G
        already_mapped_nodes = set()
        for H_node in self.__H.nodes:
            G_node = self.evaluate("node", H_node)
            if G_node in (self.__G.nodes - already_mapped_nodes):
                already_mapped_nodes.add(G_node)
            else:
                return False
        # requirements 2 and 3
        # checks that every edge in H maps to a distinct (i.e. no edge in G is in more than one mapping) set of edges in G
        # also checks if that set of edges in conncected
        already_mapped_edges = set()
        for H_edge in self.__H.hyperedges:
            subgraph = set(self.evaluate("edge", H_edge))

            # checks if we have a subgraph of G and that it is disjoint from all previous mappings
            # thus part of this check encoompases all of requirement 3
            if not subgraph <= (self.__G.hyperedges - already_mapped_edges):
                return False
        
            already_mapped_edges |= subgraph
        
            # checking if the subgraph is connected
            if not self.__G.is_connected(subgraph):
                return False

            # checks if subgraph contains all of the mappings of every point in H_edge
            # makes set of G_nodes in subgraph
            # then itterates through all H_nodes to check if their mappings are in that set
            G_nodes = set()
            for G_edge in subgraph:
                G_nodes |= self.__G.hyperedge_sets[G_edge]
        
            for H_node in self.__H.hyperedge_sets[H_edge]:
                if not (self.evaluate("node", H_node) in G_nodes):
                    return False
        return True
    
    def __str__(self):
        return "G: " + str(self.__G) + "\nH: " + str(self.__H) + "\nNodes: " + str(self.__node_mapping) + "\nEdges: " + str(self.__edge_mapping)
    
    def G(self, copy: bool = True) -> hypergraph:
        '''
        :param copy: if true, a copy will be returned, otherwise, modifying what is returned will modify the hypergrah embedded in this class
        '''
        if copy:
            return self.__G.copy()
        return self.__G
    
    def H(self, copy: bool = True) -> hypergraph:
        '''
        :param copy: if true, a copy will be returned, otherwise, modifying what is returned will modify the hypergrah embedded in this class
        '''
        if copy:
            return self.__H.copy()
        return self.__H
    
    def __eq__(self, o) -> bool:
        if self.__G == o.G() and self.__H == o.H():
            for node in self.__H.nodes:
                if self.evaluate("node", node) != o.evaluate("node", node):
                    return False
            for edge in self.__H.hyperedges:
                if self.evaluate("edge", edge) != o.evaluate("edge", edge):
                    return False
            return True
        return False
    
    def __ne__(self, o) -> bool:
        return not self == o
    
    def equal_edge_mapping(self, o) -> bool:
        if self.__G == o.G() and self.__H == o.H():
            for edge in self.__H.hyperedges:
                if set(self.evaluate("edge", edge)) != set(o.evaluate("edge", edge)):
                    return False
            return True
        return False
    
    def is_reasonable(self) -> bool:
        '''
        Evaluates whether or not every immersed to edge contains an immersed to point
        '''
        
        for H_hyperedge in self.__H.hyperedges:
            G_nodes = self.image("node", self.__H.hyperedge_sets[H_hyperedge])
            G_hyperedges = self.evaluate("edge", H_hyperedge)
            for G_hyperedge in G_hyperedges:
                s = set(G_hyperedges)
                s.remove(G_hyperedge)
                new_G_nodes = set()
                for hyperedge in s:
                    new_G_nodes |= self.__G.hyperedge_sets[hyperedge]
                if G_nodes <= new_G_nodes and self.__G.is_connected(s):
                    return False
        return True
    
    def cost(self) -> int:
        '''
        Returns the amount of G edges used in the immersion function
        '''

        cost = 0
        for hyperedge in self.__H.hyperedges:
            cost += len(self.evaluate("edge", hyperedge))
        return cost
    
    def copy(self):
        '''
        Just coppies the immersion function
        '''
        return immersion_function(self.__node_mapping, self.__edge_mapping, self.__G, self.__H)