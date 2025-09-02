from Vector import vector
from Sorted_array import sorted_array
from Segment import segment
from Polybuild import build_half_polygon
import matplotlib.pyplot as plt

class polygon:

    def __init__(self, verticies: list):
        '''
        :param verticies: a list of a vertecies in the polygon in vector form
        '''

        self.__verticies = verticies.copy()
        self.__attributes = dict()
        pass

    @classmethod
    def create_hyperedge(cls, whitelist: list, blacklist: list, clearance_paramiter = "clearance", clearance_multiplier: float = 1.0):
        '''
        :param whitelist: all point you want to be inside your polygon
        :param blacklist: all points you don't want in your polygon
        :param clearance_paramiter: the attribute used to obtain the clearance for a vector
        :param clearance_multiplier: a multiplier for the clearance (used to drawing immersions)
        '''

        if len(whitelist) == 0:
            raise ValueError("empty hyperedges cannot be drawn")
        elif len(whitelist) == 1:
            v = whitelist[0]
            clearance = v[clearance_paramiter]
            i = vector(clearance, 0)
            j = vector(0, clearance)
            return cls([v - i - j, v + i - j, v + i + j, v - i + j])
        
        # finding the two points with the greatest distance appart
        greatest_distance = 0
        N = 1
        K = 0

        # O(n^2)
        for n in range(1, len(whitelist)):
            for k in range(n):
                distance = whitelist[n].distance(whitelist[k])
                if distance > greatest_distance:
                    greatest_distance = distance
                    N = n
                    K = k
        midline = segment(whitelist[K], whitelist[N])
        i_hat = midline.direction()
        j_hat = vector(-1 * i_hat["y"], i_hat["x"]) # should be i_hat rotated by 90 degrees

        whitelist[0]["i_hat"] = whitelist[0] * i_hat
        whitelist[0]["j_hat"] = whitelist[0] * j_hat
        clearance = whitelist[0][clearance_paramiter]

        j_min = j_max = whitelist[0]["j_hat"]
        for v in whitelist:
            v["i_hat"] = v * i_hat
            v["j_hat"] = v * j_hat
            v["whitelisted"] = True
            if v["j_hat"] > j_max:
                j_max = v["j_hat"]
            elif v["j_hat"] < j_min:
                j_min = v["j_hat"]
            if v[clearance_paramiter] < clearance:
                clearance = v[clearance_paramiter]
        raw_clearance = clearance
        clearance *= clearance_multiplier
        i_min, i_max = midline["u"]["i_hat"], midline["v"]["i_hat"]
        j_middle = midline["u"] * j_hat
        i_min -= clearance
        j_min -= clearance
        i_max += clearance
        j_max += clearance

        # sorting
        # note that N > K
        whitelist_copy = whitelist.copy()
        right_endpoint = whitelist_copy.pop(N)
        left_endpoint = whitelist_copy.pop(K)
        sorted_verticies = sorted_array.sort(list(sorted_array.sort(whitelist_copy, "j_hat")), "i_hat") # O(n * log(n))
        left_obstructors = sorted_array([], "i_hat")
        right_obstructors = sorted_array([], "i_hat")

        # O(n)
        for v in blacklist:
            v["whitelisted"] = False
            v["i_hat"] = v * i_hat
            v["j_hat"] = v * j_hat
            if (i_min - 2 * clearance <= v["i_hat"] <= i_max + 2 * clearance) and (j_min - 2 * clearance <= v["j_hat"] <= j_max + 2 * clearance):
                if raw_clearance > v[clearance_paramiter]:
                    raw_clearance = v[clearance_paramiter]
                if i_min + clearance <= v["i_hat"]:
                    if v["i_hat"] <= i_max - clearance:
                        sorted_verticies.insert(v)
                    else:
                        right_obstructors.insert(v)
                else:
                    left_obstructors.insert(v)


        # in order to prevent any edge cases, the clearance will be slightly modified

        # OLD
        '''
        end_multiplier = 3.14159 # pi cuz why not, needs to be greater than three cuz edge cases
        '''
        # OLD

        # EXPERIMENTAL
        end_multiplier = 1.125 # needs to be greater than 1
        # EXPERIMENTAL

        clearance = raw_clearance * clearance_multiplier / end_multiplier
        
        upper = [] # least to greatest
        lower = [] # greatest to least

        # O(n)
        for v in sorted_verticies:

            # OLD
            '''
            if v["j_hat"] >= j_middle - clearance: # the minus clearance part is there to account for any edge cases with intersection of the midline
                upper.append(v)
            '''
            # OLD

            # EXPERIMENTAL
            if v["j_hat"] >= j_middle:
                upper.append(v)
            # EXPERIMENTAL

            else:
                lower.insert(0, v)
        
        # adding the endpoints to each
        # right and left get switched for lower
        upper.insert(0, left_endpoint)
        upper.append(right_endpoint)

        lower.append(left_endpoint)
        lower.insert(0, right_endpoint)
        
        left_bound = list(left_obstructors)
        right_bound = list(right_obstructors)

        upper_vertex_list = build_half_polygon(clearance * i_hat, clearance * j_hat, upper, left_bound, right_bound, midline, "whitelisted", end_multiplier)

        # right and left switch since we are flipping
        lower_vertex_list = build_half_polygon(-1 * clearance * i_hat, -1 * clearance * j_hat, lower, right_bound, left_bound, midline, "whitelisted", end_multiplier)


        output = cls(upper_vertex_list + lower_vertex_list)
        output[clearance_paramiter] = clearance
        return output
    
    @classmethod
    def create_line_hyperedge(cls, 
                              hyperedge_vector: vector, # the vector point for the hyperedge
                              node_vectors: list[vector], # the set of nodes in the hyperedge
                              interior_line: segment, # the line used to limit the interior curves and to determine direction of basis vectors
                              clearance: int | float, # a clearance for the nodes
                              clearance_multiplier: int | float, # multiplier for the clarance box
                              top_width: int | float, # the width for the hyperedge as well as a width for the base of the arrow if there is an arrow
                              arrow: bool = False, # adds an arrow at the end if true, otherwise it does not
                              arrow_length: int | float = 0, # the length of the arrow base + arrowhead
                              arrowhead_length: int | float = 0, # the length of the arrowhead (cannot be longer than the arrow length)
                              arrowhead_width: int | float = 0, # the width of the arrowhead
                              curve: any = "curve", # curve attribute
                              curve_type: any = "curve_type", # curve type attribute
                              bezier: any = "bezier" # curve type name for bezier curves
                              ):
        '''
        Creates a hyperedge for the line drawing for hyperedges and immersions
        polygons created from this function will already have curves implemented

        :param hyperedge_vector: the location of the hyperedge
        :param node_vectors: a list of all node locations. The list does not need to be sorted, this function will handle that (cannot be an empty list)
        :param interior_line: a line used to limit the hight of interior curves and to determine the direction that we are working with (i.e. i_hat and j_hat)
        :param clearance: the clearance (as a radius) from the nodes used to set the distance from the node for intersections
        :param clearance_multiplier: a multiplier for the clearance box which allows for drawing around nodes
        :param top_width: used both as the width for a hyperedge and as the width of the base of the arrow if applicable
        :param arrow: places an arrowhead in if true, otherwise this step is skipped. All arrow related paramiters do nothing if this is False
        :param arrow_length: the total length of the arrow from hyperedge_vector to arrow tip
        :param arrowhead_length: the length of the arrowhead (should not be more than arrow_length)
        :param arrowhead_width: the width of the arrowhead (should be greater than top_width)
        :param curve: the key used to aquire the curve attribute
        :param curve_type: the key used to aquire the curve type attribute
        :param bezier: the object for the curve type attribute meant to indicate a bezier curve
        '''

        # error conditions

        if len(node_vectors) == 0:
            raise ValueError("Cannot create line hyperedge for empty list of nodes.")

        # internal functions

        def curve_around_vertex(vertex: vector, 
                                first_segment: segment, 
                                last_segment: segment, 
                                hyperedge_vector: vector = hyperedge_vector,
                                clearance: int | float = clearance,
                                box_multiplier: int | float = clearance_multiplier,
                                curve: any = curve,
                                curve_type: any = curve_type,
                                bezier: any = bezier
                                ) -> vector:
            '''
            :param vertex: the vertex we are making a curve around
            :param first_segement: the segment that goes first (as per the direction we are going), "u" must be an offset point
            :param last_segment: the last segment (as per the direction we are going), "u" must be an offset point
            :param hyperedge_vector: the location of the hyperedge
            :param clearance: the clearance (as a radius) from the nodes used to set the distance from the node for intersections
            :param box_muliplier: a multiplier for the clearance for the box
            :param curve: the key used to aquire the curve attribute
            :param curve_type: the key used to aquire the curve type attribute
            :param bezier: the object for the curve type attribute meant to indicate a bezier curve
            '''

            # Two possible cases

            # 1. intersection between first and last segment are "above" the line (would lead to crossing on the square intersection algorithm)
            # 2. the below case, where we do the square intersection algorithm


            # NEW \/\/\/

            # establishing I and J vectors for the rectangle

            I = box_multiplier * (last_segment["u"] - vertex)
            J = vector((-1) * I["y"], I["x"])

            # checking if the intersection between the first and last segment is contained in our clearance box
            # the standard contains function will not be used here since the lines could be parellel, which could cause an error

            a_first, b_first, c_first = first_segment.equation_params()
            a_last, b_last, c_last = last_segment.equation_params()

            numerator = vector(b_first * c_last - c_first * b_last, c_first * a_last - c_last * a_first) 
            # of the intersection between first and last segment
            denominator = a_first * b_last - a_last * b_first

            # this avoids the problem of inequality signs fipping upon multiplication of a negative
            # we just force our denomiator to be positive (or zero)
            if denominator < 0:
                numerator *= -1
                denominator *= -1
            
            offset_numerator = numerator - (denominator * vertex) # offseting the numerator vector as opposed to the corners
            I_squared = I * I

            # checking if we are contained in the rectangle
            if abs(offset_numerator * I) <= denominator * I_squared and (-1) * I_squared * denominator <= offset_numerator * J <= 0:
                polyvertex = numerator / denominator # the intersection point
                polyvertex[curve] = polygon([first_segment["u"].strip(), polyvertex.strip(), last_segment["u"].strip()])
                polyvertex[curve_type] = bezier
                return polyvertex
            
            # now our intersection is outside of the box
            # we will find where each line intersects the box

            first_side = segment(vertex - I, vertex - I - J)
            last_side = segment(vertex + I, vertex + I - J)
            bottom_side = segment(first_side["v"].strip(), last_side["v"].strip())

            # first sgement

            if first_side.crosses(a_first, b_first, c_first): # if we cross the first side
                first_intermediate = first_segment.intersection(first_side)
            elif last_side.crosses(a_first, b_first, c_first): # if we cross the last side
                first_intermediate = first_segment.intersection(last_side)
            else: # otherwise we must cross the bottom side
                first_intermediate = first_segment.intersection(bottom_side)

            # last segment
            if last_side.crosses(a_last, b_last, c_last): # if we cross the last side
                last_intermediate = last_segment.intersection(last_side)
            elif first_side.crosses(a_last, b_last, c_last): # if we cross the first segment
                last_intermediate = last_segment.intersection(first_side)
            else: # otherwise we must cross the bottom side
                last_intermediate = last_segment.intersection(bottom_side)
            
            polyvertex = vertex - J
            polyvertex[curve] = polygon([first_segment["u"].strip(), first_intermediate, last_intermediate, last_segment["u"].strip()])
            polyvertex[curve_type] = bezier
            return polyvertex

            # NEW /\/\/\

            '''

            polyvertex = vertex.strip()
            offset = clearance * (polyvertex - hyperedge_vector).unit()
            polyvertex += offset
            bounding_segment = segment(polyvertex, polyvertex + vector((-1) * offset["y"], offset["x"]))

            # this is for checking if we cannot do the standard double intersection method
            # we cannot do the standard method if our two lines intersect between the perpendicular lines at the vertex and offset
            # thus if upper_val and lower_val have oppisite signs, we have a problem
            # we also have a problem if lower_val = 0
            a, b, c = bounding_segment.equation_params()
            first_last_intersection = first_segment.intersection(last_segment)

            lower_val = (first_last_intersection * (a, b)) + c

            a, b, c = segment(vertex.strip(), vertex + vector((-1) * offset["y"], offset["x"])).equation_params() # parelell line intersecing the vertex

            upper_val = (first_last_intersection * (a, b)) + c

            if lower_val == 0 or (lower_val > 0 and upper_val <= 0) or (lower_val < 0 and upper_val >= 0):
                # this means that the intersection and vertex are on the same side of the line
                # thus we will have crossing if we try to do this the standard way of taking two intersection points with the bounding segment
                first_last_intersection[curve] = polygon([first_segment["u"], first_last_intersection.strip(), last_segment["u"]])
                first_last_intersection[curve_type] = bezier
                return first_last_intersection
            
            # now for the standard method
            polyvertex[curve] = polygon([first_segment["u"], first_segment.intersection(bounding_segment), last_segment.intersection(bounding_segment), last_segment["u"]])
            polyvertex[curve_type] = bezier
            return polyvertex
            '''
        

        # unit vectors
        interior_direction = interior_line["v"] - interior_line["u"]
        j_hat = (hyperedge_vector - segment(hyperedge_vector, hyperedge_vector + vector((-1) * interior_direction["y"], interior_direction["x"])).intersection(interior_line)).unit()
        i_hat = vector(j_hat["y"], (-1) * j_hat["x"]) # ensures that the hyperedge vector lies above the interior line and that we have a right handed cordinate system
        polylist = []

        # sorting the list of verticies
        sorted_nodes = sorted_array([], "i")
        for node in node_vectors:
            v = node.strip()
            v["i"] = v * i_hat
            sorted_nodes.insert(v)

        # handling the first and final segments for the polygon as well as the arrowhead
        left_curve_end = sorted_nodes[0] - (clearance * i_hat)
        right_curve_start = sorted_nodes[-1] + (clearance * i_hat)
        inner_offset = (top_width / 2) * i_hat
        first_segment = segment(left_curve_end, hyperedge_vector - inner_offset)
        final_segment = segment(right_curve_start, hyperedge_vector + inner_offset)

        if arrow:
            # making the arrowhead

            arrow_top = hyperedge_vector + (arrow_length * j_hat)
            arrow_base_end = arrow_top - (arrowhead_length * j_hat)
            outer_offset = (arrowhead_width / 2) * i_hat
            polylist.append(arrow_base_end + outer_offset)
            polylist.append(arrow_top)
            polylist.append(arrow_base_end - outer_offset)
            for v in polylist:
                v[curve_type] = None
            
            # the outer curves
            
            # the "left" one
            first_transition_point = hyperedge_vector - inner_offset
            first_transition_point[curve] = polygon([arrow_base_end - inner_offset, first_transition_point.strip(), left_curve_end.strip()])
            first_transition_point[curve_type] = bezier
            polylist.append(first_transition_point)

            # the "right" one
            last_transition_pont = hyperedge_vector + inner_offset
            last_transition_pont[curve] = polygon([right_curve_start.strip(), last_transition_pont.strip(), arrow_base_end + inner_offset])
            last_transition_pont[curve_type] = bezier
            polylist.insert(0, last_transition_pont)
        
        else:
            # right outer curve
            final_point = hyperedge_vector + inner_offset
            final_point[curve] = polygon([right_curve_start.strip(), final_point.strip(), hyperedge_vector.strip()])
            final_point[curve_type] = bezier
            polylist.append(final_point)

            # left outer curve
            first_point = hyperedge_vector - inner_offset
            first_point[curve] = polygon([hyperedge_vector.strip(), first_point.strip(), left_curve_end.strip()])
            polylist.append(first_point)
        
        if len(sorted_nodes) < 2:
            polylist.append(curve_around_vertex(sorted_nodes[0], first_segment, final_segment))
            return cls(polylist)
        
        apex_list = []
        # list of apex intersection for the curves between points, apex_list[index] = apex between sorted_nodes[index] and sorted_nodes[index + 1]

        # doing it this way for easy organization
        for index in range(len(sorted_nodes) - 1):
            u = segment(sorted_nodes[index] + (clearance * i_hat), hyperedge_vector.strip()).intersection(interior_line)
            v = segment(sorted_nodes[index + 1] - (clearance * i_hat), hyperedge_vector.strip()).intersection(interior_line)
            apex_list.append((u + v) / 2)


        for index in range(len(sorted_nodes) - 1):
            # curving around the vertex
            last_segment = segment(sorted_nodes[index] + (clearance * i_hat), apex_list[index])
            polylist.append(curve_around_vertex(sorted_nodes[index], first_segment, last_segment))

            # curving between the verticies
            first_segment = segment(sorted_nodes[index + 1] - (clearance * i_hat), apex_list[index])
            apex = apex_list[index].strip()
            apex[curve] = polygon([last_segment["u"].strip(), apex.strip(), first_segment["u"].strip()])
            apex[curve_type] = bezier
            polylist.append(apex)

        # curving around the final vertex
        polylist.append(curve_around_vertex(sorted_nodes[-1], first_segment, final_segment))
        
        return cls(polylist)

    def __len__(self):
        return len(self.__verticies)
    
    def point_distance(self, point: vector) -> float:
        '''
        :param point: a vector in 2d space
        '''
        edges = self.edges()
        min_distance = edges[0].point_distance(point)
        for edge in edges[1:]:
            distance = edge.point_distance(point)
            if distance < min_distance:
                min_distance = distance
        return min_distance

    def __getitem__(self, item):
        if type(item) == int:
            return self.__verticies[item % len(self.__verticies)]
        elif type(item) == slice:
            return self.__verticies[item]
        return self.__attributes[item]
    
    def __setitem__(self, key, item):
        if type(key) == int:
            self.__verticies[key % len(self.__verticies)] = item
        else:
            self.__attributes[key] = item
        pass

    def set_attributes_from(self, dictionary: dict) -> None:
        '''
        Sets sets the attributes up such that all attributes map from keys to objects of the inputted dictionary (which is NOT copied)

        :param dictionary: any dictionary
        '''

        for key in dictionary.keys():
            self[key] = dictionary[key]
        
        pass

    def attributes(self) -> list:
        return self.__attributes.keys()

    def insert(self, point: vector, index: int) -> None:
        '''
        :param point: point in 2d space
        :param index: the index you want to insert into
        '''
        index %= len(self)
        self.__verticies.insert(index, point)
        pass

    def pop(self, index: int) -> vector:
        '''
        :param index: the index you want to delete
        '''
        index %= len(self)
        return self.__verticies.pop(index)
    
    def verticies(self) -> list:
        return self.__verticies.copy()
    
    def edges(self) -> list:
        L = []
        for index in range(len(self.__verticies)):
            L.append(segment(self[index - 1], self[index]))
        return L
    
    def contains(self, point) -> bool:
        '''
        :param point: an x-y point
        '''
        inside = False
        line = segment(vector(point[0], point[1]), point + vector.j())
        for E in self.edges():
            if E["u"]["x"] <= point[0] <= E["v"]["x"] or E["v"]["x"] <= point[0] <= E["u"]["x"]:
                intersection = line.intersection(E)
                if type(intersection) == vector and intersection["y"] >= point[1]:
                    inside = not inside
        return inside
    
    def bounding_box(self) -> tuple[float, float, float, float]:
        # returns in format of: xmin, xmax, ymin, ymax
        if len(self) == 0:
            raise ValueError("Cannot bound empty polygon")
        verticies = self.verticies()
        xmin, xmax, ymin, ymax = verticies[0]["x"], verticies[0]["x"], verticies[0]["y"], verticies[0]["y"]
        for v in verticies[1:]:
            if v["x"] < xmin:
                xmin = v["x"]
            elif v["x"] > xmax:
                xmax = v["x"]
            if v["y"] < ymin:
                ymin = v["y"]
            elif v["y"] > ymax:
                ymax = v["y"]
        return float(xmin), float(xmax), float(ymin), float(ymax)
    
    def plot(self, edge_color = "black", fill_color = "white", opacity = 0, thickness = 1, line_type: str = "solid", zorder: int = 1) -> None:
        '''
        :param zorder: used for what goes on top of what
        :param edge_color: the color you want your edges to be
        :param fill_color: the color you want to fill
        :param opacity: opacity of the fill, input zero if you dont want to fill anything
        :param thickness: the thickness of the lines
        :param line_type: "solid" for a solid line, "dashed" for a dashed line, and "dotted" for a dotted line
        '''

        if len(self) <= 2:
            raise ValueError("Does not qualify as polygon")
        X = []
        Y = []
        for index in range(-1, len(self)):
            X.append(self[index]["x"])
            Y.append(self[index]["y"])
        if thickness > 0:
            plt.plot(X, Y, color = edge_color, linewidth = thickness, linestyle = line_type, zorder = zorder)
        if opacity > 0:
            plt.fill(X, Y, color = fill_color, alpha = opacity, linewidth = 0, zorder = zorder)
        pass

    def show(self, edge_color = "black", fill_color = "white", opacity = 0, thickness = 1, line_type: str = "solid", buffer = 1.25, zorder: int = 1) -> None:
        '''
        :param zorder: used for what goes on top of what
        :param edge_color: the color you want your edges to be
        :param fill_color: the color you want to fill
        :param opacity: opacity of the fill, input zero if you dont want to fill anything
        :param thickness: the thickness of the lines
        :param line_type: "solid" for a solid line, "dashed" for a dashed line, and "dotted" for a dotted line
        :param buffer: used to give some buffer at the edge of a plot, use as a multiplier
        '''

        xmin, xmax, ymin, ymax = self.bounding_box()
        xcenter = (xmax + xmin) / 2
        ycenter = (ymax + ymin) / 2
        radius = buffer * max(xmax - xmin, ymax - ymin) / 2
        xmin, xmax, ymin, ymax = xcenter - radius, xcenter + radius, ycenter - radius, ycenter + radius
        plt.figure()
        plt.xlim(xmin, xmax)
        plt.ylim(ymin, ymax)
        self.plot(edge_color, fill_color, opacity, thickness, line_type, zorder)
        plt.show()
        pass

    def check(self) -> bool:
        # returns False if lines on the polygon cross themselves
        E = self.edges()
        for i in range(2, len(E) - 1):
            for j in range(i - 1):
                if E[i].intersecting(E[j]):
                    return False
        for i in range(1, len(self) - 2):
            if E[-1].intersecting(E[i]):
                return False
        return True
    
    def checkpoints(self, whitelist: list, blacklist: list, clearance_paramiter = "clearance") -> bool:
        '''
        :param whitelist: all point you want to be inside your polygon
        :param blacklist: all points you don't want in your polygon
        :param clearance_paramiter: the attribute used to obtain the clearance for a vector
        '''

        multiplier = 0.95

        for v in whitelist:
            if self.point_distance(v) < multiplier * self[clearance_paramiter] or not self.contains(v):
                return False
        
        for v in blacklist:
            if self.point_distance(v) < multiplier * self[clearance_paramiter] or self.contains(v):
                return False
        
        return True
    
    def copy(self):
        copy = polygon(self.verticies())
        for attribute in self.attributes():
            copy[attribute] = self[attribute]
        return copy
    
    def skim(self, whitelist: list, blacklist: list, clearance_paramiter = "clearance") -> None:
        '''
        :param whitelist: all point you want to be inside your polygon
        :param blacklist: all points you don't want in your polygon
        :param clearance_paramiter: the attribute used to obtain the clearance for a vector
        '''

        index = 0
        while index < len(self) and len(self) > 3:
            triangle = polygon([self[index - 1], self[index], self[index + 1]])
            # checking if we create any unwanted intersections
            new_edge = segment(self[index - 1], self[index + 1])
            intersection_problem = False
            for i in range(len(self) - 4):
                if new_edge.intersecting(segment(self[index + i + 2], self[index + i + 3])):
                    intersection_problem = True
                    break
            triangle[clearance_paramiter] = self[clearance_paramiter]
            if (not intersection_problem) and triangle.checkpoints([], whitelist + blacklist, clearance_paramiter):
                self.pop(index)
                if index > 0:
                    index -= 1
            else:
                index += 1
        pass
    
    def curvify(self, points: list, curve_paramiter = "curve", curve_type_paramiter = "curve_type") -> None:
        '''
        :param points: a list of all points for the polygon to avoid
        :param curve_paramiter: the paramiter used to put the data in the verticies
        :param curve_type_paramiter: the paramiter for curve type
        '''

        for index in range(len(self)):
            E1 = segment(self[index - 1], self[index])
            E2 = segment(self[index], self[index + 1])
            midpoint1 = E1.midpoint()
            midpoint2 = E2.midpoint()
            # setting up slopes and intercepts for triangle reduction
            direction = (midpoint2 - midpoint1).unit()
            triangle = polygon([midpoint1, self[index], midpoint2])
            for vertex in points:
                if triangle.contains(vertex):
                    changing_edge = segment(vector(vertex[0], vertex[1]), vertex + direction)
                    triangle[0] = changing_edge.intersection(E1)
                    triangle[2] = changing_edge.intersection(E2)
            self[index][curve_paramiter] = triangle
            self[index][curve_type_paramiter] = "bezier"
        pass

    def overlapping(self, o) -> bool:
        '''
        :param o: another polygon
        '''
        for E_self in self.edges():
            for E_o in o.edges():
                if E_self.intersecting(E_o):
                    return True
        return self.contains(o[0]) or o.contains(self[0])
    
    def rotate(self, angle: float | int) -> None:
        '''
        :param angle: the rotation angle in radians
        '''

        for index in range(len(self)):
            new_vertex = self[index].rotate(angle)
            if "curve" in self[index].attributes():
                curve = []
                for v in self[index]["curve"].verticies():
                    curve.append(v.rotate(angle))
                new_vertex["curve"] = polygon(curve)
            if "curve_type" in self[index].attributes():
                new_vertex["curve_type"] = self[index]["curve_type"]
            self.__verticies[index] = new_vertex
        
        pass

    def offset(self, v: vector) -> None:
        '''
        :param v: adds v to every single point in the polygon
        '''

        for index in range(len(self)):
            new_vertex = self[index] + v
            if "curve" in self[index].attributes():
                curve = []
                for u in self[index]["curve"].verticies():
                    curve.append(u + v)
                new_vertex["curve"] = polygon(curve)
            if "curve_type" in self[index].attributes():
                new_vertex["curve_type"] = self[index]["curve_type"]
            self.__verticies[index] = new_vertex
        
        pass

    def scale(self, scale_factor: float | int) -> None:
        '''
        :param scale_factor: the factor by which we scale the polygon
        '''

        for index in range(len(self)):
            new_vertex = scale_factor * self[index]
            if "curve" in self[index].attributes():
                curve = []
                for v in self[index]["curve"].verticies():
                    curve.append(scale_factor * v)
                new_vertex["curve"] = polygon(curve)
            if "curve_type" in self[index].attributes():
                new_vertex["curve_type"] = self[index]["curve_type"]
            self.__verticies[index] = new_vertex
        
        pass