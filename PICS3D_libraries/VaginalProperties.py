#! /usr/bin/env python
# Author: Sean Lisse

# Built in library imports
import collections
from numpy import Infinity, abs, dot

# Basic utilities
from Utilities import debug_levels, debugprint, rad_to_degrees

# My custom function imports
from Fiducials import Fiducial, vector_from_fiducials, get_fiducial_row_and_column
from MRMLSweep import load_fiducials_from_mrml_slicer_v_4_2, load_fiducials_from_mrml_slicer_v_4_3
from VectorMath import vector_magnitude_sum, magnitude, perpendicular_component, parallel_component, NEGLIGABLY_SMALL_NUMBER

# Constants
from Options import COORDS, CREATE_IIS, AXIS_CODING_IS
from Options import LEFT_ISCHIAL_SPINE_NAME, RIGHT_ISCHIAL_SPINE_NAME, INTER_ISCHIAL_SPINE_NAME, PUBIC_SYMPHYSIS_NAME, SC_JOINT_NAME

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

    # Intentionally "Class Global" items that are used to display comparisons
    _globalvagwidthmin = Infinity
    _globalvagwidthmax = -1 * Infinity
    
    # Amount of rotation that has been performed from raw radiographic image to current data
    _pelvic_tilt_correction_angle_about_LR_axis = None
    _pelvic_tilt_correction_angle_about_AP_axis = None
    _pelvic_tilt_correction_angle_about_IS_axis = None
    
    def __init__(self, name, fiducials = None):
        
        self._name = name
        
        if (fiducials == None):
            # Create a dictionary to contain our Fiducial points.  Each point will be indexed by name, and will be a 3-tuple of X,Y,Z values.
            self._fiducial_points = collections.OrderedDict()
        else: 
            self._fiducial_points = fiducials        
        
        self._rows = []
        self._vagwidths = []
        
        _vagwidthmin =  Infinity
        _vagwidthmax = -1 * Infinity
    
 
    def compute_properties(self):
        ''' Compute the physical properties of the pelvic floor. '''
        
        # Compute some basic properties of the pelvic floor based on bony landmarks    
        if (self._fiducial_points.has_key(PUBIC_SYMPHYSIS_NAME) 
            and self._fiducial_points.has_key(LEFT_ISCHIAL_SPINE_NAME) 
            and self._fiducial_points.has_key(RIGHT_ISCHIAL_SPINE_NAME)):
            
            #compute P_IS properties
            self._Pubic_Symphysis = self._fiducial_points[PUBIC_SYMPHYSIS_NAME]
            self._Left_IS = self._fiducial_points[LEFT_ISCHIAL_SPINE_NAME]
            self._Right_IS = self._fiducial_points[RIGHT_ISCHIAL_SPINE_NAME]
        
            self._Left_PIS_Vector = vector_from_fiducials(self._Pubic_Symphysis, self._Left_IS)
            self._Right_PIS_Vector = vector_from_fiducials(self._Pubic_Symphysis, self._Right_IS)
        
            if CREATE_IIS:
                IIS_coords = (self._Left_IS.coords + self._Right_IS.coords)/2
                self._IIS = Fiducial(INTER_ISCHIAL_SPINE_NAME, IIS_coords[COORDS.X], IIS_coords[COORDS.Y], IIS_coords[COORDS.Z])
                self._fiducial_points[INTER_ISCHIAL_SPINE_NAME] = self._IIS
    
        else:
            debugprint("Error!  Cannot find one of the points named: " 
                       + PUBIC_SYMPHYSIS_NAME 
                       + "," + LEFT_ISCHIAL_SPINE_NAME 
                       + ", or " + RIGHT_ISCHIAL_SPINE_NAME, debug_levels.ERRORS)
            
            fidpoints = self._fiducial_points
            if not fidpoints.has_key(PUBIC_SYMPHYSIS_NAME): debugprint("Missing " + PUBIC_SYMPHYSIS_NAME, debug_levels.ERRORS)   
            if not fidpoints.has_key(LEFT_ISCHIAL_SPINE_NAME): debugprint("Missing " + LEFT_ISCHIAL_SPINE_NAME, debug_levels.ERRORS)
            if not fidpoints.has_key(RIGHT_ISCHIAL_SPINE_NAME): debugprint("Missing " + RIGHT_ISCHIAL_SPINE_NAME, debug_levels.ERRORS)
        
        if (self._fiducial_points.has_key(SC_JOINT_NAME)):
            self._SC_Joint = self._fiducial_points[SC_JOINT_NAME]
        else:
            debugprint("Error!  Cannot find the point named: "
                       + SC_JOINT_NAME, debug_levels.ERRORS)
        
        # Compute paravaginal gap distances
        for key in self._fiducial_points.iterkeys():
            fid= self._fiducial_points[key]
            fid.paravaginal_gap = magnitude(get_paravaginal_gap_vector(fid, self))
            fid.paravaginal_gap_is = get_paravaginal_gap_distance_is(fid, self)
            fid.paravaginal_gap_horiz = get_paravaginal_gap_distance_horiz(fid, self)
              
        # Iterate through the Fiducial points and gather those that have a row and column number into "rows"
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
        
        # Iterate over all the Fiducial points and collect them into a sequence of point-to-point vectors for each row 
        for rowindex in range(0,len(self._rows)):
        
            columns = self._rows[rowindex]
            
            # Our list of vectors from each point to the next in the list, starting leftmost and continuing right.
            vecs = []
            
            for colindex in range(1, len(columns)):
                # Start at 1 to intentionally skip the first point so we don't underrun when looking at rows[colindex - 1]. 
                
                if (columns[colindex-1]) and (columns[colindex]):
                    # We know we have two non-empty entries, so add a vector from this point to the point before
                    vecs.append(vector_from_fiducials(columns[colindex - 1], columns[colindex]))
        
            new_width = abs(vector_magnitude_sum(vecs))
        
            self._vagwidths.insert(rowindex,new_width)
            
            # Compare against *this vagina's* min/max values
            if (self._vagwidths[rowindex] < self._vagwidthmin): 
                self._vagwidthmin = self._vagwidths[rowindex]
                
            if (self._vagwidths[rowindex] > self._vagwidthmax):
                self._vagwidthmax = self._vagwidths[rowindex]
            
            # Compare against *all vaginas'* min/max values    
            if (self._vagwidths[rowindex] < self._globalvagwidthmin): 
                self._globalvagwidthmin = self._vagwidths[rowindex]
                
            if (self._vagwidths[rowindex] > self._globalvagwidthmax):
                self._globalvagwidthmax = self._vagwidths[rowindex]
            
    def initialize_from_MRML(self, filename):
        ''' Load a set of fiducials from an MRML file.  Try both version 4.2 and version 4.3 formats.'''
        load_fiducials_from_mrml_slicer_v_4_2(filename, self._fiducial_points)
        load_fiducials_from_mrml_slicer_v_4_3(filename, self._fiducial_points)
        self.compute_properties() 

    def to_string(self):
        ''' Converts this object to a string readout. '''
        retstring = ("Vaginal properties.  " + "\n") 
        retstring += ("Name: " + self._name + "\n")
        
        retstring += ("Pubic Symphysis: " + self._Pubic_Symphysis.to_string() + "\n")
        retstring += ("Left Ischial Spine: " + self._Left_IS.to_string() + "\n")
        retstring += ("Right Ischial Spine: " + self._Right_IS.to_string() + "\n")
        retstring += ("Sacrococcygeal Joint: " + self._SC_Joint.to_string() + "\n")
        
        SCIPP_distance = magnitude(vector_from_fiducials(self._Pubic_Symphysis, self._SC_Joint))
        retstring += ("Length of SCIPP Line: " + str(SCIPP_distance) + "\n")
        
        IIS_distance = magnitude(vector_from_fiducials(self._Left_IS, self._Right_IS))
        retstring += ("Distance from L_IS to R_IS: " + str(IIS_distance) + "\n")
        
        if (rad_to_degrees(self._pelvic_tilt_correction_angle_about_LR_axis != None)): 
            retstring += ("Correction angle about LR axis ('pitch'):" + str(rad_to_degrees(self._pelvic_tilt_correction_angle_about_LR_axis)) + " degrees\n")
        
        if (rad_to_degrees(self._pelvic_tilt_correction_angle_about_AP_axis != None)):
            retstring += ("Correction angle about AP axis ('roll'):" + str(rad_to_degrees(self._pelvic_tilt_correction_angle_about_AP_axis)) + " degrees\n")
        
        if (rad_to_degrees(self._pelvic_tilt_correction_angle_about_IS_axis != None)):
            retstring += ("Correction angle about IS axis ('yaw'):" + str(rad_to_degrees(self._pelvic_tilt_correction_angle_about_IS_axis)) + " degrees\n")
        
        retstring += ("Vaginal Width Table: \n")
        
        for i in range(0, len(self._vagwidths)):
            retstring += "    Row # " + str(i+1) + ": " + str(self._vagwidths[i]) + "\n"
        
        return retstring
 

def get_paravaginal_gap_vector(fiducial, vagproperties):
    ''' Compute the vector from "fiducial" to the nearest Pubis->Ischial Spine line, aka the "Paravaginal Gap" '''
     
    if (fiducial == None) or (vagproperties._Pubic_Symphysis == None): 
        print("Error, 'None' passed to get_paravaginal_gap_vector!")
        return None

    debugprint("*****************", debug_levels.DETAILED_DEBUG)      
    debugprint("Fiducial: " + fiducial.to_string(), debug_levels.DETAILED_DEBUG)    
    debugprint("Pubic symphysis: " + vagproperties._Pubic_Symphysis.to_string(), debug_levels.DETAILED_DEBUG)

    fid_vector = vector_from_fiducials(vagproperties._Pubic_Symphysis, fiducial)
    debugprint("Fiducial Vector: " + str(fid_vector) + " with magnitude " + str(magnitude(fid_vector)), debug_levels.DETAILED_DEBUG)
    
    L_PIS_vector = vector_from_fiducials(vagproperties._Pubic_Symphysis, vagproperties._Left_IS)
    R_PIS_vector = vector_from_fiducials(vagproperties._Pubic_Symphysis, vagproperties._Right_IS)
   
    debugprint("L PIS Vector: " + str(L_PIS_vector), debug_levels.DETAILED_DEBUG)
    debugprint("R PIS Vector: " + str(R_PIS_vector), debug_levels.DETAILED_DEBUG)
     
    L_PIS_perp_vec = perpendicular_component(L_PIS_vector, fid_vector)
    R_PIS_perp_vec = perpendicular_component(R_PIS_vector, fid_vector)
    
    debugprint("L PIS Perpendicular: " + str(L_PIS_vector), debug_levels.DETAILED_DEBUG)
    debugprint("R PIS Perpendicular: " + str(R_PIS_vector), debug_levels.DETAILED_DEBUG)    
    
    debugprint("*****************", debug_levels.DETAILED_DEBUG)

    gap_vec = [None,None,None]

    # Verify that the perpendicular vector is indeed perpendicular to the PIS_Vector
    if (dot(L_PIS_vector, L_PIS_perp_vec) > NEGLIGABLY_SMALL_NUMBER):
        debugprint("ERROR!  Perpendicular vector code is returning a non-perpendicular vector when comparing to left PIS line!", debug_levels.ERRORS)
        
    if (dot(R_PIS_vector, R_PIS_perp_vec) > NEGLIGABLY_SMALL_NUMBER):
        debugprint("ERROR!  Perpendicular vector code is returning a non-perpendicular vector when comparing to right PIS line!", debug_levels.ERRORS)
 
    if (magnitude(L_PIS_perp_vec) <= magnitude(R_PIS_perp_vec)):
        gap_vec = L_PIS_perp_vec
    else:
        gap_vec = R_PIS_perp_vec

    ## Detect and repair the special case wherein the shortest distance to the IS lines is actually *in front of* the pubic symphysis.
    ## We repair it by replacing this anatomically infeasible vector with the vector from the fiducial to the pubic symphysis.
    L_dot = dot(vector_from_fiducials(vagproperties._Pubic_Symphysis, vagproperties._Left_IS), fid_vector)
    if (L_dot < (-1 * NEGLIGABLY_SMALL_NUMBER)):
        debugprint("Choosing to connect fiducial " + fiducial.name + " to the Pubic Symphysis as the origin of the Left P->IS line.", debug_levels.BASIC_DEBUG)
        for index in {0,1,2}:
            gap_vec[index] = fid_vector[index]

    R_dot = dot(vector_from_fiducials(vagproperties._Pubic_Symphysis, vagproperties._Right_IS), fid_vector)
    if (R_dot < (-1 * NEGLIGABLY_SMALL_NUMBER)):
        debugprint("Choosing to connect fiducial " + fiducial.name + " to the Pubic Symphysis as the origin of the Right P->IS line.", debug_levels.BASIC_DEBUG)

        for index in {0,1,2}:
            gap_vec[index] = fid_vector[index]

    return gap_vec
        
def get_paravaginal_gap_distance_is(fiducial, vagproperties):
    ''' Compute the distance from "fiducial" to the nearest Pubis->Ischial Spine line, aka the "Paravaginal Gap Distance", 
        along the Superior-Inferior Axis.'''
        
    if (fiducial == None) or (vagproperties._Pubic_Symphysis == None): 
        print("Error, 'None' passed to get_paravaginal_gap_distance_is!")
        return None

    gap_vec = get_paravaginal_gap_vector(fiducial, vagproperties)
        
    IS_distance = gap_vec[AXIS_CODING_IS]
        
    return IS_distance

def get_paravaginal_gap_distance_horiz(fiducial, vagproperties):
    ''' Compute the distance from "fiducial" to the nearest Pubis->Ischial Spine line, aka the "Paravaginal Gap Distance", 
        along the AP/LR Plane.'''
    
    if (fiducial == None) or (vagproperties._Pubic_Symphysis == None): 
        print("Error, 'None' passed to get_paravaginal_gap_distance_is!")
        return None

    gap_vec = get_paravaginal_gap_vector(fiducial, vagproperties)
    
    gap_vec[AXIS_CODING_IS] = 0
    
    AP_LR_distance = magnitude(gap_vec)
        
    return AP_LR_distance

def load_vaginal_properties(filenames):
    ''' Gather sets of vaginal properties from the filenames provided as arguments, and run them through the PICS standardization process. '''
    
    propslist = []
    for i in range(0,len(filenames)):
        filename = filenames[i]
                    
        vag_props = VaginalProperties(filename)        
        vag_props.initialize_from_MRML(filename)
                    
        propslist.append(vag_props) 
        
    return propslist