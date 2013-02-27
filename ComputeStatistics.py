#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from a directory tree and normalize them to the PICS system, analyze them mathematically, then display the results.

# Python base library imports
from collections import OrderedDict
from numpy import std as std_dev

# Generic custom imports 
from Utilities import setdebuglevel, debug_levels, debugprint

# Domain specific custom imports
from VaginalProperties import VaginalProperties
from Fiducials import fiducial, get_fiducial_list_by_row_and_column, COORDS, REFERENCE_POINT_NAMES
from ThreeDeePICS import pics_recenter_and_reorient, pics_verify

# Graph drawing imports 
from VaginalProperties import VaginalDisplay
from PelvicPoints import create_pelvic_points_graph
from Graphing import show_all_graphs
from GraphColoring import COLORIZATION_OPTIONS

# CONSTANTS
COLOR_STRAT = COLORIZATION_OPTIONS.WIDTH

#class fiducial_statistics():
#    ''' This is a class that collects statistical information about a particular fiducial point. '''
#    _fid_name=None
#    _fid_collated_list=[]
#    _fid_std_dev_x=None
#    _fid_std_dev_y=None
#    _fid_std_dev_z=None
#    
#    def __init__(self,name):
#        self._fid_name = name
#        
#    def add_fiducial(self, fiducial):
#        self._fid_collated_list.append(fiducial)
#        
#    def compute_properties(self): 
        

def load_vaginal_properties(filenames):
    ''' Gather sets of vaginal properties from the filenames provided as arguments '''
    
    propslist = []
    for i in range(1,len(filenames)):
        filename = filenames[i]
                    
        vag_props = VaginalProperties(filename)        
        vag_props.initialize_from_MRML(filename)
        
        pics_recenter_and_reorient(vag_props)
            
        pics_verify(vag_props)
            
        propslist.append(vag_props) 
        
    return propslist

def collate_fiducials_by_row_and_column(propslist):
    ''' Iterate over all gathered sets of vaginal properties, gathering the fiducials from them all and collating according to standardized names.'''
    
    # Gather the reference point fiducials to start
    allfids = collate_fiducials_reference_points(propslist)

    for vag_props in propslist:                    
        # Grab the rest that are named by row and column 
        fids = get_fiducial_list_by_row_and_column(vag_props._fiducial_points)
        
        for rowindex in range(1,len(fids)):
            colindex = None
            
            for colindex in range(1,len(fids[rowindex])):
            
                current_fid = fids[rowindex][colindex]
                
                standardized_fid_name = "A" + str(rowindex) + "L" + str(colindex)
            
                if (not (standardized_fid_name in allfids)): allfids[standardized_fid_name] = []
                    
                allfids[standardized_fid_name].append(current_fid)
                    
    return allfids

def collate_fiducials_by_edges(propslist):
    ''' Iterate over all gathered sets of vaginal properties, gathering the edge fiducials from them all and collating.'''
    
    LEFT_EDGE_PREFIX="Left_Edge_"
    RIGHT_EDGE_PREFIX="Right_Edge_"
    
    # Gather the reference point fiducials to start
    allfids = collate_fiducials_reference_points(propslist)
    
    for vag_props in propslist:
        # Grab the edges from the subset which are named by row and column 
        fids = get_fiducial_list_by_row_and_column(vag_props._fiducial_points)
        
        for rowindex in range(1,len(fids)):
            colindex = None
            start_found = False
            end_found = False
            
            # Count up from the left side of the row to find the left edge
            for colindex in range(1, len(fids[rowindex])):
                                
                current_fid = fids[rowindex][colindex]
                if ((not start_found) and (not current_fid == None)):
                    start_found = True
                    standardized_fid_name = LEFT_EDGE_PREFIX + str(rowindex)
                    
                    if (not (standardized_fid_name in allfids)): allfids[standardized_fid_name] = []
                    allfids[standardized_fid_name].append(current_fid)
        
                if start_found: break
        
            # Count down from the right side of the row to find the right edge
            fids[rowindex].reverse()
            for colindex in range(1, len(fids[rowindex])):
                
                current_fid = fids[rowindex][colindex]
                
                if ((not end_found) and (not current_fid == None)):
                    end_found = True
                    standardized_fid_name = RIGHT_EDGE_PREFIX + str(rowindex)
                    
                    if (not (standardized_fid_name in allfids)): allfids[standardized_fid_name] = []
                    allfids[standardized_fid_name].append(current_fid)
        
                if end_found: break
            
            # then put the row back into order
            fids[rowindex].reverse()
                
    return allfids
        
        
def collate_fiducials_reference_points(propslist):
    ''' Iterate over all gathered sets of vaginal properties, gathering the specially named reference point fiducials from them all and collating.'''

    allfids = OrderedDict()
    for vag_props in propslist:
        
        # Grab the special cases that aren't named by row and column
        for fidname in REFERENCE_POINT_NAMES:
            
            if (not fidname in vag_props._fiducial_points):
                debugprint("WARNING: Cannot find reference point fiducial named: " + fidname + "in vaginal properties " + vag_props.name, debug_levels.ERROR)        
            else: 
                current_fid = vag_props._fiducial_points[fidname]
                if (not (fidname in allfids)): allfids[fidname] = []
                allfids[fidname].append(current_fid)

    return allfids

#####################
### DEFAULT MAIN PROC
#####################  

if __name__ == '__main__':
        
    from sys import argv
     
    setdebuglevel(debug_levels.DETAILED_DEBUG) 
    
    if len(argv) < 2: 
        print "Need to supply at least one mrml file name argument."
    else:
        propslist = load_vaginal_properties(argv)                    
        
        # allfids = collate_fiducials_by_row_and_column(propslist)
        allfids = collate_fiducials_by_edges(propslist)
        
        averagedisplay = VaginalDisplay("average properties", COLOR_STRAT)
        
        # Iterate over our collated fiducials using their standardized names, and compute some values. 
        for fidname in allfids:
            fidlist = allfids[fidname]
            
            if (fidlist == None): continue
            
            listcount = 0
            xsum = ysum = zsum = 0
            xlist = []
            ylist = []
            zlist = []
            
            # Sum the values of X, Y, and Z for over the list
            for current_fid in fidlist:
                
                if (current_fid == None): continue
                
                xsum += current_fid.coords[COORDS.X]
                ysum += current_fid.coords[COORDS.Y]
                zsum += current_fid.coords[COORDS.Z]
                
                xlist.append(current_fid.coords[COORDS.X])
                ylist.append(current_fid.coords[COORDS.Y])
                zlist.append(current_fid.coords[COORDS.Z])
                
                listcount += 1
            
            if (listcount == 0): continue
           
            # Compute average properties containing the mean values for each fiducial point  
            averagedisplay._fiducial_points[fidname] = fiducial("average for " + fidname, 0,0,0)        
            averagefid = averagedisplay._fiducial_points[fidname]
            averagefid.coords[COORDS.X] = xsum/listcount
            averagefid.coords[COORDS.Y] = ysum/listcount
            averagefid.coords[COORDS.Z] = zsum/listcount 
            
            x_std_dev = std_dev(xlist)
            y_std_dev = std_dev(ylist)
            z_std_dev = std_dev(zlist)
            
            print(averagefid.to_string())
            print("X std dev: " + str(x_std_dev))
            print("Y std dev: " + str(y_std_dev))
            print("Z std dev: " + str(z_std_dev))
            
        averagedisplay.compute_properties()
        avg_graph = create_pelvic_points_graph(None, averagedisplay, "Averages")
        
        show_all_graphs()
        # TODO: Print out statistics and properties in some ordered form, here
