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
from Fiducials import COORDS, REFERENCE_POINT_NAMES

# Graph drawing imports 
from Graphing import show_all_graphs, PelvicGraph2D
from GraphColoring import calibrate_colorization_strategy_fn

# CONSTANTS
REFERENCE_POINT_BAR_COLOR="#AABBAA"
BAR_COLOR = "#EEEEEE"
POINT_COLOR = "#000000"
COORD_TO_GRAPH=COORDS.Z


def create_2D_comparison_graph(graph, graphname, exemplardisplay, rangestats):

    if (graph == None):
        graph = PelvicGraph2D(graphname)

    [color_fn, minmax_distances] = calibrate_colorization_strategy_fn(exemplardisplay)
        
    ''' Add all fiducials in the RANGE dictionary fid_list to the graph as bars.  Color code using the function color_fn which takes a fiducial as an argument. '''
    fid_list = exemplardisplay._fiducial_points
    
    fid_length = len(fid_list)
    graph._ax.set_xlim(0,fid_length)
    graph._ax.set_ylim(-50,100)
    
    stat_list = rangestats.get_all_stats()
    
    # Start with a blank point at 0 index so our first datapoint isn't right on the edge of the graph.
    x_index = 0
    x_labels = [""] 
    
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
            
            if (key in REFERENCE_POINT_NAMES):
                barcolor = REFERENCE_POINT_BAR_COLOR
            else: 
                barcolor = BAR_COLOR

            # Draw the range
            graph._ax.broken_barh([(x_index-0.5,1)], (min_val, max_val - min_val), facecolors=barcolor)
            
            # Draw the average val
            graph._ax.broken_barh([(x_index-0.5,1)], (avg_val, 0), facecolors=barcolor)
            
            # print("Stats for " + key + ": avg " + str(avg_val) + ", stdev " + str(stdev) + ", min " + str(min_val) + ", max " + str(max_val))
        
        # Draw the fiducial as a black dot.
        fid = fid_list[key]
        graph._ax.scatter(x_index, fid.coords[COORD_TO_GRAPH], marker='o', label=key, color=POINT_COLOR)
    
    # Add an extra space on the end so our last point isn't on the edge of the graph.
    x_index += 2
    x_labels.append("")
    x_labels.append("")
        
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
        print("Need to supply at least one mrml file name argument and at least one to compare it against.")
    else:
        # ignore argv[0], as it's just the filename of this python file.

        # List of fiducial stats representing a single vagina, to be compared to the range.
        propslist = load_vaginal_properties(argv[1:2])
        [propstats, propsdisplay] = get_stats_and_display_from_properties("Comparator", propslist)
        
        # List of fiducial stats representing a range to compare that single one against. 
        rangelist = load_vaginal_properties(argv[2:])
        [rangestats, rangedisplay] = get_stats_and_display_from_properties("Range", rangelist)
     
        graph = create_2D_comparison_graph(None, argv[1] + " Range Comparison", propsdisplay, rangestats)
        
    show_all_graphs()
