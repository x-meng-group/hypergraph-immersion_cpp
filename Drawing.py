from Immersion import immersion
from Hypergraph import hypergraph
from Immersion_function import immersion_function
from Hypergraph_randomizer import hypergraph_ramdomizer
from networkx import draw
from networkx import spring_layout
import matplotlib.pyplot as plt
from networkx import Graph
from Vector import vector
from Polygon import polygon
from Segment import segment
from Sorted_array import sorted_array
import numpy as np
from Scatter import scatter


class drawing:

    def __init__(self, points: list[vector], polygons: list[polygon], arrows: list[segment]):
        self.__hyperedges = polygons.copy()
        self.__nodes = points.copy()
        self.__arrows = arrows.copy()
        # arrows must have the following attributes: "shavelength", "arrowhead_length", "arrowhead_width", "thickness", "opacity", "color", and "zorder" 
        # Note: all nodes must have the following attributes: "color", "opacity", "radius", "zorder" (for what goes on top or bottom)
        # All hyperedge polygons must have the following attributes: "color", "opacity", "edge_width", "edge_type", "zorder"
        # these arributes will be stored in the base (u) of the arrow for easy access

        # defaults:
        # hyperedges:
        #   edge_width = 0
        #   edge_type = "solid"
        # nodes:
        #   radius = 0.01
        # arrows:
        #   shavelength = 0
        #   arrowhead_length = 0
        #   arrowhead_width = 0
        #   thickness = 0.01
        # all:
        #   opacity = 1
        #   color = "black"
        #   zorder = 1
        # vertices of hyperedges:
        #   curve: (non existant)
        #   curve_type: None

        self.defaults()

        pass

    def defaults(self) -> None:
        '''
        This function ensures that all internal objects have the required attributes
        '''

        # hyperedges (polygons)
        for hyperedge in self.__hyperedges:
            for index in range(5):
                attribute = ["edge_width", "edge_type", "color", "opacity", "zorder"][index]
                if not attribute in hyperedge.attributes():
                    hyperedge[attribute] = [0, "solid", "black", 1, 1][index]
            for vertex in hyperedge.verticies():
                if "curve" in vertex.attributes() and "curve_type" not in vertex.attributes():
                    l = len(vertex["curve"])
                    if l < 3:
                        vertex["curve_type"] = None
                    else:
                        vertex["curve_type"] = "bezier"
                elif "curve" not in vertex.attributes():
                    vertex["curve_type"] = None
        
        # nodes
        for node in self.__nodes:
            for index in range(4):
                attribute = ["radius", "color", "opacity", "zorder"][index]
                if not attribute in node.attributes():
                    node[attribute] = [0.01, "black", 1, 1][index]
        
        # arrows
        for arrow in self.__arrows:
            for index in range(7):
                attribute = ["shavelength", "arrowhead_length", "arrowhead_width", "thickness", "color", "opacity", "zorder"][index]
                if not attribute in arrow["u"].attributes():
                    arrow["u"][attribute] = [0, 0, 0, 0.01, "black", 1, 1][index]

        pass

    @classmethod
    def draw_hypergraph(cls, 
                        G: hypergraph,
                        layout_method: str = "factor_graph_spring_layout", 
                        max_clearance: float | int = 0.07, 
                        nodes_on_top: bool = True, 
                        hyperedge_border_thickness: int = 0,
                        node_color = "purple",
                        node_opacity: float | int = 0.69,
                        hyperedge_opacity = 0.25, 
                        saturation: int | float = 0.55
                        ):
        '''
        :param G: a hypergraph
        :param layout_method: the method used to generate the layout for the nodes
        :param max_clearance: the max clearance value for any node
        :param nodes_on_top: if true, nodes appear on top of hyperedges
        :param hyperedge_border_thickness: the thickness of the hyperedge border, shows no border if it is zero
        :param node_color: the color of the nodes
        :param node_opacity: the opacity of the nodes
        :param hyperedge_opacity: the opacity of the hyperedges
        :param saturation: the saturation of the color (between 0 and 1)
        '''

        # used for assigning colors
        def color(x, saturation) -> tuple:
            red = 0
            blue = 0
            if x < 0.5:
                red = saturation  * (1 - (2 * x))
            elif x > 0.5:
                blue = saturation * ((2 * x) - 1)
            green = saturation - red - blue
            return (red, green, blue)


        layout = scatter.layout(G, layout_method) # getting node layout

        layout.find_clearances(3 * max_clearance, "clearance") # node clearances
        for v in layout:
            v["clearance"] /= 3
        
        # for coloring hyperedges
        delta = 1 / G.hyperedge_count
        x = delta / 2

        # setting proper zordering for nodes
        z = 1
        if nodes_on_top == True:
            z += 2

        # aquiring the list of all nodes with their required attributes for displaying
        # this must be done first since this list is required for the curvify function of the polygon
        vertices = layout.stripcopy().create_vertex_list({
            "color": node_color,
            "opacity": node_opacity,
            "zorder": z,
            "radius": min(layout.image("clearance"))
            })

        hyperedges = []

        # sorting so that hyperedges are processed in acending order by label
        for hyperedge in sorted(G.hyperedges.copy()):
            
            poly = polygon.create_hyperedge(layout.image(G.hyperedge_sets[hyperedge]),
                                            layout.image(G.nodes - G.hyperedge_sets[hyperedge]),
                                            ) # drawing the hyperedge around the correct nodes
            
            poly.skim(layout.image(G.hyperedge_sets[hyperedge]),
                      layout.image(G.nodes - G.hyperedge_sets[hyperedge])
                      ) # removing any verticies that are not nececary to preserving what is inside and outside

            poly.set_attributes_from({
                "color": color(x, saturation),
                "edge_type": "solid",
                "edge_width": hyperedge_border_thickness,
                "opacity": hyperedge_opacity,
                "zorder": 2,
                "whitelist": layout.image(G.hyperedge_sets[hyperedge]),
                "blacklist": layout.image(G.nodes - G.hyperedge_sets[hyperedge])
            }) # setting all required attributes for display of the polygon

            poly.curvify(vertices) # creating the bezier curves

            hyperedges.append(poly)

            x += delta
        
        arrows = []
        
        return cls(vertices, hyperedges, arrows)


    @classmethod
    def draw_immersion(cls, 
                       alpha: immersion_function,
                       layout_method: str = "factor_graph_spring_layout",
                       max_clearance = 0.07,
                       nodes_on_top: bool = True,
                       H_hyperedge_border_thickness: float | int = 0,
                       G_hyperedge_border_thickness: float | int = 1,
                       node_color = "purple",
                       node_opacity: float | int = 0.69,
                       hyperedge_opacity = 0.25,
                       saturation: int | float = 0.55,
                       clearance_multiplier: float | int = 0.8
                       ):
        '''
        :param alpha: an immersion function (contains the hypergraphs so those don't need to be provided)
        :param layout_method: the method used to generate the layout for the nodes
        :param max_clearance: the max clearance value for any node
        :param nodes_on_top: if true, nodes appear on top of hyperedges
        :param hyperedge_border_thickness: the thickness of the hyperedge border, shows no border if it is zero
        :param node_color: the color of the nodes
        :param node_opacity: the opacity of the nodes
        :param hyperedge_opacity: the opacity of the hyperedges
        :param saturation: the saturation of the color (between 0 and 1)
        :param clearance_multiplier: a multiplier used to ensure that G_hyperedges and H_hyperedges don't cover one another up
        '''

        # used for assigning colors
        def color(x, saturation) -> tuple:
            red = 0
            blue = 0
            if x < 0.5:
                red = saturation  * (1 - (2 * x))
            elif x > 0.5:
                blue = saturation * ((2 * x) - 1)
            green = saturation - red - blue
            return (red, green, blue)

        G = alpha.G()
        H = alpha.H()

        layout = scatter.layout(G, layout_method) # getting the node layout
        copylayout = layout.stripcopy() # we need a second copy of it

        layout.find_clearances(3 * max_clearance, "clearance") # node clearances
        for v in layout:
            v["clearance"] /= 3

                # setting proper zordering for nodes
        z = 1
        if nodes_on_top == True:
            z += 4
        
        # used for assigning proper colors
        copylayout.all_set_attribite("color", "lightgrey")
        for node in H.nodes:
            copylayout[alpha.evaluate("node", node)]["color"] = node_color


        # aquiring the list of all nodes with their required attributes for displaying
        # this must be done first since this list is required for the curvify function of the polygon
        vertices = copylayout.create_vertex_list({
            "opacity": node_opacity,
            "zorder": z,
            "radius": min(layout.image("clearance"))
            })
        
        # for the colors
        delta = 1 / H.hyperedge_count
        x = delta / 2

        hyperedges = []

        unimmersed_G_edges = G.hyperedges.copy()
        
        for H_hyperedge in H.hyperedges:
            contained_G_nodes = G.subgraph_nodes(set(alpha.evaluate("edge", H_hyperedge))) # all G nodes contained
            poly = polygon.create_hyperedge(
                layout.image(contained_G_nodes), 
                layout.image(G.nodes - contained_G_nodes)
                ) # drawing the H hyperedge
            
            poly.skim(layout.image(contained_G_nodes),
                      layout.image(G.nodes - contained_G_nodes)
                      )
            
            Color = color(x, saturation)
            x += delta

            poly.set_attributes_from({
                "color": Color,
                "edge_type": "solid",
                "edge_width": H_hyperedge_border_thickness,
                "opacity": hyperedge_opacity,
                "zorder": 3,
                "whitelist": layout.image(contained_G_nodes),
                "blacklist": layout.image(G.nodes - contained_G_nodes)
            }) # setting all required attributes for display of the polygon

            poly.curvify(vertices) # creating the bezier curves

            hyperedges.append(poly)

            # now for all of the hyperedges in G that we map to
            for G_hyperedge in alpha.evaluate("edge", H_hyperedge):
                unimmersed_G_edges.remove(G_hyperedge)

                poly = polygon.create_hyperedge(layout.image(G.hyperedge_sets[G_hyperedge]),
                                                layout.image(G.nodes - G.hyperedge_sets[G_hyperedge]),
                                                clearance_multiplier = clearance_multiplier
                                                ) # drawing the hyperedge around the correct nodes
            
                poly.skim(layout.image(G.hyperedge_sets[G_hyperedge]),
                          layout.image(G.nodes - G.hyperedge_sets[G_hyperedge])
                          ) # removing any verticies that are not nececary to preserving what is inside and outside

                poly.set_attributes_from({
                    "color": Color,
                    "edge_type": "dashed",
                    "edge_width": G_hyperedge_border_thickness,
                    "opacity": hyperedge_opacity,
                    "zorder": 4,
                    "whitelist": layout.image(G.hyperedge_sets[G_hyperedge]),
                    "blacklist": layout.image(G.nodes - G.hyperedge_sets[G_hyperedge])
                    }) # setting all required attributes for display of the polygon

                poly.curvify(vertices) # creating the bezier curves

                hyperedges.append(poly)
        
        # edges not included in the immersion
        for hyperedge in unimmersed_G_edges:
            poly = polygon.create_hyperedge(layout.image(G.hyperedge_sets[hyperedge]),
                                            layout.image(G.nodes - G.hyperedge_sets[hyperedge]),
                                            clearance_multiplier = clearance_multiplier
                                            ) # drawing the hyperedge around the correct nodes
            
            poly.skim(layout.image(G.hyperedge_sets[hyperedge]),
                      layout.image(G.nodes - G.hyperedge_sets[hyperedge])
                      ) # removing any verticies that are not nececary to preserving what is inside and outside

            poly.set_attributes_from({
                "color": "lightgrey",
                "edge_type": "dashed",
                "edge_width": G_hyperedge_border_thickness,
                "opacity": hyperedge_opacity,
                "zorder": 2,
                "whitelist": layout.image(G.hyperedge_sets[hyperedge]),
                "blacklist": layout.image(G.nodes - G.hyperedge_sets[hyperedge])
            }) # setting all required attributes for display of the polygon

            poly.curvify(vertices) # creating the bezier curves

            hyperedges.append(poly)
        
        arrows = []

        return cls(vertices, hyperedges, arrows)

    @classmethod
    def line_draw_hypergraph(cls, 
                             G: hypergraph,
                             saturation: float | int = 0.55,
                             height: float | int = 2,
                             hyperedge_fill_radius: float | int = 1/4,
                             node_hyperedge_box_multiplier: float | int = 4/3, # a multiplier used for drawing the curve around the nodes
                             hyperedge_zorder: int = 1,
                             node_zorder: int = 2,
                             node_radius: float | int = 1/3,
                             edge_opacity: float | int = 0.45,
                             node_opacity: float | int = 0.5,
                             node_color: any = "purple",
                             interior_line_height: float | int = 3/2,
                             sep_power: float | int = 1/4,
                             hyperedge_top_buffer_ratio: float | int = 3/5
                             ):
        '''
        This function allows for hypergraphs to be drawn with the points in a line

        :param G: the hypergraph you want to draw
        :param saturation: the saturation you want for the colors of your hyperedges (between 0 and 1)
        :param height: the height of the drawing
        :param hyperedge_fill_radius: the radius that hyperedges wrap around nodes
        :param node_hyperedge_box_multiplier: a multiplier used for a box that curves the hyperedge around the nodes
        :param hyperedge_zorder: the zorder for the hyperedges
        :param node_zorder: the zorder for the nodes
        :param node_radius: the radius for all of the nodes
        :param points_on_top: if true, the points will apear on top of the edges
        :param edge_opacity: the opacity of the hyperedges
        :param node_opacity: the opacity of the points
        :param node_color: the color of the nodes displayed
        :param interior_line_height: the height of the interior line
        :param sep_power: used to making the corelation between hyperedge size and width to be less extreme, (width is proportional to (hyperedge size)**(sep_power))
        :param hyperedge_top_buffer_ratio: a buffer paramiter (should be less than 1) used to dertermine size of hyperedge cap.
        '''
        
        # used for assigning colors
        def color(x, saturation) -> tuple:
            red = 0
            blue = 0
            if x < 0.5:
                red = saturation * (1 - (2 * x))
            elif x > 0.5:
                blue = saturation * ((2 * x) - 1)
            green = saturation - red - blue
            return (red, green, blue)
        
        # Node and edge layout
        hyperedge_layout = scatter.hyperedge_line_layout(G, segment(vector(0, height), vector(G.node_count, height)), sep_power)
        node_layout = hyperedge_layout.get_line_node_layout(G, segment(vector(0, 0), vector(G.node_count, 0)))

        # for colors
        delta = 1 / G.hyperedge_count
        x = delta / 2


        hyperedges = []
        interior_line = segment(vector(0, interior_line_height), vector(1, interior_line_height))
        # sorted so that hyperedges are listed in acending order by label in G
        for hyperedge in sorted(G.hyperedges.copy()):
            poly = polygon.create_line_hyperedge(
                hyperedge_layout[hyperedge],
                node_layout.image(G.hyperedge_sets[hyperedge]),
                interior_line,
                hyperedge_fill_radius,
                node_hyperedge_box_multiplier,
                hyperedge_top_buffer_ratio * hyperedge_layout[hyperedge]["width"]
            ) # creating the polygon

            poly.set_attributes_from({
                "color": color(x, saturation),
                "opacity": edge_opacity,
                "zorder": hyperedge_zorder,
                "edge_width": 0,
                "edge_type": "solid"
            }) # setting all attributes

            x += delta

            hyperedges.append(poly)
        
        arrows = []
        
        return cls(node_layout.create_vertex_list({
            "color": node_color,
            "opacity": node_opacity,
            "zorder": node_zorder,
            "radius": node_radius
        }), hyperedges, arrows)
        
    @classmethod
    def line_draw_immersion(cls, 
                             alpha: immersion_function, # the immersion
                             saturation: float | int = 0.55, # used for color saturation
                             width: float | int = 5, # the distance between the two rows of nodes in G and H
                             hyperedge_fill_radius: float | int = 1/6, # radius at which hyperedges fill nodes (between 0 and 1/2)
                             node_hyperedge_box_multiplier: float | int = 4/3, # a multiplier used for drawing the curve around the nodes
                             node_radius: float | int = 1/3, # radius of a point, should be no more that 1/2
                             edge_opacity: float | int = 0.45, # opacity of hyperedges
                             node_opacity: float | int = 0.5, # opacity of points
                             node_color: any = "purple", # color of the points
                             sep_power: float | int = 1/4, # used to mitigate clearance scaling
                             node_zorder: int = 3, # zorder for nodes
                             arrow_zorder: int = 3, # zorder for arrows
                             unimmersed_edge_zorder: int = 1,
                             immersed_edge_zorder: int = 2,
                             arrow_shavelength: float | int = 1/2,
                             arrowhead_length: float | int = 1/4,
                             arrowhead_width: float | int = 1/3,
                             arrow_thickness: float | int = 1/6,
                             hyperedge_x_offset: float | int = 5/4,
                             hyperedge_arrow_length: float | int = 3/2,
                             hyperedge_arrowhead_length: float | int = 1,
                             hyperedge_base_to_arrowhead_ratio: float | int = 4/5,
                             hyperedge_arrow_buffer_ratio: float | int = 3/4,
                             interior_line_offset: float | int = 3/2,
                             match_colors: bool = False # matches the colors of e and alpha(e) if true
                             ):
        '''
        This function allows for immersions to be drawn with points, edge merging, and arrows.
        The nodes on the left are for H and the ones on the right are for G
        The internal distance between two nodes (vertically) is 1, however, this will be scaled to fit when shown

        :param alpha: the specific immersion function you want
        :param saturation: the saturation you want for the colors of your hyperedges (between 0 and 1)
        :param wdith: the distance between the dispayed nodes of G and displayed nodes of H
        :param hyperedge_fill_radius: the radius at which hyperedges fill around nodes (should be no more that 1/2)
        :param node_hyperedge_box_multiplier: a multiplier used for a box that curves the hyperedge around the nodes
        :param node_radius: the radius of the circle for the nodes
        :param edge_opacity: the opacity of the hyperedges
        :param node_opacity: the opacity of the nodes
        :param node_color: the color of the nodes displayed
        :param sep_power: used to making the corelation between hyperedge size and width to be less extreme, (width is proportional to (hyperedge size)**(sep_power))
        :param node_zorder: zorder for the nodes
        :param arrow_zorder: zorder for the arrows
        :param unimmersed_edge_zorder: zorder for the hyperedges that were not part of the immersion
        :param immersed_edge_zorder: zorder for immersed hyperedges
        :param arrow_shavelength: a positive number (must be no more than half the length of the line). Allows the base and head of the arrow to not touch the intended vector
        :param arrowhead_length: the length of the arrowhead (non-negative number), applied after shaving. The remaining arrow still needs to have non-negative length
        :param arrowhead_width: the width of the arrowhead (non-negative number), if zero, length of the arrowhead will still be shaved off of the segment
        :param arrow_thickness: the thickness of the arrow body. If zero, the arrow body will not be plotted
        :param hyperedge_x_offset: the x offset for the hyperedge points
        :param hyperedge_arrow_length: the arrow length for the arrows on the H hyperedges
        :param hyperedge_arrowhead_length: the length of the arrowhead for the H hyperedges
        :param hyperedge_base_to_arrowhead_ratio: the arrow base width / arrowhead width for hyperedges (should be less than 1)
        :param hyperedge_arrow_buffer_ratio: for H hyperedges, arrowhead width / total width
        :param interior_line_offset: the x values for the interior lines for the hyperedges
        :param match_colors: matches the colors of e and alpha(e) if true
        '''

        def color(x, saturation) -> tuple:
            red = 0
            blue = 0
            if x < 0.5:
                red = saturation * (1 - (2 * x))
            elif x > 0.5:
                blue = saturation * ((2 * x) - 1)
            green = saturation - red - blue
            return (red, green, blue)
        
        G = alpha.G()
        G_merged = G.copy()
        H = alpha.H()
        height = G.node_count

        H_G_labels_dict = dict() # we need a hypergraph that is H but with the labels of the edges of G merged

        # Merging G edges (in a copy) to match 1 to 1 with H edges \/\/\/

        G_merge_mapping = dict() # maps G hyperedges to what they merged to
        
        unimmersed_G_edges = G.hyperedges.copy()

        G_labels_to_H_labels = dict()

        for hyperedge in H.hyperedges:
            subgraph = set(alpha.evaluate("edge", hyperedge))
            unimmersed_G_edges -= subgraph
            merged_hyperedge = G_merged.coalesce(subgraph.copy())
            H_G_labels_dict[merged_hyperedge] = H.hyperedge_sets[hyperedge].copy() # transfering hyperedge labels
            G_labels_to_H_labels[merged_hyperedge] = hyperedge # for when match_colors is true in order to match the colors
            for G_hyperedge in subgraph:
                G_merge_mapping[G_hyperedge] = merged_hyperedge
        for hyperedge in unimmersed_G_edges:
            G_merge_mapping[hyperedge] = hyperedge
        H_with_G_labels = hypergraph(H.nodes.copy(), H_G_labels_dict) # important for node mapping with a reasonable level of simplicity

        # Merged G Hyperedges /\/\/\

        hyperedge_layout = scatter.hyperedge_line_layout(G_merged, segment(vector(0, 0), vector(0, height)), sep_power) # hyperedge layout
        G_node_layout = hyperedge_layout.get_line_node_layout(G_merged, segment(vector(width / 2, 0), vector(width / 2, height))) # G Node layout
        H_node_layout = hyperedge_layout.get_line_node_layout(H_with_G_labels, segment(vector((-1) * width / 2, 0), vector((-1) * width / 2, height))) # H node layout

        # getting the arrows \/\/\/

        arrows = []
        for node in H.nodes:
            arrows.append(segment(H_node_layout[node].strip(), G_node_layout[alpha.evaluate("node", node)].strip()))
            arrows[-1]["u"].set_attributes_from({
                "color": "black",
                "opacity": 1,
                "zorder": arrow_zorder,
                "shavelength": arrow_shavelength,
                "thickness": arrow_thickness,
                "arrowhead_length": arrowhead_length,
                "arrowhead_width": arrowhead_width
            })
        
        # got the arrows /\/\/\

        if match_colors:
            delta = 1 / (H.hyperedge_count + len(unimmersed_G_edges))
        else:
            delta = 1 / (H.hyperedge_count + G.hyperedge_count)
        x = delta / 2

        # H hyperedge drawing \/\/\/
        H_interior_line = segment(vector((-1) * interior_line_offset, 0), vector((-1) * interior_line_offset, 1))

        hyperedges = []

        G_same_colors = dict()

        for hyperedge in H_with_G_labels.hyperedges:
  
            arrowhead_width = hyperedge_arrow_buffer_ratio * hyperedge_layout[hyperedge]["width"]
            edge_width = arrowhead_width * hyperedge_base_to_arrowhead_ratio

            poly = polygon.create_line_hyperedge(hyperedge_layout[hyperedge] - vector(hyperedge_x_offset, 0), 
                                                 H_node_layout.image(H_with_G_labels.hyperedge_sets[hyperedge]), 
                                                 H_interior_line,
                                                 hyperedge_fill_radius,
                                                 node_hyperedge_box_multiplier,
                                                 edge_width,
                                                 True,
                                                 hyperedge_arrow_length,
                                                 hyperedge_arrowhead_length,
                                                 arrowhead_width
                                                 )
            
            polycolor = color(x, saturation)

            poly.set_attributes_from({
                "color": polycolor,
                "opacity": edge_opacity,
                "zorder": immersed_edge_zorder,
                "edge_width": 0,
                "edge_type": "solid"
            })

            for G_hyperedge in alpha.evaluate("edge", G_labels_to_H_labels[hyperedge]):
                G_same_colors[G_hyperedge] = polycolor

            x += delta

            hyperedges.append(poly)
        
        # done H hyperedges /\/\/\


        # G hyperedges \/\/\/
        G_interior_line = segment(vector(interior_line_offset, 0), vector(interior_line_offset, 1))
        for hyperedge in G.hyperedges:
            
            edge_width = hyperedge_arrow_buffer_ratio * hyperedge_base_to_arrowhead_ratio * hyperedge_layout[G_merge_mapping[hyperedge]]["width"]

            poly = polygon.create_line_hyperedge(hyperedge_layout[G_merge_mapping[hyperedge]] + vector(hyperedge_x_offset, 0), 
                                                 G_node_layout.image(G.hyperedge_sets[hyperedge]), 
                                                 G_interior_line,
                                                 hyperedge_fill_radius,
                                                 node_hyperedge_box_multiplier,
                                                 edge_width
                                                 )
            
            if hyperedge in unimmersed_G_edges:
                z = unimmersed_edge_zorder
            else:
                z = immersed_edge_zorder
            
            if match_colors and hyperedge in G_same_colors.keys():
                polycolor = G_same_colors[hyperedge]
            else:
                polycolor = color(x, saturation)
                x += delta
            
            poly.set_attributes_from({
                "color": polycolor,
                "opacity": edge_opacity,
                "zorder": z,
                "edge_width": 0,
                "edge_type": "solid"
            })

            hyperedges.append(poly)

        attribute_dict = {
            "color": node_color,
            "opacity": node_opacity,
            "zorder": node_zorder,
            "radius": node_radius
        }

        return cls(H_node_layout.create_vertex_list(attribute_dict) + G_node_layout.create_vertex_list(attribute_dict),
                   hyperedges, arrows)
    
    @classmethod
    def draw_hyperedge_adjacency_graph(cls,
                                       G: hypergraph, # the hypergraph
                                       layout_method: str = "hyperedge_adjacency_graph_spring_layout",
                                       node_radius: float | int = 0.07, # radius of nodes
                                       node_opacity: float | int = 0.5, # node opacity
                                       node_color: any = "purple", # node color
                                       nodes_on_top: bool = True,
                                       edge_color: any = "black",
                                       edge_thickness: float | int = 0.01
                                       ):
        '''
        Draws the hyperedge adjacency graph of the given hypergraph

        :param G: the hypergraph
        :param layout_method: indicates how to lay out the hyperedges
        :param node_radius: the radius of the nodes
        :param node_opacity: the opacity of the nodes
        :param node_color: the color of the nodes
        :param nodes_on_top: places nodes over edges if True
        :param edge_color: the color of the edges
        :param edge_thickness: the thickness of the edges
        '''

        if nodes_on_top:
            node_zorder = 2
            edge_zorder = 1
        else:
            node_zorder = 1
            edge_zorder = 2

        layout = scatter.hyperedge_layout(G, layout_method)

        segments = []

        prev_hyperedges = set()
        for e1 in G.hyperedges:
            prev_hyperedges.add(e1)
            for e2 in G.edge_adjacency[e1] - prev_hyperedges:
                # making the edge
                edge = segment(layout[e1], layout[e2])
                edge["u"].set_attributes_from({
                    "color": edge_color,
                    "opacity": 1,
                    "zorder": edge_zorder,
                    "shavelength": 0,
                    "thickness": edge_thickness,
                    "arrowhead_length": 0,
                    "arrowhead_width": 0
                })
                segments.append(edge)
        
        vertices = layout.stripcopy().create_vertex_list({
            "color": node_color,
            "opacity": node_opacity,
            "zorder": node_zorder,
            "radius": node_radius
            })
        
        polygons = []

        return cls(vertices, polygons, segments)
    
    @classmethod
    def correlate_hyperedge_adjacency_graph(cls,
                                           G: hypergraph,
                                           G_drawing: any, # must be a drawing
                                           layout_method: str = "hyperedge_adjacency_graph_spring_layout",
                                           edge_color: any = "black",
                                           edge_thickness: float | int = 0.01,
                                           node_radius: float | int = 0.07,
                                           nodes_on_top: bool = True
                                           ):
        '''
        Draws a hyperedge adjacency graph where node colors match that of corosponding edge colors in an inputted drawing

        :param G: the hypergraph
        :param G_drawing: a valid drawing of that hypergraph (must be a drawing class). Nodes and hyperedges must be in acending order by label in G.
        :param layout_method: the layout method
        :param edge_color: the color of the edges
        :param edge_thickness: the thickness of the edges
        :param node_radius: the radius of the nodes
        :param nodes_on_top: nodes are on top if True
        '''

        hyperedges = G_drawing.hyperedges()
        if len(hyperedges) != G.hyperedge_count:
            raise ValueError("The drawing and hypergraph need to have the same amount of hyperedges.")

        if nodes_on_top:
            node_zorder = 2
            edge_zorder = 1
        else:
            node_zorder = 1
            edge_zorder = 2
        
        layout = scatter.hyperedge_layout(G, layout_method)

        segments = []

        prev_hyperedges = set()
        for e1 in G.hyperedges:
            prev_hyperedges.add(e1)
            for e2 in G.edge_adjacency[e1] - prev_hyperedges:
                # making the edge
                edge = segment(layout[e1], layout[e2])
                edge["u"].set_attributes_from({
                    "color": edge_color,
                    "opacity": 1,
                    "zorder": edge_zorder,
                    "shavelength": 0,
                    "thickness": edge_thickness,
                    "arrowhead_length": 0,
                    "arrowhead_width": 0
                })
                segments.append(edge)
        
        vertices = layout.stripcopy().create_vertex_list({
            "zorder": node_zorder,
            "radius": node_radius
            })
        
        for index in range(G.hyperedge_count):
            vertices[index].set_attributes_from({
                "color": hyperedges[index]["color"],
                "opacity": hyperedges[index]["opacity"]
            })

        polygons = []
        return cls(vertices, polygons, segments)
        

    def get_max(self) -> float:
        max_distance = 0
        for node in self.__nodes:
            if abs(node["x"]) > max_distance:
                max_distance = abs(node["x"])
            if abs(node["y"]) > max_distance:
                max_distance = abs(node["y"])
        for hyperedge in self.__hyperedges:
            for node in hyperedge.verticies():
                if abs(node["x"]) > max_distance:
                    max_distance = abs(node["x"])
                if abs(node["y"]) > max_distance:
                    max_distance = abs(node["y"])
        return float(max_distance)
    
    def nodes(self, copy: bool = True) -> list:
        '''
        :param copy: if true, it will return a copy of the list
        '''
        if copy:
            return self.__nodes.copy()
        return self.__nodes

    def hyperedges(self, copy: bool = True) -> list:
        '''
        :param copy: if true, it will return a copy of the list
        '''
        if copy:
            return self.__hyperedges.copy()
        return self.__hyperedges
    
    def curvify(self, poly: polygon, resolution: int = 100) -> polygon:
        '''
        Applies the curving to the polgon at the given resolution

        :param poly: the polygon
        :param resolution: the number of times we evaluate for each curve
        '''
        
        delta = 1 / resolution
        curve = []
        for vertex in poly.verticies():
            t = 0
            if vertex["curve_type"] == "bezier":
                coeficients = [1]
                n = len(vertex["curve"]) - 1
                for i in range(n):
                    coeficients.append((coeficients[-1] * (n - i)) // (i + 1))
                while t <= 1:
                    v = vector(0, 0)
                    for index in range(n + 1):
                        v += (coeficients[index] * (t**index) * ((1 - t)**(n - index))) * vertex["curve"][index]
                    curve.append(v)
                    #curve.append(bezier_curve(vertex["curve"], t))
                    t += delta
            else:
                curve.append(vertex.strip())
        return polygon(curve)
    
    def copy(self):

        # nodes
        nodes = []
        for node in self.__nodes:
            nodes.append(node.copy())
        
        # arrows
        arrows = []
        for arrow in self.__arrows:
            arrows.append(segment(arrow["u"].copy(), arrow["v"].copy()))
        
        # hyperedges (polygons)
        hyperedges = []
        for hyperedge in self.__hyperedges:
            vertices = []
            for vertex in hyperedge.verticies():
                if not vertex["curve_type"] == None:
                    curve = []
                    for v in vertex["curve"].verticies():
                        curve.append(v.copy(False))
                    vertices.append(vertex.copy(False))
                    vertices[-1]["curve"] = polygon(curve)
                vertices[-1]["curve_type"] = vertex["curve_type"]
            hyperedges.append(polygon(vertices))
            hyperedges[-1]["color"] = hyperedge["color"]
            hyperedges[-1]["opacity"] = hyperedge["opacity"]
            hyperedges[-1]["edge_type"] = hyperedge["edge_type"]
            hyperedges[-1]["edge_width"] = hyperedge["edge_width"]
            hyperedges[-1]["zorder"] = hyperedge["zorder"]
        
        return drawing(nodes, hyperedges, arrows)
            

    def plot(self, resolution: int = 100) -> None:
        '''
        :param resolution: the curve resolution
        '''

        for node in self.__nodes:
            node.radplot(node["radius"], node["color"], node["opacity"], node["zorder"])
        
        for hyperedge in self.__hyperedges:
            self.curvify(hyperedge, resolution).plot(hyperedge["color"], hyperedge["color"], hyperedge["opacity"], line_type = hyperedge["edge_type"], thickness = hyperedge["edge_width"], zorder = hyperedge["zorder"])
        
        for arrow in self.__arrows:
            arrow.arrowplot(shave_length = arrow["u"]["shavelength"], arrowhead_length = arrow["u"]["arrowhead_length"], arrowhead_width = arrow["u"]["arrowhead_width"], thickness = arrow["u"]["thickness"], color = arrow["u"]["color"], opacity = arrow["u"]["opacity"], zorder = arrow["u"]["zorder"])
        
        pass

    def show(self, resolution: int = 100, buffer: float | int = 0, disable_axes: bool = True, proper_ratio: bool = True, square: bool = True) -> None:
        '''
        :param resolution: the curve resolution
        :param buffer: a number that gets added to the maxes and subtracted from the mins
        :param disable_axes: if True, the axes will not be shown
        :param proper_ratio: if True, it will insure that there is no streaching
        :param square: if True, then the plot will be square
        '''

        x_min, y_min, x_max, y_max = self.bounds()

        if square:
            x_mid = (x_min + x_max) / 2
            y_mid = (y_min + y_max) / 2
            radius = max(x_max - x_mid, y_max - y_mid)
            x_min = x_mid - radius
            y_min = y_mid - radius
            x_max = x_mid + radius
            y_max = y_mid + radius

        plt.figure()
        if disable_axes:
            plt.axis("off")
        if proper_ratio:
            plt.axis("square")
        plt.xlim(x_min - buffer, x_max + buffer)
        plt.ylim(y_min - buffer, y_max - buffer)
        self.plot(resolution)
        plt.show()

        pass

    def verify(self, explain: bool = False) -> bool:
        '''
        This function verifies if the drawing draws the hypergraph correctly
        THIS FUNCTION DOES NOT WORK FOR LINE DRAWINGS (i.e. from line_draw_hypergraph or line_draw_immersion)

        :param explain: if true, it will print out any issues with the verification (using indecies)
        '''

        m = 0.95

        def show_intersection(index: int, i: int, j: int) -> None:
            '''
            :param index: the index for the polygon
            :param i: the index for the first edge
            :param j: the index for the second edge
            '''
            print("Polygon ", index, ": Unwanted intersection between edges ", (i - 1, i), " and ", (j - 1, j), "!", sep = "")
            pass

        verified = True
        
        for index in range(len(self.__hyperedges)):

            # checking for crossing \/ \/ \/
            poly = self.__hyperedges[index]
            E = poly.edges()
            for i in range(2, len(E) - 1):
                for j in range(i - 1):
                    if E[i].intersecting(E[j]):
                        if explain:
                            show_intersection(index, i, j)
                            verified = False
                        else:
                            return False
            for i in range(1, len(poly) - 2):
                if E[-1].intersecting(E[i]):
                    if explain:
                        show_intersection(index, i, j)
                        verified = False
                    else:
                        return False
            # checking for crossing /\ /\ /\

            # checking for containment issues \/ \/ \/

            for v in poly["whitelist"]:
                if not poly.contains(v):
                    if explain:
                        print("Polygon ", index, ": does not contain the whitelisted vector ", v, "!", sep = "")
                        verified = False
                    else:
                        return False
            
            for v in poly["blacklist"]:
                if poly.contains(v):
                    if explain:
                        print("Polygon ", index, ": contains blacklisted the vector ", v, "!", sep = "")
                        verified = False
                    else:
                        return False
            # checking for containment issues /\ /\ /\
    
        return verified
    
    def rotate(self, angle: float | int) -> None:

        # hyperedges (polygons)
        for hyperedge in self.__hyperedges:
            hyperedge.rotate(angle)
        
        # arrows
        for arrow in self.__arrows:
            arrow["u"].rotate_self(angle)
            arrow["v"].rotate_self(angle)
        
        # nodes
        for node in self.__nodes:
            node.rotate_self(angle)
        
        pass

    def offset(self, v: vector) -> None:
        '''
        :param v: the vector in which we are adding to every point
        '''

        # hyperedges (polygons)
        for hyperedge in self.__hyperedges:
            hyperedge.offset(v)
        
        # arrows
        for arrow in self.__arrows:
            arrow["u"] += v
            arrow["v"] += v
        
        # nodes
        for node in self.__nodes:
            new_node = node + v
            node["x"] = new_node["x"]
            node["y"] = new_node["y"]
        
        pass

    def scale(self, scale_factor) -> None:
        '''
        :param scale_factor: the factor in which we want to scale the drawing
        '''

        # hyperedges (polygons)
        for hyperedge in self.__hyperedges:
            hyperedge.scale(scale_factor)
        
        # arrows
        for arrow in self.__arrows:
            arrow["u"] *= scale_factor
            arrow["v"] *= scale_factor
            arrow["u"]["shavelength"] *= scale_factor
            arrow["u"]["arrowhead_length"] *= scale_factor
            arrow["u"]["arrowhead_width"] *= scale_factor
            arrow["u"]["thickness"] *= scale_factor
        
        # nodes
        for node in self.__nodes:
            node["x"] *= scale_factor
            node["y"] *= scale_factor
            node["radius"] *= scale_factor
        
        pass

    def bounds(self) -> tuple[int | float, int | float, int | float, int | float]:
        '''
        bounds are returned in order of (x_min, y_min, x_max, y_max)
        '''

        bounds_established = False

        # nodes
        for node in self.__nodes:
            x = node["x"] - node["radius"]
            y = node["y"] - node["radius"]
            X = node["x"] + node["radius"]
            Y = node["y"] + node["radius"]
            if not bounds_established:
                bounds_established = True
                x_min = x
                y_min = y
                x_max = X
                y_max = Y
            else:
                if x < x_min:
                    x_min = x
                if X > x_max:
                    x_max = X
                if y < y_min:
                    y_min = y
                if Y > y_max:
                    y_max = Y
        
        # arrows
        for arrow in self.__arrows:
            for vertex in arrow.arrowvertices(shave_length = arrow["u"]["shavelength"], arrowhead_length = arrow["u"]["arrowhead_length"], arrowhead_width = arrow["u"]["arrowhead_width"], thickness = arrow["u"]["thickness"]):
                if not bounds_established:
                    bounds_established = True
                    x_min = vertex["x"]
                    x_max = vertex["x"]
                    y_min = vertex["y"]
                    y_max = vertex["y"]
                else:
                    if vertex["x"] < x_min:
                        x_min = vertex["x"]
                    if vertex["x"] > x_max:
                        x_max = vertex["x"]
                    if vertex["y"] < y_min:
                        y_min = vertex["y"]
                    if vertex["y"] > y_max:
                        y_max = vertex["y"]
        
        # hyperedges (polygons)

        for hyperedge in self.__hyperedges:
            for vertex in hyperedge.verticies():
                if not bounds_established:
                    bounds_established = True
                    x_min = vertex["x"]
                    x_max = vertex["x"]
                    y_min = vertex["y"]
                    y_max = vertex["y"]
                else:
                    if vertex["x"] < x_min:
                        x_min = vertex["x"]
                    if vertex["x"] > x_max:
                        x_max = vertex["x"]
                    if vertex["y"] < y_min:
                        y_min = vertex["y"]
                    if vertex["y"] > y_max:
                        y_max = vertex["y"]

        return x_min, y_min, x_max, y_max

    def autobound(self, buffer: float | int = 0.1, x_min: float | int = -1, y_min: float | int = -1, x_max: float | int = 1, y_max: float | int = 1) -> None:
        '''
        :param buffer: a buffer zone for the bounds
        '''

        x_min += buffer
        y_min += buffer
        x_max -= buffer
        y_max -= buffer

        real_x_min, real_y_min, real_x_max, real_y_max = self.bounds()

        real_length = real_x_max - real_x_min
        real_height = real_y_max - real_y_min
        length = x_max - x_min
        height = y_max - y_min

        # scaling
        scale_factor = min(length / real_length, height / real_height)
        self.scale(scale_factor)


        # offsetting
        real_center = ((vector(real_x_min, real_y_min) + vector(real_x_max, real_y_max)) / 2) * scale_factor
        center = (vector(x_min, y_min) + vector(x_max, y_max)) / 2
        self.offset(center - real_center)

        pass
