#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from a directory tree and normalize them to the 3DMAPS system, then display the results.

from Utilities import setdebuglevel, debug_levels, debugprint
from VectorMath import normalize, orthogonalize
from Fiducials import fiducial, recenter_fiducials, reorient_fiducials, vector_from_fiducials, COORDS
from MRMLSweep import load_fiducials_from_mrml, fiducial_points
from PelvicPoints import draw_pelvic_points_graph
from PelvicPoints import PUBIC_SYMPHYSIS_NAME, LEFT_ISCHIAL_SPINE_NAME, RIGHT_ISCHIAL_SPINE_NAME, SC_JOINT_NAME
from numpy import arctan, sin, cos, pi

# (34 degrees above horizontal is 0.5934 in radians)
DESIRED_SCIPP_ANGLE = -0.593411946

def maps_get_new_origin(fiducial_points):
    ''' Find the new origin of our coordinate system using MAPS3D methodology (i.e. recenter on the pubic symphysis). '''
    if not(fiducial_points.has_key(PUBIC_SYMPHYSIS_NAME)): raise ValueError("Cannot find pubic symphysis, so cannot set MAPS3D origin.")
    else: 
        return fiducial_points[PUBIC_SYMPHYSIS_NAME] 

def maps_get_SCIPP_line(fiducial_points):
    if not(fiducial_points.has_key(SC_JOINT_NAME)): 
        raise ValueError("Cannot find sacrococcygeal joint, so cannot find SCIPP line.")
    if not(fiducial_points.has_key(PUBIC_SYMPHYSIS_NAME)): 
        raise ValueError("Cannot find sacrococcygeal joint, so cannot find SCIPP line.")
    
    return vector_from_fiducials(fiducial_points[PUBIC_SYMPHYSIS_NAME], fiducial_points[SC_JOINT_NAME])

def maps_get_x_axis(fiducial_points):
    ''' Find the new MAPS3D X axis, which is simply a normalized version of the line between the ischial spines. '''
    if not(fiducial_points.has_key(LEFT_ISCHIAL_SPINE_NAME) and fiducial_points.has_key(RIGHT_ISCHIAL_SPINE_NAME)): 
        raise ValueError("Cannot find left and right ischial spines, so cannot set MAPS3D x axis.")
    else: 
        return normalize(vector_from_fiducials(fiducial_points[RIGHT_ISCHIAL_SPINE_NAME], fiducial_points[LEFT_ISCHIAL_SPINE_NAME]))

def maps_get_y_axis(fiducial_points):
    ''' Find the new MAPS3D Y axis, which will be SCIPP line rotated caudally 34 degrees around the pubic symphysis.'''
    
    # Determine the sacrococcygeal->inferior pubic point line ("SCIPP line")
    SCIPP_line = normalize(maps_get_SCIPP_line(fiducial_points))
    
    # Determine the current angle of the SCIPP line from the horizontal
    # Do that by taking the SCIPP angle from the Y axis in the 'old' YZ plane
    SCIPP_angle_from_horiz = arctan(SCIPP_line[COORDS.Z]/SCIPP_line[COORDS.Y]) 
    
    # Determine our angular adjustment in order to reach 34 degrees above the horizontal for the SCIPP line
   
    angle_adjustment = DESIRED_SCIPP_ANGLE - SCIPP_angle_from_horiz
    
    debugprint("SCIPP YZ angle is " + str(SCIPP_angle_from_horiz * 180 / pi), debug_levels.DETAILED_DEBUG)
    debugprint("Adjustment YZ angle is " + str(angle_adjustment * 180 / pi), debug_levels.DETAILED_DEBUG)
                         
    # ... then build in the correction.
    # Notice that in order to rotate the SCIPP line *up*, we have to rotate our reference system (aka new y) *down*, 
    # thus the inversion with a -1 multiplier.
    # This isn't perfect because ideally we'd be using the *new* z axis for the drop line, not the *old* one.  But in order to get the
    # new z axis, we need the new y axis.  So, we rotate along the old z axis instead.
    new_y_vector = [0, -1 * cos(angle_adjustment), sin(angle_adjustment)]        
       
    new_y_point = fiducial("new y", new_y_vector[COORDS.X], new_y_vector[COORDS.Y], new_y_vector[COORDS.Z])
    
    MAPS_line = normalize(vector_from_fiducials(fiducial_points[PUBIC_SYMPHYSIS_NAME], new_y_point))  
      
    return MAPS_line

def maps_get_z_axis(fiducial_points):
    ''' Find the new MAPS3D Z axis, which is orthogonal to the new x and y axes.  Depends on those axes being definable without reference to the z axis.'''
    
    return orthogonalize(maps_get_x_axis(fiducial_points), maps_get_y_axis(fiducial_points))


def maps_recenter_and_reorient(fid_points):
    ''' Rotate, translate, and (someday perhaps) scale all of our fiducial points to fit the MAPS3D reference system. ''' 

    # Change origin of coordinates to fit our MAPS3D system
    recenter_fiducials(maps_get_new_origin(fid_points), fid_points)
            
    # Change axes of coordinates to fit our MAPS3D system
    new_x_axis = maps_get_x_axis(fid_points)
    new_y_axis = maps_get_y_axis(fid_points)
    new_z_axis = maps_get_z_axis(fid_points)
    
    debugprint("Reorienting to x axis " + str(new_x_axis)
               + ", y axis  " + str(new_y_axis)
               + ", z axis " + str(new_z_axis), debug_levels.DETAILED_DEBUG)
    reorient_fiducials(new_x_axis, new_y_axis, new_z_axis, fid_points)

    # NO scaling for now - but we may reconsider this in the future!

def maps_verify(fid_points):
    # Determine the sacrococcygeal->inferior pubic point line ("SCIPP line")
    SCIPP_line = normalize(maps_get_SCIPP_line(fid_points))
    
    # Determine the current angle of the SCIPP line from the horizontal
    # Do that by taking the SCIPP angle from the Y axis in the 'old' YZ plane
    SCIPP_angle_from_horiz = arctan(SCIPP_line[COORDS.Z]/SCIPP_line[COORDS.Y])
    
    debugprint("Final SCIPP angle from horizontal is: " + str(abs(SCIPP_angle_from_horiz) * 180 /pi ) 
               + " degrees and should be: " + str(abs(DESIRED_SCIPP_ANGLE) * 180 / pi) + " degrees", debug_levels.DETAILED_DEBUG)
    

#####################
### DEFAULT MAIN PROC
#####################  

if __name__ == '__main__':
    
        
    from sys import argv
     
    setdebuglevel(debug_levels.ERRORS) 
    
    if len(argv) < 2: 
        print "Need to supply mrml file name argument."
    else:
        filename = argv[1]
    
        debugprint('Now starting MAPS3D pelvic points program',debug_levels.BASIC_DEBUG)
                    
        load_fiducials_from_mrml(filename, fiducial_points)
                
        ### Here we encode and graph by minimum distance from one of the P->IS lines.        
        if (fiducial_points.has_key(PUBIC_SYMPHYSIS_NAME) 
            and fiducial_points.has_key(LEFT_ISCHIAL_SPINE_NAME) 
            and fiducial_points.has_key(RIGHT_ISCHIAL_SPINE_NAME)
            and fiducial_points.has_key(SC_JOINT_NAME)):
            
            maps_recenter_and_reorient(fiducial_points)
            
            maps_verify(fiducial_points)
                        
            draw_pelvic_points_graph(fiducial_points, filename)
        else:
            print("Error!  Cannot find one of the points named: " + PUBIC_SYMPHYSIS_NAME 
                  + ", " + SC_JOINT_NAME 
                  + ", " + LEFT_ISCHIAL_SPINE_NAME 
                  + ", or " + RIGHT_ISCHIAL_SPINE_NAME)   
            
        debugprint('Now leaving pelvic points program',debug_levels.BASIC_DEBUG)
