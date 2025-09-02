from Hypergraph import hypergraph
from Matching import matching
from Immersion_function import immersion_function


# intended to be a far more optimized form of immersion

class quick_immersion:

    def __init__(self, G: hypergraph, 
                 H: hypergraph, 
                 max_depth: int | None = None, 
                 use_random_priority: bool = False, 
                 dynmaic_depth: bool = True
                 ) -> None:
        '''
        :param G: the graph you are trying to immerse onto
        :param H: the graph you want to immerse into G
        :param max_depth: the max amount of edge combining allowed
        :param use_random_priority: if True, the priority for edge mapping will not be determined algorithmically
        '''

        self.__smartdepth = dynmaic_depth # if True, the depth will be adjusted for each immersion found

        self.__max_depth = max_depth
        self.__depth = G.hyperedge_count - H.hyperedge_count
        if type(self.__max_depth) == int:
            if self.__max_depth < 0:
                raise ValueError ("max depth must be a non-negative integer")
            self.__depth = min(self.__max_depth, self.__depth)

        self.__G = G.copy()
        self.__H = H.copy()

        self.__match = matching() # the current matching with hyperedges
        self.__edge_mapping = dict() # H edges as keys and sets of G edges as objects
        self.__edge_node_mapping = dict() # H hyperedges to all G nodes in the current mapping
        for edge in self.__H.hyperedges:
            self.__edge_mapping[edge] = set() # of G hyperedges
            self.__edge_node_mapping[edge] = set() # of G nodes

        self.__match_history = dict() # keys are ints and objects are matchings by depth
        self.__edge_mapping_history = dict() # keys are ints and objects are edge mappings by depth
        self.__edge_node_mapping_history = dict() # keys are ints and objects are H edge to G node mappings by depth
        self.__G_edges_added = dict() # keys are ints and objects are G edges added

        self.__map_depth = 0 # number of steps we have made in changing the hyperedge mapping

        if use_random_priority:
            self.__priority = self.get_random_edge_priority()
        else:
            self.__priority = self.get_edge_priority()

        self.__priority_index = 0 # keeps track of where we are on the mapping priority
        self.__merges = 0 # number of mergers that have occured

        self.__best_immersions = []
        self.__G_free_edges = self.__G.hyperedges.copy()

        self.__end_depth = 0 # the depth that we are looking for for an end condition
        self.__end_amount = 100 # at or below the end depth, if we reach this number of possibilities, we have an end condition. 

        pass

    def change_G(self, G: hypergraph, copy: bool = True) -> None:
        '''
        This changes the current hypergraph G to a new hypergraph G

        :param G: the new hypergraph G
        :param copy: if True, it uses a copy of the hypergraph G
        '''

        self.__best_immersions.clear()
        self.__G_free_edges = G.hyperedges.copy()
        if copy:
            self.__G = G.copy()
        else:
            self.__G = G
        
        self.__depth = self.__G.hyperedge_count - self.__H.hyperedge_count
        if type(self.__max_depth) == int:
            self.__depth = min(self.__max_depth, self.__depth)
        
        pass

    def immersions(self, copy: bool = True) -> list[immersion_function]:
        '''
        Returns a list of all immersions found

        :param copy: if true, it will copy the list as well as its elements
        '''

        if copy:
            immersions = []
            for i in self.__best_immersions:
                immersions.append(i.copy())
            return immersions
        return self.__best_immersions

    def G(self, copy: bool = True) -> hypergraph:
        '''
        :param copy: if true, it will return a copy which prevents any changes to the origonal
        '''

        if copy:
            return self.__G.copy()
        return self.__G
    
    def H(self, copy: bool = True) -> hypergraph:
        '''
        :param copy: if true, it will return a copy which prevents any changes to the origonal
        '''

        if copy:
            return self.__H.copy()
        return self.__H
    
    def save(self, G_edge: int) -> None:
        '''
        This function advances our map depth and saves our history

        :param G_edge: the edge that is being added to the mapping
        '''

        self.__G_free_edges.remove(G_edge)
        self.__G_edges_added[self.__map_depth] = G_edge

        self.__match_history[self.__map_depth] = self.__match.copy()
        self.__edge_mapping_history[self.__map_depth] = dict()
        self.__edge_node_mapping_history[self.__map_depth] = dict()
        for hyperedge in self.__H.hyperedges:
            self.__edge_mapping_history[self.__map_depth][hyperedge] = self.__edge_mapping[hyperedge].copy()
            self.__edge_node_mapping_history[self.__map_depth][hyperedge] = self.__edge_node_mapping[hyperedge].copy()
        self.__map_depth += 1
        pass

    def revert(self) -> None:
        '''
        Reverts one step back
        '''

        if self.__map_depth <= 0:
            raise ValueError("This can only be called if the map depth is a postive number. The map depth was:", self.__map_depth)
        self.__map_depth -= 1

        if len(self.__edge_mapping_history[self.__map_depth][self.__priority[self.__priority_index]]) > 0:
            self.__merges -= 1

        del self.__match
        del self.__edge_mapping
        del self.__edge_node_mapping

        self.__match = self.__match_history.pop(self.__map_depth)
        self.__edge_mapping = self.__edge_mapping_history.pop(self.__map_depth)
        self.__edge_node_mapping = self.__edge_node_mapping_history.pop(self.__map_depth)
        self.__G_free_edges.add(self.__G_edges_added.pop(self.__map_depth))

        pass
    

    def add_G_edge(self, G_edge: int) -> None:
        '''
        This function adds an edge to the edge mapping and updates all things involved with updating the map_depth so the previous one is saved

        :param G_edge: the edge in G that you are adding into the system
        '''

        if len(self.__edge_mapping[self.__priority[self.__priority_index]]) > 0:
            self.__merges += 1

        self.save(G_edge) # saving what we have so far so we can revert back to it if needed

        # some edges of the matching must be removed if we are intergating a new H_edge
        if len(self.__edge_mapping[self.__priority[self.__priority_index]]) == 0:
            for H_node in self.__H.hyperedge_sets[self.__priority[self.__priority_index]]:
                if H_node in self.__match.H_set:
                    for G_node in self.__match.H_node_neighbors(H_node):
                        if G_node not in self.__G.hyperedge_sets[G_edge]:
                            self.__match.remove_edge(H_node, G_node)
                else:
                    self.__match.add_H_node(H_node)

        # now adding any new connections for points that are new members of what we are mapping to
        for G_node in (self.__G.hyperedge_sets[G_edge] - self.__edge_node_mapping[self.__priority[self.__priority_index]]):
            self.__edge_node_mapping[self.__priority[self.__priority_index]].add(G_node)
            for H_node in self.__H.hyperedge_sets[self.__priority[self.__priority_index]]:
                linked = True
                for H_edge in (self.__H.node_sets[H_node] - {self.__priority[self.__priority_index],}):
                    if G_node not in self.__edge_node_mapping[H_edge]:
                        linked = False
                        break
                if linked:
                    self.__match.add_edge(H_node, G_node)
        
        self.__edge_mapping[self.__priority[self.__priority_index]].add(G_edge)
        pass
        
    def get_edge_priority(self) -> list[int]:
        edge_priority = []
        # getting the priority order for edge immersion of H:

        edge_itteration = self.__H.hyperedges.copy()
        edge_priority = [edge_itteration.pop()] # starts with an edge in the system
        for edge in edge_itteration:
            if len(self.__H.hyperedge_sets[edge]) > len(self.__H.hyperedge_sets[edge_priority[0]]):
                edge_priority = [edge]
            elif edge_priority[0] > edge:
                if len(self.__H.hyperedge_sets[edge]) == len(self.__H.hyperedge_sets[edge_priority[0]]):
                    edge_priority = [edge]
        del edge_itteration # set not needed anymore
        edge_itteration = self.__H.hyperedges - {edge_priority[0],} # reusing the same variable for something else
        included_nodes = self.__H.hyperedge_sets[edge_priority[0]].copy() # set of all points included in an already listed edge
        # used to set how many itterations there are
        for index in range(1, self.__H.hyperedge_count):

            # ordering priority:
            # 1. edge that shares the most points with all previous edges combined
            # 2. if tie, edge with the most points of those that tied
            # 3. if tie again, edge with the lowest index of those that tied

            sub_itteration = edge_itteration.copy()
            edge_priority.append(sub_itteration.pop())
            for edge in sub_itteration:

                # priority step 1
                if len(self.__H.hyperedge_sets[edge] & included_nodes) > len(self.__H.hyperedge_sets[edge_priority[index]] & included_nodes):
                    edge_priority[index] = edge

                # priority step 2
                elif len(self.__H.hyperedge_sets[edge]) > len(self.__H.hyperedge_sets[edge_priority[index]]):
                    if len(self.__H.hyperedge_sets[edge] & included_nodes) == len(self.__H.hyperedge_sets[edge_priority[index]] & included_nodes):
                        edge_priority[index] = edge
                
                # priority step 3
                elif edge_priority[index] > edge:
                    if len(self.__H.hyperedge_sets[edge]) == len(self.__H.hyperedge_sets[edge_priority[index]]):
                        if len(self.__H.hyperedge_sets[edge] & included_nodes) == len(self.__H.hyperedge_sets[edge_priority[index]] & included_nodes):
                            edge_priority[index] = edge
            
            del sub_itteration
            included_nodes |= self.__H.hyperedge_sets[edge_priority[index]] # adding all nodes in our new edge to the set
            edge_itteration.remove(edge_priority[index]) # removing the edge from iteration
        del included_nodes
        del edge_itteration
        return edge_priority
    
    def get_random_edge_priority(self) -> list[int]:
        edge_priority = []
        edge_itteration = self.__H.hyperedges.copy()
        edge_priority.append(edge_itteration.pop())
        next_edges = self.__H.edge_adjacency[edge_priority[0]].copy()
        for index in range(1, self.__H.hyperedge_count):
            edge_priority.append(next_edges.pop())
            edge_itteration.remove(edge_priority[index])
            next_edges |= self.__H.edge_adjacency[edge_priority[index]] & edge_itteration
        return edge_priority
    
    def write(self, alpha: immersion_function) -> bool:
        '''
        This will update the depth if applicable and write the immersion iff the immersion uses an equivient cost
        If this immersion uses a lower cost, it clears all other immersions and makes this one the only one, and it will update the depth
        returns true if we have met our end condition

        :param alpha: the immersion function we want to write
        '''

        alpha_depth = alpha.cost() - self.__H.hyperedge_count
        if alpha_depth > self.__depth:
            raise ValueError("Somehow an immersion outside of our depth bounds was created.")
        if alpha_depth < self.__depth and self.__smartdepth:
            self.__depth = alpha_depth
            del self.__best_immersions
            self.__best_immersions = [alpha,]
            return self.__depth <= self.__end_depth and 1 >= self.__end_amount
        self.__best_immersions.append(alpha)
        return self.__depth <= self.__end_depth and len(self.__best_immersions) >= self.__end_amount
    
    def node_mapping(self) -> bool:
        '''
        aquires the node mapping from the edge mapping
        '''
        
        # Now we just need to do the matching
        match_exists, graph_matching = self.__match.match()
        if match_exists:
            node_mapping = dict()
            for H_node in self.__H.nodes:
                node_mapping[H_node] = graph_matching[H_node][0]
            edge_mapping = dict()
            for H_edge in self.__H.hyperedges:
                edge_mapping[H_edge] = tuple(sorted(self.__edge_mapping[H_edge]))
            return self.write(immersion_function(node_mapping, edge_mapping, self.__G, self.__H))
        return False


    def execute(self, show_end_condition: bool = False, depth: int = 0, amount: int = 100) -> bool:
        '''
        Returns true if an immersion was found and returns false if one was not found

        :param show_end_condition: if true, it will print out why it has ended
        :param depth: your intended cost goal for an end condition
        :param amount: the amount of possibilities you want within that cost goal before ending
        '''

        self.__end_depth = depth
        self.__end_amount = amount

        del self.__best_immersions
        self.__best_immersions = []

        if self.initialize():
            if show_end_condition:
                print("Ended due to meeting depth and amount condition of", amount, "immersion(s) with", depth, "or fewer edge mergers.")
            if self.__map_depth > 0:
                del self.__match
                del self.__edge_mapping
                del self.__edge_node_mapping

                self.__match = self.__match_history.pop(0)
                self.__edge_mapping = self.__edge_mapping_history.pop(0)
                self.__edge_node_mapping = self.__edge_node_mapping_history.pop(0)
                self.__G_free_edges = self.__G.hyperedges.copy()

                del self.__match_history
                del self.__edge_mapping_history
                del self.__edge_node_mapping_history
                del self.__G_edges_added
                
                self.__match_history = dict()
                self.__edge_mapping_history = dict()
                self.__edge_node_mapping_history = dict()
                self.__G_edges_added = dict()

            self.__map_depth = 0
            self.__merges = 0
            self.__priority_index = 0
        elif show_end_condition:
            print("Ended by going through all possibilities")

        self.__end_depth = 0
        self.__end_amount = 100

        return len(self.__best_immersions) > 0
    
    def initialize(self) -> bool:
        '''
        This function will itterate through all possible ways to map the first hyperedge in the priority
        '''

        whitelist = self.__G.hyperedges.copy()
        blacklist = set()
        while len(whitelist) > 0:
            hyperedge = whitelist.pop()
            blacklist.add(hyperedge)
            self.add_G_edge(hyperedge)
            if self.initialize_branching(whitelist & self.__G.edge_adjacency[hyperedge], blacklist.copy(), False, set()):
                return True
        return False

    def initialize_branching(self, whitelist: set, blacklist: set, just_reset: bool = False, current_branching: set = set()) -> bool:
        '''
        Internal Recursive Function, subfunction of fast_inital_mapping

        :param whitelist: all edges we can branch to
        :param blacklist: set of all edges we will not allow branching to. includes previous possibilities and any set part of the origin blob
        :param just_reset: True if our previous move was to reset the whitelist, otherwise False
        :param current_branching: all edges in G we have branched to since we last reset the whitelist
        '''

        # writing to our list of possibilities
        if (not just_reset) and len(self.__H.hyperedge_sets[self.__priority[0]]) <= len(self.__edge_node_mapping[self.__priority[0]]):
            if self.immerse_next_edge():
                return True
        
        # Recursion calls
        if self.__depth >= len(self.__edge_mapping[self.__priority[0]]):

            # reseting part
            if len(current_branching) > 0:
                new_blacklist = blacklist | whitelist
                new_whitelist = set()
                for hyperedge in current_branching:
                    new_whitelist |= self.__G.edge_adjacency[hyperedge]
                new_whitelist -= new_blacklist
                if len(new_whitelist) > 0:
                    if self.initialize_branching(new_whitelist, new_blacklist, True, set()):
                        return True

            while len(whitelist) > 0:
                hyperedge = whitelist.pop()
                blacklist.add(hyperedge)
                self.add_G_edge(hyperedge)
                if self.initialize_branching(whitelist.copy(), blacklist.copy(), False, current_branching | {hyperedge,}):
                    return True
        if not just_reset:
            self.revert()
        return False
    
    def immerse_next_edge(self) -> bool:
        '''
        Immerses the next edge when called
        '''

        if self.__priority_index + 1 >= self.__H.hyperedge_count:
            return self.node_mapping()
        
        self.__priority_index += 1
        
        mapped_adjacents = set()
        
        adjacent_list = []

        for edge in self.__H.edge_adjacency[self.__priority[self.__priority_index]] & set(self.__priority[0:self.__priority_index]):
            mapped_adjacents |= self.__edge_mapping[edge]
            adjacents = set()
            for hyperedge in self.__edge_mapping[edge]:
                adjacents |= self.__G.edge_adjacency[hyperedge]
            adjacents &= self.__G_free_edges
            if len(adjacents) == 0:
                self.__priority_index -= 1
                return False
            adjacent_list.append(adjacents)
        
        blob = set()
        for edge in mapped_adjacents:
            blob |= self.__G.edge_adjacency[edge]
        blob &= self.__G_free_edges

        blacklist = set()
        while len(blob) > 0:
            hyperedge = blob.pop()
            branch_adjacents = []
            blacklist.add(hyperedge)
            self.add_G_edge(hyperedge)
            for s in adjacent_list:
                if not (hyperedge in s):
                    branch_adjacents.append(s)
            if self.branch((self.__G_free_edges & self.__G.edge_adjacency[hyperedge]) - blacklist, blacklist.copy(), blob, branch_adjacents, False, set()):
                return True
        
        self.__priority_index -= 1
        return False
    
    def branch(self, whitelist: set, blacklist: set, blob: set, adjacents: list[set[int]], just_reset: bool = False, current_branching: set = set()) -> bool:
        '''
        Internal Recursive Function, subfunction of fast_inital_mapping

        :param whitelist: all edges we can branch to
        :param blacklist: set of all edges we will not allow branching to. includes previous possibilities and any set part of the origin blob
        :param blob: the remaining set of orgin edges (defined somewhere else) that we can theoretically branch to
        :param adjacents: the remain list of sets of adjacent blob edges to mappings of adjacent H edges (we want this to eventually become empty)
        :param just_reset: True if our previous move was to reset the whitelist, otherwise False
        :param current_branching: all edges in G we have branched to since we last reset the whitelist
        '''

        # writing to our list of possibilities
        if (not just_reset) and len(adjacents) == 0 and len(self.__H.hyperedge_sets[self.__priority[self.__priority_index]]) <= len(self.__edge_node_mapping[self.__priority[self.__priority_index]]):
            if self.immerse_next_edge():
                return True
        
        # Recursion calls
        if self.__depth > self.__merges:

            # reseting part
            if len(current_branching) > 0:
                new_blacklist = blacklist | whitelist
                new_whitelist = set()
                for hyperedge in current_branching:
                    new_whitelist |= self.__G.edge_adjacency[hyperedge]
                new_whitelist -= new_blacklist
                new_whitelist &= self.__G_free_edges
                if len(new_whitelist) > 0:
                    if self.branch(new_whitelist, new_blacklist, blob, adjacents, True, set()):
                        return True

            while len(whitelist) > 0:
                hyperedge = whitelist.pop()
                blacklist.add(hyperedge)
                self.add_G_edge(hyperedge)
                if hyperedge in blob:
                    new_blob = blob - {hyperedge,}
                    new_adjacents = []
                    for s in adjacents:
                        if not (hyperedge in s):
                            new_adjacents.append(s)
                else:
                    new_blob = blob
                    new_adjacents = adjacents
                if self.branch(whitelist.copy(), blacklist.copy(), new_blob, new_adjacents, False, current_branching | {hyperedge,}):
                    return True
        if not just_reset:
            self.revert()
        return False