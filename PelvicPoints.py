#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from a directory tree and perform some math upon them, then display the results.

# Nonspecific imports
from Utilities import setdebuglevel, debug_levels, debugprint

# My custom domain imports
from VaginalDisplay import VaginalDisplay

# Graphing custom imports
from Graphing import add_fiducials_to_graph3D, add_line_to_graph3D, add_scatterpoint_to_graph3D
from Graphing import add_legend_to_graph3D, set_graph_boundaries3D, show_all_graphs, PelvicGraph3D
from GraphColoring import calibrate_colorization_strategy_fn, fraction_color

# Constants
from Options import COORDS, SC_JOINT_NAME, INTER_ISCHIAL_SPINE_NAME, CREATE_IIS, SHOW_P_IS
from Options import COLOR_STRAT

# Add 8 artificial cube corners to the graph to force the same scaling on all graphs.  Set to False to not draw.
PAD_GRAPH=False

def create_pelvic_points_graph(graph, vagdisplay, graphname):

    if (graph == None):
        graph = PelvicGraph3D(graphname)
    
    fid_points = vagdisplay._fiducial_points
    
    [color_fn, minmax_distances] = calibrate_colorization_strategy_fn(vagdisplay)
    
    add_fiducials_to_graph3D(graph, vagdisplay, color_fn)
    
    PS_coords = vagdisplay._Pubic_Symphysis.coords
    L_IS_coords = vagdisplay._Left_IS.coords
    R_IS_coords = vagdisplay._Right_IS.coords
    
    # Display the P_IS lines on the graph as well
    if SHOW_P_IS:
        add_line_to_graph3D(graph, PS_coords, L_IS_coords , "black")
        add_line_to_graph3D(graph, PS_coords, R_IS_coords, "black")
    
    if CREATE_IIS:
        IIS_coords = vagdisplay._IIS.coords
        add_scatterpoint_to_graph3D(graph, INTER_ISCHIAL_SPINE_NAME, IIS_coords[COORDS.X], IIS_coords[COORDS.Y], IIS_coords[COORDS.Z], "black")
    
    if PAD_GRAPH:
        # Pad the graph to keep all graphs at equal scale for comparison
        GRAPH_PADDING=100
        set_graph_boundaries3D(graph,
                             PS_coords[COORDS.X] + GRAPH_PADDING, 
                             PS_coords[COORDS.X] - GRAPH_PADDING,
                             PS_coords[COORDS.Y] + GRAPH_PADDING, 
                             PS_coords[COORDS.Y],
                             PS_coords[COORDS.Z] + GRAPH_PADDING,
                             PS_coords[COORDS.Z] - GRAPH_PADDING/3)
        
    # Add a legend
    #    add_legend_to_graph3D(graph,
#                        "Minimum Distance: " + str(round(minmax_distances[0],1)) + "mm", 
#                        "Maximum Distance: " + str(round(minmax_distances[1],1)) + "mm",
#                        fraction_color(minmax_distances[0], minmax_distances[0], minmax_distances[1]), 
#                        fraction_color(minmax_distances[1], minmax_distances[0], minmax_distances[1]))
    
    
    return graph   

    
#####################
### DEFAULT MAIN PROC
##################### 

if __name__ == '__main__':
    
    from sys import argv
     
    setdebuglevel(debug_levels.BASIC_DEBUG) 
    
    if len(argv) < 2: 
        print "Need to supply mrml file name argument."
    else:
        filename = argv[1]
    
        debugprint('Now starting pelvic points program',debug_levels.BASIC_DEBUG)
        
        vagdisplay = VaginalDisplay(filename, COLOR_STRAT)        
        vagdisplay.initialize_from_MRML(filename)
        graph = create_pelvic_points_graph(None, vagdisplay, filename)
        
        print(vagdisplay.to_string())
        
        show_all_graphs()
        
        debugprint('Now leaving pelvic points program',debug_levels.BASIC_DEBUG)
