#! /usr/bin/env python
# Author: Sean Lisse
# Definitions of fiducials and a place to store them

import collections
import numpy
from VectorMath import normalize, magnitude, perpendicular_component
from Utilities import enum, debugprint, debug_levels

COORDS=enum('X','Y','Z')

# Create a dictionary to contain our fidicual points.  Each point will be indexed by name, and will be a 3-tuple of X,Y,Z values.
fiducial_points=collections.OrderedDict()

class fiducial:
    ''' Represents a Slicer fiducial point, with name, x, y, and z values. '''
    def __init__(self,_name,_x,_y,_z): 
        self.name = _name
        self.coords = numpy.zeros((3))

        self.coords[COORDS.X] = float(_x)
        self.coords[COORDS.Y] = float(_y)
        self.coords[COORDS.Z] = float(_z)
        
def vector_from_fiducials(startfiducial, endfiducial):
    ''' Takes two points, startfiducial and endfiducial, and returns the vector from start to end. '''
    
    startarray = startfiducial.coords
    endarray = endfiducial.coords
    result = endarray - startarray
    return result

def print_all_fiducials(fiducial_list):
        for key in fiducial_points.iterkeys():
            fid = fiducial_points[key]            
            print(fid.name + " at x:" + str(fid.x) + ", y:" + str(fid.y) + ", z:" + str(fid.z))
            
def recenter_fiducials(new_origin, points_to_recenter):
    ''' Given a point which will be the new coordinate origin (i.e. new 0,0,0), translate all points so that it is made so. '''
    
    recenter_vector = vector_from_fiducials(new_origin, fiducial("origin",0,0,0))
    
    for key in points_to_recenter.iterkeys():
        fid = fiducial_points[key]
        fid.coords = fid.coords + recenter_vector
        
def reorient_fiducials(new_x_axis, new_y_axis, new_z_axis, points_to_reorient):
    ''' Given a new set of axes expressed in the *old* coordinate system, rotate the fiducial points so that they now lie along the new axes. ''' 
    
    ROUGHLY_ZERO=0.01 #Fudge factor used in verifying that axes are indeed orthogonal
    
    if ((magnitude(new_x_axis) != 1) or (magnitude(new_y_axis) != 1) or magnitude (new_z_axis) != 1):
        debugprint("WARNING - requested reorientation of fiducials with non-normalized axes!", debug_levels.ERRORS)
        debugprint("X magnitude: " + str(magnitude(new_x_axis))
                   + ", Y magnitude: " + str(magnitude (new_y_axis))
                   + ", Z magnitude: " + str(magnitude (new_z_axis)), debug_levels.DETAILED_DEBUG)
    
    if ((numpy.dot(new_x_axis, new_y_axis) > ROUGHLY_ZERO) 
        or (numpy.dot(new_x_axis, new_z_axis) > ROUGHLY_ZERO)
        or (numpy.dot(new_y_axis, new_z_axis) > ROUGHLY_ZERO)):
        debugprint("WARNING: Correcting axes to be fully orthogonal, leaving the X axis unchanged!", debug_levels.ERRORS)
        debugprint("WARNING: Requested new axes: " + str(new_x_axis) 
                   + "," + str(new_y_axis)
                   + "," + str(new_z_axis)
                   , debug_levels.DETAILED_DEBUG)
        
        # Fix this problem by redefining Y so it's fully perpendicular to X, and Z so it's fully perpindicular to both.
        new_y_axis = normalize(perpendicular_component(new_x_axis, new_y_axis))
        new_z_axis = normalize(perpendicular_component(new_x_axis, new_z_axis))
        new_z_axis = normalize(perpendicular_component(new_y_axis, new_z_axis))
 
        debugprint("WARNING: Actual new axes: " + str(new_x_axis) 
                   + "," + str(new_y_axis)
                   + "," + str(new_z_axis)
                   , debug_levels.DETAILED_DEBUG)
    
    for key in points_to_reorient.iterkeys():
        fid = fiducial_points[key]
        
        debugprint("Reorienting fiducials!", debug_levels.DETAILED_DEBUG)
        debugprint("Coordinate " + str(fid.coords), debug_levels.DETAILED_DEBUG)
         
        original_coords = fid.coords.copy()
        
        # Cheating a little bit here and pretending that XYZ coordinates are XYZ vectors.  The math works fine, as we are rotating around the origin.
        fid.coords[COORDS.X] = numpy.dot(new_x_axis, original_coords)
        fid.coords[COORDS.Y] = numpy.dot(new_y_axis, original_coords)
        fid.coords[COORDS.Z] = numpy.dot(new_z_axis, original_coords) 
        
        debugprint("Becomes: " + str(fid.coords), debug_levels.DETAILED_DEBUG)