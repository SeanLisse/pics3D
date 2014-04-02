#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from command-line arguments and normalize them to the PICS system, 
# Graphically compare the *first* set of fiducials to the range of the *rest* of the sets, and display the results.

# Generic custom imports
import __init__ 
import numpy as np
import matplotlib.pyplot as plt
# from pylab import boxplot
from PICS3D_libraries.Utilities import setdebuglevel, debug_levels, debugprint

# Domain specific custom imports
from ComputeStatistics import load_vaginal_properties, get_stats_and_display_from_properties
from PICS3D_libraries.Graphing import filter_vagprops_for_graphing

# Graph control imports
from PICS3D_libraries.Graphing import show_all_graphs, generate_magic_subplot_number

from Options import SHOW_REFERENCE_POINTS 
from Options import WIDTH_GRAPH_MIN_MM, WIDTH_GRAPH_MAX_MM 
from Options import SHOW_PARAVAG_GRAPH, SHOW_WIDTH_GRAPH, SHOW_COORDINATE_GRAPH, COORD_TO_GRAPH
from Options import GRAPH_BACKGROUND_COLOR, POINT_COLOR
from Options import SHOW_INDIVIDUAL_VALUES, SHOW_RANGE_VALUES
from Options import COORDS

def create_2D_coordinate_graph(graph, exemplar_key_list, exemplar_props, rangestats):
    ''' Add all fiducials in key_list to the graph.  Info from rangestats appears as bars,  Info from exemplar_props as points.'''
        
    if (graph == None):
        debugprint("No graph given! ",debug_levels.ERROR)
        return
    
    x_labels = []
    x_index = 0
    boxplot_list = []
    
    stat_list = rangestats.get_all_stats()
        
    for key in exemplar_key_list:
        x_labels.append(key)
        x_index += 1

        paravag_value_list = []    
        
        if (key in stat_list):
            stat = stat_list[key]
            for fid in stat._fid_collated_list:
                paravag_value_list.append(fid.coords[COORD_TO_GRAPH])
                 
        boxplot_list.append(paravag_value_list)
        
        # Draw the fiducial as a black dot.
        fid = exemplar_props._fiducial_points[key]
        
        if SHOW_INDIVIDUAL_VALUES: 
            graph.scatter(x_index, fid.coords[COORD_TO_GRAPH], marker='o', label=key, color=POINT_COLOR)
    
    if SHOW_RANGE_VALUES:     
        graph.boxplot(boxplot_list)
    
    # graph.set_ylabel("Height (mm)")
    
    # graph.grid(True)
    
    label_obj = graph.set_xticklabels(x_labels)
    plt.setp(label_obj, rotation=60, fontsize=10)
    
    # Add a horizontal grid to the plot
    graph.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
              alpha=0.5)

    return graph        
      
def create_2D_paravaginal_graph(graph, exemplar_key_list, exemplar_props, rangestats):
    ''' Create a graph that displays the "paravaginal gap" distance (i.e. the distance from that point to the closest P-> IS line) 
    for each fiducial in exemplarlist, and compares that distance to the computed range from rangestats. '''
    
    if (graph == None):
        debugprint("No graph given! ",debug_levels.ERROR)
        return
    
    x_labels = []
    x_index = 0
    boxplot_list = []
    
    stat_list = rangestats.get_all_stats()
        
    for key in exemplar_key_list:
        x_labels.append(key)
        x_index += 1

        paravag_value_list = [ None ]    
        
        if (key in stat_list):
            stat = stat_list[key]
            for fid in stat._fid_collated_list:
                paravag_value_list.append(fid.paravaginal_gap)
                 
        boxplot_list.append(paravag_value_list)
        
        # Draw the fiducial as a black dot.
        fid = exemplar_props._fiducial_points[key]
        
        if SHOW_INDIVIDUAL_VALUES:
            graph.scatter(x_index, fid.paravaginal_gap, marker='o', label=key, color=POINT_COLOR)
    
    if SHOW_RANGE_VALUES:            
        graph.boxplot(boxplot_list,
                      sym = 'rx',
                      widths = 0.8)
    
    graph.set_ylabel("Paravaginal Gap (mm)")
    
    graph.grid(True)
    
    label_obj = graph.set_xticklabels(x_labels)
    plt.setp(label_obj, rotation=60, fontsize=10)
    
    return graph   

def create_2D_width_graph(graph, exemplar_vagprops, range_vagprop_stats): 
    
    graphmin = WIDTH_GRAPH_MIN_MM
    graphmax = WIDTH_GRAPH_MAX_MM
    
    # Create "backwards counting" tick labels 
    xticklabels = ["Hiatus", "6", "5", "4", "3", "Os", "Fornix"]
    graph.set_xlabel("Row #")
    
    graph.set_ylim(graphmin, graphmax)
    graph.set_ylabel("Width")

    rev_range_widthlists = range_vagprop_stats._vagwidthlists[:] #Copy operator
    rev_range_widthlists.reverse()

    # Graph from lowest row to highest, as convention dictates vaginal hiatus be on the left
    graph.boxplot(rev_range_widthlists,
                           sym = 'rx',
                           widths = 0.8) 
    
    # Add a horizontal grid to the plot
    graph.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
              alpha=0.5)
    
    rowcount = 0
    
    rev_ex_vagwidths = exemplar_vagprops._vagwidths[:] #Copy operator
    rev_ex_vagwidths.reverse() # Graph from lowest row to highest, as convention dictates vaginal hiatus be on the left
    
    for exemplar_width in rev_ex_vagwidths:
        rowcount +=1 
        if SHOW_INDIVIDUAL_VALUES:
            graph.scatter(rowcount, exemplar_width, marker='o', color=POINT_COLOR)

    graph.set_xticklabels(xticklabels)
    graph.grid(True)

#####################
### DEFAULT MAIN PROC
#####################  graph

if __name__ == '__main__':
        
    from sys import argv
     
    setdebuglevel(debug_levels.BASIC_DEBUG) 
    
    if len(argv) < 3: 
        print("Need to supply at least one mrml file name argument and at least one to compare it against.")
        exit()
    
    # ignore argv[0], as it's just the filename of this python file.

    # List of fiducial stats representing a single vagina, to be compared to the range.
    propslist = load_vaginal_properties(argv[1:2])
    [propstats, fidstats, propsdisplay] = get_stats_and_display_from_properties("Exemplar", propslist)
    
    # List of fiducial stats representing a range to compare that single one against. 
    rangelist = load_vaginal_properties(argv[2:])
    [rangestats, rangefidstats, rangedisplay] = get_stats_and_display_from_properties("Range", rangelist)
 
    fig = plt.figure(facecolor = GRAPH_BACKGROUND_COLOR)
    
    filtered_props_name_list = filter_vagprops_for_graphing(propsdisplay)
    
    num_graphs = 0
    graph_index = 0

    if SHOW_COORDINATE_GRAPH: num_graphs += 1
    if SHOW_PARAVAG_GRAPH: num_graphs += 1
    if SHOW_WIDTH_GRAPH: num_graphs +=1
    
            
    if (SHOW_COORDINATE_GRAPH):
        graph_index += 1
        magic_subplot_number = generate_magic_subplot_number(num_graphs, graph_index)
        graph = fig.add_subplot(magic_subplot_number)

        create_2D_coordinate_graph(graph, filtered_props_name_list, propsdisplay, rangefidstats)
    
    if (SHOW_PARAVAG_GRAPH):
        graph_index += 1
        magic_subplot_number = generate_magic_subplot_number(num_graphs, graph_index)
        graph = fig.add_subplot(magic_subplot_number)

        create_2D_paravaginal_graph(graph, filtered_props_name_list, propsdisplay, rangefidstats)
    
    if (SHOW_WIDTH_GRAPH):
        graph_index += 1
        magic_subplot_number = generate_magic_subplot_number(num_graphs, graph_index)
        graph = fig.add_subplot(magic_subplot_number)
        
        create_2D_width_graph(graph, propsdisplay, rangestats)
     
    if (num_graphs > 0): 
        show_all_graphs()
