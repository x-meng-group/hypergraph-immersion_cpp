from Vector import vector
import matplotlib.pyplot as plt
import numpy as np

class segment:

    def __init__(self, u: vector, v: vector):
        self.__u = u
        self.__v = v
        pass

    @classmethod
    def orthogonal(cls, point: vector, line, unit: bool = False):
        '''
        :param point: a point in 2d space
        :param line: an edge in 2d space (doesn't have to be an edge class)
        :param unit: makes the line have unit length if true
        '''
        perp = vector(line[1][1] - line[0][1], line[0][0] - line[1][0])
        if unit:
            return cls(point, (point + perp).unit())
        return cls(point, point + perp)

    def __getitem__(self, item):
        if item == "u" or item == "U" or item == 0:
            return self.__u
        elif item == "v" or item == "V" or item == 1:
            return self.__v
        raise ValueError("improper index")
    
    def __setitem__(self, attribute, value) -> None:
        '''
        :param attribute: the attribute you want to set. use "x", "X" or 0 to change the x cordinate and "y", "Y", or 1 to change the y cordinate
        :param value: what you want to set the attribute to
        '''
        if attribute == "u" or attribute == 0 or attribute == "U":
            self.__u = value
        elif attribute == "v" or attribute == 1 or attribute == "V":
            self.__v = value
        pass
    
    def __iter__(self):
        yield self.__u
        yield self.__v
        pass

    def direction(self) -> vector:
        return (self.__v - self.__u).unit()
    
    def equation_params(self):
        a = self.__v["y"] - self.__u["y"]
        b = self.__u["x"] - self.__v["x"]
        c = (self.__v["x"] - self.__u["x"]) * self.__u["y"] + (self.__u["y"] - self.__v["y"]) * self.__u["x"]
        return a, b, c
    
    def __abs__(self):
        return abs(self.__u - self.__v)
    
    def parallel(self, o) -> bool:
        '''
        :param o: another edge (doesn't nececarily have to be an edge class)
        '''
        return (self.__v["y"] - self.__u["y"]) * (o[1][0] - o[0][0]) == (o[1][1] - o[0][1]) * (self.__v["x"] - self.__u["x"])
    
    def intersection(self, o) -> vector:
        '''
        :param o: another edge (must be edge class)
        '''
        if self.parallel(o):
            return None
        a1, b1, c1 = self.equation_params()
        a2, b2, c2 = o.equation_params()
        return vector(b1 * c2 - c1 * b2, c1 * a2 - c2 * a1) / (a1 * b2 - a2 * b1)
    
    def point_distance(self, point: vector) -> float:
        '''
        :param point: a point in 2d space
        '''
        closest_midpoint = self.intersection(segment.orthogonal(point, self))
        if self.in_segment(closest_midpoint):
            return float(point.distance(closest_midpoint))
        u_distance = float(point.distance(self.__u))
        v_distance = float(point.distance(self.__v))
        if u_distance < v_distance:
            return u_distance
        return v_distance
    
    def line_distance(self, point: vector) -> float:
        '''
        :param point: a point in 2d space
        '''
        closest_midpoint = self.intersection(segment.orthogonal(point, self))
        return float(point.distance(closest_midpoint))
    
    def in_segment(self, point) -> bool:
        '''
        :param point: the point we are checking
        '''
        l = abs(self)
        return l >= self.__u.distance(point) and l >= self.__v.distance(point)
    
    def within_segment(self, point) -> bool:
        '''
        :param point: the point we are checking
        '''
        l = abs(self)
        return l > self.__u.distance(point) and l > self.__v.distance(point)
    
    def midpoint(self) -> vector:
        return (self.__u + self.__v) / 2
    
    def plot(self, color = "black", thickness = 1, line_type: str = "solid") -> None:
        '''
        :param color: the color you want your line to be
        :param thickness: the thickness of the line
        :param line_type: "solid" for a solid line, "dashed" for a dashed line, and "dotted" for a dotted line
        '''

        plt.plot([self.__u[0], self.__v[0]], [self.__u[1], self.__v[1]], color = color, linewidth = thickness, linestyle = line_type)
        pass

    def arrowvertices(self, 
                  shave_length: float | int = 0,
                  arrowhead_length: float | int = 0.1,
                  arrowhead_width: float | int = 0.1,
                  thickness: float | int = 0.05
                  ) -> list[vector]:
        '''
        This gathers the points required for plotting the arrow. The arrowhead at the "v" vector (i.e. the arrow goes from self["u"] to self["v"]).
        Note that an arrowhead with no zero length or zero width will cause the arrowhead to not be plotted.
        All variables refer to plotted units, NOT pixel values

        :param shave_length: a positive number (must be no more than half the length of the line). Allows the base and head of the arrow to not touch the intended vector
        :param arrowhead_length: the length of the arrowhead (non-negative number), applied after shaving. The remaining arrow still needs to have non-negative length
        :param arrowhead_width: the width of the arrowhead (non-negative number), if zero, length of the arrowhead will still be shaved off of the segment
        :param thickness: the thickness of the arrow body. If zero, the arrow body will not be plotted
        '''

        direction = self.direction()
        ortho = vector((-1) * direction["y"], direction["x"]) # the direction vector rotated by 90 degrees counterclockwise
        
        u = self.__u + (shave_length * direction)
        arrow_apex = self.__v - (shave_length * direction)
        v = arrow_apex - (arrowhead_length * direction)

        vertices = []

        # setting up vertices for the arrow body
        if thickness > 0:
            thickness_offset = (thickness / 2) * ortho
            vertices += [v - thickness_offset, u - thickness_offset, u + thickness_offset, v + thickness_offset]
        
        # setting up vertices for the arrowhead
        if arrowhead_length > 0 and arrowhead_width > 0:
            arrowhead_offset = (arrowhead_width / 2) * ortho
            vertices += [v + arrowhead_offset, arrow_apex, v - arrowhead_offset]
        
        return vertices

    def arrowplot(self, 
                  shave_length: float | int = 0,
                  arrowhead_length: float | int = 0.1,
                  arrowhead_width: float | int = 0.1,
                  thickness: float | int = 0.05,
                  color: any = "black",
                  opacity: float | int = 1,
                  zorder: int = 1
                  ) -> None:
        '''
        This plots a line as an arrow. The arrowhead at the "v" vector (i.e. the arrow goes from self["u"] to self["v"]).
        Note that an arrowhead with no zero length or zero width will cause the arrowhead to not be plotted.
        All variables refer to plotted units, NOT pixel values

        :param shave_length: a positive number (must be no more than half the length of the line). Allows the base and head of the arrow to not touch the intended vector
        :param arrowhead_length: the length of the arrowhead (non-negative number), applied after shaving. The remaining arrow still needs to have non-negative length
        :param arrowhead_width: the width of the arrowhead (non-negative number), if zero, length of the arrowhead will still be shaved off of the segment
        :param thickness: the thickness of the arrow body. If zero, the arrow body will not be plotted
        :param color: the color of the arrow
        :param opacity: the opacity of the arrow (between 0 and 1, inclusive)
        :param zorder: used for what goes over what
        '''

        vertices = self.arrowvertices(shave_length = shave_length, arrowhead_length = arrowhead_length, arrowhead_width = arrowhead_width, thickness = thickness)
        
        if len(vertices) > 0:

            # setting up X and Y for plotting
            X = []
            Y = []
            vertices.append(vertices[0])
            for vertex in vertices:
                X.append(vertex["x"])
                Y.append(vertex["y"])
            
            # plotting
            plt.fill(X, Y, color = color, alpha = opacity, linewidth = 0, zorder = zorder)
        
        pass

    def show(self, color = "black", thickness = 1, line_type: str = "solid") -> None:
        '''
        :param color: the color you want your line to be
        :param thickness: the thickness of the line
        :param line_type: "solid" for a solid line, "dashed" for a dashed line, and "dotted" for a dotted line
        '''

        plt.figure()
        self.plot(color, thickness, line_type)
        plt.show()
        pass

    def intersecting(self, o) -> bool:
        '''
        :param o: another line class
        '''

        # old
        #if self.parallel(o): 
            #return False
        #intersection = self.intersection(o)
        #return self.in_segment(intersection) and o.in_segment(intersection)

        # new
        return self.crosses(*o.equation_params()) and o.crosses(*self.equation_params())
    
    def reverse(self):
        return segment(self.__v, self.__u)
    
    def twist(self, angle: float | int, pivot: str | int = "u"):
        '''
        This function creates a line that is pivoted around one of the points

        :param angle: the angle you want to rotate by in radians
        :param pivot: which vector you want to pivot around (based on the index system)
        '''

        if pivot == "u" or pivot == "U" or pivot == 0:
            u = vector(self.__u["x"], self.__u["y"])
            v = vector(self.__v["x"], self.__v["y"])
            reverse = False
        elif pivot == "v" or pivot == "V" or pivot == 1:
            u = vector(self.__v["x"], self.__v["y"])
            v = vector(self.__u["x"], self.__u["y"])
            reverse = True
        else:
            raise ValueError("The pivot must be an index for one of the vectors in the line.")

        E = v - u
        O = vector((-1) * E["y"], E["x"]) # 90 degree rotation of E

        v += (O * float(np.sin(angle))) + (E * (float(np.cos(angle)) - 1))

        if reverse:
            u, v = v, u
        
        return segment(u, v)
    
    def extend(self, l: int | float, origin: str | int = "u"):
        '''
        This function extends a line from the origin by a given length, negative l will retract the line
        returns another segment

        :param l: the length you want to add to the line
        :param origin: which point in the line you want to keep in place
        '''

        if origin == "u" or origin == "U" or origin == 0:
            u = vector(self.__u["x"], self.__u["y"])
            v = vector(self.__v["x"], self.__v["y"])
            reverse = False
        elif origin == "v" or origin == "V" or origin == 1:
            u = vector(self.__v["x"], self.__v["y"])
            v = vector(self.__u["x"], self.__u["y"])
            reverse = True
        else:
            raise ValueError("The origin must be an index for one of the vectors in the line.")
        
        v += l * (v - u).unit()

        if reverse:
            u, v = v, u
        
        return segment(u, v)
    
    def crosses(self, a, b, c) -> bool:
        '''
        takes the paramiters for a segment and checks for crossing
        if you just have the segment but not the params, just do:
        ...[segment1].crosses(*[segment2].equation_params())
        You need to use the * at the begining of the input to unpack it, otherwise an error will be raised

        :param a: the a in ax + by + c = 0
        :param b: the b in ax + by + c = 0
        :param c: the c in ax + by + c = 0
        '''

        A = vector(a, b)

        return abs(A * (self.__u + self.__v) + (2 * c)) <= abs(A * (self.__v - self.__u))
    