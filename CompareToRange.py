#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from command-line arguments and normalize them to the PICS system, 
# Graphically compare the *first* set of fiducials to the range of the *rest* of the sets, and display the results.

# Generic custom imports 
import matplotlib.pyplot as plt
from Utilities import setdebuglevel, debug_levels, debugprint

# Domain specific custom imports
from ComputeStatistics import load_vaginal_properties, get_stats_and_display_from_properties
from ComputeStatistics import FiducialStatCollection, STD_DEV_GRAPH_MULTIPLIER
from Fiducials import COORDS

# Graph drawing imports 
from Graphing import show_all_graphs, PelvicGraph2D
from GraphColoring import calibrate_colorization_strategy_fn

# CONSTANTS
COORD_TO_GRAPH=COORDS.Z

def create_2D_comparison_graph(graph, graphname, exemplardisplay, rangestats):

    if (graph == None):
        graph = PelvicGraph2D(graphname)

    [color_fn, minmax_distances] = calibrate_colorization_strategy_fn(exemplardisplay)
        
    ''' Add all fiducials in the RANGE dictionary fid_list to the graph as bars.  Color code using the function color_fn which takes a fiducial as an argument. '''
    fid_list = exemplardisplay._fiducial_points
    
    fid_length = len(fid_list)
    graph._ax.set_xlim(0,fid_length)
    graph._ax.set_ylim(-50,200)
    
    stat_list = rangestats.get_all_stats()
    
    x_index = -1
    x_labels = []
    
    for key in fid_list.iterkeys():
        
        x_index += 1
        x_labels.append(key)
        
        

        # Draw the "error bar" on the graph in light grey
        if (key in stat_list):
            stat = stat_list[key]
        else: 
            stat = None
              
        if (stat != None): 
            avg_val = stat._averaged_fid.coords[COORD_TO_GRAPH]
            
            stdev = None
            if [COORD_TO_GRAPH == COORDS.X]: stdev = stat._fid_std_dev_x
            if [COORD_TO_GRAPH == COORDS.Y]: stdev = stat._fid_std_dev_y
            if [COORD_TO_GRAPH == COORDS.Z]: stdev = stat._fid_std_dev_z
            
            min_val = avg_val - (STD_DEV_GRAPH_MULTIPLIER * stdev)
            max_val = avg_val + (STD_DEV_GRAPH_MULTIPLIER * stdev)
            
            graph._ax.broken_barh([(x_index-.5,1)], (min_val, max_val), facecolors='lightgray')
        
        # Draw the fiducial as a black dot.
        fid = fid_list[key]
        graph._ax.scatter(x_index, fid.coords[COORD_TO_GRAPH], marker='o', label=key, color="black")
        
    graph._ax.set_xticks(range(0, x_index))   
    label_obj = graph._ax.set_xticklabels(x_labels)       

    plt.setp(label_obj, rotation=45, fontsize=8)

    graph._ax.grid(True)

    return graph   

#####################
### DEFAULT MAIN PROC
#####################  

if __name__ == '__main__':
        
    from sys import argv
     
    setdebuglevel(debug_levels.BASIC_DEBUG) 
    
    if len(argv) < 3: 
        debugprint("Need to supply at least one mrml file name argument and at least one to compare it against.",debug_levels.ERROR)
    else:
        # ignore argv[0], as it's just the filename of this python file.

        # List of fiducial stats representing a single vagina, to be compared to the range.
        propslist = load_vaginal_properties(argv[1:2])
        [propstats, propsdisplay] = get_stats_and_display_from_properties("Comparator", propslist)
        
        # List of fiducial stats representing a range to compare that single one against. 
        rangelist = load_vaginal_properties(argv[2:])
        [rangestats, rangedisplay] = get_stats_and_display_from_properties("Range", rangelist)
     
        graph = create_2D_comparison_graph(None, "Range Comparison", propsdisplay, rangestats)
        
    show_all_graphs()