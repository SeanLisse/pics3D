#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from a directory tree and perform some math upon them, then display the results.

# Nonspecific imports
from Utilities import setdebuglevel, debug_levels, debugprint

# My custom domain imports
from VaginalProperties import VaginalDisplay
from Graphing import add_fiducials_to_graph, add_columns_to_graph, add_line_to_graph, add_scatterpoint_to_graph
from Graphing import add_legend_to_graph, set_graph_boundaries, show_all_graphs, PelvicGraph
from GraphColoring import calibrate_colorization_strategy_fn, fraction_color

# Constants
from Fiducials import COORDS, SC_JOINT_NAME, INTER_ISCHIAL_SPINE_NAME
from GraphColoring import COLORIZATION_OPTIONS

# Add 8 artificial cube corners to the graph to force the same scaling on all graphs.  Set to False to not draw.
PAD_GRAPH=False

def create_pelvic_points_graph(graph, vagprops, graphname, color_strategy = COLORIZATION_OPTIONS.PIS_DISTANCE):

    if (graph == None):
        graph = PelvicGraph(graphname)
    
    fid_points = vagprops._fiducial_points
    
    [color_fn, minmax_distances] = calibrate_colorization_strategy_fn(color_strategy, vagprops)
    
    add_fiducials_to_graph(graph, vagprops, color_fn)
    
    PS_coords = vagprops._Pubic_Symphysis.coords
    L_IS_coords = vagprops._Left_IS.coords
    R_IS_coords = vagprops._Right_IS.coords
    
    # Display the P_IS lines on the graph as well
    add_line_to_graph(graph, PS_coords, L_IS_coords , "black")
    add_line_to_graph(graph, PS_coords, R_IS_coords, "black")
    
    IIS_coords = vagprops._IIS.coords
    add_scatterpoint_to_graph(graph, INTER_ISCHIAL_SPINE_NAME, IIS_coords[COORDS.X], IIS_coords[COORDS.Y], IIS_coords[COORDS.Z], "black")
    
    if(fid_points.has_key(SC_JOINT_NAME)):
        add_line_to_graph(graph, PS_coords, fid_points[SC_JOINT_NAME].coords, "black")
    
    if PAD_GRAPH:
        # Pad the graph to keep all graphs at equal scale for comparison
        GRAPH_PADDING=100
        set_graph_boundaries(graph,
                             PS_coords[COORDS.X] + GRAPH_PADDING, 
                             PS_coords[COORDS.X] - GRAPH_PADDING,
                             PS_coords[COORDS.Y] + GRAPH_PADDING, 
                             PS_coords[COORDS.Y] - GRAPH_PADDING,
                             PS_coords[COORDS.Z] + GRAPH_PADDING,
                             PS_coords[COORDS.Z] - GRAPH_PADDING)
        
    # Add a legend
    add_legend_to_graph(graph,
                        "Minimum Distance: " + str(round(minmax_distances[0],1)) + "mm", 
                        "Maximum Distance: " + str(round(minmax_distances[1],1)) + "mm",
                        fraction_color(minmax_distances[0], minmax_distances[0], minmax_distances[1]), 
                        fraction_color(minmax_distances[1], minmax_distances[0], minmax_distances[1]))
    
    return graph   

    
#####################
### DEFAULT MAIN PROC
##################### 

if __name__ == '__main__':
    
    from sys import argv
     
    setdebuglevel(debug_levels.DETAILED_DEBUG) 
    
    if len(argv) < 2: 
        print "Need to supply mrml file name argument."
    else:
        filename = argv[1]
    
        debugprint('Now starting pelvic points program',debug_levels.BASIC_DEBUG)
        
        vag_props = VaginalDisplay()        
        vag_props.initialize_from_MRML(filename)
        vag_props._graph = create_pelvic_points_graph(vag_props._graph, vag_props, filename)
        
        show_all_graphs()
            
        debugprint('Now leaving pelvic points program',debug_levels.BASIC_DEBUG)
