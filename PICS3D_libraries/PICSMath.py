#! /usr/bin/env python
# Author: Sean Lisse
# Collection of math scripts to transform fiducials into the PICS3D system.

# Built in library imports
from numpy import arctan, sin, cos, matrix, array

# Generic custom imports 
from Utilities import debug_levels, debugprint, rad_to_degrees

# Domain specific custom imports
from Fiducials import vector_from_fiducials 
from VectorMath import magnitude, normalize, orthogonalize, get_angle_between

# Constants
from Options import COORDS, DESIRED_SCIPP_ANGLE, AXIS_CODING, AXIS_CODING_OPTIONS, AXIS_CODING_AP, AXIS_CODING_IS
from Options import SCALE_BY_SCIPP_LINE, SCALE_BY_IIS_LINE, SCIPP_SCALE_LENGTH, IIS_SCALE_LENGTH
from Options import LEFT_ISCHIAL_SPINE_NAME, RIGHT_ISCHIAL_SPINE_NAME, PUBIC_SYMPHYSIS_NAME, SC_JOINT_NAME

def lisse_axes_matrix_fn(vag_props):
    ''' In "lisse" encoding, "X" increases to the patient's left, "Y" increases to the patient's posterior, and "Z" increases to the patient's superior. '''

    # We need to create a "transformation matrix".  
    # When we multiply a coordinate vector by this matrix, it will give us our coordinate under the new system.
    # To do this, we need to decide upon the new x/y/z axes, then build a matrix from their coordinates and the coordinates of the new origin.
    new_x_axis = pics_get_LR_axis(vag_props)
    new_y_axis = pics_get_AP_axis(vag_props)
    new_z_axis = pics_get_IS_axis(vag_props)
        
    # Since our coordinates will come to us as vectors in [X,Y,Z] format, each column of our transformation matrix will 
    # decide one of our new coordinates' elements - first column will be new x, second new y, third new z.
    # To make the matrix math work, the fourth column will be all zeros.  

    row1 = [new_x_axis[COORDS.X], new_y_axis[COORDS.X], new_z_axis[COORDS.X], 0]
    row2 = [new_x_axis[COORDS.Y], new_y_axis[COORDS.Y], new_z_axis[COORDS.Y], 0]
    row3 = [new_x_axis[COORDS.Z], new_y_axis[COORDS.Z], new_z_axis[COORDS.Z], 0]
    row4 = [0,0,0,0]    # We'll determine translation next, for now it's 0s. 
    
    debugprint("Degree of collinearity in X and Y axes: " + str(new_x_axis * new_y_axis), debug_levels.DETAILED_DEBUG)
    
    return matrix([row1, row2, row3, row4])

def pics3d_axes_matrix_fn(vag_props):
    # In "pics3d" encoding, "X" increases to the patient's posterior, "Y" increases to the patient's superior, and "Z" increases to the patient's left.

    # We need to create a "transformation matrix".  
    # When we multiply a coordinate vector by this matrix, it will give us our coordinate under the new system.
    # To do this, we need to decide upon the new x/y/z axes, then build a matrix from their coordinates and the coordinates of the new origin.
    new_x_axis = pics_get_AP_axis(vag_props)
    new_y_axis = pics_get_IS_axis(vag_props)
    new_z_axis = pics_get_LR_axis(vag_props)
    
    # Since our coordinates will come to us as vectors in [X,Y,Z] format, each column of our transformation matrix will 
    # decide one of our new coordinates' elements - first column will be new x, second new y, third new z.
    # To make the matrix math work, the fourth column will be all zeros.  

    row1 = [new_x_axis[COORDS.X], new_y_axis[COORDS.X], new_z_axis[COORDS.X], 0]
    row2 = [new_x_axis[COORDS.Y], new_y_axis[COORDS.Y], new_z_axis[COORDS.Y], 0]
    row3 = [new_x_axis[COORDS.Z], new_y_axis[COORDS.Z], new_z_axis[COORDS.Z], 0]
    row4 = [0,0,0,0]    # We'll determine translation next, for now it's 0s. 
    
    debugprint("Degree of collinearity in X and Y axes: " + str(new_x_axis * new_y_axis), debug_levels.DETAILED_DEBUG)
    
    return matrix([row1, row2, row3, row4])

def set_pelvic_tilt_correction_info(vag_props):
    
    # Encoding from Slicer: RAS (X = Right, Y = Anterior, Z = Superior)    
    LR_axis_vector = [-1,0,0] # our axis vector X increases to the *left*
    AP_axis_vector = [0,-1,0] # our axis vector Y increases *posteriorly*
    IS_axis_vector = [0,0,1] # our axis vector Z increases *superiorly*

    # Compare those 'standard' radiologic coordinate axes with the coordinate axes computed from our fiducial points.
    LR_rot_angle = get_angle_between(LR_axis_vector, pics_get_LR_axis(vag_props))
    AP_rot_angle = get_angle_between(AP_axis_vector, pics_get_AP_axis(vag_props))
    IS_rot_angle = get_angle_between(IS_axis_vector, pics_get_IS_axis(vag_props))
    
    vag_props._pelvic_tilt_correction_angle_about_LR_axis = LR_rot_angle
    vag_props._pelvic_tilt_correction_angle_about_AP_axis = AP_rot_angle
    vag_props._pelvic_tilt_correction_angle_about_IS_axis = IS_rot_angle

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

def pics_get_LR_axis(vag_props):
    
    fiducial_points = vag_props._fiducial_points
    
    ''' Find the new Left<->Right axis, which is simply a normalized version of the line between the ischial spines. '''
    if not(fiducial_points.has_key(LEFT_ISCHIAL_SPINE_NAME) and fiducial_points.has_key(RIGHT_ISCHIAL_SPINE_NAME)): 
        raise ValueError("Cannot find left and right ischial spines, so cannot set PICS x axis.")
    else: 
        
        new_axis = normalize(vector_from_fiducials(fiducial_points[RIGHT_ISCHIAL_SPINE_NAME], fiducial_points[LEFT_ISCHIAL_SPINE_NAME]))
        
        return new_axis

# TODO - fix me to rotate properly around the X axis, as possible...
def pics_get_AP_axis(vag_props):
    ''' Find the new Anterior<->Posterior axis, which will be the SCIPP line rotated caudally 34 degrees around the pubic symphysis.'''
    
    fiducial_points = vag_props._fiducial_points
    
    SCIPP_line = normalize(pics_get_SCIPP_line(fiducial_points))
    
    # Determine the current angle of the SCIPP line from the horizontal
    # Do that by taking the SCIPP angle from the Y axis in the 'old' YZ plane
    SCIPP_angle_from_horiz = arctan(SCIPP_line[COORDS.Z]/SCIPP_line[COORDS.Y]) 
    
    # Determine our angular adjustment in order to reach 34 degrees above the horizontal for the SCIPP line
   
    angle_adjustment = DESIRED_SCIPP_ANGLE - SCIPP_angle_from_horiz
    
    debugprint("SCIPP AP to IS angle is " + str(rad_to_degrees(SCIPP_angle_from_horiz)), debug_levels.DETAILED_DEBUG)
    debugprint("Adjustment AP to IS angle is " + str(rad_to_degrees(angle_adjustment)), debug_levels.DETAILED_DEBUG)
                         
    # ... then build in the correction.
    # Notice that in order to rotate the SCIPP line *up*, we have to rotate our reference system (aka new y) *down*, 
    # thus the inversion with a -1 multiplier.
    # This isn't perfect because ideally we'd be using the *new* z axis for the angle measurement, not the *old* one.  But in order to get the
    # new z axis, we need the new y axis.  So, we rotate along the old z axis instead.
    #
    # FIXME - This would be better if we could rotate about the new X axis, instead of the old.
    new_AP_vector = normalize([0, -1 * cos(angle_adjustment), sin(angle_adjustment)])   
    
    debugprint("New AnteroPosterior vector is " +str(new_AP_vector), debug_levels.DETAILED_DEBUG)
      
    return new_AP_vector

def pics_get_IS_axis(vag_props):
    ''' Find the new Inferior<->Superior axis, which is orthogonal to the new x and y axes.  Depends on those axes being definable without reference to the z axis.'''
    
    return orthogonalize(pics_get_LR_axis(vag_props), pics_get_AP_axis(vag_props))

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
        transform_matrix=lisse_axes_matrix_fn(vag_props)

    if (AXIS_CODING == AXIS_CODING_OPTIONS.pics3d):
        transform_matrix=pics3d_axes_matrix_fn(vag_props)
        
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

def pics_normalize_to_ischial_spine_width(vag_props):
    ''' Scale all points along the inter-ischial spine line and about the origin, so that the width of the pelvis is normalized. '''
    
    fid_points = vag_props._fiducial_points
    
    IIS_line = vector_from_fiducials(fid_points[RIGHT_ISCHIAL_SPINE_NAME], fid_points[LEFT_ISCHIAL_SPINE_NAME])
    
    scale_factor = IIS_SCALE_LENGTH/magnitude(IIS_line)
    
    if(AXIS_CODING == AXIS_CODING_OPTIONS.lisse):
        # Scale along the 'x' axis, which is L<->R.
        scale_matrix = matrix([[scale_factor,0,0,0],
                              [0,1,0,0],
                              [0,0,1,0],
                              [0,0,0,0]])
        
    if(AXIS_CODING == AXIS_CODING_OPTIONS.pics3d):
        # Scale along the 'Z' axis, which is L<->R.
        scale_matrix = matrix([[1,0,0,0],
                              [0,1,0,0],
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

        debugprint("Error!  Cannot find one of the points named: " + PUBIC_SYMPHYSIS_NAME 
              + ", " + SC_JOINT_NAME 
              + ", " + LEFT_ISCHIAL_SPINE_NAME 
              + ", or " + RIGHT_ISCHIAL_SPINE_NAME
              + " in properties list for " + vag_props._name, debug_levels.ERRORS)

        fidpoints = fid_points
        if not fidpoints.has_key(PUBIC_SYMPHYSIS_NAME): debugprint("Missing " + PUBIC_SYMPHYSIS_NAME, debug_levels.ERRORS)   
        if not fidpoints.has_key(LEFT_ISCHIAL_SPINE_NAME): debugprint("Missing " + LEFT_ISCHIAL_SPINE_NAME, debug_levels.ERRORS)
        if not fidpoints.has_key(RIGHT_ISCHIAL_SPINE_NAME): debugprint("Missing " + RIGHT_ISCHIAL_SPINE_NAME, debug_levels.ERRORS)

        exit()   
        return

    set_pelvic_tilt_correction_info(vag_props)

    transformation_matrix = pics_generate_transformation_matrix(vag_props)
 
    for fid in fid_points:
        fid_points[fid].coords = transform_coords_by_matrix(fid_points[fid].coords, transformation_matrix)

    if SCALE_BY_SCIPP_LINE:
        pics_normalize_to_SCIPP_line(vag_props)
        
    if SCALE_BY_IIS_LINE:
        pics_normalize_to_ischial_spine_width(vag_props)
    
    vag_props.compute_properties()
        

def pics_verify(vag_props):
    
    fid_points = vag_props._fiducial_points
    
    # Determine the sacrococcygeal->inferior pubic point line ("SCIPP line")
    SCIPP_line = normalize(pics_get_SCIPP_line(fid_points))
    
    # Determine the current angle of the SCIPP line from the horizontal
    # Do that by taking the SCIPP angle from the Y axis in the 'old' YZ plane
    SCIPP_angle_from_horiz = arctan(SCIPP_line[AXIS_CODING_IS]/SCIPP_line[AXIS_CODING_AP])
    
    debugprint("Final SCIPP angle from horizontal is: " + str(rad_to_degrees(SCIPP_angle_from_horiz)) 
               + " degrees and should be: " + str(-1 * rad_to_degrees(DESIRED_SCIPP_ANGLE)) + " degrees", debug_levels.BASIC_DEBUG)
