
from networkx import Graph
from networkx import draw

class hypergraph:

    # nodes and edges are numbered with non - negative integers
    def __init__(self, nodes: set = set(), edges: dict = dict()) -> None:
        '''
        :param nodes: the set of all nodes in the hypergraph. All nodes are labeled with unique non-negative integers.
        :param edges: a dictionary whose keys are the hyperedge labels (unique non-negative integers) and whose objects are sets of nodes that the hyperedge contains.
        '''
        self.nodes = nodes.copy() # set of all node labels

        self.hyperedges = set(edges.keys()).copy() # set of all edge labels

        self.node_sets = dict() # dictionary with the node labels as keys which link to the set of hyperedges that contains that node

        for node in self.nodes:
            self.node_sets[node] = set()
        
        self.hyperedge_sets = dict() # dictionary with hyperedge labels as keys which link to the set of nodes that the hyperedge contains

        for hyperedge in self.hyperedges:
            self.hyperedge_sets[hyperedge] = edges[hyperedge].copy()
            for node in edges[hyperedge]:
                self.node_sets[node].add(hyperedge)

        self.hyperedge_count = len(self.hyperedges)
        self.node_count = len(self.nodes)

        self.hyperedge_graph = self.graph_hyperedges()

        self.edge_adjacency = self.initiate_adjacency()
        pass

    @classmethod
    def read(cls, string: str):
        '''
        Reads off of an encoded string to get a hypergraph

        :param string: the encoded string
        '''

        def read_binary(bitstring: str) -> int:
            power = 1
            number = 0
            for i in bitstring[0:-1]:
                if i == "1":
                    number += power
                power *= 2
            if bitstring[-1] == "1":
                number += power
            return number

        n = 1
        while string[n] != "-":
            n += 1
        
        bitcount = read_binary(string[0:n])

        hyperedge_number = 0
        nodes = set()
        edges = dict()
        read_bits = set()
        bits_to_numbers = dict()

        for hyperedge_string in string[n + 1:].split("."):
            edges[hyperedge_number] = set()
            mutiple = 0
            while mutiple < len(hyperedge_string):
                node_bit = hyperedge_string[mutiple:mutiple + bitcount]
                if node_bit not in read_bits:
                    read_bits.add(node_bit)
                    bits_to_numbers[node_bit] = read_binary(node_bit)
                    nodes.add(bits_to_numbers[node_bit])
                edges[hyperedge_number].add(bits_to_numbers[node_bit])
                mutiple += bitcount
            hyperedge_number += 1
        
        return cls(nodes, edges)



    
    # internal function
    def graph_hyperedges(self) -> Graph:
        hyperedge_graph = Graph()
        hyperedge_graph.add_nodes_from(self.hyperedges)
        remaining_hyperedges = self.hyperedges.copy()
        adjacent_edges = set()
        while len(remaining_hyperedges) > 1:
            hyperedge = remaining_hyperedges.pop()
            adjacent_edges.clear()
            for node in self.hyperedge_sets[hyperedge]:
                adjacent_edges |= self.node_sets[node]
            adjacent_edges &= remaining_hyperedges
            for adjacent_edge in adjacent_edges:
                hyperedge_graph.add_edge(hyperedge, adjacent_edge)
        return hyperedge_graph

    # internal function
    def initiate_adjacency(self) -> dict:
        adjacency = dict()
        for edge1 in self.hyperedges:
            adjacency[edge1] = set()
            for edge2 in self.hyperedges - {edge1,}:
                if len(self.hyperedge_sets[edge1] & self.hyperedge_sets[edge2]) > 0:
                    adjacency[edge1].add(edge2)
        return adjacency
    
    # adds the node and returns the integer label for the node
    # the edges are all the edges you want the node to connect to
    def add_node(self, edges: set = set()) -> int:
        '''
        :param edges: set of all edges that contain the new node
        '''
        self.node_count += 1
        node = 0
        if len(self.nodes) > 0:
            node = max(self.nodes) + 1
        self.nodes.add(node)
        self.node_sets[node] = edges.copy()
        for edge in edges:
            if edge in self.hyperedges:
                self.hyperedge_sets[edge].add(node)
                for hyperedge in edges - (self.edge_adjacency[edge] | {edge,}):
                    self.hyperedge_graph.add_edge(hyperedge, edge)
                self.edge_adjacency[edge] |= edges - {edge,}
            else:
                self.hyperedge_sets[edge] = {node,}
                self.hyperedge_graph.add_node(edge)
                for hyperedge in edges - {edge,}:
                    self.hyperedge_graph.add_edge(hyperedge, edge)
                self.edge_adjacency[edge] = edges - {edge,}
                self.hyperedge_count += 1
        self.hyperedges |= edges
        return node
    
    # adds the edge and returns the integer label for the edge
    # the nodes are all the nodes you want the edge to contain
    def add_edge(self, nodes: set) -> int:
        '''
        :param nodes: the set of all nodes contained in the new hyperedge
        '''
        self.hyperedge_count += 1
        edge = 0
        if len(self.hyperedges) > 0:
            edge = max(self.hyperedges) + 1
        self.hyperedges.add(edge)
        self.hyperedge_sets[edge] = nodes.copy()
        self.edge_adjacency[edge] = set()
        self.hyperedge_graph.add_node(edge)
        for node in nodes:
            if node in self.nodes:
                for hyperedge in self.node_sets[node] - self.edge_adjacency[edge]:
                    self.hyperedge_graph.add_edge(hyperedge, edge)
                    self.edge_adjacency[hyperedge].add(edge)
                self.edge_adjacency[edge] |= self.node_sets[node]
                self.node_sets[node].add(edge)
            else:
                self.node_count += 1
                self.node_sets[node] = {edge,}
        self.nodes |= nodes
        return edge
    
    def copy(self):
        nodes = self.nodes.copy()
        edges = dict()
        for edge in self.hyperedges:
            edges[edge] = self.hyperedge_sets[edge].copy()
        return hypergraph(nodes, edges)
    
    def remove_node(self, node: int) -> None:
        '''
        :param node: the node you want to remove. does nothing if the node is not in the hypergraph
        '''
        if node in self.nodes:
            self.node_count -= 1
            self.nodes.remove(node)
            effected_edges = list(self.node_sets[node].copy())
            del self.node_sets[node]
            for i in range(len(effected_edges)):
                self.hyperedge_sets[effected_edges[i]].remove(node)
                for j in range(i):
                    if len(self.hyperedge_sets[effected_edges[i]] & self.hyperedge_sets[effected_edges[j]]) == 0:
                        self.edge_adjacency[effected_edges[i]].remove(effected_edges[j])
                        self.edge_adjacency[effected_edges[j]].remove(effected_edges[i])
                        self.hyperedge_graph.remove_edge(effected_edges[i], effected_edges[j])      
        pass

    def remove_edge(self, edge: int) -> None:
        '''
        :param edge: the hyperedge you want to remove
        '''
        if edge in self.hyperedges:
            self.hyperedge_count -= 1
            self.hyperedges.remove(edge)
            for node in self.hyperedge_sets[edge]:
                self.node_sets[node].remove(edge)
            del self.hyperedge_sets[edge]
            for adjacent_edge in self.edge_adjacency[edge]:
                self.edge_adjacency[adjacent_edge].remove(edge)
            del self.edge_adjacency[edge]
            self.hyperedge_graph.remove_node(edge)
        pass

    # subgraph is a set of edges
    def is_connected(self, subgraph: set) -> bool:
        '''
        :param subgraph: a set of hyperedges in the hypergraph
        '''
        if len(subgraph) == 0:
            return False
        sub_graph = subgraph.copy()
        edge = sub_graph.pop()
        cluster = self.edge_adjacency[edge] & sub_graph
        while len(cluster) > 0:
            connected_edge = cluster.pop()
            sub_graph.remove(connected_edge)
            cluster |= (sub_graph & self.edge_adjacency[connected_edge])
        return len(sub_graph) == 0
    
    def subgraph_nodes(self, subgraph: set) -> set[int]:
        '''
        :param subgraph: a set of hyperedges in the hypergraph
        '''
        nodes = set()
        for hyperedge in subgraph:
            nodes |= self.hyperedge_sets[hyperedge]
        return nodes
    
    def __str__(self):
        return str(self.hyperedge_sets)
    
    def __ge__(self, o) -> bool:
        return self.node_count >= o.node_count and self.hyperedge_count >= o.hyperedge_count
    
    def __le__(self, o) -> bool:
        return self.node_count <= o.node_count and self.hyperedge_count <= o.hyperedge_count

    # I did not know what else to call this function
    def skim(self) -> None:
        '''
        This function removes identical edges, edges containing only one node (i.e. loops), and empty edges, then nodes that are connected to no edges
        '''

        # removing identical edges (always removes the one with the higher index)
        edge_list = list(self.hyperedges.copy())
        removal_set = set()
        for i in range(len(edge_list)):
            for j in range(i):
                if self.hyperedge_sets[edge_list[i]] == self.hyperedge_sets[edge_list[j]]:
                    removal_set.add(max(edge_list[i], edge_list[j]))
        
        for edge in removal_set:
            self.remove_edge(edge)
        
        # removing edges that are empty on only conatain one node
        former_edge_set = self.hyperedges.copy()
        for edge in former_edge_set:
            if len(self.hyperedge_sets[edge]) <= 1:
                self.remove_edge(edge)

        # removing all nodes with no edges connected to them (this must be done last)
        former_node_set = self.nodes.copy()
        for node in former_node_set:
            if len(self.node_sets[node]) == 0:
                self.remove_node(node)
        
        pass

    # does not check for isomorphism, just checks if they are the same (i.e. same node + edge labels with the same connections)
    def __eq__(self, o) -> bool:
        if self.hyperedges == o.hyperedges:
            for hyperedge in self.hyperedges:
                if self.hyperedge_sets[hyperedge] != o.hyperedge_sets[hyperedge]:
                    return False
            return self.nodes == o.nodes
        return False
    
    def __ne__(self, o):
        return not self == o
    
    def draw_hyperedge_graph(self) -> None:
        draw(self.hyperedge_graph)
        pass

    def get_weighted_graph(self) -> Graph:
        weighted_graph_dictionary = dict()
        for hyperedge in self.hyperedges:
            if len(self.hyperedge_sets[hyperedge]) > 1:
                sorted_list = sorted(self.hyperedge_sets[hyperedge])
                for i in range(1, len(sorted_list)):
                    for j in range(i):
                        if (i, j) in weighted_graph_dictionary.keys():
                            weighted_graph_dictionary[(i, j)] += 1
                        else:
                            weighted_graph_dictionary[(i, j)] = 1
        G = Graph()
        G.add_nodes_from(self.nodes)
        for pair in weighted_graph_dictionary.keys():
            #G.add_edge(pair[0], pair[1], weight = weighted_graph_dictionary[pair])
            G.add_edge(*pair)
        return G
    
    def get_factor_graph(self) -> Graph:
        F = Graph()
        for hyperedge in self.hyperedges:
            F.add_node(-1 * hyperedge - 1)
            for node in self.hyperedge_sets[hyperedge]:
                F.add_edge(node, -1 * hyperedge - 1)
        return F
    
    def largest_edge(self, subgraph: set[int], use_copy: bool = True) -> int:
        '''
        :param subgraph: a set of edges in the hypergraph
        :param use_copy: if false, this function will modify the imputted set
        '''

        if len(subgraph) == 0:
            raise ValueError("Does work with empty sets.")

        if use_copy:
            hyperedges = subgraph.copy()
        else:
            hyperedges = subgraph
        
        largest_hyperedge = hyperedges.pop()
        for hyperedge in hyperedges:
            if len(self.hyperedge_sets[hyperedge]) > len(self.hyperedge_sets[largest_hyperedge]):
                largest_hyperedge = hyperedge
        return largest_hyperedge
    
    def cluster(self, subgraph: set[int]) -> list[set[int]]:
        '''
        :param subgraph: a set of edges in the hypergraph
        '''

        hyperedges = subgraph.copy()

        clusters = []
        while len(hyperedges) > 0:
            cluster = {hyperedges.pop(),}
            cluster_border = cluster.copy()
            while len(cluster_border) > 0:
                additions = self.edge_adjacency[cluster_border.pop()] & hyperedges
                hyperedges -= additions
                cluster_border |= additions
                cluster |= additions
            clusters.append(cluster)
        return clusters
    
    def average_connectivity(self, show: bool = False) -> float:
        '''
        Takes the average amount of hyperedges adjacent to a given hyperedge

        :param show: if True, it will print out a statement
        '''

        total_connections = 0
        for hyperedge in self.hyperedges:
            total_connections += len(self.edge_adjacency[hyperedge])
        average_connections = float(total_connections / self.hyperedge_count)

        if show:
            if self.hyperedge_count > 1:
                print("Average amount of adjacent hyperedges per a hyperedge:", average_connections)
                print("Total amount of hyperedges:", self.hyperedge_count)
                print("Thus on average, a hyperedge is connected to {:.3f}% of other hyperedges".format(100 * average_connections / (self.hyperedge_count - 1)))
            else:
                print("There is only one hyperedge, thus this analysis does not apply.")
        
        return average_connections
    
    def transform_hyperedge(self, hyperedge: int, new_assignment: int) -> None:
        '''
        Meant for turning one hyperedge assignment into another (which cannot already be there)

        :param hyperedge: a hyperedge inside the hypergraph
        :param new_assignment: a new assignment that is NOT inside the hypergraph
        '''

        if hyperedge not in self.hyperedges:
            if new_assignment in self.hyperedges:
                raise ValueError("Attempted to reassign a non existant hyperedge (", hyperedge, ") to an already existing one(", new_assignment, ").", sep = "")
            raise ValueError("Cannot reassign a nonexistant hyperedge.", hyperedge, "is not in this hypergraph.")
        elif new_assignment in self.hyperedges:
            raise ValueError("A hyperedge cannot be reassigned to a value already assigned to another hyperedge.", new_assignment, "has already been assigned to another hyperedge.")
        
        self.hyperedges.remove(hyperedge)
        self.hyperedges.add(new_assignment)
        for node in self.hyperedge_sets[hyperedge]:
            self.node_sets[node].remove(hyperedge)
            self.node_sets[node].add(new_assignment)
        
        self.hyperedge_sets[new_assignment] = self.hyperedge_sets.pop(hyperedge)

        self.hyperedge_graph.remove_node(hyperedge)
        self.hyperedge_graph.add_node(new_assignment)

        for edge in self.edge_adjacency[hyperedge]:
            self.edge_adjacency[edge].remove(hyperedge)
            self.edge_adjacency[edge].add(new_assignment)
            self.hyperedge_graph.add_edge(new_assignment, edge)
        
        self.edge_adjacency[new_assignment] = self.edge_adjacency.pop(hyperedge)

        pass


    def transform_node(self, node: int, new_assignment: int) -> None:
        '''
        Meant for turning one node assignment into another (which cannot already be there)

        :param node: a node inside the hypergraph
        :param new_assignment: a new assignment that is NOT inside the hypergraph
        '''

        if node not in self.nodes:
            if new_assignment in self.nodes:
                raise ValueError("Attempted to reassign a non existant node (", node, ") to an already existing one (", new_assignment, ").", sep = "")
            raise ValueError("Cannot reassign a nonexistant node.", node, "is not in this hypergraph.")
        elif new_assignment in self.nodes:
            raise ValueError("A node cannot be reassigned to a value already assigned to another node.", new_assignment, "has already been assigned to another node.")
        
        self.nodes.remove(node)
        self.nodes.add(new_assignment)

        for hyperedge in self.node_sets[node]:
            self.hyperedge_sets[hyperedge].remove(node)
            self.hyperedge_sets[hyperedge].add(new_assignment)
        
        self.node_sets[new_assignment] = self.node_sets.pop(node)

        pass

    def minimize_assignments(self) -> None:
        '''
        Just makes sure all nodes and hyperedges are assigned efficiently
        '''

        # nodes

        backdistance = 0
        MAX = max(self.nodes)

        for n in range(MAX + 1):
            if n in self.nodes:
                if backdistance > 0:
                    self.transform_node(n, n - backdistance)
            else:
                backdistance += 1
        
        backdistance = 0
        MAX = max(self.hyperedges)

        for n in range(MAX + 1):
            if n in self.hyperedges:
                if backdistance > 0:
                    self.transform_hyperedge(n, n - backdistance)
            else:
                backdistance += 1
        
        pass

    def store(self, sort: bool = False) -> str:
        '''
        converts the hypergraph into a decodeable string of the following format [# of bits per node in binary]-[hyperedge].[another hyperedge]...
        hyperedes are lists of nodes (in binary) with no parsing, just uses the amount of bits per a node to decern what node is what.

        :param sort: If true, it will insure that the hyperedges are sorted before being listed in the string
        '''

        def bitcount(n: int) -> int:
            '''
            :param n: a non negative integer
            '''
            count = 1
            MAX = 2
            while MAX <= n:
                count += 1
                MAX *= 2
            return count

        def binary(n: int, bitcount: int) -> str:
            '''
            Note: higher signifigant digits are to the right (2 = 01 not 10 in this form)

            :param n: the number
            :param bitcount: the number of bits
            '''

            bitstring = ""
            for i in range(bitcount):
                if n % 2 == 1:
                    bitstring += "1"
                else:
                    bitstring += "0"
                n //= 2
            return bitstring
        
        node_bitcount = bitcount(max(self.nodes))
        nodes_to_bits = dict()
        for node in self.nodes:
            nodes_to_bits[node] = binary(node, node_bitcount)

        if sort:
            hyperedges = sorted(list(self.hyperedges.copy()))
        else:
            hyperedges = self.hyperedges
        
        string = "-"
        first = True
        for hyperedge in hyperedges:
            if not first:
                string += "."
            first = False
            for node in self.hyperedge_sets[hyperedge]:
                string += nodes_to_bits[node]
        
        del nodes_to_bits
        
        return binary(node_bitcount, bitcount(node_bitcount)) + string
    
    def coalesce(self, subgraph: set[int]) -> int:
        '''
        Merges two adjacent hyperedges
        Returns the new hyperedge

        :param subgraph: a set of hyperedges, this subgraph must be connected
        '''

        # things I need to worry about
        # self.hyperedges, self.hyperedge_count, self.node_sets, self.hyperedge_sets, self.hyperedge_graph, self.edge_adjacency

        merged_hyperedge = subgraph.pop()

        # hyperedge_graph and edge_adjacency
        new_neighbors = set()
        for hyperedge in subgraph:
            new_neighbors |= self.edge_adjacency.pop(hyperedge)
            self.hyperedge_graph.remove_node(hyperedge)

            # for hyperedge_sets
            self.hyperedge_sets[merged_hyperedge] |= self.hyperedge_sets.pop(hyperedge)
        new_neighbors -= subgraph
        new_neighbors.discard(merged_hyperedge)

        for hyperedge in new_neighbors:
            self.edge_adjacency[hyperedge] -= subgraph
            self.edge_adjacency[hyperedge].add(merged_hyperedge)
        self.edge_adjacency[merged_hyperedge] -= subgraph

        new_neighbors -= self.edge_adjacency[merged_hyperedge]
        self.edge_adjacency[merged_hyperedge] |= new_neighbors
        
        for hyperedge in new_neighbors:
            self.hyperedge_graph.add_edge(merged_hyperedge, hyperedge)

        # node_sets
        for node in self.hyperedge_sets[merged_hyperedge]:
            self.node_sets[node] -= subgraph
            self.node_sets[node].add(merged_hyperedge)
        
        self.hyperedge_count -= len(subgraph)
        self.hyperedges -= subgraph

        return merged_hyperedge