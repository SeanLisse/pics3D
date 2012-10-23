#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from a directory tree and normalize them to the 3DMAPS system, then display the results.

from Utilities import setdebuglevel, debug_levels, debugprint
from VectorMath import normalize, orthogonalize
from Fiducials import fiducial, recenter_fiducials, reorient_fiducials, vector_from_fiducials, COORDS
from MRMLSweep import load_fiducials_from_mrml, fiducial_points
from PelvicPoints import draw_pelvic_points_graph
from PelvicPoints import PUBIC_SYMPHYSIS_FID_NAME, LEFT_ISCHIAL_SPINE_FID_NAME, RIGHT_ISCHIAL_SPINE_FID_NAME

def maps_get_new_origin(fiducial_points):
    ''' Find the new origin of our coordinate system using MAPS3D methodology (i.e. recenter on the pubic symphysis). '''
    if not(fiducial_points.has_key(PUBIC_SYMPHYSIS_FID_NAME)): raise ValueError("Cannot find pubic symphysis, so cannot set MAPS3D origin.")
    else: 
        return fiducial_points[PUBIC_SYMPHYSIS_FID_NAME] 

def maps_get_x_axis(fiducial_points):
    ''' Find the new MAPS3D X axis, which is simply a normalized version of the line between the ischial spines. '''
    if not(fiducial_points.has_key(LEFT_ISCHIAL_SPINE_FID_NAME) and fiducial_points.has_key(RIGHT_ISCHIAL_SPINE_FID_NAME)): 
        raise ValueError("Cannot find left and right ischial spines, so cannot set MAPS3D x axis.")
    else: 
        return normalize(vector_from_fiducials(fiducial_points[LEFT_ISCHIAL_SPINE_FID_NAME], fiducial_points[RIGHT_ISCHIAL_SPINE_FID_NAME]))

def maps_get_y_axis(fiducial_points):
    ''' Find the new MAPS3D Y axis, which will be SCIPP line rotate caudally 34 degrees through the pubic symphysis.'''
    
    # WRONG right now but just for testing.,,
    iis_coords = (fiducial_points[LEFT_ISCHIAL_SPINE_FID_NAME].coords + fiducial_points[RIGHT_ISCHIAL_SPINE_FID_NAME].coords) / 2
    inter_ischial_point = fiducial("IIS", iis_coords[COORDS.X], iis_coords[COORDS.Y], iis_coords[COORDS.Z])
    return normalize(vector_from_fiducials(fiducial_points[PUBIC_SYMPHYSIS_FID_NAME], inter_ischial_point))

def maps_get_z_axis(fiducial_points):
    ''' Find the new MAPS3D Z axis, which is orthogonal to the new x and y axes.'''
    
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
               + ", z axis " + str(new_z_axis))
    reorient_fiducials(new_x_axis, new_y_axis, new_z_axis, fid_points)

    # NO scaling for now - but we may reconsider this in the future!

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
        if (fiducial_points.has_key(PUBIC_SYMPHYSIS_FID_NAME) 
            and fiducial_points.has_key(LEFT_ISCHIAL_SPINE_FID_NAME) 
            and fiducial_points.has_key(RIGHT_ISCHIAL_SPINE_FID_NAME)):
            
            maps_recenter_and_reorient(fiducial_points)
                        
            draw_pelvic_points_graph(fiducial_points)
        else:
            print("Error!  Cannot find one of the points named: " + PUBIC_SYMPHYSIS_FID_NAME + "," + LEFT_ISCHIAL_SPINE_FID_NAME + ", or " + RIGHT_ISCHIAL_SPINE_FID_NAME)   
            
        debugprint('Now leaving pelvic points program',debug_levels.BASIC_DEBUG)
