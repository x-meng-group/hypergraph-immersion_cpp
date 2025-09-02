from Vector import vector
from Hypergraph import hypergraph
import random
from networkx import spring_layout
from networkx import Graph
from Segment import segment
import numpy as np


class scatter:

    def __init__(self, vertex_dict: dict[any, vector]):
        '''
        This is mostly called internally

        :param vertex_dict: a dictionary that maps vertex labels to points on 2D space
        '''

        self.__labels = set(vertex_dict.keys())
        self.__labels_to_vertices = vertex_dict

        pass

    def __len__(self) -> int:
        return len(self.__labels)
    
    def __getitem__(self, label: any) -> vector:
        return self.__labels_to_vertices[label]
    
    def __setitem__(self, label: any, object: vector) -> None:
        self.__labels.add(label)
        self.__labels_to_vertices[label] = object
        pass

    def image(self, key: any) -> list:
        '''
        This function takes in either a universal attribiute (across all vectors) or a set (or list or range) of node labels.
        The former returns a list of all of the attributes and the ladder returns a list of all vectors in the set of nodes.
        Note that this list is NOT sorted in any manner in either case

        :param key: the attribute or itterable input
        '''

        if type(key) == list or type(key) == set or type(key) == range:
            vectors = []
            for n in key:
                vectors.append(self[n].copy())
            return vectors
        
        objects = []
        for v in self:
            objects.append(v[key])
        
        return objects


    def labels(self, copy: bool = True) -> set:
        '''
        Returns a set of all of the labels

        :param copy: if True, the set is first copied
        '''

        if copy:
            return self.__labels.copy()
        return self.__labels
    
    def __iter__(self):
        for label in sorted(self.__labels.copy()):
            yield self.__labels_to_vertices[label]
        pass

    def pop(self, label: any) -> vector:
        '''
        Removes the label from the scatter and returns it's corosponding vector

        :param label: the label being removed
        '''

        self.__labels.remove(label)
        return self.__labels_to_vertices.pop(label)
    
    def __contains__(self, label: any) -> bool:
        '''
        Returns true only if the label is one of the labels in the scatter

        :param label: the label in question
        '''

        return label in self.__labels
    
    def __str__(self):
        if len(self) < 1:
            return "{empty scatter}"
        s = "{"
        L = list(sorted(self.labels()))
        label = L.pop(0)
        s += str(label) + ": " + str(self.__labels_to_vertices[label])
        for l in L:
            s += ", " + str(l) + ": " + str(self.__labels_to_vertices[label])
        return s + "}"
    
    def shift(self, v: vector):
        plot = scatter(dict())
        for label in self.labels():
            plot[label] = self[label] + v
        return plot
    
    def all_set_attribite(self, attribute: any, object: any, apply_copy: bool = False) -> None:
        '''
        Assigns an attribute - object pair to all vectors in a scatter

        :param attribute: the attribute (must be a hashable type)
        :param object: any object in which the attribute links to.
        :param apply_copy: if True, a copy is applied rather than the original. The .copy() method must exist for the object type
        '''

        for v in self:
            if apply_copy:
                v[attribute] = object.copy()
            else:
                v[attribute] = object
        
        pass

    def find_clearances(self, max_allowed_clearance: int | float, clearance_param: any = "clearance") -> None:
        '''
        Find's the min distance to another point for every point

        :param max_allowed_clearance: the max clearance value allowed
        :param clearance_param: the paramiter for clearance
        '''

        max_clearance = max_allowed_clearance**2
        L = list(self.__labels.copy())
        for i in range(len(L)):
            self[L[i]][clearance_param] = max_clearance
            for j in range(i):
                difference = self[L[i]] - self[L[j]]
                clearance = (difference["x"]**2) + (difference["y"]**2)
                if clearance < self[L[i]][clearance_param]:
                    self[L[i]][clearance_param] = clearance
                if clearance < self[L[j]][clearance_param]:
                    self[L[j]][clearance_param] = clearance
        
        for v in self:
            v[clearance_param] **= 1/2
        
        pass
    
    def create_vertex_list(self, attributes: dict) -> list[vector]:
        '''
        This function creates a list of all points and assigns attributes. Vertices are sorted in acending order by label in the hypergraph

        :param attributes: a dictionary containing all attributes and what they are, which will be mapped onto all vectors
        '''

        vertices = []

        for v in self:
            vertex = v.copy()
            vertex.set_attributes_from(attributes)
            vertices.append(vertex)
        return vertices
    
    def copy(self):
        '''
        Creates a copy of the scatter
        '''

        vertex_dict = dict()
        for n in self.__labels:
            vertex_dict[n] = self.__labels_to_vertices[n].copy()
        return scatter(vertex_dict)
    
    def strip(self) -> None:
        '''
        Strips all attributes in all vectors
        '''

        for v in self:
            v.strip()
        
        pass

    def stripcopy(self):
        '''
        Creates a stripped copy of the scatter
        '''

        new_scatter = self.copy()
        new_scatter.strip()
        return new_scatter
    
    def get_line_node_layout(self, G: hypergraph, line: segment):
        '''
        This function is highly specific. it is meant for getting a node layout from a hyperedge line layout

        :param G: the hypergraph (a copy is fine) that the line hyperedge layout was derived from
        :param line: a line parellel to the line used for deriving the hyperedge layout
        '''

        i_hat = (line["v"] - line["u"]) / G.node_count

        hyperedge_i_values = dict() # maps hyperedges to locations along the line in i value
        for hyperedge in self.__labels:
            hyperedge_i_values[hyperedge] = self[hyperedge] * i_hat
        
        node_tuples = []
        for node in G.nodes:
            i_total = 0
            for hyperedge in G.node_sets[node]:
                i_total += hyperedge_i_values[hyperedge]
            node_tuples.append((i_total / len(G.node_sets[node]), node))

        del hyperedge_i_values

        node_tuples.sort()
        vertex_dict = dict()

        v = line["u"] + (i_hat / 2)
        for tup in node_tuples:
            vertex_dict[tup[1]] = v
            v += i_hat
        
        del node_tuples
        return scatter(vertex_dict)
    
    # a method for aquiring all layout based initiation methods with their string indicators

    @classmethod
    def layout_methods(cls) -> None:
        '''
        This function just prints out a guide to all layout methods
        '''

        print(
            '''
            Specific Layout Methods:
            (these should be inputted as a string for in the method paramiter for the scatter.layout()))

            "random": 
            a random layout of nodes where each node has a vector of randomized x and y values between -1 and 1

            "factor_graph_spring_layout": 
            spring layout of the factor graph

            "sorted_circle": 
            creates a circle where nodes are sorted in assigment number by angle (around (0, 0) and radius 1))
            '''
        )

        pass

    @classmethod
    def hyperedge_layout_methods(cls) -> None:
        '''
        This function just prints out a guide to all layout methods
        '''

        print(
            '''
            Specific Layout Methods:
            (these should be inputted as a string for in the method paramiter for the scatter.layout()))
            These options are for drawing graphs/hypergraphs with hyperedges as nodes.

            "random": 
            a random layout of hyperedges where each node has a vector of randomized x and y values between -1 and 1

            "hyperedge_adjacency_graph_spring_layout": 
            spring layout of the hyperedge adjacency graph

            "sorted_circle": 
            creates a circle where hyperedges are sorted in assigment number by angle (around (0, 0) and radius 1))
            '''
        )

        pass
    
    # all initiation methods

    # the "general" initiation method

    @classmethod
    def layout(cls, G: hypergraph, method: str):
        '''
        This is the general initiation method for layouts

        :param G: the hypergraph
        :param method: a string which defines the method of gathering the layout

        Specific methods: \n
        "random": a random layout of nodes where each node has a vector of randomized x and y values between -1 and 1 \n
        "factor_graph_spring_layout": spring layout of the factor graph
        "sorted_circle: creates a circle where nodes are sorted in assigment number by angle (around (0, 0) and radius 1)
        '''

        function = method.lower().strip()

        if function == "random":
            return cls.random_layout(G, "vertex")
        elif function == "factor_graph_spring_layout":
            return cls.factor_graph_spring_layout(G)
        elif function == "sorted_circle":
            return cls.sorted_circle(G, "vertex")
        raise ValueError(method, "is not a proper layout method.")
    

    @classmethod
    def hyperedge_layout(cls, G: hypergraph, method: str):
        '''
        This is the general initiation method for layouts

        :param G: the hypergraph
        :param method: a string which defines the method of gathering the layout

        Specific methods: \n
        "random": a random layout of hyperedges where each node has a vector of randomized x and y values between -1 and 1 \n
        "hyperedge_adjacency_graph_spring_layout": spring layout of the hyperedge adjacency graph
        "sorted_circle: creates a circle where hyperedges are sorted in assigment number by angle (around (0, 0) and radius 1)
        '''

        function = method.lower().strip()

        if function == "random":
            return cls.random_layout(G, "hyperedge")
        elif function == "hyperedge_adjacency_graph_spring_layout":
            return cls.hyperedge_adjacency_graph_spring_layout(G)
        elif function == "sorted_circle":
            return cls.sorted_circle(G, "hyperedge")
        raise ValueError(method, "is not a proper layout method.")


    # "specific" initiation methods
    # these initiation methods take in one input, which is the hypergraph

    @classmethod
    def factor_graph_spring_layout(cls, G: hypergraph):
        '''
        Aquires the node layout via a spring_layout of the factor graph

        :param G: the hypergraph
        '''

        layout = spring_layout(G.get_factor_graph()) # spring layout
        # Note, hyperedge numeric labels were negated (and had 1 subtracted to avoid issues with hyperedge 0)
        # Thus we just have to filter out the negative labels

        vertex_dict = dict() # dictionary of all verticies to vector locations

        for key in layout.keys(): # itterating through all keys in the dictionary
            if key >= 0:
                vertex_dict[key] = vector(float(layout[key][0]), float(layout[key][1]))
        
        return cls(vertex_dict) # making the scatter
    
    @classmethod
    def random_layout(cls, G: hypergraph, type: str = "vertex"):
        '''
        This function just gets a random layout for the verticies where each vertex can be between -1 and 1 exculusive

        :param G: the hypergraph
        '''

        vertex_dict = dict()

        if type == "vertex":
            nodes = G.nodes
        elif type == "hyperedge":
            nodes = G.hyperedges
        else:
            raise ValueError("type must be vertex or hyperedge.")

        # all nodes in G
        for node in nodes:
            # generating a randomized vector
            vertex_dict[node] = vector(float(random.choice([-1, 1]) * random.random()), float(random.choice([-1, 1]) * random.random()))
        
        return cls(vertex_dict)
    
    @classmethod
    def sorted_circle(cls, G: hypergraph, type: str = "vertex"):
        '''
        retruns a layout of points evenly spaces in a circle of radius 1 sorted in acending label order
        '''

        vertex_dict = dict()

        if type == "vertex":
            nodes = G.nodes
        elif type == "hyperedge":
            nodes = G.hyperedges
        else:
            raise ValueError("type must be vertex or hyperedge.")

        if len(nodes) == 0:
            return cls(vertex_dict)

        r_hat = vector(1, 0)
        sorted_nodes = list(sorted(nodes.copy()))

        delta_theta = float(2 * np.pi / len(nodes))

        first_node = sorted_nodes.pop(0)
        vertex_dict[first_node] = r_hat
        
        for node in sorted_nodes:
            r_hat = r_hat.rotate(delta_theta)
            vertex_dict[node] = r_hat
        
        return cls(vertex_dict)
    
    # special initiation functions
    # ones that require more paramiters

    @classmethod
    def hyperedge_line_layout(cls, 
                              G: hypergraph, 
                              line: segment,
                              sep_pow: float | int = 1/4
                              ):
        '''
        Places hyperedges in a lineup along the segment (from u to v)

        :param G: the hypergraph
        :param line: the line segment
        :param sep_pow: used to adjust scaling by size of hyperedge
        '''

        # Getting an edge priority for G
        G_tuples = []
        for hyperedge in G.hyperedges:
            G_tuples.append((len(G.edge_adjacency[hyperedge]), len(G.hyperedge_sets[hyperedge]), hyperedge))
        G_tuples.sort()
        G_edge_priority = []
        for array in G_tuples:
            G_edge_priority.append(array[2])
        
        del G_tuples


        # ordering the hyperedges
        hyperedge_order = [G_edge_priority[0]]
        index = 0
        for hyperedge in G_edge_priority[1:]:
            index += 1
            left_sum = 0
            right_sum = 0
            for i in range(index):
                n = len(G.hyperedge_sets[hyperedge] & G.hyperedge_sets[hyperedge_order[i]])
                left_sum += (i + 1) * n
                right_sum += (index - i) * n
            if left_sum < right_sum:
                hyperedge_order.insert(0, hyperedge)
            else:
                hyperedge_order.append(hyperedge)
        
        # Now translating that into hyperedge locations

        i_hat = (line["v"] - line["u"]).unit()


        G_hyperedge_locations = dict()

        widths = []
        for hyperedge in hyperedge_order:
            widths.append(len(G.hyperedge_sets[hyperedge])**sep_pow)
        multiplier = abs(line) / (2 * sum(widths))
        loc_sum = line["u"].strip()
        for index in range(G.hyperedge_count):
            delta_width = (widths[index] * multiplier) * i_hat
            loc_sum += delta_width
            G_hyperedge_locations[hyperedge_order[index]] = loc_sum.strip()
            G_hyperedge_locations[hyperedge_order[index]]["width"] = 2 * widths[index] * multiplier  # used to get the widths if applicable
            loc_sum += delta_width
        

        return cls(G_hyperedge_locations)
    
    @classmethod
    def hyperedge_adjacency_graph_spring_layout(cls, G: hypergraph):
        '''
        This gathers the spring layout of the hyperedge adjacency graph.
        '''

        layout = spring_layout(G.hyperedge_graph) # spring layout

        vertex_dict = dict() # dictionary of all verticies to vector locations

        for key in layout.keys(): # itterating through all keys in the dictionary
            vertex_dict[key] = vector(float(layout[key][0]), float(layout[key][1]))
        
        return cls(vertex_dict) # making the scatter