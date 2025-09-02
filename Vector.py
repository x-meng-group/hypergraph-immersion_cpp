import numpy as np
import matplotlib.pyplot as plt

class vector:

    def __init__(self, x, y):
        '''
        :param x: the x value of the vector
        :param y: the y value of the vector
        '''
        self.__x = x
        self.__y = y

        # used for associating important data to the vector
        self.__attributes = dict()

        pass

    def __iter__(self):
        yield self.__x
        yield self.__y
        pass

    @classmethod
    def from_angle(cls, angle, magnitude = 1):
        '''
        :param angle: the angle you want in radians
        :param magnitude: the magnitude of you vector
        '''
        
        return vector(magnitude * float(np.cos(angle)), magnitude * float(np.sin(angle)))
    
    @classmethod
    def i(cls):
        return vector(1, 0)
    
    @classmethod
    def j(cls):
        return vector(0, 1)
    
    def unit(self):
        return self / abs(self)

    def __getitem__(self, attribute):
        '''
        :param attribute: allows access to attributes. "x", "X" or 0 gives the x cordinate and "y", "Y", or 1 gives the y cordinate
        '''
        if attribute == "x" or attribute == 0 or attribute == "X":
            return self.__x
        elif attribute == "y" or attribute == 1 or attribute == "Y":
            return self.__y
        return self.__attributes[attribute]
    
    def __setitem__(self, attribute, value) -> None:
        '''
        :param attribute: the attribute you want to set. use "x", "X" or 0 to change the x cordinate and "y", "Y", or 1 to change the y cordinate
        :param value: what you want to set the attribute to
        '''
        if attribute == "x" or attribute == 0 or attribute == "X":
            self.__x = value
        elif attribute == "y" or attribute == 1 or attribute == "Y":
            self.__y = value
        else:
            self.__attributes[attribute] = value
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
    
    def angle(self) -> float:
        if self.__x == 0:
            if self.__y > 0:
                return np.pi / 2
            elif self.__y < 0:
                return 3 * np.pi / 2
            return 0
        elif self.__y == 0:
            if self.__x >= 0:
                return 0
            return np.pi
        angle = float(np.arctan(abs(self.__y / self.__x)))
        if self.__x > 0:
            if self.__y > 0:
                return angle
            return (2 * np.pi) - angle
        elif self.__y > 0:
            return np.pi - angle
        return np.pi + angle
    
    def __add__(self, o):
        return vector(self.__x + o[0], self.__y + o[1])
    
    def __radd__(self, o):
        return vector(self.__x + o[0], self.__y + o[1])
    
    def __iadd__(self, o):
        v = vector(self.__x + o[0], self.__y + o[1])
        for attribute in self.attributes():
            v[attribute] = self[attribute]
        return v
    
    def __sub__(self, o):
        return vector(self.__x - o[0], self.__y - o[1])
    
    def __rsub__(self, o):
        return vector(o[0] - self.__x, o[1] - self.__y)
    
    def __isub__(self, o):
        v = vector(self.__x - o[0], self.__y - o[1])
        for attribute in self.attributes():
            v[attribute] = self[attribute]
        return v
    
    def __mul__(self, o):
        if type(o) == int or type(o) == float:
            return vector(o * self.__x, o * self.__y)
        return self.__x * o[0] + self.__y * o[1]
    
    def __rmul__(self, o):
        if type(o) == int or type(o) == float:
            return vector(o * self.__x, o * self.__y)
        return self.__x * o[0] + self.__y * o[1]
    
    def __imul__(self, o):
        if type(o) == int or type(o) == float:
            v = vector(o * self.__x, o * self.__y)
            for attribute in self.attributes():
                v[attribute] = self[attribute]
            return v
        return self.__x * o[0] + self.__y * o[1]
    
    def __truediv__(self, o):
        if type(o) == int or type(o) == float:
            return vector(self.__x / o, self.__y / o)
        raise ValueError("vectors can only be devided by real numbers.")
    
    def __itruediv__(self, o):
        if type(o) == int or type(o) == float:
            v = vector(self.__x / o, self.__y / o)
            for attribute in self.attributes():
                v[attribute] = self[attribute]
            return v
        raise ValueError("vectors can only be devided by real numbers.")
    
    def __eq__(self, o):
        if type(o) == vector:
            return self.__x == o[0] and self.__y == o[1]
        return False
    
    def __ne__(self, o):
        if type(o) == vector:
            return self.__x != o[0] or self.__y != o[1]
        return True
    
    def copy(self, retain_attributes: bool = True):
        v = vector(self.__x, self.__y)
        if retain_attributes:
            for attribute in self.attributes():
                v[attribute] = self[attribute]
        return v
    
    def __str__(self):
        return "<" + str(self.__x) + ", " + str(self.__y) + ">"
    
    def __abs__(self):
        return (self.__x**2 + self.__y**2)**(1/2)
    
    def distance(self, o):
        '''
        :param o: any vector list or tuple you want to measure the distance from for the vector
        '''
        return abs(self - o)
    
    # In order to put vectors in sets
    def __hash__(self):
        return hash(tuple(self))
    
    def orthogonals(self, magnitude = 1):
        '''
        :param magnitude: the magnitude you want
        '''
        return magnitude * (vector(self.__y, -1 * self.__x).unit()), magnitude * (vector(-1 * self.__y, self.__x).unit())
    
    def rotate(self, angle: int | float):
        '''
        :param angle: the angle you want to rotate by in radians
        '''
        # return vector.from_angle(self.angle() + angle, abs(self)) - old

        cos = float(np.cos(angle))
        sin = float(np.sin(angle))

        return vector((self.__x * cos) - (self.__y * sin), (self.__x * sin) + (self.__y * cos))
    
    def rotate_self(self, angle: int | float) -> None:
        '''
        This function rotates the vector itself

        :param angle: the angle you want to rotate the vector by in radians
        '''

        cos = float(np.cos(angle))
        sin = float(np.sin(angle))

        x = (self.__x * cos) - (self.__y * sin)
        y = (self.__x * sin) + (self.__y * cos)

        self.__x = x
        self.__y = y

        pass
    
    def plot(self, color = "black", size = 25) -> None:
        '''
        :param color: the color of your point
        :param size: the size of your point
        '''

        plt.scatter([self.__x], [self.__y], color = color, s = [size])
        pass

    def show(self, color = "black", size = 100) -> None:
        '''
        :param color: the color of your point
        :param size: the size of your point
        '''

        plt.figure()
        self.plot(color, size)
        plt.show()
        pass

    def square_plot(self, i, j, color = "black", size = 100) -> None:
        '''
        :param i: vector to use as "unit" vector in "+x" direction (a unit is the min clearance value)
        :param j: "unit" (magnitude of min clearance value) vector in "+y" direction
        :param color: the color of your point
        :param size: the size of your point
        '''

        X = []
        Y = []
        for t in [(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)]:
            corner = self + (t[0] * i) + (t[1] * j)
            X.append(corner["x"])
            Y.append(corner["y"])
        plt.plot(X, Y)
        self.plot(color, size)
        pass

    def radplot(self, radius: int | float, color = "black", opacity: int | float = 1, zorder: int = 1, resolution: int = 72) -> None:
        '''
        This function plots a point with a specific radius.

        :param radius: the radius of the circle
        :param color: the color of your circle, defaults as black
        :param opacity: the opacity of your circle (between 0 and 1)
        :param zorder: the ordering for what goes on top of what
        :param resolution: the amount of subdivisions in the border of the circle
        '''

        if resolution <= 0:
            raise ValueError("Resolution cannot be zero or negative")

        phi = 2 * np.pi / resolution
        delta = vector(np.cos(phi), np.sin(phi))
        r = vector(radius, 0)

        X = [radius + self.__x]
        Y = [self.__y]

        for i in range(resolution - 1):

            # incrementing (instead of keeping track of the angle, we are just incrementing using trig addtion fomulas)
            r = vector((r[0] * delta[0]) - (r[1] * delta[1]), (r[0] * delta[1]) + (r[1] * delta[0]))

            X.append(r[0] + self.__x)
            Y.append(r[1] + self.__y)
        
        X.append(radius + self.__x)
        Y.append(self.__y)

        plt.fill(X, Y, color = color, alpha = opacity, zorder = zorder, linewidth = 0) # the filling step

        pass

    def strip(self):
        '''
        Returns a copy of the vector without any of it's attributes
        '''
        return vector(self.__x, self.__y)