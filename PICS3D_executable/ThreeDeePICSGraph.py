#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from a directory tree and normalize them to the PICS system, then display the results.

# Generic custom imports 
import __init__
from PICS3D_libraries.Utilities import setdebuglevel, debug_levels, debugprint

# Domain specific custom imports
from PICS3D_libraries.VaginalDisplay import VaginalDisplay
from PICS3D_libraries.Graphing import show_all_graphs
from PelvicPoints import create_pelvic_points_graph
from PICS3D_libraries.PICSMath import pics_recenter_and_reorient, pics_verify

# Constants
from Options import COLOR_STRAT

#####################
### DEFAULT MAIN PROC
#####################  

if __name__ == '__main__':
        
    from sys import argv
             
    setdebuglevel(debug_levels.BASIC_DEBUG)
    
    if len(argv) < 2: 
        print "Need to supply mrml file name argument."
    else:
        
        # Use a single graph to show all inputs
        graph = None
        
        for i in range(1,len(argv)):
            filename = argv[i]
        
            debugprint('Now starting PICS pelvic points program',debug_levels.DETAILED_DEBUG)
                        
            vag_props = VaginalDisplay(filename, COLOR_STRAT)        
            vag_props.initialize_from_MRML(filename)
            
            pics_recenter_and_reorient(vag_props)
                
            pics_verify(vag_props)
                
            graph = create_pelvic_points_graph(graph, vag_props, filename)
            
            print(vag_props.to_string())
            
            print("************ Detailed fiducial list: ")
            
            for row in vag_props._rows:
                print(row)
                for fid in row:    
                    if (fid == []): continue
                    print(fid.to_string())
                            
        show_all_graphs()
            
        debugprint('Now leaving pelvic points program',debug_levels.DETAILED_DEBUG)
