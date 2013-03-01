#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from a directory tree and normalize them to the PICS system, analyze them mathematically, then display the results.

# Python base library imports
from collections import OrderedDict
from numpy import std as std_dev
from numpy import mean

# Generic custom imports 
from Utilities import setdebuglevel, debug_levels, debugprint

# Domain specific custom imports
from VaginalProperties import VaginalProperties
from Fiducials import fiducial, get_fiducial_list_by_row_and_column, COORDS, REFERENCE_POINT_NAMES
from ThreeDeePICS import pics_recenter_and_reorient, pics_verify

# Graph drawing imports 
from VaginalProperties import VaginalDisplay
from PelvicPoints import create_pelvic_points_graph
from Graphing import show_all_graphs, add_line_to_graph #, add_ellipsoid_to_graph
from GraphColoring import COLORIZATION_OPTIONS

# CONSTANTS
COLOR_STRAT = COLORIZATION_OPTIONS.SEQUENTIAL

# Should we compute edge points?
COMPUTE_EDGES = False

# What about the mid-sagittal section?
COMPUTE_CENTER = True

# Should we directly compare points by name?
COMPUTE_ALL_INDIVIDUAL_POINTS = False

# Should we draw std_dev error bars?
GRAPH_STD_DEV = True
# How long should they be?  length = std_dev * graph_multiplier.
STD_DEV_GRAPH_MULTIPLIER=2

# String constants for constructing standard names
LEFT_EDGE_PREFIX="Left_Edge_"
RIGHT_EDGE_PREFIX="Right_Edge_"
CENTER_PREFIX="Center_"

class FiducialStatistics():
    ''' This is a class that collects statistical information about a particular fiducial point. '''
    
    def __init__(self,name):
        self._fid_name = name
        self._fid_collated_list=[]
        self._averaged_fid=None
        self._fid_std_dev_x=None
        self._fid_std_dev_y=None
        self._fid_std_dev_z=None
        
    def add_fiducial(self, fiducial):
        self._fid_collated_list.append(fiducial)
        
    def compute_statistics(self): 
            
            debugprint("Computing statistics for " + self._fid_name, debug_levels.DETAILED_DEBUG)
            
            if (len(self._fid_collated_list) == 0): return
            
            xlist = []
            ylist = []
            zlist = []
            
            # Sum the values of X, Y, and Z for over the list
            for current_fid_index in range(0, len(self._fid_collated_list)):
                current_fid = self._fid_collated_list[current_fid_index]
                
                if (current_fid == None): continue
             
                xlist.append(current_fid.coords[COORDS.X])
                ylist.append(current_fid.coords[COORDS.Y])
                zlist.append(current_fid.coords[COORDS.Z])

            x_avg = mean(xlist)
            y_avg = mean(ylist)
            z_avg = mean(zlist)            
            
            self._averaged_fid = fiducial(fidname, float(x_avg), float(y_avg), float(z_avg)) 
            
            self._fid_std_dev_x = std_dev(xlist)
            self._fid_std_dev_y = std_dev(ylist)
            self._fid_std_dev_z = std_dev(zlist)

class FiducialStatCollection():
    ''' A self-maintaining list of FiducialStatistics '''
    def __init__(self):
        self._statlist = OrderedDict()
        
    def add_fiducial_by_name(self, fiducialname, fiducial):
        if (not fiducialname in self._statlist):
            self._statlist[fiducialname] = FiducialStatistics(fiducialname)
         
        self._statlist[fiducialname].add_fiducial(fiducial)
    
    def get_all_stats(self):
        return self._statlist
         
    def get_stats_for_name(self, fiducialname):
        if (not fiducialname in self._statlist): 
            return None
        else:
            return self._statlist[fiducialname]

def load_vaginal_properties(filenames):
    ''' Gather sets of vaginal properties from the filenames provided as arguments, and run them through the PICS standardization process. '''
    
    propslist = []
    for i in range(1,len(filenames)):
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
                debugprint("WARNING: Cannot find reference point fiducial named: " + fidname + "in vaginal properties " + vag_props.name, debug_levels.ERROR)        
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
                
                print("Start: " + str(start_index) + " Mid: " + str(mid_index) + " End: " + str(end_index + len(fids[rowindex])))
                
                standardized_fid_name = CENTER_PREFIX + str(rowindex)    
                current_fid = fids[rowindex][mid_index]   
                
                if (COMPUTE_CENTER): allfidstats.add_fiducial_by_name(standardized_fid_name, current_fid) 
                
    return allfidstats

def print_results(allfidstats):
    
    for fidname in allfidstats.get_all_stats():
        stat = allfidstats.get_stats_for_name(fidname)
        print("================")
        print("Statistics for " + stat._fid_name)
        print("Mean fiducial: " + stat._averaged_fid.to_string())
        print("X std dev: " + str(stat._fid_std_dev_x))
        print("Y std dev: " + str(stat._fid_std_dev_y))
        print("Z std dev: " + str(stat._fid_std_dev_z))
        print("================")
        
#####################
### DEFAULT MAIN PROC
#####################  

if __name__ == '__main__':
        
    from sys import argv
     
    setdebuglevel(debug_levels.BASIC_DEBUG) 
    
    if len(argv) < 2: 
        debugprint("Need to supply at least one mrml file name argument.",debug_levels.ERROR)
    else:
        propslist = load_vaginal_properties(argv)  

        # Gather the reference point fiducials to start
        allfidstats = collate_fiducials_reference_points(propslist)

        # Then collate edge points and/or center points if desired
        if (COMPUTE_EDGES or COMPUTE_CENTER): 
            collate_fiducials_by_edges(propslist, allfidstats)
        
        # Then collate each individual point by name if desired
        if (COMPUTE_ALL_INDIVIDUAL_POINTS):
            collate_fiducials_by_row_and_column(propslist, allfidstats)
        
        averagedisplay = VaginalDisplay("Averaged fiducials", COLOR_STRAT)
                
        # Iterate over our collated fiducial stats using their standardized names, and compute some values. 
        for fidname in allfidstats.get_all_stats():
            fidstats = allfidstats.get_stats_for_name(fidname)
            fidstats.compute_statistics()
            
            averagedisplay._fiducial_points[fidname] = fidstats._averaged_fid
            # print("Adding to the average display:" + averagedisplay._fiducial_points[fidname].to_string())
        
        averagedisplay.compute_properties()
        avg_graph = create_pelvic_points_graph(None, averagedisplay, "Computed Statistics")
        
        if (GRAPH_STD_DEV):
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
                add_line_to_graph(avg_graph, start_coords, end_coords, "pink")
                
                # Draw a line through the average point from min to max for y
                start_coords=[center_x, min_y, center_z]
                end_coords=[center_x, max_y, center_z]
                add_line_to_graph(avg_graph, start_coords, end_coords, "lightgreen")
                
                # Draw a line through the average point from min to max for z
                start_coords=[center_x, center_y, min_z]
                end_coords=[center_x, center_y, max_z]
                add_line_to_graph(avg_graph, start_coords, end_coords, "lightblue")
                
                # Add an ellipsoid to the graph
                # add_ellipsoid_to_graph(avg_graph, [center_x, center_y, center_z], max_x - min_x, max_y - min_y, max_z - min_z)
        
        print_results(allfidstats)
        
        show_all_graphs()
        # TODO: Print out statistics and properties in some ordered form, here
