#! /usr/bin/env python
# Author: Sean Lisse

# Built in library imports
import collections
from numpy import Infinity

# Basic utilities
from Utilities import debug_levels, debugprint

# My custom function imports
from Fiducials import fiducial, vector_from_fiducials
from MRMLSweep import load_fiducials_from_mrml

# Constants
from Fiducials import COORDS, REFERENCE_POINT_NAMES, LEFT_ISCHIAL_SPINE_NAME, RIGHT_ISCHIAL_SPINE_NAME, PUBIC_SYMPHYSIS_NAME

class VaginalProperties(object):
    ''' This class This class is used to store information about the bony pelvis and pelvic floor of a particular woman, as determined by imaging. '''
    
    _fiducial_points = None
    
    _Pubic_Symphysis = _Left_IS = _Right_IS = _IIS = None
    _Left_PIS_Vector = _Right_PIS_Vector = None
    _PIS_distance_min = Infinity
    _PIS_distance_max = -1 * Infinity
    
    def __init__(self, fiducials=None):
        
        if (fiducials==None):
            # Create a dictionary to contain our fiducial points.  Each point will be indexed by name, and will be a 3-tuple of X,Y,Z values.
            self._fiducial_points = collections.OrderedDict()
        else: 
            self._fiducial_points = fiducials
 
    def compute_properties(self):
        
        print("Computing properties!")
        
        ### Here we encode and graph by minimum distance from one of the P->IS lines.        
        if (self._fiducial_points.has_key(PUBIC_SYMPHYSIS_NAME) 
            and self._fiducial_points.has_key(LEFT_ISCHIAL_SPINE_NAME) 
            and self._fiducial_points.has_key(RIGHT_ISCHIAL_SPINE_NAME)):
            
            #compute P_IS properties
            self._Pubic_Symphysis = self._fiducial_points[PUBIC_SYMPHYSIS_NAME]
            self._Left_IS = self._fiducial_points[LEFT_ISCHIAL_SPINE_NAME]
            self._Right_IS = self._fiducial_points[RIGHT_ISCHIAL_SPINE_NAME]
        
            self._Left_PIS_Vector = vector_from_fiducials(self._Pubic_Symphysis, self._Left_IS)
            self._Right_PIS_Vector = vector_from_fiducials(self._Pubic_Symphysis, self._Right_IS)
        
            IIS_coords = (self._Left_IS.coords + self._Right_IS.coords)/2
            self._IIS = fiducial("IIS", IIS_coords[COORDS.X], IIS_coords[COORDS.Y], IIS_coords[COORDS.Z])

        else:
            debugprint("Error!  Cannot find one of the points named: " 
                       + PUBIC_SYMPHYSIS_NAME 
                       + "," + LEFT_ISCHIAL_SPINE_NAME 
                       + ", or " + RIGHT_ISCHIAL_SPINE_NAME, debug_levels.ERRORS)   
            
    def initialize_from_MRML(self, filename):
        load_fiducials_from_mrml(filename, self._fiducial_points)
        self.compute_properties() 


class VaginalDisplay(VaginalProperties):
    
    _color_strategy = None
    _graph = None
    
    def __init__(self):
        VaginalProperties.__init__(self)
    
    def setColorStrategy(self, color_strategy):
        self._color_strategy = color_strategy   
    