#! /usr/bin/env python
# Author: Sean Lisse
# Define a class to encapsulate a vagina and its display method

from VaginalProperties import VaginalProperties
from PICS3D_executable.Options import DEFAULT_COLORIZATION_STRATEGY

class VaginalDisplay(VaginalProperties):
 
    # What strategy should we use to display this vagina?
    _color_strategy = None
    
    # Vaginal width list (indexed by fiducial rows)
    _vagrowcolors = None
    
    def __init__(self, name, color_strat = DEFAULT_COLORIZATION_STRATEGY ):
        VaginalProperties.__init__(self, name)
        
        self._color_strategy = color_strat
        self._vagrowcolors=[]
        
    def to_string(self):
        result = VaginalProperties.to_string(self) # + "\n COLOR STRAT: " + str(self._color_strategy) + "\n"
            
        print(result)
        return result
    
def load_vaginal_displays(filenames, color_strat = DEFAULT_COLORIZATION_STRATEGY ):
    ''' Gather sets of vaginal properties from the filenames provided as arguments, and run them through the PICS standardization process. '''
    
    displaylist = []
    for i in range(0,len(filenames)):
        filename = filenames[i]
                    
        display = VaginalDisplay(filename, color_strat)        
        display.initialize_from_MRML(filename)
                    
        displaylist.append(display) 
        
    return displaylist