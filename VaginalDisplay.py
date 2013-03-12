#! /usr/bin/env python
# Author: Sean Lisse
# Define a class to encapsulate a vagina and its display method

from VaginalProperties import VaginalProperties
from Options import DEFAULT_COLORIZATION_STRATEGY

class VaginalDisplay(VaginalProperties):
 
    # What strategy should we use to display this vagina?
    _color_strategy = None
    
    # Vaginal width list (indexed by fiducial rows)
    _vagrowcolors = None
    
    def __init__(self, name, color_strat = DEFAULT_COLORIZATION_STRATEGY ):
        VaginalProperties.__init__(self, name)
        
        self._color_strategy = color_strat
        
        self._vagrowcolors=[]