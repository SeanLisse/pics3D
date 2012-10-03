#! /usr/bin/env python
# Author: Sean Lisse
# Definitions of fiducials and a place to store them

import collections
import numpy

# Create a dictionary to contain our fidicual points.  Each point will be indexed by name, and will be a 3-tuple of X,Y,Z values.
fiducial_points=collections.OrderedDict()

class fiducial:
    ''' Represents a Slicer fiducial point, with name, x, y, and z values. '''
    def __init__(self,_name,_x,_y,_z): 
        self.name = _name
        self.x = _x
        self.y = _y
        self.z = _z 
        self.coords = numpy.zeros((3))

        self.coords[0] = float(_x)
        self.coords[1] = float(_y)
        self.coords[2] = float(_z)
        
def distance_vector(startfiducial, endfiducial):
    ''' Takes two points, startfiducial and endfiducial, and returns the vector from start to end. '''
    
    startarray = startfiducial.coords
    endarray = endfiducial.coords
    result = endarray - startarray
    return result