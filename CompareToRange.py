#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from command-line arguments and normalize them to the PICS system, 
# Graphically compare the *first* set of fiducials to the range of the *rest* of the sets, and display the results.

# Generic custom imports 
import matplotlib.pyplot as plt
from Utilities import setdebuglevel, debug_levels, debugprint

# Domain specific custom imports
from ComputeStatistics import load_vaginal_properties, get_stats_and_display_from_properties
from Options import COORDS, REFERENCE_POINT_NAMES

# Graph control imports
from Graphing import show_all_graphs, generate_magic_subplot_number

from Options import STD_DEV_GRAPH_MULTIPLIER, SHOW_REFERENCE_POINTS, PARAVAG_MIN_MM, PARAVAG_MAX_MM, GRAPH_MIN_MM, GRAPH_MAX_MM
from Options import SHOW_PARAVAG_GRAPH, SHOW_WIDTH_GRAPH, SHOW_COORDINATE_GRAPH, COORD_TO_GRAPH
from Options import REFERENCE_POINT_BAR_COLOR, BAR_COLOR, POINT_COLOR

def filter_vagprops_for_graphing(exemplardisplay):
    ''' Trim out any fiducial points that we do *not* want to show. '''
    
    fid_dict = exemplardisplay._fiducial_points
    
    key_list = []
    
    # Make fid_list a reversed and filtered copy of fid_dict
    for key in fid_dict.iterkeys():
        
        if (fid_dict[key]) == None: continue
        
        if ((key in REFERENCE_POINT_NAMES) and (not SHOW_REFERENCE_POINTS)): continue
        
        key_list.insert(0, key)
      
    return key_list

def create_2D_paravaginal_graph(graph, graphname, exemplar_key_list, exemplar_props, rangestats):
    ''' Create a graph that displays the "paravaginal gap" distance (i.e. the distance from that point to the closest P-> IS line) 
    for each fiducial in exemplarlist, and compares that distance to the computed range from rangestats. '''
    
    if (graph == None):
        debugprint("No graph given! ",debug_levels.ERROR)
        return
    
    stat_list = rangestats.get_all_stats()
    
    fid_length = len(exemplar_key_list)
    graph.set_xlim(0,fid_length)
    graph.set_ylim(PARAVAG_MIN_MM, PARAVAG_MAX_MM)
    
    # Start with a blank point at 0 index so our first datapoint isn't right on the edge of the graph.
    x_index = 0
    x_labels = [""] 
    
    for key in exemplar_key_list:
        
        x_index += 1
        x_labels.append(key)

        # Draw the "error bar" on the graph in light grey
        if (key in stat_list):
            stat = stat_list[key]
        else: 
            stat = None
              
        if (stat != None): 
            avg_val = stat._averaged_paravag_gap
            
            stdev = stat._fid_paravag_gap_std_dev
            
            min_val = avg_val - (STD_DEV_GRAPH_MULTIPLIER * stdev)
            max_val = avg_val + (STD_DEV_GRAPH_MULTIPLIER * stdev)
            
            if (key in REFERENCE_POINT_NAMES):
                barcolor = REFERENCE_POINT_BAR_COLOR
            else: 
                barcolor = BAR_COLOR

            # Draw the range
            graph.broken_barh([(x_index-0.5,1)], (min_val, max_val - min_val), facecolors=barcolor)
            
            # Draw the average val
            graph.broken_barh([(x_index-0.5,1)], (avg_val, 0), facecolors=barcolor)
            
            # print("Stats for " + key + ": avg " + str(avg_val) + ", stdev " + str(stdev) + ", min " + str(min_val) + ", max " + str(max_val))
        
        # Draw the fiducial as a black dot.
        fid = exemplar_props._fiducial_points[key]
        graph.scatter(x_index, fid.paravaginal_gap, marker='o', label=key, color=POINT_COLOR)
        
    # Add an extra space on the end so our last point isn't on the edge of the graph.
    x_index += 2
    x_labels.append("")
    x_labels.append("")
        
    graph.set_xticks(range(0, x_index))    
    label_obj = graph.set_xticklabels(x_labels)
    graph.set_xlabel("Fiducial Point")
    
    graph.set_ylabel("Paravaginal Gap")       

    plt.setp(label_obj, rotation=45, fontsize=8)

    graph.grid(True)

    return graph   

def create_2D_comparison_graph(graph, graphname, exemplar_key_list, exemplar_props, rangestats):
    ''' Add all fiducials in key_list to the graph.  Info from rangestats appears as bars,  Info from exemplar_props as points.'''
        
    if (graph == None):
        debugprint("No graph given! ",debug_levels.ERROR)
        return
      
    fid_length = len(exemplar_key_list)
    graph.set_xlim(0,fid_length)
    graph.set_ylim(GRAPH_MIN_MM, GRAPH_MAX_MM)
    
    stat_list = rangestats.get_all_stats()
    
    # Start with a blank point at 0 index so our first datapoint isn't right on the edge of the graph.
    x_index = 0
    x_labels = [""] 
    
    for key in exemplar_key_list:
        
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
            graph.broken_barh([(x_index-0.5,1)], (min_val, max_val - min_val), facecolors=barcolor)
            
            # Draw the average val
            graph.broken_barh([(x_index-0.5,1)], (avg_val, 0), facecolors=barcolor)
            
            # print("Stats for " + key + ": avg " + str(avg_val) + ", stdev " + str(stdev) + ", min " + str(min_val) + ", max " + str(max_val))
        
        # Draw the fiducial as a black dot.
        fid = exemplar_props._fiducial_points[key]
        graph.scatter(x_index, fid.coords[COORD_TO_GRAPH], marker='o', label=key, color=POINT_COLOR)
    
    # Add an extra space on the end so our last point isn't on the edge of the graph.
    x_index += 2
    x_labels.append("")
    x_labels.append("")
        
    graph.set_xticks(range(0, x_index))    
    label_obj = graph.set_xticklabels(x_labels)       
    graph.set_xlabel("Fiducial Point")

    graph.set_ylabel("Superior-Inferior Axis")

    plt.setp(label_obj, rotation=45, fontsize=8)

    graph.grid(True)

    return graph   

def create_2D_width_graph(graph, graphname, exemplar_vagprop_stats, range_vagprop_stats): 
    
    # Rowcount is going to be the array index (e.g. 0..6).
    rowcount = len(exemplar_vagprop_stats._vagwidthlists)
    
    widthmin = min(range_vagprop_stats._vagwidthmeanslist)
    widthmax = max(range_vagprop_stats._vagwidthmeanslist)
    maxdev = max(range_vagprop_stats._vagwidthstddevlist)
    
    graphmin = widthmin - STD_DEV_GRAPH_MULTIPLIER * maxdev
    graphmax = widthmax + STD_DEV_GRAPH_MULTIPLIER * maxdev
    
    graph.set_xlim(0,rowcount + 1)
    graph.set_xticks(range(0, rowcount + 1))
    graph.set_xlabel("Row")
    
    graph.set_ylim(graphmin, graphmax)
    graph.set_ylabel("Width")

    for rowindex in range(0,rowcount):
        
        user_displayable_index = rowindex + 1
                
        range_avg_val = range_vagprop_stats._vagwidthmeanslist[rowindex]
        range_stddev = range_vagprop_stats._vagwidthstddevlist[rowindex]
        min_val = range_avg_val - STD_DEV_GRAPH_MULTIPLIER * range_stddev
        max_val = range_avg_val + STD_DEV_GRAPH_MULTIPLIER * range_stddev
         
        # Draw the min and max from range stats
        graph.broken_barh([(user_displayable_index-0.5,1)], (min_val, max_val - min_val), facecolors=BAR_COLOR)
            
        # Draw the average from range stats
        graph.broken_barh([(user_displayable_index-0.5,1)], (range_avg_val, 0), facecolors=BAR_COLOR)

        # Draw the point from exemplar stats
        exemplar_avg_val = exemplar_vagprop_stats._vagwidthmeanslist[rowindex]
        graph.scatter(user_displayable_index, exemplar_avg_val, marker='o', color=POINT_COLOR)

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
    [propstats, fidstats, propsdisplay] = get_stats_and_display_from_properties("Comparator", propslist)
    
    # List of fiducial stats representing a range to compare that single one against. 
    rangelist = load_vaginal_properties(argv[2:])
    [rangestats, rangefidstats, rangedisplay] = get_stats_and_display_from_properties("Range", rangelist)
 
    fig = plt.figure()
    
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
        
        create_2D_comparison_graph(graph, argv[1] + " Range Comparison", filtered_props_name_list, propsdisplay, rangefidstats)
    
    if (SHOW_PARAVAG_GRAPH):
        graph_index += 1
        magic_subplot_number = generate_magic_subplot_number(num_graphs, graph_index)
        graph = fig.add_subplot(magic_subplot_number)
        
        create_2D_paravaginal_graph(graph, argv[1] + " Paravaginal Comparison", filtered_props_name_list, propsdisplay, rangefidstats)
    
    if (SHOW_WIDTH_GRAPH):
        graph_index += 1
        magic_subplot_number = generate_magic_subplot_number(num_graphs, graph_index)
        graph = fig.add_subplot(magic_subplot_number)
        
        create_2D_width_graph(graph, argv[1] + " Width Comparison", propstats, rangestats)
    
    if (num_graphs > 0): show_all_graphs()
