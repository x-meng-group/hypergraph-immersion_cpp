from Hypergraph import hypergraph
from Matching import matching
from Immersion_function import immersion_function


class immersion:

    def __init__(self, G: hypergraph, H: hypergraph) -> None:
        '''
        :param G: the graph you are trying to immerse onto
        :param H: the graph you want to immerse into G
        '''
        self.G = G
        self.H = H

        self.immersions = [] # list of all possible immersion functions

        self.edge_priority = []   

        self.depth = self.G.hyperedge_count - self.H.hyperedge_count

        self.__update_depth_internally = False

        pass

    def get_edge_priority(self) -> None:
        self.edge_priority.clear()
        # getting the priority order for edge immersion of H:

        edge_itteration = self.H.hyperedges.copy()
        self.edge_priority = [edge_itteration.pop()] # starts with an edge in the system
        for edge in edge_itteration:
            if len(self.H.hyperedge_sets[edge]) > len(self.H.hyperedge_sets[self.edge_priority[0]]):
                self.edge_priority = [edge]
            elif self.edge_priority[0] > edge:
                if len(self.H.hyperedge_sets[edge]) == len(self.H.hyperedge_sets[self.edge_priority[0]]):
                    self.edge_priority = [edge]
        del edge_itteration # set not needed anymore
        edge_itteration = self.H.hyperedges - {self.edge_priority[0],} # reusing the same variable for something else
        included_nodes = self.H.hyperedge_sets[self.edge_priority[0]].copy() # set of all points included in an already listed edge
        # used to set how many itterations there are
        for index in range(1, self.H.hyperedge_count):

            # ordering priority:
            # 1. edge that shares the most points with all previous edges combined
            # 2. if tie, edge with the most points of those that tied
            # 3. if tie again, edge with the lowest index of those that tied

            sub_itteration = edge_itteration.copy()
            self.edge_priority.append(sub_itteration.pop())
            for edge in sub_itteration:

                # priority step 1
                if len(self.H.hyperedge_sets[edge] & included_nodes) > len(self.H.hyperedge_sets[self.edge_priority[index]] & included_nodes):
                    self.edge_priority[index] = edge

                # priority step 2
                elif len(self.H.hyperedge_sets[edge]) > len(self.H.hyperedge_sets[self.edge_priority[index]]):
                    if len(self.H.hyperedge_sets[edge] & included_nodes) == len(self.H.hyperedge_sets[self.edge_priority[index]] & included_nodes):
                        self.edge_priority[index] = edge
                
                # priority step 3
                elif self.edge_priority[index] > edge:
                    if len(self.H.hyperedge_sets[edge]) == len(self.H.hyperedge_sets[self.edge_priority[index]]):
                        if len(self.H.hyperedge_sets[edge] & included_nodes) == len(self.H.hyperedge_sets[self.edge_priority[index]] & included_nodes):
                            self.edge_priority[index] = edge
            
            del sub_itteration
            included_nodes |= self.H.hyperedge_sets[self.edge_priority[index]] # adding all nodes in our new edge to the set
            edge_itteration.remove(self.edge_priority[index]) # removing the edge from iteration
        del included_nodes
        del edge_itteration
        pass

    def get_random_edge_priority(self) -> None:
        self.edge_priority.clear()
        edge_itteration = self.H.hyperedges.copy()
        self.edge_priority.append(edge_itteration.pop())
        next_edges = self.H.edge_adjacency[self.edge_priority[0]].copy()
        for index in range(1, self.H.hyperedge_count):
            self.edge_priority.append(next_edges.pop())
            edge_itteration.remove(self.edge_priority[index])
            next_edges |= self.H.edge_adjacency[self.edge_priority[index]] & edge_itteration
        pass

    # used for setting up the mapping of our first edge
    def set_up_initial_mapping(self, prev_subgraph: set, combos: list, removal_min: int = 0) -> list:
        '''
        :param prev_subgraph: the previous subgraph that we are working from
        :param combos: the list of all combos we have already checked for
        :param removal_min: the lowest edge index that can be removed, used to create a removal order thus ensuring each combo occurs only once
        '''

        if len(self.G.subgraph_nodes(prev_subgraph)) < len(self.H.hyperedge_sets[self.edge_priority[0]]):
            return combos
        
        if len(prev_subgraph) <= self.depth + 1:
            if self.G.is_connected(prev_subgraph):
                combos.append(prev_subgraph)
        
        for hyperedge in (prev_subgraph - set(range(removal_min))):
            self.set_up_initial_mapping(prev_subgraph - {hyperedge,}, combos, hyperedge + 1)
        
        return combos
    
    def quick_immerse(self, depth: int, max_results: int | None = None, use_random_priority: bool = False) -> bool:
        '''
        Allows for much more percice and direct attempts at immersion with localized checks. 
        However, this function may fail to find an immersion, even if one exists (one which would require a higher depth to find).
        If the depth paramiter is greater than (or equal to) the max depth required to find all immersions, then it will find every possible immersion.

        :param depth: the max search depth allowed
        :param max_results: if None, then there is no max, otherwise, it will stop once it has more than max immersions (give or take)
        :param use_random_priority: if True, the priority will be random, and if False, it will use a specific higharchy to set priority
        '''

        old_depth = self.depth
        self.depth = min(old_depth, depth)

        self.immersions.clear()
        
        if use_random_priority:
            self.get_random_edge_priority()
        else:
            self.get_edge_priority()

        self.__update_depth_internally = True
        
        start_check = 0 # where to start the cost check
        mapping_size = 1 # size of current mappings were are checking
        min_cost = self.G.hyperedge_count # min cost immersion we have

        for first_mapping in self.fast_initial_mapping():

            if len(first_mapping) > mapping_size:
                for I in self.immersions[start_check:]:
                    min_cost = min(min_cost, I.cost())
                start_check = len(self.immersions)
                mapping_size = len(first_mapping)
                if mapping_size + self.H.hyperedge_count >= min_cost: # if we cannot get an immersion of less or equal cost
                    break

            edge_mapping = dict()
            edge_mapping[self.edge_priority[0]] = tuple(sorted(first_mapping))
            matching_checker = dict()
            for G_node in self.G.subgraph_nodes(first_mapping):
                matching_checker[G_node] = {self.edge_priority[0],}
            self.recursive_immerse(edge_mapping, self.G.hyperedges - first_mapping, matching_checker, 1, len(first_mapping) - 1)

            if max_results != None:
                if len(self.immersions) >= max_results:
                    break
        self.depth = old_depth
        self.__update_depth_internally = False
        return len(self.immersions) > 0


    def immerse(self, use_random_priority: bool = False) -> bool:
        '''
        Finds every single immersion possible between the two hypergraphs

        :param use_random_priority: if True, the priority will be random, and if False, it will use a specific higharchy to set priority
        '''
        self.immersions.clear()
        
        if use_random_priority:
            self.get_random_edge_priority()
        else:
            self.get_edge_priority()

        #combos = []

        #for first_mapping in self.set_up_initial_mapping(self.G.hyperedges.copy(), combos, 0): - old
        for first_mapping in self.fast_initial_mapping():
            edge_mapping = dict()
            edge_mapping[self.edge_priority[0]] = tuple(sorted(first_mapping))
            matching_checker = dict()
            for G_node in self.G.subgraph_nodes(first_mapping):
                matching_checker[G_node] = {self.edge_priority[0],}
            self.recursive_immerse(edge_mapping, self.G.hyperedges - first_mapping, matching_checker, 1, len(first_mapping) - 1)

        return len(self.immersions) > 0
    
    def aquire_origins(self, origin: set, index: int, matching_checker: dict, max_origin_size: int, origins: list = [], removal_min: int = 0) -> list:
        '''
        :param origin: the origin we are working with
        :param index: the index marker of the edge we are working with
        :param matching_checker: a dictionary with G_nodes as keys which link to sets of H_edges whose mappings contain the G_node
        :param max_origin_size: the max size of the origin before exceeding depth
        :param origins: the current list of origins we add to
        :param removal_min: the lowest edge index that can be removed, used to create a removal order thus ensuring each combo occurs only once
        '''

        # checking if we have a vaild origin
        # bipartite mattching part
        match_check = matching()
        constrained_H_nodes = self.H.hyperedge_sets[self.edge_priority[index]] & self.H.subgraph_nodes(set(self.edge_priority[0:index]))

        for G_node in self.G.subgraph_nodes(origin) & set(matching_checker.keys()):
            for H_node in constrained_H_nodes:
                if matching_checker[G_node] >= (self.H.node_sets[H_node] & set(self.edge_priority[0:index])):
                    match_check.add_edge(H_node, G_node)
        if constrained_H_nodes == match_check.H_set and match_check.match_exists():
            if max_origin_size >= len(origin):
                origins.append(origin)
            for edge in (origin - set(range(removal_min))):
                self.aquire_origins(origin - {edge,}, index, matching_checker, max_origin_size, origins, edge + 1)
        return origins
    
    # how we expand out from the origin
    def branch(self, subgraph: set, blacklist: set, whitelist: set, G_free_edges: set, connectivity_status: bool, hyperedge_size: int, max_subgraph_size: int, subgraphs: list = [], just_reset: bool = False, current_branching: set = set()) -> list:
        '''
        :param subgraph: the subgraph we have so far
        :param blacklist: set of all edges we will not allow branching to. includes previous possibilities and any set part of the origin blob
        :param whitelist: all edges we can branch to
        :param G_free_edges: all edges in G which we have not mapped to
        :param connectivity_status: True if subgraph is connected and False if not
        :param hyperedge_size: the size of the hyperedge we are trying to immerse
        :param max_subgraph_size: max size of our subgraph
        :param subgraphs: list of our current set of possible mappings
        :param just_reset: True if our previous move was to reset the whitelist, otherwise False
        :param current_branching: all edges in G we have branched to since we last reset the whitelist
        '''

        # checking if we can write this to subgraphs
        if (not just_reset) and connectivity_status and hyperedge_size <= len(self.G.subgraph_nodes(subgraph)):
            subgraphs.append(subgraph)

        if max_subgraph_size > len(subgraph):

        
            # branching out
            # remember to remove all below in whitelist when branching to maintain order

            for hyperedge in whitelist:
                whitelist_removal = set(range(hyperedge + 1)) & whitelist
                if connectivity_status:
                    self.branch(subgraph | {hyperedge,}, blacklist | whitelist_removal, whitelist - whitelist_removal, G_free_edges, True, hyperedge_size, max_subgraph_size, subgraphs, False, current_branching | {hyperedge,})
                else:
                    self.branch(subgraph | {hyperedge,}, blacklist | whitelist_removal, whitelist - whitelist_removal, G_free_edges, self.G.is_connected(subgraph | {hyperedge,}), hyperedge_size, max_subgraph_size, subgraphs, False, current_branching | {hyperedge,})
        
            # reseting the whitelist
            if len(current_branching) > 0:
                new_blacklist = blacklist | whitelist
                new_whitelist = set()
                for hyperedge in current_branching:
                    new_whitelist |= self.G.edge_adjacency[hyperedge]
                new_whitelist &= G_free_edges
                new_whitelist -= new_blacklist
                if len(new_whitelist) > 0:
                    self.branch(subgraph, new_blacklist, new_whitelist, G_free_edges, connectivity_status, hyperedge_size, max_subgraph_size, subgraphs, True, set())
        return subgraphs
    
    def recursive_immerse(self, edge_mapping: dict, G_free_edges: set, matching_checker: dict, index: int = 1, mergers: int = 0) -> None:
        '''
        :param edge_mapping: the current edge mapping we are working with, keys are H_edges which link to sorted tuples of G_edges
        :param G_free_edges: all edges in G which we have not mapped to
        :param matching_checker: a dictionary with G_nodes as keys which link to sets of H_edges whose mappings contain the G_node
        :param index: a measure of recursing depth + an indicator of what edge we are immersing
        :param mergers: keeps track of how many times we have combined edges in order to not exceed depth
        '''

        # checking if we need to continue
        if index < self.H.hyperedge_count:


            # step 1: getting our central "blob"
            # this can be done by taking all edges in G adjasant to the mapping of all adjacent mapped edges to our current edge
        
            mapped_adjacents = set()
            for edge in self.H.edge_adjacency[self.edge_priority[index]] & set(self.edge_priority[0:index]):
                mapped_adjacents |= set(edge_mapping[edge])
        
            blob = set()
            for edge in mapped_adjacents:
                blob |= self.G.edge_adjacency[edge]
            blob &= G_free_edges

            # now we must aquire our origins
            # an origin is a subset of our "blob" that allows point matching, we must aquire all of them
            keys = set(matching_checker.keys())
            for origin_subgraph in self.aquire_origins(blob.copy(), index, matching_checker, self.depth - mergers + 1, []):
                whitelist = set()
                for hyperedge in origin_subgraph:
                    whitelist |= self.G.edge_adjacency[hyperedge]
                whitelist &= G_free_edges
                whitelist -= blob
                for complete_subgraph in self.branch(origin_subgraph, blob.copy(), whitelist, G_free_edges, self.G.is_connected(origin_subgraph), len(self.H.hyperedge_sets[self.edge_priority[index]]), self.depth - mergers + 1, [], False, set()):
                    # updating edge mapping
                    new_edge_mapping = edge_mapping.copy()
                    new_edge_mapping[self.edge_priority[index]] = tuple(sorted(complete_subgraph))

                    # updating matching checker
                    new_matching_checker = dict()
                    subgraph_nodes = self.G.subgraph_nodes(complete_subgraph)
                    for G_node in subgraph_nodes | keys:
                        if G_node in keys:
                            new_matching_checker[G_node] = matching_checker[G_node].copy()
                            if G_node in subgraph_nodes:
                                new_matching_checker[G_node].add(self.edge_priority[index])
                        else:
                            new_matching_checker[G_node] = {self.edge_priority[index],}
                
                    # recursive calling
                    self.recursive_immerse(new_edge_mapping, G_free_edges - complete_subgraph, new_matching_checker, index + 1, mergers + len(complete_subgraph) - 1)
        else:
            # once here, we have a completed edge mapping, which means that we can check for node mapping and then wirte it to the list if one is found
            self.get_node_mapping(edge_mapping, matching_checker)
        pass

    def get_node_mapping(self, edge_mapping: dict, matching_checker: dict) -> None:
        '''
        :param edge_mapping: the dictionary that maps edges from H to sets of edges in G
        :param matching_checker: a dictionary with G_nodes as keys which link to sets of H_edges whose mappings contain the G_node
        '''

        # setting up the bipartite matching
        match_graph = matching()
        for G_node in matching_checker.keys():
            for H_node in self.H.subgraph_nodes(matching_checker[G_node]):
                if matching_checker[G_node] >= self.H.node_sets[H_node]:
                    match_graph.add_edge(H_node, G_node)
        if self.H.nodes != match_graph.H_set:
            return None
        
        # Now we just need to do the matching
        match_exists, graph_matching = match_graph.match()
        if match_exists:
            node_mapping = dict()
            for H_node in self.H.nodes:
                node_mapping[H_node] = graph_matching[H_node][0]
            IMMERSION = immersion_function(node_mapping, edge_mapping, self.G, self.H)
            self.immersions.append(IMMERSION)
            if self.__update_depth_internally:
                self.depth = IMMERSION.cost() - self.H.hyperedge_count
        
        pass

    def fast_initial_mapping(self) -> list[set]:
        '''
        O(n^depth), n = number of edges in G (worst case computation time)
        This function can only be called after we have done the priority ordering
        '''

        min_nodes = len(self.H.hyperedge_sets[self.edge_priority[0]])

        whitelist = self.G.hyperedges.copy()
        blacklist = set()
        mappings = [[]]
        for i in range(self.depth):
            mappings.append([])
        while len(whitelist) > 0:
            hyperedge = whitelist.pop()
            blacklist.add(hyperedge)
            self.pointbranch(min_nodes, {hyperedge,}, whitelist & self.G.edge_adjacency[hyperedge], blacklist.copy(), mappings, self.G.hyperedge_sets[hyperedge], False, set())
        initial_mappings = []
        for i in mappings:
            initial_mappings += i
        return initial_mappings


    def pointbranch(self, min_nodes: int, subgraph: set, whitelist: set, blacklist: set, mappings: list[list[set]], nodes: set, just_reset: bool = False, current_branching: set = set()) -> None:
        '''
        Internal Recursive Function, subfunction of fast_inital_mapping

        :param min_nodes: the min amount of nodes in a subgraph
        :param subgraph: the subgraph we have so far
        :param whitelist: all edges we can branch to
        :param blacklist: set of all edges we will not allow branching to. includes previous possibilities and any set part of the origin blob
        :param mappings: list of lists of our current set of possible mappings (lists catigorized by size of subgraph in hyperedges, mappings[n] is all (n + 1) edge subgraphs)
        :param nodes: the set of nodes in G included in our set
        :param just_reset: True if our previous move was to reset the whitelist, otherwise False
        :param current_branching: all edges in G we have branched to since we last reset the whiteli
        '''

        # writing to our list of possibilities
        if (not just_reset) and min_nodes <= len(nodes):
            mappings[len(subgraph) - 1].append(subgraph)
        
        # Recursion calls
        if self.depth >= len(subgraph):

            # reseting part
            if len(current_branching) > 0:
                new_blacklist = blacklist | whitelist
                new_whitelist = set()
                for hyperedge in current_branching:
                    new_whitelist |= self.G.edge_adjacency[hyperedge]
                new_whitelist -= new_blacklist
                if len(new_whitelist) > 0:
                    self.pointbranch(min_nodes, subgraph, new_whitelist, new_blacklist, mappings, nodes, True, set())

            while len(whitelist) > 0:
                hyperedge = whitelist.pop()
                blacklist.add(hyperedge)
                self.pointbranch(min_nodes, subgraph | {hyperedge,}, whitelist.copy(), blacklist.copy(), mappings, nodes | self.G.hyperedge_sets[hyperedge], False, current_branching | {hyperedge})
        pass