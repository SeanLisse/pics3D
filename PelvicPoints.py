#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from a directory tree and perform some math upon them, then display the results.

from MRMLSweep import load_fiducials_from_mrml, fiducial_points
from Graphing import add_fiducials_to_graph, show_graph
from numpy import Infinity

incremental_color = 0
def incremental_color_fn(fiducial):
    INCREMENTAL_STEP = 0.01
    global incremental_color
    incremental_color = incremental_color + INCREMENTAL_STEP
    while (incremental_color > 1):
        incremental_color=incremental_color -1
    return [incremental_color, incremental_color, incremental_color]


# Define absurd mins & maxes for use with xyz_color_fn
x_min = y_min = z_min = Infinity
x_max = y_max = z_max = -1 * Infinity

def xyz_color_calibration(fiducial_list):
    global x_min, y_min, z_min, x_max, y_max,z_max
    
    for key in fiducial_points.iterkeys():
        fid = fiducial_points[key]
        
        if (fid.x < x_min): x_min = fid.x
        if (fid.y < y_min): y_min = fid.y
        if (fid.z < z_min): z_min = fid.z
        if (fid.x > x_max): x_max = fid.x
        if (fid.y > y_max): y_max = fid.y
        if (fid.z > z_max): z_max = fid.z

def xyz_color_fn(fiducial):
    ''' Takes a fiducial point and returns a color with R based on relative X, G based on Y and B based on Z.
    NOTE: ASSUMES x_min,x_max,y_min,y_max,and z_min,z_max globals have been properly set!'''
    
    global x_min, y_min, z_min, x_max, y_max,z_max
    
    red = (fiducial.x - x_min) / (x_max - x_min)
    green = (fiducial.y - y_min) / (y_max - y_min)
    blue = (fiducial.z - z_min) / (z_max - z_min)
    
    return [red,green,blue]

#####################
### DEFAULT MAIN PROC
#####################
    
if __name__ == '__main__':
    
    from sys import argv
    from Utilities import setdebuglevel, debug_levels, debugprint
     
    setdebuglevel(debug_levels.NO_DEBUG) 
    
    if len(argv) < 2: 
        print "Need to supply mrml file name argument."
    else:
        filename = argv[1]
    
        debugprint('Now starting pelvic points program',debug_levels.BASIC_DEBUG)
                    
        load_fiducials_from_mrml(filename, fiducial_points)
           
#        print('************Final fiducials***********')
#        for key in fiducial_points.iterkeys():
#            fid = fiducial_points[key]            
#            print(fid.name + " at x:" + str(fid.x) + ", y:" + str(fid.y) + ", z:" + str(fid.z))
        
        xyz_color_calibration(fiducial_points)
        add_fiducials_to_graph(fiducial_points, xyz_color_fn)
        show_graph()
            
        debugprint('Now leaving pelvic points program',debug_levels.BASIC_DEBUG)
