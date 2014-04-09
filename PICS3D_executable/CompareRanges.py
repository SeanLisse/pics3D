#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from command-line arguments and normalize them to the PICS system, 
# Graphically compare the *first* set of fiducials to the range of the *rest* of the sets, and display the results.

# Generic custom imports 
import __init__
import numpy as np
import matplotlib.pyplot as plt

from PICS3D_libraries.Utilities import setdebuglevel, debug_levels, debugprint

# Domain specific custom imports
from ComputeStatistics import load_vaginal_properties, get_stats_and_display_from_properties
from Options import RANGE_ONE_COLOR, RANGE_TWO_COLOR
from PICS3D_libraries.Options import AXIS_CODING_SI, REFERENCE_POINT_NAMES

# Graph control imports
from PICS3D_libraries.Graphing import show_all_graphs, generate_magic_subplot_number, filter_vagprops_for_graphing
from PICS3D_libraries.GraphColoring import set_boxplot_colors

from Options import SHOW_REFERENCE_POINTS 
from Options import COORDINATE_GRAPH_MIN_MM, COORDINATE_GRAPH_MAX_MM
from Options import SHOW_PARAVAG_GRAPH, SHOW_WIDTH_GRAPH, SHOW_COORDINATE_GRAPH, AXIS_TO_GRAPH
from Options import GRAPH_BACKGROUND_COLOR, POINT_COLOR
from Options import SHOW_INDIVIDUAL_VALUES, SHOW_RANGE_VALUES

def create_2D_height_range_comparison_graph(graph, key_list, stats_collection_1, stats_collection_2):
    ''' Add all fiducials in key_list to the graph. Plot their heights against each other.
        Takes as input a graph to draw on, a list of all the fiducial names (keys) to draw,
        and two sets of statistics to compare, which are dictionaries of [key, FiducialStatistics] format.'''

    axes = graph.axes

    # Tracker for the X index of our box plot - 0 is leftmost box plot, and we increase as we go.
    xtick_list = []
    xtick_index = 1

    for key in key_list:
  
        ## Grab the statistics for each key      
        stats1 = stats_collection_1.get_stats_for_name(key)
        stats2 = stats_collection_2.get_stats_for_name(key)
        
        stats1_height_list = []
        stats2_z_list = []
        
        for stat in stats1._fid_collated_list:
            stats1_height_list.append(stat.coords[AXIS_CODING_SI])
            
        for stat in stats2._fid_collated_list:
            stats2_z_list.append(stat.coords[AXIS_CODING_SI])
        
        # print("xtick_index = " + str(xtick_index))
        bp = graph.boxplot([stats1_height_list, stats2_z_list], 
                           sym = 'rx',
                           positions = [xtick_index, xtick_index + 1],
                           widths = 0.8)
        
        xtick_list.append(xtick_index + 0.5)
        
        # Set the colors of the new boxes we just drew.
        set_boxplot_colors(bp, RANGE_ONE_COLOR, 0)
        set_boxplot_colors(bp, RANGE_TWO_COLOR, 1)
        
        # Increment our graph's x ticker to account for the two boxes we just plotted, plus a third space
        xtick_index += 4
        
    # Show all the values we just plotted
    axes.set_autoscalex_on(False)
    axes.set_xlim([0, xtick_index])
    axes.set_xticks(xtick_list)
    axes.set_xticklabels(key_list)
    
    axes.set_ylim(COORDINATE_GRAPH_MIN_MM, COORDINATE_GRAPH_MAX_MM)
    
    # Add a vertical grid to the plot
#     axes.xaxis.grid(True, linestyle='-', which='major', color='lightgrey',
#               alpha=0.5)
    
    # Add a horizontal grid to the plot
    axes.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
              alpha=0.5)
    
#       # Initialize
#       stats1_value = 0
#       stats2_value = 0
#
#         stats1_value_list = []
#         stats1_dev_list = []
#     
#         stats2_value_list = []
#         stats2_dev_list = []    
#
#         if (stats1 == None):
#             # This key is not present in stats1, just use zeros instead.
#             stats1_value = 0
#             stats1_value_list.append(stats1_value)
#             stats1_dev_list.append(0)
#         else: 
#             # Grab the height value and its stddev
#             stats1_value = stats1._averaged_fid.coords[AXIS_CODING_SI]
#             stats1_value_list.append(stats1_value)
#             stats1_dev_list.append(stats1._fid_std_dev_z)
#               
#         if (stats2 == None):
#             # This key is not present in stats1, just use zeros instead.
#             stats2_value = 0
#             stats2_value_list.append(stats2_value)
#             stats2_dev_list.append(0)
#         else: 
#             # Grab the height value and its stddev
#             stats2_value = stats2._averaged_fid.coords[AXIS_CODING_SI]
#             stats2_value_list.append(stats2_value)
#             stats2_dev_list.append(stats2._fid_std_dev_z)

#     # Bar graphing code - currently turned off.
#     if (False):    
#         BAR_WIDTH = 0.5
#         # Choose the total width of the graph - we'll need one column for each bar in stats1, one for each in stats2, and a space between, plus a gap at the end. 
#         GRAPH_WIDTH = BAR_WIDTH * 3 * len(key_list) + BAR_WIDTH  
#         
#         # Start with a space BAR_WIDTH big, then go all the way through GRAPH_WIDTH at spacing BAR_WIDTH * 3
#         stats1_x_locs = np.arange(2 * BAR_WIDTH, GRAPH_WIDTH, BAR_WIDTH*3)
#         stats2_x_locs = np.arange(3 * BAR_WIDTH, GRAPH_WIDTH, BAR_WIDTH*3)
#         
#         graph.bar(stats1_x_locs, stats1_value_list, BAR_WIDTH, color=RANGE_ONE_COLOR, yerr=stats1_dev_list)
#         graph.bar(stats2_x_locs, stats2_value_list, BAR_WIDTH, color=RANGE_TWO_COLOR, yerr=stats2_dev_list)
#         
#         graph.set_xticks(stats1_x_locs+BAR_WIDTH)
#         graph.set_xticklabels(key_list)

        

    

#####################
### DEFAULT MAIN PROC
#####################  graph

if __name__ == '__main__':
        
    from sys import argv
     
    setdebuglevel(debug_levels.BASIC_DEBUG) 
    
    ARGUMENT_LIST_SEPARATOR = ':'
    
    # Check argument validity
    if ((len(argv) < 4) 
        or not (argv.count(ARGUMENT_LIST_SEPARATOR) == 1)
        or (argv.index(ARGUMENT_LIST_SEPARATOR) >= len(argv))):
         
        print("Need to supply at two sets of mrml file names as arguments, separated by a single ':'")
        exit()
    
    # Get the two argument lists of file names.  Ignore argv[0], as it's just the filename of this python file.

    separator_index = argv.index(ARGUMENT_LIST_SEPARATOR)

    # List of fiducial stats representing a single vagina, to be compared to the range.
    range1propslist = load_vaginal_properties(argv[1:separator_index])
    [range1propstats, range1fidstats, range1propsdisplay] = get_stats_and_display_from_properties("Range 1", range1propslist)
    
    # List of fiducial stats representing a range to compare that single one against. 
    range2propslist = load_vaginal_properties(argv[separator_index + 1:])
    [range2propstats, range2fidstats, range2propsdisplay] = get_stats_and_display_from_properties("Range 2", range2propslist)
 
    fig = plt.figure(facecolor = GRAPH_BACKGROUND_COLOR)
    
    filtered_props_name_list = filter_vagprops_for_graphing(range1propsdisplay)
    
    num_graphs = 1
    graph_index = 1

    magic_subplot_number = generate_magic_subplot_number(num_graphs, graph_index)
    graph = fig.add_subplot(magic_subplot_number)
    
    create_2D_height_range_comparison_graph(graph, filtered_props_name_list, range1fidstats, range2fidstats)
    
    if (num_graphs > 0): 
        show_all_graphs()
