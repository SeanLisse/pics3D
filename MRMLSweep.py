#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from a directory tree

# Tested on /home/slisse/working/MRI_data/Reproducing_Larsen/138/Slicer4-Scene.mrml

from os import path

from xml.parsers import expat

from Utilities import debugprint
from Utilities import debug_levels

from Fiducials import fiducial, fiducial_points, print_all_fiducials

FIDUCIAL_XML_NODE_NAME = "AnnotationFiducials"
FIDUCIAL_COORD_ATTR_NAME = "ctrlPtsCoord"
FIDUCIAL_NAME_ATTR_NAME = "name"

def load_fiducials_from_mrml(filename, fiducial_list):
    ''' Load a fiducial from an mrml file. '''
    
    def start_element(nodename, attrs):
        ''' Internal helper for loading fiducial xml nodes from Slicer4 MRML files'''
        debugprint("Checking XML element: " + nodename, debug_levels.DETAILED_DEBUG)
    
        if (nodename == FIDUCIAL_XML_NODE_NAME):
            name = attrs[FIDUCIAL_NAME_ATTR_NAME] 
            
            coordstring = attrs[FIDUCIAL_COORD_ATTR_NAME]
            debugprint("Coordstring is: " + coordstring, debug_levels.DETAILED_DEBUG)
            x,y,z = coordstring.split(" ")
        
            debugprint("Creating fiducial from XML: " + name + "," + x + "," + y + "," + z, debug_levels.BASIC_DEBUG)
            fiducial_list[name] = fiducial(name,float(x),float(y),float(z))
    
    debugprint("Loading fiducials from MRML file: " + filename, debug_levels.BASIC_DEBUG)
    
    if not(path.isfile(filename)): 
        raise ValueError("Error: " + filename + " is not a valid file name.")
    
    debugprint("Loading mrml file " + filename, debug_levels.DETAILED_DEBUG)
    
    xmlparser = expat.ParserCreate()
    xmlparser.StartElementHandler=start_element

    with open(filename) as openfile: filecontents = str(openfile.read())

    # Automagically deals with fiducials using the start_element procedure above
    xmlparser.Parse(filecontents)

#####################
### DEFAULT MAIN PROC
#####################
    
if __name__ == '__main__':
    
    import sys
    
    if len(sys.argv) < 2: 
        filename = "/home/slisse/working/MRI_data/Reproducing_Larsen/Sagittal_Only_Slicer_Files/OPALII_138/OPII_138.mrml"
    else:
        filename = sys.argv[1]
    
    debugprint('Now starting pelvic points program',debug_levels.BASIC_DEBUG)
                
    load_fiducials_from_mrml(filename, fiducial_points)
        
    print('************Final fiducials***********')
    print_all_fiducials(fiducial_points)
    
    debugprint('Now leaving pelvic points program',debug_levels.BASIC_DEBUG)
