#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from a directory tree and normalize them to the PICS system, then display the results.

# Generic custom imports 
import __init__
from PICS3D_libraries.Utilities import setdebuglevel, debug_levels, debugprint
from PICS3D_libraries.Options import COORDS, AXIS_CODING, AXIS_CODING_OPTIONS

# Domain specific custom imports
from PICS3D_libraries.VaginalDisplay import VaginalDisplay
from PICS3D_libraries.PICSMath import pics_recenter_and_reorient, pics_verify
from PICS3D_executable.ComputeStatistics import collate_fiducials_reference_points,collate_fiducials_by_edges,collate_fiducials_by_row_and_column

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
        
        for i in range(1,len(argv)):
            filename = argv[i]
        
            debugprint('Now starting PICS pelvic points program',debug_levels.DETAILED_DEBUG)
                        
            vag_props = VaginalDisplay(filename, COLOR_STRAT)        
            vag_props.initialize_from_MRML(filename)
            
            pics_recenter_and_reorient(vag_props)
                
            pics_verify(vag_props)
             
            # Done processing, now do outputs! 
                
            print(vag_props.to_string())
            
            # Print all the reference point fiducials as CSV.
            print("\nLandmark fiducial list: ************")
            
            fidstats = collate_fiducials_reference_points([vag_props])
            fiddict = fidstats.get_all_stats()
            
            for fidstat in fiddict.itervalues():
                print(fidstat._averaged_fid.to_csv())
            
            # Print all the vaginal edge point fiducials as CSV.
            print("\nEdge fiducial list: ************")
                        
            fidstats = collate_fiducials_by_edges([vag_props])
            fiddict = fidstats.get_all_stats()
            
            for fidstat in fiddict.itervalues():
                print(fidstat._averaged_fid.to_csv() + " " 
                      + "Paravag Gap: " + str(fidstat._averaged_paravag_gap))
            

            # Print all the vaginal fiducials as CSV.
            print("\nDetailed fiducial list: ************")
            
            fidstats = collate_fiducials_by_row_and_column([vag_props])
            fiddict = fidstats.get_all_stats()
            
            can_compute_lowest_height = True
            lowest_height = float("inf") #infinity
            lowest_fiducial = None
            if (AXIS_CODING == AXIS_CODING_OPTIONS.lisse): 
                height_coordinate_index = COORDS.Z
            else: 
                if (AXIS_CODING == AXIS_CODING_OPTIONS.pics3d):
                    height_coordinate_index = COORDS.Y
                else: 
                    print("ERROR - CANNOT COMPUTE LOWEST HEIGHT DUE TO UNKNOWN AXIS CODING.")
                    can_compute_lowest_height = False                
            
            for fidstat in fiddict.itervalues():
                fid = fidstat._averaged_fid
                
                if (can_compute_lowest_height):
                    if (fid.coords[height_coordinate_index] < lowest_height):
                        lowest_fiducial = fid
                        lowest_height = fid.coords[height_coordinate_index]
                
                print(fid.to_csv())
            
            # Print the lowest fiducial point (assuming it's the "worst prolapse").
            print("\nLowest Fiducial: ************")    
            if (lowest_fiducial == None):
                print("Could not compute a lowest height fiducial.")
            else: 
                print("Lowest height fiducial is " + lowest_fiducial.to_string())
            
        debugprint('Now leaving pelvic points program',debug_levels.DETAILED_DEBUG)