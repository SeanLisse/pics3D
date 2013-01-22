#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in two sets of fiducials from two files, normalize them to the 3DMAPS system, compare them, and display the results.

# Built in library imports
import collections

# Domain specific custom imports
from Fiducials import vector_from_fiducials, COORDS
from VectorMath import magnitude
from ThreeDeeMAPS import maps_recenter_and_reorient, maps_verify
from VaginalProperties import VaginalDisplay
from Graphing import show_all_graphs, add_line_to_graph
from GraphColoring import COLORIZATION_OPTIONS
from PelvicPoints import create_pelvic_points_graph


# Generic custom imports
from Utilities import setdebuglevel, debug_levels, debugprint

class FiducialDifference(object):
    _fiducial_point_one = None
    _fiducial_point_two = None
    _difference_vector = None
    
    def __init__(self, fiducial_point_one, fiducial_point_two):
        self._fiducial_point_one = fiducial_point_one
        self._fiducial_point_two = fiducial_point_two
        self._difference_vector = vector_from_fiducials(fiducial_point_one, fiducial_point_two) 
        
        
def compare_fiducials(fids1, fids2):
    ''' Given two sets of fiducials, fids1 and fids2, compare the two and compile a list of computable differences between them. '''
      
    # Create a list 
    difference_list = collections.OrderedDict()
        
    # Look through list "fids1".  For each fiducial in it, check fids2 to see if there is one with the same name.
    # If a match is found, calculate the difference and add it to the difference list.
    for fid_name in fids1:
        if (fid_name in fids2):
            difference_list[fid_name] = FiducialDifference(fids1[fid_name], fids2[fid_name])
            
    return difference_list            
            

def draw_differences(graph, difflist):
    ''' Given a list of differences (difflist) between fiducial points and a graph (graph), draw lines connecting the first and second set of corresponding fiducial points on the graph.'''
    
    for diff_name in difflist:
            print("Found a difference: " + diff_name + " has moved: ")
            diff_vec = difflist[diff_name]._difference_vector
            print("  " + str(diff_vec[COORDS.X]) + "," + str(diff_vec[COORDS.Y]) + "," + str(diff_vec[COORDS.Z]) + " (Distance: " + str(magnitude(diff_vec)) + ")")
            
    for diff_name in difflist:
            diff = difflist[diff_name]
            coords1 = diff._fiducial_point_one.coords
            coords2 = diff._fiducial_point_two.coords
            add_line_to_graph(graph, coords1, coords2 , "grey")
            
#####################
### DEFAULT MAIN PROC 
#####################  

if __name__ == '__main__':
        
    from sys import argv
     
    setdebuglevel(debug_levels.ERRORS) 
    
    if len(argv) <> 3: 
        print "Need to supply TWO mrml file names, and we will compare fiducials from the second to the first."
        print "E.g. CompareFiducialSets.py original.mrml changed.mrml"
    else:
        
        # Use a single graph to show all inputs
        graph = None
        
        debugprint('Now starting fiducial comparison program',debug_levels.BASIC_DEBUG)
 
        # Load vaginal coordinates from MRML file #1.
        filename = argv[1]                       
        vag_display1 = VaginalDisplay(filename, COLORIZATION_OPTIONS.SEQUENTIAL)        
        vag_display1.initialize_from_MRML(filename)
        
        # Normalize to MAPS.        
        maps_recenter_and_reorient(vag_display1)
        maps_verify(vag_display1)
        
        # Display it.
        print(vag_display1.to_string())    
        graph = create_pelvic_points_graph(graph, vag_display1, filename)
        
        # Load vaginal coordinates from MRML file #2.
        filename = argv[2]
        vag_display2 = VaginalDisplay(filename, COLORIZATION_OPTIONS.SEQUENTIAL)        
        vag_display2.initialize_from_MRML(filename)
        
        # Normalize to MAPS.        
        maps_recenter_and_reorient(vag_display2)
        maps_verify(vag_display2)

        # Display it.
        graph = create_pelvic_points_graph(graph, vag_display2, filename)
        print(vag_display2.to_string())
    
        difflist = compare_fiducials(vag_display1._fiducial_points, vag_display2._fiducial_points)
        draw_differences(graph, difflist)
                                              
        show_all_graphs()