#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from command-line arguments and normalize them to the PICS system, analyze them mathematically, then display the results.

# Python base library imports
from collections import OrderedDict
from numpy import std as std_dev
from numpy import mean

# Generic custom imports 
from Utilities import setdebuglevel, debug_levels, debugprint, rad_to_degrees

# Domain specific custom imports
from VaginalProperties import VaginalProperties
from Fiducials import Fiducial, get_fiducial_list_by_row_and_column
from ThreeDeePICS import pics_recenter_and_reorient, pics_verify
from Options import COORDS, REFERENCE_POINT_NAMES, LEFT_EDGE_PREFIX, RIGHT_EDGE_PREFIX, CENTER_PREFIX
from Options import COMPUTE_EDGES, COMPUTE_CENTER, COMPUTE_ALL_INDIVIDUAL_POINTS, STD_DEV_GRAPH_MULTIPLIER

# Graph drawing imports 
from VaginalDisplay import VaginalDisplay
from PelvicPoints import create_pelvic_points_graph
from Graphing import show_all_graphs, add_line_to_graph3D
from Options import COLOR_STRAT

class FiducialStatistics():
    ''' This is a class that collects statistical information about a particular Fiducial point. '''
    
    def __init__(self,name):
        self._fid_name = name
        self._fid_collated_list=[]
        self._averaged_fid=None
        self._fid_std_dev_x=None
        self._fid_std_dev_y=None
        self._fid_std_dev_z=None
        
        self._averaged_paravag_gap=None
        self._fid_paravag_gap_std_dev=None
        
    def add_fiducial(self, Fiducial):
        self._fid_collated_list.append(Fiducial)
        self.update_statistics()
        
    def update_statistics(self): 
            
            debugprint("Computing statistics for " + self._fid_name, debug_levels.DETAILED_DEBUG)
            
            if (len(self._fid_collated_list) == 0): return
            
            xlist = []
            ylist = []
            zlist = []
            
            paravaginal_gap_list = []
            
            # Sum the values of X, Y, and Z for over the list
            for current_fid_index in range(0, len(self._fid_collated_list)):
                current_fid = self._fid_collated_list[current_fid_index]
                
                if (current_fid == None): continue
             
                xlist.append(current_fid.coords[COORDS.X])
                ylist.append(current_fid.coords[COORDS.Y])
                zlist.append(current_fid.coords[COORDS.Z])
                
                paravaginal_gap_list.append(current_fid.paravaginal_gap)

            x_avg = mean(xlist)
            y_avg = mean(ylist)
            z_avg = mean(zlist)            
            
            
            self._averaged_fid = Fiducial(self._fid_name, float(x_avg), float(y_avg), float(z_avg)) 
            
            self._fid_std_dev_x = std_dev(xlist)
            self._fid_std_dev_y = std_dev(ylist)
            self._fid_std_dev_z = std_dev(zlist)
            
            self._averaged_paravag_gap = mean(paravaginal_gap_list)
            self._fid_paravag_gap_std_dev = std_dev(paravaginal_gap_list)

class FiducialStatCollection():
    ''' A self-maintaining list of FiducialStatistics '''
    def __init__(self):
        self._statsdict = OrderedDict()
        
    def add_fiducial_by_name(self, fiducialname, Fiducial):
        if (not fiducialname in self._statsdict):
            self._statsdict[fiducialname] = FiducialStatistics(fiducialname)
         
        self._statsdict[fiducialname].add_fiducial(Fiducial)
    
    def get_all_stats(self):
        return self._statsdict
         
    def get_stats_for_name(self, fiducialname):
        if (not fiducialname in self._statsdict): 
            return None
        else:
            return self._statsdict[fiducialname]

class VaginalPropertyStatistics():
    ''' This is a class that collects statistical information about a collection of vaginalproperties objects. '''
    
    _propslist = None # A list of [name,VaginalProperties] pairs
    
    _fidstatcollection = None # A collection of fiducial statistics summarizing all of the values from propslist
    
    _vagwidthlists = None # An array of lists, each of which collects values for one row across all vaginalproperties
    _vagwidthmeanslist = None # An array of values, each of which is a mean for one of the rows in vagwidthlists.
    _vagwidthstddevlist = None # An array of values, each of which is a std dev for one of the rows in vagwidthlists.
    
    _pitch_correction_list = None
    _roll_correction_list = None
    _yaw_correction_list = None
    
    def __init__(self):
        self._propslist = []
        self._fidstatcollection = FiducialStatCollection()
        self._vagwidthlists = []  
    
        self._pitch_correction_list = []
        self._roll_correction_list = []
        self._yaw_correction_list = []
    
    def update_statistics(self):
        
        self._vagwidthmeanslist = []
        self._vagwidthstddevlist = []
        
        for widthlist in self._vagwidthlists:
            
            row_mean = mean(widthlist)
            row_std_dev = std_dev(widthlist)
            
            self._vagwidthmeanslist.append(row_mean)
            self._vagwidthstddevlist.append(row_std_dev)
               
        
    def add_vaginalproperties(self, vagprops):
        self._propslist.append([vagprops._name, vagprops])
        
        fids = vagprops._fiducial_points
        
        widthindex = 0
        
        # Collate vaginal width values from this set of vaginal properties
        for item in vagprops._vagwidths:
            
            if (len(self._vagwidthlists) <= widthindex):
                self._vagwidthlists.append([])
            
            if (self._vagwidthlists[widthindex] == None):
                self._vagwidthlists[widthindex] = []
            
            # Add the width to the list
            self._vagwidthlists[widthindex].append(item)
    
            widthindex += 1
            
        for key in fids.iterkeys():
            fid = fids[key]
            
            self._fidstatcollection.add_fiducial_by_name(key, fid)
            
        self._pitch_correction_list.append(rad_to_degrees(vagprops._pelvic_tilt_correction_angle_about_LR_axis))
        self._roll_correction_list.append(rad_to_degrees(vagprops._pelvic_tilt_correction_angle_about_AP_axis))
        self._yaw_correction_list.append(rad_to_degrees(vagprops._pelvic_tilt_correction_angle_about_IS_axis))
            
        self.update_statistics()
    
    def add_vaginalproperties_from_list(self, propslist):
        for item in propslist:
            self.add_vaginalproperties(item)

def load_vaginal_properties(filenames):
    ''' Gather sets of vaginal properties from the filenames provided as arguments, and run them through the PICS standardization process. '''
    
    propslist = []
    for i in range(0,len(filenames)):
        filename = filenames[i]
                    
        vag_props = VaginalProperties(filename)        
        vag_props.initialize_from_MRML(filename)
        
        pics_recenter_and_reorient(vag_props)
            
        pics_verify(vag_props)
            
        propslist.append(vag_props) 
        
    return propslist


def collate_fiducials_reference_points(propslist, allfidstats = None):
    ''' Iterate over all gathered sets of vaginal properties, gathering the specially named reference point fiducials from them all and collating.
    Fills statslist with the results and returns it.'''

    if (allfidstats == None): 
        allfidstats = FiducialStatCollection()
        
    for vag_props in propslist:
        
        # Grab the special cases that aren't named by row and column
        for fidname in REFERENCE_POINT_NAMES:
            
            if (not fidname in vag_props._fiducial_points):
                debugprint("WARNING: Cannot find reference point Fiducial named: " + fidname + "in vaginal properties " + vag_props.name, debug_levels.ERROR)        
            else: 
                current_fid = vag_props._fiducial_points[fidname]
               
                allfidstats.add_fiducial_by_name(fidname, current_fid)

    return allfidstats


def collate_fiducials_by_row_and_column(propslist, allfidstats = None):
    ''' Iterate over all gathered sets of vaginal properties, gathering the fiducials from them all and collating according to standardized names.'''
    
    if (allfidstats == None): 
        allfidstats = FiducialStatCollection()
        
    for vag_props in propslist:                    
        # Grab the rest that are named by row and column 
        fids = get_fiducial_list_by_row_and_column(vag_props._fiducial_points)
        
        for rowindex in range(1,len(fids)):
            colindex = None
            
            for colindex in range(1,len(fids[rowindex])):
            
                current_fid = fids[rowindex][colindex]
                
                standardized_fid_name = "A" + str(rowindex) + "L" + str(colindex)
                    
                allfidstats.add_fiducial_by_name(standardized_fid_name, current_fid)
                    
    return allfidstats

def collate_fiducials_by_edges(propslist, allfidstats = None):
    ''' Iterate over propslist, gathering the edge fiducials from them all and collating.
    Fills statslist with the results and returns it.'''
    
    if (allfidstats == None): 
        allfidstats = FiducialStatCollection()
            
    for vag_props in propslist:
        # Grab the edges from the subset which are named by row and column 
        fids = get_fiducial_list_by_row_and_column(vag_props._fiducial_points)
        
        for rowindex in range(1,len(fids)):
            colindex = None
            start_index = None
            end_index = None
            
            # Count up from the left side of the row to find the left edge
            for colindex in range(1, len(fids[rowindex])):
                                
                current_fid = fids[rowindex][colindex]
                if ((start_index == None) and (current_fid != None)):
                    start_index = colindex
                    standardized_fid_name = LEFT_EDGE_PREFIX + str(rowindex)
                    
                    if COMPUTE_EDGES: allfidstats.add_fiducial_by_name(standardized_fid_name, current_fid)   
                        
                if (start_index != None): break
        
            # Count down from the right side of the row to find the right edge
            
            fids[rowindex].reverse()  # Temporarily reverse the row ...
            
            for colindex in range(0, len(fids[rowindex])):
                
                current_fid = fids[rowindex][colindex]
                
                if ((end_index == None) and (current_fid != None)):
                    end_index = -1 * colindex
                    standardized_fid_name = RIGHT_EDGE_PREFIX + str(rowindex)
                    
                    if COMPUTE_EDGES: allfidstats.add_fiducial_by_name(standardized_fid_name, current_fid) 
                            
                if (end_index != None): break
            
            # ... then put the row back into order
            fids[rowindex].reverse()
            
            if ((start_index != None) and (end_index != None)):
                # Find the middle of the list between start and end.  Because end is counted from the *end* of the row and is expressed as a negative,
                # we need to average start_index and (end_index + length)
                # e.g. if start_index is 0, the list is 5 items long [0..4], and end_index is -1, mid_index should be (0 + -1 + 5)/2 = 2.
                mid_index = (start_index + len(fids[rowindex]) + end_index)/2
                mid_index = int(round(mid_index))
                
                #print("Start: " + str(start_index) + " Mid: " + str(mid_index) + " End: " + str(end_index + len(fids[rowindex])))
                
                standardized_fid_name = CENTER_PREFIX + str(rowindex)    
                current_fid = fids[rowindex][mid_index]   
                
                if (COMPUTE_CENTER): allfidstats.add_fiducial_by_name(standardized_fid_name, current_fid) 
                
    return allfidstats

def get_stats_and_display_from_properties(display_name, inputlist):
    ''' Takes a list of vaginal properties and returns a VaginalDisplay. '''
    
    propstats = VaginalPropertyStatistics()
        
    propstats.add_vaginalproperties_from_list(inputlist)
    
    statscollection = collate_fiducials_reference_points(inputlist)
    if (COMPUTE_EDGES or COMPUTE_CENTER): 
        statscollection = collate_fiducials_by_edges(inputlist, statscollection)
    if (COMPUTE_ALL_INDIVIDUAL_POINTS):
        statscollection = collate_fiducials_by_row_and_column(inputlist, statscollection)

    display = VaginalDisplay(display_name, COLOR_STRAT)        
    # Iterate over our collated Fiducial stats using their standardized names, and compute some values. 
    for fidname in statscollection.get_all_stats():
        stats = statscollection.get_stats_for_name(fidname)
        
        display._fiducial_points[fidname] = stats._averaged_fid
       

    for widthmean in propstats._vagwidthmeanslist:
        display._vagwidths.append(widthmean)

    display.compute_properties()
    
    return [propstats, statscollection,display]

def print_results(propstats, allfidstats):
    
    print("================")
    print("Vaginal Property Statistics for all sets of vaginas... ")
    print("Vaginal Width List:")
    
    rowcount = 0
    while (rowcount < len(propstats._vagwidthlists)):
        widthlist = propstats._vagwidthlists[rowcount]
        rowcount += 1 # Done here so the displayed row # makes sense
        print("Row # " + str(rowcount) 
              + ", mean: " +  str(mean(widthlist)) 
              + ", std dev: " + str(std_dev(widthlist)))
              
    print("================")
    
    print("Pitch Correction Angle mean: " + str(mean(propstats._pitch_correction_list)))
    print("Roll Correction Angle mean: " + str(mean(propstats._roll_correction_list)))
    print("Yaw Correction Angle mean: " + str(mean(propstats._yaw_correction_list)))
    
    print("================")
    
    for fidname in allfidstats.get_all_stats():
        stat = allfidstats.get_stats_for_name(fidname)
        print("================")
        print("Statistics for " + stat._fid_name)
        print("Mean Fiducial: " + stat._averaged_fid.to_string())
        print("X std dev: " + str(stat._fid_std_dev_x))
        print("Y std dev: " + str(stat._fid_std_dev_y))
        print("Z std dev: " + str(stat._fid_std_dev_z))
        print("Mean paravaginal gap: " + str(stat._averaged_paravag_gap))
        print("Paravaginal gap std dev: " + str(stat._fid_paravag_gap_std_dev)) 
        print("================")
     
    print("================")

def add_errorbars_to_graph(graph, fiducialstats):
    ''' Annotate the graph with standard deviation error bars. '''
    
    for fidname in allfidstats.get_all_stats():
            fidstats = allfidstats.get_stats_for_name(fidname)
            avg_fid = fidstats._averaged_fid
            
            center_x = avg_fid.coords[COORDS.X]
            center_y = avg_fid.coords[COORDS.Y]
            center_z = avg_fid.coords[COORDS.Z]
            
            max_x = center_x + (fidstats._fid_std_dev_x * STD_DEV_GRAPH_MULTIPLIER)
            min_x = center_x - (fidstats._fid_std_dev_x * STD_DEV_GRAPH_MULTIPLIER)
            
            max_y = center_y + (fidstats._fid_std_dev_y * STD_DEV_GRAPH_MULTIPLIER)
            min_y = center_y - (fidstats._fid_std_dev_y * STD_DEV_GRAPH_MULTIPLIER)
            
            max_z = center_z + (fidstats._fid_std_dev_z * STD_DEV_GRAPH_MULTIPLIER)
            min_z = center_z - (fidstats._fid_std_dev_z * STD_DEV_GRAPH_MULTIPLIER)
            
            # Draw a line through the average point from min to max for x
            start_coords=[min_x, center_y, center_z]
            end_coords=[max_x, center_y, center_z]
            add_line_to_graph3D(graph, start_coords, end_coords, "pink")
            
            # Draw a line through the average point from min to max for y
            start_coords=[center_x, min_y, center_z]
            end_coords=[center_x, max_y, center_z]
            add_line_to_graph3D(graph, start_coords, end_coords, "lightgreen")
            
            # Draw a line through the average point from min to max for z
            start_coords=[center_x, center_y, min_z]
            end_coords=[center_x, center_y, max_z]
            add_line_to_graph3D(graph, start_coords, end_coords, "lightblue")
            
            
#####################
### DEFAULT MAIN PROC
#####################  

if __name__ == '__main__':
        
    from sys import argv
     
    setdebuglevel(debug_levels.BASIC_DEBUG) 
    
    if len(argv) < 2: 
        debugprint("Need to supply at least one mrml file name argument.",debug_levels.ERROR)
    else:
        # ignore the argv[0], as it's just the filename of this python file.
        propslist = load_vaginal_properties(argv[1:])

        [propstats, allfidstats, averagedisplay] = get_stats_and_display_from_properties("Computed fiducials", propslist)

        avg_graph = create_pelvic_points_graph(None, averagedisplay, "Computed Statistics")
        
        add_errorbars_to_graph(avg_graph, allfidstats)
        
        print_results(propstats, allfidstats)
        
        show_all_graphs()
        # TODO: Print out statistics and properties in some ordered form, here
