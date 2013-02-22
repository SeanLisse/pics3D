#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from a directory tree and normalize them to the PICS system, then display the results.

# Built in library imports
from numpy import arctan, sin, cos, pi, matrix, array

# Generic custom imports 
from Utilities import enum
from Utilities import setdebuglevel, debug_levels, debugprint

# Domain specific custom imports
from Fiducials import vector_from_fiducials, COORDS
from VaginalProperties import VaginalDisplay
from VectorMath import magnitude, normalize, orthogonalize
from Graphing import show_all_graphs
from PelvicPoints import create_pelvic_points_graph

#Constants
from Fiducials import LEFT_ISCHIAL_SPINE_NAME, RIGHT_ISCHIAL_SPINE_NAME, PUBIC_SYMPHYSIS_NAME, SC_JOINT_NAME
from GraphColoring import COLORIZATION_OPTIONS

COLOR_STRAT = COLORIZATION_OPTIONS.WIDTH

# (34 degrees above horizontal is 0.5934 in radians)
DESIRED_SCIPP_ANGLE = -0.593411946

# Scale all points so that the SCIPP LINE LENGTH is equal to SCIPP_SCALE_LENGTH?
#
# WARNING WARNING - IF THIS IS TRUE, THEN ALL MEASUREMENTS BECOME RELATIVE AND ARE NO LONGER ABSOLUTE VALUES!!!
SCALE_BY_SCIPP_LINE=False

# If scaling is desired, to what length should we normalize the SCIPP line? 
SCIPP_SCALE_LENGTH=1

# Which axes go where.
# In "lisse" encoding, "X" increases to the patient's left, 
# "Y" increases to the patient's posterior, and 
# "Z" increases to the patient's superior.
#
# In "pics3d" encoding, "X" increases to the patient's posterior, 
# "Y" increases to the patient's superior, 
# and "Z" increases to the patient's left.
# 
# In "pseudo-JCS" encoding, that "X" increases to the patient's anterior, 
# "Y" increases to the patient's superior, and 
# "Z" increases to the patient's right.
# 
# In ALL of the above, we adjust the anterior-posterior axis to attempt to corect pelvic inclination to true "standing" position.
AXIS_CODING_OPTIONS = enum('lisse','pics3d', 'pseudojcs')
AXIS_CODING = AXIS_CODING_OPTIONS.lisse

def lisse_axes_matrix_fn(fiducial_points):
    # In "lisse" encoding, "X" increases to the patient's left, "Y" increases to the patient's posterior, and "Z" increases to the patient's superior.

    # We need to create a "transformation matrix".  
    # When we multiply a coordinate vector by this matrix, it will give us our coordinate under the new system.
    # To do this, we need to decide upon the new x/y/z axes, then build a matrix from their coordinates and the coordinates of the new origin.
    new_x_axis = pics_get_LR_axis(fiducial_points)
    new_y_axis = pics_get_AP_axis(fiducial_points)
    new_z_axis = pics_get_IS_axis(fiducial_points)
    
    # Since our coordinates will come to us as vectors in [X,Y,Z] format, each column of our transformation matrix will 
    # decide one of our new coordinates' elements - first column will be new x, second new y, third new z.
    # To make the matrix math work, the fourth column will be all zeros.  

    row1 = [new_x_axis[COORDS.X], new_y_axis[COORDS.X], new_z_axis[COORDS.X], 0]
    row2 = [new_x_axis[COORDS.Y], new_y_axis[COORDS.Y], new_z_axis[COORDS.Y], 0]
    row3 = [new_x_axis[COORDS.Z], new_y_axis[COORDS.Z], new_z_axis[COORDS.Z], 0]
    row4 = [0,0,0,0]    # We'll determine translation next, for now it's 0s. 
    
    debugprint("Degree of collinearity in X and Y axes: " + str(new_x_axis * new_y_axis), debug_levels.DETAILED_DEBUG)
    
    return matrix([row1, row2, row3, row4])

def pics3d_axes_matrix_fn(fiducial_points):
    # In "pics3d" encoding, "X" increases to the patient's posterior, "Y" increases to the patient's superior, and "Z" increases to the patient's left.

    # We need to create a "transformation matrix".  
    # When we multiply a coordinate vector by this matrix, it will give us our coordinate under the new system.
    # To do this, we need to decide upon the new x/y/z axes, then build a matrix from their coordinates and the coordinates of the new origin.
    new_x_axis = pics_get_AP_axis(fiducial_points)
    new_y_axis = pics_get_IS_axis(fiducial_points)
    new_z_axis = pics_get_LR_axis(fiducial_points)
    
    # Since our coordinates will come to us as vectors in [X,Y,Z] format, each column of our transformation matrix will 
    # decide one of our new coordinates' elements - first column will be new x, second new y, third new z.
    # To make the matrix math work, the fourth column will be all zeros.  

    row1 = [new_x_axis[COORDS.X], new_y_axis[COORDS.X], new_z_axis[COORDS.X], 0]
    row2 = [new_x_axis[COORDS.Y], new_y_axis[COORDS.Y], new_z_axis[COORDS.Y], 0]
    row3 = [new_x_axis[COORDS.Z], new_y_axis[COORDS.Z], new_z_axis[COORDS.Z], 0]
    row4 = [0,0,0,0]    # We'll determine translation next, for now it's 0s. 
    
    debugprint("Degree of collinearity in X and Y axes: " + str(new_x_axis * new_y_axis), debug_levels.DETAILED_DEBUG)
    
    return matrix([row1, row2, row3, row4])


def pics_get_new_origin(fiducial_points):
    ''' Find the new origin of our coordinate system using PICS methodology (i.e. recenter on the pubic symphysis). '''
    if not(fiducial_points.has_key(PUBIC_SYMPHYSIS_NAME)): raise ValueError("Cannot find pubic symphysis, so cannot set PICS origin.")
    else: 
        return fiducial_points[PUBIC_SYMPHYSIS_NAME] 

def pics_get_SCIPP_line(fiducial_points):
    ''' Determine the sacrococcygeal->inferior pubic point line ("SCIPP line").
        The SCIPP line is the line between the pubic symphysis and the sacro-coccygeal junction.'''
        
    if not(fiducial_points.has_key(SC_JOINT_NAME)):
        raise ValueError("Cannot find sacrococcygeal joint, so cannot find SCIPP line.")
    if not(fiducial_points.has_key(PUBIC_SYMPHYSIS_NAME)): 
        raise ValueError("Cannot find sacrococcygeal joint, so cannot find SCIPP line.")
    
    return vector_from_fiducials(fiducial_points[PUBIC_SYMPHYSIS_NAME], fiducial_points[SC_JOINT_NAME])

def pics_get_LR_axis(fiducial_points):
    ''' Find the new Left<->Right axis, which is simply a normalized version of the line between the ischial spines. '''
    if not(fiducial_points.has_key(LEFT_ISCHIAL_SPINE_NAME) and fiducial_points.has_key(RIGHT_ISCHIAL_SPINE_NAME)): 
        raise ValueError("Cannot find left and right ischial spines, so cannot set PICS x axis.")
    else: 
        return normalize(vector_from_fiducials(fiducial_points[RIGHT_ISCHIAL_SPINE_NAME], fiducial_points[LEFT_ISCHIAL_SPINE_NAME]))

# TODO - fix me to rotate properly around the X axis, as possible...
def pics_get_AP_axis(fiducial_points):
    ''' Find the new Anterior<->Posterior axis, which will be the SCIPP line rotated caudally 34 degrees around the pubic symphysis.'''
    
    SCIPP_line = normalize(pics_get_SCIPP_line(fiducial_points))
    
    # Determine the current angle of the SCIPP line from the horizontal
    # Do that by taking the SCIPP angle from the Y axis in the 'old' YZ plane
    SCIPP_angle_from_horiz = arctan(SCIPP_line[COORDS.Z]/SCIPP_line[COORDS.Y]) 
    
    # Determine our angular adjustment in order to reach 34 degrees above the horizontal for the SCIPP line
   
    angle_adjustment = DESIRED_SCIPP_ANGLE - SCIPP_angle_from_horiz
    
    debugprint("SCIPP AP to IS angle is " + str(SCIPP_angle_from_horiz * 180 / pi), debug_levels.DETAILED_DEBUG)
    debugprint("Adjustment AP to IS angle is " + str(angle_adjustment * 180 / pi), debug_levels.DETAILED_DEBUG)
                         
    # ... then build in the correction.
    # Notice that in order to rotate the SCIPP line *up*, we have to rotate our reference system (aka new y) *down*, 
    # thus the inversion with a -1 multiplier.
    # This isn't perfect because ideally we'd be using the *new* z axis for the angle measurement, not the *old* one.  But in order to get the
    # new z axis, we need the new y axis.  So, we rotate along the old z axis instead.
    #
    # FIXME - This would be better if we could rotate about the new X axis, instead of the old.
    new_AP_vector = normalize([0, -1 * cos(angle_adjustment), sin(angle_adjustment)])   
    
    debugprint("New AnteroPosterior vector is " +str(new_AP_vector))
      
    return new_AP_vector

def pics_get_IS_axis(fiducial_points):
    ''' Find the new Inferior<->Superior axis, which is orthogonal to the new x and y axes.  Depends on those axes being definable without reference to the z axis.'''
    
    return orthogonalize(pics_get_LR_axis(fiducial_points), pics_get_AP_axis(fiducial_points))

def transform_coords_by_matrix(coords, matrix):
    ''' Given a transformation matrix and a set of coordinates, return the coordinates transformed by the matrix. '''
    coords_vector = [coords[COORDS.X],coords[COORDS.Y],coords[COORDS.Z], 1]
    
    return array((coords_vector * matrix).tolist()[0])

def pics_generate_transformation_matrix(vag_props):
    ''' Generate a transformation matrix that we can use to translate points from radiological coordinates into pics coordinates.
        To do this, we compute our pics x,y, and z axes as described in the radiological coordinate system, find our new origin point, 
        and create a matrix from that information.  NO scaling for now - but we may reconsider this in the future.'''
    
    fiducial_points = vag_props._fiducial_points

    if (AXIS_CODING == AXIS_CODING_OPTIONS.lisse):
        transform_matrix=lisse_axes_matrix_fn(fiducial_points)

    if (AXIS_CODING == AXIS_CODING_OPTIONS.pics3d):
        transform_matrix=pics3d_axes_matrix_fn(fiducial_points)
        
    # To find out how much to translate each old point to the new coordinate system,
    # we find the vector from the old origin (0,0,0) to the new origin.
    # Our origin translation becomes the new fourth row, *after* being converted to the new coordinate system.
    new_origin = pics_get_new_origin(fiducial_points).coords
    origin_translation = [0,0,0] - new_origin
    row4 = [origin_translation[COORDS.X], origin_translation[COORDS.Y], origin_translation[COORDS.Z], 1] * transform_matrix
    transform_matrix = matrix([transform_matrix[0].tolist()[0], 
                               transform_matrix[1].tolist()[0],
                               transform_matrix[2].tolist()[0],
                               row4.tolist()[0]])
     
    debugprint("Transformation Matrix: " + str(transform_matrix.tolist()), debug_levels.DETAILED_DEBUG)
    
    debugprint("New origin in old coordinates: " + str(new_origin), debug_levels.DETAILED_DEBUG)
    debugprint("New origin in new coordinates: " + str(transform_coords_by_matrix(new_origin, transform_matrix)), debug_levels.DETAILED_DEBUG)

    return transform_matrix

def pics_normalize_to_SCIPP_line(vag_props):
    ''' Scale all points toward/away from the origin so that the length of the SCIPP line is equal to the constant SCIPP_SCALE. ''' 
    
    fid_points = vag_props._fiducial_points
    
    SCIPP_line = pics_get_SCIPP_line(fid_points)
    
    scale_factor = SCIPP_SCALE_LENGTH/magnitude(SCIPP_line)
    
    scale_matrix = matrix([[scale_factor,0,0,0],
                              [0,scale_factor,0,0],
                              [0,0,scale_factor,0],
                              [0,0,0,0]])
    
    for fid in fid_points:
        fid_points[fid].coords = transform_coords_by_matrix(fid_points[fid].coords, scale_matrix)

def pics_recenter_and_reorient(vag_props):
    ''' Rotate, translate, and (someday perhaps) scale all of our fiducial points to fit the PICS reference system. ''' 

    fid_points = vag_props._fiducial_points

    ### Here we encode and graph by minimum distance from one of the P->IS lines.        
    if not (fid_points.has_key(PUBIC_SYMPHYSIS_NAME) 
        and fid_points.has_key(LEFT_ISCHIAL_SPINE_NAME) 
        and fid_points.has_key(RIGHT_ISCHIAL_SPINE_NAME)
        and fid_points.has_key(SC_JOINT_NAME)):

        print("Error!  Cannot find one of the points named: " + PUBIC_SYMPHYSIS_NAME 
              + ", " + SC_JOINT_NAME 
              + ", " + LEFT_ISCHIAL_SPINE_NAME 
              + ", or " + RIGHT_ISCHIAL_SPINE_NAME
              + " in file " + filename)   
        return

    transformation_matrix = pics_generate_transformation_matrix(vag_props)
 
    for fid in fid_points:
        fid_points[fid].coords = transform_coords_by_matrix(fid_points[fid].coords, transformation_matrix)

    if SCALE_BY_SCIPP_LINE:
        pics_normalize_to_SCIPP_line(vag_props)

def pics_verify(vag_props):
    
    fid_points = vag_props._fiducial_points
    
    # Determine the sacrococcygeal->inferior pubic point line ("SCIPP line")
    SCIPP_line = normalize(pics_get_SCIPP_line(fid_points))
    
    # Determine the current angle of the SCIPP line from the horizontal
    # Do that by taking the SCIPP angle from the Y axis in the 'old' YZ plane
    SCIPP_angle_from_horiz = arctan(SCIPP_line[COORDS.Z]/SCIPP_line[COORDS.Y])
    
    debugprint("Final SCIPP angle from horizontal is: " + str(SCIPP_angle_from_horiz * 180 /pi ) 
               + " degrees and should be: " + str(DESIRED_SCIPP_ANGLE * 180 / pi) + " degrees", debug_levels.DETAILED_DEBUG)
    


#####################
### DEFAULT MAIN PROC
#####################  

if __name__ == '__main__':
        
    from sys import argv
     
    setdebuglevel(debug_levels.DETAILED_DEBUG) 
    
    if len(argv) < 2: 
        print "Need to supply mrml file name argument."
    else:
        
        # Use a single graph to show all inputs
        graph = None
        
        for i in range(1,len(argv)):
            filename = argv[i]
        
            debugprint('Now starting PICS pelvic points program',debug_levels.BASIC_DEBUG)
                        
            vag_props = VaginalDisplay(filename, COLOR_STRAT)        
            vag_props.initialize_from_MRML(filename)
            
            pics_recenter_and_reorient(vag_props)
                
            pics_verify(vag_props)
                
            graph = create_pelvic_points_graph(graph, vag_props, filename)
            
            print(vag_props.to_string())
                            
        show_all_graphs()
            
        debugprint('Now leaving pelvic points program',debug_levels.BASIC_DEBUG)
