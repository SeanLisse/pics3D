#! /usr/bin/env python
# Author: Sean Lisse
# Definitions of fiducials and a place to store them

import numpy
from VectorMath import normalize, magnitude, perpendicular_component
from Utilities import enum, debugprint, debug_levels

COORDS=enum('X','Y','Z')

PUBIC_SYMPHYSIS_NAME="PS"
SC_JOINT_NAME="SCJ"
LEFT_ISCHIAL_SPINE_NAME="L_IS"
RIGHT_ISCHIAL_SPINE_NAME="R_IS"
INTER_ISCHIAL_SPINE_NAME="IIS"

REFERENCE_POINT_NAMES={PUBIC_SYMPHYSIS_NAME, SC_JOINT_NAME, LEFT_ISCHIAL_SPINE_NAME, RIGHT_ISCHIAL_SPINE_NAME, INTER_ISCHIAL_SPINE_NAME}

# This is the pattern used to match fiducial names and parse out the row number (from apex, A) and column number (from left, L).
# We want to find the part of the string that starts with an A followed by some numerals, then an L followed by some numerals.
INDEX_PATTERN='A(\d+)L(\d+)'

class fiducial:
    name = ""
    coords = []
    
    ''' Represents a Slicer fiducial point, with name, x, y, and z values. '''
    def __init__(self,_name, _x,_y,_z): 
        self.name = _name
        self.coords = numpy.zeros((3))

        self.coords[COORDS.X] = float(_x)
        self.coords[COORDS.Y] = float(_y)
        self.coords[COORDS.Z] = float(_z)
        
    def to_string(self):
        if (self == None): return "[None]"
        
        retstring = self.name + ":"
        retstring += "["
        retstring += str(self.coords[COORDS.X])
        retstring += ","
        retstring += str(self.coords[COORDS.Y])
        retstring += ","
        retstring += str(self.coords[COORDS.Z])
        retstring += "]"
        
        return retstring
        
def vector_from_fiducials(startfiducial, endfiducial):
    ''' Takes two points, startfiducial and endfiducial, and returns the vector from start to end. '''
    
    startarray = startfiducial.coords
    endarray = endfiducial.coords
    result = endarray - startarray
    return result

def print_all_fiducials(fiducial_list):
        for key in fiducial_list.iterkeys():
            fid = fiducial_list[key]            
            print(fid.name + " at x:" + str(fid.x) + ", y:" + str(fid.y) + ", z:" + str(fid.z))
            
def recenter_fiducials(new_origin, points_to_recenter):
    ''' Given a point which will be the new coordinate origin (i.e. new 0,0,0), translate all points so that it is made so. '''
    
    recenter_vector = vector_from_fiducials(new_origin, fiducial("origin",0,0,0))
    
    for key in points_to_recenter.iterkeys():
        fid = points_to_recenter[key]
        fid.coords = fid.coords + recenter_vector
        
def reorient_fiducials(new_x_axis, new_y_axis, new_z_axis, points_to_reorient):
    ''' Given a new set of axes expressed in the *old* coordinate system, rotate the fiducial points so that they now lie along the new axes. ''' 
    
    ROUGHLY_ZERO=0.05 #Fudge factor used in verifying that axes are indeed orthogonal
    
    # Give a margin of 0.01 before warning about non-unit magnitude axes.
    if ((magnitude(new_x_axis) < 0.99) or (magnitude(new_y_axis) < 0.99) or (magnitude(new_z_axis) < 0.99)
        or (magnitude(new_x_axis) > 1.01) or (magnitude(new_y_axis) > 1.01) or (magnitude(new_z_axis) > 1.01)):
        debugprint("WARNING - requested reorientation of fiducials with non-normalized axes!", debug_levels.ERRORS)
        debugprint("X magnitude: " + str(magnitude(new_x_axis))
                   + ", Y magnitude: " + str(magnitude (new_y_axis))
                   + ", Z magnitude: " + str(magnitude (new_z_axis)), debug_levels.DETAILED_DEBUG)
    
    # Check for orthogonality of the new axis
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
        fid = points_to_reorient[key]
        
        debugprint("Reorienting fiducials!", debug_levels.DETAILED_DEBUG)
        debugprint("Coordinate " + str(fid.coords), debug_levels.DETAILED_DEBUG)
         
        original_coords = fid.coords.copy()
        
        # Cheating a little bit here and pretending that XYZ coordinates are XYZ vectors.  The math works fine, as we are rotating around the origin.
        fid.coords[COORDS.X] = numpy.dot(new_x_axis, original_coords)
        fid.coords[COORDS.Y] = numpy.dot(new_y_axis, original_coords)
        fid.coords[COORDS.Z] = numpy.dot(new_z_axis, original_coords) 
        
        debugprint("Becomes: " + str(fid.coords), debug_levels.DETAILED_DEBUG)
        
def get_fiducial_row_and_column(fid_point):
    ''' Parse a fiducial point's name to find out what its row and column are.  
    Returns a [row, column] tuple.  E.g. if the point is A1L1, returns [1,1].
    Returns [None, None] if it cannot find them.'''
     
    # Grab the regular expressions library "re" so we can use it to parse fiducial names
    import re
       
    # Ignore reference points
    if (fid_point.name in REFERENCE_POINT_NAMES):
        return [None, None]

    searchresults = re.search(INDEX_PATTERN, fid_point.name)
    
    if (searchresults == None): return [None, None]
    
    rownum = searchresults.groups()[0] # the first group we grab should be the number after the 'A', so the row number.
    colnum = searchresults.groups()[1] # The second group we grab should be the number after the 'L', so the column number.
    
    return [int(rownum), int(colnum)]

def get_fiducial_list_by_row_and_column(fids):
    ''' Given an orderedDict fids, iterate through it and parse out all names by row and column.  Return a list of rows, each of which is a list of fiducials by column. '''
    
    # Rows go from Apex (A1) to near the hiatus.
    # Columns go from leftmost (L1) to rightmost (e.g. L10).
    
    # The below two dictionaries will be indexed by row (e.g. leftmostpoints[1] will be the leftmost point in row 1). 
    rows = list()
    
    # print ("Created rows: " + str(rows))
    
    # There is no row "zero", so we'll make that index a None-value.
    rows.append(None)
    
    for fid_name in fids:
        [row,column] = get_fiducial_row_and_column(fids[fid_name])
        
        if (row == None): continue
        
        # Add 1 since there is no row 0.
        while (len(rows) < (row + 1)): rows.append(list())
        
        while (len(rows[row]) < (column + 1)): rows[row].append(None)
        
        rows[row][column] = fids[fid_name]
        
        
    # print ("Returning rows: " + str(rows))
    return rows