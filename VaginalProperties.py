#! /usr/bin/env python
# Author: Sean Lisse

# Built in library imports
import collections
from numpy import Infinity

# Basic utilities
from Utilities import debug_levels, debugprint

# My custom function imports
from Fiducials import fiducial, vector_from_fiducials, get_fiducial_row_and_column
from MRMLSweep import load_fiducials_from_mrml
from VectorMath import vector_magnitude_sum

# Constants
from Fiducials import COORDS, LEFT_ISCHIAL_SPINE_NAME, RIGHT_ISCHIAL_SPINE_NAME, INTER_ISCHIAL_SPINE_NAME, PUBIC_SYMPHYSIS_NAME, SC_JOINT_NAME

class VaginalProperties(object):
    ''' This class is used to store information about the bony pelvis and pelvic floor of a particular woman, as determined by imaging. '''
    
    _name = ""
    
    # Set of all points defining the vagina
    _fiducial_points = None
    
    # Set of reference points
    _Pubic_Symphysis = _Left_IS = _Right_IS = _IIS = None
    
    ## Pubis->Ischial spine system definitions
    _Left_PIS_Vector = _Right_PIS_Vector = None
    _PIS_distance_min = Infinity
    _PIS_distance_max = -1 * Infinity
    
    ## Sacrococcygeal joint definition
    _SC_Joint = None

    # "rows" is a list of lists.
    # Outer list index is row number (minus one), so A1 == rows[0]
    # Inner list index is column number (minus one), so A1L3 == rows[0][2]
    # Note that we may have some empty entries (fid point A1L1 may not exist, for example), which we will skip when tabulating later.   
    _rows = None
    
    # List of vaginal widths for each row 
    _vagwidths = None
    
    _vagwidthmin =  None
    _vagwidthmax = None
    
    def __init__(self, name, fiducials=None):
        
        self._name = name
        
        if (fiducials==None):
            # Create a dictionary to contain our fiducial points.  Each point will be indexed by name, and will be a 3-tuple of X,Y,Z values.
            self._fiducial_points = collections.OrderedDict()
        else: 
            self._fiducial_points = fiducials        
        
        self._rows = []
        self._vagwidths = []
        
        _vagwidthmin =  Infinity
        _vagwidthmax = -1 * Infinity
    
 
    def compute_properties(self):
        ''' Compute the physical properties of the pelvic floor. '''
        
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
            self._IIS = fiducial(INTER_ISCHIAL_SPINE_NAME, IIS_coords[COORDS.X], IIS_coords[COORDS.Y], IIS_coords[COORDS.Z])
            
            self._fiducial_points[INTER_ISCHIAL_SPINE_NAME] = self._IIS
    
        else:
            debugprint("Error!  Cannot find one of the points named: " 
                       + PUBIC_SYMPHYSIS_NAME 
                       + "," + LEFT_ISCHIAL_SPINE_NAME 
                       + ", or " + RIGHT_ISCHIAL_SPINE_NAME, debug_levels.ERRORS)   
        
        if (self._fiducial_points.has_key(SC_JOINT_NAME)):
            self._SC_Joint = self._fiducial_points[SC_JOINT_NAME]
        else:
            debugprint("Error!  Cannot find the point named: "
                       + SC_JOINT_NAME, debug_levels.ERRORS)
              
        # Iterate through the fiducial points and gather those that have a row and column number into "rows"
        for key in self._fiducial_points.iterkeys():
            
            rownum,colnum = get_fiducial_row_and_column(self._fiducial_points[key])
        
            if ((rownum == None) or (colnum == None)):
                continue
        
            rowindex = int(rownum) - 1
            colindex = int(colnum) - 1
        
            # Expand rows[] to encompass our new row as needed
            while(len(self._rows) < (rowindex + 1)):
                self._rows.append([])
        
            # Expand rows[][] to encompass our new column as needed
            while(len(self._rows[rowindex]) < (colindex + 1)):
                self._rows[int(rowindex)].append([])
        
            fid = self._fiducial_points[key]
            self._rows[rowindex][colindex] = fid
        
        # Iterate over all the fiducial points and collect them into a sequence of point-to-point vectors for each row 
        for rowindex in range(0,len(self._rows)):
        
            columns = self._rows[rowindex]
            
            # Our list of vectors from each point to the next in the list, starting leftmost and continuing right.
            vecs = []
            
            for colindex in range(1, len(columns)):
                # Start at 1 to intentionally skip the first point so we don't underrun when looking at rows[colindex - 1]. 
                
                if (columns[colindex-1]) and (columns[colindex]):
                    # We know we have two non-empty entries, so add a vector from this point to the point before
                    vecs.append(vector_from_fiducials(columns[colindex - 1], columns[colindex]))
        
            self._vagwidths.insert(rowindex,vector_magnitude_sum(vecs))
            
            if (self._vagwidths[rowindex] < self._vagwidthmin): 
                self._vagwidthmin = self._vagwidths[rowindex]
                
            if (self._vagwidths[rowindex] > self._vagwidthmax):
                self._vagwidthmax = self._vagwidths[rowindex]
            
    def initialize_from_MRML(self, filename):
        load_fiducials_from_mrml(filename, self._fiducial_points)
        self.compute_properties() 

    def to_string(self):
        retstring = ("Vaginal properties.  " + "\n") 
        retstring += ("Name: " + self._name + "\n")
        
        retstring += ("Pubic Symphysis: " + self._Pubic_Symphysis.to_string() + "\n")
        retstring += ("Left Ischial Spine: " + self._Left_IS.to_string() + "\n")
        retstring += ("Right Ischial Spine: " + self._Right_IS.to_string() + "\n")
        retstring += ("Sacrococcygeal Joint: " + self._SC_Joint.to_string() + "\n")
        
        retstring += ("Vaginal Width Table: \n")
        
        for i in range(0, len(self._vagwidths)):
            retstring += "    Row # " + str(i+1) + ": " + str(self._vagwidths[i]) + "\n"
        
        return retstring

class VaginalDisplay(VaginalProperties):
    
    # Graph to use to display this vagina
    _graph = None
        # Strategy to use to color this vagina
    _color_strategy = None
    # Vaginal width list (indexed by fiducial rows)
    _vagrowcolors=[]
    
    # Intentionally "Class Global" items that are used to display comparisons
    _globalvagwidthmin = Infinity
    _globalvagwidthmax = -1 * Infinity
    
    def __init__(self, name):
        VaginalProperties.__init__(self, name)
    
    def setColorStrategy(self, color_strategy):
        self._color_strategy = color_strategy
        
    def compute_properties(self):
        VaginalProperties.compute_properties(self)
        
        # Iterate over all the fiducial points and collect them into a sequence of point-to-point vectors for each row 
        for rowindex in range(0,len(self._rows)):
        
            if (self._vagwidths[rowindex] < self._globalvagwidthmin): 
                self._globalvagwidthmin = self._vagwidths[rowindex]
                
            if (self._vagwidths[rowindex] > self._globalvagwidthmax):
                self._globalvagwidthmax = self._vagwidths[rowindex]
    