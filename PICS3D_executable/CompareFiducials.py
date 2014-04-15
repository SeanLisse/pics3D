#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in two sets of fiducials from two files, normalize them to the PICS3D system, compare them, and display the results.

# Domain specific custom imports
import __init__
from PICS3D_libraries.Fiducials import vector_from_fiducials, get_fiducial_list_by_row_and_column
from PICS3D_libraries.VectorMath import magnitude 
from PICS3D_libraries.PICSMath import pics_correct_and_verify
from PICS3D_libraries.VaginalDisplay import load_vaginal_displays
from PICS3D_libraries.Graphing import show_all_graphs, add_line_to_graph3D
from PICS3D_libraries.Options import  COORDS
from PelvicPoints import create_pelvic_points_graph

# Generic custom imports
from PICS3D_libraries.Utilities import setdebuglevel, debug_levels, debugprint

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
      
    # Create a list to contain our pairs of compared points.
    difference_list = list()

    # OLD VERSION        
    # Look through list "fids1".  For each fiducial in it, check fids2 to see if there is one with the same name.
    # If a match is found, calculate the difference and add it to the difference list.
    # for fid_name in fids1:
    #     if (fid_name in fids2):
    #         difference_list.append(FiducialDifference(fids1[fid_name], fids2[fid_name]))d
       
    # NEW VERSION
    # Scan through the rows and find the 'edge' points of each.  We'll compare the edge fiducial locations of each row from fids1 with those of the same
    # row in fids2.
    
    fidsmatrix1 = get_fiducial_list_by_row_and_column(fids1)
    fidsmatrix2 = get_fiducial_list_by_row_and_column(fids2)
    
    # Subroutine to search our newly organized matrixes, finding the minimum and maximum column index for each row.
    for rowindex in range(1,len(fidsmatrix1)):
        colindex = None
        
        minindex1 = minindex2 = None
        maxindex1 = maxindex2 = None
        
        for colindex in range(1,len(fidsmatrix1[rowindex])):
            
            if (fidsmatrix1[rowindex][colindex] <> None):
                # We've struck a valid value
                if (minindex1 == None): minindex1 = colindex
                
                # Grab it as the newest maximum value - will be overwritten by the next iteration
                # if there's a later one.
                maxindex1 = colindex

        # Check to be sure we're looking at a valid row of matrix 2
        if (rowindex >= len(fidsmatrix2)): continue
            
        for colindex in range(1,len(fidsmatrix2[rowindex])):
            
            if (fidsmatrix2[rowindex][colindex] <> None):
                # We've struck a valid value
                if (minindex2 == None): minindex2 = colindex
                
                # Grab it as the newest maximum value - will be overwritten by the next iteration
                # if there's a later one.
                maxindex2 = colindex
        
        # Check to be sure we have all four indices we need for a valid comparison of rows
        if ((minindex1 == None) or (maxindex1 == None) or (minindex2 == None) or (maxindex2 == None)):
            continue
        
        # Append the comparison of MINimum fiducial points
        fid1 = fidsmatrix1[rowindex][minindex1]
        fid2 = fidsmatrix2[rowindex][minindex2]
        difference_list.append(FiducialDifference(fid1, fid2))

        # Append the comparison of MAXimum fiducial points
        fid1 = fidsmatrix1[rowindex][maxindex1]
        fid2 = fidsmatrix2[rowindex][maxindex2]
        difference_list.append(FiducialDifference(fid1, fid2))
            
    return difference_list
            

def draw_differences(graph, difflist):
    ''' Given a list of differences (difflist) between fiducial points and a graph (graph), draw lines connecting the first and second set of corresponding fiducial points on the graph.'''
    
    for diff in difflist:
            print("Comparing data set 1's fiducial named: " + diff._fiducial_point_one.name + " to data set 2's fiducial named: " + diff._fiducial_point_two.name + ".")
            diff_vec = diff._difference_vector
            print("  " + str(diff_vec[COORDS.X]) + "," + str(diff_vec[COORDS.Y]) + "," + str(diff_vec[COORDS.Z]) + " (Distance: " + str(magnitude(diff_vec)) + ")")
            
    for diff in difflist:
            coords1 = diff._fiducial_point_one.coords
            coords2 = diff._fiducial_point_two.coords
            add_line_to_graph3D(graph, coords1, coords2 , "grey")
            
#####################
### DEFAULT MAIN PROC 
#####################  

if __name__ == '__main__':
        
    from sys import argv
     
    setdebuglevel(debug_levels.DETAILED_DEBUG) 
    
    if len(argv) <> 3: 
        print "Need to supply TWO mrml file names, and we will compare fiducials from the second to the first."
        print "E.g. CompareFiducialSets.py original.mrml changed.mrml"
    else:
        
        # Use a single graph to show all inputs
        graph = None
        
        debugprint('Now starting fiducial comparison program',debug_levels.BASIC_DEBUG)
 
        # Load both MRML files...
        displays = load_vaginal_displays(argv[1:3])
        
        for index in {0,1}:
            filename = argv[index + 1]
            display=displays[index]
            print(display.to_string()) 
            pics_correct_and_verify(display)
            graph = create_pelvic_points_graph(graph, display, filename)
        
        difflist = compare_fiducials(displays[0]._fiducial_points, displays[1]._fiducial_points)
        draw_differences(graph, difflist)
                                              
        show_all_graphs()