#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from a directory tree

# Tested on /home/slisse/working/MRI_data/Reproducing_Larsen/138/Slicer4-Scene.mrml

# System imports
from os import path
from xml.parsers import expat

# Generic custom imports 
from Utilities import debugprint, debug_levels

# Domain specific custom imports
from Fiducials import Fiducial
from Options import SLICER4_2_FIDUCIAL_XML_NODE_NAME, SLICER4_2_FIDUCIAL_COORD_ATTR_NAME, SLICER4_2_FIDUCIAL_NAME_ATTR_NAME
from Options import SLICER4_3_FIDUCIAL_XML_NODE_NAME, SLICER4_3_FIDUCIAL_CSV_FILENAME_ATTR_NAME
from Options import SLICER4_3_CSV_NAME_INDEX, SLICER4_3_CSV_X_INDEX, SLICER4_3_CSV_Y_INDEX, SLICER4_3_CSV_Z_INDEX

def load_fiducials_from_mrml_slicer_v_4_2(filename, fiducial_list):
    ''' Load a Fiducial from an mrml file created by slicer version 4.0 through 4.2. '''
    
    def start_element(nodename, attrs):
        ''' Internal helper for loading Fiducial xml nodes from Slicer4 MRML files'''
        # debugprint("Checking XML element: " + nodename, debug_levels.DETAILED_DEBUG)
    
        if (nodename == SLICER4_2_FIDUCIAL_XML_NODE_NAME):
            name = attrs[SLICER4_2_FIDUCIAL_NAME_ATTR_NAME] 
            
            coordstring = attrs[SLICER4_2_FIDUCIAL_COORD_ATTR_NAME]
            # debugprint("Coordstring is: " + coordstring, debug_levels.DETAILED_DEBUG)
            x,y,z = coordstring.split(" ")
        
            debugprint("Creating Fiducial from XML: " + name + "," + x + "," + y + "," + z, debug_levels.DETAILED_DEBUG)
            fiducial_list[name] = Fiducial(name,float(x),float(y),float(z))
    
    debugprint("Attempting to load fiducials from MRML file as Slicer 4.2: " + filename, debug_levels.BASIC_DEBUG)
    
    if not(path.isfile(filename)): 
        raise ValueError("Error: " + filename + " is not a valid file name.")
        
    xmlparser = expat.ParserCreate()
    xmlparser.StartElementHandler=start_element

    with open(filename) as openfile: filecontents = str(openfile.read())

    # Automagically deals with fiducials using the start_element procedure above
    xmlparser.Parse(filecontents)



def load_fiducials_from_mrml_slicer_v_4_3(filename, fiducial_list):
    ''' Load a Fiducial from an mrml file created by slicer version 4.3 and beyond. '''
    
    #List to hold the names of all the FCSV files we have to parse for fiducials...
    csv_file_list = []
    
    def start_element(nodename, attrs):
        ''' Internal helper for loading Fiducial xml nodes from Slicer4.3 MRML files'''
        # debugprint("Checking XML element: " + nodename, debug_levels.DETAILED_DEBUG)
    
        if (nodename == SLICER4_3_FIDUCIAL_XML_NODE_NAME):
            csv_file_name = attrs[SLICER4_3_FIDUCIAL_CSV_FILENAME_ATTR_NAME] 
            
            csv_file_list.append(csv_file_name)

    debugprint("Attempting to load fiducials from MRML file as Slicer 4.3: " + filename, debug_levels.BASIC_DEBUG)
    with open(filename) as openfile: contents = str(openfile.read())
    
    xmlparser = expat.ParserCreate()
    xmlparser.StartElementHandler=start_element    
    
    # Use the XML parser and our start_element function above to populate csv_file_list with the names
    # of CSV files that potentially contain fiducials.
    xmlparser.Parse(contents)
     
    # Run through the CSV files one at a time, read each line and parse it as a Comma Separated Value
    # list of strings.       
    for csv_file_name in csv_file_list:
        with open(csv_file_name) as openfile: contents = str(openfile.read())
        
        lines = contents.splitlines()
        
        for line in lines:
            
            # Skip comment lines
            if '#' in line: 
                debugprint("Skipping line: " + line, debug_levels.DETAILED_DEBUG)
                continue
            
            fidvalues = line.split(',')
                        
            #Skip too-short lines (assuming the name is the last item on the line you want
            if len(fidvalues) <= SLICER4_3_CSV_NAME_INDEX: 
                debugprint("Skipping line: " + line, debug_levels.DETAILED_DEBUG)
                continue
            
            debugprint("Parsing line: " + line, debug_levels.DETAILED_DEBUG)
            name = fidvalues[SLICER4_3_CSV_NAME_INDEX]
            x = fidvalues[SLICER4_3_CSV_X_INDEX]
            y = fidvalues[SLICER4_3_CSV_Y_INDEX]
            z = fidvalues[SLICER4_3_CSV_Z_INDEX]
        
            debugprint("Creating Fiducial from CSV: " + name + "," + x + "," + y + "," + z, debug_levels.DETAILED_DEBUG)
            fiducial_list[name] = Fiducial(name,float(x),float(y),float(z))
    